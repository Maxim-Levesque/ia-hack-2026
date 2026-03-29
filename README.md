# IA Hack 2026 — Détection des sons de mammifères marins

> **Équipe E** — Cégep de Rivière-du-Loup  
> Justin Chamberlant · Mathis Dubé-Tremblay · Ridwane Berfroi · Maxim Lévesque

Application Streamlit de classification automatique des vocalisations de mammifères marins du Saint-Laurent, développée dans le cadre du **Défi #1 — IA Hack 2026**.

---

## ⚡ Déploiement rapide (Ubuntu / Proxmox)

```bash
curl -sSL https://raw.githubusercontent.com/Maxim-Levesque/ia-hack-2026/main/deploy.sh | sudo bash
```

Cette commande installe tout automatiquement et lance l'app comme service système.  
L'application sera accessible sur `http://VOTRE_IP:8501`.

---


L'application permet de :
- **Analyser** un fichier audio (WAV / MP3 / FLAC) et identifier les espèces de mammifères marins présentes
- **Visualiser** la forme d'onde ou le spectrogramme avec un lecteur audio synchronisé
- **Explorer** une chronologie des détections sur la durée de l'enregistrement
- **Consulter** la fiche de chaque espèce détectable (fréquences, signature acoustique, statut)
- **Comprendre** l'architecture complète du système ML (page Informations)

### Espèces détectées
| Espèce | Fréquences | Précision modèle |
|--------|-----------|-----------------|
| Béluga (*Delphinapterus leucas*) | 2 — 12 kHz | 94 % |
| Rorqual commun (*Balaenoptera physalus*) | 15 — 30 Hz | 96 % |
| Baleine à bosse (*Megaptera novaeangliae*) | 20 Hz — 8 kHz | 98 % |
| Cachalot (*Physeter macrocephalus*) | 10 — 30 kHz | 99 % |
| Dauphin à flancs blancs (*Lagenorhynchus acutus*) | 1 — 20 kHz | 97 % |

---

## Prérequis

- **Python 3.11+**
- **Git**
- (Optionnel) Les données d'entraînement pour ré-entraîner le modèle

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/<votre-utilisateur>/<votre-repo>.git
cd <votre-repo>
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

Activer l'environnement :

- **Windows (PowerShell)**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**
  ```bash
  source .venv/bin/activate
  ```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Entraîner le modèle *(requis avant la première utilisation)*

Le modèle entraîné (`.pkl`) n'est pas inclus dans le dépôt (fichiers binaires volumineux).  
Placez vos données d'entraînement dans le dossier `Ressources/` selon la structure suivante :

```
Ressources/
├── Beluga_WhiteWhale/
│   └── *.wav
├── Fin_FinbackWhale/
│   └── *.wav
├── HumpbackWhale/
│   └── *.wav
├── SpermWhale/
│   └── *.wav
├── White_sidedDolphin/
│   └── *.wav
└── Noise/
    └── *.wav
```

Puis lancez l'entraînement :

```bash
python train_model.py
```

Cela génère automatiquement `model/classifier.pkl`, `model/scaler.pkl` et `model/metadata.pkl`.

### 5. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre sur [http://localhost:8501](http://localhost:8501).

---

## Déploiement sur Streamlit Cloud

### Étape 1 — Pousser le code sur GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Étape 2 — Créer un compte Streamlit Cloud

Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez votre compte GitHub.

### Étape 3 — Déployer l'application

1. Cliquez sur **"New app"**
2. Sélectionnez votre dépôt GitHub
3. Branche : `main`
4. Fichier principal : `app.py`
5. Cliquez sur **"Deploy"**

> **Important :** Le modèle `.pkl` doit être inclus dans le dépôt pour que Streamlit Cloud puisse l'utiliser. Si les fichiers sont trop volumineux (> 100 MB), utilisez [Git LFS](https://git-lfs.github.com/) ou hébergez-les séparément.

#### Avec Git LFS (si modèle > 100 MB)

```bash
git lfs install
git lfs track "model/*.pkl"
git add .gitattributes
git add model/
git commit -m "Add model with LFS"
git push origin main
```

---

## Déploiement alternatif — Serveur Linux (VPS / Render / Railway)

### Avec `screen` ou `tmux`

```bash
pip install -r requirements.txt
python train_model.py  # si le modèle n'est pas présent
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Avec un fichier `Procfile` (Heroku / Render)

Créez un fichier `Procfile` à la racine :

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Structure du projet

```
.
├── app.py                  # Point d'entrée Streamlit (navigation, layout)
├── train_model.py          # Script d'entraînement du Random Forest
├── requirements.txt        # Dépendances Python
├── .gitignore
├── README.md
│
├── assets/
│   ├── style.css           # Design system glassmorphism
│   ├── images/             # Images des espèces + logo
│   └── audio/              # Extraits audio par espèce
│
├── model/
│   ├── predictor.py        # Module d'inférence (fenêtrage + features + RF)
│   ├── classifier.pkl      # [généré] Modèle Random Forest entraîné
│   ├── scaler.pkl          # [généré] StandardScaler
│   └── metadata.pkl        # [généré] Paramètres du modèle
│
└── pages_custom/
    ├── home.py             # Page d'accueil (pipeline, métriques)
    ├── analyse.py          # Page d'analyse audio
    ├── especes.py          # Répertoire des espèces
    └── infos.py            # Page d'informations techniques
```

---

## Pipeline ML

```
Audio WAV/MP3
    ↓
Librosa (22 050 Hz, mono)
    ↓
Fenêtres 2s (hop 0.5s)
    ↓
182 features / fenêtre
  ├─ MFCC × 40 (mean + std)
  ├─ Delta MFCC × 40 (mean + std)
  ├─ Chroma × 12
  ├─ Centroïde spectral (mean + std)
  ├─ Bande passante (mean + std)
  ├─ Rolloff (mean + std)
  ├─ Zero Crossing Rate (mean + std)
  └─ RMS Energy (mean + std)
    ↓
StandardScaler
    ↓
Random Forest (300 arbres)
    ↓
Probabilités par espèce
    ↓
Agrégation + Filtrage
    ↓
Résultats + Chronologie
```

---

## Technologies

| Outil | Usage |
|-------|-------|
| [Streamlit](https://streamlit.io) | Interface web |
| [Librosa](https://librosa.org) | Analyse audio |
| [Scikit-learn](https://scikit-learn.org) | Random Forest |
| [NumPy](https://numpy.org) | Traitement vectoriel |
| [Plotly](https://plotly.com) | Visualisations |
| [Joblib](https://joblib.readthedocs.io) | Sérialisation du modèle |

---

## Licence

Projet académique — IA Hack 2026 — Cégep de Rivière-du-Loup.
