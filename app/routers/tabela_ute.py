import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import carregar_dados_ute
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

SORT_COLS = ["Frequência (MHz)", "País/Entidade", "Local", "Processo SEI"]
PAGE_SIZE_OPTIONS = [10, 20, 30, 40, 50, 100, 200]


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        **kwargs,
    }


@router.get("/ute", response_class=HTMLResponse)
async def get_ute(
    request: Request,
    sort: str = "Frequência (MHz)",
    dir: str = "asc",
    page_size: int = 10,
):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    if page_size not in PAGE_SIZE_OPTIONS:
        page_size = 10

    df = carregar_dados_ute(evento_id=sp_id)

    rows = []
    if not df.empty:
        ascendente = dir == "asc"
        if sort == "Frequência (MHz)":
            df["_ord"] = pd.to_numeric(
                df["Frequência (MHz)"].astype(str).str.replace(",", "."),
                errors="coerce",
            ).fillna(0)
            df = df.sort_values(by="_ord", ascending=ascendente).drop(columns=["_ord"])
        elif sort in df.columns:
            df = df.sort_values(by=sort, ascending=ascendente)
        rows = df.to_dict(orient="records")

    return templates.TemplateResponse(
        request,
        "tabela_ute.html",
        _ctx(
            request,
            rows=rows,
            sort_cols=SORT_COLS,
            sort=sort,
            dir=dir,
            page_size=page_size,
            page_size_options=PAGE_SIZE_OPTIONS,
        ),
    )
