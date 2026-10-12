"""Executa a base de regressao sem permitir conexoes com bancos reais.

Executar da raiz: uv run python -m scripts.testar_regressoes
"""

import sys
import unittest
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.pool import ConnectionPoolEntry

MODULOS_SEGUROS = (
    "scripts.testar_login_criar_evento",
    "scripts.testar_consulta_tickets",
    "scripts.testar_fluxos_base",
    "scripts.testar_fluxos_operacionais",
    "scripts.testar_etiquetagem_incidentes",
)


def main() -> int:
    """Retorna falha se um teste falhar ou tentar acessar um banco real."""
    tentativas_conexao: list[str] = []

    def bloquear_conexao(
        dialect: Dialect,
        connection_record: ConnectionPoolEntry,
        connection_args: list[Any],
        connection_params: dict[str, Any],
    ) -> None:
        tentativas_conexao.append(dialect.name)
        raise AssertionError(
            "Banco real bloqueado nos testes. Simule a persistencia com unittest.mock."
        )

    event.listen(Engine, "do_connect", bloquear_conexao)
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(MODULOS_SEGUROS)
        if suite.countTestCases() == 0:
            print("ERRO: nenhum teste encontrado.", file=sys.stderr)
            return 1
        resultado = unittest.TextTestRunner(verbosity=2).run(suite)
        if tentativas_conexao:
            print(
                f"ERRO: {len(tentativas_conexao)} tentativa(s) de conexao real bloqueada(s).",
                file=sys.stderr,
            )
        return int(not resultado.wasSuccessful() or bool(tentativas_conexao))
    finally:
        event.remove(Engine, "do_connect", bloquear_conexao)


if __name__ == "__main__":
    raise SystemExit(main())
