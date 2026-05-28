import streamlit as st

from app.components.botoes import botao_voltar, render_ocorrencia_readonly
from app.components.header import render_header
from app.services.google_sheets import _buscar_por_texto_livre, listar_abas_estacoes


def tela_busca(client, spread_id):
    render_header()
    termo = st.text_input("Buscar texto (mín 3 chars):")
    abas_est = listar_abas_estacoes(client, spread_id)
    abas_ops = ["Abordagem"] + abas_est
    abas_sel = st.multiselect("Abas:", abas_ops, default=abas_ops)

    if st.button("Consultar", use_container_width=True):
        termo_clean = termo.strip()
        if len(termo_clean) < 3:
            st.warning("Digite pelo menos 3 caracteres para consultar.")
        else:
            with st.spinner("Buscando..."):
                res = _buscar_por_texto_livre(client, spread_id, termo_clean, abas_sel)
            if res.empty:
                st.info("Nenhum resultado encontrado.")
            else:
                st.success(f"Resultados encontrados: {len(res)}")
                for i, (_, row) in enumerate(res.iterrows(), start=1):
                    cabecalho = []
                    aba_origem = row.get("Aba/Origem", "")
                    loc = row.get(
                        "Local", row.get("Local/Região", row.get("Estação", ""))
                    )
                    if not loc and aba_origem:
                        loc = aba_origem
                    if loc:
                        cabecalho.append(str(loc))
                    dt = row.get("Data", row.get("Dia", ""))
                    if dt:
                        cabecalho.append(str(dt))
                    fr = row.get("Frequência (MHz)", row.get("Frequência", ""))
                    if fr:
                        cabecalho.append(f"{fr} MHz")
                    id_val = row.get("ID", "")
                    if id_val:
                        cabecalho.append(f"ID {id_val}")
                    titulo_expander = (
                        " | ".join(cabecalho) if cabecalho else f"Resultado #{i}"
                    )
                    with st.expander(titulo_expander):
                        render_ocorrencia_readonly(
                            row, key_prefix=f"busca_{i}_{id_val}"
                        )

    if botao_voltar(key="voltar_busca"):
        st.session_state.view = "main_menu"
        st.rerun()
