import streamlit as st

from app.views.abordagem_view import tela_consultar, tela_inserir
from app.views.bsr_erb import tela_bsr_erb
from app.views.busca import tela_busca
from app.views.menu_principal import tela_menu_principal
from app.views.selecao_evento import tela_selecao_evento
from app.views.tabela_ute import tela_tabela_ute


def rotear(client) -> None:
    if "view" not in st.session_state:
        st.session_state.view = "selecao"
    if "spreadsheet_id" not in st.session_state:
        st.session_state.spreadsheet_id = None

    if st.session_state.view == "selecao" or not st.session_state.spreadsheet_id:
        tela_selecao_evento(client)
        return

    sp_id = st.session_state.spreadsheet_id
    rotas = {
        "main_menu": lambda: tela_menu_principal(client, sp_id),
        "consultar": lambda: tela_consultar(client, sp_id),
        "inserir": lambda: tela_inserir(client, sp_id),
        "bsr_erb": lambda: tela_bsr_erb(client, sp_id),
        "busca": lambda: tela_busca(client, sp_id),
        "tabela_ute": lambda: tela_tabela_ute(client, sp_id),
    }
    handler = rotas.get(
        st.session_state.view, lambda: tela_menu_principal(client, sp_id)
    )
    handler()
