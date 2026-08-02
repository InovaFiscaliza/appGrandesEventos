"""Script temporário para executar o schema SQL e verificar tabelas."""

import sys

sys.path.insert(0, ".")

from app.services.db import get_engine
from sqlalchemy import text

with open("db/schema.sql", "r", encoding="utf-8") as f:
    ddl = f.read()

with get_engine().begin() as conn:
    conn.execute(text(ddl))
print("Schema executado com sucesso!")

with get_engine().connect() as conn:
    rows = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name
        """)).all()
    print("Tabelas criadas:", [r[0] for r in rows])
