"""
Entry point futuro da aplicação AppEventos.

ESTADO ATUAL
------------
O app roda via:  streamlit run abordagem.py
Todo o código ainda está em abordagem.py (não modificar durante a migração).

ESTADO ALVO (após migração completa)
-------------------------------------
O app passará a rodar via:  streamlit run main.py

Estrutura planejada:
  app/
    config.py          ← constantes globais (BTN_HEIGHT, ABAS_SISTEMA, etc.)
    router.py          ← roteador central (session_state["view"] → tela)
    services/
      google_sheets.py ← autenticação e operações na planilha
    utils/
      formatters.py    ← helpers puros (normalizar texto, busca livre)
    components/
      header.py        ← render_header()
      botoes.py        ← botao_voltar(), render_ocorrencia_readonly()
    views/
      selecao_evento.py  ← tela_selecao_evento()
      menu_principal.py  ← tela_menu_principal()
      abordagem_view.py  ← tela_consultar(), tela_inserir()
      bsr_erb.py         ← tela_bsr_erb()
      busca.py           ← tela_busca()
      tabela_ute.py      ← tela_tabela_ute()

Quando a migração estiver concluída, descomentar o bloco abaixo e
remover abordagem.py como entry point.
"""

import streamlit as st
from app.components.header import apply_app_css
from app.services.google_sheets import obter_cliente_gspread
from app.router import rotear

st.set_page_config(
    page_title="AppEventos",
    page_icon="anatel.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_app_css()

try:
    client = obter_cliente_gspread()
    rotear(client)
except Exception as e:
    st.error("Erro fatal na aplicação.")
    st.exception(e)
