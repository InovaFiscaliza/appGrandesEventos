from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.config import MODELOS_EQUIPAMENTO, TITULO_PRINCIPAL
from app.services.postgres import (
    IdentificacaoEstacaoExistenteError,
    atualizar_estacao,
    criar_estacao,
    desabilitar_estacao,
    listar_estacoes_evento,
    listar_eventos_detalhes,
    reativar_estacao,
    registrar_auditoria_coordenacao,
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
    """Confirma que o usuário selecionou o papel Coordenação no login."""
    del evento_id
    return (
        str(request.session.get("tipo_usuario", "")).strip().casefold() == "coordenação"
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
    estacoes = (
        listar_estacoes_evento(int(evento_id), incluir_inativas=True)
        if evento_id
        else []
    )
    for estacao in estacoes:
        nome_normalizado = str(estacao["nome"]).strip().casefold()
        estacao["colisoes_ativas"] = [
            ativa
            for ativa in estacoes
            if ativa["ativa"]
            and str(ativa["nome"]).strip().casefold() == nome_normalizado
            and ativa["id"] != estacao["id"]
        ]
        estacao["colisoes_ativas_ids"] = ", ".join(
            f"#{ativa['id']}" for ativa in estacao["colisoes_ativas"]
        )
    reativar_id = request.query_params.get("reativar", "")
    estacao_reativacao = next(
        (
            estacao
            for estacao in estacoes
            if reativar_id.isdigit()
            and str(estacao["id"]) == reativar_id
            and not estacao["ativa"]
        ),
        None,
    )
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
            estacao_reativacao=estacao_reativacao,
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
    reativar_id = None
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
    except IdentificacaoEstacaoExistenteError as exc:
        erro = True
        if exc.estacao["desabilitada_em"] is not None:
            reativar_id = int(exc.estacao["id"])
            request.session["flash_error"] = (
                "Essa identificação pertence a uma estação inativa. "
                "Confirme a reativação na lista; os registros anteriores serão preservados."
            )
        else:
            request.session["flash_error"] = (
                "Já existe uma estação ativa com essa identificação no evento. "
                "A comparação não diferencia maiúsculas e minúsculas."
            )
    except IntegrityError:
        erro = True
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    except ValueError:
        erro = True
        request.session["flash_error"] = "Informe latitude e longitude válidas."
    sufixo = (
        f"&reativar={reativar_id}#estacao-{reativar_id}"
        if reativar_id
        else "&novo=1" if erro else ""
    )
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
    reativar_id = None
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
    except IdentificacaoEstacaoExistenteError as exc:
        erro = True
        if exc.estacao["desabilitada_em"] is not None:
            reativar_id = int(exc.estacao["id"])
            request.session["flash_error"] = (
                "Essa identificação pertence a uma estação inativa. "
                "Confirme a reativação na lista; os registros anteriores serão preservados."
            )
        else:
            request.session["flash_error"] = (
                "Já existe uma estação ativa com essa identificação no evento. "
                "A comparação não diferencia maiúsculas e minúsculas."
            )
    except IntegrityError:
        erro = True
        request.session["flash_error"] = (
            "Já existe uma estação com essa identificação no evento."
        )
    except ValueError:
        erro = True
        request.session["flash_error"] = "Informe latitude e longitude válidas."
    sufixo = (
        f"&reativar={reativar_id}#estacao-{reativar_id}"
        if reativar_id
        else f"&editar={estacao_id}" if erro else ""
    )
    return RedirectResponse(f"/estacoes?evento_id={evento_id}{sufixo}", status_code=303)


@router.post("/estacoes/{estacao_id}/reativar")
async def post_reativar_estacao(request: Request, estacao_id: int):
    """Reativa estação inativa após confirmação explícita da coordenação."""
    form = await request.form()
    evento_id = str(form.get("evento_id", "")).strip()
    if not evento_id.isdigit() or not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    try:
        estacao = reativar_estacao(int(evento_id), estacao_id)
    except IdentificacaoEstacaoExistenteError:
        request.session["flash_error"] = (
            "Não foi possível reativar: já existe uma estação ativa com essa identificação."
        )
    else:
        if estacao is None:
            request.session["flash_error"] = "Estação não encontrada ou já está ativa."
        else:
            nome = estacao["nome"]
            estacoes_substituidas = estacao.get("estacoes_desativadas", [])
            ids_substituidos = ", ".join(
                str(item["id"]) for item in estacoes_substituidas
            )
            complemento = (
                f"; estações ativas substituídas: #{ids_substituidos}"
                if ids_substituidos
                else ""
            )
            registrar_auditoria_coordenacao(
                evento_id=int(evento_id),
                usuario_fiscal=request.session.get(
                    "fiscal_nome", "Usuário não identificado"
                ),
                acao="Estação reativada",
                valor_anterior=(
                    f"Estação #{estacao_id} ({nome}); estado: Inativa{complemento}"
                ),
                valor_novo=(
                    f"Estação #{estacao_id} ({nome}); estado: Ativa{complemento}; "
                    "IDs e referências históricas preservados"
                ),
            )
            request.session["flash_success"] = (
                "Estação reativada com sucesso. "
                + (
                    f"A estação ativa #{ids_substituidos} foi desativada; "
                    "IDs e registros anteriores foram preservados."
                    if ids_substituidos
                    else "Os registros anteriores foram preservados."
                )
            )
    return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)


@router.post("/estacoes/{estacao_id}/excluir")
async def post_excluir_estacao(request: Request, estacao_id: int):
    """Desabilita uma estação e preserva seu histórico de utilização."""
    form = await request.form()
    evento_id = str(form.get("evento_id", "")).strip()
    if not evento_id.isdigit() or not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    estacao = desabilitar_estacao(int(evento_id), estacao_id)
    if estacao is None:
        request.session["flash_error"] = "Estação não encontrada ou já desabilitada."
    else:
        registrar_auditoria_coordenacao(
            evento_id=int(evento_id),
            usuario_fiscal=request.session.get(
                "fiscal_nome", "Usuário não identificado"
            ),
            acao="Coordenação - Estação desabilitada",
            valor_anterior=(
                f"Estação #{estacao_id}; nome: {estacao['nome']}; "
                f"modelo: {estacao['modelo_equipamento'] or 'não informado'}; "
                f"local: {estacao['local'] or 'não informado'}"
            ),
            valor_novo="Estação desabilitada; registros históricos preservados",
        )
        request.session["flash_success"] = "Estação desabilitada com sucesso."
    return RedirectResponse(f"/estacoes?evento_id={evento_id}", status_code=303)
