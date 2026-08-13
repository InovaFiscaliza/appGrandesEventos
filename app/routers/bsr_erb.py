from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile

from app.services.postgres import (
    atualizar_bsr_erb,
    excluir_bsr_erb,
    inserir_bsr_erb,
    listar_bsr_erb,
)
from app.utils.formatters import _img_b64, _normalize_coord, _valid_coord
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
EXTENSOES_IMAGEM = {".jpeg", ".jpg", ".png"}
TIPOS_IMAGEM = {"image/jpeg", "image/png"}
TAMANHO_MAXIMO_IMAGEM = 10 * 1024 * 1024


async def _ler_imagens(form) -> tuple[list[dict], list[str]]:
    """Lê e valida as fotos anexadas ao registro BSR/ERB."""
    imagens = []
    erros = []
    for arquivo in form.getlist("imagens"):
        if not isinstance(arquivo, UploadFile) or not getattr(
            arquivo, "filename", None
        ):
            continue
        extensao = (
            "." + arquivo.filename.rsplit(".", 1)[-1].lower()
            if "." in arquivo.filename
            else ""
        )
        if extensao not in EXTENSOES_IMAGEM or arquivo.content_type not in TIPOS_IMAGEM:
            erros.append(f"Imagem inválida: {arquivo.filename}. Use JPEG, JPG ou PNG.")
            continue
        conteudo = await arquivo.read()
        if not conteudo:
            erros.append(f"Imagem vazia: {arquivo.filename}.")
            continue
        if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
            erros.append(f"Imagem muito grande: {arquivo.filename}. Limite de 10 MB.")
            continue
        imagens.append(
            {
                "nome_arquivo": arquivo.filename,
                "tipo_mime": arquivo.content_type,
                "tamanho_bytes": len(conteudo),
                "conteudo": conteudo,
            }
        )
    return imagens, erros


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
    registros = listar_bsr_erb(int(request.session["spreadsheet_id"]))
    editar_id = request.query_params.get("editar")
    registro_edicao = None
    if editar_id and editar_id.isdigit():
        registro_edicao = next(
            (registro for registro in registros if registro["id"] == int(editar_id)),
            None,
        )
        if registro_edicao is None:
            request.session["flash_error"] = "Registro BSR/ERB não encontrado."
            return RedirectResponse("/bsr-erb", status_code=303)
    return templates.TemplateResponse(
        request,
        "bsr_erb.html",
        _ctx(
            request,
            tipo=registro_edicao["tipo"] if registro_edicao else "BSR/Jammer",
            regiao=registro_edicao["regiao"] if registro_edicao else "",
            lat=registro_edicao["latitude"] if registro_edicao else "",
            lon=registro_edicao["longitude"] if registro_edicao else "",
            observacoes=registro_edicao["observacoes"] if registro_edicao else "",
            registros=registros,
            registro_edicao=registro_edicao,
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
    imagens, erros_imagens = await _ler_imagens(form)
    tipo = form.get("tipo", "BSR/Jammer")
    regiao = form.get("regiao", "").strip()
    lat = form.get("lat", "").strip()
    lon = form.get("lon", "").strip()
    observacoes = form.get("observacoes", "").strip()

    lat = _normalize_coord(lat)
    lon = _normalize_coord(lon)

    error = "; ".join(erros_imagens) if erros_imagens else None
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
                observacoes=observacoes,
                registros=listar_bsr_erb(int(sp_id)),
                flash_error=error,
                flash_success=None,
            ),
        )

    res = inserir_bsr_erb(
        evento_id=sp_id,
        tipo=tipo,
        regiao=regiao,
        lat=lat,
        lon=lon,
        observacoes=observacoes,
        imagens=imagens,
    )

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
                observacoes=observacoes,
                registros=listar_bsr_erb(int(sp_id)),
                flash_error=res,
                flash_success=None,
            ),
        )

    request.session["flash_success"] = res
    return RedirectResponse("/bsr-erb", status_code=303)


@router.post("/bsr-erb/{registro_id}/editar", response_class=HTMLResponse)
async def post_editar_bsr_erb(request: Request, registro_id: int):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    imagens, erros_imagens = await _ler_imagens(form)
    tipo = form.get("tipo", "BSR/Jammer")
    regiao = form.get("regiao", "").strip()
    lat = _normalize_coord(form.get("lat", "").strip())
    lon = _normalize_coord(form.get("lon", "").strip())
    observacoes = form.get("observacoes", "").strip()

    error = "; ".join(erros_imagens) if erros_imagens else None
    if not regiao:
        error = "O campo 'Local' é obrigatório."
    elif not _valid_coord(lat, -90.0, 90.0):
        error = "Latitude inválida. Deve ser um número entre -90 e 90."
    elif not _valid_coord(lon, -180.0, 180.0):
        error = "Longitude inválida. Deve ser um número entre -180 e 180."

    if error:
        registro_edicao = next(
            (
                registro
                for registro in listar_bsr_erb(int(sp_id))
                if registro["id"] == registro_id
            ),
            None,
        )
        return templates.TemplateResponse(
            request,
            "bsr_erb.html",
            _ctx(
                request,
                tipo=tipo,
                regiao=regiao,
                lat=lat,
                lon=lon,
                observacoes=observacoes,
                registros=listar_bsr_erb(int(sp_id)),
                registro_edicao=registro_edicao,
                flash_error=error,
                flash_success=None,
            ),
        )

    res = atualizar_bsr_erb(
        registro_id=registro_id,
        evento_id=sp_id,
        tipo=tipo,
        regiao=regiao,
        lat=lat,
        lon=lon,
        observacoes=observacoes,
        imagens=imagens,
    )
    if res.startswith("ERRO"):
        request.session["flash_error"] = res
    else:
        request.session["flash_success"] = res
    return RedirectResponse("/bsr-erb", status_code=303)


@router.post("/bsr-erb/{registro_id}/excluir")
async def post_excluir_bsr_erb(request: Request, registro_id: int):
    """Exclui logicamente um registro BSR/ERB e registra a auditoria."""
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)
    res = excluir_bsr_erb(registro_id=registro_id, evento_id=sp_id)
    request.session["flash_error" if res.startswith("ERRO") else "flash_success"] = res
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
    observacoes = dados.get("observacoes", "").strip()

    if not regiao:
        return JSONResponse({"erro": "Campo 'Local' obrigatório"}, status_code=400)
    if not _valid_coord(lat, -90.0, 90.0):
        return JSONResponse({"erro": "Latitude inválida"}, status_code=400)
    if not _valid_coord(lon, -180.0, 180.0):
        return JSONResponse({"erro": "Longitude inválida"}, status_code=400)

    res = inserir_bsr_erb(
        evento_id=sp_id,
        tipo=tipo,
        regiao=regiao,
        lat=lat,
        lon=lon,
        observacoes=observacoes,
    )
    if res.startswith("ERRO"):
        return JSONResponse({"erro": res}, status_code=500)
    return JSONResponse({"ok": True, "msg": res})
