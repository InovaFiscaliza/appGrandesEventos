from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import (
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    get_city_map_url,
    listar_coordenadores_evento,
    listar_tickets_evento,
)
from app.utils.formatters import _img_b64
from app.config import (
    STATUS_TICKET_CONCLUIDO_COORDENADOR,
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    TITULO_PRINCIPAL,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/menu", response_class=HTMLResponse)
async def get_menu(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    df_painel = carregar_pendencias_painel_mapeadas(evento_id=sp_id)
    df_estac = carregar_pendencias_todas_estacoes(evento_id=sp_id)
    link_mapa = get_city_map_url(evento_id=sp_id)

    fiscal_id = request.session.get("fiscal_id")
    coordenador = (
        str(request.session.get("tipo_usuario", "")).strip().casefold() == "coordenação"
    )
    fiscal_nome = str(request.session.get("fiscal_nome", "")).strip().casefold()
    if not coordenador:

        def somente_proprias(df):
            if df is None or df.empty or not fiscal_nome or "Fiscal" not in df.columns:
                return df.iloc[0:0] if df is not None else df
            return df[
                df["Fiscal"].fillna("").astype(str).str.strip().str.casefold()
                == fiscal_nome
            ]

        df_painel = somente_proprias(df_painel)
        df_estac = somente_proprias(df_estac)

    total = sum(len(df) for df in [df_painel, df_estac] if df is not None)
    tickets_atribuidos = [
        ticket
        for ticket in listar_tickets_evento(int(sp_id))
        if fiscal_id
        and str(fiscal_id).isdigit()
        and int(fiscal_id) in ticket.get("fiscal_ids", [])
        and ticket.get("status")
        not in {
            STATUS_TICKET_CONCLUIDO_FISCAIS,
            STATUS_TICKET_CONCLUIDO_COORDENADOR,
        }
    ]

    return templates.TemplateResponse(
        request,
        "menu.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
            "total": total,
            "exibir_tratamento_pendencias": coordenador or total > 0,
            "exibir_tratamento_tickets": bool(tickets_atribuidos),
            "total_tickets_atribuidos": len(tickets_atribuidos),
            "link_mapa": link_mapa,
            "flash_success": request.session.pop("flash_success", None),
            "flash_error": request.session.pop("flash_error", None),
        },
    )


@router.get("/api/ping")
async def api_ping():
    """Endpoint de health check — usado pelo connectivity.js para detectar conectividade real."""
    return JSONResponse({"ok": True})
