from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/teste_etiquetagem", response_class=HTMLResponse)
async def get_teste_etiquetagem(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        request,
        "teste_etiquetagem.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
        },
    )
