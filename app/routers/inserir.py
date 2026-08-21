from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile

from app.services.postgres import (
    carregar_opcoes_identificacao,
    FrequenciaOcupadaError,
    inserir_emissao_I_W,
    listar_estacoes_evento,
    obter_fuso_horario_evento,
    verificar_equipamento_frequencia,
)
from app.utils.formatters import _data_hora_foto, _img_b64
from app.utils.offline import (
    extrair_dados_inserir,
    preparar_offline_ctx,
)
from app.config import FAIXA_OPCOES, TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
EXTENSOES_IMAGEM = {".jpeg", ".jpg", ".png"}
TIPOS_IMAGEM = {"image/jpeg", "image/png"}
TAMANHO_MAXIMO_IMAGEM = 10 * 1024 * 1024


async def _ler_imagens(form) -> tuple[list[dict], list[str]]:
    """Lê os anexos de imagem e valida extensão, MIME e tamanho."""
    imagens = []
    erros = []
    for arquivo in form.getlist("imagens"):
        if not isinstance(arquivo, UploadFile) or not getattr(
            arquivo, "filename", None
        ):
            continue
        nome = arquivo.filename
        extensao = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
        if extensao not in EXTENSOES_IMAGEM or arquivo.content_type not in TIPOS_IMAGEM:
            erros.append(f"Imagem inválida: {nome}. Use JPEG, JPG ou PNG.")
            continue
        conteudo = await arquivo.read()
        if not conteudo:
            erros.append(f"Imagem vazia: {nome}.")
            continue
        if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
            erros.append(f"Imagem muito grande: {nome}. Limite de 10 MB.")
            continue
        data_hora_foto = _data_hora_foto(conteudo)
        imagens.append(
            {
                "nome_arquivo": nome,
                "data_foto": data_hora_foto.date() if data_hora_foto else None,
                "hora_foto": data_hora_foto.time() if data_hora_foto else None,
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
        "faixa_opcoes": FAIXA_OPCOES,
        **kwargs,
    }


@router.get("/inserir", response_class=HTMLResponse)
async def get_inserir(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    idents = carregar_opcoes_identificacao(evento_id=sp_id)
    estacoes = listar_estacoes_evento(evento_id=sp_id)
    fuso = obter_fuso_horario_evento(evento_id=sp_id)
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
            estacao_id="",
            estacoes=estacoes,
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
    imagens, erros_imagens = await _ler_imagens(form)
    fiscal = form.get("fiscal", "").strip()
    local = form.get("local", "").strip()
    dia_str = form.get("dia", "")
    hora_str = form.get("hora", "")
    freq_str = form.get("freq", "")
    larg_str = form.get("larg", "")
    faixa = form.get("faixa", "")
    ident = form.get("ident", "")
    estacao_id = form.get("estacao_id", "").strip()
    interferente = form.get("interferente", "")
    ute = bool(form.get("ute"))
    proc = form.get("proc", "").strip()
    obs = form.get("obs", "").strip()
    situacao = form.get("situacao", "")

    idents = carregar_opcoes_identificacao(evento_id=sp_id)
    estacoes = listar_estacoes_evento(evento_id=sp_id)

    erros = list(erros_imagens)
    if not fiscal:
        erros.append("Fiscal")
    try:
        freq = float(freq_str) if freq_str else 0.0
    except ValueError:
        freq = 0.0
    if freq <= 0:
        erros.append("Frequência")
    if estacao_id not in {str(estacao["id"]) for estacao in estacoes}:
        erros.append("Estação da captura")
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
                estacao_id=estacao_id,
                estacoes=estacoes,
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

    conflito = verificar_equipamento_frequencia(
        evento_id=sp_id, freq_digitada=freq, largura_khz=larg, localidade=local
    )

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
        "Estação ID": int(estacao_id) if estacao_id.isdigit() else None,
    }

    try:
        ok = inserir_emissao_I_W(
            evento_id=sp_id, dados_formulario=dados_submit, imagens=imagens
        )
    except FrequenciaOcupadaError as exc:
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
                estacao_id=estacao_id,
                estacoes=estacoes,
                interferente=interferente,
                ute=ute,
                proc=proc,
                obs=obs,
                situacao=situacao,
                flash_error=str(exc),
                flash_success=None,
            ),
        )
    if ok:
        msg = "Emissão inserida com sucesso. Caso queira continuar inserindo emissões desta entidade, basta alterar os dados específicos e clicar em Registrar Emissão."
        if conflito:
            msg = (
                f"⚠️ AVISO: existe equipamento usando essa frequência ({conflito}). "
                + msg
            )
        request.session["flash_success"] = msg
        return RedirectResponse("/inserir", status_code=303)

    # Falhou (offline ou erro) → salva na fila local via frontend
    dados_json = extrair_dados_inserir(form)
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
            estacao_id=estacao_id,
            estacoes=estacoes,
            interferente=interferente,
            ute=ute,
            proc=proc,
            obs=obs,
            situacao=situacao,
            flash_error=None,
            flash_success=None,
            **preparar_offline_ctx(dados_json),
        ),
    )


@router.get("/check-freq")
async def check_freq(
    request: Request, freq: float = 0.0, larg: float = 0.0, local: str = ""
):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id or freq <= 0:
        return {"conflito": None}
    conflito = verificar_equipamento_frequencia(
        evento_id=sp_id, freq_digitada=freq, largura_khz=larg, localidade=local
    )
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

    try:
        ok = inserir_emissao_I_W(evento_id=sp_id, dados_formulario=dados)
    except FrequenciaOcupadaError as exc:
        return JSONResponse(
            {"erro": str(exc), "codigo": "frequencia_ocupada"}, status_code=409
        )
    if ok:
        return JSONResponse({"ok": True})
    return JSONResponse({"erro": "Falha ao inserir na planilha"}, status_code=500)
