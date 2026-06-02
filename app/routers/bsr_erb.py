from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.google_sheets import inserir_bsr_erb, obter_cliente_gspread
from app.utils.formatters import _img_b64, _valid_neg_coord
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


@router.get("/bsr-erb", response_class=HTMLResponse)
async def get_bsr_erb(request: Request):
    if not request.session.get("spreadsheet_id"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "bsr_erb.html",
        _ctx(
            request,
            tipo="BSR/Jammer",
            regiao="",
            lat="",
            lon="",
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/bsr-erb", response_class=HTMLResponse)
async def post_bsr_erb(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    tipo = form.get("tipo", "BSR/Jammer")
    regiao = form.get("regiao", "").strip()
    lat = form.get("lat", "").strip()
    lon = form.get("lon", "").strip()

    error = None
    if not regiao:
        error = "O campo 'Local' é obrigatório."
    elif not _valid_neg_coord(lat) or not _valid_neg_coord(lon):
        error = "Coordenadas inválidas. Use o formato -N.NNNNNN."

    if error:
        return templates.TemplateResponse(
            "bsr_erb.html",
            _ctx(
                request,
                tipo=tipo,
                regiao=regiao,
                lat=lat,
                lon=lon,
                flash_error=error,
                flash_success=None,
            ),
        )

    client = obter_cliente_gspread()
    res = inserir_bsr_erb(client, sp_id, tipo, regiao, lat, lon)

    if res.startswith("ERRO"):
        return templates.TemplateResponse(
            "bsr_erb.html",
            _ctx(
                request,
                tipo=tipo,
                regiao=regiao,
                lat=lat,
                lon=lon,
                flash_error=res,
                flash_success=None,
            ),
        )

    request.session["flash_success"] = res
    return RedirectResponse("/bsr-erb", status_code=303)
