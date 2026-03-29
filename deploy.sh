#!/usr/bin/env bash
# ============================================================
#  deploy.sh — IA Hack 2026 · Déploiement Ubuntu (Proxmox)
#  Usage : curl -sSL https://raw.githubusercontent.com/Maxim-Levesque/ia-hack-2026/main/deploy.sh | bash
#       ou : chmod +x deploy.sh && ./deploy.sh
# ============================================================
set -e

# ── Couleurs ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERREUR]${NC} $1"; exit 1; }

echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     IA Hack 2026 — Déploiement automatique          ║"
echo "║     Détection sons mammifères marins                 ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Variables ────────────────────────────────────────────────
REPO_URL="https://github.com/Maxim-Levesque/ia-hack-2026.git"
APP_DIR="/opt/ia-hack-2026"
VENV_DIR="$APP_DIR/.venv"
SERVICE_NAME="ia-hack"
PORT=8501
PYTHON_MIN="3.11"

# ── 1. Vérification root ─────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Ce script doit être exécuté en tant que root.\nRelancez avec : sudo bash deploy.sh"
fi

# ── 2. Mise à jour système + dépendances ─────────────────────
info "Mise à jour des paquets système..."
apt-get update -qq
apt-get install -y -qq \
    git python3 python3-pip python3-venv \
    libsndfile1 ffmpeg curl \
    > /dev/null 2>&1
success "Dépendances système installées"

# ── 3. Vérification version Python ───────────────────────────
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python détecté : $PY_VER"
if python3 -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)" 2>/dev/null; then
    success "Version Python compatible"
else
    warn "Python $PY_VER détecté — recommandé : 3.11+"
    warn "L'application devrait quand même fonctionner."
fi

# ── 4. Clone / Mise à jour du dépôt ─────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    info "Dépôt existant détecté — mise à jour..."
    cd "$APP_DIR"
    git pull origin main
    success "Code mis à jour"
else
    info "Clonage du dépôt dans $APP_DIR..."
    git clone "$REPO_URL" "$APP_DIR"
    success "Dépôt cloné"
fi
cd "$APP_DIR"

# ── 5. Environnement virtuel ─────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    info "Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
    success "Environnement virtuel créé"
fi

source "$VENV_DIR/bin/activate"

# ── 6. Installation des dépendances Python ───────────────────
info "Installation des dépendances Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
success "Dépendances Python installées"

# ── 7. Entraînement du modèle (si nécessaire) ────────────────
if [ -f "model/classifier.pkl" ] && [ -f "model/scaler.pkl" ]; then
    success "Modèle ML déjà entraîné — étape ignorée"
else
    warn "Modèle ML non trouvé."
    echo ""
    echo -e "  Pour entraîner le modèle, placez vos données dans :"
    echo -e "  ${BOLD}$APP_DIR/Ressources/${NC}"
    echo ""
    echo -e "  Structure attendue :"
    echo "    Ressources/"
    echo "    ├── Beluga_WhiteWhale/*.wav"
    echo "    ├── Fin_FinbackWhale/*.wav"
    echo "    ├── HumpbackWhale/*.wav"
    echo "    ├── SpermWhale/*.wav"
    echo "    ├── White_sidedDolphin/*.wav"
    echo "    └── Noise/*.wav"
    echo ""
    echo -e "  Puis lancez : ${BOLD}cd $APP_DIR && source .venv/bin/activate && python train_model.py${NC}"
    echo ""

    read -p "  Voulez-vous lancer l'entraînement maintenant ? (o/N) : " -r TRAIN_NOW
    if [[ "$TRAIN_NOW" =~ ^[Oo]$ ]]; then
        info "Lancement de l'entraînement..."
        python train_model.py
        success "Modèle entraîné avec succès"
    else
        warn "Entraînement ignoré — l'app démarrera sans modèle (mode dégradé)"
    fi
fi

# ── 8. Service systemd ────────────────────────────────────────
info "Configuration du service systemd..."

cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=IA Hack 2026 - Marine Mammal Sound Classifier
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/streamlit run app.py \\
    --server.port=$PORT \\
    --server.address=0.0.0.0 \\
    --server.headless=true \\
    --browser.gatherUsageStats=false
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}.service" > /dev/null 2>&1
systemctl restart "${SERVICE_NAME}.service"
success "Service systemd configuré et démarré"

# ── 9. Vérification ─────────────────────────────────────────
sleep 3
if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
    success "Service actif!"
else
    warn "Le service ne semble pas actif. Vérifiez les logs :"
    echo "    journalctl -u ${SERVICE_NAME} -n 50"
fi

# ── 10. Récap final ──────────────────────────────────────────
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Déploiement terminé!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Application accessible sur :"
echo -e "  ${BOLD}${CYAN}http://${SERVER_IP}:${PORT}${NC}"
echo ""
echo -e "  Commandes utiles :"
echo -e "  ${BOLD}systemctl status ${SERVICE_NAME}${NC}     — état du service"
echo -e "  ${BOLD}systemctl restart ${SERVICE_NAME}${NC}    — redémarrer"
echo -e "  ${BOLD}systemctl stop ${SERVICE_NAME}${NC}       — arrêter"
echo -e "  ${BOLD}journalctl -u ${SERVICE_NAME} -f${NC}     — logs en temps réel"
echo -e "  ${BOLD}cd $APP_DIR && git pull && systemctl restart ${SERVICE_NAME}${NC}  — mettre à jour"
echo ""
