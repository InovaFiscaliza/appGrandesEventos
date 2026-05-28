import pandas as pd
import streamlit as st

from app.components.botoes import botao_voltar
from app.components.header import render_header
from app.services.google_sheets import carregar_dados_ute


def tela_tabela_ute(client, spread_id):
    render_header()
    evento_atual = st.session_state.get("evento_nome", "Evento")
    st.markdown(f"#### Atos de UTE - {evento_atual}")
    st.markdown(
        "<p style='text-align: center; font-size: small; margin-top: -0.5rem; margin-bottom: 0.5rem; color: #555;'>(gire o celular ⟳)</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <script>
    function copyToClipboard(text, element) {
        const el = document.createElement('textarea');
        el.value = text;
        el.style.position = 'absolute';
        el.style.left = '-9999px';
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        element.innerHTML = 'Copiado!';
        setTimeout(() => { element.innerHTML = text; }, 1500);
    }
    </script>
    """,
        unsafe_allow_html=True,
    )
    df = carregar_dados_ute(client, spread_id)
    if not df.empty:
        st.markdown(
            "<p style='text-align: center; font-size: 0.9rem; color: #555; margin-bottom: 0;'><b>Ordenar tabela por:</b></p>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            coluna_ordem = st.selectbox(
                "Coluna",
                ["Frequência (MHz)", "País/Entidade", "Local", "Processo SEI"],
                label_visibility="collapsed",
            )
        with col2:
            direcao = st.selectbox(
                "Direção", ["Crescente", "Decrescente"], label_visibility="collapsed"
            )
        ascendente = direcao == "Crescente"
        if coluna_ordem == "Frequência (MHz)":
            df["_ordem_temp"] = pd.to_numeric(
                df["Frequência (MHz)"].astype(str).str.replace(",", "."),
                errors="coerce",
            ).fillna(0)
            df = df.sort_values(by="_ordem_temp", ascending=ascendente).drop(
                columns=["_ordem_temp"]
            )
        else:
            df = df.sort_values(by=coluna_ordem, ascending=ascendente)
        html = "<table class='ute-table'><thead><tr>"
        html += "<th>País/Entidade</th><th>Local</th><th>Frequência (MHz)</th><th>Processo SEI</th>"
        html += "</tr></thead><tbody>"
        for _, row in df.iterrows():
            proc = str(row["Processo SEI"])
            html += f"<tr><td>{row['País/Entidade']}</td><td>{row['Local']}</td><td>{row['Frequência (MHz)']}</td>"
            html += f"<td class='copyable-cell' onclick='copyToClipboard(\"{proc}\", this)'>{proc}</td></tr>"
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Sem dados de UTE.")
    c1, c2 = st.columns(2)
    c1.link_button("SEI Interno", "https://sei.anatel.gov.br", use_container_width=True)
    c2.link_button(
        "SEI Público",
        "https://sei.anatel.gov.br/sei/modulos/pesquisa/md_pesq_processo_pesquisar.php?acao_externa=protocolo_pesquisar&acao_origem_externa=protocolo_pesquisar&id_orgao_acesso_externo=0",
        use_container_width=True,
    )
    if botao_voltar():
        st.session_state.view = "main_menu"
        st.rerun()
