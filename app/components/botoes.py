import pandas as pd
import streamlit as st


def botao_voltar(label="⬅️ Voltar ao Menu", key=None):
    left, center, right = st.columns([2, 2, 2])
    with center:
        return st.button(label, use_container_width=True, key=key)


def render_ocorrencia_readonly(row: pd.Series, key_prefix: str):
    """Renderiza os dados de uma ocorrência em modo somente leitura."""
    c1, c2 = st.columns(2)
    data_val = row.get("Data", row.get("Dia", ""))
    hora_val = row.get("HH:mm", row.get("Hora", ""))
    freq_val = row.get("Frequência (MHz)", row.get("Frequência", ""))
    bw_val = row.get("Largura (kHz)", row.get("BW", ""))
    with c1:
        st.text_input(
            "ID", value=str(row.get("ID", "")), disabled=True, key=f"{key_prefix}_id"
        )
        st.text_input(
            "Local/Estação",
            value=str(row.get("Local", row.get("Estação", row.get("Aba/Origem", "")))),
            disabled=True,
            key=f"{key_prefix}_loc",
        )
        st.text_input(
            "Fiscal",
            value=str(row.get("Fiscal", "")),
            disabled=True,
            key=f"{key_prefix}_fisc",
        )
        st.text_input(
            "Data da identificação",
            value=str(data_val),
            disabled=True,
            key=f"{key_prefix}_dt",
        )
        st.text_input(
            "Hora (HH:mm)", value=str(hora_val), disabled=True, key=f"{key_prefix}_hr"
        )
        st.text_input(
            "Frequência (MHz)",
            value=str(freq_val),
            disabled=True,
            key=f"{key_prefix}_frq",
        )
    with c2:
        st.text_input(
            "Largura (kHz)", value=str(bw_val), disabled=True, key=f"{key_prefix}_bw"
        )
        st.text_input(
            "Faixa de Frequência",
            value=str(row.get("Faixa de Frequência Envolvida", "")),
            disabled=True,
            key=f"{key_prefix}_faixa",
        )
        st.text_input(
            "Identificação",
            value=str(row.get("Identificação", "")),
            disabled=True,
            key=f"{key_prefix}_ident",
        )
        st.text_input(
            "Autorizado?",
            value=str(row.get("Autorizado?", "")),
            disabled=True,
            key=f"{key_prefix}_autz",
        )
        st.text_input(
            "Processo SEI UTE",
            value=str(row.get("Processo SEI UTE", row.get("Processo SEI", ""))),
            disabled=True,
            key=f"{key_prefix}_sei",
        )
        st.text_input(
            "Situação",
            value=str(row.get("Situação", "")),
            disabled=True,
            key=f"{key_prefix}_sit",
        )
    st.text_input(
        "Alguém mais ciente?",
        value=str(row.get("Alguém mais ciente?", "")),
        disabled=True,
        key=f"{key_prefix}_cient",
    )
    st.text_area(
        "Ocorrência (observações)",
        value=str(
            row.get("Ocorrência (observações)", row.get("Ocorrência (obsevações)", ""))
        ),
        disabled=True,
        key=f"{key_prefix}_obs",
    )
    st.caption(
        f"Fonte: {row.get('Fonte', 'N/A')} | Aba Origem: {row.get('Aba/Origem', 'N/A')}"
    )
