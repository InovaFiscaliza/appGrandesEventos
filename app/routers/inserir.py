from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.google_sheets import (
    carregar_opcoes_identificacao,
    inserir_emissao_I_W,
    obter_cliente_gspread,
    obter_fuso_horario_evento,
    verificar_frequencia_global,
)
from app.utils.formatters import _img_b64
from app.config import FAIXA_OPCOES, TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        "faixa_opcoes": FAIXA_OPCOES,
        **kwargs,
    }


@router.get("/inserir", response_class=HTMLResponse)
async def get_inserir(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    client = obter_cliente_gspread()
    idents = carregar_opcoes_identificacao(client, sp_id)
    fuso = obter_fuso_horario_evento(client, sp_id)
    agora = datetime.now(ZoneInfo(fuso))

    return templates.TemplateResponse(
        request,
        "inserir.html",
        _ctx(
            request,
            ident_opcoes=idents,
            dia=agora.strftime("%Y-%m-%d"),
            hora=agora.strftime("%H:%M"),
            fiscal="",
            local="",
            freq="",
            larg="",
            faixa="",
            ident="",
            interferente="",
            ute=False,
            proc="",
            obs="",
            situacao="",
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/inserir", response_class=HTMLResponse)
async def post_inserir(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    fiscal = form.get("fiscal", "").strip()
    local = form.get("local", "").strip()
    dia_str = form.get("dia", "")
    hora_str = form.get("hora", "")
    freq_str = form.get("freq", "")
    larg_str = form.get("larg", "")
    faixa = form.get("faixa", "")
    ident = form.get("ident", "")
    interferente = form.get("interferente", "")
    ute = bool(form.get("ute"))
    proc = form.get("proc", "").strip()
    obs = form.get("obs", "").strip()
    situacao = form.get("situacao", "")

    client = obter_cliente_gspread()
    idents = carregar_opcoes_identificacao(client, sp_id)

    erros = []
    if not fiscal:
        erros.append("Fiscal")
    try:
        freq = float(freq_str) if freq_str else 0.0
    except ValueError:
        freq = 0.0
    if freq <= 0:
        erros.append("Frequência")
    if not situacao:
        erros.append("Status")
    erros = list(dict.fromkeys(erros))

    if erros:
        return templates.TemplateResponse(
            request,
            "inserir.html",
            _ctx(
                request,
                ident_opcoes=idents,
                dia=dia_str,
                hora=hora_str,
                fiscal=fiscal,
                local=local,
                freq=freq_str,
                larg=larg_str,
                faixa=faixa,
                ident=ident,
                interferente=interferente,
                ute=ute,
                proc=proc,
                obs=obs,
                situacao=situacao,
                flash_error="Preencha os campos obrigatórios: " + ", ".join(erros),
                flash_success=None,
            ),
        )

    try:
        larg = float(larg_str) if larg_str else 0.0
    except ValueError:
        larg = 0.0

    conflito = verificar_frequencia_global(client, sp_id, freq)

    try:
        dia_obj = datetime.strptime(dia_str, "%Y-%m-%d").date()
    except Exception:
        dia_obj = datetime.now().date()
    try:
        hora_obj = datetime.strptime(hora_str, "%H:%M").time()
    except Exception:
        hora_obj = datetime.now().time()

    dados_submit = {
        "Dia": dia_obj,
        "Hora": hora_obj,
        "Fiscal": fiscal,
        "Local/Região": local,
        "Frequência em MHz": freq,
        "Largura em kHz": larg,
        "Faixa de Frequência": faixa,
        "Identificação": ident,
        "UTE?": ute,
        "Processo SEI ou Ato UTE": proc,
        "Observações/Detalhes/Contatos": obs,
        "Situação": situacao,
        "Autorizado? (Q)": "Indefinido",
        "Interferente?": interferente,
    }

    ok = inserir_emissao_I_W(client, sp_id, dados_submit)

    if ok:
        msg = "Emissão inserida com sucesso. Caso queira continuar inserindo emissões desta entidade, basta alterar os dados específicos e clicar em Registrar Emissão."
        if conflito:
            msg = f"⚠️ AVISO: Frequência consta na Planilha - Aba: {conflito}. " + msg
        request.session["flash_success"] = msg
        return RedirectResponse("/inserir", status_code=303)

    return templates.TemplateResponse(
        request,
        "inserir.html",
        _ctx(
            request,
            ident_opcoes=idents,
            dia=dia_str,
            hora=hora_str,
            fiscal=fiscal,
            local=local,
            freq=freq_str,
            larg=larg_str,
            faixa=faixa,
            ident=ident,
            interferente=interferente,
            ute=ute,
            proc=proc,
            obs=obs,
            situacao=situacao,
            flash_error="Erro ao inserir emissão. Tente novamente.",
            flash_success=None,
        ),
    )


@router.get("/check-freq")
async def check_freq(request: Request, freq: float = 0.0):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id or freq <= 0:
        return {"conflito": None}
    client = obter_cliente_gspread()
    conflito = verificar_frequencia_global(client, sp_id, freq)
    return {"conflito": conflito}


@router.post("/api/inserir")
async def api_inserir(request: Request):
    """Recebe JSON da fila offline (IndexedDB/sync.js) e insere na planilha."""
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    try:
        dados = await request.json()
    except Exception:
        return JSONResponse({"erro": "JSON inválido"}, status_code=400)

    client = obter_cliente_gspread()
    ok = inserir_emissao_I_W(client, sp_id, dados)
    if ok:
        return JSONResponse({"ok": True})
    return JSONResponse({"erro": "Falha ao inserir na planilha"}, status_code=500)
