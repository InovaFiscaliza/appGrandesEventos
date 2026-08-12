from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.config import MODELOS_EQUIPAMENTO, TITULO_PRINCIPAL
from app.services.postgres import (
    criar_estacao,
    atualizar_estacao,
    listar_estacoes_evento,
    listar_eventos_detalhes,
)
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        **kwargs,
    }


@router.get("/estacoes", response_class=HTMLResponse)
async def get_estacoes(request: Request):
    evento_id = request.query_params.get("evento_id") or request.session.get(
        "spreadsheet_id"
    )
    estacoes = listar_estacoes_evento(int(evento_id)) if evento_id else []
    return templates.TemplateResponse(
        request,
        "estacoes.html",
        _ctx(
            request,
            eventos=listar_eventos_detalhes(),
            evento_id=str(evento_id) if evento_id else "",
            estacoes=estacoes,
            modelos=MODELOS_EQUIPAMENTO,
            flash_error=request.session.pop("flash_error", None),
            flash_success=request.session.pop("flash_success", None),
        ),
    )


@router.post("/estacoes")
async def post_estacao(request: Request):
    form = await request.form()
    evento_id = str(form.get("evento_id", "")).strip()
    nome = str(form.get("nome", "")).strip()
    modelo = str(form.get("modelo", "")).strip()
    local = str(form.get("local", "")).strip()

    if not evento_id.isdigit() or not nome or not modelo or not local:
        request.session["flash_error"] = (
            "Informe evento, identificação, modelo e local da estação."
        )
        return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)

    try:
        criar_estacao(
            evento_id=int(evento_id),
            nome=nome,
            modelo=modelo,
            local=local,
        )
        request.session["flash_success"] = "Estação cadastrada com sucesso."
    except IntegrityError:
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)


@router.post("/estacoes/{estacao_id}/editar")
async def post_editar_estacao(request: Request, estacao_id: int):
    form = await request.form()
    evento_id = str(form.get("evento_id", "")).strip()
    nome = str(form.get("nome", "")).strip()
    modelo = str(form.get("modelo", "")).strip()
    local = str(form.get("local", "")).strip()

    if not evento_id.isdigit() or not nome:
        request.session["flash_error"] = (
            "Informe o evento e a identificação da estação."
        )
        return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)

    try:
        atualizar_estacao(
            evento_id=int(evento_id),
            estacao_id=estacao_id,
            nome=nome,
            modelo=modelo,
            local=local,
        )
        request.session["flash_success"] = "Estação atualizada com sucesso."
    except IntegrityError:
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)
