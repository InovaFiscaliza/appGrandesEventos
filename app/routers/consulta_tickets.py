"""Consulta de tickets do evento, disponivel a todos os usuarios da sessao."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import STATUS_TICKET_ROTULOS, TITULO_PRINCIPAL
from app.services.postgres import (
    carregar_imagens_ocorrencias,
    listar_tickets_evento,
    obter_detalhes_ticket_evento,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/tickets", response_class=HTMLResponse)
async def get_tickets(request: Request):
    """Lista todos os tickets do evento, sem restricao de fiscal ou situacao."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id or not request.session.get("fiscal_id"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request,
        "consulta_tickets.html",
        {
            "titulo": TITULO_PRINCIPAL,
            "evento_nome": request.session.get("evento_nome", ""),
            "tickets": listar_tickets_evento(int(evento_id)),
            "ticket": None,
            "status_ticket_rotulos": STATUS_TICKET_ROTULOS,
        },
    )


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def get_ticket(request: Request, ticket_id: int):
    """Exibe dados e registros vinculados sem permitir sua alteracao."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id or not request.session.get("fiscal_id"):
        return RedirectResponse("/", status_code=302)
    ticket = obter_detalhes_ticket_evento(int(evento_id), ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket nao encontrado neste evento.")
    imagens = carregar_imagens_ocorrencias(
        evento_id=int(evento_id),
        ocorrencia_ids=[emissao["id"] for emissao in ticket["emissoes"]],
    )
    for emissao in ticket["emissoes"]:
        emissao["imagens"] = imagens.get(emissao["id"], [])
    return templates.TemplateResponse(
        request,
        "consulta_tickets.html",
        {
            "titulo": TITULO_PRINCIPAL,
            "evento_nome": request.session.get("evento_nome", ""),
            "ticket": ticket,
            "status_ticket_rotulos": STATUS_TICKET_ROTULOS,
        },
    )