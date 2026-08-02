from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import inserir_bsr_erb
from app.utils.formatters import _img_b64, _normalize_coord, _valid_coord
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
        request,
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

    lat = _normalize_coord(lat)
    lon = _normalize_coord(lon)

    error = None
    if not regiao:
        error = "O campo 'Local' é obrigatório."
    elif not _valid_coord(lat, -90.0, 90.0):
        error = "Latitude inválida. Deve ser um número entre -90 e 90."
    elif not _valid_coord(lon, -180.0, 180.0):
        error = "Longitude inválida. Deve ser um número entre -180 e 180."

    if error:
        return templates.TemplateResponse(
            request,
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

    res = inserir_bsr_erb(evento_id=sp_id, tipo=tipo, regiao=regiao, lat=lat, lon=lon)

    if res.startswith("ERRO"):
        return templates.TemplateResponse(
            request,
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


@router.post("/api/bsr-erb")
async def api_bsr_erb(request: Request):
    """Recebe JSON da fila offline (IndexedDB/sync.js) e insere na planilha."""
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    try:
        dados = await request.json()
    except Exception:
        return JSONResponse({"erro": "JSON inválido"}, status_code=400)

    tipo = dados.get("tipo", "BSR/Jammer")
    regiao = dados.get("regiao", "").strip()
    lat = _normalize_coord(dados.get("lat", ""))
    lon = _normalize_coord(dados.get("lon", ""))

    if not regiao:
        return JSONResponse({"erro": "Campo 'Local' obrigatório"}, status_code=400)
    if not _valid_coord(lat, -90.0, 90.0):
        return JSONResponse({"erro": "Latitude inválida"}, status_code=400)
    if not _valid_coord(lon, -180.0, 180.0):
        return JSONResponse({"erro": "Longitude inválida"}, status_code=400)

    res = inserir_bsr_erb(evento_id=sp_id, tipo=tipo, regiao=regiao, lat=lat, lon=lon)
    if res.startswith("ERRO"):
        return JSONResponse({"erro": res}, status_code=500)
    return JSONResponse({"ok": True, "msg": res})
