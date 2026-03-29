"""
model/predictor.py — Module d'inférence pour la classification de sons marins
======================================================================================
Charge le modèle entraîné et effectue l'inférence sur un fichier audio uploadé.
Supporte la détection multi-espèces par fenêtre glissante.
"""

import io
import os
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np

# ── Chemins ────────────────────────────────────────────────────────────────────
_MODEL_DIR = Path(__file__).parent
_CLF_PATH = _MODEL_DIR / "classifier.pkl"
_SCALER_PATH = _MODEL_DIR / "scaler.pkl"
_META_PATH = _MODEL_DIR / "metadata.pkl"

# ── Mapping espèce-dossier → index SPECIES dans especes.py ────────────────────
FOLDER_TO_SPECIES_IDX = {
    "Beluga_WhiteWhale": 0,
    "Fin_FinbackWhale": 1,
    "HumpbackWhale": 2,
    "SpermWhale": 3,
    "White_sidedDolphin": 4,
}

# Seuil de confiance minimal pour qu'une espèce soit "détectée"
CONFIDENCE_THRESHOLD = 0.25
# Seuil de bruit : si la proba max d'espèce est sous ce seuil, c'est du bruit
# Augmenté à 0.55 pour être plus conservateur et éviter les faux positifs (Baleine à bosse)
NOISE_THRESHOLD = 0.55
# Seuil d'énergie RMS : si l'énergie moyenne est sous ce seuil, c'est du silence/bruit
ENERGY_THRESHOLD = 0.002


def _load_model():
    """Charge le classifieur, le scaler et les métadonnées depuis le disque."""
    import joblib

    if not _CLF_PATH.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {_CLF_PATH}\n"
            "Veuillez d'abord entraîner le modèle avec : python train_model.py"
        )

    clf = joblib.load(_CLF_PATH)
    scaler = joblib.load(_SCALER_PATH)
    meta = joblib.load(_META_PATH)
    return clf, scaler, meta


# On utilise un simple cache global pour éviter de recharger à chaque appel
_cache = {}


def _get_model():
    """Retourne le modèle chargé (avec cache en mémoire)."""
    if "clf" not in _cache:
        clf, scaler, meta = _load_model()
        _cache["clf"] = clf
        _cache["scaler"] = scaler
        _cache["meta"] = meta
    return _cache["clf"], _cache["scaler"], _cache["meta"]


def _extract_features(y: np.ndarray, sr: int, n_mfcc: int = 40) -> tuple:
    """
    Extrait un vecteur de features et l'énergie moyenne.
    """
    import librosa

    min_samples = int(0.1 * sr)
    if len(y) < min_samples:
        y = np.pad(y, (0, min_samples - len(y)))

    features = []

    # 1. MFCCs
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    features.extend(np.mean(mfccs, axis=1))
    features.extend(np.std(mfccs, axis=1))

    # 2. Delta MFCCs
    delta_mfccs = librosa.feature.delta(mfccs)
    features.extend(np.mean(delta_mfccs, axis=1))
    features.extend(np.std(delta_mfccs, axis=1))

    # 3. Chroma
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
    mean_rms = float(np.mean(rms))
    features.append(mean_rms)
    features.append(float(np.std(rms)))

    return np.array(features, dtype=np.float32), mean_rms


def predict_audio(audio_file) -> dict:
    """
    Analyse un fichier audio uploadé via Streamlit et retourne les prédictions.
    """
    import librosa

    try:
        clf, scaler, meta = _get_model()
    except FileNotFoundError as e:
        return {
            "probabilities": np.array([0, 0, 0, 0, 0, 1.0]),
            "timeline": [],
            "multi_species": False,
            "detected_species": [],
            "dominant_species": -1,
            "model_accuracy": 0.0,
            "error": str(e),
        }

    sample_rate = meta.get("sample_rate", 22050)
    window_duration = meta.get("window_duration", 3.0)
    hop_duration = meta.get("hop_duration", 1.5)
    n_mfcc = meta.get("n_mfcc", 40)
    model_accuracy = meta.get("accuracy", 0.0)

    # ── Charger l'audio ────────────────────────────────────────────
    try:
        audio_file.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        y, sr = librosa.load(tmp_path, sr=sample_rate, mono=True)
        os.unlink(tmp_path)
    except Exception as e:
        return {
            "probabilities": np.array([0, 0, 0, 0, 0, 1.0]),
            "timeline": [],
            "multi_species": False,
            "detected_species": [],
            "dominant_species": -1,
            "model_accuracy": model_accuracy,
            "error": f"Erreur de chargement audio : {e}",
        }

    duration = len(y) / sr
    window_samples = int(window_duration * sr)
    hop_samples = int(hop_duration * sr)

    # ── Prédictions par fenêtre ────────────────────────────────────
    window_results = []  # list of {"t_start", "t_end", "proba", "rms"}

    def _predict_segment(segment, t_start, t_end):
        feat, rms_val = _extract_features(segment, sr, n_mfcc)
        feat_scaled = scaler.transform(feat.reshape(1, -1))
        proba = clf.predict_proba(feat_scaled)[0]  # shape (5,)
        return {"t_start": t_start, "t_end": t_end, "proba": proba, "rms": rms_val}

    if duration <= window_duration:
        res = _predict_segment(y, 0.0, duration)
        window_results.append(res)
    else:
        start_sample = 0
        while start_sample + window_samples <= len(y):
            t_start = start_sample / sr
            t_end = t_start + window_duration
            segment = y[start_sample : start_sample + window_samples]
            res = _predict_segment(segment, t_start, t_end)
            window_results.append(res)
            start_sample += hop_samples

        if start_sample < len(y):
            segment = y[start_sample:]
            t_start = start_sample / sr
            t_end = duration
            if len(segment) > int(0.5 * sr):
                res = _predict_segment(segment, t_start, t_end)
                window_results.append(res)

    # ── Agréger les probabilités globales ──────────────────────────
    all_probas = np.array([r["proba"] for r in window_results])
    mean_proba = np.mean(all_probas, axis=0)  # peut être taille 5 ou 6
    n_expected = len(mean_proba)

    # ── Calcul du Bruit ─────────────────────────────────────────────
    # Si le modèle a 6 classes, la 6ème (index 5) est 'Bruit'
    if n_expected == 6:
        # Enlever la classe de bruit pour les probabilités d'espèces (pour l'interface)
        final_species_probas = mean_proba[:5]
        noise_proba_model = float(mean_proba[5])
    else:
        # Fallback pour le modèle v1 (5 classes)
        final_species_probas = mean_proba
        max_sp_proba = float(np.max(mean_proba))
        if max_sp_proba < NOISE_THRESHOLD:
            noise_proba_model = 1.0 - max_sp_proba
        else:
            noise_proba_model = max(0.0, 1.0 - float(np.sum(mean_proba[mean_proba >= 0.25])))

    # Énergie minimale (silence total) → forcer bruit à 100%
    avg_energy = np.mean([r["rms"] for r in window_results])
    if avg_energy < ENERGY_THRESHOLD:
        noise_proba = 1.0
        final_species_probas = np.zeros(5)
    else:
        noise_proba = noise_proba_model

    # Assembler le vecteur final de 6 éléments [esp0..4, bruit]
    probabilities = np.append(final_species_probas, noise_proba)
    probabilities = probabilities / probabilities.sum()

    # ── Chronologie par fenêtre ───────────────────────────────────
    timeline = []
    for r in window_results:
        proba = r["proba"]
        rms_val = r["rms"]
        best_idx = int(np.argmax(proba))
        
        # Mapping index vers UI (-1 pour Bruit)
        if len(proba) == 6 and best_idx == 5:
            # Le modèle a classé ce segment comme Bruit
            ui_idx = -1
        elif rms_val < ENERGY_THRESHOLD:
            # Silence total
            ui_idx = -1
        elif len(proba) == 5 and proba[best_idx] < NOISE_THRESHOLD:
            # Pas assez de confiance (Modèle v1)
            ui_idx = -1
        else:
            # Animal détecté !
            ui_idx = best_idx

        timeline.append({
            "t_start": r["t_start"],
            "t_end": r["t_end"],
            "species_idx": ui_idx,
            "confidence": float(proba[best_idx]) if ui_idx != -1 else (1.0 - float(proba[best_idx]) if len(proba)==6 else 0.5),
        })

    # ── Détecter les espèces présentes ────────────────────────────
    detected_species = sorted(set(
        r["species_idx"] for r in timeline if r["species_idx"] != -1
    ))

    multi_species = len(detected_species) > 1

    # Espèce dominante (animal uniquement)
    if np.max(final_species_probas) < 0.1 and noise_proba > 0.8:
        dominant_species = -1
    else:
        dominant_species = int(np.argmax(final_species_probas))

    return {
        "probabilities": probabilities,
        "timeline": timeline,
        "multi_species": multi_species,
        "detected_species": detected_species,
        "dominant_species": dominant_species,
        "model_accuracy": model_accuracy,
        "error": None,
    }


def is_model_ready() -> bool:
    """Retourne True si le modèle entraîné est disponible."""
    return _CLF_PATH.exists() and _SCALER_PATH.exists()
