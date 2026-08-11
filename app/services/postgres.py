"""
Serviço de dados PostgreSQL — substitui google_sheets.py mantendo o mesmo contrato.

Cada função tem o MESMO nome e assinatura (retornos: pd.DataFrame, str, bool, dict)
que a equivalente em google_sheets.py, para que routers/views não precisem ser alterados.

O parâmetro _client é ignorado (mantido apenas para compatibilidade de assinatura).
O parâmetro spreadsheet_id é tratado como evento_id (inteiro).
"""

import base64
import logging
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import text

from app.config import IDENT_OPCOES, USR_FISCAL_ANATEL
from app.services.db import get_engine

logger = logging.getLogger(__name__)


class FrequenciaOcupadaError(Exception):
    """Indica que a frequência já está cadastrada no evento selecionado."""


# =========================================================================
# Utilitários internos
# =========================================================================


def _escape_like(s: str) -> str:
    """Escapa caracteres especiais LIKE do PostgreSQL."""
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def carregar_imagens_ocorrencia(evento_id=None, ocorrencia_id=None) -> list[dict]:
    """Retorna imagens da ocorrência como data URLs para previews no navegador."""
    with get_engine().connect() as conn:
        registros = conn.execute(
            text("""
                SELECT oi.id, oi.nome_arquivo, oi.tipo_mime, oi.conteudo
                FROM ocorrencia_imagens oi
                JOIN ocorrencias o ON o.id = oi.ocorrencia_id
                WHERE o.evento_id = :evento_id AND o.id = :ocorrencia_id
                ORDER BY oi.id
            """),
            {"evento_id": evento_id, "ocorrencia_id": ocorrencia_id},
        ).mappings()
        return [
            {
                "id": registro["id"],
                "nome_arquivo": registro["nome_arquivo"],
                "url": (
                    f"data:{registro['tipo_mime']};base64,"
                    f"{base64.b64encode(bytes(registro['conteudo'])).decode('ascii')}"
                ),
            }
            for registro in registros
        ]


def carregar_imagem_ocorrencia(evento_id=None, ocorrencia_id=None, imagem_id=None):
    """Retorna o conteúdo de uma imagem somente dentro da ocorrência informada."""
    with get_engine().connect() as conn:
        registro = (
            conn.execute(
                text("""
                SELECT oi.tipo_mime, oi.conteudo
                FROM ocorrencia_imagens oi
                JOIN ocorrencias o ON o.id = oi.ocorrencia_id
                WHERE o.evento_id = :evento_id
                  AND o.id = :imagem_id
                  AND oi.ocorrencia_id = :ocorrencia_id
            """),
                {
                    "evento_id": int(evento_id),
                    "ocorrencia_id": int(ocorrencia_id),
                    "imagem_id": int(imagem_id),
                },
            )
            .mappings()
            .first()
        )
    return registro


# =========================================================================
# Eventos (era buscar_planilhas / listar_abas_estacoes)
# =========================================================================


def buscar_planilhas(_client=None) -> dict:
    """Retorna {nome_evento: str(evento_id)} — mesmo formato do google_sheets."""
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text("SELECT nome, id FROM eventos ORDER BY nome")
            ).all()
        return {nome: str(ev_id) for nome, ev_id in rows}
    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}", exc_info=True)
        return {}


def listar_abas_estacoes(_client=None, evento_id=None) -> list:
    """Retorna lista de nomes de estações de um evento."""
    if evento_id is None:
        return []
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text("SELECT nome FROM estacoes WHERE evento_id = :ev ORDER BY nome"),
                {"ev": int(evento_id)},
            ).all()
        return [r[0] for r in rows]
    except Exception as e:
        logger.error(f"Erro ao listar estações: {e}", exc_info=True)
        return []


# =========================================================================
# Metadados do evento
# =========================================================================


def get_city_map_url(_client=None, evento_id=None) -> str:
    """Retorna URL do Google Maps com a localização do evento."""
    if evento_id is None:
        return "https://www.google.com/maps"
    try:
        with get_engine().connect() as conn:
            row = conn.execute(
                text("SELECT latitude, longitude FROM eventos WHERE id = :ev"),
                {"ev": int(evento_id)},
            ).first()
        if row and row[0] and row[1]:
            lat = str(row[0]).replace(",", ".")
            lon = str(row[1]).replace(",", ".")
            return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    except Exception:
        pass
    return "https://www.google.com/maps"


def obter_fuso_horario_evento(_client=None, evento_id=None) -> str:
    """Retorna o fuso horário do evento (ex: 'America/Sao_Paulo')."""
    if evento_id is None:
        return "America/Sao_Paulo"
    try:
        with get_engine().connect() as conn:
            row = conn.execute(
                text("SELECT fuso_horario FROM eventos WHERE id = :ev"),
                {"ev": int(evento_id)},
            ).first()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return "America/Sao_Paulo"


# =========================================================================
# Verificação de frequência
# =========================================================================


def verificar_frequencia_existente(
    _client=None, evento_id=None, freq_digitada=None
) -> Optional[str]:
    """Verifica se a frequência já existe (ocorrências ou UTE)."""
    if not freq_digitada or freq_digitada <= 0 or evento_id is None:
        return None
    try:
        f_val = round(float(freq_digitada), 3)
        with get_engine().connect() as conn:
            # Checa ocorrências
            row = conn.execute(
                text("""
                    SELECT COALESCE(e.nome, o.local_regiao)
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev AND round(o.frequencia_mhz, 3) = :f
                    LIMIT 1
                """),
                {"ev": int(evento_id), "f": f_val},
            ).first()
            if row:
                return row[0]
            # Checa UTE
            row = conn.execute(
                text("""
                    SELECT 'Tabela UTE'
                    FROM tabela_ute
                    WHERE evento_id = :ev AND round(frequencia_mhz, 3) = :f
                    LIMIT 1
                """),
                {"ev": int(evento_id), "f": f_val},
            ).first()
            if row:
                return row[0]
    except Exception:
        pass
    return None


def verificar_frequencia_global(
    _client=None, evento_id=None, freq_digitada=None
) -> Optional[str]:
    """Verifica se a frequência existe em ocorrências ou UTE (com detalhe)."""
    if not freq_digitada or freq_digitada <= 0 or evento_id is None:
        return None
    try:
        f_val = round(float(freq_digitada), 3)
        with get_engine().connect() as conn:
            # Ocorrências
            row = conn.execute(
                text("""
                    SELECT COALESCE(e.nome, o.local_regiao)
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev AND round(o.frequencia_mhz, 3) = :f
                    LIMIT 1
                """),
                {"ev": int(evento_id), "f": f_val},
            ).first()
            if row:
                return row[0]
            # UTE com nome da entidade
            row = conn.execute(
                text("""
                    SELECT 'UTE [Entidade: ' || COALESCE(pais_entidade, 'Não identificada') || ']'
                    FROM tabela_ute
                    WHERE evento_id = :ev AND round(frequencia_mhz, 3) = :f
                    LIMIT 1
                """),
                {"ev": int(evento_id), "f": f_val},
            ).first()
            if row:
                return row[0]
    except Exception:
        pass
    return None


# =========================================================================
# Pendências (carregar_pendencias_*)
# =========================================================================


def carregar_pendencias_painel_mapeadas(_client=None, evento_id=None) -> pd.DataFrame:
    """Retorna pendências de todas as ocorrências (equivalente ao PAINEL)."""
    if evento_id is None:
        return pd.DataFrame()
    try:
        sql = text("""
            SELECT
                COALESCE(e.nome, o.local_regiao) AS "Local",
                COALESCE(e.nome, o.local_regiao) AS "EstacaoRaw",
                o.id::text AS "ID",
                o.fiscal AS "Fiscal",
                o.data::text AS "Data",
                to_char(
                    ((o.data + o.hora) AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(ev.fuso_horario, 'America/Sao_Paulo')),
                    'HH24:MI'
                ) AS "HH:mm",
                o.frequencia_mhz::text AS "Frequência (MHz)",
                o.largura_khz::text AS "Largura (kHz)",
                o.faixa AS "Faixa de Frequência Envolvida",
                o.identificacao AS "Identificação",
                o.autorizado AS "Autorizado?",
                CASE WHEN o.ute THEN 'Sim' ELSE 'Não' END AS "UTE?",
                o.processo_sei_ute AS "Processo SEI UTE",
                o.observacoes AS "Ocorrência (observações)",
                o.alguem_ciente AS "Alguém mais ciente?",
                o.interferente AS "Interferente?",
                o.situacao AS "Situação",
                o.fonte AS "Fonte"
            FROM ocorrencias o
            LEFT JOIN estacoes e ON e.id = o.estacao_id
            JOIN eventos ev ON ev.id = o.evento_id
            WHERE o.evento_id = :ev
              AND lower(trim(o.situacao)) = 'pendente'
            ORDER BY "Local", "Data"
        """)
        return pd.read_sql(sql, get_engine(), params={"ev": int(evento_id)})
    except Exception as e:
        logger.error(f"Erro carregar_pendencias_painel_mapeadas: {e}", exc_info=True)
        return pd.DataFrame()


def carregar_pendencias_abordagem_pendentes(
    _client=None, evento_id=None
) -> pd.DataFrame:
    """Retorna pendências com fonte = 'ABORDAGEM'."""
    if evento_id is None:
        return pd.DataFrame()
    try:
        sql = text("""
            SELECT
                o.id::text AS "ID",
                COALESCE(o.local_regiao, 'Abordagem') AS "Local",
                o.fiscal AS "Fiscal",
                o.data::text AS "Data",
                to_char(
                    ((o.data + o.hora) AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(ev.fuso_horario, 'America/Sao_Paulo')),
                    'HH24:MI'
                ) AS "HH:mm",
                o.frequencia_mhz::text AS "Frequência (MHz)",
                o.largura_khz::text AS "Largura (kHz)",
                o.faixa AS "Faixa de Frequência Envolvida",
                o.identificacao AS "Identificação",
                o.autorizado AS "Autorizado?",
                CASE WHEN o.ute THEN 'Sim' ELSE 'Não' END AS "UTE?",
                o.processo_sei_ute AS "Processo SEI UTE",
                o.observacoes AS "Ocorrência (observações)",
                o.alguem_ciente AS "Alguém mais ciente?",
                o.interferente AS "Interferente?",
                o.situacao AS "Situação",
                'ABORDAGEM' AS "EstacaoRaw",
                'ABORDAGEM' AS "Fonte"
            FROM ocorrencias o
            JOIN eventos ev ON ev.id = o.evento_id
            WHERE o.evento_id = :ev
              AND o.fonte = 'ABORDAGEM'
              AND lower(trim(o.situacao)) = 'pendente'
            ORDER BY o.local_regiao, o.data
        """)
        return pd.read_sql(sql, get_engine(), params={"ev": int(evento_id)})
    except Exception as e:
        logger.error(
            f"Erro carregar_pendencias_abordagem_pendentes: {e}", exc_info=True
        )
        return pd.DataFrame()


def carregar_pendencias_todas_estacoes(_client=None, evento_id=None) -> pd.DataFrame:
    """Retorna pendências de todas as estações (fonte = 'ESTACAO')."""
    if evento_id is None:
        return pd.DataFrame()
    try:
        sql = text("""
            SELECT
                COALESCE(e.nome, o.local_regiao) AS "Local",
                COALESCE(e.nome, o.local_regiao) AS "EstacaoRaw",
                o.id::text AS "ID",
                o.fiscal AS "Fiscal",
                o.data::text AS "Data",
                to_char(
                    ((o.data + o.hora) AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(ev.fuso_horario, 'America/Sao_Paulo')),
                    'HH24:MI'
                ) AS "HH:mm",
                o.frequencia_mhz::text AS "Frequência (MHz)",
                o.largura_khz::text AS "Largura (kHz)",
                o.faixa AS "Faixa de Frequência Envolvida",
                o.identificacao AS "Identificação",
                o.autorizado AS "Autorizado?",
                CASE WHEN o.ute THEN 'Sim' ELSE 'Não' END AS "UTE?",
                o.processo_sei_ute AS "Processo SEI UTE",
                o.observacoes AS "Ocorrência (observações)",
                o.alguem_ciente AS "Alguém mais ciente?",
                o.interferente AS "Interferente?",
                o.situacao AS "Situação",
                'ESTACAO' AS "Fonte"
            FROM ocorrencias o
            JOIN estacoes e ON e.id = o.estacao_id
            JOIN eventos ev ON ev.id = o.evento_id
            WHERE o.evento_id = :ev
              AND lower(trim(o.situacao)) = 'pendente'
            ORDER BY "Local", "Data"
        """)
        return pd.read_sql(sql, get_engine(), params={"ev": int(evento_id)})
    except Exception as e:
        logger.error(f"Erro carregar_pendencias_todas_estacoes: {e}", exc_info=True)
        return pd.DataFrame()


def carregar_todas_frequencias(_client=None, evento_id=None) -> dict:
    """Retorna {frequencia: local} para todas as ocorrências."""
    if evento_id is None:
        return {}
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT round(o.frequencia_mhz, 3) as freq,
                           COALESCE(e.nome, o.local_regiao) as local
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev AND o.frequencia_mhz IS NOT NULL
                    ORDER BY freq
                """),
                {"ev": int(evento_id)},
            ).all()
        return {float(r[0]): r[1] for r in rows if r[0] is not None}
    except Exception as e:
        logger.error(f"Erro carregar_todas_frequencias: {e}", exc_info=True)
        return {}


# =========================================================================
# UTE
# =========================================================================


def carregar_dados_ute(_client=None, evento_id=None) -> pd.DataFrame:
    """Retorna DataFrame com País/Entidade, Local, Frequência (MHz), Processo SEI."""
    if evento_id is None:
        return pd.DataFrame()
    try:
        sql = text("""
            SELECT
                pais_entidade AS "País/Entidade",
                local AS "Local",
                frequencia_mhz::text AS "Frequência (MHz)",
                processo_sei AS "Processo SEI"
            FROM tabela_ute
            WHERE evento_id = :ev
              AND trim(COALESCE(processo_sei, '')) != ''
            ORDER BY frequencia_mhz
        """)
        return pd.read_sql(sql, get_engine(), params={"ev": int(evento_id)})
    except Exception as e:
        logger.error(f"Erro carregar_dados_ute: {e}", exc_info=True)
        return pd.DataFrame()


# =========================================================================
# Opções de identificação
# =========================================================================


def carregar_opcoes_identificacao(_client=None, evento_id=None) -> list:
    """Retorna lista de opções de identificação (do banco ou fallback fixo)."""
    if evento_id is None:
        return IDENT_OPCOES
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT DISTINCT valor FROM opcoes_identificacao
                    WHERE (evento_id = :ev OR evento_id IS NULL)
                    ORDER BY valor
                """),
                {"ev": int(evento_id)},
            ).all()
        if rows:
            return [r[0] for r in rows]
    except Exception:
        pass
    return IDENT_OPCOES


# =========================================================================
# Teste e etiquetagem
# =========================================================================


def verificar_etiqueta_existente(
    _client=None, numero_etiqueta=None, excluir_id=None
) -> Optional[dict]:
    """Retorna evento e data do primeiro cadastro da etiqueta, se houver."""
    numero = str(numero_etiqueta or "").strip()
    if not numero:
        return None
    try:
        with get_engine().connect() as conn:
            row = (
                conn.execute(
                    text("""
                          SELECT e.nome AS evento,
                              to_char(t.criado_em, 'DD/MM/YYYY') AS data,
                              t.entidade,
                              t.cpf_cnpj
                    FROM testes_etiquetagem t
                    JOIN eventos e ON e.id = t.evento_id
                    WHERE trim(t.numero_etiqueta) = trim(:numero)
                      AND (:excluir_id IS NULL OR t.id <> :excluir_id)
                    ORDER BY t.criado_em, t.id
                    LIMIT 1
                """),
                    {"numero": numero, "excluir_id": excluir_id},
                )
                .mappings()
                .first()
            )
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Erro verificar_etiqueta_existente: {e}", exc_info=True)
        return None


def verificar_frequencia_etiquetagem(
    _client=None, evento_id=None, freq_digitada=None, excluir_id=None
) -> Optional[str]:
    """Retorna a origem de uma frequência já cadastrada no evento, se houver."""
    if evento_id is None or freq_digitada is None:
        return None
    try:
        frequencia = round(float(freq_digitada), 3)
    except (TypeError, ValueError):
        return None
    if frequencia <= 0:
        return None

    try:
        with get_engine().connect() as conn:
            row = conn.execute(
                text("""
                    SELECT COALESCE(e.nome, o.local_regiao, 'Ocorrências')
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev
                      AND round(o.frequencia_mhz, 3) = :freq
                    LIMIT 1
                """),
                {"ev": int(evento_id), "freq": frequencia},
            ).first()
            if row:
                return f"Ocorrências ({row[0]})"

            row = conn.execute(
                text("""
                    SELECT 'Tabela UTE'
                    FROM tabela_ute
                    WHERE evento_id = :ev
                      AND round(frequencia_mhz, 3) = :freq
                    LIMIT 1
                """),
                {"ev": int(evento_id), "freq": frequencia},
            ).first()
            if row:
                return row[0]

            row = conn.execute(
                text("""
                    SELECT 'Teste de etiquetagem: ' || entidade
                    FROM testes_etiquetagem t
                    CROSS JOIN LATERAL unnest(t.frequencias_selecionadas) AS selecionada
                    WHERE t.evento_id = :ev
                      AND round(
                            replace(split_part(selecionada, ' MHz', 1), ',', '.')::numeric,
                            3
                          ) = :freq
                      AND (:excluir_id IS NULL OR t.id <> :excluir_id)
                    LIMIT 1
                """),
                {"ev": int(evento_id), "freq": frequencia, "excluir_id": excluir_id},
            ).first()
            if row:
                return row[0]
    except Exception as e:
        logger.error(f"Erro verificar_frequencia_etiquetagem: {e}", exc_info=True)
    return None


def consultar_equipamentos_frequencia(
    _client=None, evento_id=None, freq_digitada=None, excluir_id=None
) -> dict:
    """Consulta equipamentos e referências cadastrados na frequência do evento."""
    resultado = {"equipamentos": [], "referencias": []}
    if evento_id is None or freq_digitada is None:
        return resultado
    try:
        frequencia = round(float(freq_digitada), 3)
    except (TypeError, ValueError):
        return resultado
    if frequencia <= 0:
        return resultado

    try:
        with get_engine().connect() as conn:
            equipamentos = (
                conn.execute(
                    text("""
                    SELECT t.id, t.entidade, t.cpf_cnpj, t.contato, t.local,
                           t.tipo_equipamento, t.numero_etiqueta,
                           t.equipamento_homologado, selecionada AS frequencia
                    FROM testes_etiquetagem t
                    CROSS JOIN LATERAL unnest(t.frequencias_selecionadas) AS selecionada
                    WHERE t.evento_id = :ev
                                            AND round(
                                                        replace(split_part(selecionada, ' MHz', 1), ',', '.')::numeric,
                                                        3
                                                    ) = :freq
                      AND (:excluir_id IS NULL OR t.id <> :excluir_id)
                    ORDER BY t.id
                """),
                    {
                        "ev": int(evento_id),
                        "freq": frequencia,
                        "excluir_id": excluir_id,
                    },
                )
                .mappings()
                .all()
            )
            resultado["equipamentos"] = [dict(row) for row in equipamentos]

            ocorrencias = (
                conn.execute(
                    text("""
                    SELECT 'Ocorrência' AS origem,
                           COALESCE(e.nome, o.local_regiao, 'Local não informado') AS detalhe
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev
                      AND round(o.frequencia_mhz, 3) = :freq
                    LIMIT 5
                """),
                    {"ev": int(evento_id), "freq": frequencia},
                )
                .mappings()
                .all()
            )
            ute = (
                conn.execute(
                    text("""
                    SELECT 'Tabela UTE' AS origem,
                           COALESCE(pais_entidade, 'Entidade não informada') AS detalhe
                    FROM tabela_ute
                    WHERE evento_id = :ev
                      AND round(frequencia_mhz, 3) = :freq
                    LIMIT 5
                """),
                    {"ev": int(evento_id), "freq": frequencia},
                )
                .mappings()
                .all()
            )
            resultado["referencias"] = [dict(row) for row in [*ocorrencias, *ute]]
    except Exception as e:
        logger.error(f"Erro consultar_equipamentos_frequencia: {e}", exc_info=True)
    return resultado


def inserir_teste_etiquetagem(_client=None, evento_id=None, dados: dict = None) -> str:
    """Insere um teste de etiquetagem vinculado ao evento selecionado."""
    if evento_id is None or dados is None:
        return "ERRO: parâmetros insuficientes."
    try:
        with get_engine().begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO testes_etiquetagem (
                        evento_id, licenca, perfil, entidade, contato, local,
                        cpf_cnpj,
                        equipamento_homologado, permissao,
                        frequencias_selecionadas, tipo_equipamento,
                        numero_etiqueta, observacoes
                    ) VALUES (
                        :ev, :licenca, :perfil, :entidade, :contato, :local,
                        :cpf_cnpj,
                        :homologado, :permissao, :frequencias,
                        :tipo_equipamento, :numero_etiqueta, :observacoes
                    )
                """),
                {
                    "ev": int(evento_id),
                    "licenca": dados["licenca"],
                    "perfil": dados["perfil"],
                    "entidade": dados["entidade"],
                    "contato": dados.get("contato", ""),
                    "local": dados["local"],
                    "cpf_cnpj": dados.get("cpf_cnpj", ""),
                    "homologado": bool(dados.get("equipamento_homologado")),
                    "permissao": dados["permissao"],
                    "frequencias": dados.get("frequencias_selecionadas", []),
                    "tipo_equipamento": dados["tipo_equipamento"],
                    "numero_etiqueta": dados["numero_etiqueta"],
                    "observacoes": dados.get("observacoes", ""),
                },
            )
        return "Teste de etiquetagem inserido com sucesso."
    except Exception as e:
        logger.error(f"Erro inserir_teste_etiquetagem: {e}", exc_info=True)
        if "testes_etiquetagem_evento_id_numero_etiqueta_key" in str(e):
            return "ERRO: o número da etiqueta já existe neste evento."
        return f"ERRO ao inserir teste de etiquetagem: {e}"


def listar_testes_etiquetagem(_client=None, evento_id=None) -> list[dict]:
    """Lista os testes de etiquetagem cadastrados no evento selecionado."""
    if evento_id is None:
        return []
    try:
        with get_engine().connect() as conn:
            rows = (
                conn.execute(
                    text("""
                    SELECT id, licenca, perfil, entidade, contato, local,
                              cpf_cnpj,
                           equipamento_homologado, permissao,
                           frequencias_selecionadas, tipo_equipamento,
                           numero_etiqueta, observacoes, criado_em, atualizado_em
                    FROM testes_etiquetagem
                    WHERE evento_id = :ev
                    ORDER BY criado_em DESC, id DESC
                """),
                    {"ev": int(evento_id)},
                )
                .mappings()
                .all()
            )
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Erro ao listar testes de etiquetagem: {e}", exc_info=True)
        return []


def obter_teste_etiquetagem(
    _client=None, evento_id=None, registro_id=None
) -> dict | None:
    """Obtém um teste de etiquetagem pertencente ao evento selecionado."""
    if evento_id is None or registro_id is None:
        return None
    try:
        with get_engine().connect() as conn:
            row = (
                conn.execute(
                    text("""
                    SELECT id, licenca, perfil, entidade, contato, local,
                              cpf_cnpj,
                           equipamento_homologado, permissao,
                           frequencias_selecionadas, tipo_equipamento,
                           numero_etiqueta, observacoes
                    FROM testes_etiquetagem
                    WHERE id = :id AND evento_id = :ev
                """),
                    {"id": int(registro_id), "ev": int(evento_id)},
                )
                .mappings()
                .first()
            )
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Erro ao obter teste de etiquetagem: {e}", exc_info=True)
        return None


def atualizar_teste_etiquetagem(
    _client=None, evento_id=None, registro_id=None, dados: dict = None
) -> str:
    """Atualiza um teste de etiquetagem pertencente ao evento selecionado."""
    if evento_id is None or registro_id is None or dados is None:
        return "ERRO: parâmetros insuficientes."
    try:
        with get_engine().begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE testes_etiquetagem
                    SET licenca = :licenca, perfil = :perfil, entidade = :entidade,
                        contato = :contato, local = :local, cpf_cnpj = :cpf_cnpj,
                        equipamento_homologado = :homologado, permissao = :permissao,
                        frequencias_selecionadas = :frequencias,
                        tipo_equipamento = :tipo_equipamento,
                        numero_etiqueta = :numero_etiqueta, observacoes = :observacoes,
                        atualizado_em = now()
                    WHERE id = :id AND evento_id = :ev
                """),
                {
                    "id": int(registro_id),
                    "ev": int(evento_id),
                    "licenca": dados["licenca"],
                    "perfil": dados["perfil"],
                    "entidade": dados["entidade"],
                    "contato": dados.get("contato", ""),
                    "local": dados["local"],
                    "cpf_cnpj": dados.get("cpf_cnpj", ""),
                    "homologado": bool(dados.get("equipamento_homologado")),
                    "permissao": dados["permissao"],
                    "frequencias": dados.get("frequencias_selecionadas", []),
                    "tipo_equipamento": dados["tipo_equipamento"],
                    "numero_etiqueta": dados["numero_etiqueta"],
                    "observacoes": dados.get("observacoes", ""),
                },
            )
        return (
            "Teste de etiquetagem atualizado com sucesso."
            if result.rowcount
            else "ERRO: registro não encontrado."
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar teste de etiquetagem: {e}", exc_info=True)
        if "testes_etiquetagem_evento_id_numero_etiqueta_key" in str(e):
            return "ERRO: o número da etiqueta já existe neste evento."
        return f"ERRO ao atualizar teste de etiquetagem: {e}"


def excluir_teste_etiquetagem(_client=None, evento_id=None, registro_id=None) -> str:
    """Exclui um teste de etiquetagem pertencente ao evento selecionado."""
    if evento_id is None or registro_id is None:
        return "ERRO: parâmetros insuficientes."
    try:
        with get_engine().begin() as conn:
            result = conn.execute(
                text("""
                    DELETE FROM testes_etiquetagem
                    WHERE id = :id AND evento_id = :ev
                """),
                {"id": int(registro_id), "ev": int(evento_id)},
            )
        return (
            "Teste de etiquetagem excluído com sucesso."
            if result.rowcount
            else "ERRO: registro não encontrado."
        )
    except Exception as e:
        logger.error(f"Erro ao excluir teste de etiquetagem: {e}", exc_info=True)
        return f"ERRO ao excluir teste de etiquetagem: {e}"


# =========================================================================
# Inserir ocorrência (era inserir_emissao_I_W)
# =========================================================================


def inserir_emissao_I_W(
    _client=None,
    evento_id=None,
    dados_formulario: dict = None,
    imagens: list[dict] | None = None,
) -> int | bool:
    """Insere nova ocorrência (emissão) no banco."""
    if evento_id is None or dados_formulario is None:
        return False
    try:
        freq = float(dados_formulario.get("Frequência em MHz", 0))
        conflito = verificar_frequencia_global(evento_id=evento_id, freq_digitada=freq)
        if conflito:
            raise FrequenciaOcupadaError(
                f"A frequência {freq:.3f} MHz já está ocupada: {conflito}."
            )

        dia = dados_formulario.get("Dia")
        if hasattr(dia, "strftime"):
            dia = dia.strftime("%Y-%m-%d")
        hora = dados_formulario.get("Hora")
        if hasattr(hora, "strftime"):
            hora = hora.strftime("%H:%M")

        with get_engine().begin() as conn:
            resultado = conn.execute(
                text("""
                    INSERT INTO ocorrencias
                        (evento_id, local_regiao, fiscal, data, hora,
                         frequencia_mhz, largura_khz, faixa,
                         identificacao, autorizado, ute,
                         processo_sei_ute, observacoes,
                         interferente, situacao, fonte)
                    VALUES
                        (:ev, :local, :fiscal, :data, :hora,
                         :freq, :bw, :faixa,
                         :ident, :autz, :ute,
                         :proc, :obs,
                        :inter, :situ, 'ABORDAGEM')
                    RETURNING id
                """),
                {
                    "ev": int(evento_id),
                    "local": dados_formulario.get("Local/Região", "Abordagem"),
                    "fiscal": dados_formulario.get("Fiscal", ""),
                    "data": dia,
                    "hora": hora,
                    "freq": freq,
                    "bw": float(dados_formulario.get("Largura em kHz", 0)),
                    "faixa": dados_formulario.get("Faixa de Frequência", ""),
                    "ident": dados_formulario.get("Identificação", ""),
                    "autz": dados_formulario.get("Autorizado? (Q)", ""),
                    "ute": bool(dados_formulario.get("UTE?", False)),
                    "proc": dados_formulario.get("Processo SEI ou Ato UTE", ""),
                    "obs": f"{dados_formulario.get('Observações/Detalhes/Contatos', '')} - {dados_formulario.get('Responsável pela emissão', '')}",
                    "inter": dados_formulario.get("Interferente?", ""),
                    "situ": dados_formulario.get("Situação", "Pendente"),
                },
            )
            ocorrencia_id = resultado.scalar_one()
            for imagem in imagens or []:
                conn.execute(
                    text("""
                        INSERT INTO ocorrencia_imagens
                            (ocorrencia_id, nome_arquivo, tipo_mime,
                             tamanho_bytes, conteudo)
                        VALUES (:ocorrencia_id, :nome, :tipo, :tamanho, :conteudo)
                    """),
                    {
                        "ocorrencia_id": ocorrencia_id,
                        "nome": imagem["nome_arquivo"],
                        "tipo": imagem["tipo_mime"],
                        "tamanho": imagem["tamanho_bytes"],
                        "conteudo": imagem["conteudo"],
                    },
                )
        return ocorrencia_id
    except FrequenciaOcupadaError:
        raise
    except Exception as e:
        logger.error(f"Erro inserir_emissao_I_W: {e}", exc_info=True)
        return False


# =========================================================================
# BSR / ERB
# =========================================================================


def inserir_bsr_erb(
    _client=None, evento_id=None, tipo="", regiao="", lat="", lon=""
) -> str:
    """Insere registro de BSR/Jammer ou ERB Fake."""
    if evento_id is None:
        return "ERRO: evento_id não informado."
    try:
        lat_v = float(lat.replace(",", ".")) if lat else None
        lon_v = float(lon.replace(",", ".")) if lon else None
    except (ValueError, AttributeError):
        lat_v = None
        lon_v = None

    try:
        with get_engine().begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO bsr_erb (evento_id, tipo, regiao, latitude, longitude)
                    VALUES (:ev, :tipo, :regiao, :lat, :lon)
                """),
                {
                    "ev": int(evento_id),
                    "tipo": tipo,
                    "regiao": regiao or "",
                    "lat": lat_v,
                    "lon": lon_v,
                },
            )
        return f"'{tipo}' incluído com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


# =========================================================================
# Atualização de campos (edição de ocorrências)
# =========================================================================


def atualizar_campos_na_aba_mae(
    _client=None,
    evento_id=None,
    estacao_raw="",
    id_ocorrencia="",
    novos_valores: dict = None,
    usuario_fiscal: str = USR_FISCAL_ANATEL,
    imagens: list[dict] | None = None,
    imagens_excluir: list[int] | None = None,
) -> str:
    """Atualiza campos de uma ocorrência (qualquer fonte)."""
    if evento_id is None or novos_valores is None:
        return "ERRO: parâmetros insuficientes."
    try:
        with get_engine().begin() as conn:
            updates = []
            params = {"ev": int(evento_id), "id": int(id_ocorrencia)}

            field_map = {
                "Identificação": "identificacao",
                "Autorizado?": "autorizado",
                "UTE?": "ute",
                "Processo SEI UTE": "processo_sei_ute",
                "Ocorrência (observações)": "observacoes",
                "Alguém mais ciente?": "alguem_ciente",
                "Interferente?": "interferente",
                "Situação": "situacao",
            }

            campos = list(field_map.values())
            atual = (
                conn.execute(
                    text(f"""
                    SELECT {', '.join(campos)}
                    FROM ocorrencias
                    WHERE evento_id = :ev AND id = :id
                    FOR UPDATE
                """),
                    params,
                )
                .mappings()
                .first()
            )
            if atual is None:
                return f"ERRO: ID {id_ocorrencia} não encontrado no evento {evento_id}."

            alteracoes = []

            for key, col in field_map.items():
                if key in novos_valores:
                    if key == "UTE?":
                        novo_valor = str(novos_valores[key]).lower() in [
                            "sim",
                            "true",
                            "1",
                            "ok",
                        ]
                    else:
                        novo_valor = str(novos_valores[key])

                    valor_atual = atual[col]
                    comparavel_atual = (
                        bool(valor_atual)
                        if key == "UTE?"
                        else "" if valor_atual is None else str(valor_atual)
                    )
                    if comparavel_atual != novo_valor:
                        updates.append(f"{col} = :v_{col}")
                        params[f"v_{col}"] = novo_valor
                        alteracoes.append((key, valor_atual, novo_valor))

            if not updates and not imagens and not imagens_excluir:
                return "Nada a atualizar."

            if updates:
                sql = f"""
                    UPDATE ocorrencias
                    SET {', '.join(updates)}
                    WHERE evento_id = :ev AND id = :id
                """
                result = conn.execute(text(sql), params)
                if result.rowcount == 0:
                    return f"ERRO: ID {id_ocorrencia} não encontrado no evento {evento_id}."

            imagens_remover = []
            if imagens_excluir:
                imagens_remover = (
                    conn.execute(
                        text("""
                            SELECT id, nome_arquivo
                            FROM ocorrencia_imagens
                            WHERE ocorrencia_id = :ocorrencia_id
                              AND id = ANY(:imagem_ids)
                        """),
                        {
                            "ocorrencia_id": int(id_ocorrencia),
                            "imagem_ids": imagens_excluir,
                        },
                    )
                    .mappings()
                    .all()
                )

            for imagem in imagens or []:
                conn.execute(
                    text("""
                        INSERT INTO ocorrencia_imagens
                            (ocorrencia_id, nome_arquivo, tipo_mime,
                             tamanho_bytes, conteudo)
                        VALUES (:ocorrencia_id, :nome, :tipo, :tamanho, :conteudo)
                    """),
                    {
                        "ocorrencia_id": int(id_ocorrencia),
                        "nome": imagem["nome_arquivo"],
                        "tipo": imagem["tipo_mime"],
                        "tamanho": imagem["tamanho_bytes"],
                        "conteudo": imagem["conteudo"],
                    },
                )

                conn.execute(
                    text("""
                        INSERT INTO auditoria_ocorrencias (
                            ocorrencia_id, evento_id, usuario_fiscal, campo,
                            valor_anterior, valor_novo
                        ) VALUES (
                            :ocorrencia_id, :evento_id, :usuario_fiscal,
                            'Imagem anexada', NULL, :valor_novo
                        )
                    """),
                    {
                        "ocorrencia_id": int(id_ocorrencia),
                        "evento_id": int(evento_id),
                        "usuario_fiscal": usuario_fiscal,
                        "valor_novo": imagem["nome_arquivo"],
                    },
                )

            if imagens_excluir:
                conn.execute(
                    text("""
                        DELETE FROM ocorrencia_imagens
                        WHERE ocorrencia_id = :ocorrencia_id
                          AND id = ANY(:imagem_ids)
                    """),
                    {
                        "ocorrencia_id": int(id_ocorrencia),
                        "imagem_ids": imagens_excluir,
                    },
                )

                for imagem in imagens_remover:
                    conn.execute(
                        text("""
                            INSERT INTO auditoria_ocorrencias (
                                ocorrencia_id, evento_id, usuario_fiscal, campo,
                                valor_anterior, valor_novo
                            ) VALUES (
                                :ocorrencia_id, :evento_id, :usuario_fiscal,
                                'Imagem excluída', :valor_anterior, NULL
                            )
                        """),
                        {
                            "ocorrencia_id": int(id_ocorrencia),
                            "evento_id": int(evento_id),
                            "usuario_fiscal": usuario_fiscal,
                            "valor_anterior": imagem["nome_arquivo"],
                        },
                    )

            for campo, valor_anterior, valor_novo in alteracoes:
                conn.execute(
                    text("""
                        INSERT INTO auditoria_ocorrencias (
                            ocorrencia_id, evento_id, usuario_fiscal, campo,
                            valor_anterior, valor_novo
                        ) VALUES (
                            :ocorrencia_id, :evento_id, :usuario_fiscal, :campo,
                            :valor_anterior, :valor_novo
                        )
                    """),
                    {
                        "ocorrencia_id": int(id_ocorrencia),
                        "evento_id": int(evento_id),
                        "usuario_fiscal": usuario_fiscal,
                        "campo": campo,
                        "valor_anterior": (
                            None if valor_anterior is None else str(valor_anterior)
                        ),
                        "valor_novo": str(valor_novo),
                    },
                )
        return f"Atualizado no banco (ID {id_ocorrencia})."
    except Exception as e:
        return f"ERRO ao atualizar: {e}"


def atualizar_campos_abordagem_por_id(
    _client=None,
    evento_id=None,
    id_h="",
    novos_valores: dict = None,
    usuario_fiscal: str = USR_FISCAL_ANATEL,
    imagens: list[dict] | None = None,
    imagens_excluir: list[int] | None = None,
) -> str:
    """Atualiza campos de uma ocorrência da Abordagem (alias para atualizar_campos_na_aba_mae)."""
    return atualizar_campos_na_aba_mae(
        _client,
        evento_id,
        "Abordagem",
        id_h,
        novos_valores,
        usuario_fiscal,
        imagens,
        imagens_excluir,
    )


def consultar_historico_ocorrencia(evento_id=None, ocorrencia_id=None) -> list[dict]:
    """Retorna o histórico de alterações de uma ocorrência, do mais recente ao mais antigo."""
    if evento_id is None or ocorrencia_id is None:
        return []
    try:
        with get_engine().connect() as conn:
            rows = (
                conn.execute(
                    text("""
                                        SELECT
                                                auditoria.usuario_fiscal,
                                                auditoria.campo,
                                                auditoria.valor_anterior,
                                                auditoria.valor_novo,
                        CASE
                                                        WHEN auditoria.campo = 'Imagem anexada' THEN imagem.id
                        END AS imagem_id,
                        imagem.tipo_mime AS imagem_tipo_mime,
                        imagem.conteudo AS imagem_conteudo,
                                                to_char(auditoria.modificado_em AT TIME ZONE 'America/Sao_Paulo',
                                'DD/MM/YYYY HH24:MI:SS') AS modificado_em
                                        FROM auditoria_ocorrencias auditoria
                                        LEFT JOIN LATERAL (
                                                SELECT oi.id, oi.tipo_mime, oi.conteudo
                                                FROM ocorrencia_imagens oi
                                                WHERE oi.ocorrencia_id = auditoria.ocorrencia_id
                                                    AND oi.nome_arquivo = auditoria.valor_novo
                                                    AND auditoria.campo = 'Imagem anexada'
                                                ORDER BY oi.id
                                                LIMIT 1
                                        ) imagem ON TRUE
                                        WHERE auditoria.evento_id = :evento_id
                                            AND auditoria.ocorrencia_id = :ocorrencia_id
                                        ORDER BY auditoria.modificado_em DESC, auditoria.id DESC
                """),
                    {
                        "evento_id": int(evento_id),
                        "ocorrencia_id": int(ocorrencia_id),
                    },
                )
                .mappings()
                .all()
            )
        historico = []
        for row in rows:
            registro = dict(row)
            conteudo = registro.pop("imagem_conteudo", None)
            tipo_mime = registro.pop("imagem_tipo_mime", None)
            registro["imagem_url"] = (
                f"data:{tipo_mime};base64,{base64.b64encode(bytes(conteudo)).decode('ascii')}"
                if conteudo and tipo_mime
                else None
            )
            historico.append(registro)
        return historico
    except Exception as e:
        logger.error("Erro ao consultar histórico da ocorrência: %s", e, exc_info=True)
        return []


# =========================================================================
# Busca textual
# =========================================================================


def _buscar_por_texto_livre(
    _client=None, evento_id=None, termos: str = "", abas: list = None
) -> pd.DataFrame:
    """Busca textual em ocorrências usando unaccent + ILIKE."""
    if evento_id is None or not termos or len(termos.strip()) < 3:
        return pd.DataFrame()
    try:
        termo_clean = _escape_like(termos.strip())
        sql = text("""
            SELECT
                o.id::text AS "ID",
                COALESCE(e.nome, o.local_regiao) AS "Local",
                o.fiscal AS "Fiscal",
                o.data::text AS "Data",
                o.hora::text AS "HH:mm",
                o.frequencia_mhz::text AS "Frequência (MHz)",
                o.largura_khz::text AS "Largura (kHz)",
                o.faixa AS "Faixa de Frequência Envolvida",
                o.identificacao AS "Identificação",
                o.autorizado AS "Autorizado?",
                CASE WHEN o.ute THEN 'Sim' ELSE 'Não' END AS "UTE?",
                o.processo_sei_ute AS "Processo SEI UTE",
                o.observacoes AS "Ocorrência (observações)",
                o.alguem_ciente AS "Alguém mais ciente?",
                o.interferente AS "Interferente?",
                o.situacao AS "Situação",
                COALESCE(e.nome, o.local_regiao, '') AS "Aba/Origem",
                'BUSCA' AS "Fonte"
            FROM ocorrencias o
            LEFT JOIN estacoes e ON e.id = o.estacao_id
            WHERE o.evento_id = :ev
              AND unaccent(lower(
                    COALESCE(o.local_regiao,'') || ' ' ||
                    COALESCE(o.fiscal,'') || ' ' ||
                    COALESCE(o.identificacao,'') || ' ' ||
                    COALESCE(o.observacoes,'') || ' ' ||
                    COALESCE(o.faixa,'') || ' ' ||
                    COALESCE(o.processo_sei_ute,'')
              )) LIKE unaccent(lower(:q))
            ORDER BY o.data DESC
            LIMIT 200
        """)
        df = pd.read_sql(
            sql,
            get_engine(),
            params={"ev": int(evento_id), "q": f"%{termo_clean}%"},
        )
        return df
    except Exception as e:
        logger.error(f"Erro _buscar_por_texto_livre: {e}", exc_info=True)
        return pd.DataFrame()
