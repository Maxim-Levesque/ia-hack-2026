"""
train_model.py — Entraînement du classificateur de sons marins
=================================================================
Utilise la base de données fournie (train/test) pour entraîner un
modèle Random Forest basé sur les MFCCs et features spectrales.

Exécuter: python train_model.py
"""

import os
import glob
import warnings
import numpy as np
import joblib
from pathlib import Path
from collections import Counter

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DB_PART1 = BASE_DIR / "Ressources" / "Ressources du défi #1" / "Partie #1" / "Base de données"
DB_PART2 = BASE_DIR / "Ressources" / "Ressources du défi #1" / "Partie #2" / "Complément de base de données"

# Dossiers sources (on va scanner les deux parties)
DATA_SOURCES = [DB_PART1, DB_PART2]

MODEL_DIR = BASE_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

# Mapping: nom du dossier → index de classe
SPECIES_MAP = {
    "Beluga_WhiteWhale": 0,
    "Fin_FinbackWhale": 1,
    "HumpbackWhale": 2,
    "SpermWhale": 3,
    "White_sidedDolphin": 4,
    "noise": 5,  # Nouvelle classe de bruit issue de la Partie 2
}

SPECIES_NAMES = [
    "Béluga",
    "Rorqual Commun",
    "Baleine à bosse",
    "Cachalot",
    "Dauphin à flancs blancs",
    "Bruit",
]

# Feature extraction parameters
SAMPLE_RATE = 22050      # Hz — standard librosa
WINDOW_DURATION = 2.0    # secondes par fenêtre
HOP_DURATION = 0.5       # plus haute résolution temporelle
N_MFCC = 40              # Nombre de coefficients MFCC


# ── Feature extraction ────────────────────────────────────────────────────────
def extract_features(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Extrait un vecteur de features d'un segment audio.

    Features extraites (total ~180 valeurs) :
    - 40 MFCCs × (mean + std) = 80
    - delta MFCCs × (mean + std) = 80
    - Chroma × mean = 12
    - Spectral centroid, bandwidth, rolloff × (mean + std) = 6
    - Zero Crossing Rate × (mean + std) = 2
    - RMS Energy × (mean + std) = 2
    """
    import librosa

    # Assurer longueur minimale
    min_samples = int(0.1 * sr)
    if len(y) < min_samples:
        y = np.pad(y, (0, min_samples - len(y)))

    features = []

    # 1. MFCCs (40 coefficients × mean + std)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    features.extend(np.mean(mfccs, axis=1))
    features.extend(np.std(mfccs, axis=1))

    # 2. Delta MFCCs (dérivée première = vélocité)
    delta_mfccs = librosa.feature.delta(mfccs)
    features.extend(np.mean(delta_mfccs, axis=1))
    features.extend(np.std(delta_mfccs, axis=1))

    # 3. Chroma (12 semi-tons)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features.extend(np.mean(chroma, axis=1))

    # 4. Spectral centroid
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    features.append(float(np.mean(spec_cent)))
    features.append(float(np.std(spec_cent)))

    # 5. Spectral bandwidth
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    features.append(float(np.mean(spec_bw)))
    features.append(float(np.std(spec_bw)))

    # 6. Spectral rolloff
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    features.append(float(np.mean(rolloff)))
    features.append(float(np.std(rolloff)))

    # 7. Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)
    features.append(float(np.mean(zcr)))
    features.append(float(np.std(zcr)))

    # 8. RMS Energy
    rms = librosa.feature.rms(y=y)
    features.append(float(np.mean(rms)))
    features.append(float(np.std(rms)))

    return np.array(features, dtype=np.float32)


SEQ_AUDIO_PATH = BASE_DIR / "Ressources" / "Ressources du défi #1" / "Partie #2" / "Longues séquences" / "audio"
SEQ_ANNOT_PATH = BASE_DIR / "Ressources" / "Ressources du défi #1" / "Partie #2" / "Longues séquences" / "annotations"


def extract_features_from_file(filepath: str, oversample: bool = False) -> list[np.ndarray]:
    """
    Charge un fichier audio et extrait les features par fenêtre glissante.
    Si oversample=True (pour le bruit), on utilise un pas beaucoup plus petit.
    """
    import librosa

    y, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)
    duration = len(y) / sr

    window_samples = int(WINDOW_DURATION * sr)
    # Plus petit pas pour le bruit pour multiplier les exemples (Data Augmentation)
    hop_dur = 0.5 if oversample else HOP_DURATION
    hop_samples = int(hop_dur * sr)

    feature_list = []

    if duration <= WINDOW_DURATION:
        feat = extract_features(y, sr)
        feature_list.append(feat)
    else:
        start = 0
        while start + window_samples <= len(y):
            segment = y[start : start + window_samples]
            feat = extract_features(segment, sr)
            feature_list.append(feat)
            start += hop_samples

        if start < len(y):
            segment = y[start:]
            if len(segment) > int(0.1 * sr):
                feat = extract_features(segment, sr)
                feature_list.append(feat)

    return feature_list


def build_dataset_from_sequences(all_features: list, all_labels: list):
    """
    Extrait des exemples depuis les longues séquences annotées par CSV.
    Tout ce qui n'est pas annoté est considéré comme du BRUIT (Noise).
    """
    import csv
    import librosa

    if not SEQ_AUDIO_PATH.exists() or not SEQ_ANNOT_PATH.exists():
        print(f"Chemins séquences introuvables : {SEQ_AUDIO_PATH} ou {SEQ_ANNOT_PATH}")
        return

    print(f"\nExtraction depuis les LONGUES SÉQUENCES ({SEQ_AUDIO_PATH.name})...")
    
    wav_files = list(SEQ_AUDIO_PATH.glob("*.wav"))
    for audio_file in wav_files:
        csv_file = SEQ_ANNOT_PATH / f"{audio_file.stem}.csv"
        if not csv_file.exists():
            continue
            
        try:
            y, sr = librosa.load(audio_file, sr=SAMPLE_RATE)
            annotations = []
            
            # Lire CSV avec le module standard csv
            with open(csv_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    animal = row['animal']
                    if animal in SPECIES_MAP:
                        class_idx = SPECIES_MAP[animal]
                        start_s = float(row['start_sec'])
                        end_s = float(row['end_sec'])
                        annotations.append((class_idx, start_s, end_s))
            
            # 1. Extraire les ANIMAUX annotés
            for class_idx, start_s, end_s in annotations:
                # Extraire le segment (on s'assure d'avoir au moins 3s)
                center = (start_s + end_s) / 2
                seg_start = max(0, int((center - 1.5) * sr))
                seg_end = min(len(y), seg_start + int(3.0 * sr))
                
                seg = y[seg_start:seg_end]
                all_features.append(extract_features(seg, sr))
                all_labels.append(class_idx)
            
            # 2. Extraire le BRUIT (entre les annotations)
            mask = np.ones(len(y), dtype=bool)
            for _, start_s, end_s in annotations:
                s = max(0, int((start_s - 0.5) * sr)) # Marge de sécurité 0.5s
                e = min(len(y), int((end_s + 0.5) * sr))
                mask[s:e] = False
            
            # Parcourir les zones de "bruit" avec un pas de 1.5s
            hop = int(1.5 * sr)
            win = int(3.0 * sr)
            for i in range(0, len(y) - win, hop):
                if np.all(mask[i : i + win]):
                    seg = y[i : i + win]
                    all_features.append(extract_features(seg, sr))
                    all_labels.append(5) # Classe Bruit
                        
        except Exception as e:
            print(f"Erreur séquence {audio_file.name}: {e}")


# ── Dataset building ──────────────────────────────────────────────────────────
def build_dataset(sources: list[Path], subset: str = "train") -> tuple[np.ndarray, np.ndarray]:
    """
    Construit le dataset complet. Si subset=='train', on inclut aussi les séquences.
    """
    all_features = []
    all_labels = []

    print(f"\nScanning databases for: {subset}")

    # Ajout des séquences (seulement pour le train pour booster la robustesse)
    if subset == "train":
        build_dataset_from_sequences(all_features, all_labels)

    
    for db_path in sources:
        search_path = db_path / subset
        if not search_path.exists():
            continue
            
        print(f"Source: {db_path.name}")
        
        for species_dir, class_idx in SPECIES_MAP.items():
            species_path = search_path / species_dir
            if not species_path.exists():
                continue

            wav_files = list(species_path.glob("*.wav")) + list(species_path.glob("*.WAV"))
            if not wav_files:
                continue
                
            print(f"{SPECIES_NAMES[class_idx]:23s} → {len(wav_files):3d} fichiers")

            # On oversample la classe BRUIT (5) pour qu'elle soit mieux apprise
            is_noise = (class_idx == 5)

            for wav_file in wav_files:
                try:
                    feats = extract_features_from_file(str(wav_file), oversample=is_noise)
                    for f in feats:
                        all_features.append(f)
                        all_labels.append(class_idx)
                except Exception as e:
                    print(f"Erreur {wav_file.name}: {e}")

    if not all_features:
        raise ValueError(f"Aucune donnée trouvée pour le subset '{subset}' dans les sources fournies.")

    X = np.array(all_features, dtype=np.float32)
    y = np.array(all_labels, dtype=np.int32)
    return X, y


# ── Main training ─────────────────────────────────────────────────────────────
def train():
    import librosa  # noqa — verify import
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    print("\n" + "=" * 60)
    print("  ENTRAÎNEMENT v3 — RÉÉQUILIBRAGE & DATA AUGMENTATION BRUIT")
    print("=" * 60)

    # ── Données d'entraînement ────────────────────────────────────
    X_train, y_train = build_dataset(DATA_SOURCES, subset="train")
    print(f"\n  Shape X_train : {X_train.shape}")
    print(f"  Distribution labels : {dict(Counter(y_train))}")

    # ── Données de test ───────────────────────────────────────────
    X_test, y_test = build_dataset(DATA_SOURCES, subset="test")
    print(f"\n  Shape X_test  : {X_test.shape}")
    print(f"  Distribution labels : {dict(Counter(y_test))}")

    # ── Normalisation ─────────────────────────────────────────────
    print("\nNormalisation StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ── Entraînement Random Forest ────────────────────────────────
    print("\nEntrainement du Random Forest (n=200 arbres)...")
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
        verbose=1,
    )
    clf.fit(X_train_scaled, y_train)

    # ── Évaluation ────────────────────────────────────────────────
    print("\nEvaluation sur le jeu de TEST...")
    y_pred = clf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Accuracy : {accuracy:.2%}")
    print("\n  Rapport de classification :")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=SPECIES_NAMES,
            zero_division=0,
        )
    )

    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    print("\n  Matrice de confusion :")
    header = "  " + " ".join([f"{n[:8]:>8}" for n in SPECIES_NAMES])
    print(header)
    for i, row in enumerate(cm):
        row_str = "  " + " ".join([f"{v:8d}" for v in row])
        print(f"  {SPECIES_NAMES[i][:8]:8s}{row_str}")

    # ── Sauvegarde ────────────────────────────────────────────────
    clf_path = MODEL_DIR / "classifier.pkl"
    scaler_path = MODEL_DIR / "scaler.pkl"
    meta_path = MODEL_DIR / "metadata.pkl"

    joblib.dump(clf, clf_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(
        {
            "species_names": SPECIES_NAMES,
            "species_map": SPECIES_MAP,
            "n_mfcc": N_MFCC,
            "sample_rate": SAMPLE_RATE,
            "window_duration": WINDOW_DURATION,
            "hop_duration": HOP_DURATION,
            "accuracy": accuracy,
            "n_features": X_train.shape[1],
        },
        meta_path,
    )

    print(f"\nModèle sauvegardé dans '{MODEL_DIR}':")
    print(f"   - {clf_path.name}")
    print(f"   - {scaler_path.name}")
    print(f"   - {meta_path.name}")
    print("\nEntraînement terminé!\n")

    return accuracy


if __name__ == "__main__":
    train()
