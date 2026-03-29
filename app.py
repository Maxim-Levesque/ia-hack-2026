import base64
import os
import time
import streamlit as st  # type: ignore

def _img_to_base64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="IA Hack 2026 - Équipe E",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Inject global CSS ──────────────────────────────────────────────────────────
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join("assets", "images", "Logo_IA'HACK.png")
    logo_b64 = _img_to_base64(logo_path)
    if logo_b64:
        st.markdown(
            f'<div class="sidebar-brand-container">'
            f'<img src="data:image/png;base64,{logo_b64}" style="width:100px;"/>'
            f'<div class="brand-sub">Équipe E</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if "_nav" not in st.session_state:
        st.session_state["_nav"] = "Accueil"

    def navigate_to(p):
        st.session_state["_nav"] = p
        st.rerun()

    # Navigation section
    if st.button("Accueil", use_container_width=True, type="primary" if st.session_state["_nav"] == "Accueil" else "secondary"):
        navigate_to("Accueil")
    if st.button("Espèces", use_container_width=True, type="primary" if st.session_state["_nav"] == "Espèces" else "secondary"):
        navigate_to("Espèces")
    if st.button("Analyse Audio", use_container_width=True, type="primary" if st.session_state["_nav"] == "Analyse" else "secondary"):
        navigate_to("Analyse")
    if st.button("Informations", use_container_width=True, type="primary" if st.session_state["_nav"] == "Infos" else "secondary"):
        navigate_to("Infos")

    page = st.session_state["_nav"]

    # Footer section stays at the bottom
    st.markdown("<div style='flex-grow:1'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border-top: 1px solid rgba(0, 150, 255, 0.08); padding-top: 20px;'>"
        "<div class='sidebar-footer-title'>IA Hack 2026</div>"
        "<div class='sidebar-footer-discreet'>Cégep de Rivière-du-Loup</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Route pages ───────────────────────────────────────────────────────────────
if page == "Accueil":
    from pages_custom import home  # type: ignore
    home.render()
elif page == "Analyse":
    from pages_custom import analyse  # type: ignore
    analyse.render()
elif page == "Espèces":
    from pages_custom import especes  # type: ignore
    especes.render()
elif page == "Infos":
    from pages_custom import infos  # type: ignore
    infos.render()

# ── Footer global ─────────────────────────────────────────────────────────────
if logo_b64:
    st.markdown(
        f"""
        <div style='margin-top: 60px; padding-top: 25px; border-top: 1px solid rgba(0, 150, 255, 0.1); text-align: center; opacity: 0.5; transition: opacity 0.3s ease;' onmouseover="this.style.opacity='0.9'" onmouseout="this.style.opacity='0.5'">
            <img src="data:image/png;base64,{logo_b64}" style="height: 50px; margin-bottom: 10px; filter: grayscale(100%) brightness(1.5); transition: filter 0.3s ease;" onmouseover="this.style.filter='grayscale(0%) brightness(1)'" onmouseout="this.style.filter='grayscale(100%) brightness(1.5)'"/>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.75rem; color: #a0cce0; letter-spacing: 0.08em; text-transform: uppercase;">
                Projet réalisé pour l'IA Hack 2026
            </div>
            <div style="font-size: 0.65rem; color: #5599cc; margin-top: 4px;">
                Équipe E • Cégep de Rivière-du-Loup
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


