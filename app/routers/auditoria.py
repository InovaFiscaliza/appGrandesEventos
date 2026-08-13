from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import consultar_auditoria_evento
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
ORIGENS_AUDITORIA = ("Emissão", "Teste de etiquetagem", "BSR/ERB")


@router.get("/auditoria", response_class=HTMLResponse)
async def get_auditoria(request: Request, origem: str | None = None):
    """Exibe a auditoria consolidada do evento selecionado."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    origem_selecionada = origem if origem in ORIGENS_AUDITORIA else None
    auditoria = consultar_auditoria_evento(
        evento_id=evento_id,
        origem=origem_selecionada,
    )
    return templates.TemplateResponse(
        request,
        "auditoria.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
            "auditoria": auditoria,
            "origens": ORIGENS_AUDITORIA,
            "origem_selecionada": origem_selecionada or "",
        },
    )
