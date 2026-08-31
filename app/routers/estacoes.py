from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.config import MODELOS_EQUIPAMENTO, TITULO_PRINCIPAL
from app.services.postgres import (
    criar_estacao,
    atualizar_estacao,
    listar_coordenadores_evento,
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


def _usuario_e_coordenador(request: Request, evento_id: int) -> bool:
    """Confirma que o usuário logado coordena o evento selecionado."""
    fiscal_id = request.session.get("fiscal_id")
    return str(
        request.session.get("tipo_usuario", "")
    ).strip().casefold() == "coordenação" or bool(
        fiscal_id
        and str(fiscal_id).isdigit()
        and int(fiscal_id) in listar_coordenadores_evento(evento_id)
    )


def _acesso_negado(request: Request) -> RedirectResponse:
    """Redireciona para o menu quando o usuário não coordena o evento."""
    request.session["flash_error"] = "Acesso restrito aos coordenadores do evento."
    return RedirectResponse("/menu", status_code=303)


@router.get("/estacoes", response_class=HTMLResponse)
async def get_estacoes(request: Request):
    evento_id = request.query_params.get("evento_id") or request.session.get(
        "spreadsheet_id"
    )
    if not evento_id or not str(evento_id).isdigit():
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)
    mostrar_form = request.query_params.get("novo") == "1"
    editar_id = request.query_params.get("editar")
    estacoes = listar_estacoes_evento(int(evento_id)) if evento_id else []
    eventos = listar_eventos_detalhes()
    evento = next((item for item in eventos if str(item["id"]) == str(evento_id)), None)
    estacao_edicao = next(
        (
            estacao
            for estacao in estacoes
            if editar_id and str(estacao["id"]) == str(editar_id)
        ),
        None,
    )
    if editar_id and estacao_edicao is None:
        request.session["flash_error"] = "Estação não encontrada para edição."
        return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)
    mostrar_form = mostrar_form or estacao_edicao is not None
    return templates.TemplateResponse(
        request,
        "estacoes.html",
        _ctx(
            request,
            eventos=eventos,
            evento=evento,
            evento_id=str(evento_id) if evento_id else "",
            estacoes=estacoes,
            modelos=MODELOS_EQUIPAMENTO,
            mostrar_form=mostrar_form,
            estacao_edicao=estacao_edicao,
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
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()

    if not evento_id.isdigit() or not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    if (
        not evento_id.isdigit()
        or not nome
        or not modelo
        or not local
        or not latitude_texto
        or not longitude_texto
    ):
        request.session["flash_error"] = (
            "Informe evento, identificação, modelo, local, latitude e longitude da estação."
        )
        return RedirectResponse(
            f"/estacoes?evento_id={evento_id}&novo=1", status_code=303
        )

    erro = False
    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        criar_estacao(
            evento_id=int(evento_id),
            nome=nome,
            modelo=modelo,
            local=local,
            latitude=latitude,
            longitude=longitude,
        )
        request.session["flash_success"] = "Estação cadastrada com sucesso."
    except IntegrityError:
        erro = True
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    except ValueError:
        erro = True
        request.session["flash_error"] = "Informe latitude e longitude válidas."
    sufixo = "&novo=1" if erro else ""
    return RedirectResponse(f"/estacoes?evento_id={evento_id}{sufixo}", status_code=303)


@router.post("/estacoes/{estacao_id}/editar")
async def post_editar_estacao(request: Request, estacao_id: int):
    form = await request.form()
    evento_id = str(form.get("evento_id", "")).strip()
    nome = str(form.get("nome", "")).strip()
    modelo = str(form.get("modelo", "")).strip()
    local = str(form.get("local", "")).strip()
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()

    if not evento_id.isdigit() or not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    if not evento_id.isdigit() or not nome or not modelo or not local:
        request.session["flash_error"] = (
            "Informe evento, identificação, modelo e local da estação."
        )
        return RedirectResponse(
            f"/estacoes?evento_id={evento_id}&editar={estacao_id}", status_code=303
        )

    erro = False
    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        atualizar_estacao(
            evento_id=int(evento_id),
            estacao_id=estacao_id,
            nome=nome,
            modelo=modelo,
            local=local,
            latitude=latitude,
            longitude=longitude,
        )
        request.session["flash_success"] = "Estação atualizada com sucesso."
    except IntegrityError:
        erro = True
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    except ValueError:
        erro = True
        request.session["flash_error"] = "Informe latitude e longitude válidas."
    sufixo = f"&editar={estacao_id}" if erro else ""
    return RedirectResponse(f"/estacoes?evento_id={evento_id}{sufixo}", status_code=303)
