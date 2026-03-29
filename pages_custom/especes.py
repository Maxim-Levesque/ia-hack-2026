"""Espèces page — gallery of marine mammals with info."""
import base64
import os
import streamlit as st  # type: ignore

# ── Species data ───────────────────────────────────────────────────────────────
SPECIES = [
    {
        "id": "beluga",
        "name": "Béluga",
        "latin": "Delphinapterus leucas",
        "emoji": "🤍",
        "freq": "2 — 12 kHz",
        "img": "assets/images/beluga.png",
        "color": "#0088ff",
        "statut": "En voie de disparition",
        "statut_color": "#ff4455",
        "taille": "3 — 5 m",
        "desc": (
            "Le béluga du Saint-Laurent est l'un des cétacés les plus emblématiques du Québec. "
            "Surnommé le « canari des mers » pour sa vocalisation riche et variée, il émet des clics, "
            "sifflements et trilles dans la plage 2–12 kHz."
        ),
        "audio_note": "Clics d'écholocation, sifflements, « meuglements »",
    },
    {
        "id": "rorqual_commun",
        "name": "Rorqual Commun (Fin Finback Whale)",
        "latin": "Balaenoptera physalus",
        "emoji": "🐋",
        "freq": "15 — 30 Hz",
        "img": "assets/images/rorqual_commun.png",
        "color": "#0055cc",
        "statut": "Vulnérable",
        "statut_color": "#ffaa00",
        "taille": "18 — 22 m",
        "desc": (
            "Le rorqual commun est le 2e plus grand animal au monde. Il produit des impulsions de basse "
            "fréquence, souvent autour de 20 Hz, qui peuvent voyager sur de grandes distances pour "
            "communiquer et s'orienter dans l'océan."
        ),
        "audio_note": "Impulsions courtes de très basse fréquence (20 Hz)",
    },
    {
        "id": "rorqual_a_bosse",
        "name": "Baleine à bosse",
        "latin": "Megaptera novaeangliae",
        "emoji": "🌊",
        "freq": "20 Hz — 8 kHz",
        "img": "assets/images/baleine_a_bosse.png",
        "color": "#0066aa",
        "statut": "Préoccupation mineure",
        "statut_color": "#22cc66",
        "taille": "12 — 16 m",
        "desc": (
            "Connu pour ses chants complexes et mélodieux, le rorqual à bosse "
            "est l'un des mammifères marins les plus vocaux. Ses séquences de chant peuvent durer "
            "plusieurs heures, notamment pour la reproduction."
        ),
        "audio_note": "Chants complexes et mélodieux, longues séquences",
    },
    {
        "id": "cachalot",
        "name": "Cachalot (Sperm Whale)",
        "latin": "Physeter macrocephalus",
        "emoji": "🦑",
        "freq": "10 — 30 kHz",
        "img": "assets/images/cachalot.png",
        "color": "#4d94ff",
        "statut": "Vulnérable",
        "statut_color": "#ffaa00",
        "taille": "12 — 18 m",
        "desc": (
            "Le cachalot possède le plus gros cerveau du règne animal. Il plonge à de grandes profondeurs "
            "et utilise de puissants clics d'écholocation directionnels (jusqu'à 235 dB) pour chasser "
            "le calmar géant dans l'obscurité totale des abysses."
        ),
        "audio_note": "Clics très puissants et rythmés (codas) pour l'écholocation",
    },
    {
        "id": "dauphin_flancs_blancs",
        "name": "Dauphin à flancs blancs (White sided Dolphin)",
        "latin": "Lagenorhynchus acutus",
        "emoji": "🐬",
        "freq": "1 — 20 kHz",
        "img": "assets/images/Dauphin_flancs_blancs.jpg",
        "color": "#00bfff",
        "statut": "Préoccupation mineure",
        "statut_color": "#22cc66",
        "taille": "2.5 — 2.8 m",
        "desc": (
            "Le dauphin à flancs blancs de l'Atlantique est une espèce grégaire et très active. Ils "
            "produisent une grande variété de clics d'écholocation rapides et de sifflements "
            "aigus pour coordonner leurs techniques de chasse en groupe."
        ),
        "audio_note": "Rafales de clics rapides et sifflements très modulés",
    },
]

def _img_to_base64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _render_custom_player(audio_path: str, unique_id: str):
    if not os.path.exists(audio_path):
        return
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_type = "audio/wav"

    player_html = f"""
    <style>
    body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Inter', sans-serif; }}
    .player-bar {{
        background: rgba(5, 25, 55, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 150, 255, 0.15);
        border-radius: 16px;
        padding: 12px 18px;
        display: flex; align-items: center; gap: 14px;
        box-shadow: 0 4px 20px rgba(0, 50, 120, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }}
    .play-button {{
        background: linear-gradient(135deg, #0055cc, #0088ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        min-width: 44px !important;
        height: 38px !important;
        cursor: pointer !important;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 15px rgba(0, 100, 255, 0.3) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        padding: 0 !important;
    }}
    .play-button:hover {{ box-shadow: 0 4px 15px rgba(0, 100, 255, 0.3) !important; }}
    .play-button svg {{ transition: transform 0.2s ease; }}
    .play-button:hover svg {{ transform: scale(1.15); }}
    
    .time-label {{ color: #a0e4ff; font-family: 'Space Grotesk', monospace; font-size: 13px; min-width: 40px; font-weight: 600; text-align: center; }}
    
    .prog-wrap {{
        position: relative; flex-grow: 1; height: 16px;
        display: flex; align-items: center; cursor: pointer;
    }}
    .prog-track {{ width: 100%; height: 5px; background: rgba(0, 50, 100, 0.4); border-radius: 99px; overflow: hidden; position: relative; }}
    .prog-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #0066ff, #00ccff); pointer-events: none; }}
    .prog-handle {{
        position: absolute; width: 14px; height: 14px; background: #fff;
        border: 2px solid #0088ff; border-radius: 50%;
        top: 50%; transform: translate(-50%, -50%); left: 0%;
        box-shadow: 0 0 10px rgba(0, 136, 255, 0.6);
        pointer-events: none;
    }}
    .speed-opt {{
        appearance: none; -webkit-appearance: none; -moz-appearance: none;
        background: rgba(0, 30, 70, 0.6) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="%237ec8f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>') no-repeat right 8px center;
        background-size: 12px 12px;
        color: #e0f4ff; border: 1px solid rgba(0, 150, 255, 0.3); border-radius: 10px; 
        padding: 6px 24px 6px 10px; font-size: 0.75rem; cursor: pointer; outline: none; font-weight: 600;
        transition: all 0.2s ease; box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05); font-family: inherit;
    }}
    .speed-opt:hover {{ background-color: rgba(0, 80, 180, 0.4); border-color: #4dc8ff; }}
    .speed-opt option {{ background-color: #031527; color: #e0f4ff; font-weight: 500; }}
    </style>

    <div class="player-bar">
        <button class="play-button" id="p_trigger_{unique_id}" onclick="handleP_{unique_id}()">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M7 6.75C7 5.79708 8.03092 5.19896 8.85857 5.66118L18.2251 10.9126C19.0657 11.3833 19.0657 12.6167 18.2251 13.0874L8.85857 18.3388C8.03092 18.801 7 18.2029 7 17.25V6.75Z"/></svg>
        </button>
        <div class="time-label" id="t_c_{unique_id}">0.0s</div>
        <div class="prog-wrap" id="s_z_{unique_id}" onmousedown="handleS_{unique_id}(event)">
            <div class="prog-track"><div class="prog-fill" id="p_f_{unique_id}"></div></div>
            <div class="prog-handle" id="p_h_{unique_id}"></div>
        </div>
        <div class="time-label" id="t_d_{unique_id}">0.0s</div>
        <select class="speed-opt" id="v_s_{unique_id}" onchange="handleSpeed_{unique_id}(this.value)">
            <option value="0.5">x0.5</option>
            <option value="1.0" selected>x1.0</option>
            <option value="1.5">x1.5</option>
        </select>
    </div>
    <audio id="core_a_{unique_id}" src="data:{audio_type};base64,{audio_b64}"></audio>

    <script>
    const a_{unique_id} = document.getElementById('core_a_{unique_id}');
    const b_{unique_id} = document.getElementById('p_trigger_{unique_id}');
    const h_{unique_id} = document.getElementById('p_h_{unique_id}');
    const f_{unique_id} = document.getElementById('p_f_{unique_id}');
    const tc_{unique_id} = document.getElementById('t_c_{unique_id}');
    const td_{unique_id} = document.getElementById('t_d_{unique_id}');
    
    let syncInterval_{unique_id} = null;
    let dur_max_{unique_id} = 0;

    a_{unique_id}.onloadedmetadata = () => {{
        dur_max_{unique_id} = a_{unique_id}.duration;
        td_{unique_id}.innerHTML = dur_max_{unique_id}.toFixed(1) + "s";
    }};

    function handleP_{unique_id}() {{
        if (a_{unique_id}.paused) {{
            if (a_{unique_id}.currentTime >= dur_max_{unique_id} - 0.05) {{ a_{unique_id}.currentTime = 0; }}
            a_{unique_id}.play();
        }} else {{
            a_{unique_id}.pause();
        }}
    }}

    function handleSpeed_{unique_id}(v) {{ a_{unique_id}.playbackRate = parseFloat(v); }}

    function handleS_{unique_id}(e) {{
        const doMove = (me) => {{
            const rect = document.getElementById('s_z_{unique_id}').getBoundingClientRect();
            let p = (me.clientX - rect.left) / rect.width;
            p = Math.max(0, Math.min(1, p));
            a_{unique_id}.currentTime = p * a_{unique_id}.duration;
        }};
        const stopMove = () => {{
            window.removeEventListener('mousemove', doMove);
            window.removeEventListener('mouseup', stopMove);
            updateUI_{unique_id}();
        }};
        window.addEventListener('mousemove', doMove);
        window.addEventListener('mouseup', stopMove);
        doMove(e);
    }}

    function updateUI_{unique_id}() {{
        if (!dur_max_{unique_id}) return;
        const p_val = (a_{unique_id}.currentTime / dur_max_{unique_id}) * 100;
        h_{unique_id}.style.left = p_val + "%";
        f_{unique_id}.style.width = p_val + "%";
        tc_{unique_id}.innerHTML = a_{unique_id}.currentTime.toFixed(1) + "s";
    }}

    const playIcon = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M7 6.75C7 5.79708 8.03092 5.19896 8.85857 5.66118L18.2251 10.9126C19.0657 11.3833 19.0657 12.6167 18.2251 13.0874L8.85857 18.3388C8.03092 18.801 7 18.2029 7 17.25V6.75Z"/></svg>';
    const pauseIcon = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1.5"/><rect x="14" y="5" width="4" height="14" rx="1.5"/></svg>';

    a_{unique_id}.onplay = () => {{
        b_{unique_id}.innerHTML = pauseIcon;
        if (syncInterval_{unique_id}) clearInterval(syncInterval_{unique_id});
        syncInterval_{unique_id} = setInterval(updateUI_{unique_id}, 50);
    }};

    a_{unique_id}.onpause = () => {{
        b_{unique_id}.innerHTML = playIcon;
        clearInterval(syncInterval_{unique_id});
        updateUI_{unique_id}();
    }};

    a_{unique_id}.onended = () => {{
        b_{unique_id}.innerHTML = playIcon;
        clearInterval(syncInterval_{unique_id});
        a_{unique_id}.currentTime = 0;
        updateUI_{unique_id}();
    }};

    a_{unique_id}.onseeked = () => {{ updateUI_{unique_id}(); }};

    // Inject CSS into the Streamlit container to pull this visually into the species card
    setTimeout(() => {{
        const myIframe = window.frameElement;
        if (myIframe) {{
            const stContainer = myIframe.closest('.element-container');
            if (stContainer) {{
                stContainer.style.marginTop = "-125px";
                stContainer.style.position = "relative";
                stContainer.style.zIndex = "10";
                stContainer.style.padding = "0 20px 10px 20px";
            }}
        }}
    }}, 100);
    </script>
    """
    st.components.v1.html(player_html, height=85)


def render():
    st.markdown(
        '''<div class="page-header" style="margin-bottom: 40px;">
  <h1 class="main-title">Nos espèces</h1>
  <div class="subtitle">Découvrez les mammifères marins qui fréquentent le Saint-Laurent.</div>
</div>''',
        unsafe_allow_html=True,
    )

    cols_a = st.columns(2, gap="large")
    for idx, sp in enumerate(SPECIES):
        col = cols_a[idx % 2]
        img_b64 = _img_to_base64(sp["img"])
        img_tag = f'<img src="data:image/png;base64,{img_b64}" style="width:100%;height:220px;object-fit:cover;filter:brightness(.85) saturate(1.2);"/>' if img_b64 else f'<div style="width:100%;height:220px;background:linear-gradient(135deg,{sp["color"]}44,{sp["color"]}22);display:flex;align-items:center;justify-content:center;font-size:4rem;color:#ffffff;">{sp["name"][0]}</div>'

        # Even more generous spacing between cards
        card_html = f'''<div class="species-card" style="margin-bottom: 45px;">
{img_tag}
<div class="card-body" style="padding-bottom: 95px;">
<div class="card-name">{sp["name"]}</div>
<div class="card-latin">{sp["latin"]}</div>
<hr style="border-color: rgba(255,255,255,0.05); margin: 12px 0;"/>
<div style="font-size:0.85rem; color:#8ab8d8; margin-bottom:12px;">{sp["desc"]}</div>
<div style="background:rgba(0,100,255,0.05); border:1px solid rgba(0,150,255,0.1); border-radius:12px; padding:15px; margin-top:10px;">
<div style="display:flex; justify-content:space-between; margin-bottom:8px;">
<div style="font-size:0.75rem; color:#5588aa; text-transform:uppercase;">Taille</div>
<div style="font-size:0.85rem; color:#aaddff; font-weight:700;">{sp["taille"]}</div>
</div>
<div style="display:flex; justify-content:space-between; margin-bottom:8px;">
<div style="font-size:0.75rem; color:#5588aa; text-transform:uppercase;">Fréquences</div>
<div style="font-size:0.85rem; color:#00ccff; font-weight:700;">{sp["freq"]}</div>
</div>
<div style="border-top:1px solid rgba(0,150,255,0.1); margin-top:8px; padding-top:8px;">
<div style="font-size:0.7rem; color:#4477aa; text-transform:uppercase; margin-bottom:4px;">Signature Acoustique</div>
<div style="font-size:0.82rem; color:#7ec8f5; font-style:italic;">{sp["audio_note"]}</div>
</div>
</div>
</div>
</div>'''
        with col:
            st.markdown(card_html, unsafe_allow_html=True)
            audio_path = f"assets/audio/{sp['id']}.wav"
            if os.path.exists(audio_path):
                _render_custom_player(audio_path, sp['id'])
            else:
                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
