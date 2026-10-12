"""Executa persistencia e, opcionalmente, navegador em banco exclusivo de testes."""

import argparse
import os
import sys
import unittest

from scripts.ambiente_testes import preparar_banco


def main() -> int:
    """Prepara schema sintetico antes de importar qualquer modulo da aplicacao."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--navegador", action="store_true")
    args = parser.parse_args()
    valor = os.environ.get("TEST_DATABASE_URL")
    if not valor:
        print(
            "ERRO: defina TEST_DATABASE_URL para o PostgreSQL exclusivo de testes.",
            file=sys.stderr,
        )
        return 1
    url = preparar_banco(valor)
    os.environ["DATABASE_URL"] = url.render_as_string(hide_password=False)
    modulos = ["scripts.testar_persistencia"]
    if args.navegador:
        modulos.append("scripts.testar_navegador")
    suite = unittest.TestLoader().loadTestsFromNames(modulos)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    return int(not resultado.wasSuccessful() or resultado.testsRun == 0)


if __name__ == "__main__":
    raise SystemExit(main())
