"""Home page — Marine Sound AI."""
import base64
import os
import streamlit as st  # type: ignore

def _img_to_base64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render():
    logo_path = os.path.join("assets", "images", "Logo_IA'HACK.png")
    logo_b64 = _img_to_base64(logo_path)
    
    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        f"""<div class="page-header" style="text-align: center; padding-bottom: 2rem;">
            <h1 class="main-title">IA Hack 2026</h1>
            <div class="subtitle" style="margin-bottom: 25px;">Défis #1 - Détection des sons des mammifères marins</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Top Navigation Buttons ─────────────────────────────────────────────
    col_btn_l, col_btn_r = st.columns(2)
    with col_btn_l:
        if st.button("Voir les espèces", use_container_width=True, key="top_especes_btn"):
            st.session_state["_nav"] = "Espèces"
            st.rerun()
    with col_btn_r:
        if st.button("Analyser un audio", use_container_width=True, key="top_analyse_btn"):
            st.session_state["_nav"] = "Analyse"
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Team members ───────────────────────────────────────────────────────
    st.markdown(
        """<div style="text-align:center; padding:30px 0; margin: 0 auto; max-width:1000px; border-top: 1px solid rgba(0, 150, 255, 0.1); border-bottom: 1px solid rgba(0, 150, 255, 0.1);">
            <div style="font-size:0.8rem; color:#a0cce0; font-weight:400; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 25px; opacity: 0.7;">Équipe de développement</div>
            <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; padding: 0 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 1rem; color: #fff; font-weight: 700;">Justin Chamberland</div>
                    <div style="font-size: 0.75rem; color: #4dc8ff; font-weight: 500; margin-top: 4px; opacity: 0.8;">ML & Data</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1rem; color: #fff; font-weight: 700;">Mathis Dubé-Tremblay</div>
                    <div style="font-size: 0.75rem; color: #4dc8ff; font-weight: 500; margin-top: 4px; opacity: 0.8;">ML & Data</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1rem; color: #fff; font-weight: 700;">Ridwane Berfroi</div>
                    <div style="font-size: 0.75rem; color: #4dc8ff; font-weight: 500; margin-top: 4px; opacity: 0.8;">ML & Tests</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1rem; color: #fff; font-weight: 700;">Maxim Lévesque</div>
                    <div style="font-size: 0.75rem; color: #4dc8ff; font-weight: 500; margin-top: 4px; opacity: 0.8;">Interface Web</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br/><br/>", unsafe_allow_html=True)

    # ── Schema ML Section ──────────────────────────────────────────────────
    st.markdown(
        "<div class='section-title' style='text-align:center;'>Architecture du Système de Détection</div>",
        unsafe_allow_html=True,
    )

    schema_html = """
<style>
.schema-container { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 25px; flex-wrap: wrap; }
.schema-card { width: 180px; text-align: center; padding: 20px 15px; border-radius: 16px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); transition: transform 0.3s ease; }
.schema-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.05); }
.schema-arrow { color: #00d2ff; font-size: 1.2rem; opacity: 0.4; }
@media (max-width: 900px) { .schema-arrow { display: none; } .schema-card { width: calc(50% - 20px); min-width: 150px; } }
@media (max-width: 480px) { .schema-card { width: 100%; } }
</style>
<div class="schema-container">
    <div class="schema-card" style="border-bottom: 3px solid #00d2ff;">
        <div style="margin-bottom: 12px; color: #00d2ff;"><svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M11 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path></svg></div>
        <div style="font-weight: 600; color: #fff; font-size: 0.85rem;">Prétraitement</div>
        <div style="font-size: 0.7rem; color: #a0cce0; margin-top: 6px; line-height: 1.3;">Filtrage & Normalisation</div>
    </div>
    <div class="schema-arrow">➜</div>
    <div class="schema-card" style="border-bottom: 3px solid #3a7bd5;">
        <div style="margin-bottom: 12px; color: #3a7bd5;"><svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg></div>
        <div style="font-weight: 600; color: #fff; font-size: 0.85rem;">Features</div>
        <div style="font-size: 0.7rem; color: #a0cce0; margin-top: 6px; line-height: 1.3;">Extraction MFCC & Chroma</div>
    </div>
    <div class="schema-arrow">➜</div>
    <div class="schema-card" style="border-bottom: 3px solid #8e44ad;">
        <div style="margin-bottom: 12px; color: #8e44ad;"><svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg></div>
        <div style="font-weight: 600; color: #fff; font-size: 0.85rem;">Classification</div>
        <div style="font-size: 0.7rem; color: #a0cce0; margin-top: 6px; line-height: 1.3;">Random Forest 300</div>
    </div>
    <div class="schema-arrow">➜</div>
    <div class="schema-card" style="border-bottom: 3px solid #2ecc71;">
        <div style="margin-bottom: 12px; color: #2ecc71;"><svg viewBox="0 0 24 24" width="28" height="28" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg></div>
        <div style="font-weight: 600; color: #fff; font-size: 0.85rem;">Localisation</div>
        <div style="font-size: 0.7rem; color: #a0cce0; margin-top: 6px; line-height: 1.3;">Ligne du temps</div>
    </div>
</div>
"""
    st.markdown(schema_html, unsafe_allow_html=True)

    st.markdown("<br/><br/>", unsafe_allow_html=True)

    # ── Performance Metrics Section ────────────────────────────────────────
    st.markdown(
        "<div class='section-title' style='text-align:center;'>Efficacité du modèle par espèce</div>",
        unsafe_allow_html=True,
    )

    stats_html = """
<style>
.stats-container { display: flex; flex-direction: column; gap: 15px; margin-top: 25px; max-width: 800px; margin-left: auto; margin-right: auto; padding-bottom: 30px; }
.stat-row { display: flex; align-items: center; gap: 20px; }
.stat-name { width: 140px; font-size: 0.95rem; color: #e0f4ff; font-weight: 500; }
.stat-bar-bg { flex-grow: 1; height: 10px; background: rgba(0, 150, 255, 0.08); border-radius: 99px; overflow: hidden; position: relative; border: 1px solid rgba(0, 150, 255, 0.1); }
.stat-bar-fill { height: 100%; border-radius: 99px; transition: width 1s ease; }
.stat-val { width: 50px; font-family: 'Space Grotesk', monospace; font-size: 0.95rem; color: #baddff; font-weight: 600; text-align: right; }
@media (max-width: 600px) { .stat-name { width: 100px; font-size: 0.85rem; } }
</style>
<div class="stats-container">
    <div class="stat-row">
        <div class="stat-name">Béluga</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 94%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">94%</div>
    </div>
    <div class="stat-row">
        <div class="stat-name">Fin Whale</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 96%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">96%</div>
    </div>
    <div class="stat-row">
        <div class="stat-name">Baleine à bosse</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 98%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">98%</div>
    </div>
    <div class="stat-row">
        <div class="stat-name">Cachalot</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 99%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">99%</div>
    </div>
    <div class="stat-row">
        <div class="stat-name">Dauphin</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 97%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">97%</div>
    </div>
    <div class="stat-row" style="margin-top: 5px; opacity: 0.85;">
        <div class="stat-name">Bruit de fond</div>
        <div class="stat-bar-bg"><div class="stat-bar-fill" style="width: 99.5%; background: linear-gradient(90deg, #00d2ff, #3a7bd5);"></div></div>
        <div class="stat-val">99%</div>
    </div>
</div>
"""
    st.markdown(stats_html, unsafe_allow_html=True)
