"""Aplica migracoes versionadas, em uma transacao, ao banco de preparacao."""

import hashlib
import os
import re
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def aplicar_migracoes(directory: Path) -> None:
    """Registra cada migracao uma vez e rejeita alteracoes no historico."""
    files = sorted(directory.glob("*.sql"))
    if not files:
        raise RuntimeError("O pacote nao possui migracoes de estrutura.")
    migrations = {}
    for path in files:
        if not re.fullmatch(r"\d{4}_[a-z0-9_]+\.sql", path.name):
            raise RuntimeError(f"Nome de migracao invalido: {path.name}")
        content = path.read_bytes()
        migrations[path.name] = (hashlib.sha256(content).hexdigest(), content.decode("utf-8-sig"))

    database = os.environ["DEPLOY_CHECK_DATABASE"]
    if not re.fullmatch(r"appeventos_stage_\d{14}_[a-f0-9]{8}", database):
        raise RuntimeError("Execute as migracoes apenas no banco temporario do instalador.")
    url = make_url(os.environ["DATABASE_URL"]).set(database=database)
    engine = create_engine(url, connect_args={"connect_timeout": 5}, hide_parameters=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_xact_lock(1937001)"))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS public.app_schema_migrations (
                    version TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """))
            applied = dict(connection.execute(text(
                "SELECT version, sha256 FROM public.app_schema_migrations ORDER BY version"
            )).tuples().all())
            for version, checksum in applied.items():
                if version not in migrations or migrations[version][0] != checksum:
                    raise RuntimeError(f"Migracao aplicada foi removida ou alterada: {version}")
            pending = [name for name in migrations if name not in applied]
            if applied and any(name < max(applied) for name in pending):
                raise RuntimeError("Novas migracoes devem vir depois das versoes ja aplicadas.")
            for version in pending:
                checksum, sql = migrations[version]
                print(f"Aplicando migracao {version}", flush=True)
                connection.exec_driver_sql(sql)
                connection.execute(text("""
                    INSERT INTO public.app_schema_migrations (version, sha256)
                    VALUES (:version, :checksum)
                """), {"version": version, "checksum": checksum})
        print(f"Migracoes concluidas: {len(pending)} nova(s).", flush=True)
    finally:
        engine.dispose()


if __name__ == "__main__":
    aplicar_migracoes(Path(__file__).parent / "migrations")
