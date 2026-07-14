"""
Script de backup via pg_dump executado dentro do container PostgreSQL.

Utiliza Podman para executar pg_dump no container postgres_appeventos
e salva o arquivo .sql no diretório bd_backup/.

Uso:
    uv run python scripts/backup_db.py
    uv run python scripts/backup_db.py --output bd_backup/meu_backup.sql
    uv run python scripts/backup_db.py --container postgres_appeventos
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")

from app.services.db import _get_database_url

# Nome padrao do container definido via Podman
CONTAINER_PADRAO = "postgres_appeventos"


def _container_engine() -> str | None:
    """Retorna podman se disponivel, ou docker como fallback."""
    for cmd in ["podman", "docker"]:
        try:
            subprocess.run(
                [cmd, "ps"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            # Se chegou aqui sem FileNotFoundError, o comando existe
            # Verificar se o container alvo esta rodando
            check = subprocess.run(
                [
                    cmd,
                    "ps",
                    "--filter",
                    f"name={CONTAINER_PADRAO}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if CONTAINER_PADRAO in check.stdout.strip():
                return cmd
        except FileNotFoundError:
            continue
    return None


def backup_database(
    output_path: str | None = None,
    container: str | None = None,
) -> str:
    """
    Executa pg_dump dentro do container PostgreSQL via Podman/Docker.

    Retorna o caminho absoluto do arquivo .sql gerado.
    """
    container = container or CONTAINER_PADRAO

    # Descobrir engine de container
    engine = _container_engine()
    if not engine:
        msg = (
            "Nenhum container runtime encontrado (podman/docker)!\n\n"
            "Verifique se o Podman esta instalado e o container "
            f"'{container}' esta rodando."
        )
        raise RuntimeError(msg)

    print(f"Engine: {engine}")
    print(f"Container: {container}")

    # Extrair dados de conexao da URL
    db_url = _get_database_url()
    # postgresql+psycopg://appeventos:appeventos@localhost:5432/appeventos
    resto = db_url.split("://", 1)[1]
    creds, hostpart = resto.rsplit("@", 1)
    usuario, senha = creds.split(":", 1)
    host_port, banco = hostpart.split("/", 1)
    host = host_port.split(":")[0] if ":" in host_port else host_port
    porta = host_port.split(":")[1] if ":" in host_port else "5432"

    # Caminho de saida
    if output_path:
        out = Path(output_path)
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("bd_backup")
        backup_dir.mkdir(parents=True, exist_ok=True)
        out = backup_dir / f"backup_{timestamp}.sql"

    # Montar comando: podman exec -e PGPASSWORD=... CONTAINER pg_dump ...
    cmd = [
        engine,
        "exec",
        "-i",
        "-e",
        f"PGPASSWORD={senha}",
        container,
        "pg_dump",
        "--host",
        host,
        "--port",
        porta,
        "--username",
        usuario,
        "--dbname",
        banco,
        "--format",
        "p",  # plain SQL
        "--create",  # CREATE DATABASE
        "--clean",  # DROP antes de CREATE
        "--if-exists",  # so DROP se existir
        "--no-owner",  # evita erros de owner
        "--no-privileges",  # evita erros de permissao
    ]

    print(f"Executando pg_dump no container...")
    print(f"  Host: {host}:{porta}")
    print(f"  Banco: {banco}")
    print(f"  Usuario: {usuario}")
    print(f"  Saida: {out.resolve()}")
    print()

    # Executar e capturar stdout (pg_dump manda o dump pra stdout)
    with open(out, "w", encoding="utf-8") as f:
        result = subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )

    # Verificar resultado
    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Se ja criou o arquivo parcial, remover
        if out.exists():
            out.unlink()
        raise RuntimeError(f"pg_dump falhou (codigo {result.returncode}):\n{stderr}")

    # Mostrar warnings do stderr
    if result.stderr and result.stderr.strip():
        warnings = [l for l in result.stderr.splitlines() if "warn" in l.lower()]
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  {w.strip()}")

    print(f"\nBackup concluido: {out.resolve()}")
    return str(out.resolve())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backup do banco AppEventos via pg_dump no container"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Caminho do arquivo de saida (padrao: bd_backup/backup_<timestamp>.sql)",
    )
    parser.add_argument(
        "--container",
        "-c",
        default=CONTAINER_PADRAO,
        help=f"Nome do container PostgreSQL (padrao: {CONTAINER_PADRAO})",
    )
    args = parser.parse_args()

    try:
        backup_database(args.output, args.container)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
