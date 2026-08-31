"""
Serviço de dados PostgreSQL — substitui google_sheets.py mantendo o mesmo contrato.

Cada função tem o MESMO nome e assinatura (retornos: pd.DataFrame, str, bool, dict)
que a equivalente em google_sheets.py, para que routers/views não precisem ser alterados.

O parâmetro _client é ignorado (mantido apenas para compatibilidade de assinatura).
O parâmetro spreadsheet_id é tratado como evento_id (inteiro).
"""

import base64
import logging
import re
from datetime import datetime, timezone
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


def _nome_imagem_emissao(
    ocorrencia_id: int,
    data_emissao,
    hora_emissao,
    nome_original: str,
    data_foto=None,
    hora_foto=None,
) -> str:
    """Gera um nome usando a emissão e o momento original registrado na foto."""
    extensao = ""
    if "." in nome_original:
        extensao = "." + nome_original.rsplit(".", 1)[-1].lower()
    data_base = data_foto or data_emissao
    hora_base = hora_foto or hora_emissao
    data_texto = (
        data_base.strftime("%Y%m%d")
        if hasattr(data_base, "strftime")
        else str(data_base).replace("-", "")
    )
    hora_texto = (
        hora_base.strftime("%H%M")
        if hasattr(hora_base, "strftime")
        else str(hora_base).replace(":", "")[:4]
    )
    return f"ID_{ocorrencia_id}_{data_texto}_{hora_texto}{extensao}"


def _nome_imagem_bsr_erb(
    registro_id: int,
    tipo: str,
    nome_evento: str,
    instante: datetime,
    nome_original: str,
    indice: int,
) -> str:
    """Gera nome padronizado para fotos de ocorrências especiais."""
    extensao = ""
    if "." in nome_original:
        extensao = "." + nome_original.rsplit(".", 1)[-1].lower()

    def limpar(valor: str) -> str:
        valor = re.sub(r"[^A-Za-z0-9]+", "_", str(valor or "")).strip("_")
        return valor or "SEM_VALOR"

    instante_local = instante.astimezone(timezone.utc)
    return (
        f"{limpar(nome_evento)}_{limpar(tipo)}_ID_{registro_id}_"
        f"{instante_local:%Y%m%d}_{instante_local:%H%M%S}_"
        f"{indice:02d}{extensao}"
    )


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


def carregar_imagens_ocorrencias(
    evento_id=None, ocorrencia_ids=None
) -> dict[int, list[dict]]:
    """Retorna as fotos agrupadas por ocorrência, validando o evento."""
    ids = [int(valor) for valor in (ocorrencia_ids or []) if str(valor).isdigit()]
    if evento_id is None or not ids:
        return {}
    with get_engine().connect() as conn:
        registros = (
            conn.execute(
                text("""
                SELECT oi.ocorrencia_id, oi.id, oi.nome_arquivo,
                       oi.tipo_mime, oi.conteudo
                FROM ocorrencia_imagens oi
                JOIN ocorrencias o ON o.id = oi.ocorrencia_id
                WHERE o.evento_id = :evento_id
                  AND oi.ocorrencia_id = ANY(:ocorrencia_ids)
                ORDER BY oi.ocorrencia_id, oi.id
            """),
                {"evento_id": int(evento_id), "ocorrencia_ids": ids},
            )
            .mappings()
            .all()
        )
    imagens = {}
    for registro in registros:
        imagens.setdefault(registro["ocorrencia_id"], []).append(
            {
                "nome_arquivo": registro["nome_arquivo"],
                "url": (
                    f"data:{registro['tipo_mime']};base64,"
                    f"{base64.b64encode(bytes(registro['conteudo'])).decode('ascii')}"
                ),
            }
        )
    return imagens


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


def _nome_imagem_teste_etiquetagem(
    teste_id: int, numero_etiqueta: str, imagem_id: int, nome_original: str
) -> str:
    """Gera um nome numerado e rastreável para a foto do equipamento."""
    extensao = ""
    if "." in nome_original:
        extensao = "." + nome_original.rsplit(".", 1)[-1].lower()
    etiqueta = re.sub(r"[^A-Za-z0-9_-]+", "_", str(numero_etiqueta).strip())
    if re.match(r"^ETQ[_-]", etiqueta, re.IGNORECASE):
        etiqueta = re.sub(r"^(?:ETQ[_-])+", "ETQ-", etiqueta, flags=re.IGNORECASE)
    else:
        etiqueta = f"ETQ_{etiqueta}"
    return f"{etiqueta}_ID_{teste_id}_FOTO_{imagem_id:02d}{extensao}"


def carregar_imagens_teste_etiquetagem(evento_id=None, teste_id=None) -> list[dict]:
    """Retorna as fotos de um equipamento como data URLs para o formulário."""
    with get_engine().connect() as conn:
        registros = conn.execute(
            text("""
                SELECT imagem.id, imagem.nome_arquivo, imagem.tipo_mime,
                       imagem.conteudo
                FROM teste_etiquetagem_imagens imagem
                JOIN testes_etiquetagem teste
                  ON teste.id = imagem.teste_etiquetagem_id
                WHERE teste.evento_id = :evento_id
                  AND teste.id = :teste_id
                ORDER BY imagem.id
            """),
            {"evento_id": int(evento_id), "teste_id": int(teste_id)},
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


def criar_evento(
    nome: str,
    latitude: float | None = None,
    longitude: float | None = None,
    fuso_horario: str = "America/Sao_Paulo",
    cidade: str | None = None,
    uf: str | None = None,
    acao_fiscalizacao: str | None = None,
    processo_sei: str | None = None,
    periodo_inicio: str | None = None,
    periodo_fim: str | None = None,
    teste_etiquetagem: bool = True,
    unidades_executantes: list[str] | None = None,
    observacoes: str | None = None,
    estacoes: list[str | dict] | None = None,
    fiscais: list[str] | None = None,
    coordenadores: list[str] | None = None,
) -> int:
    """Cria um evento, suas estações e retorna o identificador do evento."""
    with get_engine().begin() as conn:
        evento_id = conn.execute(
            text("""
                INSERT INTO eventos
                    (nome, latitude, longitude, fuso_horario, cidade, uf,
                     acao_fiscalizacao, processo_sei,
                     periodo_inicio, periodo_fim, teste_etiquetagem, observacoes)
                VALUES
                    (:nome, :latitude, :longitude, :fuso_horario, :cidade, :uf,
                    :acao_fiscalizacao, :processo_sei,
                    :periodo_inicio, :periodo_fim, :teste_etiquetagem, :observacoes)
                RETURNING id
            """),
            {
                "nome": nome,
                "latitude": latitude,
                "longitude": longitude,
                "fuso_horario": fuso_horario,
                "cidade": cidade,
                "uf": uf,
                "acao_fiscalizacao": acao_fiscalizacao,
                "processo_sei": processo_sei,
                "periodo_inicio": periodo_inicio,
                "periodo_fim": periodo_fim,
                "teste_etiquetagem": teste_etiquetagem,
                "observacoes": observacoes,
            },
        ).scalar_one()
        nomes_inseridos = set()
        for estacao in estacoes or []:
            dados = {"nome": estacao} if isinstance(estacao, str) else estacao
            nome_estacao = str(dados.get("nome", "")).strip()
            if not nome_estacao or nome_estacao in nomes_inseridos:
                continue
            nomes_inseridos.add(nome_estacao)
            conn.execute(
                text("""
                    INSERT INTO estacoes
                        (evento_id, nome, modelo_equipamento, local)
                    VALUES
                        (:evento_id, :nome, :modelo, :local)
                """),
                {
                    "evento_id": evento_id,
                    "nome": nome_estacao,
                    "modelo": dados.get("modelo"),
                    "local": dados.get("local"),
                },
            )
        for sigla in unidades_executantes or []:
            conn.execute(
                text("""
                    INSERT INTO eventos_unidades_executantes (evento_id, unidade_sigla)
                    VALUES (:evento_id, :unidade_sigla)
                    ON CONFLICT DO NOTHING
                """),
                {"evento_id": evento_id, "unidade_sigla": sigla},
            )
        for fiscal_id in fiscais or []:
            conn.execute(
                text("""
                INSERT INTO eventos_fiscais (evento_id, fiscal_id)
                VALUES (:evento_id, :fiscal_id)
                ON CONFLICT DO NOTHING
                """),
                {"evento_id": evento_id, "fiscal_id": int(fiscal_id)},
            )
        for fiscal_id in coordenadores or []:
            conn.execute(
                text("""
                INSERT INTO eventos_coordenadores (evento_id, fiscal_id)
                SELECT :evento_id, ef.fiscal_id
                FROM eventos_fiscais ef
                JOIN fiscais f ON f.id = ef.fiscal_id
                WHERE ef.evento_id = :evento_id
                  AND ef.fiscal_id = :fiscal_id
                  AND f.funcao_evento = 'Coordenação'
                ON CONFLICT DO NOTHING
                """),
                {"evento_id": evento_id, "fiscal_id": int(fiscal_id)},
            )
        return evento_id


def listar_unidades_executantes() -> list[dict]:
    """Retorna as GRs e UOs disponíveis para vincular a eventos."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("""
            SELECT sigla, nome
            FROM unidades_executantes
            ORDER BY CASE WHEN sigla LIKE 'GR%' THEN 0 ELSE 1 END, sigla
        """)).mappings().all()
    return [dict(row) for row in rows]


def listar_fiscais() -> list[dict]:
    """Retorna a lista global de fiscais cadastrados."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("""
            SELECT f.id, f.nome, f.local_anatel, u.nome AS local_anatel_nome,
                   f.funcao_evento
            FROM fiscais f
            JOIN unidades_executantes u ON u.sigla = f.local_anatel
            ORDER BY f.nome, f.local_anatel, f.funcao_evento
        """)).mappings().all()
    return [dict(row) for row in rows]


def criar_fiscal(nome: str, local_anatel: str, funcao_evento: str) -> int:
    """Cadastra um fiscal na lista global e retorna seu identificador."""
    with get_engine().begin() as conn:
        return conn.execute(
            text("""
            INSERT INTO fiscais (nome, local_anatel, funcao_evento)
            VALUES (:nome, :local_anatel, :funcao_evento)
            RETURNING id
        """),
            {
                "nome": nome,
                "local_anatel": local_anatel,
                "funcao_evento": funcao_evento,
            },
        ).scalar_one()


def excluir_fiscal(fiscal_id: int) -> None:
    """Exclui um fiscal global e seus vínculos com eventos."""
    with get_engine().begin() as conn:
        conn.execute(
            text("DELETE FROM fiscais WHERE id = :fiscal_id"),
            {
                "fiscal_id": int(fiscal_id),
            },
        )


def listar_fiscais_evento(evento_id: int) -> list[int]:
    """Retorna os IDs dos fiscais participantes do evento."""
    with get_engine().connect() as conn:
        return list(
            conn.execute(
                text("""
            SELECT fiscal_id
            FROM eventos_fiscais
            WHERE evento_id = :evento_id
            ORDER BY fiscal_id
        """),
                {"evento_id": int(evento_id)},
            ).scalars()
        )


def listar_coordenadores_evento(evento_id: int) -> list[int]:
    """Retorna os IDs dos coordenadores vinculados ao evento."""
    with get_engine().connect() as conn:
        vinculados = list(
            conn.execute(
                text("""
                SELECT fiscal_id
                FROM eventos_coordenadores
                WHERE evento_id = :evento_id
                ORDER BY fiscal_id
                """),
                {"evento_id": int(evento_id)},
            ).scalars()
        )
        return vinculados


def listar_tickets_evento(evento_id: int) -> list[dict]:
    """Lista tickets de coordenação com uma ou mais emissões vinculadas."""
    with get_engine().connect() as conn:
        rows = (
            conn.execute(
                text("""
                  SELECT t.id, t.evento_id, t.status, t.prioridade, t.observacoes,
                      to_char(t.criado_em AT TIME ZONE 'America/Sao_Paulo',
                          'DD/MM/YYYY HH24:MI') AS criado_em,
                      to_char(t.atualizado_em AT TIME ZONE 'America/Sao_Paulo',
                          'DD/MM/YYYY HH24:MI') AS atualizado_em,
                      string_agg(DISTINCT o.id::text, ', ' ORDER BY o.id::text) AS ocorrencia_ids,
                      string_agg(DISTINCT COALESCE(o.identificacao, 'Emissão #' || o.id::text), ', ' ORDER BY COALESCE(o.identificacao, 'Emissão #' || o.id::text)) AS identificacao,
                      string_agg(DISTINCT COALESCE(o.local_regiao, 'Não informado'), ', ' ORDER BY COALESCE(o.local_regiao, 'Não informado')) AS local_regiao,
                      string_agg(DISTINCT o.frequencia_mhz::text, ', ' ORDER BY o.frequencia_mhz::text) AS frequencia_mhz,
                      string_agg(DISTINCT o.largura_khz::text, ', ' ORDER BY o.largura_khz::text) AS largura_khz,
                      array_remove(array_agg(DISTINCT tf.fiscal_id), NULL) AS fiscal_ids,
                       COALESCE(
                           string_agg(DISTINCT f.nome, ', ' ORDER BY f.nome),
                           ''
                       ) AS fiscais
                FROM tickets t
                LEFT JOIN ticket_ocorrencias toco ON toco.ticket_id = t.id
                LEFT JOIN ocorrencias o ON o.id = toco.ocorrencia_id
                LEFT JOIN ticket_fiscais tf ON tf.ticket_id = t.id
                LEFT JOIN fiscais f ON f.id = tf.fiscal_id
                WHERE t.evento_id = :evento_id
                GROUP BY t.id, t.evento_id, t.status, t.prioridade, t.observacoes,
                         t.criado_em, t.atualizado_em
                ORDER BY
                    CASE t.status
                        WHEN 'pendente' THEN 0
                        WHEN 'concluido_pelos_fiscais' THEN 1
                        ELSE 2
                    END,
                    CASE t.prioridade
                        WHEN 'alta' THEN 0
                        WHEN 'normal' THEN 1
                        ELSE 2
                    END,
                    t.id
            """),
                {"evento_id": int(evento_id)},
            )
            .mappings()
            .all()
        )
    tickets = []
    for row in rows:
        ticket = dict(row)
        ticket["fiscal_ids"] = [
            int(fiscal_id) for fiscal_id in (ticket.get("fiscal_ids") or [])
        ]
        tickets.append(ticket)
    return tickets


def listar_emissoes_evento(evento_id: int) -> list[dict]:
    """Lista somente as emissões com situação pendente para criação de tickets."""
    with get_engine().connect() as conn:
        rows = (
            conn.execute(
                text("""
                  SELECT o.id, o.identificacao,
                      NULLIF(concat_ws(', ', o.fiscal, participantes.nomes), '') AS fiscal,
                      o.local_regiao, o.data,
                       o.hora, o.frequencia_mhz, o.largura_khz, o.situacao,
                       vinculacao.ticket_id AS ticket_id_vinculado,
                       (vinculacao.ticket_id IS NOT NULL) AS ja_possui_ticket
                FROM ocorrencias o
                  LEFT JOIN LATERAL (
                      SELECT string_agg(f.nome, ', ' ORDER BY f.nome) AS nomes
                      FROM ocorrencia_fiscais ocorrencia_fiscal
                      JOIN fiscais f ON f.id = ocorrencia_fiscal.fiscal_id
                      WHERE ocorrencia_fiscal.ocorrencia_id = o.id
                  ) participantes ON true
                LEFT JOIN LATERAL (
                    SELECT t.id AS ticket_id
                    FROM ticket_ocorrencias toco
                    JOIN tickets t ON t.id = toco.ticket_id
                    WHERE toco.ocorrencia_id = o.id
                      AND t.evento_id = :evento_id
                    ORDER BY t.id DESC
                    LIMIT 1
                ) vinculacao ON true
                WHERE o.evento_id = :evento_id
                  AND lower(trim(o.situacao)) = 'pendente'
                ORDER BY data DESC NULLS LAST, hora DESC NULLS LAST, id DESC
            """),
                {"evento_id": int(evento_id)},
            )
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


def obter_emissao_evento(evento_id: int, ocorrencia_id: int) -> dict | None:
    """Retorna os detalhes de uma emissão específica do evento."""
    with get_engine().connect() as conn:
        registro = (
            conn.execute(
                text("""
                SELECT o.id, o.identificacao, o.local_regiao, o.fiscal,
                       o.data, o.hora, o.frequencia_mhz, o.largura_khz,
                       o.faixa, o.autorizado, o.ute, o.processo_sei_ute,
                       o.observacoes, o.alguem_ciente, o.interferente,
                       o.situacao, COALESCE(e.nome, '') AS estacao_nome
                FROM ocorrencias o
                LEFT JOIN estacoes e ON e.id = o.estacao_id
                WHERE o.evento_id = :evento_id AND o.id = :ocorrencia_id
            """),
                {
                    "evento_id": int(evento_id),
                    "ocorrencia_id": int(ocorrencia_id),
                },
            )
            .mappings()
            .first()
        )
    return dict(registro) if registro else None


def salvar_ticket_evento(
    evento_id: int,
    ocorrencia_ids: list[int],
    prioridade: str = "normal",
    observacoes: str | None = None,
    fiscal_ids: list[int] | None = None,
) -> int:
    """Cria um ticket vinculado a uma ou mais emissões pendentes."""
    with get_engine().begin() as conn:
        ids = list(dict.fromkeys(int(item) for item in ocorrencia_ids))
        if not ids:
            raise ValueError("Selecione ao menos uma emissão para abrir o ticket.")

        emissao_count = conn.execute(
            text("""
                SELECT count(*)
                FROM ocorrencias
                WHERE evento_id = :evento_id
                  AND id = ANY(CAST(:ocorrencia_ids AS BIGINT[]))
                  AND lower(trim(situacao)) = 'pendente'
            """),
            {"evento_id": int(evento_id), "ocorrencia_ids": ids},
        ).scalar_one()
        if int(emissao_count) != len(ids):
            raise ValueError(
                "Somente emissões pendentes do evento podem receber tickets de fiscalização."
            )

        emissao_ja_vinculada = conn.execute(
            text("""
                SELECT count(*)
                FROM ocorrencias o
                WHERE o.evento_id = :evento_id
                  AND o.id = ANY(CAST(:ocorrencia_ids AS BIGINT[]))
                  AND EXISTS (
                      SELECT 1
                      FROM ticket_ocorrencias toco
                      JOIN tickets t ON t.id = toco.ticket_id
                      WHERE toco.ocorrencia_id = o.id
                        AND t.evento_id = :evento_id
                  )
            """),
            {"evento_id": int(evento_id), "ocorrencia_ids": ids},
        ).scalar_one()
        if int(emissao_ja_vinculada) > 0:
            raise ValueError(
                "Uma ou mais emissões selecionadas já estão vinculadas a ticket."
            )

        ticket_id = conn.execute(
            text("""
                INSERT INTO tickets (evento_id, prioridade, observacoes)
                VALUES (:evento_id, :prioridade, :observacoes)
                RETURNING id
            """),
            {
                "evento_id": int(evento_id),
                "prioridade": prioridade,
                "observacoes": observacoes,
            },
        ).scalar_one()

        conn.execute(
            text("""
                INSERT INTO ticket_ocorrencias (ticket_id, ocorrencia_id)
                SELECT :ticket_id, unnest(CAST(:ocorrencia_ids AS BIGINT[]))
            """),
            {"ticket_id": int(ticket_id), "ocorrencia_ids": ids},
        )

        conn.execute(
            text("DELETE FROM ticket_fiscais WHERE ticket_id = :ticket_id"),
            {"ticket_id": int(ticket_id)},
        )
        for fiscal_id in list(dict.fromkeys(int(item) for item in (fiscal_ids or []))):
            conn.execute(
                text("""
                    INSERT INTO ticket_fiscais (ticket_id, fiscal_id)
                    VALUES (:ticket_id, :fiscal_id)
                    ON CONFLICT DO NOTHING
                """),
                {"ticket_id": int(ticket_id), "fiscal_id": int(fiscal_id)},
            )
        return int(ticket_id)


def salvar_escala_evento(
    evento_id: int,
    fiscal_id: int,
    data_trabalho: str,
    turno_inicio: str | None = None,
    turno_fim: str | None = None,
    observacoes: str | None = None,
) -> None:
    """Salva a escala de trabalho de um fiscal para um evento."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                INSERT INTO escalas_trabalho (
                    evento_id, fiscal_id, data_trabalho,
                    turno_inicio, turno_fim, observacoes
                )
                VALUES (
                    :evento_id, :fiscal_id, :data_trabalho,
                    :turno_inicio, :turno_fim, :observacoes
                )
            """),
            {
                "evento_id": int(evento_id),
                "fiscal_id": int(fiscal_id),
                "data_trabalho": data_trabalho,
                "turno_inicio": turno_inicio,
                "turno_fim": turno_fim,
                "observacoes": observacoes,
            },
        )


def listar_escalas_evento(evento_id: int) -> list[dict]:
    """Lista a escala de trabalho por evento."""
    with get_engine().connect() as conn:
        rows = (
            conn.execute(
                text("""
                SELECT e.id, e.evento_id, e.data_trabalho, e.turno_inicio,
                       e.turno_fim, e.observacoes, f.nome AS fiscal_nome
                FROM escalas_trabalho e
                JOIN fiscais f ON f.id = e.fiscal_id
                WHERE e.evento_id = :evento_id
                ORDER BY e.data_trabalho, f.nome
            """),
                {"evento_id": int(evento_id)},
            )
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


def atualizar_ticket_evento(
    ticket_id: int,
    evento_id: int,
    status: str,
    fiscal_ids: list[int] | None = None,
    observacoes: str | None = None,
    prioridade: str | None = None,
    usuario_fiscal: str = USR_FISCAL_ANATEL,
) -> None:
    """Atualiza o ticket e conclui suas emissões no encerramento pela Coordenação."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                UPDATE tickets
                SET status = :status,
                    prioridade = COALESCE(:prioridade, prioridade),
                    observacoes = :observacoes,
                    atualizado_em = now()
                WHERE id = :ticket_id AND evento_id = :evento_id
            """),
            {
                "ticket_id": int(ticket_id),
                "evento_id": int(evento_id),
                "status": status,
                "prioridade": prioridade,
                "observacoes": observacoes,
            },
        )

        if status == "concluido":
            emissões_concluidas = (
                conn.execute(
                    text("""
                    WITH emissões_do_ticket AS (
                        SELECT o.id, o.situacao AS valor_anterior
                        FROM ocorrencias o
                        JOIN ticket_ocorrencias toco ON toco.ocorrencia_id = o.id
                        WHERE toco.ticket_id = :ticket_id
                          AND o.evento_id = :evento_id
                    )
                    UPDATE ocorrencias o
                    SET situacao = 'Concluído'
                    FROM emissões_do_ticket emissao
                    WHERE o.id = emissao.id
                      AND o.situacao IS DISTINCT FROM 'Concluído'
                    RETURNING o.id, emissao.valor_anterior
                """),
                    {
                        "ticket_id": int(ticket_id),
                        "evento_id": int(evento_id),
                    },
                )
                .mappings()
                .all()
            )
            for emissao in emissões_concluidas:
                conn.execute(
                    text("""
                        INSERT INTO auditoria_ocorrencias (
                            ocorrencia_id, evento_id, usuario_fiscal, campo,
                            valor_anterior, valor_novo
                        ) VALUES (
                            :ocorrencia_id, :evento_id, :usuario_fiscal,
                            'Situação', :valor_anterior, 'Concluído'
                        )
                    """),
                    {
                        "ocorrencia_id": int(emissao["id"]),
                        "evento_id": int(evento_id),
                        "usuario_fiscal": usuario_fiscal,
                        "valor_anterior": emissao["valor_anterior"],
                    },
                )

        if fiscal_ids is not None:
            conn.execute(
                text("DELETE FROM ticket_fiscais WHERE ticket_id = :ticket_id"),
                {"ticket_id": int(ticket_id)},
            )
            for fiscal_id in list(
                dict.fromkeys(int(item) for item in (fiscal_ids or []))
            ):
                conn.execute(
                    text("""
                        INSERT INTO ticket_fiscais (ticket_id, fiscal_id)
                        VALUES (:ticket_id, :fiscal_id)
                        ON CONFLICT DO NOTHING
                    """),
                    {"ticket_id": int(ticket_id), "fiscal_id": int(fiscal_id)},
                )


def cancelar_ticket_evento(ticket_id: int, evento_id: int) -> None:
    """Cancela o ticket e libera suas emissões para novos vínculos."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                UPDATE tickets
                SET status = 'concluido',
                    atualizado_em = now()
                WHERE id = :ticket_id AND evento_id = :evento_id
            """),
            {
                "ticket_id": int(ticket_id),
                "evento_id": int(evento_id),
            },
        )
        conn.execute(
            text("DELETE FROM ticket_ocorrencias WHERE ticket_id = :ticket_id"),
            {"ticket_id": int(ticket_id)},
        )


def atualizar_fiscais_evento(evento_id: int, fiscais: list[str]) -> None:
    """Substitui os fiscais participantes do evento."""
    with get_engine().begin() as conn:
        conn.execute(
            text("DELETE FROM eventos_fiscais WHERE evento_id = :evento_id"),
            {"evento_id": int(evento_id)},
        )
        for fiscal_id in fiscais:
            conn.execute(
                text("""
                INSERT INTO eventos_fiscais (evento_id, fiscal_id)
                VALUES (:evento_id, :fiscal_id)
                ON CONFLICT DO NOTHING
            """),
                {"evento_id": int(evento_id), "fiscal_id": int(fiscal_id)},
            )


def listar_unidades_evento(evento_id: int) -> list[str]:
    """Retorna as siglas das unidades executantes vinculadas ao evento."""
    with get_engine().connect() as conn:
        return list(
            conn.execute(
                text("""
            SELECT unidade_sigla
            FROM eventos_unidades_executantes
            WHERE evento_id = :evento_id
            ORDER BY unidade_sigla
        """),
                {"evento_id": int(evento_id)},
            ).scalars()
        )


def atualizar_unidades_evento(evento_id: int, unidades: list[str]) -> None:
    """Substitui as unidades executantes vinculadas ao evento."""
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "DELETE FROM eventos_unidades_executantes WHERE evento_id = :evento_id"
            ),
            {"evento_id": int(evento_id)},
        )
        for sigla in unidades:
            conn.execute(
                text("""
                INSERT INTO eventos_unidades_executantes (evento_id, unidade_sigla)
                VALUES (:evento_id, :unidade_sigla)
            """),
                {"evento_id": int(evento_id), "unidade_sigla": sigla},
            )


def listar_eventos_detalhes() -> list[dict]:
    """Retorna os eventos cadastrados com seus dados e vínculos resumidos."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("""
                  SELECT e.id, e.nome, e.latitude, e.longitude, e.fuso_horario, e.cidade, e.uf,
                      acao_fiscalizacao, processo_sei,
                      (
                          SELECT string_agg(f.nome, ', ' ORDER BY f.nome)
                          FROM eventos_coordenadores ec
                          JOIN fiscais f ON f.id = ec.fiscal_id
                          WHERE ec.evento_id = e.id
                      ) AS coordenador_responsavel,
                      periodo_inicio, periodo_fim, teste_etiquetagem, observacoes,
                      COALESCE((
                          SELECT string_agg(eu.unidade_sigla, ', ' ORDER BY eu.unidade_sigla)
                          FROM eventos_unidades_executantes eu
                          WHERE eu.evento_id = e.id
                      ), '') AS unidades_executantes,
                      COALESCE((
                          SELECT string_agg(est.nome, ', ' ORDER BY est.nome)
                          FROM estacoes est
                          WHERE est.evento_id = e.id
                      ), '') AS estacoes,
                      COALESCE((
                          SELECT string_agg(
                              f.nome || ' (' || f.local_anatel || ' - ' || f.funcao_evento || ')',
                              ', ' ORDER BY f.nome
                          )
                          FROM eventos_fiscais ef
                          JOIN fiscais f ON f.id = ef.fiscal_id
                          WHERE ef.evento_id = e.id
                      ), '') AS fiscais_participantes
                  FROM eventos e
                ORDER BY e.nome
            """)).mappings().all()
    return [dict(row) for row in rows]


def listar_municipios() -> list[dict]:
    """Retorna os municípios cadastrados, agrupáveis por UF no formulário."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("""
                SELECT codigo_ibge, nome, uf
                FROM municipios
                ORDER BY uf, nome
            """)).mappings().all()
    return [dict(row) for row in rows]


def listar_ufs_municipios() -> list[str]:
    """Retorna as UFs presentes na tabela oficial de municípios."""
    with get_engine().connect() as conn:
        return list(
            conn.execute(text("SELECT DISTINCT uf FROM municipios ORDER BY uf"))
            .scalars()
            .all()
        )


def cidade_pertence_uf(cidade: str, uf: str) -> bool:
    """Verifica no banco se a cidade pertence à UF selecionada."""
    with get_engine().connect() as conn:
        return bool(
            conn.execute(
                text("""
                    SELECT 1 FROM municipios
                    WHERE lower(nome) = lower(:cidade) AND uf = :uf
                    LIMIT 1
                """),
                {"cidade": cidade, "uf": uf},
            ).first()
        )


def obter_evento(evento_id: int) -> dict | None:
    """Retorna um evento pelo identificador."""
    with get_engine().connect() as conn:
        row = (
            conn.execute(
                text("""
                  SELECT e.id, e.nome, e.latitude, e.longitude, e.fuso_horario, e.cidade, e.uf,
                      e.acao_fiscalizacao, e.processo_sei,
                      (
                          SELECT string_agg(f.nome, ', ' ORDER BY f.nome)
                          FROM eventos_coordenadores ec
                          JOIN fiscais f ON f.id = ec.fiscal_id
                          WHERE ec.evento_id = e.id
                      ) AS coordenador_responsavel,
                      periodo_inicio, periodo_fim, teste_etiquetagem, observacoes
                FROM eventos e
                WHERE e.id = :id
            """),
                {"id": int(evento_id)},
            )
            .mappings()
            .first()
        )
    return dict(row) if row else None


def registrar_auditoria_evento(
    evento_id: int,
    valores_anteriores: dict,
    valores_novos: dict,
    usuario_fiscal: str = USR_FISCAL_ANATEL,
) -> None:
    """Registra as diferenças de todos os campos editáveis de um evento."""
    campos = (
        ("nome", "Nome do evento"),
        ("latitude", "Latitude"),
        ("longitude", "Longitude"),
        ("fuso_horario", "Fuso horário"),
        ("cidade", "Cidade"),
        ("uf", "UF"),
        ("acao_fiscalizacao", "Ação de fiscalização"),
        ("processo_sei", "Processo SEI"),
        ("coordenadores", "Coordenadores responsáveis"),
        ("fiscais_participantes", "Fiscais participantes"),
        ("unidades_executantes", "Unidades executantes"),
        ("periodo_inicio", "Período inicial"),
        ("periodo_fim", "Período final"),
        ("teste_etiquetagem", "Teste de etiquetagem neste evento"),
        ("observacoes", "Observações"),
    )

    def normalizar(valor):
        if valor is None or valor == "":
            return None
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        return str(valor)

    alteracoes = []
    for campo, rotulo in campos:
        anterior = normalizar(valores_anteriores.get(campo))
        novo = normalizar(valores_novos.get(campo))
        if anterior != novo:
            alteracoes.append(
                {
                    "evento_id": int(evento_id),
                    "usuario_fiscal": usuario_fiscal,
                    "campo": rotulo,
                    "valor_anterior": anterior,
                    "valor_novo": novo,
                }
            )
    if not alteracoes:
        return
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                INSERT INTO auditoria_eventos
                    (evento_id, usuario_fiscal, campo, valor_anterior, valor_novo)
                VALUES
                    (:evento_id, :usuario_fiscal, :campo, :valor_anterior, :valor_novo)
            """),
            alteracoes,
        )


def registrar_login_evento(evento_id: int, usuario_fiscal: str) -> None:
    """Registra o acesso de um usuário ao evento na auditoria do sistema."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                INSERT INTO auditoria_eventos
                    (evento_id, usuario_fiscal, campo, valor_anterior, valor_novo)
                VALUES
                    (:evento_id, :usuario_fiscal, 'Login no sistema', NULL,
                     'Acesso realizado no evento')
            """),
            {
                "evento_id": int(evento_id),
                "usuario_fiscal": usuario_fiscal,
            },
        )


def registrar_auditoria_coordenacao(
    evento_id: int,
    usuario_fiscal: str,
    acao: str,
    valor_anterior: str | None,
    valor_novo: str | None,
) -> None:
    """Registra uma ação da coordenação na auditoria consolidada do evento."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                INSERT INTO auditoria_eventos
                    (evento_id, usuario_fiscal, campo, valor_anterior, valor_novo)
                VALUES
                    (:evento_id, :usuario_fiscal, :campo, :valor_anterior, :valor_novo)
            """),
            {
                "evento_id": int(evento_id),
                "usuario_fiscal": usuario_fiscal,
                "campo": f"Coordenação - {acao}",
                "valor_anterior": valor_anterior,
                "valor_novo": valor_novo,
            },
        )


def obter_snapshot_auditoria_evento(evento_id: int) -> dict:
    """Retorna os campos do evento e seus vínculos para comparação de auditoria."""
    evento = obter_evento(int(evento_id)) or {}
    fiscais = {fiscal["id"]: fiscal for fiscal in listar_fiscais()}
    participantes = listar_fiscais_evento(int(evento_id))
    coordenadores = listar_coordenadores_evento(int(evento_id))
    evento["fiscais_participantes"] = ", ".join(
        fiscais[fiscal_id]["nome"]
        for fiscal_id in participantes
        if fiscal_id in fiscais
    )
    evento["coordenadores"] = ", ".join(
        fiscais[fiscal_id]["nome"]
        for fiscal_id in coordenadores
        if fiscal_id in fiscais
    )
    evento["unidades_executantes"] = ", ".join(listar_unidades_evento(int(evento_id)))
    return evento


def listar_estacoes_evento(evento_id: int) -> list[dict]:
    """Lista as estações vinculadas a um evento."""
    with get_engine().connect() as conn:
        rows = (
            conn.execute(
                text("""
                  SELECT id, nome, modelo_equipamento, local,
                      latitude, longitude
                FROM estacoes
                WHERE evento_id = :evento_id
                ORDER BY nome
            """),
                {"evento_id": int(evento_id)},
            )
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


def criar_estacao(
    evento_id: int,
    nome: str,
    modelo: str | None = None,
    local: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> int:
    """Adiciona uma estação a um evento e retorna seu identificador."""
    with get_engine().begin() as conn:
        return conn.execute(
            text("""
                INSERT INTO estacoes
                    (evento_id, nome, modelo_equipamento, local, latitude, longitude)
                VALUES
                    (:evento_id, :nome, :modelo, :local, :latitude, :longitude)
                RETURNING id
            """),
            {
                "evento_id": int(evento_id),
                "nome": nome,
                "modelo": modelo,
                "local": local,
                "latitude": latitude,
                "longitude": longitude,
            },
        ).scalar_one()


def atualizar_estacao(
    evento_id: int,
    estacao_id: int,
    nome: str,
    modelo: str | None = None,
    local: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> None:
    """Atualiza os dados de uma estação vinculada ao evento informado."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                UPDATE estacoes
                SET nome = :nome,
                    modelo_equipamento = :modelo,
                    local = :local,
                    latitude = :latitude,
                    longitude = :longitude
                WHERE id = :estacao_id AND evento_id = :evento_id
            """),
            {
                "evento_id": int(evento_id),
                "estacao_id": int(estacao_id),
                "nome": nome,
                "modelo": modelo,
                "local": local,
                "latitude": latitude,
                "longitude": longitude,
            },
        )


def atualizar_evento(
    evento_id: int,
    nome: str,
    latitude: float | None = None,
    longitude: float | None = None,
    cidade: str | None = None,
    uf: str | None = None,
    acao_fiscalizacao: str | None = None,
    processo_sei: str | None = None,
    periodo_inicio: str | None = None,
    periodo_fim: str | None = None,
    teste_etiquetagem: bool = True,
    unidades_executantes: list[str] | None = None,
    observacoes: str | None = None,
    coordenadores: list[str] | None = None,
) -> None:
    """Atualiza o nome e a localização de um evento."""
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                UPDATE eventos
                SET nome = :nome,
                    latitude = :latitude,
                    longitude = :longitude,
                    cidade = :cidade,
                    uf = :uf,
                    acao_fiscalizacao = :acao_fiscalizacao,
                    processo_sei = :processo_sei,
                    periodo_inicio = :periodo_inicio,
                    periodo_fim = :periodo_fim,
                    teste_etiquetagem = :teste_etiquetagem,
                    observacoes = :observacoes
                WHERE id = :id
            """),
            {
                "id": int(evento_id),
                "nome": nome,
                "latitude": latitude,
                "longitude": longitude,
                "cidade": cidade,
                "uf": uf,
                "acao_fiscalizacao": acao_fiscalizacao,
                "processo_sei": processo_sei,
                "periodo_inicio": periodo_inicio,
                "periodo_fim": periodo_fim,
                "teste_etiquetagem": teste_etiquetagem,
                "observacoes": observacoes,
            },
        )
        conn.execute(
            text("DELETE FROM eventos_coordenadores WHERE evento_id = :evento_id"),
            {"evento_id": int(evento_id)},
        )
        for fiscal_id in dict.fromkeys(coordenadores or []):
            conn.execute(
                text("""
                    INSERT INTO eventos_coordenadores (evento_id, fiscal_id)
                    SELECT :evento_id, ef.fiscal_id
                    FROM eventos_fiscais ef
                    JOIN fiscais f ON f.id = ef.fiscal_id
                    WHERE ef.evento_id = :evento_id
                      AND ef.fiscal_id = :fiscal_id
                      AND f.funcao_evento = 'Coordenação'
                """),
                {"evento_id": int(evento_id), "fiscal_id": int(fiscal_id)},
            )


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
    except Exception:
        pass
    return None


def _largura_frequencia_etiqueta(valor: str) -> float:
    """Extrai a largura em kHz de uma frequência salva na etiqueta."""
    correspondencia = re.search(r"⌂\s*([\d.,]+)\s*kHz", str(valor or ""), re.I)
    if not correspondencia:
        return 0.0
    numero = correspondencia.group(1).replace(".", "").replace(",", ".")
    try:
        return max(float(numero), 0.0)
    except ValueError:
        return 0.0


def consultar_conflitos_frequencia(
    _client=None,
    evento_id=None,
    freq_digitada=None,
    largura_khz=0,
    localidade=None,
    excluir_id=None,
) -> list[dict]:
    """Retorna conflitos por sobreposição de banda no evento e local informados."""
    if evento_id is None or freq_digitada is None:
        return []
    try:
        frequencia = float(freq_digitada)
        largura = max(float(largura_khz or 0), 0.0)
    except (TypeError, ValueError):
        return []
    if frequencia <= 0:
        return []

    inicio = frequencia - largura / 2000
    fim = frequencia + largura / 2000
    local_normalizado = str(localidade or "").strip().casefold()
    conflitos = []
    try:
        with get_engine().connect() as conn:
            ocorrencias = (
                conn.execute(
                    text("""
                    SELECT o.id, o.frequencia_mhz, COALESCE(o.largura_khz, 0) AS largura_khz,
                           COALESCE(NULLIF(o.local_regiao, ''), NULLIF(e.local, ''), '') AS local,
                           COALESCE(e.nome, 'Ocorrência') AS equipamento,
                           o.identificacao AS etiqueta
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev
                      AND (:local = '' OR lower(trim(COALESCE(o.local_regiao, e.local, ''))) = :local)
                      AND (CAST(:excluir_id AS BIGINT) IS NULL OR o.id <> CAST(:excluir_id AS BIGINT))
                """),
                    {
                        "ev": int(evento_id),
                        "local": local_normalizado,
                        "excluir_id": (
                            int(excluir_id) if str(excluir_id).isdigit() else None
                        ),
                    },
                )
                .mappings()
                .all()
            )
            for registro in ocorrencias:
                centro = float(registro["frequencia_mhz"] or 0)
                banda = max(float(registro["largura_khz"] or 0), 0.0)
                existente_inicio = centro - banda / 2000
                existente_fim = centro + banda / 2000
                if inicio <= existente_fim and fim >= existente_inicio:
                    conflitos.append(
                        {
                            "origem": "Ocorrência",
                            "id": registro["id"],
                            "frequencia": centro,
                            "largura_khz": banda,
                            "local": registro["local"] or "Local não informado",
                            "equipamento": registro["equipamento"],
                            "etiqueta": registro["etiqueta"] or "Não informada",
                        }
                    )

            equipamentos = (
                conn.execute(
                    text("""
                    SELECT t.id, t.entidade, t.cpf_cnpj, t.local, t.tipo_equipamento,
                           t.numero_etiqueta, selecionada AS frequencia_texto
                    FROM testes_etiquetagem t
                    CROSS JOIN LATERAL unnest(t.frequencias_selecionadas) AS selecionada
                    WHERE t.evento_id = :ev
                      AND (:local = '' OR lower(trim(COALESCE(t.local, ''))) = :local)
                      AND (CAST(:excluir_id AS BIGINT) IS NULL OR t.id <> CAST(:excluir_id AS BIGINT))
                """),
                    {
                        "ev": int(evento_id),
                        "local": local_normalizado,
                        "excluir_id": (
                            int(excluir_id) if str(excluir_id).isdigit() else None
                        ),
                    },
                )
                .mappings()
                .all()
            )
            for registro in equipamentos:
                texto = str(registro["frequencia_texto"] or "")
                correspondencia = re.match(r"\s*([\d.,]+)", texto)
                if not correspondencia:
                    continue
                try:
                    centro = float(correspondencia.group(1).replace(",", "."))
                except ValueError:
                    continue
                banda = _largura_frequencia_etiqueta(texto)
                existente_inicio = centro - banda / 2000
                existente_fim = centro + banda / 2000
                if inicio <= existente_fim and fim >= existente_inicio:
                    conflitos.append(
                        {
                            "origem": "Teste de etiquetagem",
                            "id": registro["id"],
                            "frequencia": centro,
                            "largura_khz": banda,
                            "local": registro["local"] or "Local não informado",
                            "equipamento": registro["entidade"] or "Nome não informado",
                            "etiqueta": registro["numero_etiqueta"] or "Não informada",
                            "tipo_equipamento": registro["tipo_equipamento"]
                            or "Não informado",
                            "cpf_cnpj": registro["cpf_cnpj"] or "Não informado",
                        }
                    )
    except Exception as e:
        logger.error(f"Erro consultar_conflitos_frequencia: {e}", exc_info=True)
    return conflitos


def verificar_frequencia_global(
    _client=None, evento_id=None, freq_digitada=None, largura_khz=0, localidade=None
) -> Optional[str]:
    """Retorna uma descrição curta do primeiro conflito de frequência."""
    conflitos = consultar_conflitos_frequencia(
        evento_id=evento_id,
        freq_digitada=freq_digitada,
        largura_khz=largura_khz,
        localidade=localidade,
    )
    if not conflitos:
        return None
    conflito = conflitos[0]
    return (
        f"{conflito['origem']} {conflito['equipamento']} | "
        f"etiqueta: {conflito['etiqueta']} | local: {conflito['local']}"
    )


def verificar_equipamento_frequencia(
    _client=None, evento_id=None, freq_digitada=None, largura_khz=0, localidade=None
) -> Optional[str]:
    """Retorna apenas o alerta de equipamento do teste de etiquetagem."""
    conflitos = consultar_conflitos_frequencia(
        evento_id=evento_id,
        freq_digitada=freq_digitada,
        largura_khz=largura_khz,
        localidade=localidade,
    )
    for conflito in conflitos:
        if conflito["origem"] == "Teste de etiquetagem":
            return (
                f"equipamento: {conflito['equipamento']} | "
                f"etiqueta: {conflito['etiqueta']} | local: {conflito['local']}"
            )
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
                o.local_regiao AS "Local",
                COALESCE(e.nome, o.origem_captura, o.local_regiao) AS "EstacaoRaw",
                o.estacao_id::text AS "EstacaoID",
                o.origem_captura AS "OrigemCaptura",
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
                            AND COALESCE(NULLIF(upper(trim(o.fonte)), ''), 'PAINEL') = 'PAINEL'
              AND lower(trim(o.situacao)) = 'pendente'
            ORDER BY "Local", "Data"
        """)
        return pd.read_sql(sql, get_engine(), params={"ev": int(evento_id)})
    except Exception as e:
        logger.error(f"Erro carregar_pendencias_painel_mapeadas: {e}", exc_info=True)
        return pd.DataFrame()


def carregar_pendencias_todas_estacoes(_client=None, evento_id=None) -> pd.DataFrame:
    """Retorna pendências de todas as estações (fonte = 'ESTACAO')."""
    if evento_id is None:
        return pd.DataFrame()
    try:
        sql = text("""
            SELECT
                o.local_regiao AS "Local",
                COALESCE(e.nome, o.origem_captura, o.local_regiao) AS "EstacaoRaw",
                o.estacao_id::text AS "EstacaoID",
                o.origem_captura AS "OrigemCaptura",
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
                            AND o.fonte = 'ESTACAO'
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
                                            AND (
                                                        CAST(:excluir_id AS BIGINT) IS NULL
                                                        OR t.id <> CAST(:excluir_id AS BIGINT)
                                                    )
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
    _client=None,
    evento_id=None,
    freq_digitada=None,
    largura_khz=0,
    localidade=None,
    excluir_id=None,
) -> Optional[str]:
    """Retorna a descrição do primeiro conflito de frequência."""
    conflitos = consultar_conflitos_frequencia(
        evento_id=evento_id,
        freq_digitada=freq_digitada,
        largura_khz=largura_khz,
        localidade=localidade,
        excluir_id=excluir_id,
    )
    if not conflitos:
        return None
    conflito = conflitos[0]
    return (
        f"{conflito['origem']}: {conflito['equipamento']} | "
        f"etiqueta: {conflito['etiqueta']} | local: {conflito['local']}"
    )


def consultar_equipamentos_frequencia(
    _client=None,
    evento_id=None,
    freq_digitada=None,
    largura_khz=0,
    localidade=None,
    excluir_id=None,
) -> dict:
    """Consulta conflitos detalhados de frequência no evento e local informados."""
    resultado = {"equipamentos": [], "referencias": []}
    conflitos = consultar_conflitos_frequencia(
        evento_id=evento_id,
        freq_digitada=freq_digitada,
        largura_khz=largura_khz,
        localidade=localidade,
        excluir_id=excluir_id,
    )
    resultado["equipamentos"] = [
        c for c in conflitos if c["origem"] == "Teste de etiquetagem"
    ]
    resultado["referencias"] = [
        {
            "origem": c["origem"],
            "detalhe": (
                f"{c['equipamento']} | etiqueta: {c['etiqueta']} | "
                f"local: {c['local']} | {c['frequencia']:.3f} MHz / {c['largura_khz']:.3f} kHz"
            ),
        }
        for c in conflitos
        if c["origem"] != "Teste de etiquetagem"
    ]
    return resultado


def _salvar_imagens_teste_etiquetagem(
    conn,
    evento_id: int,
    teste_id: int,
    numero_etiqueta: str,
    imagens: list[dict] | None = None,
    imagens_excluir: list[int] | None = None,
) -> None:
    """Salva fotos do equipamento e registra anexos e exclusões na auditoria."""
    if imagens_excluir:
        removidas = (
            conn.execute(
                text("""
                SELECT id, nome_arquivo
                FROM teste_etiquetagem_imagens
                WHERE teste_etiquetagem_id = :teste_id
                  AND id = ANY(:imagem_ids)
            """),
                {"teste_id": teste_id, "imagem_ids": imagens_excluir},
            )
            .mappings()
            .all()
        )
        conn.execute(
            text("""
                DELETE FROM teste_etiquetagem_imagens
                WHERE teste_etiquetagem_id = :teste_id
                  AND id = ANY(:imagem_ids)
            """),
            {"teste_id": teste_id, "imagem_ids": imagens_excluir},
        )
        for imagem in removidas:
            conn.execute(
                text("""
                    INSERT INTO auditoria_testes_etiquetagem (
                        teste_etiquetagem_id, evento_id, usuario_fiscal,
                        campo, valor_anterior, valor_novo
                    ) VALUES (:teste_id, :evento_id, :usuario_fiscal,
                              'Imagem excluída', :nome, NULL)
                """),
                {
                    "teste_id": teste_id,
                    "evento_id": evento_id,
                    "usuario_fiscal": USR_FISCAL_ANATEL,
                    "nome": imagem["nome_arquivo"],
                },
            )

    for imagem in imagens or []:
        imagem_id = conn.execute(
            text("""
                INSERT INTO teste_etiquetagem_imagens
                    (teste_etiquetagem_id, nome_arquivo, tipo_mime,
                     tamanho_bytes, conteudo)
                VALUES (:teste_id, :nome, :tipo, :tamanho, :conteudo)
                RETURNING id
            """),
            {
                "teste_id": teste_id,
                "nome": imagem["nome_arquivo"],
                "tipo": imagem["tipo_mime"],
                "tamanho": imagem["tamanho_bytes"],
                "conteudo": imagem["conteudo"],
            },
        ).scalar_one()
        nome_imagem = _nome_imagem_teste_etiquetagem(
            teste_id, numero_etiqueta, imagem_id, imagem["nome_arquivo"]
        )
        conn.execute(
            text("""
                UPDATE teste_etiquetagem_imagens
                SET nome_arquivo = :nome
                WHERE id = :imagem_id
            """),
            {"nome": nome_imagem, "imagem_id": imagem_id},
        )
        conn.execute(
            text("""
                INSERT INTO auditoria_testes_etiquetagem (
                    teste_etiquetagem_id, evento_id, usuario_fiscal,
                    campo, valor_anterior, valor_novo
                ) VALUES (:teste_id, :evento_id, :usuario_fiscal,
                          'Imagem anexada', NULL, :nome)
            """),
            {
                "teste_id": teste_id,
                "evento_id": evento_id,
                "usuario_fiscal": USR_FISCAL_ANATEL,
                "nome": nome_imagem,
            },
        )


def inserir_teste_etiquetagem(_client=None, evento_id=None, dados: dict = None) -> str:
    """Insere um teste de etiquetagem vinculado ao evento selecionado."""
    if evento_id is None or dados is None:
        return "ERRO: parâmetros insuficientes."
    try:
        with get_engine().begin() as conn:
            resultado = conn.execute(
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
                    RETURNING id
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
            teste_id = resultado.scalar_one()
            _salvar_imagens_teste_etiquetagem(
                conn,
                int(evento_id),
                teste_id,
                dados["numero_etiqueta"],
                dados.get("imagens"),
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
        registros = [dict(row) for row in rows]
        for registro in registros:
            registro["imagens"] = carregar_imagens_teste_etiquetagem(
                evento_id=evento_id, teste_id=registro["id"]
            )
        return registros
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
            atual = (
                conn.execute(
                    text("""
                    SELECT numero_etiqueta
                    FROM testes_etiquetagem
                    WHERE id = :id AND evento_id = :ev
                    FOR UPDATE
                """),
                    {"id": int(registro_id), "ev": int(evento_id)},
                )
                .mappings()
                .first()
            )
            if atual is None:
                return "ERRO: registro não encontrado."
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
            _salvar_imagens_teste_etiquetagem(
                conn,
                int(evento_id),
                int(registro_id),
                dados["numero_etiqueta"],
                dados.get("imagens"),
                dados.get("imagens_excluir"),
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
                        (evento_id, estacao_id, origem_captura, local_regiao, fiscal, data, hora,
                         frequencia_mhz, largura_khz, faixa,
                         identificacao, autorizado, ute,
                         processo_sei_ute, observacoes,
                         interferente, situacao, fonte)
                    VALUES
                        (:ev, :estacao_id, :origem_captura, :local, :fiscal, :data, :hora,
                         :freq, :bw, :faixa,
                         :ident, :autz, :ute,
                         :proc, :obs,
                        :inter, :situ, :fonte)
                    RETURNING id
                """),
                {
                    "ev": int(evento_id),
                    "estacao_id": dados_formulario.get("Estação ID") or None,
                    "origem_captura": dados_formulario.get("Origem da captura") or None,
                    "local": dados_formulario.get("Local/Região", ""),
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
                    "fonte": "ESTACAO",
                },
            )
            ocorrencia_id = resultado.scalar_one()
            fiscais_participantes = list(
                dict.fromkeys(
                    int(fiscal_id)
                    for fiscal_id in dados_formulario.get("Fiscais participantes", [])
                    if str(fiscal_id).isdigit()
                )
            )
            if fiscais_participantes:
                fiscais_validos = (
                    conn.execute(
                        text("""
                        SELECT fiscal_id
                        FROM eventos_fiscais
                        WHERE evento_id = :evento_id
                          AND fiscal_id = ANY(CAST(:fiscal_ids AS BIGINT[]))
                    """),
                        {
                            "evento_id": int(evento_id),
                            "fiscal_ids": fiscais_participantes,
                        },
                    )
                    .scalars()
                    .all()
                )
                if set(fiscais_validos) != set(fiscais_participantes):
                    raise ValueError("Fiscal participante não pertence ao evento.")
                conn.execute(
                    text("""
                        INSERT INTO ocorrencia_fiscais (ocorrencia_id, fiscal_id)
                        SELECT :ocorrencia_id, unnest(CAST(:fiscal_ids AS BIGINT[]))
                    """),
                    {
                        "ocorrencia_id": int(ocorrencia_id),
                        "fiscal_ids": fiscais_participantes,
                    },
                )
                nomes_participantes = conn.execute(
                    text("""
                        SELECT string_agg(nome, ', ' ORDER BY nome)
                        FROM fiscais WHERE id = ANY(CAST(:fiscal_ids AS BIGINT[]))
                    """),
                    {"fiscal_ids": fiscais_participantes},
                ).scalar_one()
                conn.execute(
                    text("""
                        INSERT INTO auditoria_ocorrencias (
                            ocorrencia_id, evento_id, usuario_fiscal, campo, valor_anterior, valor_novo
                        ) VALUES (:ocorrencia_id, :evento_id, :usuario_fiscal,
                                  'Fiscais participantes', NULL, :valor_novo)
                    """),
                    {
                        "ocorrencia_id": int(ocorrencia_id),
                        "evento_id": int(evento_id),
                        "usuario_fiscal": dados_formulario.get("Fiscal", ""),
                        "valor_novo": nomes_participantes,
                    },
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
                        "ocorrencia_id": ocorrencia_id,
                        "nome": _nome_imagem_emissao(
                            ocorrencia_id,
                            dia,
                            hora,
                            imagem["nome_arquivo"],
                            imagem.get("data_foto"),
                            imagem.get("hora_foto"),
                        ),
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
    _client=None,
    evento_id=None,
    tipo="",
    regiao="",
    lat="",
    lon="",
    observacoes="",
    imagens=None,
) -> str:
    """Insere registro de ocorrência especial."""
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
            bsr_erb_id = conn.execute(
                text("""
                    INSERT INTO bsr_erb
                        (evento_id, tipo, regiao, latitude, longitude, observacoes)
                    VALUES (:ev, :tipo, :regiao, :lat, :lon, :observacoes)
                    RETURNING id
                """),
                {
                    "ev": int(evento_id),
                    "tipo": tipo,
                    "regiao": regiao or "",
                    "lat": lat_v,
                    "lon": lon_v,
                    "observacoes": observacoes or "",
                },
            ).scalar_one()
            nome_evento = conn.execute(
                text("SELECT nome FROM eventos WHERE id = :evento_id"),
                {"evento_id": int(evento_id)},
            ).scalar_one_or_none()
            instante_imagens = datetime.now(timezone.utc)
            conn.execute(
                text("""
                    INSERT INTO auditoria_bsr_erb (
                        bsr_erb_id, evento_id, usuario_fiscal, campo,
                        valor_anterior, valor_novo
                    ) VALUES (:registro_id, :evento_id, :usuario, 'Inclusão', NULL, :valor)
                """),
                {
                    "registro_id": bsr_erb_id,
                    "evento_id": int(evento_id),
                    "usuario": USR_FISCAL_ANATEL,
                    "valor": f"{tipo} | {regiao or ''}",
                },
            )
            for indice, imagem in enumerate(imagens or [], start=1):
                nome_arquivo = _nome_imagem_bsr_erb(
                    bsr_erb_id,
                    tipo,
                    nome_evento,
                    instante_imagens,
                    imagem["nome_arquivo"],
                    indice,
                )
                conn.execute(
                    text("""
                        INSERT INTO bsr_erb_imagens
                            (bsr_erb_id, nome_arquivo, tipo_mime, tamanho_bytes, conteudo)
                        VALUES
                            (:bsr_erb_id, :nome_arquivo, :tipo_mime, :tamanho_bytes, :conteudo)
                    """),
                    {
                        "bsr_erb_id": bsr_erb_id,
                        "nome_arquivo": nome_arquivo,
                        "tipo_mime": imagem["tipo_mime"],
                        "tamanho_bytes": imagem["tamanho_bytes"],
                        "conteudo": imagem["conteudo"],
                    },
                )
                conn.execute(
                    text("""
                        INSERT INTO auditoria_bsr_erb (
                            bsr_erb_id, evento_id, usuario_fiscal, campo,
                            valor_anterior, valor_novo
                        ) VALUES (:registro_id, :evento_id, :usuario,
                                  'Imagem anexada', NULL, :valor)
                    """),
                    {
                        "registro_id": bsr_erb_id,
                        "evento_id": int(evento_id),
                        "usuario": USR_FISCAL_ANATEL,
                        "valor": nome_arquivo,
                    },
                )
        return f"'{tipo}' incluído com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


def atualizar_bsr_erb(
    registro_id,
    evento_id,
    tipo="",
    regiao="",
    lat="",
    lon="",
    observacoes="",
    imagens=None,
) -> str:
    """Atualiza um registro BSR/ERB e acrescenta novas fotos, se houver."""
    try:
        lat_v = float(lat.replace(",", ".")) if lat else None
        lon_v = float(lon.replace(",", ".")) if lon else None
    except (ValueError, AttributeError):
        lat_v = None
        lon_v = None

    try:
        with get_engine().begin() as conn:
            anterior = (
                conn.execute(
                    text("""
                    SELECT tipo, regiao, latitude, longitude, observacoes
                    FROM bsr_erb
                    WHERE id = :id AND evento_id = :evento_id AND excluido_em IS NULL
                    FOR UPDATE
                """),
                    {"id": int(registro_id), "evento_id": int(evento_id)},
                )
                .mappings()
                .first()
            )
            if anterior is None:
                return "ERRO: Ocorrência especial não encontrada."
            atualizado = conn.execute(
                text("""
                    UPDATE bsr_erb
                    SET tipo = :tipo, regiao = :regiao, latitude = :lat,
                        longitude = :lon, observacoes = :observacoes
                    WHERE id = :id AND evento_id = :evento_id
                """),
                {
                    "id": int(registro_id),
                    "evento_id": int(evento_id),
                    "tipo": tipo,
                    "regiao": regiao or "",
                    "lat": lat_v,
                    "lon": lon_v,
                    "observacoes": observacoes or "",
                },
            ).rowcount
            if not atualizado:
                return "ERRO: Ocorrência especial não encontrada."

            valores_novos = {
                "Tipo": tipo,
                "Local": regiao or "",
                "Latitude": lat_v,
                "Longitude": lon_v,
                "Observações": observacoes or "",
            }
            valores_anteriores = {
                "Tipo": anterior["tipo"],
                "Local": anterior["regiao"] or "",
                "Latitude": anterior["latitude"],
                "Longitude": anterior["longitude"],
                "Observações": anterior["observacoes"] or "",
            }
            for campo, valor_novo in valores_novos.items():
                valor_anterior = valores_anteriores[campo]
                if str(valor_anterior) != str(valor_novo):
                    conn.execute(
                        text("""
                            INSERT INTO auditoria_bsr_erb (
                                bsr_erb_id, evento_id, usuario_fiscal, campo,
                                valor_anterior, valor_novo
                            ) VALUES (:registro_id, :evento_id, :usuario, :campo,
                                      :valor_anterior, :valor_novo)
                        """),
                        {
                            "registro_id": int(registro_id),
                            "evento_id": int(evento_id),
                            "usuario": USR_FISCAL_ANATEL,
                            "campo": campo,
                            "valor_anterior": str(valor_anterior),
                            "valor_novo": str(valor_novo),
                        },
                    )

            nome_evento = conn.execute(
                text("SELECT nome FROM eventos WHERE id = :evento_id"),
                {"evento_id": int(evento_id)},
            ).scalar_one_or_none()
            instante_imagens = datetime.now(timezone.utc)
            quantidade_imagens = conn.execute(
                text(
                    "SELECT COUNT(*) FROM bsr_erb_imagens WHERE bsr_erb_id = :registro_id"
                ),
                {"registro_id": int(registro_id)},
            ).scalar_one()
            for indice, imagem in enumerate(
                imagens or [], start=int(quantidade_imagens) + 1
            ):
                nome_arquivo = _nome_imagem_bsr_erb(
                    int(registro_id),
                    tipo,
                    nome_evento,
                    instante_imagens,
                    imagem["nome_arquivo"],
                    indice,
                )
                conn.execute(
                    text("""
                        INSERT INTO bsr_erb_imagens
                            (bsr_erb_id, nome_arquivo, tipo_mime, tamanho_bytes, conteudo)
                        VALUES
                            (:bsr_erb_id, :nome_arquivo, :tipo_mime, :tamanho_bytes, :conteudo)
                    """),
                    {
                        "bsr_erb_id": int(registro_id),
                        "nome_arquivo": nome_arquivo,
                        "tipo_mime": imagem["tipo_mime"],
                        "tamanho_bytes": imagem["tamanho_bytes"],
                        "conteudo": imagem["conteudo"],
                    },
                )
                conn.execute(
                    text("""
                        INSERT INTO auditoria_bsr_erb (
                            bsr_erb_id, evento_id, usuario_fiscal, campo,
                            valor_anterior, valor_novo
                        ) VALUES (:registro_id, :evento_id, :usuario,
                                  'Imagem anexada', NULL, :valor)
                    """),
                    {
                        "registro_id": int(registro_id),
                        "evento_id": int(evento_id),
                        "usuario": USR_FISCAL_ANATEL,
                        "valor": nome_arquivo,
                    },
                )
        return f"'{tipo}' atualizado com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


def excluir_bsr_erb(
    registro_id, evento_id, usuario_fiscal: str = USR_FISCAL_ANATEL
) -> str:
    """Marca um registro BSR/ERB como excluído, sem apagar seus dados."""
    try:
        with get_engine().begin() as conn:
            atualizado = conn.execute(
                text("""
                    UPDATE bsr_erb
                    SET excluido_em = now(), excluido_por = :usuario
                    WHERE id = :id AND evento_id = :evento_id AND excluido_em IS NULL
                """),
                {
                    "id": int(registro_id),
                    "evento_id": int(evento_id),
                    "usuario": usuario_fiscal,
                },
            ).rowcount
            if not atualizado:
                return "ERRO: Ocorrência especial não encontrada ou já excluída."
            conn.execute(
                text("""
                    INSERT INTO auditoria_bsr_erb (
                        bsr_erb_id, evento_id, usuario_fiscal, campo,
                        valor_anterior, valor_novo
                    ) VALUES (:registro_id, :evento_id, :usuario,
                              'Exclusão lógica', NULL, :valor)
                """),
                {
                    "registro_id": int(registro_id),
                    "evento_id": int(evento_id),
                    "usuario": usuario_fiscal,
                    "valor": "Registro marcado como excluído",
                },
            )
        return "Ocorrência especial excluída com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


def excluir_imagem_bsr_erb(
    imagem_id, registro_id, evento_id, usuario_fiscal: str = USR_FISCAL_ANATEL
) -> str:
    """Exclui uma foto de BSR/ERB e registra a ação na auditoria."""
    try:
        with get_engine().begin() as conn:
            imagem = (
                conn.execute(
                    text("""
                    SELECT i.nome_arquivo
                    FROM bsr_erb_imagens i
                    JOIN bsr_erb b ON b.id = i.bsr_erb_id
                    WHERE i.id = :imagem_id AND i.bsr_erb_id = :registro_id
                      AND b.evento_id = :evento_id AND b.excluido_em IS NULL
                    """),
                    {
                        "imagem_id": int(imagem_id),
                        "registro_id": int(registro_id),
                        "evento_id": int(evento_id),
                    },
                )
                .mappings()
                .first()
            )
            if imagem is None:
                return "ERRO: Foto não encontrada."

            conn.execute(
                text("DELETE FROM bsr_erb_imagens WHERE id = :imagem_id"),
                {"imagem_id": int(imagem_id)},
            )
            conn.execute(
                text("""
                    INSERT INTO auditoria_bsr_erb (
                        bsr_erb_id, evento_id, usuario_fiscal, campo,
                        valor_anterior, valor_novo
                    ) VALUES (:registro_id, :evento_id, :usuario,
                              'Imagem excluída', :valor, NULL)
                """),
                {
                    "registro_id": int(registro_id),
                    "evento_id": int(evento_id),
                    "usuario": usuario_fiscal,
                    "valor": imagem["nome_arquivo"],
                },
            )
        return "Foto excluída com sucesso."
    except Exception as e:
        return f"ERRO: {e}"


def listar_bsr_erb(evento_id: int) -> list[dict]:
    """Lista registros BSR/ERB do evento com as fotos anexadas."""
    with get_engine().connect() as conn:
        registros = (
            conn.execute(
                text("""
                SELECT b.id, b.tipo, b.regiao, b.latitude, b.longitude,
                       b.observacoes, b.criado_em,
                       i.id AS imagem_id, i.nome_arquivo, i.tipo_mime, i.conteudo
                FROM bsr_erb b
                LEFT JOIN bsr_erb_imagens i ON i.bsr_erb_id = b.id
                WHERE b.evento_id = :evento_id AND b.excluido_em IS NULL
                ORDER BY b.criado_em DESC, i.id
            """),
                {"evento_id": int(evento_id)},
            )
            .mappings()
            .all()
        )

    registros_por_id = {}
    for registro in registros:
        item = registros_por_id.setdefault(
            registro["id"],
            {
                "id": registro["id"],
                "tipo": registro["tipo"],
                "regiao": registro["regiao"],
                "latitude": registro["latitude"],
                "longitude": registro["longitude"],
                "observacoes": registro["observacoes"],
                "criado_em": registro["criado_em"],
                "imagens": [],
            },
        )
        if registro["imagem_id"]:
            item["imagens"].append(
                {
                    "id": registro["imagem_id"],
                    "nome_arquivo": registro["nome_arquivo"],
                    "url": (
                        f"data:{registro['tipo_mime']};base64,"
                        f"{base64.b64encode(bytes(registro['conteudo'])).decode('ascii')}"
                    ),
                }
            )
    return list(registros_por_id.values())


# =========================================================================
# Atualização de campos (edição de ocorrências)
# =========================================================================


def atualizar_campos_na_aba_mae(
    _client=None,
    evento_id=None,
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
                          SELECT o.{', o.'.join(campos)}, o.estacao_id, o.origem_captura,
                              COALESCE(e.nome, o.origem_captura, '') AS estacao_nome
                    FROM ocorrencias o
                    LEFT JOIN estacoes e ON e.id = o.estacao_id
                    WHERE o.evento_id = :ev AND o.id = :id
                    FOR UPDATE OF o
                """),
                    params,
                )
                .mappings()
                .first()
            )
            if atual is None:
                return f"ERRO: ID {id_ocorrencia} não encontrado no evento {evento_id}."

            alteracoes = []

            if "Estação ID" in novos_valores:
                try:
                    nova_estacao_id = int(str(novos_valores["Estação ID"]).strip())
                except (TypeError, ValueError):
                    return "ERRO: estação inválida."

                nova_estacao = (
                    conn.execute(
                        text("""
                            SELECT nome
                            FROM estacoes
                            WHERE id = :estacao_id AND evento_id = :ev
                        """),
                        {"estacao_id": nova_estacao_id, "ev": int(evento_id)},
                    )
                    .mappings()
                    .first()
                )
                if nova_estacao is None:
                    return "ERRO: estação não pertence ao evento selecionado."

                estacao_atual_id = atual["estacao_id"]
                if estacao_atual_id != nova_estacao_id or atual["origem_captura"]:
                    updates.extend(
                        ["estacao_id = :v_estacao_id", "origem_captura = NULL"]
                    )
                    params["v_estacao_id"] = nova_estacao_id
                    alteracoes.append(
                        (
                            "Estação utilizada",
                            atual["estacao_nome"] or estacao_atual_id,
                            nova_estacao["nome"],
                        )
                    )

            if "Origem da captura" in novos_valores:
                nova_origem = str(novos_valores["Origem da captura"]).strip()
                if not nova_origem:
                    return "ERRO: origem da captura inválida."
                if (
                    atual["estacao_id"] is not None
                    or atual["origem_captura"] != nova_origem
                ):
                    updates.extend(
                        ["estacao_id = NULL", "origem_captura = :v_origem_captura"]
                    )
                    params["v_origem_captura"] = nova_origem
                    alteracoes.append(
                        ("Estação utilizada", atual["estacao_nome"], nova_origem)
                    )

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

            emissao = (
                conn.execute(
                    text(
                        "SELECT data, hora FROM ocorrencias WHERE evento_id = :ev AND id = :id"
                    ),
                    {"ev": int(evento_id), "id": int(id_ocorrencia)},
                )
                .mappings()
                .one()
            )
            for imagem in imagens or []:
                nome_imagem = _nome_imagem_emissao(
                    int(id_ocorrencia),
                    emissao["data"],
                    emissao["hora"],
                    imagem["nome_arquivo"],
                    imagem.get("data_foto"),
                    imagem.get("hora_foto"),
                )
                conn.execute(
                    text("""
                        INSERT INTO ocorrencia_imagens
                            (ocorrencia_id, nome_arquivo, tipo_mime,
                             tamanho_bytes, conteudo)
                        VALUES (:ocorrencia_id, :nome, :tipo, :tamanho, :conteudo)
                    """),
                    {
                        "ocorrencia_id": int(id_ocorrencia),
                        "nome": nome_imagem,
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
                        "valor_novo": nome_imagem,
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


def consultar_auditoria_evento(
    evento_id=None,
    origem=None,
    data_inicio=None,
    data_fim=None,
    fiscal=None,
    palavra=None,
) -> list[dict]:
    """Retorna a auditoria consolidada de emissões, etiquetagem e BSR/ERB."""
    if evento_id is None:
        return []
    try:
        with get_engine().connect() as conn:
            rows = (
                conn.execute(
                    text("""
                           SELECT origem, registro_id, registro, usuario_fiscal,
                               campo, valor_anterior, valor_novo, modificado_em,
                               imagem_tipo_mime, imagem_conteudo
                        FROM (
                            SELECT
                                'Emissão' AS origem,
                                auditoria.ocorrencia_id AS registro_id,
                                COALESCE(ocorrencia.id_planilha,
                                         'Ocorrência #' || ocorrencia.id::text) AS registro,
                                auditoria.usuario_fiscal,
                                auditoria.campo,
                                auditoria.valor_anterior,
                                auditoria.valor_novo,
                                                                auditoria.modificado_em,
                                                                imagem.tipo_mime AS imagem_tipo_mime,
                                                                imagem.conteudo AS imagem_conteudo
                            FROM auditoria_ocorrencias auditoria
                            JOIN ocorrencias ocorrencia
                              ON ocorrencia.id = auditoria.ocorrencia_id
                                                        LEFT JOIN LATERAL (
                                                                SELECT oi.tipo_mime, oi.conteudo
                                                                FROM ocorrencia_imagens oi
                                                                WHERE oi.ocorrencia_id = auditoria.ocorrencia_id
                                                                    AND oi.nome_arquivo = auditoria.valor_novo
                                                                    AND auditoria.campo = 'Imagem anexada'
                                                                ORDER BY oi.id
                                                                LIMIT 1
                                                        ) imagem ON TRUE
                            WHERE auditoria.evento_id = :evento_id
                            UNION ALL

                            SELECT
                                'Teste de etiquetagem' AS origem,
                                auditoria.teste_etiquetagem_id AS registro_id,
                                COALESCE(teste.numero_etiqueta,
                                         'Teste #' || teste.id::text) AS registro,
                                auditoria.usuario_fiscal,
                                auditoria.campo,
                                auditoria.valor_anterior,
                                auditoria.valor_novo,
                                                                auditoria.modificado_em,
                                                                imagem.tipo_mime AS imagem_tipo_mime,
                                                                imagem.conteudo AS imagem_conteudo
                            FROM auditoria_testes_etiquetagem auditoria
                            JOIN testes_etiquetagem teste
                              ON teste.id = auditoria.teste_etiquetagem_id
                                                        LEFT JOIN LATERAL (
                                                                SELECT imagem.tipo_mime, imagem.conteudo
                                                                FROM teste_etiquetagem_imagens imagem
                                                                WHERE imagem.teste_etiquetagem_id = auditoria.teste_etiquetagem_id
                                                                    AND imagem.nome_arquivo = auditoria.valor_novo
                                                                    AND auditoria.campo = 'Imagem anexada'
                                                                ORDER BY imagem.id
                                                                LIMIT 1
                                                        ) imagem ON TRUE
                            WHERE auditoria.evento_id = :evento_id
                            UNION ALL

                            SELECT
                                'Ocorrências especiais' AS origem,
                                auditoria.bsr_erb_id AS registro_id,
                                COALESCE(
                                    NULLIF(CONCAT_WS(' - ', bsr.tipo, bsr.regiao), ''),
                                    'Registro #' || bsr.id::text
                                ) AS registro,
                                auditoria.usuario_fiscal,
                                auditoria.campo,
                                auditoria.valor_anterior,
                                auditoria.valor_novo,
                                auditoria.modificado_em,
                                imagem.tipo_mime AS imagem_tipo_mime,
                                imagem.conteudo AS imagem_conteudo
                            FROM auditoria_bsr_erb auditoria
                            JOIN bsr_erb bsr ON bsr.id = auditoria.bsr_erb_id
                            LEFT JOIN LATERAL (
                                SELECT imagem.tipo_mime, imagem.conteudo
                                FROM bsr_erb_imagens imagem
                                WHERE imagem.bsr_erb_id = auditoria.bsr_erb_id
                                  AND imagem.nome_arquivo = auditoria.valor_novo
                                  AND auditoria.campo = 'Imagem anexada'
                                ORDER BY imagem.id
                                LIMIT 1
                            ) imagem ON TRUE
                            WHERE auditoria.evento_id = :evento_id

                            UNION ALL

                            SELECT
                                CASE
                                    WHEN auditoria.campo LIKE 'Coordenação - %'
                                        THEN 'Coordenação'
                                    WHEN auditoria.campo = 'Login no sistema'
                                        THEN 'Login'
                                    ELSE 'Evento'
                                END AS origem,
                                auditoria.evento_id AS registro_id,
                                CASE
                                    WHEN auditoria.campo LIKE 'Coordenação - %'
                                        THEN split_part(auditoria.valor_novo, ';', 1)
                                    WHEN auditoria.campo = 'Login no sistema'
                                        THEN 'Acesso ao sistema'
                                    ELSE evento.nome
                                END AS registro,
                                auditoria.usuario_fiscal,
                                auditoria.campo,
                                auditoria.valor_anterior,
                                auditoria.valor_novo,
                                auditoria.modificado_em,
                                NULL AS imagem_tipo_mime,
                                NULL AS imagem_conteudo
                            FROM auditoria_eventos auditoria
                            JOIN eventos evento ON evento.id = auditoria.evento_id
                            WHERE auditoria.evento_id = :evento_id
                        ) auditoria_consolidada
                                                WHERE (
                                                            CAST(:origem AS TEXT) IS NULL
                                                            OR CAST(:origem AS TEXT) = ''
                                                            OR origem = CAST(:origem AS TEXT)
                                                    )
                          AND (
                              CAST(:data_inicio AS DATE) IS NULL
                              OR modificado_em >= CAST(:data_inicio AS DATE)
                          )
                          AND (
                              CAST(:data_fim AS DATE) IS NULL
                              OR modificado_em < CAST(:data_fim AS DATE) + INTERVAL '1 day'
                          )
                          AND (
                              CAST(:fiscal AS TEXT) IS NULL
                              OR CAST(:fiscal AS TEXT) = ''
                              OR LOWER(COALESCE(usuario_fiscal, '')) LIKE LOWER('%' || CAST(:fiscal AS TEXT) || '%')
                          )
                          AND (
                              CAST(:palavra AS TEXT) IS NULL
                              OR CAST(:palavra AS TEXT) = ''
                              OR LOWER(CONCAT_WS(
                                  ' ', origem, registro, usuario_fiscal, campo,
                                  valor_anterior, valor_novo
                              )) LIKE LOWER('%' || CAST(:palavra AS TEXT) || '%')
                          )
                        ORDER BY modificado_em DESC
                    """),
                    {
                        "evento_id": int(evento_id),
                        "origem": origem,
                        "data_inicio": data_inicio,
                        "data_fim": data_fim,
                        "fiscal": fiscal,
                        "palavra": palavra,
                    },
                )
                .mappings()
                .all()
            )
        auditoria = []
        for row in rows:
            registro = dict(row)
            conteudo = registro.pop("imagem_conteudo", None)
            tipo_mime = registro.pop("imagem_tipo_mime", None)
            registro["imagem_url"] = (
                f"data:{tipo_mime};base64,{base64.b64encode(bytes(conteudo)).decode('ascii')}"
                if conteudo and tipo_mime
                else None
            )
            auditoria.append(registro)
        return auditoria
    except Exception as e:
        logger.error("Erro ao consultar auditoria consolidada: %s", e, exc_info=True)
        return []


# =========================================================================
# Busca textual
# =========================================================================


def _buscar_por_texto_livre(
    _client=None, evento_id=None, termos: str = "", abas: list = None
) -> pd.DataFrame:
    """Busca ocorrências por texto, ID ou todas as emissões do evento."""
    termo = termos.strip() if termos else ""
    if evento_id is None or (termo and len(termo) < 3 and not termo.isdigit()):
        return pd.DataFrame()
    try:
        termo_clean = _escape_like(termo)
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
              AND (
                                    (:listar_tratadas)
                                    OR (
                                        NOT :listar_tratadas
                                        AND (
                                            unaccent(lower(
                                                COALESCE(o.local_regiao,'') || ' ' ||
                                                COALESCE(o.fiscal,'') || ' ' ||
                                                COALESCE(o.identificacao,'') || ' ' ||
                                                COALESCE(o.observacoes,'') || ' ' ||
                                                COALESCE(o.faixa,'') || ' ' ||
                                                COALESCE(o.processo_sei_ute,'')
                                            )) LIKE unaccent(lower(:q))
                                            OR o.id::text LIKE :q
                                        )
                                    )
              )
                        ORDER BY o.data DESC NULLS LAST, o.id DESC
                        LIMIT CASE WHEN :listar_tratadas THEN 2147483647 ELSE 200 END
        """)
        df = pd.read_sql(
            sql,
            get_engine(),
            params={
                "ev": int(evento_id),
                "q": f"%{termo_clean}%",
                "listar_tratadas": not bool(termo),
            },
        )
        return df
    except Exception as e:
        logger.error(f"Erro _buscar_por_texto_livre: {e}", exc_info=True)
        return pd.DataFrame()


def sugerir_busca_emissoes(evento_id=None, termo: str = "") -> list[dict]:
    """Retorna sugestões de ID e descrição para o autocomplete de emissões."""
    termo = termo.strip() if termo else ""
    if evento_id is None or not termo:
        return []
    try:
        with get_engine().connect() as conn:
            rows = (
                conn.execute(
                    text("""
                        SELECT o.id::text AS id,
                               COALESCE(e.nome, o.local_regiao, 'Sem local') AS local,
                               o.frequencia_mhz::text AS frequencia,
                               o.identificacao AS identificacao
                        FROM ocorrencias o
                        LEFT JOIN estacoes e ON e.id = o.estacao_id
                        WHERE o.evento_id = :evento_id
                          AND (
                              o.id::text LIKE :termo
                              OR unaccent(lower(
                                  COALESCE(e.nome, '') || ' ' ||
                                  COALESCE(o.local_regiao, '') || ' ' ||
                                  COALESCE(o.identificacao, '') || ' ' ||
                                  COALESCE(o.observacoes, '')
                              )) LIKE unaccent(lower(:termo))
                          )
                        ORDER BY o.id DESC
                        LIMIT 10
                    """),
                    {"evento_id": int(evento_id), "termo": f"%{_escape_like(termo)}%"},
                )
                .mappings()
                .all()
            )
        return [
            {
                "id": row["id"],
                "label": " | ".join(
                    parte
                    for parte in [
                        f"ID {row['id']}",
                        row["local"],
                        f"{row['frequencia']} MHz" if row["frequencia"] else "",
                        row["identificacao"] or "",
                    ]
                    if parte
                ),
            }
            for row in rows
        ]
    except Exception as e:
        logger.error("Erro ao sugerir emissões: %s", e, exc_info=True)
        return []
