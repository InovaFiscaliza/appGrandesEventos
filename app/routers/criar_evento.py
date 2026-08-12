from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.services.postgres import (
    atualizar_evento,
    criar_evento,
    listar_estacoes_evento,
    listar_eventos_detalhes,
    obter_evento,
)
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

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


@router.get("/criar-evento", response_class=HTMLResponse)
async def get_criar_evento(request: Request):
    editar_id = request.query_params.get("editar")
    evento = None
    estacoes = []
    if editar_id and editar_id.isdigit():
        evento = obter_evento(int(editar_id))
        if evento:
            estacoes = listar_estacoes_evento(int(editar_id))
    if editar_id and evento is None:
        request.session["flash_error"] = "Evento não encontrado."
        return RedirectResponse("/criar-evento", status_code=303)

    return templates.TemplateResponse(
        request,
        "criar_evento.html",
        _ctx(
            request,
            evento=evento,
            estacoes=estacoes,
            eventos=listar_eventos_detalhes(),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/criar-evento")
async def post_criar_evento(request: Request):
    form = await request.form()
    nome = str(form.get("nome", "")).strip()
    local = str(form.get("local", "")).strip()
    acao_fiscalizacao = str(form.get("acao_fiscalizacao", "")).strip()
    processo_sei = str(form.get("processo_sei", "")).strip()
    coordenador_responsavel = str(form.get("coordenador_responsavel", "")).strip()
    observacoes = str(form.get("observacoes", "")).strip()
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()
    if not nome:
        request.session["flash_error"] = "Informe o nome do evento."
        return RedirectResponse("/criar-evento", status_code=303)

    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        evento_id = criar_evento(
            nome=nome,
            latitude=latitude,
            longitude=longitude,
            local=local or None,
            acao_fiscalizacao=acao_fiscalizacao or None,
            processo_sei=processo_sei or None,
            coordenador_responsavel=coordenador_responsavel or None,
            observacoes=observacoes or None,
        )
    except ValueError:
        request.session["flash_error"] = "Latitude ou longitude inválida."
        return RedirectResponse("/criar-evento", status_code=303)
    except IntegrityError:
        request.session["flash_error"] = "Já existe um evento com esse nome."
        return RedirectResponse("/criar-evento", status_code=303)

    request.session["evento_nome"] = nome
    request.session["spreadsheet_id"] = str(evento_id)
    request.session["flash_success"] = "Evento criado com sucesso."
    return RedirectResponse("/menu", status_code=303)


@router.post("/criar-evento/{evento_id}/editar")
async def post_editar_evento(request: Request, evento_id: int):
    form = await request.form()
    nome = str(form.get("nome", "")).strip()
    local = str(form.get("local", "")).strip()
    acao_fiscalizacao = str(form.get("acao_fiscalizacao", "")).strip()
    processo_sei = str(form.get("processo_sei", "")).strip()
    coordenador_responsavel = str(form.get("coordenador_responsavel", "")).strip()
    observacoes = str(form.get("observacoes", "")).strip()
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()

    if not nome:
        request.session["flash_error"] = "Informe o nome do evento."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)

    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        atualizar_evento(
            evento_id,
            nome,
            latitude,
            longitude,
            local or None,
            acao_fiscalizacao or None,
            processo_sei or None,
            coordenador_responsavel or None,
            observacoes or None,
        )
    except ValueError:
        request.session["flash_error"] = "Latitude ou longitude inválida."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)
    except IntegrityError:
        request.session["flash_error"] = "Já existe um evento com esse nome."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)

    if str(request.session.get("spreadsheet_id")) == str(evento_id):
        request.session["evento_nome"] = nome
    request.session["flash_success"] = "Evento atualizado com sucesso."
    return RedirectResponse("/criar-evento", status_code=303)
