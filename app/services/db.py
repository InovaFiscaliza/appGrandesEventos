"""
Conexão com o banco PostgreSQL via SQLAlchemy.

A string de conexão é lida de:
  1. Variável de ambiente DATABASE_URL (prioritário), ou
  2. Arquivo .streamlit/secrets.toml, seção [database], chave url

Uso:
    from app.services.db import get_engine, SessionLocal
    with SessionLocal() as session:
        ...
"""

import os
import tomllib
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _get_database_url() -> str:
    # 1. Tentar variável de ambiente
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    # 2. Tentar secrets.toml (padrão legado do Streamlit)
    secrets_path = Path(".streamlit/secrets.toml")
    if secrets_path.exists():
        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)
        url = secrets.get("database", {}).get("url")
        if url:
            return url
    # 3. Fallback para desenvolvimento local
    return "postgresql+psycopg://appeventos:appeventos@localhost:5432/appeventos"


_engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,  # verifica conexão antes de usar
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=_engine, autoflush=False, future=True)


def get_engine():
    return _engine
