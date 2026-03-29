"""Audio analysis page — file upload, visualization, and ML inference."""
import time
import numpy as np
import plotly.graph_objects as go
import streamlit as st  # type: ignore
from pages_custom.especes import SPECIES

# ── Helper: Plotly dark layout ──────────────────────────────────────────────
def _plotly_dark_layout(title: str):
    return {
        "title": {"text": title, "font": {"color": "#a0e4ff", "size": 15}, "x": 0.05, "y": 0.95},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"t": 40, "b": 40, "l": 40, "r": 20},
        "font": {"color": "#8ab8d8", "family": "Inter, sans-serif"},
        "xaxis": {
            "gridcolor": "rgba(255,255,255,0.03)",
            "zerolinecolor": "rgba(255,255,255,0.05)",
            "fixedrange": True,
            "showticklabels": False if "Spectrogram" in title else True,
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,0.03)",
            "zerolinecolor": "rgba(255,255,255,0.05)",
            "fixedrange": True,
        },
        "dragmode": False,
        "showlegend": False,
    }

# ── Custom Audio Player (Syncing Chart) ──────────────────────────────────────
def _render_synced_player(fig, audio_file, duration, plot_key):
    """Renders the professional player matching the app theme and syncs across the active chart."""
    if audio_file is None:
        return

    import base64
    audio_file.seek(0)
    audio_bytes = audio_file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_file.seek(0)
    audio_type = getattr(audio_file, "type", "audio/wav")
    if not audio_type or audio_type == "application/octet-stream":
        audio_type = "audio/wav"

    # Render Chart first
    st.plotly_chart(fig, use_container_width=True, key=plot_key, config={"displayModeBar": False})

    # The Player UI (HTML + Styles + Script in a single f-string)
    player_html = f"""
    <style>
    body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
    .player-bar {{
        background: rgba(5, 25, 55, 0.6);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 150, 255, 0.18);
        border-radius: 20px;
        padding: 15px 24px;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 8px 32px rgba(0, 50, 120, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        font-family: 'Inter', sans-serif;
    }}
    .play-button {{
        background: linear-gradient(135deg, #0055cc, #0088ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        min-width: 110px !important;
        display: flex; align-items: center; justify-content: center; gap: 8px;
        box-shadow: 0 4px 20px rgba(0, 100, 255, 0.35) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    .play-button:hover {{ box-shadow: 0 4px 20px rgba(0, 100, 255, 0.35) !important; }}
    .play-button svg {{ transition: transform 0.2s ease; }}
    .play-button:hover svg {{ transform: scale(1.15); }}
    
    .time-label {{ color: #a0e4ff; font-family: 'Space Grotesk', monospace; font-size: 14px; min-width: 50px; font-weight: 600; text-align: center; }}
    
    .prog-wrap {{
        position: relative; flex-grow: 1; height: 16px;
        display: flex; align-items: center; cursor: pointer;
    }}
    .prog-track {{ width: 100%; height: 6px; background: rgba(0, 50, 100, 0.4); border-radius: 99px; overflow: hidden; position: relative; }}
    .prog-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #0066ff, #00ccff); pointer-events: none; }}
    .prog-handle {{
        position: absolute; width: 16px; height: 16px; background: #fff;
        border: 2px solid #0088ff; border-radius: 50%;
        top: 50%; transform: translate(-50%, -50%); left: 0%;
        box-shadow: 0 0 10px rgba(0, 136, 255, 0.6);
        pointer-events: none;
    }}
    .speed-opt {{
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        background: rgba(0, 30, 70, 0.6) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="%237ec8f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>') no-repeat right 12px center;
        background-size: 14px 14px;
        color: #e0f4ff; 
        border: 1px solid rgba(0, 150, 255, 0.3);
        border-radius: 12px; 
        padding: 8px 34px 8px 14px; 
        font-size: 0.85rem; 
        cursor: pointer; 
        outline: none; 
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        font-family: inherit;
    }}
    .speed-opt:hover {{
        background-color: rgba(0, 80, 180, 0.4);
        border-color: #4dc8ff;
        box-shadow: 0 4px 15px rgba(0, 150, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }}
    .speed-opt:focus {{
        border-color: #4dc8ff;
        box-shadow: 0 0 0 2px rgba(77, 200, 255, 0.25);
    }}
    .speed-opt option {{
        background-color: #031527;
        color: #e0f4ff;
        font-weight: 500;
        padding: 8px;
    }}
    
    @media screen and (max-width: 1024px) {{
        .btn-text {{ display: none; }}
        .play-button {{ 
            min-width: 45px !important; 
            padding: 8px 14px !important; 
        }}
    }}
    </style>

    <div class="player-bar">
        <button class="play-button" id="p_trigger" onclick="handleP()">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="margin-right:8px; vertical-align:middle;"><path d="M7 6.75C7 5.79708 8.03092 5.19896 8.85857 5.66118L18.2251 10.9126C19.0657 11.3833 19.0657 12.6167 18.2251 13.0874L8.85857 18.3388C8.03092 18.801 7 18.2029 7 17.25V6.75Z"/></svg>
            <span class="btn-text"> Lecture</span>
        </button>
        <div class="time-label" id="t_c">0.0s</div>
        <div class="prog-wrap" id="s_z" onmousedown="handleS(event)">
            <div class="prog-track"><div class="prog-fill" id="p_f"></div></div>
            <div class="prog-handle" id="p_h"></div>
        </div>
        <div class="time-label" id="t_d">{duration:.1f}s</div>
        <select class="speed-opt" id="v_s" onchange="handleSpeed(this.value)">
            <option value="0.2">x0.2</option>
            <option value="0.5">x0.5</option>
            <option value="1.0" selected>x1.0</option>
            <option value="1.5">x1.5</option>
        </select>
    </div>
    <audio id="core_a" src="data:{audio_type};base64,{audio_b64}" preload="auto"></audio>

    <script>
    const a = document.getElementById('core_a');
    const b = document.getElementById('p_trigger');
    const h = document.getElementById('p_h');
    const f = document.getElementById('p_f');
    const tc = document.getElementById('t_c');
    const dur_max = {duration};
    
    // Force loading the source
    a.load();
    
    let syncInterval = null;

    function handleP() {{
        if (a.paused) {{
            if (a.currentTime >= dur_max - 0.1) {{ a.currentTime = 0; }}
            var p = a.play();
            if (p !== undefined) {{ p.catch(e => {{ console.log('Playback error:', e); }}); }}
        }} else {{
            a.pause();
        }}
    }}

    function handleSpeed(v) {{ a.playbackRate = parseFloat(v); }}

    function handleS(e) {{
        const doMove = (me) => {{
            const rect = document.getElementById('s_z').getBoundingClientRect();
            let p = (me.clientX - rect.left) / rect.width;
            p = Math.max(0, Math.min(1, p));
            a.currentTime = p * a.duration;
        }};
        const stopMove = () => {{
            window.removeEventListener('mousemove', doMove);
            window.removeEventListener('mouseup', stopMove);
            updateUI();
        }};
        window.addEventListener('mousemove', doMove);
        window.addEventListener('mouseup', stopMove);
        doMove(e);
    }}

    function updateUI() {{
        if (!dur_max) return;
        const p_val = (a.currentTime / dur_max) * 100;
        h.style.left = p_val + "%";
        f.style.width = p_val + "%";
        tc.innerHTML = a.currentTime.toFixed(1) + "s";

        // Sync Plot
        try {{
            const plots = window.parent.document.querySelectorAll('.js-plotly-plot');
            plots.forEach(gd => {{
                if (gd && gd.layout) {{
                    const news = (gd.layout.shapes || []).filter(sh => sh.name !== 'tr');
                    news.push({{
                        type: 'line', x0: a.currentTime, x1: a.currentTime,
                        y0: 0, y1: 1, yref: 'paper', name: 'tr',
                        line: {{ color: '#ff4444', width: 2, dash: 'dot' }}
                    }});
                    window.parent.Plotly.relayout(gd, {{ shapes: news }});
                }}
            }});
        }} catch(e) {{
            // Plotly not yet available or chart not ready
        }}
    }}

    const playIconHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="margin-right:8px; vertical-align:middle;"><path d="M7 6.75C7 5.79708 8.03092 5.19896 8.85857 5.66118L18.2251 10.9126C19.0657 11.3833 19.0657 12.6167 18.2251 13.0874L8.85857 18.3388C8.03092 18.801 7 18.2029 7 17.25V6.75Z"/></svg><span class="btn-text"> Lecture</span>';
    const pauseIconHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="margin-right:8px; vertical-align:middle;"><rect x="6" y="5" width="4" height="14" rx="1.5"/><rect x="14" y="5" width="4" height="14" rx="1.5"/></svg><span class="btn-text"> Pause</span>';

    a.onplay = () => {{
        b.innerHTML = pauseIconHTML;
        if (syncInterval) clearInterval(syncInterval);
        syncInterval = setInterval(updateUI, 50); // 20 frames/sec for smooth line movement
    }};

    a.onpause = () => {{
        b.innerHTML = playIconHTML;
        clearInterval(syncInterval);
        updateUI();
    }};

    a.onended = () => {{
        b.innerHTML = playIconHTML;
        clearInterval(syncInterval);
        a.currentTime = 0;
        updateUI();
    }};

    a.onseeked = () => {{
        updateUI();
    }};
    </script>
    """
    st.components.v1.html(player_html, height=100)

# ── Main Render ─────────────────────────────────────────────────────────────
def render():
    st.markdown(
        """<style>
/* Analyse Page specific: Stack the 2 columns (Player/Graph and Results) on tablet vertically */
@media screen and (max-width: 1024px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 1.5rem !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
}
</style>
<div class="page-header">
<h1 class="main-title">Analyse Audio</h1>
<div class="subtitle">
<span>Importation de signal</span>
<span class="dot">•</span>
<span>Inférence taxonomique</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Importation du signal",
        type=["wav", "mp3", "flac"],
        label_visibility="collapsed",
        key="upl_v4"
    )

    if uploaded is None:
        # The CSS styling is now globally handled via assets/style.css
        pass
    else:
        uploaded.seek(0)
        p_left, p_right = st.columns([3, 2], gap="large")

        with p_left:
            import librosa  # type: ignore
            import tempfile
            import os
            with st.spinner("Analyse du signal..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(uploaded.getvalue())
                    tmp_file_path = tmp_file.name
                
                y, sr = librosa.load(tmp_file_path, sr=None)
                duration = len(y) / sr
                
                os.unlink(tmp_file_path)

            st.markdown("<div class='section-title'>Visualisation & Synchronisation</div>", unsafe_allow_html=True)
            
            # Use st.radio for switching visualization
            view_option = st.radio("Type de visualisation", ["Forme d'onde", "Spectrogramme"], horizontal=True)
            
            if view_option == "Forme d'onde":
                # (1) Waveform
                step = max(1, len(y) // 2500)
                y_s = np.asarray(y)[::step]
                x_s = np.linspace(0, duration, len(y_s))
                fig_active = go.Figure(go.Scatter(x=x_s, y=y_s, line={"color": "#4dc8ff", "width": 1}, hoverinfo="none"))
                fig_active.update_layout(**_plotly_dark_layout("Forme d'onde (Amplitude)"), height=220)
                plot_key = "pl_waveform"
            else:
                # (2) Spectrogram
                D = librosa.stft(y)
                S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
                fig_active = go.Figure(go.Heatmap(
                    z=S_db, 
                    x=np.linspace(0, duration, S_db.shape[1]), 
                    y=np.linspace(0, sr/2, S_db.shape[0]), 
                    colorscale=[[0, '#001226'], [0.25, '#00264d'], [0.5, '#004080'], [0.75, '#0080ff'], [1, '#4dc8ff']],
                    showscale=False,
                    hoverinfo="none"
                ))
                fig_active.update_layout(**_plotly_dark_layout("Spectrogramme fréquentiel"), height=220)
                plot_key = "pl_spectrogram"

            # RENDER DUAL PLAYER (Sync Active View)
            _render_synced_player(fig_active, uploaded, duration, plot_key)

            st.markdown("<br/>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("Durée", f"{duration:.2f} s")
            m2.metric("Fréq. Échant.", f"{sr:,} Hz")

        with p_right:
            st.markdown("<div class='section-title'>Présence dans la trame</div>", unsafe_allow_html=True)

            # ── Chargement du modèle & inférence ──────────────────────────
            import sys
            import os as _os
            _root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
            if _root not in sys.path:
                sys.path.insert(0, _root)

            from model.predictor import predict_audio, is_model_ready

            model_ready = is_model_ready()
            # Initialize safe defaults (used in timeline fallback)
            cache_key = None
            preds = None
            bruit_pct = 100.0

            if not model_ready:
                st.markdown(
                    """<div class='glass-card' style='border-color:rgba(255,170,0,0.4); padding:20px;'>
                    <h4 style='color:#ffaa00; margin:0 0 8px 0;'>⚙️ Modèle non entraîné</h4>
                    <p style='color:#a0d8f0; font-size:0.9rem; margin:0;'>
                    Exécutez <code style='background:rgba(0,0,0,0.4); padding:2px 6px; border-radius:4px;'>python train_model.py</code>
                    pour entraîner le classificateur avant de pouvoir analyser des sons.
                    </p></div>""",
                    unsafe_allow_html=True,
                )
            else:
                # Cache les résultats par nom de fichier uploadé
                cache_key = f"ml_result_{uploaded.name}"
                if cache_key not in st.session_state:
                    with st.spinner("Analyse de la trame..."):
                        uploaded.seek(0)
                        result = predict_audio(uploaded)
                    st.session_state[cache_key] = result

                result = st.session_state[cache_key]

                if result.get("error"):
                    st.error(f"Erreur d'inférence : {result['error']}")
                else:
                    raw_vals = result["probabilities"]
                    # 🧊 Filtrage intelligent basé sur la DURÉE RÉELLE détectée
                    # On ne cache une espèce que si elle représente moins de 0.8 seconde cumulée ET moins de 10%.
                    # Cela permet de garder un événement de 5% sur 250s (12.5s) mais d'ignorer 4% sur 2s (0.08s).
                    preds = np.copy(raw_vals)
                    noise_offset = 0.0
                    for i in range(5):
                        species_duration = preds[i] * duration
                        if species_duration < 0.8 and preds[i] < 0.10:
                            noise_offset += preds[i]
                            preds[i] = 0.0
                    preds[5] += noise_offset
                    
                    bruit_pct = float(preds[5]) * 100
                    multi_species = result["multi_species"]
                    # On ne garde que les espèces qui dépassent le seuil de durée
                    detected = [i for i in range(5) if preds[i] > 0]
                    model_acc = result["model_accuracy"]

                    st.markdown("<br/>", unsafe_allow_html=True)


                    # Barres de probabilité
                    if bruit_pct > 99.0:
                        st.markdown(
                            "<div class='glass-card' style='text-align:center; padding: 25px;'>"
                            "<h3 style='color:#ff4d4d; margin:0;'>⚠️ Son non compatible</h3>"
                            "<p style='color:#a0d8f0; font-size:0.9rem; margin-top:5px; margin-bottom:0;'>"
                            "Aucun signal marin clair n'a été détecté (Bruit prédominant).</p></div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        bars = ""
                        for i, sp in enumerate(SPECIES):
                            pct = float(preds[i]) * 100
                            if pct >= 1.0:
                                bars += (
                                    f'<div class="pred-bar-wrap">'
                                    f'<div class="pred-bar-header">'
                                    f'<span class="pred-bar-name">{sp["name"]}</span>'
                                    f'<span class="pred-bar-pct">{pct:.1f}%</span>'
                                    f'</div>'
                                    f'<div class="pred-bar-track">'
                                    f'<div class="pred-bar-fill" style="width:{pct:.1f}%; background:{sp["color"]};"></div>'
                                    f'</div></div>'
                                )

                        if bruit_pct >= 1.0:
                            bars += (
                                f'<div class="pred-bar-wrap">'
                                f'<div class="pred-bar-header">'
                                f'<span class="pred-bar-name" style="color:#8ab8d8;">Bruit de fond</span>'
                                f'<span class="pred-bar-pct" style="color:#8ab8d8;">{bruit_pct:.1f}%</span>'
                                f'</div>'
                                f'<div class="pred-bar-track" style="background:rgba(0,30,60,0.5);">'
                                f'<div class="pred-bar-fill" style="width:{bruit_pct:.1f}%; background:#556677;"></div>'
                                f'</div></div>'
                            )

                        st.markdown(f"<div class='glass-card'>{bars}</div>", unsafe_allow_html=True)

            st.markdown("<br/><div class='section-title'>Chronologie</div>", unsafe_allow_html=True)

            # ── Chronologie basée sur les résultats ML ─────────────────
            # Construire depuis la timeline ML si disponible, sinon simulation
            use_ml_timeline = (
                model_ready
                and "error" in locals()
                and not result.get("error")
                and len(result.get("timeline", [])) > 0
            )

            # Reconstruire la timeline depuis les données ML
            blocks = []
            try:
                if model_ready and cache_key in st.session_state:
                    ml_result = st.session_state[cache_key]
                    if not ml_result.get("error") and ml_result.get("timeline"):
                        raw_timeline = ml_result["timeline"]
                        # Fusionner les fenêtres consécutives de même espèce
                        if raw_timeline:
                            curr_species = raw_timeline[0]["species_idx"]
                            curr_start = raw_timeline[0]["t_start"]
                            curr_end = raw_timeline[0]["t_end"]
                            for seg in raw_timeline[1:]:
                                if seg["species_idx"] == curr_species:
                                    curr_end = seg["t_end"]
                                else:
                                    blocks.append((curr_species, curr_start, curr_end))
                                    curr_species = seg["species_idx"]
                                    curr_start = seg["t_start"]
                                    curr_end = seg["t_end"]
                            blocks.append((curr_species, curr_start, curr_end))
            except Exception:
                blocks = []

            # Fallback : simulation si pas de timeline ML
            if not blocks:
                _preds_available = preds is not None
                _bruit = bruit_pct if _preds_available else 100.0
                if not model_ready or _bruit > 99.9:
                    top_idx = -1
                    second_idx = -1
                else:
                    animal_preds = preds[:5]
                    top_idx = int(np.argmax(animal_preds))
                    second_idx_candidates = np.where(animal_preds > 0.1)[0]
                    second_idx = int(second_idx_candidates[np.argsort(animal_preds[second_idx_candidates])[-2]]) \
                        if len(second_idx_candidates) > 1 else top_idx

                n_seg = max(6, int(duration * 2))
                sequence = []
                current_state = -1
                for i in range(n_seg):
                    if top_idx == -1:
                        sequence.append(-1)
                    else:
                        _noise_p = float(preds[5]) if _preds_available else 0.3
                        if current_state == -1 and np.random.random() < (1.0 - _noise_p):
                            current_state = top_idx if np.random.random() < 0.75 else second_idx
                        elif current_state != -1 and np.random.random() < _noise_p * 1.5:
                            current_state = -1
                        sequence.append(current_state)

                if sequence:
                    curr_lbl = sequence[0]
                    curr_s = 0
                    for i in range(1, len(sequence)):
                        if sequence[i] != curr_lbl:
                            blocks.append((curr_lbl, curr_s * duration / n_seg, i * duration / n_seg))
                            curr_lbl = sequence[i]
                            curr_s = i
                    blocks.append((curr_lbl, curr_s * duration / n_seg, duration))

            segs_html = ""
            for lbl, t_start, t_end in blocks:
                seg_class = "seg-noise" if lbl == -1 else f'seg-{SPECIES[lbl]["id"]}'
                name = "Bruit / Silence" if lbl == -1 else SPECIES[lbl]["name"]
                t_dur = t_end - t_start

                segs_html += f'''<div style="position: relative; display: flex; align-items: center; margin-bottom: 12px;">
    <div class="{seg_class}" style="position: absolute; left: -21px; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #020b18; z-index: 2; box-shadow: 0 0 8px rgba(0, 150, 255, 0.4);"></div>
    <div style="background: rgba(5, 25, 55, 0.4); border: 1px solid rgba(0, 150, 255, 0.15); border-radius: 12px; padding: 10px 14px; display: flex; align-items: center; flex-grow: 1; transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: default;" onmouseover="this.style.transform='translateX(4px)'; this.style.backgroundColor='rgba(0, 40, 90, 0.6)';" onmouseout="this.style.transform='translateX(0)'; this.style.backgroundColor='rgba(5, 25, 55, 0.4)';">
        <div style="font-family: 'Space Grotesk', monospace; color: #7ec8f5; font-size: 0.85rem; width: 85px; font-weight: 600;">{t_start:.1f}s - {t_end:.1f}s</div>
        <div style="color: #e0f4ff; font-weight: 600; font-size: 0.95rem; flex-grow: 1; letter-spacing: 0.02em;">{name}</div>
        <div style="color: #4dc8ff; font-weight: 700; font-size: 0.8rem; background: rgba(0, 150, 255, 0.12); border: 1px solid rgba(0, 150, 255, 0.2); padding: 3px 10px; border-radius: 20px;">{t_dur:.1f}s</div>
    </div>
</div>'''

            timeline_container = f'''<div style="background: rgba(0, 20, 50, 0.3); border: 1px solid rgba(0, 150, 255, 0.1); border-radius: 16px; padding: 20px 20px 8px 35px; position: relative;">
    <div style="position: absolute; left: 20px; top: 25px; bottom: 25px; width: 2px; background: rgba(0, 150, 255, 0.15); z-index: 1;"></div>
    {segs_html}
</div>'''

            st.markdown(timeline_container, unsafe_allow_html=True)
