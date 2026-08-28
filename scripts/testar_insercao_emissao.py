"""Cria uma emissão de teste e confirma sua persistência no PostgreSQL."""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import text

sys.path.insert(0, ".")

from app.services.db import get_engine
from app.services.postgres import (
    buscar_planilhas,
    inserir_emissao_I_W,
    listar_fiscais,
    listar_fiscais_evento,
    obter_fuso_horario_evento,
)


def main() -> None:
    """Executa um cadastro real usando o mesmo serviço da tela de inserção."""
    eventos = buscar_planilhas()
    if not eventos:
        raise RuntimeError("Não há evento disponível para o teste.")

    evento_id = int(next(iter(eventos.values())))
    fiscais_ids = set(listar_fiscais_evento(evento_id))
    fiscal = next(
        (item for item in listar_fiscais() if int(item["id"]) in fiscais_ids),
        None,
    )
    if fiscal is None:
        raise RuntimeError("O evento selecionado não possui fiscal vinculado.")

    agora = datetime.now(ZoneInfo(obter_fuso_horario_evento(evento_id)))
    ocorrencia_id = inserir_emissao_I_W(
        evento_id=evento_id,
        dados_formulario={
            "Dia": agora.date(),
            "Hora": agora.time().replace(microsecond=0),
            "Fiscal": fiscal["nome"],
            "Local/Região": "Teste automatizado",
            "Frequência em MHz": 433.925,
            "Largura em kHz": 25.0,
            "Faixa de Frequência": "SLP",
            "Identificação": "Não identificado",
            "UTE?": False,
            "Processo SEI ou Ato UTE": "",
            "Observações/Detalhes/Contatos": "Teste automatizado de inserção",
            "Interferente?": "Não",
            "Situação": "Concluído",
            "Estação ID": None,
            "Origem da captura": "Analisador de espectro - campo",
            "Fiscais participantes": [],
        },
    )
    if not isinstance(ocorrencia_id, int):
        raise RuntimeError("O serviço não retornou o ID da emissão criada.")

    with get_engine().connect() as connection:
        emissao = (
            connection.execute(
                text("""
                SELECT id, fiscal, origem_captura, frequencia_mhz, largura_khz, situacao
                FROM ocorrencias
                WHERE id = :ocorrencia_id AND evento_id = :evento_id
            """),
                {"ocorrencia_id": ocorrencia_id, "evento_id": evento_id},
            )
            .mappings()
            .one_or_none()
        )
    if emissao is None:
        raise RuntimeError("A emissão criada não foi encontrada no banco.")

    print("Inserção validada:", dict(emissao))


if __name__ == "__main__":
    main()
