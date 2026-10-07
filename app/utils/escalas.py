from datetime import date, datetime, time


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
