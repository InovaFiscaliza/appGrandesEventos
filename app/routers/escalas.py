from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import (
    listar_escalas_evento,
    listar_fiscais,
    listar_fiscais_evento,
)
from app.utils.escalas import montar_calendario_escalas, resumir_horas_escalas
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/escalas", response_class=HTMLResponse)
async def get_escalas(request: Request):
    """Exibe as escalas do evento selecionado para os fiscais do evento."""
    evento_id = request.session.get("spreadsheet_id")
    fiscal_id = request.session.get("fiscal_id")
    if not evento_id or not fiscal_id:
        return RedirectResponse("/", status_code=302)

    evento_id_int = int(evento_id)
    escalas = listar_escalas_evento(evento_id_int)
    fiscais_com_escala = sorted({int(escala["fiscal_id"]) for escala in escalas})
    cores_fiscais = {
        fiscal: f"hsl({indice * 360 / len(fiscais_com_escala)} 65% 90%)"
        for indice, fiscal in enumerate(fiscais_com_escala)
    }
    fiscais_ids_evento = set(listar_fiscais_evento(evento_id_int))
    fiscais = [
        fiscal for fiscal in listar_fiscais() if int(fiscal["id"]) in fiscais_ids_evento
    ]
    visualizacao = request.query_params.get("visualizacao", "todas")
    visualizacoes_validas = {"todas", "proprias"} | {
        str(fiscal["id"]) for fiscal in fiscais
    }
    if visualizacao not in visualizacoes_validas:
        visualizacao = "todas"

    fiscal_id_atual = int(fiscal_id)
    if visualizacao == "proprias":
        escalas = [
            escala for escala in escalas if int(escala["fiscal_id"]) == fiscal_id_atual
        ]
    elif visualizacao.isdigit():
        fiscal_id_selecionado = int(visualizacao)
        escalas = [
            escala
            for escala in escalas
            if int(escala["fiscal_id"]) == fiscal_id_selecionado
        ]
    resumo_horas = resumir_horas_escalas(escalas)

    return templates.TemplateResponse(
        request,
        "escalas.html",
        {
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
            "escalas": escalas,
            "resumo_horas": resumo_horas,
            "cores_fiscais": cores_fiscais,
            "fiscais": fiscais,
            "fiscal_id_atual": fiscal_id_atual,
            "visualizacao": visualizacao,
            "calendario": montar_calendario_escalas(
                escalas, request.query_params.get("mes", "")
            ),
        },
    )
