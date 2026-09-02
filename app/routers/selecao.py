from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import (
    buscar_planilhas,
    listar_fiscais,
    listar_fiscais_evento,
    registrar_login_evento,
)
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_selecao(request: Request):
    if request.session.get("spreadsheet_id") and request.session.get("fiscal_id"):
        return RedirectResponse("/menu", status_code=302)

    eventos = getattr(request.state, "eventos", None)
    if eventos is None:
        eventos = buscar_planilhas()

    fiscais = listar_fiscais()

    return templates.TemplateResponse(
        request,
        "selecao.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64": _img_b64("anatel.png"),
            "eventos": eventos,
            "fiscais": fiscais,
            "flash_error": request.session.pop("flash_error", None),
        },
    )


@router.post("/", response_class=HTMLResponse)
async def post_selecao(request: Request):
    form = await request.form()
    evento_key = form.get("evento_key", "")
    fiscal_id = str(form.get("fiscal_id", "")).strip()
    senha = str(form.get("senha", "")).strip()
    papel = str(form.get("papel", "")).strip()

    if not evento_key or "|||" not in evento_key:
        request.session["flash_error"] = "Selecione um evento válido."
        return RedirectResponse("/", status_code=303)

    nome, ev_id = evento_key.split("|||", 1)

    # Troca de evento via cabeçalho (quando já existe login válido na sessão).
    if (not fiscal_id and not senha) and request.session.get("fiscal_id"):
        request.session["evento_nome"] = nome
        request.session["spreadsheet_id"] = ev_id
        return RedirectResponse("/menu", status_code=303)

    if not fiscal_id or not fiscal_id.isdigit():
        request.session["flash_error"] = "Selecione um usuário válido."
        return RedirectResponse("/", status_code=303)

    if not senha:
        request.session["flash_error"] = "Informe a senha."
        return RedirectResponse("/", status_code=303)

    fiscais_ids_evento = {int(fid) for fid in listar_fiscais_evento(int(ev_id))}
    fiscal_id_int = int(fiscal_id)
    if fiscais_ids_evento and fiscal_id_int not in fiscais_ids_evento:
        request.session["flash_error"] = (
            "Usuário não está vinculado ao evento selecionado."
        )
        return RedirectResponse("/", status_code=303)

    fiscal = next(
        (item for item in listar_fiscais() if int(item["id"]) == fiscal_id_int), None
    )
    if fiscal is None:
        request.session["flash_error"] = "Usuário selecionado não foi encontrado."
        return RedirectResponse("/", status_code=303)
    if papel not in (fiscal.get("papeis") or []):
        request.session["flash_error"] = "Selecione um papel permitido para o usuário."
        return RedirectResponse("/", status_code=303)

    request.session["evento_nome"] = nome
    request.session["spreadsheet_id"] = ev_id
    request.session["fiscal_id"] = fiscal_id_int
    request.session["fiscal_nome"] = fiscal["nome"]
    request.session["fiscal_local_anatel"] = str(
        fiscal.get("local_anatel") or ""
    ).strip()
    request.session["fiscal_funcao_evento"] = papel
    request.session["tipo_usuario"] = papel.lower()
    registrar_login_evento(
        evento_id=int(ev_id),
        usuario_fiscal=str(fiscal["nome"]),
    )
    return RedirectResponse("/menu", status_code=303)


@router.get("/api/eventos")
async def api_eventos():
    """Retorna eventos disponíveis para o combo da barra superior."""
    eventos = buscar_planilhas()
    return JSONResponse(
        [
            {"nome": nome, "key": f"{nome}|||{evento_id}"}
            for nome, evento_id in eventos.items()
        ]
    )


@router.get("/api/eventos/{evento_id}/fiscais")
async def api_fiscais_evento(evento_id: int):
    """Retorna fiscais vinculados ao evento para a tela de login."""
    fiscais_evento_ids = {int(fid) for fid in listar_fiscais_evento(int(evento_id))}
    fiscais = [
        fiscal for fiscal in listar_fiscais() if int(fiscal["id"]) in fiscais_evento_ids
    ]
    return JSONResponse(
        [
            {
                "id": fiscal["id"],
                "nome": fiscal["nome"],
                "local_anatel": fiscal["local_anatel"],
                "papeis": fiscal.get("papeis") or [],
            }
            for fiscal in fiscais
        ]
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
