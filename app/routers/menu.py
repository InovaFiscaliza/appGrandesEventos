from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import (
    carregar_pendencias_abordagem_pendentes,
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    get_city_map_url,
)
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/menu", response_class=HTMLResponse)
async def get_menu(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    df_painel = carregar_pendencias_painel_mapeadas(evento_id=sp_id)
    df_abord = carregar_pendencias_abordagem_pendentes(evento_id=sp_id)
    df_estac = carregar_pendencias_todas_estacoes(evento_id=sp_id)
    link_mapa = get_city_map_url(evento_id=sp_id)

    total = sum(len(df) for df in [df_painel, df_abord, df_estac] if df is not None)

    return templates.TemplateResponse(
        request,
        "menu.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
            "total": total,
            "link_mapa": link_mapa,
            "flash_success": request.session.pop("flash_success", None),
            "flash_error": request.session.pop("flash_error", None),
        },
    )
