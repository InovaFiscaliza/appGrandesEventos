"""Utilitários de geocodificação para localidades de eventos."""

import asyncio
import json
import logging
import unicodedata
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

UF_POR_ESTADO = {
    "acre": "AC",
    "alagoas": "AL",
    "amapa": "AP",
    "amazonas": "AM",
    "bahia": "BA",
    "ceara": "CE",
    "distrito federal": "DF",
    "espirito santo": "ES",
    "goias": "GO",
    "maranhao": "MA",
    "mato grosso": "MT",
    "mato grosso do sul": "MS",
    "minas gerais": "MG",
    "para": "PA",
    "paraiba": "PB",
    "parana": "PR",
    "pernambuco": "PE",
    "piaui": "PI",
    "rio de janeiro": "RJ",
    "rio grande do norte": "RN",
    "rio grande do sul": "RS",
    "rondonia": "RO",
    "roraima": "RR",
    "santa catarina": "SC",
    "sao paulo": "SP",
    "sergipe": "SE",
    "tocantins": "TO",
}


def _normalizar(valor: object) -> str:
    texto = unicodedata.normalize("NFD", str(valor or ""))
    return (
        "".join(
            caractere for caractere in texto if unicodedata.category(caractere) != "Mn"
        )
        .strip()
        .casefold()
    )


@lru_cache(maxsize=256)
def _consultar_endereco(latitude: float, longitude: float) -> dict[str, str]:
    parametros = urlencode(
        {
            "format": "jsonv2",
            "addressdetails": "1",
            "lat": f"{latitude:.6f}",
            "lon": f"{longitude:.6f}",
        }
    )
    requisicao = Request(
        f"https://nominatim.openstreetmap.org/reverse?{parametros}",
        headers={
            "Accept": "application/json",
            "Accept-Language": "pt-BR",
            "User-Agent": "AppGrandesEventos/1.0",
        },
    )
    with urlopen(requisicao, timeout=5) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    endereco = dados.get("address") or {}
    cidade = next(
        (
            str(endereco.get(chave) or "").strip()
            for chave in ("city", "town", "village", "municipality")
            if endereco.get(chave)
        ),
        "",
    )
    localidade = next(
        (
            str(endereco.get(chave) or "").strip()
            for chave in (
                "amenity",
                "building",
                "tourism",
                "leisure",
                "road",
                "neighbourhood",
                "suburb",
                "city_district",
            )
            if endereco.get(chave)
        ),
        "",
    )
    codigo_estado = (
        str(endereco.get("ISO3166-2-lvl4") or endereco.get("state_code") or "")
        .rsplit("-", 1)[-1]
        .upper()
    )
    uf = (
        codigo_estado
        if len(codigo_estado) == 2
        else UF_POR_ESTADO.get(_normalizar(endereco.get("state")), "")
    )
    return {"cidade": cidade, "uf": uf, "localidade": localidade}


async def obter_endereco_por_coordenadas(
    latitude: object,
    longitude: object,
) -> dict[str, str]:
    """Obtém cidade, UF e localidade pelas coordenadas sem bloquear o servidor."""
    vazio = {"cidade": "", "uf": "", "localidade": ""}
    try:
        latitude_numero = float(latitude)
        longitude_numero = float(longitude)
        if not -90 <= latitude_numero <= 90 or not -180 <= longitude_numero <= 180:
            return vazio
        return await asyncio.to_thread(
            _consultar_endereco,
            round(latitude_numero, 6),
            round(longitude_numero, 6),
        )
    except (OSError, TimeoutError, TypeError, ValueError, json.JSONDecodeError):
        logger.warning(
            "Não foi possível obter o endereço pelas coordenadas do evento.",
            exc_info=True,
        )
        return vazio
