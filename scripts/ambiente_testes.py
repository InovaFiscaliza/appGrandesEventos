"""Prepara schemas sinteticos em PostgreSQL exclusivo de testes."""

import hashlib
import re
from graphlib import TopologicalSorter
from pathlib import Path
from uuid import uuid4

from pglast import ast, parse_sql
from pglast.stream import RawStream
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL, make_url

RAIZ = Path(__file__).resolve().parents[1]


def validar_url_testes(valor: str) -> URL:
    """Recusa bancos de trabalho, servidores remotos e nomes genericos."""
    url = make_url(valor)
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in {"127.0.0.1", "localhost"}
        or not re.fullmatch(r"appeventos_test_[a-f0-9]{8}", url.database or "")
    ):
        raise ValueError(
            "Use PostgreSQL local exclusivo com nome appeventos_test_<8 hexadecimais>."
        )
    return url


def aplicar_migracoes_testes(engine: Engine) -> None:
    """Executa as migracoes publicadas em transacao, somente no banco de testes."""
    validar_url_testes(engine.url.render_as_string(hide_password=False))
    with engine.begin() as connection:
        connection.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS test_schema_migrations (
                version TEXT PRIMARY KEY, sha256 TEXT NOT NULL
            )
        """)
        aplicadas = dict(
            connection.execute(
                text("SELECT version, sha256 FROM test_schema_migrations")
            )
            .tuples()
            .all()
        )
        for arquivo in sorted((RAIZ / "local_server" / "migrations").glob("*.sql")):
            checksum = hashlib.sha256(arquivo.read_bytes()).hexdigest()
            if arquivo.name in aplicadas:
                if aplicadas[arquivo.name] != checksum:
                    raise ValueError(f"Migracao publicada foi alterada: {arquivo.name}")
                continue
            connection.exec_driver_sql(arquivo.read_text(encoding="utf-8-sig"))
            connection.execute(
                text(
                    "INSERT INTO test_schema_migrations (version, sha256) VALUES (:version, :sha256)"
                ),
                {"version": arquivo.name, "sha256": checksum},
            )


def preparar_banco(valor: str, migrar: bool = True) -> URL:
    """Cria um schema novo; nunca executa o schema legado integral nem apaga dados."""
    url = validar_url_testes(valor)
    schema = f"regressao_{uuid4().hex}"
    engine = create_engine(url, hide_parameters=True)
    tabelas: dict[str, ast.CreateStmt] = {}
    indices: list[ast.IndexStmt] = []
    adicoes: list[ast.AlterTableStmt] = []
    for instrucao in parse_sql(
        (RAIZ / "db" / "schema.sql").read_text(encoding="utf-8-sig")
    ):
        node = instrucao.stmt
        if isinstance(node, ast.CreateStmt):
            tabelas[node.relation.relname] = node
        elif isinstance(node, ast.IndexStmt):
            indices.append(node)
        elif isinstance(node, ast.AlterTableStmt) and all(
            comando.subtype.name == "AT_AddColumn" for comando in node.cmds
        ):
            if not (
                node.relation.relname == "ocorrencias"
                and any(
                    comando.def_.colname == "submetida_coordenador_em"
                    for comando in node.cmds
                )
            ):
                adicoes.append(node)

    dependencias: dict[str, set[str]] = {}
    for nome, tabela in tabelas.items():
        referencias: set[str] = set()
        for coluna in tabela.tableElts or ():
            restricoes = (
                coluna.constraints if isinstance(coluna, ast.ColumnDef) else (coluna,)
            )
            for restricao in restricoes or ():
                if isinstance(restricao, ast.Constraint) and restricao.pktable:
                    referencias.add(restricao.pktable.relname)
        dependencias[nome] = referencias - {nome}

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public"
            )
            connection.exec_driver_sql(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public"
            )
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}", public')
            for nome in TopologicalSorter(dependencias).static_order():
                connection.exec_driver_sql(RawStream()(tabelas[nome]))
            for node in adicoes:
                connection.exec_driver_sql(RawStream()(node))
            for node in indices:
                connection.exec_driver_sql(RawStream()(node))
    finally:
        engine.dispose()
    query = {**url.query, "options": f"-csearch_path={schema},public"}
    url_schema = url.set(query=query)
    engine_schema = create_engine(url_schema, hide_parameters=True)
    try:
        if migrar:
            aplicar_migracoes_testes(engine_schema)
    finally:
        engine_schema.dispose()
    print(f"Schema de testes preparado: {schema}", flush=True)
    return url_schema


def assinaturas_migracoes() -> dict[str, str]:
    """Registra as versoes publicadas para verificar estabilidade na execucao."""
    return {
        arquivo.name: hashlib.sha256(arquivo.read_bytes()).hexdigest()
        for arquivo in sorted((RAIZ / "local_server" / "migrations").glob("*.sql"))
    }
