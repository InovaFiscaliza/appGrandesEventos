from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.services.postgres import (
    atualizar_evento,
    criar_evento,
    listar_estacoes_evento,
    listar_eventos_detalhes,
    obter_evento,
    atualizar_unidades_evento,
    listar_unidades_evento,
    listar_unidades_executantes,
    listar_fiscais,
    criar_fiscal,
    listar_fiscais_evento,
    listar_coordenadores_evento,
    registrar_auditoria_evento,
    obter_snapshot_auditoria_evento,
    atualizar_fiscais_evento,
    excluir_fiscal,
    listar_municipios,
    listar_ufs_municipios,
    cidade_pertence_uf,
)
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _usuario_e_coordenador(request: Request) -> bool:
    """Confirma se o fiscal logado coordena o evento selecionado."""
    evento_id = request.session.get("spreadsheet_id")
    fiscal_id = request.session.get("fiscal_id")
    return str(
        request.session.get("tipo_usuario", "")
    ).strip().casefold() == "coordenação" or bool(
        evento_id
        and str(evento_id).isdigit()
        and fiscal_id
        and str(fiscal_id).isdigit()
        and int(fiscal_id) in listar_coordenadores_evento(int(evento_id))
    )


def _acesso_negado(request: Request) -> RedirectResponse:
    """Redireciona para o menu quando o usuário não é coordenador."""
    request.session["flash_error"] = "Acesso restrito aos coordenadores do evento."
    return RedirectResponse("/menu", status_code=303)


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
    if not _usuario_e_coordenador(request):
        return _acesso_negado(request)

    editar_id = request.query_params.get("editar")
    evento = None
    estacoes = []
    if editar_id and editar_id.isdigit():
        evento = obter_evento(int(editar_id))
        if evento:
            evento["unidades_executantes"] = listar_unidades_evento(int(editar_id))
            evento["fiscais"] = listar_fiscais_evento(int(editar_id))
            evento["coordenadores"] = listar_coordenadores_evento(int(editar_id))
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
            municipios=listar_municipios(),
            ufs=listar_ufs_municipios(),
            unidades_executantes=listar_unidades_executantes(),
            fiscais=listar_fiscais(),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/fiscais")
async def post_criar_fiscal(request: Request):
    """Cadastra um fiscal globalmente para uso em todos os eventos."""
    if not _usuario_e_coordenador(request):
        return JSONResponse(
            {"ok": False, "mensagem": "Acesso restrito aos coordenadores do evento."},
            status_code=403,
        )

    form = await request.form()
    nome = str(form.get("nome", "")).strip()
    local_anatel = str(form.get("local_anatel", "")).strip()
    funcao_evento = str(form.get("funcao_evento", "")).strip()
    funcoes = {"Coordenação", "Abordagem", "Monitoração"}
    unidades = {item["sigla"] for item in listar_unidades_executantes()}
    if not nome or local_anatel not in unidades or funcao_evento not in funcoes:
        return JSONResponse(
            {"ok": False, "mensagem": "Preencha os dados do fiscal corretamente."},
            status_code=400,
        )
    try:
        fiscal_id = criar_fiscal(nome, local_anatel, funcao_evento)
    except IntegrityError:
        return JSONResponse(
            {"ok": False, "mensagem": "Este fiscal já está cadastrado."},
            status_code=409,
        )
    fiscal = next(item for item in listar_fiscais() if item["id"] == fiscal_id)
    return JSONResponse({"ok": True, "fiscal": fiscal})


@router.post("/fiscais/{fiscal_id}/excluir")
async def post_excluir_fiscal(request: Request, fiscal_id: int):
    """Exclui um fiscal da lista global."""
    if not _usuario_e_coordenador(request):
        return JSONResponse(
            {"ok": False, "mensagem": "Acesso restrito aos coordenadores do evento."},
            status_code=403,
        )

    excluir_fiscal(fiscal_id)
    return JSONResponse({"ok": True})


@router.post("/criar-evento")
async def post_criar_evento(request: Request):
    if not _usuario_e_coordenador(request):
        return _acesso_negado(request)

    form = await request.form()
    nome = str(form.get("nome", "")).strip()
    cidade = str(form.get("cidade", "")).strip()
    uf = str(form.get("uf", "")).strip().upper()
    acao_fiscalizacao = str(form.get("acao_fiscalizacao", "")).strip()
    processo_sei = str(form.get("processo_sei", "")).strip()
    periodo_inicio = str(form.get("periodo_inicio", "")).strip()
    periodo_fim = str(form.get("periodo_fim", "")).strip()
    teste_etiquetagem = str(form.get("teste_etiquetagem", "sim")).strip() == "sim"
    unidades_executantes = form.getlist("unidades_executantes")
    fiscais_evento = form.getlist("fiscais_evento")
    coordenadores_evento = [
        valor for valor in form.getlist("coordenador_responsavel") if valor.isdigit()
    ]
    observacoes = str(form.get("observacoes", "")).strip()
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()
    if not nome:
        request.session["flash_error"] = "Informe o nome do evento."
        return RedirectResponse("/criar-evento", status_code=303)
    if cidade and uf and not cidade_pertence_uf(cidade, uf):
        request.session["flash_error"] = "Selecione uma cidade e UF válidas."
        return RedirectResponse("/criar-evento", status_code=303)

    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        inicio = date.fromisoformat(periodo_inicio) if periodo_inicio else None
        fim = date.fromisoformat(periodo_fim) if periodo_fim else None
        if inicio and fim and fim < inicio:
            raise ValueError
        evento_id = criar_evento(
            nome=nome,
            latitude=latitude,
            longitude=longitude,
            cidade=cidade or None,
            uf=uf or None,
            acao_fiscalizacao=acao_fiscalizacao or None,
            processo_sei=processo_sei or None,
            periodo_inicio=periodo_inicio or None,
            periodo_fim=periodo_fim or None,
            teste_etiquetagem=teste_etiquetagem,
            unidades_executantes=unidades_executantes,
            fiscais=fiscais_evento,
            coordenadores=coordenadores_evento,
            observacoes=observacoes or None,
        )
    except ValueError:
        request.session["flash_error"] = (
            "Informe um período válido (o fim não pode ser anterior ao início)."
        )
        return RedirectResponse("/criar-evento", status_code=303)
    except IntegrityError:
        request.session["flash_error"] = "Já existe um evento com esse nome."
        return RedirectResponse("/criar-evento", status_code=303)

    request.session["evento_nome"] = nome
    request.session["spreadsheet_id"] = str(evento_id)
    evento_novo = obter_snapshot_auditoria_evento(evento_id)
    registrar_auditoria_evento(evento_id, {}, evento_novo)
    request.session["flash_success"] = "Evento criado com sucesso."
    return RedirectResponse("/menu", status_code=303)


@router.post("/criar-evento/{evento_id}/editar")
async def post_editar_evento(request: Request, evento_id: int):
    if not _usuario_e_coordenador(request):
        return _acesso_negado(request)

    form = await request.form()
    nome = str(form.get("nome", "")).strip()
    cidade = str(form.get("cidade", "")).strip()
    uf = str(form.get("uf", "")).strip().upper()
    acao_fiscalizacao = str(form.get("acao_fiscalizacao", "")).strip()
    processo_sei = str(form.get("processo_sei", "")).strip()
    periodo_inicio = str(form.get("periodo_inicio", "")).strip()
    periodo_fim = str(form.get("periodo_fim", "")).strip()
    teste_etiquetagem = str(form.get("teste_etiquetagem", "sim")).strip() == "sim"
    unidades_executantes = form.getlist("unidades_executantes")
    fiscais_evento = form.getlist("fiscais_evento")
    coordenadores_evento = [
        valor for valor in form.getlist("coordenador_responsavel") if valor.isdigit()
    ]
    observacoes = str(form.get("observacoes", "")).strip()
    latitude_texto = str(form.get("latitude", "")).strip()
    longitude_texto = str(form.get("longitude", "")).strip()

    if not nome:
        request.session["flash_error"] = "Informe o nome do evento."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)
    if cidade and uf and not cidade_pertence_uf(cidade, uf):
        request.session["flash_error"] = "Selecione uma cidade e UF válidas."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)

    try:
        latitude = float(latitude_texto) if latitude_texto else None
        longitude = float(longitude_texto) if longitude_texto else None
        if latitude is not None and not -90 <= latitude <= 90:
            raise ValueError
        if longitude is not None and not -180 <= longitude <= 180:
            raise ValueError
        inicio = date.fromisoformat(periodo_inicio) if periodo_inicio else None
        fim = date.fromisoformat(periodo_fim) if periodo_fim else None
        if inicio and fim and fim < inicio:
            raise ValueError
        evento_anterior = obter_snapshot_auditoria_evento(evento_id)
        if evento_anterior is None:
            request.session["flash_error"] = "Evento não encontrado."
            return RedirectResponse("/criar-evento", status_code=303)
        atualizar_fiscais_evento(evento_id, fiscais_evento)
        atualizar_evento(
            evento_id=evento_id,
            nome=nome,
            latitude=latitude,
            longitude=longitude,
            cidade=cidade or None,
            uf=uf or None,
            acao_fiscalizacao=acao_fiscalizacao or None,
            processo_sei=processo_sei or None,
            periodo_inicio=periodo_inicio or None,
            periodo_fim=periodo_fim or None,
            teste_etiquetagem=teste_etiquetagem,
            observacoes=observacoes or None,
            coordenadores=coordenadores_evento,
        )
        atualizar_unidades_evento(evento_id, unidades_executantes)
        evento_novo = obter_snapshot_auditoria_evento(evento_id)
        registrar_auditoria_evento(evento_id, evento_anterior, evento_novo)
    except ValueError:
        request.session["flash_error"] = (
            "Informe um período válido (o fim não pode ser anterior ao início)."
        )
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)
    except IntegrityError:
        request.session["flash_error"] = "Já existe um evento com esse nome."
        return RedirectResponse(f"/criar-evento?editar={evento_id}", status_code=303)

    if str(request.session.get("spreadsheet_id")) == str(evento_id):
        request.session["evento_nome"] = nome
    request.session["flash_success"] = "Evento atualizado com sucesso."
    return RedirectResponse("/criar-evento", status_code=303)
