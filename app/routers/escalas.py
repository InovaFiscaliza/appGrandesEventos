from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import listar_escalas_evento
from app.utils.escalas import resumir_horas_escalas
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

    escalas = listar_escalas_evento(int(evento_id))
    visualizacao = request.query_params.get("visualizacao", "todas")
    if visualizacao not in {"todas", "proprias", "outros"}:
        visualizacao = "todas"

    fiscal_id_atual = int(fiscal_id)
    if visualizacao == "proprias":
        escalas = [
            escala for escala in escalas if int(escala["fiscal_id"]) == fiscal_id_atual
        ]
    elif visualizacao == "outros":
        escalas = [
            escala for escala in escalas if int(escala["fiscal_id"]) != fiscal_id_atual
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
            "fiscal_id_atual": fiscal_id_atual,
            "visualizacao": visualizacao,
        },
    )
