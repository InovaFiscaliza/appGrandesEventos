"""Estrutura os dados de contato dos registros de teste e etiquetagem."""

import sys

from sqlalchemy import text

sys.path.insert(0, ".")

from app.services.db import get_engine


def main() -> None:
    """Cria os campos estruturados e preserva o responsável legado."""
    with get_engine().begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE testes_etiquetagem "
                "ADD COLUMN IF NOT EXISTS responsavel_contato TEXT"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS telefone TEXT"
            )
        )
        connection.execute(
            text("ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS email TEXT")
        )
        connection.execute(text("""
            UPDATE testes_etiquetagem
            SET responsavel_contato = contato
            WHERE responsavel_contato IS NULL
              AND NULLIF(trim(contato), '') IS NOT NULL
        """))
    print("Migração dos contatos estruturados concluída.")


if __name__ == "__main__":
    main()
