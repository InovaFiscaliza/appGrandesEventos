import streamlit as st

from app.components.botoes import botao_voltar
from app.components.header import render_header
from app.config import OBRIG
from app.services.google_sheets import inserir_bsr_erb
from app.utils.formatters import _valid_neg_coord


def tela_bsr_erb(client, spread_id):
    render_header()
    st.markdown('<div id="marker-bsr-erb-form"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("##### Registrar Jammer ou ERB Fake")
        with st.form("form_bsr"):
            tipo = st.radio(f"Tipo {OBRIG}", ("BSR/Jammer", "ERB Fake"))
            regiao = st.text_input(f"Local {OBRIG}")
            c1, c2 = st.columns(2)
            lat = c1.text_input("Latitude (-N.NNNN)")
            lon = c2.text_input("Longitude (-N.NNNN)")
            submitted = st.form_submit_button("Registrar", use_container_width=True)
            if submitted:
                if not regiao:
                    st.error("O campo 'Local' é obrigatório.")
                elif not _valid_neg_coord(lat) or not _valid_neg_coord(lon):
                    st.error("Coordenadas inválidas. Use o formato -N.NNNNNN.")
                else:
                    res = inserir_bsr_erb(client, spread_id, tipo, regiao, lat, lon)
                    st.success(res)
    if botao_voltar(key="voltar_bsr"):
        st.session_state.view = "main_menu"
        st.rerun()
