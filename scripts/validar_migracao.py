"""
Script de validação: Compara contagem de registros entre Google Sheets e PostgreSQL.

Uso:
    uv run scripts/validar_migracao.py
"""

import sys

sys.path.insert(0, ".")

import logging
from collections import defaultdict

from sqlalchemy import text

from app.services.db import get_engine
from app.services.google_sheets import (
    abrir_planilha_selecionada,
    buscar_planilhas,
    listar_abas_estacoes,
    obter_cliente_gspread,
)
from app.config import ABAS_SISTEMA

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("validacao")


def contar_sheets(client, engine):
    """Conta registros no Google Sheets e no PostgreSQL para cada evento/tabela."""
    planilhas = buscar_planilhas(client)
    logger.info(f"Encontradas {len(planilhas)} planilhas para validação.")

    resultados = []

    for nome_evento, sheet_id in planilhas.items():
        logger.info(f"--- Validando: {nome_evento} ---")
        planilha = abrir_planilha_selecionada(client, sheet_id)
        abas_estacao = listar_abas_estacoes(client, sheet_id)
        evento = dict(nome=nome_evento, sheet_id=sheet_id)

        # Buscar evento_id no PG
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT id FROM eventos WHERE nome = :nome"),
                {"nome": nome_evento},
            ).fetchone()
            evento_id = row[0] if row else None

        # --- Abordagem (colunas H-W) ---
        try:
            aba = planilha.worksheet("Abordagem")
            matriz = aba.get("H1:W")
            qtd_sheets_abordagem = max(0, len(matriz) - 1) if matriz else 0
        except Exception:
            qtd_sheets_abordagem = 0

        qtd_pg_abordagem = 0
        if evento_id:
            with engine.connect() as conn:
                qtd_pg_abordagem = (
                    conn.execute(
                        text(
                            "SELECT count(*) FROM ocorrencias WHERE evento_id = :ev AND fonte = 'ABORDAGEM'"
                        ),
                        {"ev": evento_id},
                    ).scalar()
                    or 0
                )

        resultados.append(
            dict(
                evento=nome_evento,
                tabela="Abordagem (ocorrências)",
                sheets=qtd_sheets_abordagem,
                postgres=qtd_pg_abordagem,
                diff=qtd_sheets_abordagem - qtd_pg_abordagem,
            )
        )

        # --- Abas de estação ---
        for nome_est in abas_estacao:
            try:
                aba = planilha.worksheet(nome_est)
                matriz = aba.get_all_values()
                # Encontra linha de cabeçalho
                header_idx = 0
                for i in range(min(6, len(matriz))):
                    row_txt = [str(c).lower().strip() for c in matriz[i]]
                    if any("situa" in x for x in row_txt):
                        header_idx = i
                        break
                rows = matriz[header_idx + 1 :]
                qtd = sum(1 for r in rows if len(r) > 0 and str(r[0]).strip())
            except Exception:
                qtd = 0

            # Buscar estacao_id e contar
            qtd_pg = 0
            if evento_id:
                with engine.connect() as conn:
                    est = conn.execute(
                        text(
                            "SELECT id FROM estacoes WHERE evento_id = :ev AND nome = :nome"
                        ),
                        {"ev": evento_id, "nome": nome_est},
                    ).fetchone()
                    if est:
                        qtd_pg = (
                            conn.execute(
                                text(
                                    "SELECT count(*) FROM ocorrencias WHERE estacao_id = :est"
                                ),
                                {"est": est[0]},
                            ).scalar()
                            or 0
                        )

            resultados.append(
                dict(
                    evento=nome_evento,
                    tabela=f"Estação: {nome_est}",
                    sheets=qtd,
                    postgres=qtd_pg,
                    diff=qtd - qtd_pg,
                )
            )

        # --- Tabela UTE ---
        try:
            aba_ute = planilha.worksheet("Tabela UTE")
            qtd_sheets_ute = max(0, len(aba_ute.get_all_values()) - 1)
        except Exception:
            qtd_sheets_ute = 0

        qtd_pg_ute = 0
        if evento_id:
            with engine.connect() as conn:
                qtd_pg_ute = (
                    conn.execute(
                        text("SELECT count(*) FROM tabela_ute WHERE evento_id = :ev"),
                        {"ev": evento_id},
                    ).scalar()
                    or 0
                )

        resultados.append(
            dict(
                evento=nome_evento,
                tabela="Tabela UTE",
                sheets=qtd_sheets_ute,
                postgres=qtd_pg_ute,
                diff=qtd_sheets_ute - qtd_pg_ute,
            )
        )

        # --- BSR/ERB (coluna X-AC da Abordagem) ---
        try:
            aba = planilha.worksheet("Abordagem")
            bsr_matriz = aba.get("X1:AC")
            if bsr_matriz and len(bsr_matriz) > 1:
                qtd_sheets_bsr = 0
                for r in bsr_matriz[1:]:
                    if len(r) >= 1 and str(r[0]).strip() in ("1", "Sim", "X", "x"):
                        qtd_sheets_bsr += 1
                    if len(r) >= 3 and str(r[2]).strip() in ("1", "Sim", "X", "x"):
                        qtd_sheets_bsr += 1
            else:
                qtd_sheets_bsr = 0
        except Exception:
            qtd_sheets_bsr = 0

        qtd_pg_bsr = 0
        if evento_id:
            with engine.connect() as conn:
                qtd_pg_bsr = (
                    conn.execute(
                        text("SELECT count(*) FROM bsr_erb WHERE evento_id = :ev"),
                        {"ev": evento_id},
                    ).scalar()
                    or 0
                )

        resultados.append(
            dict(
                evento=nome_evento,
                tabela="BSR/ERB",
                sheets=qtd_sheets_bsr,
                postgres=qtd_pg_bsr,
                diff=qtd_sheets_bsr - qtd_pg_bsr,
            )
        )

    return resultados


def exibir_resultados(resultados):
    """Exibe tabela comparativa."""
    print()
    print("=" * 100)
    print(f"{'EVENTO':<25} {'TABELA':<35} {'SHEETS':>8} {'POSTGRES':>10} {'DIF':>8}")
    print("=" * 100)

    totais_sheets = 0
    totais_pg = 0
    divergencias = 0

    for r in resultados:
        diff = r["diff"]
        flag = " <<<" if diff != 0 else ""
        if diff != 0:
            divergencias += 1
        print(
            f"{r['evento']:<25} {r['tabela']:<35} {r['sheets']:>8} {r['postgres']:>10} {diff:>8}{flag}"
        )
        totais_sheets += r["sheets"]
        totais_pg += r["postgres"]

    print("=" * 100)
    print(
        f"{'TOTAIS':<25} {'':<35} {totais_sheets:>8} {totais_pg:>10} {totais_sheets - totais_pg:>8}"
    )
    print()

    if divergencias == 0:
        logger.info("✅ VALIDAÇÃO CONCLUÍDA — TODOS OS REGISTROS CONFEREM!")
    else:
        logger.warning(
            f"⚠️  VALIDAÇÃO CONCLUÍDA — {divergencias} divergência(s) encontrada(s)!"
        )


def main():
    client = obter_cliente_gspread()
    engine = get_engine()

    logger.info("Iniciando validação Google Sheets ↔ PostgreSQL...")
    resultados = contar_sheets(client, engine)
    exibir_resultados(resultados)


if __name__ == "__main__":
    main()
