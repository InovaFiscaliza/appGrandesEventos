from types import SimpleNamespace

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    STATUS_TICKET_PENDENTE,
    STATUS_TICKET_ROTULOS,
    STATUS_TICKET_VALIDOS,
    TITULO_PRINCIPAL,
)
from app.services.postgres import (
    cancelar_ticket_evento,
    atualizar_ticket_evento,
    carregar_imagens_ocorrencia,
    concluir_emissao_coordenador,
    listar_emissoes_evento,
    listar_coordenadores_evento,
    listar_escalas_evento,
    listar_fiscais,
    listar_fiscais_evento,
    listar_tickets_evento,
    obter_emissao_evento,
    registrar_auditoria_coordenacao,
    salvar_escala_evento,
    salvar_ticket_evento,
)
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _usuario_e_coordenador(request: Request, evento_id: int) -> bool:
    """Confirma que o fiscal logado está vinculado como coordenador do evento."""
    fiscal_id = request.session.get("fiscal_id")
    return str(
        request.session.get("tipo_usuario", "")
    ).strip().casefold() == "coordenação" or bool(
        fiscal_id
        and str(fiscal_id).isdigit()
        and int(fiscal_id) in listar_coordenadores_evento(evento_id)
    )


def _acesso_negado(request: Request) -> RedirectResponse:
    """Redireciona para o menu quando o usuário não tem perfil de coordenação."""
    request.session["flash_error"] = "Acesso restrito aos coordenadores do evento."
    return RedirectResponse("/menu", status_code=303)


def _ctx(request: Request, **kwargs):
    if not hasattr(request.state, "eventos"):
        request.state.eventos = {}
    if not hasattr(request.state, "permissoes"):
        request.state.permissoes = SimpleNamespace(teste_etiquetagem=False)

    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        **kwargs,
    }


@router.get("/coordenacao", response_class=HTMLResponse)
async def get_coordenacao(request: Request):
    """Página inicial da coordenação do evento."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    event_fiscais_ids = set(listar_fiscais_evento(int(evento_id)))
    fiscais_evento = [
        fiscal for fiscal in listar_fiscais() if int(fiscal["id"]) in event_fiscais_ids
    ]

    todos_tickets = listar_tickets_evento(int(evento_id))
    tickets_pendentes = [
        ticket
        for ticket in todos_tickets
        if ticket.get("status") == STATUS_TICKET_PENDENTE
    ]
    tickets_concluidos_fiscais = [
        ticket
        for ticket in todos_tickets
        if ticket.get("status") == STATUS_TICKET_CONCLUIDO_FISCAIS
    ]

    return templates.TemplateResponse(
        request,
        "coordenacao.html",
        _ctx(
            request,
            tickets=tickets_pendentes,
            tickets_concluidos_fiscais=tickets_concluidos_fiscais,
            status_ticket_rotulos=STATUS_TICKET_ROTULOS,
            emissões=listar_emissoes_evento(int(evento_id)),
            escalas=listar_escalas_evento(int(evento_id)),
            fiscais=fiscais_evento,
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/coordenacao/ticket")
async def post_ticket_evento(request: Request):
    """Cria ou atualiza um ticket para uma emissão e atribui um ou mais fiscais."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    form = await request.form()
    ocorrencia_ids = list(
        dict.fromkeys(
            int(item)
            for item in form.getlist("ocorrencia_ids")
            if str(item).strip().isdigit()
        )
    )
    prioridade = str(form.get("prioridade", "normal")).strip() or "normal"
    observacoes = str(form.get("observacoes", "")).strip() or None
    fiscais = [
        int(item) for item in form.getlist("fiscais") if str(item).strip().isdigit()
    ]

    if not ocorrencia_ids:
        request.session["flash_error"] = (
            "Selecione ao menos uma emissão para abrir o ticket."
        )
        return RedirectResponse("/coordenacao", status_code=303)

    try:
        ticket_id = salvar_ticket_evento(
            evento_id=int(evento_id),
            ocorrencia_ids=ocorrencia_ids,
            prioridade=prioridade,
            observacoes=observacoes,
            fiscal_ids=fiscais,
            usuario_fiscal=request.session.get(
                "fiscal_nome", "Usuário não identificado"
            ),
        )
    except ValueError as exc:
        request.session["flash_error"] = str(exc)
        return RedirectResponse("/coordenacao", status_code=303)

    registrar_auditoria_coordenacao(
        evento_id=int(evento_id),
        usuario_fiscal=request.session.get("fiscal_nome", "Usuário não identificado"),
        acao="Ticket criado",
        valor_anterior=None,
        valor_novo=(
            f"Ticket #{ticket_id}; emissões: {', '.join(f'#{item}' for item in ocorrencia_ids)}; "
            f"prioridade: {prioridade}; fiscais: {', '.join(f'#{item}' for item in fiscais) or 'nenhum'}; "
            f"observações: {observacoes or 'nenhuma'}"
        ),
    )
    request.session["flash_success"] = (
        "Ticket salvo e atribuído aos fiscais selecionados."
    )
    return RedirectResponse("/coordenacao", status_code=303)


@router.post("/coordenacao/escala")
async def post_escala_evento(request: Request):
    """Salva uma escala de trabalho para um fiscal do evento."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    form = await request.form()
    fiscal_id = str(form.get("fiscal_id", "")).strip()
    data_trabalho = str(form.get("data_trabalho", "")).strip()
    turno_inicio = str(form.get("turno_inicio", "")).strip() or None
    turno_fim = str(form.get("turno_fim", "")).strip() or None
    observacoes = str(form.get("observacoes", "")).strip() or None

    if not fiscal_id or not data_trabalho:
        request.session["flash_error"] = "Selecione o fiscal e a data de trabalho."
        return RedirectResponse("/coordenacao", status_code=303)

    salvar_escala_evento(
        evento_id=int(evento_id),
        fiscal_id=int(fiscal_id),
        data_trabalho=data_trabalho,
        turno_inicio=turno_inicio,
        turno_fim=turno_fim,
        observacoes=observacoes,
    )
    registrar_auditoria_coordenacao(
        evento_id=int(evento_id),
        usuario_fiscal=request.session.get("fiscal_nome", "Usuário não identificado"),
        acao="Escala criada",
        valor_anterior=None,
        valor_novo=(
            f"Escala; fiscal #{fiscal_id}; data: {data_trabalho}; "
            f"início: {turno_inicio or 'não informado'}; fim: {turno_fim or 'não informado'}; "
            f"observações: {observacoes or 'nenhuma'}"
        ),
    )
    request.session["flash_success"] = "Escala salva com sucesso."
    return RedirectResponse("/coordenacao", status_code=303)


@router.post("/coordenacao/ticket/{ticket_id}/status")
async def post_ticket_status(request: Request, ticket_id: int):
    """Atualiza o status de um ticket."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    form = await request.form()
    status = str(form.get("status", "pendente")).strip() or "pendente"
    if status not in STATUS_TICKET_VALIDOS:
        request.session["flash_error"] = "Status de ticket inválido."
        return RedirectResponse("/coordenacao", status_code=303)
    prioridade = None
    if "prioridade" in form:
        prioridade = str(form.get("prioridade", "")).strip() or None
    observacoes = None
    if "observacoes" in form:
        observacoes = str(form.get("observacoes", "")).strip() or None
    fiscais = None
    if "fiscais" in form:
        fiscais = [
            int(item) for item in form.getlist("fiscais") if str(item).strip().isdigit()
        ]

    ticket_anterior = next(
        (
            ticket
            for ticket in listar_tickets_evento(int(evento_id))
            if int(ticket["id"]) == ticket_id
        ),
        None,
    )

    try:
        atualizar_ticket_evento(
            ticket_id=ticket_id,
            evento_id=int(evento_id),
            status=status,
            fiscal_ids=fiscais,
            observacoes=observacoes,
            prioridade=prioridade,
            usuario_fiscal=request.session.get(
                "fiscal_nome", "Usuário não identificado"
            ),
        )
    except ValueError as exc:
        request.session["flash_error"] = str(exc)
        return RedirectResponse("/coordenacao", status_code=303)
    if ticket_anterior:
        fiscais_anteriores = (
            ", ".join(f"#{item}" for item in (ticket_anterior.get("fiscal_ids") or []))
            or "nenhum"
        )
        fiscais_novos = (
            ", ".join(f"#{item}" for item in fiscais)
            if fiscais is not None
            else fiscais_anteriores
        ) or "nenhum"
        registrar_auditoria_coordenacao(
            evento_id=int(evento_id),
            usuario_fiscal=request.session.get(
                "fiscal_nome", "Usuário não identificado"
            ),
            acao="Ticket atualizado",
            valor_anterior=(
                f"Ticket #{ticket_id}; status: {ticket_anterior.get('status')}; "
                f"prioridade: {ticket_anterior.get('prioridade')}; fiscais: {fiscais_anteriores}; "
                f"observações: {ticket_anterior.get('observacoes') or 'nenhuma'}"
            ),
            valor_novo=(
                f"Ticket #{ticket_id}; status: {status}; "
                f"prioridade: {prioridade or ticket_anterior.get('prioridade')}; fiscais: {fiscais_novos}; "
                f"observações: {observacoes if observacoes is not None else ticket_anterior.get('observacoes') or 'nenhuma'}"
            ),
        )
    request.session["flash_success"] = "Ticket atualizado com sucesso."
    return RedirectResponse("/coordenacao", status_code=303)


@router.post("/coordenacao/ticket/{ticket_id}/cancelar")
async def post_ticket_cancelar(request: Request, ticket_id: int):
    """Cancela ticket e libera suas emissões para novos tickets."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    ticket_anterior = next(
        (
            ticket
            for ticket in listar_tickets_evento(int(evento_id))
            if int(ticket["id"]) == ticket_id
        ),
        None,
    )
    cancelar_ticket_evento(ticket_id=ticket_id, evento_id=int(evento_id))
    if ticket_anterior:
        registrar_auditoria_coordenacao(
            evento_id=int(evento_id),
            usuario_fiscal=request.session.get(
                "fiscal_nome", "Usuário não identificado"
            ),
            acao="Ticket cancelado",
            valor_anterior=(
                f"Ticket #{ticket_id}; status: {ticket_anterior.get('status')}; "
                f"emissões: {ticket_anterior.get('ocorrencia_ids') or 'nenhuma'}"
            ),
            valor_novo=f"Ticket #{ticket_id}; cancelado; emissões liberadas para nova atribuição",
        )
    request.session["flash_success"] = "Ticket cancelado e emissões liberadas."
    return RedirectResponse("/coordenacao", status_code=303)


@router.get("/coordenacao/api/emissao/{ocorrencia_id}")
async def get_emissao_detalhe(request: Request, ocorrencia_id: int):
    """Retorna os detalhes da emissão para popup na coordenação."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return JSONResponse(
            {"erro": "Acesso restrito aos coordenadores do evento."}, status_code=403
        )

    emissao = obter_emissao_evento(int(evento_id), int(ocorrencia_id))
    if not emissao:
        return JSONResponse({"erro": "Emissão não encontrada"}, status_code=404)

    emissao["imagens"] = carregar_imagens_ocorrencia(
        evento_id=int(evento_id),
        ocorrencia_id=int(ocorrencia_id),
    )
    return JSONResponse(jsonable_encoder(emissao))


@router.post("/coordenacao/emissao/{ocorrencia_id}/concluir")
async def post_concluir_emissao_coordenador(request: Request, ocorrencia_id: int):
    """Registra a conclusão definitiva de uma emissão pela coordenação."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if not _usuario_e_coordenador(request, int(evento_id)):
        return _acesso_negado(request)

    res = concluir_emissao_coordenador(
        evento_id=int(evento_id),
        ocorrencia_id=ocorrencia_id,
        usuario_fiscal=request.session.get(
            "fiscal_nome", "Usuário não identificado"
        ),
    )

    if res.startswith("ERRO"):
        request.session["flash_error"] = res
    else:
        request.session["flash_success"] = res

    return RedirectResponse("/coordenacao", status_code=303)
