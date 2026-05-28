import streamlit as st

from app.components.header import _img_b64
from app.config import TITULO_PRINCIPAL
from app.services.google_sheets import buscar_planilhas


def tela_selecao_evento(client):
    st.markdown(
        """
        <style>
            div[data-testid="stImage"] { display: flex; justify-content: center; }
            div[data-testid="stImage"] > img { width: 170px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _, col_cent, _ = st.columns([1, 2, 1])
    with col_cent:
        img_b64 = _img_b64("anatel.png")
        if img_b64:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="data:image/png;base64,{img_b64}" width="170">
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<h3 style='text-align: center; color: #14337b;'>{TITULO_PRINCIPAL}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center;'>Selecione o evento para carregar a base de dados:</p>",
            unsafe_allow_html=True,
        )
        eventos_dict = buscar_planilhas(client)
        if not eventos_dict:
            st.error("Nenhuma planilha de 'Monitoração' encontrada.")
            return
        opcoes = list(eventos_dict.keys())

        def ao_selecionar():
            selecao = st.session_state.get("key_selecao_evento")
            if selecao:
                st.session_state["evento_nome"] = selecao
                st.session_state["spreadsheet_id"] = eventos_dict[selecao]
                st.session_state["view"] = "main_menu"

        st.selectbox(
            "Eventos Disponíveis:",
            opcoes,
            index=None,
            placeholder="Selecione...",
            key="key_selecao_evento",
            on_change=ao_selecionar,
        )
