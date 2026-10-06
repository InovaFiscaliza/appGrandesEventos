"""Exemplo PostgreSQL: usa a mesma conexão SQLAlchemy do AppGrandesEventos.
As tabelas didáticas ficam no schema guia_programacao.
"""
from pathlib import Path
from sqlalchemy import text
from app.services.db import get_engine

BASE = Path(__file__).resolve().parent
FISCAIS = {1: "Ana — Fiscal", 2: "Bruno — Fiscal"}


def preparar():
    # Executado somente ao iniciar o laboratório, nunca ao importar o módulo.
    # Configure DATABASE_URL para um banco PostgreSQL de desenvolvimento.
    with get_engine().begin() as conn:
        sql = (BASE / "schema.sql").read_text(encoding="utf-8")
        for comando in sql.split(";"):
            if comando.strip():
                conn.execute(text(comando))


def validar(form):
    titulo = str(form.get("titulo", "")).strip()
    descricao = str(form.get("descricao", "")).strip()
    status = str(form.get("status", ""))
    prioridade = str(form.get("prioridade", ""))
    try:
        fiscal_id = int(form.get("fiscal_id", ""))
    except (TypeError, ValueError):
        raise ValueError("Selecione um fiscal válido.") from None
    if not 3 <= len(titulo) <= 100:
        raise ValueError("O título deve ter entre 3 e 100 caracteres.")
    if len(descricao) > 2000:
        raise ValueError("A descrição deve ter até 2000 caracteres.")
    if status not in {"pendente", "concluida"}:
        raise ValueError("Status inválido.")
    if prioridade not in {"baixa", "normal", "alta"}:
        raise ValueError("Prioridade inválida.")
    if fiscal_id not in FISCAIS:
        raise ValueError("Fiscal não encontrado.")
    return dict(titulo=titulo, descricao=descricao, status=status,
                prioridade=prioridade, fiscal_id=fiscal_id)


def listar(evento_id):
    with get_engine().connect() as conn:
        resultado = conn.execute(text("""
            SELECT * FROM guia_programacao.tarefas
            WHERE evento_id = :evento_id ORDER BY id DESC
        """), {"evento_id": int(evento_id)})
        return [dict(row) for row in resultado.mappings().all()]


def criar(evento_id, valores):
    with get_engine().begin() as conn:
        return conn.execute(text("""
            INSERT INTO guia_programacao.tarefas
                (evento_id, titulo, descricao, status, prioridade, fiscal_id)
            VALUES (:evento_id, :titulo, :descricao, :status, :prioridade, :fiscal_id)
            RETURNING id
        """), {**valores, "evento_id": int(evento_id)}).scalar_one()


def editar(evento_id, tarefa_id, valores, fiscal_id, coordenador):
    with get_engine().begin() as conn:
        parametros = {"evento_id": int(evento_id), "tarefa_id": int(tarefa_id)}
        atual = conn.execute(text("""
            SELECT * FROM guia_programacao.tarefas
            WHERE evento_id = :evento_id AND id = :tarefa_id
            FOR UPDATE
        """), parametros).mappings().first()
        if atual is None:
            raise ValueError("Tarefa não encontrada neste evento.")
        if not coordenador and (atual["fiscal_id"] != fiscal_id or valores["fiscal_id"] != fiscal_id):
            raise PermissionError("Você pode editar apenas suas tarefas e não pode reatribuí-las.")
        conn.execute(text("""
            UPDATE guia_programacao.tarefas
            SET titulo = :titulo, descricao = :descricao, status = :status,
                prioridade = :prioridade, fiscal_id = :fiscal_id
            WHERE evento_id = :evento_id AND id = :tarefa_id
        """), {**valores, **parametros})


def excluir(evento_id, tarefa_id):
    with get_engine().begin() as conn:
        resultado = conn.execute(text("""
            DELETE FROM guia_programacao.tarefas
            WHERE evento_id = :evento_id AND id = :tarefa_id
        """), {"evento_id": int(evento_id), "tarefa_id": int(tarefa_id)})
        return resultado.rowcount == 1
