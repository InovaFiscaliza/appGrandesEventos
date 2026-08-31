"""Rotas para o fiscal acompanhar e concluir tickets atribuídos."""

from types import SimpleNamespace

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    STATUS_TICKET_CONCLUIDO_COORDENADOR,
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    STATUS_TICKET_PENDENTE,
    STATUS_TICKET_ROTULOS,
    TITULO_PRINCIPAL,
)
from app.services.postgres import (
    atualizar_ticket_evento,
    listar_tickets_evento,
    registrar_auditoria_coordenacao,
)
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
STATUS_VALIDOS = {STATUS_TICKET_PENDENTE, STATUS_TICKET_CONCLUIDO_FISCAIS}


def _ctx(request: Request, **kwargs):
    """Monta o contexto comum da tela de tratamento."""
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
        "status_ticket_rotulos": STATUS_TICKET_ROTULOS,
        **kwargs,
    }


def _tickets_atribuidos(request: Request, evento_id: int) -> list[dict]:
    """Lista somente tickets abertos atribuídos ao fiscal da sessão."""
    fiscal_id = request.session.get("fiscal_id")
    if not fiscal_id or not str(fiscal_id).isdigit():
        return []
    return [
        ticket
        for ticket in listar_tickets_evento(evento_id)
        if int(fiscal_id) in ticket.get("fiscal_ids", [])
        and ticket.get("status")
        not in {
            STATUS_TICKET_CONCLUIDO_FISCAIS,
            STATUS_TICKET_CONCLUIDO_COORDENADOR,
        }
    ]


@router.get("/tratamento-tickets", response_class=HTMLResponse)
async def get_tratamento_tickets(request: Request):
    """Exibe os tickets abertos atribuídos ao fiscal logado."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        request,
        "tratamento_tickets.html",
        _ctx(
            request,
            tickets=_tickets_atribuidos(request, int(evento_id)),
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/tratamento-tickets/{ticket_id}")
async def post_tratamento_ticket(request: Request, ticket_id: int):
    """Atualiza ou conclui pelo fiscal um ticket a ele atribuído."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    ticket = next(
        (
            item
            for item in _tickets_atribuidos(request, int(evento_id))
            if int(item["id"]) == ticket_id
        ),
        None,
    )
    if ticket is None:
        request.session["flash_error"] = (
            "Você não tem permissão para tratar este ticket."
        )
        return RedirectResponse("/tratamento-tickets", status_code=303)

    form = await request.form()
    status = str(form.get("status", "")).strip()
    observacoes = str(form.get("observacoes", "")).strip() or None
    if status not in STATUS_VALIDOS:
        request.session["flash_error"] = "Status de ticket inválido."
        return RedirectResponse("/tratamento-tickets", status_code=303)
    if status == STATUS_TICKET_CONCLUIDO_FISCAIS and not observacoes:
        request.session["flash_error"] = (
            "Informe as providências tomadas antes de concluir o ticket."
        )
        return RedirectResponse("/tratamento-tickets", status_code=303)

    atualizar_ticket_evento(
        ticket_id=ticket_id,
        evento_id=int(evento_id),
        status=status,
        observacoes=observacoes,
        usuario_fiscal=request.session.get(
            "fiscal_nome", "Usuário não identificado"
        ),
    )
    registrar_auditoria_coordenacao(
        evento_id=int(evento_id),
        usuario_fiscal=request.session.get("fiscal_nome", "Usuário não identificado"),
        acao="Ticket tratado",
        valor_anterior=(
            f"Ticket #{ticket_id}; status: {ticket['status']}; "
            f"observações: {ticket.get('observacoes') or 'nenhuma'}"
        ),
        valor_novo=(
            f"Ticket #{ticket_id}; status: {status}; "
            f"observações: {observacoes or 'nenhuma'}"
        ),
    )
    request.session["flash_success"] = "Ticket atualizado com sucesso."
    return RedirectResponse("/tratamento-tickets", status_code=303)
