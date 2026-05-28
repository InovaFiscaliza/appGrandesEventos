import unicodedata

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from app.config import ABAS_SISTEMA
from app.utils.formatters import (
    _col_to_index,
    _first_col_match,
    _first_empty_row_in_block,
    _first_row_where_col_empty,
    _next_sequential_id,
    _normalize_text,
)
from typing import Dict, List


@st.cache_resource(ttl=3600, show_spinner=False)
def obter_cliente_gspread():
    try:
        info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(
            info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        return None


def buscar_planilhas(client):
    if not client:
        return {}
    try:
        arquivos = client.list_spreadsheet_files()
        planilhas = {}
        termo = "monitoracao"
        for arq in arquivos:
            nome_real = arq["name"]
            file_id = arq["id"]
            nome_norm = "".join(
                c
                for c in unicodedata.normalize("NFD", nome_real)
                if unicodedata.category(c) != "Mn"
            ).lower()
            if termo in nome_norm:
                nome_exibicao = (
                    nome_real.replace("Monitoração - ", "")
                    .replace("Monitoracao - ", "")
                    .replace("MONITORAÇÃO - ", "")
                )
                planilhas[nome_exibicao] = file_id
        return planilhas
    except Exception as e:
        st.error(f"Erro ao listar arquivos: {e}")
        return {}


def abrir_planilha_selecionada(_client, spreadsheet_id):
    return _client.open_by_key(spreadsheet_id)


@st.cache_data(ttl=150, show_spinner=False)
def listar_abas_estacoes(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        todas = [ws.title for ws in planilha.worksheets()]
        return [t for t in todas if t not in ABAS_SISTEMA]
    except Exception:
        return []


def get_city_map_url(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        abas_estacoes = [
            ws for ws in planilha.worksheets() if ws.title not in ABAS_SISTEMA
        ]
        if abas_estacoes:
            aba = abas_estacoes[0]
            lat = aba.cell(3, 31).value
            lon = aba.cell(4, 31).value
            if lat and lon:
                lat = str(lat).replace(",", ".").strip()
                lon = str(lon).replace(",", ".").strip()
                return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    except Exception:
        pass
    return "https://www.google.com/maps"


def verificar_frequencia_existente(client, spreadsheet_id, freq_digitada):
    if not freq_digitada or freq_digitada <= 0:
        return None
    try:
        f_val = round(float(freq_digitada), 3)
        planilha = abrir_planilha_selecionada(client, spreadsheet_id)
        aba_abord = planilha.worksheet("Abordagem")
        col_m = aba_abord.col_values(13)
        for val in col_m[1:]:
            try:
                if round(float(str(val).replace(",", ".")), 3) == f_val:
                    return "Abordagem"
            except Exception:
                continue
        aba_ute = planilha.worksheet("Tabela UTE")
        col_e = aba_ute.col_values(5)
        for val in col_e[1:]:
            try:
                if round(float(str(val).replace(",", ".")), 3) == f_val:
                    return "Tabela UTE"
            except Exception:
                continue
        estacoes = listar_abas_estacoes(client, spreadsheet_id)
        for nome_est in estacoes:
            aba_est = planilha.worksheet(nome_est)
            col_f = aba_est.col_values(6)
            for val in col_f[1:]:
                try:
                    if round(float(str(val).replace(",", ".")), 3) == f_val:
                        return f"Estação {nome_est}"
                except Exception:
                    continue
    except Exception:
        pass
    return None


def verificar_frequencia_global(client, spreadsheet_id, freq_digitada):
    if freq_digitada <= 0:
        return None
    try:
        f_val = round(float(freq_digitada), 3)
        planilha = abrir_planilha_selecionada(client, spreadsheet_id)
        aba_abord = planilha.worksheet("Abordagem")
        col_m = aba_abord.col_values(13)
        for val in col_m[1:]:
            try:
                if round(float(str(val).replace(",", ".")), 3) == f_val:
                    return "Abordagem"
            except Exception:
                continue
        aba_ute = planilha.worksheet("Tabela UTE")
        entidades = aba_ute.col_values(1)
        freqs_ute = aba_ute.col_values(5)
        for i in range(1, len(freqs_ute)):
            try:
                if round(float(str(freqs_ute[i]).replace(",", ".")), 3) == f_val:
                    entidade = (
                        entidades[i] if i < len(entidades) else "Não identificada"
                    )
                    return f"UTE [Entidade: {entidade}]"
            except Exception:
                continue
        estacoes = listar_abas_estacoes(client, spreadsheet_id)
        for nome_est in estacoes:
            aba_est = planilha.worksheet(nome_est)
            col_f = aba_est.col_values(6)
            for val in col_f[1:]:
                try:
                    if round(float(str(val).replace(",", ".")), 3) == f_val:
                        return f"Estação {nome_est}"
                except Exception:
                    continue
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def obter_fuso_horario_evento(_client, spreadsheet_id):
    fuso_padrao = "America/Sao_Paulo"
    try:
        from timezonefinder import TimezoneFinder

        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        abas_estacoes = [
            ws for ws in planilha.worksheets() if ws.title not in ABAS_SISTEMA
        ]
        if abas_estacoes:
            aba = abas_estacoes[0]
            lat_str = aba.cell(3, 31).value
            lon_str = aba.cell(4, 31).value
            if lat_str and lon_str:
                lat = float(str(lat_str).replace(",", ".").strip())
                lon = float(str(lon_str).replace(",", ".").strip())
                tf = TimezoneFinder()
                fuso_encontrado = tf.timezone_at(lng=lon, lat=lat)
                if fuso_encontrado:
                    return fuso_encontrado
    except Exception:
        pass
    return fuso_padrao


@st.cache_data(ttl=150, show_spinner=False)
def carregar_dados_ute(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("Tabela UTE")
        matriz = aba.get_all_values()
        if not matriz or len(matriz) < 2:
            return pd.DataFrame()
        dados = []
        for row in matriz[1:]:
            if len(row) > 7:
                dados.append(
                    {
                        "País/Entidade": row[0],
                        "Local": row[3],
                        "Frequência (MHz)": row[4],
                        "Processo SEI": row[7],
                    }
                )
        df = pd.DataFrame(dados)
        df = df[df["Processo SEI"].str.strip() != ""]
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=150, show_spinner=False)
def carregar_pendencias_painel_mapeadas(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("PAINEL")
        matriz = aba.get("A1:AF")
        if not matriz or len(matriz) < 2:
            return pd.DataFrame()
        header, rows = matriz[0], matriz[1:]
        df = pd.DataFrame(rows, columns=header)

        def col_like(*checks):
            return _first_col_match(
                df.columns, *[(lambda s, c=c: c(s)) for c in checks]
            )

        cols_map = {
            "situ": lambda s: s == "situação" or s == "situacao",
            "est": lambda s: "estação" in s or "estacao" in s,
            "id": lambda s: s == "id",
            "fiscal": lambda s: "fiscal" in s,
            "data": lambda s: s == "data" or s == "dia",
            "hora": lambda s: "hh" in s or "hora" in s,
            "freq": lambda s: "frequência" in s or "frequencia" in s,
            "bw": lambda s: "largura" in s,
            "faixa": lambda s: "faixa" in s and "envolvida" in s,
            "ident": lambda s: "identificação" in s,
            "autz": lambda s: "autorizado" in s,
            "ute": lambda s: s.strip() == "ute" or "ute?" in s,
            "proc": lambda s: "processo" in s and "sei" in s,
            "obs": lambda s: "ocorrência" in s or "observa" in s,
            "cient": lambda s: "ciente" in s,
            "inter": lambda s: "interferente" in s,
        }
        found_cols = {k: col_like(v) for k, v in cols_map.items()}
        if not (found_cols["situ"] and found_cols["est"] and found_cols["id"]):
            return pd.DataFrame()
        situ = df[found_cols["situ"]].astype(str).str.strip().str.lower()
        pend = df[situ.eq("pendente")].copy()
        if pend.empty:
            return pd.DataFrame()
        out = pd.DataFrame()
        out["Local"] = pend[found_cols["est"]]
        out["EstacaoRaw"] = pend[found_cols["est"]]
        out["ID"] = pend[found_cols["id"]]
        mappings = [
            ("Fiscal", "fiscal"),
            ("Data", "data"),
            ("HH:mm", "hora"),
            ("Frequência (MHz)", "freq"),
            ("Largura (kHz)", "bw"),
            ("Faixa de Frequência Envolvida", "faixa"),
            ("Identificação", "ident"),
            ("Autorizado?", "autz"),
            ("UTE?", "ute"),
            ("Processo SEI UTE", "proc"),
            ("Ocorrência (observações)", "obs"),
            ("Alguém mais ciente?", "cient"),
            ("Interferente?", "inter"),
            ("Situação", "situ"),
        ]
        for dest, key in mappings:
            out[dest] = pend[found_cols[key]] if found_cols[key] else ""
        out = out.sort_values(
            by=["Local", "Data"], kind="stable", na_position="last"
        ).reset_index(drop=True)
        out["Fonte"] = "PAINEL"
        return out
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=150, show_spinner=False)
def carregar_pendencias_abordagem_pendentes(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("Abordagem")
        matriz = aba.get("H1:W")
        if not matriz or len(matriz) < 2:
            return pd.DataFrame()
        header, rows = matriz[0], matriz[1:]

        def get_col(idx_offset):
            return pd.Series(
                [
                    str(r[idx_offset]).strip() if len(r) > idx_offset else ""
                    for r in rows
                ]
            )

        pend = pd.DataFrame(
            {
                "ID": get_col(0),
                "Local": get_col(1),
                "Fiscal": get_col(2),
                "Data": get_col(3),
                "HH:mm": get_col(4),
                "Frequência (MHz)": get_col(5),
                "Largura (kHz)": get_col(6),
                "Faixa de Frequência Envolvida": get_col(7),
                "Identificação": get_col(8),
                "Autorizado?": get_col(9),
                "UTE?": get_col(10),
                "Processo SEI UTE": get_col(11),
                "Ocorrência (observações)": get_col(12),
                "Alguém mais ciente?": get_col(13),
                "Interferente?": get_col(14),
                "Situação": get_col(15),
                "EstacaoRaw": "ABORDAGEM",
                "Fonte": "ABORDAGEM",
            }
        )
        pend = pend[pend["Situação"].str.lower().str.strip() == "pendente"].copy()
        return pend.sort_values(by=["Local", "Data"], kind="stable").reset_index(
            drop=True
        )
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=150, show_spinner=False)
def carregar_pendencias_todas_estacoes(_client, spreadsheet_id):
    try:
        estacoes = listar_abas_estacoes(_client, spreadsheet_id)
        if not estacoes:
            return pd.DataFrame()
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        dfs = []
        for nome_aba in estacoes:
            try:
                aba = planilha.worksheet(nome_aba)
                matriz = aba.get_all_values()
                if not matriz or len(matriz) < 2:
                    continue
                header_idx = 0
                for i in range(min(6, len(matriz))):
                    row_txt = [str(c).lower().strip() for c in matriz[i]]
                    if any("situa" in x for x in row_txt) and (
                        any("id" == x for x in row_txt)
                        or any("data" in x for x in row_txt)
                    ):
                        header_idx = i
                        break
                header = matriz[header_idx]
                rows = matriz[header_idx + 1 :]
                df = pd.DataFrame(rows, columns=header)

                def col_like(*checks):
                    return _first_col_match(
                        df.columns, *[(lambda s, c=c: c(s)) for c in checks]
                    )

                cols_map = {
                    "est": lambda s: "estação" in s or "estacao" in s or "local" in s,
                    "situ": lambda s: "situação" in s or "situacao" in s,
                    "id": lambda s: s == "id",
                    "fiscal": lambda s: "fiscal" in s,
                    "data": lambda s: "data" in s or "dia" in s,
                    "hora": lambda s: "hh" in s or "hora" in s,
                    "freq": lambda s: "frequência" in s or "frequencia" in s,
                    "bw": lambda s: "largura" in s,
                    "faixa": lambda s: "faixa" in s,
                    "ident": lambda s: "identificação" in s,
                    "autz": lambda s: "autorizado" in s,
                    "ute": lambda s: "ute" in s,
                    "proc": lambda s: "processo" in s,
                    "obs": lambda s: "ocorrência" in s or "observa" in s,
                    "cient": lambda s: "ciente" in s,
                    "inter": lambda s: "interferente" in s,
                }
                found = {k: col_like(v) for k, v in cols_map.items()}
                if not found["situ"]:
                    continue
                situ = df[found["situ"]].astype(str).str.strip().str.lower()
                pend = df[situ.eq("pendente")].copy()
                if pend.empty:
                    continue
                out = pd.DataFrame()
                out["ID"] = (
                    pend[found["id"]]
                    if found["id"]
                    else (pend.iloc[:, 0] if len(pend.columns) > 0 else "")
                )
                if found["est"]:
                    out["Local"] = pend[found["est"]]
                elif len(pend.columns) > 1:
                    out["Local"] = pend.iloc[:, 1]
                else:
                    out["Local"] = nome_aba
                out["EstacaoRaw"] = nome_aba
                if found["data"]:
                    out["Data"] = pend[found["data"]]
                else:
                    out["Data"] = pend.iloc[:, 3] if len(pend.columns) > 3 else ""
                mappings = [
                    ("Fiscal", "fiscal"),
                    ("HH:mm", "hora"),
                    ("Frequência (MHz)", "freq"),
                    ("Largura (kHz)", "bw"),
                    ("Faixa de Frequência Envolvida", "faixa"),
                    ("Identificação", "ident"),
                    ("Autorizado?", "autz"),
                    ("UTE?", "ute"),
                    ("Processo SEI UTE", "proc"),
                    ("Ocorrência (observações)", "obs"),
                    ("Alguém mais ciente?", "cient"),
                    ("Interferente?", "inter"),
                    ("Situação", "situ"),
                ]
                for dest, key in mappings:
                    out[dest] = pend[found[key]] if found[key] else ""
                out["Fonte"] = "ESTACAO"
                dfs.append(out)
            except Exception:
                pass
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=150, show_spinner=False)
def carregar_todas_frequencias(_client, spreadsheet_id):
    frequencias_map = {}
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba_painel = planilha.worksheet("PAINEL")
        dados_painel = aba_painel.get("B2:G")
        for row in dados_painel:
            if len(row) >= 6:
                estacao, freq = row[0], row[5]
                if estacao and freq:
                    try:
                        f_val = round(float(str(freq).replace(",", ".")), 3)
                        if f_val not in frequencias_map:
                            frequencias_map[f_val] = estacao
                    except Exception:
                        pass
        aba_abord = planilha.worksheet("Abordagem")
        dados_abord = aba_abord.get("I2:M")
        for row in dados_abord:
            if len(row) >= 5:
                regiao, freq = row[0], row[4]
                if regiao and freq:
                    try:
                        f_val = round(float(str(freq).replace(",", ".")), 3)
                        if f_val not in frequencias_map:
                            frequencias_map[f_val] = regiao
                    except Exception:
                        pass
    except Exception:
        pass
    return frequencias_map


def atualizar_campos_na_aba_mae(
    _client, spreadsheet_id, estacao_raw, id_ocorrencia, novos_valores: Dict[str, str]
) -> str:
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        try:
            aba = planilha.worksheet(estacao_raw)
        except Exception:
            return f"ERRO: Aba '{estacao_raw}' não encontrada na planilha."
        header = aba.row_values(1)
        cell = aba.find(str(id_ocorrencia), in_column=1)
        if not cell:
            return f"ERRO: ID {id_ocorrencia} não encontrado."

        def find_col(*checks):
            for idx, name in enumerate(header, start=1):
                s = (name or "").strip().lower()
                for p in checks:
                    if p(s):
                        return idx
            return None

        cols_idx = {
            "Situação": find_col(lambda s: s == "situação" or s == "situacao"),
            "Identificação": find_col(lambda s: "identificação" in s),
            "Autorizado?": find_col(lambda s: "autorizado" in s),
            "UTE?": find_col(lambda s: "ute" in s),
            "Processo SEI UTE": find_col(lambda s: "processo" in s),
            "Ocorrência (observações)": find_col(lambda s: "ocorrência" in s),
            "Alguém mais ciente?": find_col(lambda s: "ciente" in s),
            "Interferente?": find_col(lambda s: "interferente" in s),
        }
        updates = []
        for key, val in novos_valores.items():
            if key in cols_idx and cols_idx[key]:
                updates.append((cell.row, cols_idx[key], val))
        for r, c, v in updates:
            aba.update_cell(r, c, v)
        return f"Atualizado na aba '{aba.title}'."
    except Exception as e:
        return f"ERRO ao atualizar: {e}"


def atualizar_campos_abordagem_por_id(
    _client, spreadsheet_id, id_h: str, novos_valores: Dict[str, str]
) -> str:
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("Abordagem")
        cell = aba.find(str(id_h), in_column=_col_to_index("H"))
        if not cell:
            return "Registro não encontrado."
        col_map = {
            "Identificação": "P",
            "Autorizado?": "Q",
            "UTE?": "R",
            "Processo SEI UTE": "S",
            "Ocorrência (observações)": "T",
            "Alguém mais ciente?": "U",
            "Interferente?": "V",
            "Situação": "W",
        }
        for k, v in novos_valores.items():
            if k in col_map:
                aba.update_cell(cell.row, _col_to_index(col_map[k]), v)
        return "Alterações salvas na 'Abordagem'."
    except Exception as e:
        return f"Erro: {e}"


def inserir_emissao_I_W(
    _client, spreadsheet_id, dados_formulario: Dict[str, str]
) -> bool:
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("Abordagem")
        row = _first_row_where_col_empty(aba, "M", start_row=2)
        next_id = _next_sequential_id(aba, col_letter="H", start_row=2)
        dia = dados_formulario.get("Dia")
        if hasattr(dia, "strftime"):
            dia = dia.strftime("%d/%m/%Y")
        hora = dados_formulario.get("Hora")
        if hasattr(hora, "strftime"):
            hora = hora.strftime("%H:%M")
        vals = [
            dados_formulario.get("Local/Região", "Abordagem"),
            dados_formulario.get("Fiscal", ""),
            dia,
            hora,
            float(dados_formulario.get("Frequência em MHz", 0)),
            float(dados_formulario.get("Largura em kHz", 0)),
            dados_formulario.get("Faixa de Frequência", ""),
            dados_formulario.get("Identificação", ""),
            dados_formulario.get("Autorizado? (Q)", ""),
            "Sim" if dados_formulario.get("UTE?") else "Não",
            dados_formulario.get("Processo SEI ou Ato UTE", ""),
            f"{dados_formulario.get('Observações/Detalhes/Contatos', '')} - {dados_formulario.get('Responsável pela emissão', '')}",
            "",
            dados_formulario.get("Interferente?", ""),
            dados_formulario.get("Situação", "Pendente"),
        ]
        aba.update(f"H{row}", [[str(next_id)]], value_input_option="RAW")
        aba.update(f"I{row}:W{row}", [vals], value_input_option="RAW")
        return True
    except Exception as e:
        st.error(f"Erro inserção: {e}")
        return False


def inserir_bsr_erb(_client, spreadsheet_id, tipo, regiao, lat, lon) -> str:
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        aba = planilha.worksheet("Abordagem")
        row = _first_empty_row_in_block(aba, "X", "AC")
        coords = [[lat or "", lon or ""]]
        if tipo == "BSR/Jammer":
            aba.update(
                f"X{row}:Y{row}", [["1", regiao]], value_input_option="USER_ENTERED"
            )
        else:
            aba.update(
                f"Z{row}:AA{row}", [["1", regiao]], value_input_option="USER_ENTERED"
            )
        aba.update(f"AB{row}:AC{row}", coords, value_input_option="USER_ENTERED")
        return f"'{tipo}' incluído com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_opcoes_identificacao(_client, spreadsheet_id):
    try:
        planilha = abrir_planilha_selecionada(_client, spreadsheet_id)
        todas = planilha.worksheets()
        aba_alvo = next((ws for ws in todas if ws.title not in ABAS_SISTEMA), None)
        if aba_alvo:
            return [i[0] for i in aba_alvo.get("AC2:AC7") if i]
        return ["Opções não encontradas"]
    except Exception:
        return ["Opção genérica (erro leitura)"]


def _buscar_por_texto_livre(
    client, spreadsheet_id, termos: str, abas: List[str]
) -> pd.DataFrame:
    planilha = abrir_planilha_selecionada(client, spreadsheet_id)
    resultados = []
    termos_norm = _normalize_text(termos)
    for nome in abas:
        try:
            aba = planilha.worksheet(nome)
            all_vals = aba.get_all_values()
            if not all_vals:
                continue
            if nome == "Abordagem":
                header = all_vals[0][7:23]
                rows = [r[7:23] for r in all_vals[1:]]
                df = pd.DataFrame(rows, columns=header)
                df = df.rename(
                    columns={
                        "Estação": "Local",
                        "Ocorrência (obsevações)": "Ocorrência (observações)",
                    }
                )
            else:
                df = pd.DataFrame(all_vals[1:], columns=all_vals[0])
                df = df.iloc[:, ~df.columns.duplicated()]
            df.insert(0, "Aba/Origem", nome)
            df["Fonte"] = "BUSCA"
            comb = df.fillna("").astype(str).agg(" ".join, axis=1)
            mask = comb.apply(lambda x: termos_norm in _normalize_text(x))
            achados = df[mask].copy()
            if not achados.empty:
                resultados.append(achados)
        except Exception:
            continue
    if not resultados:
        return pd.DataFrame()
    return pd.concat(resultados, ignore_index=True)
