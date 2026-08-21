"""Atualiza a tabela de municípios com os dados oficiais do IBGE."""

import gzip
import json
import sys
import urllib.request

sys.path.insert(0, ".")

from sqlalchemy import text

from app.services.db import get_engine

URL_IBGE = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def carregar_municipios() -> list[dict]:
    """Baixa e normaliza a lista atual de municípios do IBGE."""
    resposta = urllib.request.urlopen(URL_IBGE, timeout=60)
    conteudo = resposta.read()
    if resposta.headers.get("Content-Encoding") == "gzip":
        conteudo = gzip.decompress(conteudo)
    dados = json.loads(conteudo)
    return [
        {
            "codigo_ibge": int(item["id"]),
            "nome": item["nome"],
            "uf": (
                item["microrregiao"]["mesorregiao"]["UF"]["sigla"]
                if item.get("microrregiao")
                else item["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
            ),
        }
        for item in dados
    ]


municipios = carregar_municipios()
with get_engine().begin() as conn:
    conn.execute(
        text("""
            INSERT INTO municipios (codigo_ibge, nome, uf)
            VALUES (:codigo_ibge, :nome, :uf)
            ON CONFLICT (codigo_ibge) DO UPDATE
            SET nome = EXCLUDED.nome, uf = EXCLUDED.uf
        """),
        municipios,
    )
print(f"Municípios atualizados: {len(municipios)}")
