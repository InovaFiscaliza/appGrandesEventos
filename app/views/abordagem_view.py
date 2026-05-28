import pandas as pd
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from app.components.botoes import botao_voltar
from app.components.header import render_header
from app.config import FAIXA_OPCOES, IDENT_OPCOES, OBRIG
from app.services.google_sheets import (
    atualizar_campos_abordagem_por_id,
    atualizar_campos_na_aba_mae,
    carregar_opcoes_identificacao,
    carregar_pendencias_abordagem_pendentes,
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    inserir_emissao_I_W,
    obter_fuso_horario_evento,
    verificar_frequencia_global,
)


def tela_consultar(client, spread_id):
    render_header()
    st.markdown(
        '<div class="info-green">Consulte as emissões pendentes de identificação.</div>',
        unsafe_allow_html=True,
    )
    df_p = carregar_pendencias_painel_mapeadas(client, spread_id)
    df_a = carregar_pendencias_abordagem_pendentes(client, spread_id)
    df_e = carregar_pendencias_todas_estacoes(client, spread_id)
    dfs = [d for d in [df_p, df_a, df_e] if not d.empty]
    df_pend = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    if not df_pend.empty:
        opcoes = [
            f"{r['Local']} | {r['Data']} | {r['Frequência (MHz)']} MHz | {r.get('Ocorrência (observações)', '')} | {r['ID']}"
            for _, r in df_pend.iterrows()
        ]
        selecionado = st.selectbox(
            "Selecione a emissão:",
            options=opcoes,
            index=None,
            placeholder="Escolha uma pendência...",
        )
        if selecionado:
            idx = opcoes.index(selecionado)
            reg = df_pend.iloc[idx]
            st.markdown("#### Editar ocorrência")
            with st.form("form_editar_pendente"):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("ID", value=str(reg.get("ID", "")), disabled=True)
                    st.text_input(
                        "Estação utilizada",
                        value=str(reg.get("Local", "")),
                        disabled=True,
                    )
                    st.text_input(
                        "Fiscal", value=str(reg.get("Fiscal", "")), disabled=True
                    )
                    st.text_input(
                        "Data da identificação",
                        value=str(reg.get("Data", "")),
                        disabled=True,
                    )
                    st.text_input(
                        "HH:mm",
                        value=str(reg.get("HH:mm", "") or reg.get("Hora", "")),
                        disabled=True,
                    )
                    st.text_input(
                        "Frequência (MHz)",
                        value=str(reg.get("Frequência (MHz)", "")),
                        disabled=True,
                    )
                    st.text_input(
                        "Largura (kHz)",
                        value=str(reg.get("Largura (kHz)", "")),
                        disabled=True,
                    )
                    st.text_input(
                        "Faixa de Frequência Envolvida",
                        value=str(reg.get("Faixa de Frequência Envolvida", "")),
                        disabled=True,
                    )
                with c2:
                    ident_v = str(reg.get("Identificação", ""))
                    ident_edit = st.selectbox(
                        f"Identificação {OBRIG}",
                        IDENT_OPCOES,
                        index=(
                            IDENT_OPCOES.index(ident_v)
                            if ident_v in IDENT_OPCOES
                            else 0
                        ),
                    )
                    autz_v = str(reg.get("Autorizado?", ""))
                    autz_opts = ["Sim", "Não", "Não licenciável"]
                    autz_edit = st.selectbox(
                        f"Autorizado? {OBRIG}",
                        autz_opts,
                        index=autz_opts.index(autz_v) if autz_v in autz_opts else 2,
                    )
                    ute_check = st.checkbox(
                        "UTE?",
                        value=(
                            str(reg.get("UTE?", "")).lower()
                            in ["sim", "true", "1", "ok"]
                        ),
                    )
                    proc_edit = st.text_input(
                        "Processo SEI UTE (ou Ato UTE)",
                        value=str(reg.get("Processo SEI UTE", "")),
                    )
                    obs_edit = st.text_area(
                        "Ocorrência (observações)",
                        value=str(reg.get("Ocorrência (observações)", "")),
                    )
                    cient_edit = st.text_input(
                        "Alguém mais ciente?",
                        value=str(reg.get("Alguém mais ciente?", "")),
                    )
                    interf_v = str(reg.get("Interferente?", ""))
                    interf_opts = ["Sim", "Não", "Indefinido"]
                    interf_edit = st.selectbox(
                        f"Interferente? {OBRIG}",
                        interf_opts,
                        index=(
                            interf_opts.index(interf_v)
                            if interf_v in interf_opts
                            else 2
                        ),
                    )
                    situ_v = str(reg.get("Situação", "Pendente"))
                    situ_opts = ["Pendente", "Concluído"]
                    situ_edit = st.selectbox(
                        f"Situação {OBRIG}",
                        situ_opts,
                        index=situ_opts.index(situ_v) if situ_v in situ_opts else 0,
                    )
                if st.form_submit_button("Salvar alterações", use_container_width=True):
                    erros = []
                    if not ident_edit:
                        erros.append("Identificação")
                    if ute_check and not proc_edit:
                        erros.append("Processo SEI (UTE)")
                    if erros:
                        st.error("Faltam dados: " + ", ".join(erros))
                    else:
                        pac = {
                            "Identificação": ident_edit,
                            "Autorizado?": autz_edit,
                            "UTE?": "Sim" if ute_check else "Não",
                            "Processo SEI UTE": proc_edit,
                            "Ocorrência (observações)": obs_edit,
                            "Alguém mais ciente?": cient_edit,
                            "Interferente?": interf_edit,
                            "Situação": situ_edit,
                        }
                        if reg["Fonte"] in ("PAINEL", "ESTACAO"):
                            res = atualizar_campos_na_aba_mae(
                                client,
                                spread_id,
                                str(reg["EstacaoRaw"]),
                                str(reg["ID"]),
                                pac,
                            )
                        else:
                            res = atualizar_campos_abordagem_por_id(
                                client, spread_id, str(reg["ID"]), pac
                            )
                        st.success(res)
    else:
        st.success("✔️ Nenhuma pendência encontrada.")

    if botao_voltar():
        st.session_state.view = "main_menu"
        st.rerun()


def tela_inserir(client, spread_id):
    render_header()
    st.markdown(
        """
    <style>
    div[data-testid="stNumberInput"] button { display: none !important; }
    .stButton > button {
        background: linear-gradient(to bottom, #14337b, #4464A7) !important;
        border: 3.4px solid #54515c !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 600 !important;
        height: 3.8em !important;
    }
    .stButton > button:hover {
        background: linear-gradient(to bottom, #9ccc65, #AED581) !important;
        border-color: #7cb342 !important;
        color: white !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    def check_freq_callback():
        f_digitada = st.session_state.freq_input_key
        if f_digitada is not None and f_digitada > 0:
            st.session_state.aba_conflito = verificar_frequencia_global(
                client, spread_id, f_digitada
            )
        else:
            st.session_state.aba_conflito = None
        st.session_state.insert_success = None

    if "aba_conflito" not in st.session_state:
        st.session_state.aba_conflito = None
    if "insert_success" not in st.session_state:
        st.session_state.insert_success = None

    idents = carregar_opcoes_identificacao(client, spread_id)
    dados_prev = st.session_state.get("dados_para_salvar", {})

    with st.container(border=True):
        col1, col2 = st.columns(2)
        fuso_evento = obter_fuso_horario_evento(client, spread_id)
        val_dia = dados_prev.get("Dia", datetime.now(ZoneInfo(fuso_evento)).date())
        val_hora = dados_prev.get("Hora", datetime.now(ZoneInfo(fuso_evento)).time())
        dia = col1.date_input(f"Data {OBRIG}", value=val_dia, format="DD/MM/YYYY")
        hora = col2.time_input(f"Hora {OBRIG}", value=val_hora)
        fiscal = st.text_input(f"Fiscal {OBRIG}", value=dados_prev.get("Fiscal", ""))
        local = st.text_input("Local/Região", value=dados_prev.get("Local/Região", ""))
        c3, c4 = st.columns(2)
        val_freq = dados_prev.get("Frequência em MHz")
        val_freq = float(val_freq) if val_freq else None
        val_larg = dados_prev.get("Largura em kHz")
        val_larg = float(val_larg) if val_larg else None
        freq = c3.number_input(
            f"Frequência (MHz) {OBRIG}",
            value=val_freq,
            format="%.3f",
            key="freq_input_key",
            on_change=check_freq_callback,
        )
        larg = c4.number_input(f"Largura (kHz) {OBRIG}", value=val_larg, format="%.1f")
        if st.session_state.aba_conflito:
            st.markdown(
                f"""
                <div style="background-color: #d32f2f; color: white; padding: 12px; border-radius: 8px;
                            text-align: center; font-weight: bold; margin: 15px 0; border: 2px solid #b71c1c;">
                    ⚠️ AVISO (apenas): Essa frequência consta na Planilha - Aba: {st.session_state.aba_conflito}
                </div>
                """,
                unsafe_allow_html=True,
            )
        faixa = st.selectbox(
            f"Faixa relacionada {OBRIG}",
            FAIXA_OPCOES,
            index=None,
            placeholder="Selecione...",
        )
        ident = st.selectbox(
            f"Identificação {OBRIG}", idents, index=None, placeholder="Selecione..."
        )
        interferente = st.selectbox(
            f"Interferente? {OBRIG}",
            ["Sim", "Não", "Indefinido"],
            index=None,
            placeholder="Selecione...",
        )
        ute = st.checkbox("UTE?", value=dados_prev.get("UTE?", False))
        proc = st.text_input(
            "Processo SEI ou Ato UTE",
            value=dados_prev.get("Processo SEI ou Ato UTE", ""),
        )
        obs = st.text_area(
            f"Entidade Resp./Contato/Observações {OBRIG}",
            value=dados_prev.get("Observações/Detalhes/Contatos", ""),
        )
        situacao = st.selectbox(
            f"Status desta emissão {OBRIG}",
            ["Pendente", "Concluído"],
            index=None,
            placeholder="Selecione o status",
        )
        if st.session_state.insert_success:
            st.success(st.session_state.insert_success)
        if st.button("Registrar Emissão", use_container_width=True):
            erros = []
            if not fiscal:
                erros.append("Fiscal")
            if not freq or freq <= 0:
                erros.append("Frequência")
            if not situacao:
                erros.append("Status")
            if erros:
                st.error("Preencha os campos obrigatórios.")
                st.session_state.insert_success = None
            else:
                dados_submit = {
                    "Dia": dia,
                    "Hora": hora,
                    "Fiscal": fiscal,
                    "Local/Região": local,
                    "Frequência em MHz": freq,
                    "Largura em kHz": (larg if larg is not None else 0.0),
                    "Faixa de Frequência": faixa,
                    "Identificação": ident,
                    "UTE?": ute,
                    "Processo SEI ou Ato UTE": proc,
                    "Observações/Detalhes/Contatos": obs,
                    "Situação": situacao,
                    "Autorizado? (Q)": "Indefinido",
                    "Interferente?": interferente,
                }
                if inserir_emissao_I_W(client, spread_id, dados_submit):
                    st.session_state.insert_success = "Emissão inserida com sucesso."
                    st.session_state.aba_conflito = None
                    st.rerun()

    if botao_voltar():
        st.session_state.insert_success = None
        st.session_state.view = "main_menu"
        st.rerun()
