from calendar import Calendar
from datetime import date, datetime, time


def montar_calendario_escalas(escalas: list[dict], mes: str = "") -> dict:
    """Organiza as escalas por dia e calcula a navegacao mensal."""
    por_dia: dict[date, list[dict]] = {}
    for escala in escalas:
        data_trabalho = _converter_data(escala.get("data_trabalho"))
        if data_trabalho is not None:
            por_dia.setdefault(data_trabalho, []).append(escala)
    try:
        referencia = date.fromisoformat(f"{mes}-01")
    except ValueError:
        referencia = min(por_dia) if por_dia else date.today()
    ano, numero_mes = referencia.year, referencia.month
    nomes_meses = (
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    )
    semanas = []
    total = 0
    for semana in Calendar().monthdayscalendar(ano, numero_mes):
        dias = []
        for numero_dia in semana:
            data_dia = date(ano, numero_mes, numero_dia) if numero_dia else None
            jornadas = por_dia.get(data_dia, []) if data_dia else []
            total += len(jornadas)
            dias.append({"numero": numero_dia, "data": data_dia, "escalas": jornadas})
        semanas.append(dias)
    anterior = (
        (f"{ano - 1:04d}-12" if numero_mes == 1 else f"{ano:04d}-{numero_mes - 1:02d}")
        if (ano, numero_mes) != (1, 1)
        else None
    )
    proximo = (
        (f"{ano + 1:04d}-01" if numero_mes == 12 else f"{ano:04d}-{numero_mes + 1:02d}")
        if (ano, numero_mes) != (9999, 12)
        else None
    )
    return {
        "mes": f"{ano:04d}-{numero_mes:02d}",
        "titulo": f"{nomes_meses[numero_mes - 1]} de {ano}",
        "anterior": anterior,
        "proximo": proximo,
        "semanas": semanas,
        "total": total,
        "hoje": date.today(),
    }


def _converter_data(valor: object) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor[:10])
        except ValueError:
            return None
    return None


def _converter_hora_segundos(valor: object) -> int | None:
    if isinstance(valor, time):
        return valor.hour * 3600 + valor.minute * 60 + valor.second
    if isinstance(valor, str):
        try:
            hora = time.fromisoformat(valor)
        except ValueError:
            return None
        return hora.hour * 3600 + hora.minute * 60 + hora.second
    return None


def buscar_escala_sobreposta(
    escalas: list[dict],
    fiscal_id: int,
    data_trabalho: object,
    turno_inicio: object,
    turno_fim: object,
) -> dict | None:
    """Retorna escala do fiscal que se sobrepõe ao novo turno, se houver."""
    data_nova = _converter_data(data_trabalho)
    inicio_novo = _converter_hora_segundos(turno_inicio)
    fim_novo = _converter_hora_segundos(turno_fim)
    if data_nova is None or inicio_novo is None or fim_novo is None:
        return None

    fim_novo_absoluto = fim_novo + (24 * 60 * 60 if fim_novo < inicio_novo else 0)
    for escala in escalas:
        if int(escala["fiscal_id"]) != int(fiscal_id):
            continue

        data_existente = _converter_data(escala.get("data_trabalho"))
        inicio_existente = _converter_hora_segundos(escala.get("turno_inicio"))
        fim_existente = _converter_hora_segundos(escala.get("turno_fim"))
        if data_existente is None or inicio_existente is None or fim_existente is None:
            continue

        deslocamento_dias = (data_existente - data_nova).days
        inicio_existente_absoluto = deslocamento_dias * 24 * 60 * 60 + inicio_existente
        fim_existente_absoluto = deslocamento_dias * 24 * 60 * 60 + fim_existente
        if fim_existente < inicio_existente:
            fim_existente_absoluto += 24 * 60 * 60

        if (
            inicio_novo < fim_existente_absoluto
            and inicio_existente_absoluto < fim_novo_absoluto
        ):
            return escala
    return None


def resumir_horas_escalas(escalas: list[dict]) -> list[dict]:
    """Agrupa horas alocadas e turnos incompletos por mês e fiscal."""
    totais: dict[tuple[int, int, int], dict] = {}
    for escala in escalas:
        data_trabalho = _converter_data(escala.get("data_trabalho"))
        if data_trabalho is None:
            continue

        fiscal_id = int(escala["fiscal_id"])
        chave = (data_trabalho.year, data_trabalho.month, fiscal_id)
        total = totais.setdefault(
            chave,
            {
                "mes": f"{data_trabalho.month:02d}/{data_trabalho.year}",
                "fiscal_id": fiscal_id,
                "fiscal_nome": escala.get("fiscal_nome") or "Fiscal não informado",
                "total_segundos": 0,
                "turnos_incompletos": 0,
            },
        )

        inicio = _converter_hora_segundos(escala.get("turno_inicio"))
        fim = _converter_hora_segundos(escala.get("turno_fim"))
        if inicio is None or fim is None:
            total["turnos_incompletos"] += 1
            continue

        total["total_segundos"] += (fim - inicio) % (24 * 60 * 60)

    resumos = []
    for (ano, mes, _), total in sorted(
        totais.items(),
        key=lambda item: (item[0][0], item[0][1], item[1]["fiscal_nome"].casefold()),
    ):
        resumos.append(
            {
                "mes": total["mes"],
                "fiscal_id": total["fiscal_id"],
                "fiscal_nome": total["fiscal_nome"],
                "total_minutos": round(total["total_segundos"] / 60),
                "turnos_incompletos": total["turnos_incompletos"],
            }
        )
    return resumos
