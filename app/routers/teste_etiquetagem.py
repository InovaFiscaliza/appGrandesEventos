from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import (
    inserir_teste_etiquetagem,
    verificar_frequencia_etiquetagem,
)
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

LICENCAS = {"ute", "outorgado", "nao_outorgado", "radiacao_restrita"}
PERFIS = {"pf", "pj", "estrangeiro"}
PERMISSOES = {"permitido", "todos", "nao"}
PASSOS = {"12,5kHz": 12.5, "25kHz": 25.0, "50kHz": 50.0}


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        **kwargs,
    }


def _form_values(form) -> dict:
    return {
        "licenca": form.get("licenca", "ute"),
        "perfil": form.get("perfil", "pf"),
        "entidade": form.get("entidade", "").strip(),
        "contato": form.get("contato", "").strip(),
        "local": form.get("local", "").strip(),
        "cpf_cnpj": form.get("cpf_cnpj", "").strip(),
        "frequencia_mhz": form.get("frequencia_mhz", "").strip(),
        "passo": form.get("passo", "25kHz"),
        "faixa": form.get("faixa", "SLP").strip(),
        "equipamento_homologado": bool(form.get("equipamento_homologado")),
        "permissao": form.get("permissao", "permitido"),
        "frequencias_selecionadas": form.getlist("frequencias_selecionadas"),
        "tipo_equipamento": form.get("tipo_equipamento", "").strip(),
        "numero_etiqueta": form.get("numero_etiqueta", "").strip(),
        "observacoes": form.get("observacoes", "").strip(),
    }


def _render_form(request: Request, values: dict, error: str | None = None):
    return templates.TemplateResponse(
        request,
        "teste_etiquetagem.html",
        _ctx(
            request,
            values=values,
            flash_error=error,
            flash_success=None,
        ),
    )


@router.get("/teste_etiquetagem", response_class=HTMLResponse)
async def get_teste_etiquetagem(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        request,
        "teste_etiquetagem.html",
        _ctx(
            request,
            values={
                "licenca": "ute",
                "perfil": "pf",
                "entidade": "",
                "contato": "",
                "local": "",
                "cpf_cnpj": "",
                "frequencia_mhz": "",
                "passo": "25kHz",
                "faixa": "SLP",
                "equipamento_homologado": False,
                "permissao": "permitido",
                "frequencias_selecionadas": [],
                "tipo_equipamento": "",
                "numero_etiqueta": "",
                "observacoes": "",
            },
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/teste_etiquetagem", response_class=HTMLResponse)
async def post_teste_etiquetagem(request: Request):
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    values = _form_values(form)
    erros = []

    if values["licenca"] not in LICENCAS:
        erros.append("Tipo de licença inválido")
    if values["perfil"] not in PERFIS:
        erros.append("Perfil inválido")
    if not values["entidade"]:
        erros.append("Entidade")
    if not values["local"]:
        erros.append("Local")
    if not values["faixa"]:
        erros.append("Faixa")
    if values["permissao"] not in PERMISSOES:
        erros.append("Permissão inválida")
    if not values["tipo_equipamento"]:
        erros.append("Tipo do equipamento")
    if not values["numero_etiqueta"]:
        erros.append("Número da etiqueta")
    if not values["frequencias_selecionadas"]:
        erros.append("Selecione ao menos uma frequência")

    try:
        frequencia = float(values["frequencia_mhz"].replace(",", "."))
        if frequencia <= 0:
            raise ValueError
    except (AttributeError, ValueError):
        frequencia = 0.0
        erros.append("Frequência válida")

    passo_khz = PASSOS.get(values["passo"])
    if passo_khz is None:
        erros.append("Passo de frequência inválido")

    if erros:
        return _render_form(
            request,
            values,
            "Preencha os campos corretamente: " + ", ".join(dict.fromkeys(erros)) + ".",
        )

    conflito = verificar_frequencia_etiquetagem(
        evento_id=evento_id, freq_digitada=frequencia
    )
    if conflito:
        return _render_form(
            request,
            values,
            f"Frequência {values['frequencia_mhz']} MHz já cadastrada em {conflito}.",
        )

    resultado = inserir_teste_etiquetagem(
        evento_id=evento_id,
        dados={
            **values,
            "frequencia_mhz": frequencia,
            "passo_khz": passo_khz,
        },
    )
    if resultado.startswith("ERRO"):
        return _render_form(request, values, resultado)

    request.session["flash_success"] = resultado
    return RedirectResponse("/teste_etiquetagem", status_code=303)
