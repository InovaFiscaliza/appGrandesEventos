from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import buscar_planilhas
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_selecao(request: Request):
    if request.session.get("spreadsheet_id"):
        return RedirectResponse("/menu", status_code=302)

    eventos = buscar_planilhas()

    return templates.TemplateResponse(
        request,
        "selecao.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64": _img_b64("anatel.png"),
            "eventos": eventos,
            "flash_error": request.session.pop("flash_error", None),
        },
    )


@router.post("/", response_class=HTMLResponse)
async def post_selecao(request: Request):
    form = await request.form()
    evento_key = form.get("evento_key", "")

    if not evento_key or "|||" not in evento_key:
        request.session["flash_error"] = "Selecione um evento válido."
        return RedirectResponse("/", status_code=303)

    nome, ev_id = evento_key.split("|||", 1)
    request.session["evento_nome"] = nome
    request.session["spreadsheet_id"] = ev_id
    return RedirectResponse("/menu", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
