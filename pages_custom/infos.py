"""Page Informations — Fonctionnement detaille du systeme de classification."""
import streamlit as st  # type: ignore

# SVG icons inline (Feather/Lucide style)
_ICON = {
    "music": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "scissors": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/></svg>',
    "bar-chart": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    "cpu": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "trending-up": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "sliders": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "zap": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "activity": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "target": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "maximize": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>',
    "crosshair": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>',
    "align-left": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="13" y1="18" x2="3" y2="18"/></svg>',
    "battery": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="18" height="12" rx="2"/><line x1="23" y1="13" x2="23" y2="11"/></svg>',
    "grid": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "code": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
    "package": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
    "save": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
    "layers": '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
}


def _ico(name: str, color: str = "#4dc8ff") -> str:
    """Retourne un SVG inline avec la couleur demandee."""
    svg = _ICON.get(name, "")
    return svg.replace('stroke="currentColor"', f'stroke="{color}"')


def render():
    st.markdown(
        """<div class="page-header">
  <h1 class="main-title">Informations</h1>
  <div class="subtitle">
    <span>Fonctionnement du systeme</span>
    <span class="dot">&bull;</span>
    <span>Architecture &amp; Methodologie</span>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Section 1 — Vue d'ensemble du pipeline
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title' style='margin-top:10px;'>Vue d'ensemble du pipeline</div>",
        unsafe_allow_html=True,
    )

    pip_steps = [
        (_ico("music", "#00d2ff"),      "#00d2ff", "ETAPE 1", "Chargement Audio",    "Fichier WAV / MP3 / FLAC chargé via Librosa au taux d'échantillonnage du modèle (22 050 Hz)"),
        (_ico("scissors", "#3a7bd5"),   "#3a7bd5", "ETAPE 2", "Fenêtrage",           "Signal découpé en fenêtres glissantes de 2 s avec un saut de 0,5 s (25 % de chevauchement)"),
        (_ico("sliders", "#8e44ad"),    "#8e44ad", "ETAPE 3", "Extraction Features", "MFCC × 40, Delta MFCC, Chroma, Centroïde spectral, Rolloff, ZCR, RMS — 182 features/fenêtre"),
        (_ico("cpu", "#00b894"),        "#00b894", "ETAPE 4", "Classification",      "Random Forest (300 arbres, StandardScaler) prédit la probabilité d'appartenance à chaque espèce"),
        (_ico("trending-up", "#fdcb6e"),"#fdcb6e", "ETAPE 5", "Agrégation",         "Moyenne des probabilités par fenêtre + filtrage intelligent par durée cumulée et seuil"),
    ]

    pip_cards = ""
    for i, (ico, color, num, name, desc) in enumerate(pip_steps):
        arrow = '<div class="pip-arrow">&#8594;</div>' if i < len(pip_steps) - 1 else ""
        pip_cards += f"""
        <div class="pip-step" style="border-bottom: 3px solid {color};">
          <span class="pip-num">{num}</span>
          <div class="pip-ico" style="color:{color};">{ico}</div>
          <div class="pip-name">{name}</div>
          <div class="pip-desc">{desc}</div>
        </div>
        {arrow}"""

    pipeline_html = """
<style>
.pip-container{display:flex;align-items:stretch;justify-content:center;gap:0;margin:28px 0;flex-wrap:wrap;}
.pip-step{flex:1 1 160px;max-width:200px;background:rgba(5,25,55,0.7);border:1px solid rgba(0,150,255,0.18);border-radius:16px;padding:22px 14px;text-align:center;position:relative;transition:transform 0.25s ease,box-shadow 0.25s ease;}
.pip-step:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,100,255,0.25);background:rgba(5,30,70,0.85);}
.pip-arrow{display:flex;align-items:center;justify-content:center;color:#0088ff;font-size:1.2rem;opacity:0.4;padding:0 4px;flex-shrink:0;align-self:center;}
.pip-ico{margin-bottom:12px;display:flex;justify-content:center;}
.pip-num{position:absolute;top:10px;left:12px;font-size:0.65rem;font-weight:800;color:#0088ff;letter-spacing:0.08em;opacity:0.7;}
.pip-name{font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:700;color:#c8e8ff;margin-bottom:6px;}
.pip-desc{font-size:0.72rem;color:#5588aa;line-height:1.4;}
@media(max-width:700px){.pip-arrow{display:none;}.pip-step{max-width:100%;}}
</style>
<div class="pip-container">""" + pip_cards + "</div>"

    st.markdown(pipeline_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 2 — Features acoustiques
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Les fonctionalités acoustiques</div>",
        unsafe_allow_html=True,
    )

    feat_data = [
        ("sliders",     "#4dc8ff", "MFCC",                    "80 valeurs",  "Mel-Frequency Cepstral Coefficients — 40 coefficients en moyenne + 40 en écart-type. Capture la forme spectrale de l'enveloppe vocale, caractéristique de l'espèce."),
        ("zap",         "#4dc8ff", "Delta MFCC",              "80 valeurs",  "Dérivée temporelle des MFCC. Mesure la vitesse de variation spectrale et capte la dynamique temporelle des vocalisations (clics vs chants continus)."),
        ("grid",        "#4dc8ff", "Chroma",                  "12 valeurs",  "Distribution de l'énergie sur 12 classes de hauteur musicale. Utile pour les espèces produisant des sons tonaux comme le béluga et la baleine à bosse."),
        ("crosshair",   "#4dc8ff", "Centroïde Spectral",      "2 valeurs",   "Fréquence «centre de gravité» du spectre. Distingue les sons graves du rorqual commun (20 Hz) des sifflements aigus du dauphin (kHz)."),
        ("maximize",    "#4dc8ff", "Bande Passante Spectrale", "2 valeurs",  "Largeur du spectre autour du centroïde. Un cachalot avec ses clics percussifs montre une bande très large, contrairement aux sons purs du rorqual."),
        ("battery",     "#4dc8ff", "Rolloff Spectral",         "2 valeurs",  "Fréquence en dessous de laquelle 85 % de l'énergie est concentrée. Permet de distinguer les sons à haute fréquence des sons à basse fréquence."),
        ("activity",    "#4dc8ff", "Zero Crossing Rate",       "2 valeurs",  "Nombre de fois que le signal passe par zéro par seconde. Élevé pour les clics de dauphin impulsifs, faible pour les sons tonaux graves."),
        ("bar-chart",   "#4dc8ff", "Énergie RMS",              "2 valeurs",  "Root Mean Square Energy — mesure l'amplitude globale. Sert de filtre de silence : si RMS < 0.002, le segment est classé bruit/silence."),
    ]

    feat_cards = ""
    for ico_name, color, name, badge, desc in feat_data:
        feat_cards += f"""
        <div class="feat-card">
          <div class="feat-hdr">
            <div class="feat-ico" style="color:{color};">{_ico(ico_name, color)}</div>
            <span class="feat-name">{name}</span>
          </div>
          <div class="feat-desc">{desc}</div>
        </div>"""

    features_html = """
<style>
.feat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:20px 0 10px;}
.feat-card{background:rgba(5,20,50,0.6);border:1px solid rgba(0,150,255,0.15);border-radius:14px;padding:18px 20px;transition:border-color 0.2s,background 0.2s;}
.feat-card:hover{border-color:rgba(0,200,255,0.35);background:rgba(0,30,80,0.7);}
.feat-hdr{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.feat-ico{display:flex;flex-shrink:0;}
.feat-name{font-family:'Space Grotesk',sans-serif;font-size:0.9rem;font-weight:700;color:#4dc8ff;flex-grow:1;}
.feat-desc{font-size:0.8rem;color:#6699bb;line-height:1.5;}
</style>
<div class="feat-grid">""" + feat_cards + "</div>"""

    st.markdown(features_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 3 — Modèle Random Forest
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Le modèle : Random Forest</div>",
        unsafe_allow_html=True,
    )

    rf_html = """
<style>
.rf-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0 30px;}
@media(max-width:600px){.rf-grid{grid-template-columns:1fr;}}
.rf-block{background:rgba(5,20,50,0.6);border:1px solid rgba(0,150,255,0.15);border-radius:14px;padding:20px 22px;}
.rf-block-title{font-family:'Space Grotesk',sans-serif;font-size:0.85rem;font-weight:700;color:#a0d8f0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid rgba(0,150,255,0.12);}
.rf-param{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.rf-param-name{font-size:0.82rem;color:#6699bb;}
.rf-param-val{font-family:'Space Grotesk',monospace;font-size:0.88rem;font-weight:700;color:#4dc8ff;background:rgba(0,100,200,0.15);border:1px solid rgba(0,150,255,0.2);border-radius:8px;padding:3px 10px;}
.rf-why-item{display:flex;gap:10px;align-items:flex-start;margin-bottom:12px;}
.rf-why-dot{width:6px;height:6px;border-radius:50%;background:#0088ff;flex-shrink:0;margin-top:7px;}
.rf-why-text{font-size:0.82rem;color:#6699bb;line-height:1.5;}
</style>
<div class="rf-grid">
  <div class="rf-block">
    <div class="rf-block-title">Hyperparamètres</div>
    <div class="rf-param"><span class="rf-param-name">Algorithme</span><span class="rf-param-val">Random Forest</span></div>
    <div class="rf-param"><span class="rf-param-name">Nombre d'arbres</span><span class="rf-param-val">300</span></div>
    <div class="rf-param"><span class="rf-param-name">Normalisation</span><span class="rf-param-val">StandardScaler</span></div>
    <div class="rf-param"><span class="rf-param-name">Fenêtre d'analyse</span><span class="rf-param-val">2.0 s</span></div>
    <div class="rf-param"><span class="rf-param-name">Saut (Hop)</span><span class="rf-param-val">0.5 s (25 %)</span></div>
    <div class="rf-param"><span class="rf-param-name">Taux d'échantillonnage</span><span class="rf-param-val">22 050 Hz</span></div>
    <div class="rf-param"><span class="rf-param-name">Seuil de confiance</span><span class="rf-param-val">0.55</span></div>
    <div class="rf-param"><span class="rf-param-name">Seuil énergie (silence)</span><span class="rf-param-val">0.002 RMS</span></div>
  </div>
  <div class="rf-block">
    <div class="rf-block-title">Pourquoi Random Forest ?</div>
    <div class="rf-why-item"><div class="rf-why-dot"></div><div class="rf-why-text"><strong style="color:#a0d8f0">Robustesse</strong> — Fonctionne bien même avec des données audio bruitées ou des enregistrements de qualité variable (hydrophones, profondeur variable).</div></div>
    <div class="rf-why-item"><div class="rf-why-dot"></div><div class="rf-why-text"><strong style="color:#a0d8f0">Interprétabilité</strong> — Permet d'analyser l'importance de chaque feature acoustique pour comprendre quels attributs distinguent chaque espèce.</div></div>
    <div class="rf-why-item"><div class="rf-why-dot"></div><div class="rf-why-text"><strong style="color:#a0d8f0">Probabilités calibrées</strong> — Retourne des probabilités par classe qu'on agrège sur toutes les fenêtres temporelles pour une prédiction globale fiable.</div></div>
    <div class="rf-why-item"><div class="rf-why-dot"></div><div class="rf-why-text"><strong style="color:#a0d8f0">Rapidité d'inférence</strong> — Idéal pour un outil temps-réel : une prédiction prend moins de 50 ms par fenêtre de 2 secondes.</div></div>
  </div>
</div>"""
    st.markdown(rf_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 4 — Classes détectées
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Classes de classification</div>",
        unsafe_allow_html=True,
    )

    classes_html = """
<style>
.cls-table{width:100%;border-collapse:collapse;margin:20px 0 30px;font-size:0.85rem;}
.cls-table th{font-family:'Space Grotesk',sans-serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#4477aa;padding:10px 16px;border-bottom:1px solid rgba(0,150,255,0.15);text-align:left;background:rgba(0,20,50,0.3);}
.cls-table td{padding:12px 16px;border-bottom:1px solid rgba(0,150,255,0.06);color:#8ab8d8;vertical-align:top;}
.cls-table tr:hover td{background:rgba(0,40,90,0.3);}
.cls-name{color:#c8e8ff;font-weight:600;}
.cls-freq{font-family:'Space Grotesk',monospace;color:#00ccff;font-weight:700;font-size:0.82rem;white-space:nowrap;}
.cls-acc{display:inline-block;background:rgba(0,180,100,0.15);border:1px solid rgba(0,180,100,0.25);border-radius:20px;padding:2px 10px;font-family:'Space Grotesk',monospace;font-weight:700;color:#00cc77;font-size:0.82rem;}
</style>
<table class="cls-table">
  <thead>
    <tr>
      <th>Espece</th>
      <th>Nom latin</th>
      <th>Frequences</th>
      <th>Signature acoustique</th>
      <th>Precision</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="cls-name">Beluga</span></td>
      <td style="font-style:italic;color:#3a7aaa;">Delphinapterus leucas</td>
      <td><span class="cls-freq">2 — 12 kHz</span></td>
      <td>Clics d'echolocation, sifflements, trilles varies</td>
      <td><span class="cls-acc">94 %</span></td>
    </tr>
    <tr>
      <td><span class="cls-name">Rorqual commun</span></td>
      <td style="font-style:italic;color:#3a7aaa;">Balaenoptera physalus</td>
      <td><span class="cls-freq">15 — 30 Hz</span></td>
      <td>Impulsions tres courtes de basse frequence (~20 Hz)</td>
      <td><span class="cls-acc">96 %</span></td>
    </tr>
    <tr>
      <td><span class="cls-name">Baleine a bosse</span></td>
      <td style="font-style:italic;color:#3a7aaa;">Megaptera novaeangliae</td>
      <td><span class="cls-freq">20 Hz — 8 kHz</span></td>
      <td>Chants complexes et melodieux, longues sequences</td>
      <td><span class="cls-acc">98 %</span></td>
    </tr>
    <tr>
      <td><span class="cls-name">Cachalot</span></td>
      <td style="font-style:italic;color:#3a7aaa;">Physeter macrocephalus</td>
      <td><span class="cls-freq">10 — 30 kHz</span></td>
      <td>Clics tres puissants et rythmes (codas), echolocation</td>
      <td><span class="cls-acc">99 %</span></td>
    </tr>
    <tr>
      <td><span class="cls-name">Dauphin flancs blancs</span></td>
      <td style="font-style:italic;color:#3a7aaa;">Lagenorhynchus acutus</td>
      <td><span class="cls-freq">1 — 20 kHz</span></td>
      <td>Rafales de clics rapides et sifflements modules</td>
      <td><span class="cls-acc">97 %</span></td>
    </tr>
    <tr>
      <td><span class="cls-name" style="color:#8ab8d8;">Bruit de fond</span></td>
      <td style="font-style:italic;color:#3a7aaa;">— / silence</td>
      <td><span class="cls-freq" style="color:#5588aa;">variable</span></td>
      <td>Bruit ambiant, silence, sons non-biologiques</td>
      <td><span class="cls-acc">99 %</span></td>
    </tr>
  </tbody>
</table>"""
    st.markdown(classes_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 5 — Logique de filtrage intelligente
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Filtrage post-inference intelligent</div>",
        unsafe_allow_html=True,
    )

    filter_steps = [
        ("Filtre d'energie (silence)",      "Si l'energie RMS moyenne d'une fenetre est inferieure a <span class='code-pill'>0.002</span>, le segment est automatiquement classe comme bruit/silence, independamment des probabilites du modele."),
        ("Seuil de confiance",              "Pour le modele 5-classes, si la probabilite maximale de l'espece dominante est inferieure a <span class='code-pill'>0.55</span>, la fenetre est consideree comme bruit. Cela reduit les faux positifs."),
        ("Filtrage par duree minimale",     "Une espece n'est affichee que si sa duree cumulee detectee est superieure a <span class='code-pill'>0.8 s</span> ET sa probabilite superieure a <span class='code-pill'>10 %</span>. Supprime les artefacts courts."),
        ("Redistribution vers le bruit",    "Les probabilites des especes filtrees sont ajoutees au bruit de fond pour que la somme reste toujours egale a <span class='code-pill'>100 %</span>."),
        ("Fusion de la chronologie",        "Les fenetres consecutives de meme espece sont fusionnees en un seul bloc dans la chronologie pour une visualisation claire de la ligne du temps."),
    ]

    filt_items = ""
    for i, (title, desc) in enumerate(filter_steps):
        filt_items += f"""
        <div class="filt-step">
          <div class="filt-step-num">{i+1}</div>
          <div>
            <div class="filt-step-title">{title}</div>
            <div class="filt-step-desc">{desc}</div>
          </div>
        </div>"""

    filter_html = """
<style>
.filt-steps{display:flex;flex-direction:column;gap:12px;margin:20px 0 30px;}
.filt-step{display:flex;gap:16px;align-items:flex-start;background:rgba(5,20,50,0.55);border:1px solid rgba(0,150,255,0.13);border-radius:14px;padding:16px 20px;transition:background 0.2s;}
.filt-step:hover{background:rgba(0,30,75,0.7);}
.filt-step-num{width:32px;height:32px;border-radius:50%;flex-shrink:0;background:linear-gradient(135deg,#0055cc,#0088ff);display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:800;color:#fff;}
.filt-step-title{font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:700;color:#a0d8f0;margin-bottom:4px;}
.filt-step-desc{font-size:0.8rem;color:#6699bb;line-height:1.5;}
.code-pill{background:rgba(0,0,0,0.4);border:1px solid rgba(0,150,255,0.2);border-radius:6px;padding:1px 8px;font-family:monospace;font-size:0.78rem;color:#4dc8ff;}
</style>
<div class="filt-steps">""" + filt_items + "</div>"

    st.markdown(filter_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 6 — Stack technique
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Stack technique</div>",
        unsafe_allow_html=True,
    )

    stack_items = [
        ("code",      "#4dc8ff", "Python 3.11+",  "Langage principal"),
        ("layers",    "#4dc8ff", "Streamlit",      "Interface web interactive"),
        ("activity",  "#4dc8ff", "Librosa",        "Analyse audio & extraction MFCC"),
        ("target",    "#4dc8ff", "Scikit-learn",   "Random Forest & StandardScaler"),
        ("bar-chart", "#4dc8ff", "NumPy",          "Calculs vectoriels sur les features"),
        ("trending-up","#4dc8ff","Plotly",         "Visualisations interactives"),
        ("save",      "#4dc8ff", "Joblib",         "Serialisation du modele (.pkl)"),
        ("package",   "#4dc8ff", "CSS / HTML",     "Design glassmorphism custom"),
    ]

    stack_cards = ""
    for ico_name, color, name, role in stack_items:
        stack_cards += f"""
        <div class="stack-card">
          <div class="stack-ico" style="color:{color};">{_ico(ico_name, color)}</div>
          <div class="stack-name">{name}</div>
          <div class="stack-role">{role}</div>
        </div>"""

    stack_html = """
<style>
.stack-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin:20px 0 30px;}
.stack-card{background:rgba(5,20,50,0.6);border:1px solid rgba(0,150,255,0.14);border-radius:14px;padding:16px 18px;text-align:center;transition:transform 0.2s,box-shadow 0.2s;}
.stack-card:hover{transform:translateY(-3px);box-shadow:0 8px 30px rgba(0,100,255,0.2);}
.stack-ico{display:flex;justify-content:center;margin-bottom:10px;}
.stack-name{font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:700;color:#c8e8ff;margin-bottom:4px;}
.stack-role{font-size:0.72rem;color:#4477aa;line-height:1.3;}
</style>
<div class="stack-grid">""" + stack_cards + "</div>"

    st.markdown(stack_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Section 7 — Contexte du projet
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title'>Contexte du projet</div>",
        unsafe_allow_html=True,
    )

    context_html = """
<div style="background:rgba(5,20,50,0.55);border:1px solid rgba(0,150,255,0.14);border-radius:16px;padding:24px 28px;margin:20px 0 10px;line-height:1.7;">
  <p style="color:#8ab8d8;font-size:0.9rem;margin:0 0 14px 0;">
    Ce projet a ete realise dans le cadre du <strong style="color:#c8e8ff">IA Hack 2026</strong>, un hackathon organise au Cégep de Rimouski.
    Le defi #1 consistait a developper un systeme de <strong style="color:#4dc8ff">detection et classification automatique
    des sons de mammiferes marins</strong> du Saint-Laurent a partir d'enregistrements hydrophones.
  </p>
  <p style="color:#8ab8d8;font-size:0.9rem;margin:0 0 14px 0;">
    La conservation des mammiferes marins du Saint-Laurent est un enjeu ecologique majeur. La capacite a
    identifier automatiquement les especes par leur signature acoustique permet aux chercheurs de surveiller
    les populations sans perturber les animaux, et d'analyser de grandes quantites de donnees audio
    collectees en continu par des bouees acoustiques.
  </p>
  <p style="color:#6699bb;font-size:0.82rem;margin:0;">
    <strong style="color:#a0d8f0">Donnees d'entrainement :</strong> Fichiers WAV issus de bases de donnees publiques de vocalisations
    de mammiferes marins (MBARI, NOAA, etc.), augmentes et equilibres par espece pour eviter les biais de classe.
  </p>
</div>"""
    st.markdown(context_html, unsafe_allow_html=True)
