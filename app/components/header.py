import base64
from pathlib import Path
from typing import Optional

import streamlit as st

from app.config import BTN_GAP, BTN_HEIGHT, TITULO_PRINCIPAL


def _img_b64(path: str) -> Optional[str]:
    p = Path(path)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")


def apply_app_css() -> None:
    """Injeta o CSS global da aplicação. Chamar uma vez em main.py."""
    st.markdown(
        f"""
<style>
  :root {{ --btn-height: {BTN_HEIGHT}; --btn-gap: {BTN_GAP}; --btn-font: 1.02em; }}

  div[data-testid="stAppViewBlockContainer"] {{
      opacity: 1 !important;
      transition: none !important;
  }}
  div[data-stale="true"],
  div[data-testid="stFormSubmitButton"] > button:active {{
      opacity: 1 !important;
      transition: none !important;
      filter: none !important;
  }}
  div[data-testid="stStatusWidget"] {{
      visibility: hidden;
  }}
  .stApp {{
      background-color: #F1F8E9;
  }}
  .stWidgetLabel, label, p, .stMarkdown {{
      color: #000000 !important;
  }}
  input, textarea, select, div[data-baseweb="select"] {{
      color: #000000 !important;
      background-color: #FFFFFF !important;
      -webkit-text-fill-color: #000000 !important;
  }}
  .stButton > button,
  .app-btn,
  div[data-testid="stLinkButton"] a,
  button[data-testid="stFormSubmitButton"] {{
      color: #FFFFFF !important;
      -webkit-text-fill-color: #FFFFFF !important;
  }}
  .block-container {{
      max-width: 760px;
      padding-top: 10px !important;
      padding-bottom: 1.9rem;
      margin: 0 auto;
  }}
  .header-grid {{
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      gap: 10px;
      width: 100%;
      margin-bottom: 0px;
  }}
  .stApp {{ background-color: #F1F8E9; }}
  #MainMenu, footer, header {{ visibility: hidden; }}
  div[data-testid="stWidgetLabel"] > label {{ color:#000 !important; }}
  hr {{ margin-top: 0 !important; margin-bottom: 0 !important; }}
  .hdr-img {{ height: 55px; object-fit: contain; }}
  .hdr-title {{
      margin: 0;
      color: #1A311F;
      font-weight: 800;
      font-size: 1.7rem;
      line-height: 1.1;
      text-shadow: 1px 1px 0 rgba(255,255,255,.35), 0 1px 2px rgba(0,0,0,.28);
      font-family: sans-serif;
      text-align: center;
      white-space: normal;
  }}
  @media (max-width: 480px) {{
      .hdr-img {{ height: 38px; }}
      .hdr-title {{ font-size: 1.3rem; }}
      .header-grid {{ gap: 5px; }}
  }}
  .stButton:not(.st-key-btn_trocar_evento_texto) > button, .app-btn, div[data-testid="stLinkButton"] a {{
    width: 100% !important;
    height: var(--btn-height); min-height: var(--btn-height);
    font-size: var(--btn-font) !important; font-weight: 600 !important;
    border-radius: 8px !important; border: 3.4px solid #54515c !important;
    color: white !important; background: linear-gradient(to bottom, #14337b, #4464A7) !important;
    box-shadow: 2px 2px 5px rgba(0,0,0,.3) !important;
    margin: 0 auto var(--btn-gap) auto !important;
    display: flex; align-items: center; justify-content: center;
    text-decoration: none !important;
  }}
  div[data-testid="stForm"] .stButton > button:hover {{
    background: linear-gradient(to bottom, #9ccc65, #AED581) !important;
    border-color: #7cb342 !important;
    color: white !important;
  }}
  div.stElementContainer:has(div.st-key-btn_trocar_evento_texto) {{
    margin-bottom: -25px !important;
  }}
  div.stElementContainer:has(div.st-key-btn_trocar_evento_texto),
  div.st-key-btn_trocar_evento_texto {{
    display: flex !important; width: 100% !important;
    justify-content: center !important; align-items: center !important;
    margin-top: 0px;
  }}
  div.st-key-btn_trocar_evento_texto button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #2E7D32 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    min-height: 0px !important;
    height: 26px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 auto !important;
  }}
  div.st-key-btn_trocar_evento_texto button p {{
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    padding-top: 2px !important;
  }}
  div.st-key-btn_trocar_evento_texto button:hover {{
    color: #1b5e20 !important; text-decoration: underline !important;
    transform: scale(1.05) !important; background: transparent !important;
  }}
  div[data-testid="stElementContainer"]:has(#marker-vermelho) {{
      margin-top: -12.5px !important;
      margin-bottom: 0px !important;
      line-height: 0;
  }}
  #marker-vermelho {{ display: none; }}
  div[data-testid="stElementContainer"]:has(#marker-vermelho) ~ div[data-testid="stElementContainer"]:nth-of-type(-n+4) .stButton > button {{
    background: linear-gradient(to bottom, #c62828, #e53935) !important; border-color: #a92222 !important;
  }}
  div[data-testid="stLinkButton"] a[href*="translate.google.com"],
  div[data-testid="stLinkButton"] a[href*="maps.google"] {{
    background: linear-gradient(to bottom, #2e7d32, #4caf50) !important; border-color: #1b5e20 !important;
  }}
  #marker-bsr-erb-form {{ display: none; }}
  div[data-testid="stElementContainer"]:has(#marker-bsr-erb-form) ~ div[data-testid="stElementContainer"] div[data-testid="stForm"] .stButton > button {{
    background: linear-gradient(to bottom, #2e7d32, #4caf50) !important;
    border-color: #1b5e20 !important;
  }}
  .confirm-warning{{ background: linear-gradient(to bottom, #f0ad4e, #ec971f); color:#333 !important; font-weight:600; text-align:center; padding:1rem; border-radius:8px; margin-bottom:1rem; border: 1px solid #d58512; }}
  .info-green {{ background: linear-gradient(to bottom, #1b5e20, #2e7d32); color: #fff; font-weight: 700; text-align: center; padding: .8rem 1rem; border-radius: 8px; margin: .25rem 0 1rem; }}
  .ute-table {{ width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; }}
  .ute-table th, .ute-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
  .ute-table th {{ background-color: #f2f2f2; color: #333; }}
  .copyable-cell {{ cursor: pointer; color: #14337b; font-weight: bold; }}
  .copyable-cell:hover {{ text-decoration: underline; background-color: #f0f0f0; }}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header(
    imagem_esq: str = "anatel.png",
    imagem_dir: str = "anatelS.png",
    show_logout: bool = False,
):
    b64_esq = _img_b64(imagem_esq)
    tag_esq = (
        f'<img class="hdr-img" src="data:image/png;base64,{b64_esq}" alt="Logo Esq">'
        if b64_esq
        else ""
    )
    b64_dir = _img_b64(imagem_dir)
    tag_dir = (
        f'<img class="hdr-img" src="data:image/png;base64,{b64_dir}" alt="Logo Dir">'
        if b64_dir
        else ""
    )
    evento_atual = st.session_state.get("evento_nome", "")
    st.markdown(
        f"""
        <div class="header-grid">
            <div style="text-align: right;">{tag_esq}</div>
            <div class="hdr-title">{TITULO_PRINCIPAL}</div>
            <div style="text-align: left;">{tag_dir}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if evento_atual:
        if show_logout:
            if st.button(
                f"Evento selecionado: {evento_atual} 🔄",
                key="btn_trocar_evento_texto",
                help="Clique para trocar de evento",
            ):
                for key in ["evento_nome", "spreadsheet_id", "view"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            st.markdown(
                f"<div style='text-align:center; color:#2E7D32; margin:0; font-size: 0.85rem; font-weight: 600; margin-top: -0.5px; margin-bottom: 0px; font-family: sans-serif;'>Evento selecionado: {evento_atual}</div>",
                unsafe_allow_html=True,
            )
    st.markdown(
        """
        <hr style='
            margin-top: -100px !important;
            margin-bottom: 2px !important;
            border: 0;
            border-top: 1px solid #ccc;
        '>
        """,
        unsafe_allow_html=True,
    )
