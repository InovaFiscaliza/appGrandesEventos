from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    STATUS_TICKET_CONCLUIDO_COORDENADOR,
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    TITULO_PRINCIPAL,
)
from app.domain.emissao.service import EmissaoService
from app.infrastructure.persistence.postgres.emissao_repository import (
    PostgresEmissaoRepository,
)
from app.services.postgres import (
    get_city_map_url,
    listar_tickets_evento,
)
from app.utils.formatters import _img_b64


def get_emissao_service() -> EmissaoService:
    repo = PostgresEmissaoRepository()
    return EmissaoService(repo)


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/menu", response_class=HTMLResponse)
async def get_menu(
    request: Request,
    emissao_service: EmissaoService = Depends(get_emissao_service),
):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    sp_id_int = int(sp_id)

    # Use EmissaoService to get all emissions for the event (incluir_todas=True)
    emissoes = [
        emissao
        for emissao in emissao_service.listar_por_evento(sp_id_int, incluir_todas=True)
        if emissao.situacao.strip().casefold() == "pendente"
        and emissao.submetida_coordenador_em is None
    ]

    # Convert to DataFrame for existing logic
    import pandas as pd

    if not emissoes:
        df = pd.DataFrame()
    else:
        data = []
        for e in emissoes:
            data.append(
                {
                    "Local": e.local_regiao,
                    "EstacaoRaw": e.equipamento or "",
                    "EstacaoID": str(e.id),
                    "OrigemCaptura": e.fonte,
                    "CriadorFiscalID": e.fiscal_id,
                    "CadastradoPor": e.fiscal_nome or "Não informado",
                    "SubmetidaCoordenadorEm": e.submetida_coordenador_em,
                    "ID": str(e.id),
                    "IDExibicao": e.id_exibicao,
                    "Fiscal": e.fiscal_nome or "",
                    "Data": e.data,
                    "HH:mm": e.hora.strftime("%H:%M") if e.hora else "",
                    "Frequência (MHz)": str(e.frequencia_mhz),
                    "Largura (kHz)": str(e.largura_khz),
                    "Faixa de Frequência Envolvida": e.faixa,
                    "Identificação": e.identificacao,
                    "Autorizado?": (
                        "Sim"
                        if e.autorizado
                        else ("Não" if e.autorizado is False else "Indefinido")
                    ),
                    "UTE?": "Sim" if e.ute else "Não",
                    "Processo SEI UTE": e.processo_sei_ute or "",
                    "Ato UTE": e.ato_ute or "",
                    "Ocorrência (observações)": e.observacoes,
                    "Alguém mais ciente?": e.alguem_ciente,
                    "Interferente?": "Sim" if e.interferente else "Não",
                    "Situação": e.situacao,
                    "Fonte": e.fonte,
                }
            )
        df = pd.DataFrame(data)

    # Filter by source like the old functions did
    df_painel = df[df["Fonte"] == "PAINEL"] if not df.empty else pd.DataFrame()
    df_estac = df[df["Fonte"] == "ESTACAO"] if not df.empty else pd.DataFrame()

    link_mapa = get_city_map_url(evento_id=sp_id_int)

    fiscal_id = request.session.get("fiscal_id")
    coordenador = (
        str(request.session.get("tipo_usuario", "")).strip().casefold() == "coordenação"
    )
    fiscal_nome = str(request.session.get("fiscal_nome", "")).strip().casefold()
    if not coordenador:

        def somente_proprias(df):
            if df is None or df.empty:
                return df.iloc[0:0] if df is not None else df
            criador_ids = pd.to_numeric(df["CriadorFiscalID"], errors="coerce")
            propria = pd.Series(False, index=df.index)
            if fiscal_id and str(fiscal_id).isdigit():
                propria = criador_ids.eq(int(fiscal_id))
            if fiscal_nome:
                propria |= (criador_ids.isna() | criador_ids.eq(0)) & (
                    df["Fiscal"].fillna("").astype(str).str.strip().str.casefold()
                    == fiscal_nome
                )
            return df[propria]

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
