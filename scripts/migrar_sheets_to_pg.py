"""
Script de migração: Google Sheets → PostgreSQL

Lê cada planilha do Google (via gspread) e popula as tabelas do PostgreSQL.
Pode ser executado múltiplas vezes (idempotente).

Uso:
    uv run scripts/migrar_sheets_to_pg.py
"""

import sys

sys.path.insert(0, ".")

import logging
import re
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from app.services.db import get_engine
from app.services.google_sheets import (
    abrir_planilha_selecionada,
    buscar_planilhas,
    listar_abas_estacoes,
    get_city_map_url,
    obter_fuso_horario_evento,
    obter_cliente_gspread,
)
from app.config import ABAS_SISTEMA

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("migracao")


def _parse_date(val) -> str | None:
    """Converte valor de data para string YYYY-MM-DD."""
    if val is None or str(val).strip() == "":
        return None
    v = str(val).strip()
    # Tenta DD/MM/YYYY
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", v)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # Tenta DD/MM/YY
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2})", v)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"20{y:02d}-{mo:02d}-{d:02d}"
    # Tenta ISO
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", v)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def _parse_time(val) -> str | None:
    """Converte valor de hora para string HH:MM."""
    if val is None or str(val).strip() == "":
        return None
    v = str(val).strip()
    m = re.match(r"(\d{1,2}):(\d{2})", v)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return f"{h:02d}:{mi:02d}"
    return None


def _parse_float(val) -> float | None:
    """Converte valor numérico (vírgula como separador decimal)."""
    if val is None or str(val).strip() == "":
        return None
    try:
        return round(float(str(val).replace(",", ".").strip()), 3)
    except (ValueError, TypeError):
        return None


def _parse_bool(val) -> bool:
    if val is None:
        return False
    v = str(val).strip().lower()
    return v in ("sim", "true", "1", "ok", "x", "yes")


def migrar():
    client = obter_cliente_gspread()
    planilhas = buscar_planilhas(client)
    logger.info(f"Encontradas {len(planilhas)} planilhas de monitoração.")

    engine = get_engine()

    for nome_evento, sheet_id in planilhas.items():
        logger.info(f"--- Migrando evento: {nome_evento} (sheet_id={sheet_id}) ---")
        try:
            _migrar_evento(client, engine, nome_evento, sheet_id)
        except Exception as e:
            logger.error(f"Falha ao migrar evento '{nome_evento}': {e}", exc_info=True)

    logger.info("Migração concluída!")


def _migrar_evento(client, engine, nome_evento, sheet_id):
    # 1. Cria/atualiza o evento
    fuso = obter_fuso_horario_evento(client, sheet_id)
    url_mapa = get_city_map_url(client, sheet_id)
    lat = None
    lon = None
    if url_mapa and "query=" in url_mapa:
        try:
            coords = url_mapa.split("query=")[1].split(",")
            lat = float(coords[0])
            lon = float(coords[1])
        except (ValueError, IndexError):
            pass

    with engine.begin() as conn:
        row = conn.execute(
            text("""
                INSERT INTO eventos (nome, legacy_sheet_id, latitude, longitude, fuso_horario)
                VALUES (:nome, :sid, :lat, :lon, :fuso)
                ON CONFLICT (nome)
                DO UPDATE SET legacy_sheet_id = EXCLUDED.legacy_sheet_id,
                              latitude = COALESCE(EXCLUDED.latitude, eventos.latitude),
                              longitude = COALESCE(EXCLUDED.longitude, eventos.longitude),
                              fuso_horario = EXCLUDED.fuso_horario
                RETURNING id
            """),
            {
                "nome": nome_evento,
                "sid": sheet_id,
                "lat": lat,
                "lon": lon,
                "fuso": fuso,
            },
        ).scalar()
        evento_id = row

    logger.info(f"  Evento ID: {evento_id}")

    planilha = abrir_planilha_selecionada(client, sheet_id)
    abas_estacoes = listar_abas_estacoes(client, sheet_id)

    # 2. Cria as estações
    estacao_ids = {}
    with engine.begin() as conn:
        for nome_est in abas_estacoes:
            row = conn.execute(
                text("""
                    INSERT INTO estacoes (evento_id, nome)
                    VALUES (:ev, :nome)
                    ON CONFLICT (evento_id, nome) DO NOTHING
                    RETURNING id
                """),
                {"ev": evento_id, "nome": nome_est},
            ).scalar()
            if row:
                estacao_ids[nome_est] = row
            else:
                # Já existe, buscar o id
                estacao_ids[nome_est] = conn.execute(
                    text(
                        "SELECT id FROM estacoes WHERE evento_id = :ev AND nome = :nome"
                    ),
                    {"ev": evento_id, "nome": nome_est},
                ).scalar()

    logger.info(f"  Estaçoes criadas: {len(estacao_ids)}")

    # 3. Migra aba "Abordagem" (colunas H a W)
    _migrar_abordagem(client, engine, planilha, evento_id, sheet_id)

    # 4. Migra abas de estação
    _migrar_estacoes(client, engine, planilha, evento_id, sheet_id, estacao_ids)

    # 5. Migra Tabela UTE
    _migrar_ute(client, engine, planilha, evento_id)

    # 6. Migra BSR/ERB (colunas X-AC da Abordagem)
    _migrar_bsr_erb(client, engine, planilha, evento_id)

    # 7. Migra opções de identificação (LISTAS)
    _migrar_opcoes(client, engine, planilha, evento_id)


def _migrar_abordagem(client, engine, planilha, evento_id, sheet_id):
    """Migra a aba Abordagem (colunas H-W) para ocorrencias."""
    try:
        aba = planilha.worksheet("Abordagem")
    except Exception:
        logger.info("  Aba 'Abordagem' não encontrada, pulando.")
        return

    try:
        matriz = aba.get("H1:W")
    except Exception:
        logger.info("  Sem dados na Abordagem (H:W).")
        return

    if not matriz or len(matriz) < 2:
        logger.info("  Abordagem sem linhas de dados.")
        return

    header, rows = matriz[0], matriz[1:]
    logger.info(f"  Abordagem: {len(rows)} linhas")

    with engine.begin() as conn:
        for i, row in enumerate(rows, start=2):
            if len(row) < 16:
                continue
            id_val = str(row[0]).strip() if row[0] else ""
            local = str(row[1]).strip() if len(row) > 1 else ""
            fiscal = str(row[2]).strip() if len(row) > 2 else ""
            data = _parse_date(row[3]) if len(row) > 3 else None
            hora = _parse_time(row[4]) if len(row) > 4 else None
            freq = _parse_float(row[5]) if len(row) > 5 else None
            bw = _parse_float(row[6]) if len(row) > 6 else None
            faixa = str(row[7]).strip() if len(row) > 7 else ""
            ident = str(row[8]).strip() if len(row) > 8 else ""
            autz = str(row[9]).strip() if len(row) > 9 else ""
            ute = _parse_bool(row[10]) if len(row) > 10 else False
            proc = str(row[11]).strip() if len(row) > 11 else ""
            obs = str(row[12]).strip() if len(row) > 12 else ""
            cient = str(row[13]).strip() if len(row) > 13 else ""
            inter = str(row[14]).strip() if len(row) > 14 else ""
            situ = str(row[15]).strip() if len(row) > 15 else "Pendente"

            if not freq and not fiscal:
                continue  # linha vazia

            conn.execute(
                text("""
                    INSERT INTO ocorrencias
                        (evento_id, id_planilha, local_regiao, fiscal, data, hora,
                         frequencia_mhz, largura_khz, faixa,
                         identificacao, autorizado, ute,
                         processo_sei_ute, observacoes, alguem_ciente,
                         interferente, situacao, fonte)
                    VALUES
                        (:ev, :id_p, :local, :fiscal, :data, :hora,
                         :freq, :bw, :faixa,
                         :ident, :autz, :ute,
                         :proc, :obs, :cient,
                         :inter, :situ, 'ABORDAGEM')
                """),
                {
                    "ev": evento_id,
                    "id_p": id_val or None,
                    "local": local or "Abordagem",
                    "fiscal": fiscal,
                    "data": data,
                    "hora": hora,
                    "freq": freq,
                    "bw": bw,
                    "faixa": faixa,
                    "ident": ident,
                    "autz": autz,
                    "ute": ute,
                    "proc": proc,
                    "obs": obs,
                    "cient": cient,
                    "inter": inter,
                    "situ": situ if situ else "Pendente",
                },
            )

    logger.info(f"  Abordagem migrada ({len(rows)} linhas processadas)")


def _migrar_estacoes(client, engine, planilha, evento_id, sheet_id, estacao_ids):
    """Migra cada aba de estação para ocorrencias."""
    for nome_est, est_id in estacao_ids.items():
        try:
            aba = planilha.worksheet(nome_est)
        except Exception:
            continue

        try:
            matriz = aba.get_all_values()
        except Exception:
            continue

        if not matriz or len(matriz) < 2:
            continue

        # Encontra a linha de cabeçalho
        header_idx = 0
        for i in range(min(6, len(matriz))):
            row_txt = [str(c).lower().strip() for c in matriz[i]]
            if any("situa" in x for x in row_txt) and (
                any(x == "id" for x in row_txt) or any("data" in x for x in row_txt)
            ):
                header_idx = i
                break

        header = matriz[header_idx]
        rows = matriz[header_idx + 1 :]

        # Mapeia colunas por nome
        col_map = {}
        for idx, name in enumerate(header):
            n = str(name).strip().lower() if name else ""
            if n == "id":
                col_map["id"] = idx
            elif "esta" in n or "local" in n:
                col_map["local"] = idx
            elif "fiscal" in n:
                col_map["fiscal"] = idx
            elif n in ("data", "dia"):
                col_map["data"] = idx
            elif "hh" in n or "hora" in n:
                col_map["hora"] = idx
            elif "frequ" in n:
                col_map["freq"] = idx
            elif "largura" in n:
                col_map["bw"] = idx
            elif "faixa" in n:
                col_map["faixa"] = idx
            elif "identifica" in n:
                col_map["ident"] = idx
            elif "autorizado" in n:
                col_map["autz"] = idx
            elif n == "ute" or "ute?" in n:
                col_map["ute"] = idx
            elif "processo" in n and "sei" in n:
                col_map["proc"] = idx
            elif "ocorren" in n or "observa" in n:
                col_map["obs"] = idx
            elif "ciente" in n:
                col_map["cient"] = idx
            elif "interferente" in n:
                col_map["inter"] = idx
            elif "situa" in n:
                col_map["situ"] = idx

        if "situ" not in col_map:
            continue

        with engine.begin() as conn:
            for row in rows:
                situ = (
                    str(row[col_map["situ"]]).strip().lower()
                    if len(row) > col_map["situ"]
                    else ""
                )
                if not situ:
                    continue
                id_val = (
                    str(row[col_map.get("id", 0)]).strip()
                    if "id" in col_map and len(row) > col_map["id"]
                    else ""
                )
                local = (
                    str(row[col_map["local"]]).strip()
                    if "local" in col_map and len(row) > col_map["local"]
                    else nome_est
                )
                fiscal = (
                    str(row[col_map["fiscal"]]).strip()
                    if "fiscal" in col_map and len(row) > col_map["fiscal"]
                    else ""
                )
                data = (
                    _parse_date(row[col_map["data"]])
                    if "data" in col_map and len(row) > col_map["data"]
                    else None
                )
                hora = (
                    _parse_time(row[col_map["hora"]])
                    if "hora" in col_map and len(row) > col_map["hora"]
                    else None
                )
                freq = (
                    _parse_float(row[col_map["freq"]])
                    if "freq" in col_map and len(row) > col_map["freq"]
                    else None
                )
                bw = (
                    _parse_float(row[col_map["bw"]])
                    if "bw" in col_map and len(row) > col_map["bw"]
                    else None
                )
                faixa = (
                    str(row[col_map["faixa"]]).strip()
                    if "faixa" in col_map and len(row) > col_map["faixa"]
                    else ""
                )
                ident = (
                    str(row[col_map["ident"]]).strip()
                    if "ident" in col_map and len(row) > col_map["ident"]
                    else ""
                )
                autz = (
                    str(row[col_map["autz"]]).strip()
                    if "autz" in col_map and len(row) > col_map["autz"]
                    else ""
                )
                ute = (
                    _parse_bool(row[col_map["ute"]])
                    if "ute" in col_map and len(row) > col_map["ute"]
                    else False
                )
                proc = (
                    str(row[col_map["proc"]]).strip()
                    if "proc" in col_map and len(row) > col_map["proc"]
                    else ""
                )
                obs = (
                    str(row[col_map["obs"]]).strip()
                    if "obs" in col_map and len(row) > col_map["obs"]
                    else ""
                )
                cient = (
                    str(row[col_map["cient"]]).strip()
                    if "cient" in col_map and len(row) > col_map["cient"]
                    else ""
                )
                inter = (
                    str(row[col_map["inter"]]).strip()
                    if "inter" in col_map and len(row) > col_map["inter"]
                    else ""
                )

                if not freq and not fiscal:
                    continue

                conn.execute(
                    text("""
                        INSERT INTO ocorrencias
                            (evento_id, estacao_id, id_planilha, local_regiao, fiscal, data, hora,
                             frequencia_mhz, largura_khz, faixa,
                             identificacao, autorizado, ute,
                             processo_sei_ute, observacoes, alguem_ciente,
                             interferente, situacao, fonte)
                        VALUES
                            (:ev, :est, :id_p, :local, :fiscal, :data, :hora,
                             :freq, :bw, :faixa,
                             :ident, :autz, :ute,
                             :proc, :obs, :cient,
                             :inter, :situ, 'ESTACAO')
                    """),
                    {
                        "ev": evento_id,
                        "est": est_id,
                        "id_p": id_val or None,
                        "local": local,
                        "fiscal": fiscal,
                        "data": data,
                        "hora": hora,
                        "freq": freq,
                        "bw": bw,
                        "faixa": faixa,
                        "ident": ident,
                        "autz": autz,
                        "ute": ute,
                        "proc": proc,
                        "obs": obs,
                        "cient": cient,
                        "inter": inter,
                        "situ": situ,
                    },
                )

        logger.info(f"  Estação '{nome_est}' migrada ({len(rows)} linhas)")


def _migrar_ute(client, engine, planilha, evento_id):
    """Migra a aba Tabela UTE."""
    try:
        aba = planilha.worksheet("Tabela UTE")
    except Exception:
        logger.info("  Aba 'Tabela UTE' não encontrada, pulando.")
        return

    try:
        matriz = aba.get_all_values()
    except Exception:
        return

    if not matriz or len(matriz) < 2:
        return

    with engine.begin() as conn:
        for row in matriz[1:]:
            if len(row) <= 7:
                continue
            pais = str(row[0]).strip() if row[0] else ""
            local = str(row[3]).strip() if row[3] else ""
            freq = _parse_float(row[4]) if row[4] else None
            proc = str(row[7]).strip() if row[7] else ""

            if not proc:
                continue

            conn.execute(
                text("""
                    INSERT INTO tabela_ute (evento_id, pais_entidade, local, frequencia_mhz, processo_sei)
                    VALUES (:ev, :pais, :local, :freq, :proc)
                """),
                {
                    "ev": evento_id,
                    "pais": pais,
                    "local": local,
                    "freq": freq,
                    "proc": proc,
                },
            )

    logger.info(f"  Tabela UTE migrada ({len(matriz) - 1} linhas)")


def _migrar_bsr_erb(client, engine, planilha, evento_id):
    """Migra BSR/Jammer e ERB Fake (colunas X-AC da Abordagem)."""
    try:
        aba = planilha.worksheet("Abordagem")
    except Exception:
        return

    try:
        matriz = aba.get("X1:AC")
    except Exception:
        return

    if not matriz or len(matriz) < 2:
        return

    header, rows = matriz[0], matriz[1:]
    with engine.begin() as conn:
        for row in rows:
            # Col X = "1" para BSR, Col Z = "1" para ERB
            if len(row) >= 2:
                bsr_marker = str(row[0]).strip() if row[0] else ""
                bsr_regiao = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                if bsr_marker in ("1", "Sim", "X", "x"):
                    bsr_lat = _parse_float(row[4]) if len(row) > 4 else None
                    bsr_lon = _parse_float(row[5]) if len(row) > 5 else None
                    conn.execute(
                        text("""
                            INSERT INTO bsr_erb (evento_id, tipo, regiao, latitude, longitude)
                            VALUES (:ev, 'BSR/Jammer', :reg, :lat, :lon)
                        """),
                        {
                            "ev": evento_id,
                            "reg": bsr_regiao,
                            "lat": bsr_lat,
                            "lon": bsr_lon,
                        },
                    )

            if len(row) >= 4:
                erb_marker = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                erb_regiao = str(row[3]).strip() if len(row) > 3 and row[3] else ""
                if erb_marker in ("1", "Sim", "X", "x"):
                    erb_lat = _parse_float(row[4]) if len(row) > 4 else None
                    erb_lon = _parse_float(row[5]) if len(row) > 5 else None
                    conn.execute(
                        text("""
                            INSERT INTO bsr_erb (evento_id, tipo, regiao, latitude, longitude)
                            VALUES (:ev, 'ERB Fake', :reg, :lat, :lon)
                        """),
                        {
                            "ev": evento_id,
                            "reg": erb_regiao,
                            "lat": erb_lat,
                            "lon": erb_lon,
                        },
                    )

    logger.info(f"  BSR/ERB migrados ({len(rows)} linhas)")


def _migrar_opcoes(client, engine, planilha, evento_id):
    """Migra opções de identificação (LISTAS / AC2:AC7)."""
    try:
        todas = planilha.worksheets()
        aba_alvo = next((ws for ws in todas if ws.title not in ABAS_SISTEMA), None)
        if not aba_alvo:
            return
        opcoes = [i[0] for i in aba_alvo.get("AC2:AC7") if i and i[0]]
    except Exception:
        return

    if not opcoes:
        return

    with engine.begin() as conn:
        for valor in opcoes:
            conn.execute(
                text("""
                    INSERT INTO opcoes_identificacao (evento_id, valor)
                    VALUES (:ev, :valor)
                    ON CONFLICT DO NOTHING
                """),
                {"ev": evento_id, "valor": str(valor).strip()},
            )

    logger.info(f"  Opções de identificação migradas ({len(opcoes)})")


if __name__ == "__main__":
    migrar()
