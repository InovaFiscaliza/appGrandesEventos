import streamlit as st

from app.components.header import render_header
from app.services.google_sheets import (
    carregar_pendencias_abordagem_pendentes,
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    get_city_map_url,
)


def tela_menu_principal(client, spread_id):
    render_header(show_logout=True)
    with st.spinner("Carregando base de dados..."):
        df_painel = carregar_pendencias_painel_mapeadas(client, spread_id)
        df_abord = carregar_pendencias_abordagem_pendentes(client, spread_id)
        df_estac = carregar_pendencias_todas_estacoes(client, spread_id)
        link_mapa = get_city_map_url(client, spread_id)

    count_painel = len(df_painel) if df_painel is not None else 0
    count_abord = len(df_abord) if df_abord is not None else 0
    count_estac = len(df_estac) if df_estac is not None else 0
    total = count_painel + count_abord + count_estac
    label_tratar = f"**📝 TRATAR** emissões pendentes ({total})"

    _, button_col, _ = st.columns([1, 2, 1])
    with button_col:
        st.markdown('<div id="marker-vermelho"></div>', unsafe_allow_html=True)
        if st.button(
            "**📋 INSERIR** emissão verificada em campo",
            use_container_width=True,
            key="btn_inserir",
        ):
            st.session_state.view = "inserir"
            st.rerun()
        if st.button(label_tratar, use_container_width=True, key="btn_consultar"):
            st.session_state.view = "consultar"
            st.rerun()
        if st.button(
            "**📵 REGISTRAR** Jammer ou ERB Fake",
            use_container_width=True,
            key="btn_bsr",
        ):
            st.session_state.view = "bsr_erb"
            st.rerun()
        if st.button(
            "**🔎 PESQUISAR** emissões cadastradas",
            use_container_width=True,
            key="btn_buscar",
        ):
            st.session_state.view = "busca"
            st.rerun()
        if st.button(
            "🗒️ **CONSULTAR** Atos de UTE", use_container_width=True, key="btn_ute"
        ):
            st.session_state.view = "tabela_ute"
            st.rerun()
        st.link_button(
            "🗺️ **Mapa da Região/Evento**", link_mapa, use_container_width=True
        )
        st.link_button(
            "🌍 **Tradutor de Texto/Voz**",
            "https://translate.google.com/?sl=auto&tl=pt&op=translate",
            use_container_width=True,
        )
