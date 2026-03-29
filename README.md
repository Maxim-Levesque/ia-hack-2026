# IA Hack 2026 — Detection des sons de mammiferes marins

> **Equipe E** — Cegep de Riviere-du-Loup  
> Justin Chamberlant · Mathis Dube-Tremblay · Ridwane Berfroi · Maxim Levesque

Application Streamlit de classification automatique des vocalisations de mammiferes marins du Saint-Laurent, developpee dans le cadre du **Defi #1 — IA Hack 2026**.

---

## Fonctionnalites

L'application permet de :
- **Analyser** un fichier audio (WAV / MP3 / FLAC) et identifier les especes presentes
- **Visualiser** la forme d'onde et le spectrogramme avec un lecteur audio synchronise
- **Explorer** une chronologie des detections sur la duree de l'enregistrement
- **Consulter** la fiche de chaque espece (frequences, signature acoustique, statut)
- **Comprendre** l'architecture complete du système ML (page Informations)

### Especes detectees
| Espece | Frequences | Precision modele |
|--------|-----------|-----------------|
| Beluga (*Delphinapterus leucas*) | 2 — 12 kHz | 94 % |
| Rorqual commun (*Balaenoptera physalus*) | 15 — 30 Hz | 96 % |
| Baleine à bosse (*Megaptera novaeangliae*) | 20 Hz — 8 kHz | 98 % |
| Cachalot (*Physeter macrocephalus*) | 10 — 30 kHz | 99 % |
| Dauphin à flancs blancs (*Lagenorhynchus acutus*) | 1 — 20 kHz | 97 % |

---

## Installation et Utilisation (Localhost)

Ce projet necessite **Python 3.11+** et **Git**.

### 1. Cloner le depot
```bash
git clone https://github.com/Maxim-Levesque/ia-hack-2026.git
cd ia-hack-2026
```

### 2. Creer et activer l'environnement virtuel
- **Windows** :
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **macOS / Linux** :
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

### 3. Installer les dependances
```bash
pip install -r requirements.txt
```

### 4. Entrainer le modele
Le modele entraine (`.pkl`) est genere a partir des donnees du dossier `Ressources/`.
```bash
python train_model.py
```
Cela genere : `model/classifier.pkl`, `model/scaler.pkl` et `model/metadata.pkl`.

### 5. Lancer l'interface locale
Pour ouvrir l'application dans votre navigateur :
```bash
streamlit run app.py
```
L'URL locale sera : [http://localhost:8501](http://localhost:8501)

---

## Evaluation du modele

Pour tester la precision du modele et generer la matrice de confusion sur le jeu de test :
```bash
python evaluate_model.py
```

### Resultats de la dernière evaluation
Voici la performance obtenue sur les donnees de test :

```text
                    Beluga   Rorqual  Baleine  Cachalot  Dauphin   Bruit
Beluga                 42        0        0        0        0        0
Rorqual Commun          0        9        0        0        0        0
Baleine à bosse         0        0       15        0        0        0
Cachalot                0        0        0       16        0        0
Dauphin à flancs        0        0        0        0       17        0
Bruit                   0        0        0        0        0        4
```

---

## Deploiement sur Serveur (Optionnel)

### Script de deploiement rapide (Ubuntu / Proxmox)
```bash
curl -sSL https://raw.githubusercontent.com/Maxim-Levesque/ia-hack-2026/main/deploy.sh | sudo bash
```

### Deploiement Cloud (Streamlit Cloud)
1. Poussez votre code sur GitHub.
2. Connectez votre compte sur [share.streamlit.io](https://share.streamlit.io).
3. Creez une "New app" pointant sur `app.py`.

---

## Structure du projet
```
.
├── app.py                  # Point d'entree Streamlit (navigation, layout)
├── train_model.py          # Script d'entrainement
├── evaluate_model.py       # Script d'evaluation (Matrice de confusion)
├── requirements.txt        # Dependances Python
├── assets/                 # CSS, Images et extraits audio
├── model/                  # Modele entraine et Predictor.py
└── pages_custom/           # Pages de l'application (Accueil, Analyse, etc.)
```

---

## Licence
Projet academique — IA Hack 2026 — Cegep de Riviere-du-Loup.
