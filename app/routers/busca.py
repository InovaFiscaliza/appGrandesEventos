from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.google_sheets import (
    _buscar_por_texto_livre,
    listar_abas_estacoes,
    obter_cliente_gspread,
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


def _row_to_display(row, i: int) -> dict:
    aba_origem = str(row.get("Aba/Origem", ""))
    loc = str(row.get("Local", row.get("Local/Região", row.get("Estação", ""))))
    if not loc and aba_origem:
        loc = aba_origem
    dt = str(row.get("Data", row.get("Dia", "")))
    fr = str(row.get("Frequência (MHz)", row.get("Frequência", "")))
    id_val = str(row.get("ID", ""))

    partes = [
        p
        for p in [
            loc,
            dt,
            f"{fr} MHz" if fr else "",
            f"ID {id_val}" if id_val else "",
        ]
        if p and p.strip() not in ("", " MHz", "MHz")
    ]
    titulo = " | ".join(partes) if partes else f"Resultado #{i}"

    skip = {"Fonte", "Aba/Origem"}
    campos = [
        (col, str(row.get(col, "")))
        for col in row.index
        if col not in skip and str(row.get(col, "")).strip()
    ]

    return {
        "titulo": titulo,
        "campos": campos,
        "fonte": str(row.get("Fonte", "N/A")),
        "aba_origem": aba_origem or "N/A",
    }


@router.get("/busca", response_class=HTMLResponse)
async def get_busca(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    client = obter_cliente_gspread()
    abas_est = listar_abas_estacoes(client, sp_id)
    abas_opcoes = ["Abordagem"] + abas_est

    return templates.TemplateResponse(
        "busca.html",
        _ctx(
            request,
            abas_opcoes=abas_opcoes,
            abas_sel=abas_opcoes,
            termo="",
            resultados=None,
            flash_warning=None,
        ),
    )


@router.post("/busca", response_class=HTMLResponse)
async def post_busca(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    termo = form.get("termo", "").strip()
    abas_sel = form.getlist("abas")

    client = obter_cliente_gspread()
    abas_est = listar_abas_estacoes(client, sp_id)
    abas_opcoes = ["Abordagem"] + abas_est

    if not abas_sel:
        abas_sel = abas_opcoes

    if len(termo) < 3:
        return templates.TemplateResponse(
            "busca.html",
            _ctx(
                request,
                abas_opcoes=abas_opcoes,
                abas_sel=abas_sel,
                termo=termo,
                resultados=None,
                flash_warning="Digite pelo menos 3 caracteres para consultar.",
            ),
        )

    res = _buscar_por_texto_livre(client, sp_id, termo, abas_sel)
    resultados = (
        []
        if res.empty
        else [
            _row_to_display(row, i)
            for i, (_, row) in enumerate(res.iterrows(), start=1)
        ]
    )

    return templates.TemplateResponse(
        "busca.html",
        _ctx(
            request,
            abas_opcoes=abas_opcoes,
            abas_sel=abas_sel,
            termo=termo,
            resultados=resultados,
            flash_warning=None,
        ),
    )
