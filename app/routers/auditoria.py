from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import consultar_auditoria_evento
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
ORIGENS_AUDITORIA = ("Evento", "Emissão", "Teste de etiquetagem", "BSR/ERB")


@router.get("/auditoria", response_class=HTMLResponse)
async def get_auditoria(
    request: Request,
    origem: str | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    fiscal: str | None = None,
    palavra: str | None = None,
):
    """Exibe a auditoria consolidada do evento selecionado."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    origem_selecionada = origem if origem in ORIGENS_AUDITORIA else None
    try:
        data_inicio_selecionada = (
            date.fromisoformat(data_inicio) if data_inicio else None
        )
    except ValueError:
        data_inicio_selecionada = None
    try:
        data_fim_selecionada = date.fromisoformat(data_fim) if data_fim else None
    except ValueError:
        data_fim_selecionada = None
    fiscal_selecionado = (fiscal or "").strip()
    palavra_selecionada = (palavra or "").strip()
    auditoria = consultar_auditoria_evento(
        evento_id=evento_id,
        origem=origem_selecionada,
        data_inicio=data_inicio_selecionada,
        data_fim=data_fim_selecionada,
        fiscal=fiscal_selecionado or None,
        palavra=palavra_selecionada or None,
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
            "data_inicio_selecionada": (
                data_inicio_selecionada.isoformat() if data_inicio_selecionada else ""
            ),
            "data_fim_selecionada": (
                data_fim_selecionada.isoformat() if data_fim_selecionada else ""
            ),
            "fiscal_selecionado": fiscal_selecionado,
            "palavra_selecionada": palavra_selecionada,
        },
    )
