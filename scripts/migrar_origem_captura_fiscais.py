"""Aplica as estruturas de banco usadas pela origem e participantes da emissão."""

import sys

from sqlalchemy import text

sys.path.insert(0, ".")

from app.services.db import get_engine


def main() -> None:
    """Cria somente a coluna e a tabela adicionadas ao fluxo de inserção."""
    with get_engine().begin() as connection:
        connection.execute(
            text("ALTER TABLE ocorrencias ADD COLUMN IF NOT EXISTS origem_captura TEXT")
        )
        connection.execute(text("""
                CREATE TABLE IF NOT EXISTS ocorrencia_fiscais (
                    ocorrencia_id BIGINT NOT NULL REFERENCES ocorrencias(id) ON DELETE CASCADE,
                    fiscal_id BIGINT NOT NULL REFERENCES fiscais(id) ON DELETE CASCADE,
                    PRIMARY KEY (ocorrencia_id, fiscal_id)
                )
            """))
        connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ocorrencia_fiscais_fiscal
                ON ocorrencia_fiscais (fiscal_id)
            """))
    print("Migração de origem de captura e fiscais participantes concluída.")


if __name__ == "__main__":
    main()
