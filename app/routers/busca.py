from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.postgres import (
    _buscar_por_texto_livre,
    carregar_imagens_ocorrencias,
    sugerir_busca_emissoes,
)
from app.utils.formatters import _img_b64
from app.config import TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/api/busca/sugestoes")
async def get_sugestoes_busca(request: Request, termo: str = ""):
    """Retorna sugestões de emissões do evento selecionado."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    return JSONResponse(sugerir_busca_emissoes(evento_id=evento_id, termo=termo))


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        **kwargs,
    }


def _row_to_display(row, i: int, imagens_por_ocorrencia: dict | None = None) -> dict:
    aba_origem = str(row.get("Aba/Origem", ""))
    loc = str(row.get("Local", row.get("Local/Região", row.get("Estação", ""))))
    if not loc and aba_origem:
        loc = aba_origem
    dt = str(row.get("Data", row.get("Dia", "")))
    fr = str(row.get("Frequência (MHz)", row.get("Frequência", "")))
    id_val = str(row.get("ID", ""))
    imagens = (imagens_por_ocorrencia or {}).get(
        int(id_val) if id_val.isdigit() else -1,
        [],
    )

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

    campos = [(col, str(row.get(col, "")).strip() or "(vazio)") for col in row.index]

    return {
        "titulo": titulo,
        "id": id_val,
        "local": loc,
        "data": dt,
        "frequencia": fr,
        "identificacao": str(row.get("Identificação", "")),
        "situacao": str(row.get("Situação", "")),
        "campos": campos,
        "imagens": imagens,
        "fonte": str(row.get("Fonte", "N/A")),
        "aba_origem": aba_origem or "N/A",
    }


@router.get("/busca", response_class=HTMLResponse)
async def get_busca(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        request,
        "busca.html",
        _ctx(
            request,
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
    if termo and len(termo) < 3 and not termo.isdigit():
        return templates.TemplateResponse(
            request,
            "busca.html",
            _ctx(
                request,
                termo=termo,
                resultados=None,
                flash_warning="Digite pelo menos 3 caracteres, informe um ID ou deixe vazio para listar todas as emissões.",
            ),
        )

    res = _buscar_por_texto_livre(evento_id=sp_id, termos=termo)
    imagens_por_ocorrencia = carregar_imagens_ocorrencias(
        evento_id=sp_id,
        ocorrencia_ids=res["ID"].tolist() if not res.empty else [],
    )
    resultados = (
        []
        if res.empty
        else [
            _row_to_display(row, i, imagens_por_ocorrencia)
            for i, (_, row) in enumerate(res.iterrows(), start=1)
        ]
    )

    return templates.TemplateResponse(
        request,
        "busca.html",
        _ctx(
            request,
            termo=termo,
            resultados=resultados,
            flash_warning=None,
        ),
    )
