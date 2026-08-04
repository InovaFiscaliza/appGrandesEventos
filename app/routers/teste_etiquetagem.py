from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TITULO_PRINCIPAL
from app.services.postgres import (
    atualizar_teste_etiquetagem,
    excluir_teste_etiquetagem,
    inserir_teste_etiquetagem,
    listar_testes_etiquetagem,
    obter_teste_etiquetagem,
    verificar_etiqueta_existente,
    verificar_frequencia_etiquetagem,
)
from app.utils.formatters import _img_b64

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

LICENCAS = {"ute", "outorgado", "nao_outorgado", "radiacao_restrita"}
PERFIS = {"pf", "pj", "estrangeiro"}
PERMISSOES = {"permitido", "todos", "nao"}


def _formatar_banda(valor: int) -> str:
    """Formata a largura de banda em kHz para exibição no formulário."""
    return f"{valor:,}".replace(",", ".") + " kHz"


BANDA_OPCOES = [
    _formatar_banda(valor)
    for valor in [5, 10, *range(25, 501, 25), *range(1_000, 100_001, 1_000)]
]
FAIXAS_ETIQUETAGEM = [
    "SLP / VHF (148-174 MHz)",
    "SLP / UHF (360-470 MHz)",
    "SLP / 800 MHz (806-854 MHz)",
    "SLP / 2,4 GHz (2390-2495 MHz)",
    "SLP / 3,7 GHz (3700-3800 MHz)",
    "Radiação Restrita (Wi-Fi/Bluetooth/LoRa)",
    "Outra faixa autorizada pela Anatel",
]


def _validar_cpf_cnpj(documento: str) -> bool:
    """Valida CPF ou CNPJ pelos dígitos verificadores, quando informado."""
    numeros = "".join(caractere for caractere in documento if caractere.isdigit())
    if len(numeros) not in {11, 14} or len(set(numeros)) == 1:
        return False

    if len(numeros) == 11:
        soma = sum(
            int(numero) * (10 - indice) for indice, numero in enumerate(numeros[:9])
        )
        primeiro = (soma * 10 % 11) % 10
        if primeiro != int(numeros[9]):
            return False
        soma = sum(
            int(numero) * (11 - indice) for indice, numero in enumerate(numeros[:10])
        )
        segundo = (soma * 10 % 11) % 10
        return segundo == int(numeros[10])

    pesos = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    soma = sum(int(numero) * peso for numero, peso in zip(numeros[:12], pesos))
    primeiro = 0 if soma % 11 < 2 else 11 - soma % 11
    if primeiro != int(numeros[12]):
        return False
    pesos = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    soma = sum(int(numero) * peso for numero, peso in zip(numeros[:13], pesos))
    segundo = 0 if soma % 11 < 2 else 11 - soma % 11
    return segundo == int(numeros[13])


def _ctx(request: Request, **kwargs):
    return {
        "request": request,
        "titulo": TITULO_PRINCIPAL,
        "img_b64_esq": _img_b64("anatel.png"),
        "img_b64_dir": _img_b64("anatelS.png"),
        "evento_nome": request.session.get("evento_nome", ""),
        "faixa_opcoes": FAIXAS_ETIQUETAGEM,
        "banda_opcoes": BANDA_OPCOES,
        **kwargs,
    }


def _form_values(form) -> dict:
    frequencias_selecionadas = form.getlist("frequencias_selecionadas")
    return {
        "licenca": form.get("licenca", "ute"),
        "perfil": form.get("perfil", "pf"),
        "entidade": form.get("entidade", "").strip(),
        "contato": form.get("contato", "").strip(),
        "local": form.get("local", "").strip(),
        "cpf_cnpj": form.get("cpf_cnpj", "").strip(),
        "frequencia_mhz": form.get("frequencia_mhz", "").strip(),
        "passo": form.get("passo", "").strip(),
        "faixa": form.get("faixa", "").strip(),
        "equipamento_homologado": bool(form.get("equipamento_homologado")),
        "permissao": form.get("permissao", "permitido"),
        "frequencias_selecionadas": frequencias_selecionadas,
        "frequencias_disponiveis": frequencias_selecionadas.copy(),
        "tipo_equipamento": form.get("tipo_equipamento", "").strip(),
        "numero_etiqueta": form.get("numero_etiqueta", "").strip(),
        "observacoes": form.get("observacoes", "").strip(),
        "invalid_fields": [],
    }


def _record_values(record: dict) -> dict:
    """Converte um registro do PostgreSQL para o formato usado pelo formulário."""
    values = dict(record)
    values["frequencia_mhz"] = ""
    values["passo"] = ""
    values["faixa"] = ""
    values["frequencias_selecionadas"] = values.get("frequencias_selecionadas") or []
    values["frequencias_disponiveis"] = list(values["frequencias_selecionadas"])
    values["invalid_fields"] = []
    return values


def _render_form(
    request: Request,
    values: dict,
    error: str | None = None,
    invalid_fields: list[str] | None = None,
):
    values = {**values, "invalid_fields": invalid_fields or []}
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
async def get_teste_etiquetagem(request: Request, edit_id: int | None = None):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    values = {
        "licenca": "ute",
        "perfil": "pf",
        "entidade": "",
        "contato": "",
        "local": "",
        "cpf_cnpj": "",
        "frequencia_mhz": "",
        "passo": "",
        "faixa": "",
        "equipamento_homologado": False,
        "permissao": "permitido",
        "frequencias_selecionadas": [],
        "frequencias_disponiveis": [],
        "tipo_equipamento": "",
        "numero_etiqueta": "",
        "observacoes": "",
        "invalid_fields": [],
    }
    if edit_id is not None:
        registro = obter_teste_etiquetagem(evento_id=sp_id, registro_id=edit_id)
        if registro:
            values = _record_values(registro)
            values["registro_id"] = edit_id

    return templates.TemplateResponse(
        request,
        "teste_etiquetagem.html",
        _ctx(
            request,
            values=values,
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
    registro_id = form.get("registro_id")
    erros = []
    invalid_fields = []

    def adicionar_erro(mensagem: str, campo: str | None = None):
        erros.append(mensagem)
        if campo and campo not in invalid_fields:
            invalid_fields.append(campo)

    if values["licenca"] not in LICENCAS:
        adicionar_erro("Tipo de licença inválido")
    if values["perfil"] not in PERFIS:
        adicionar_erro("Perfil inválido")
    if not values["entidade"]:
        adicionar_erro("Entidade", "entidade")
    if not values["local"]:
        adicionar_erro("Local", "local")
    if values["permissao"] not in PERMISSOES:
        adicionar_erro("Permissão inválida")
    if not values["tipo_equipamento"]:
        adicionar_erro("Tipo do equipamento", "tipo_equipamento")
    if not values["numero_etiqueta"]:
        adicionar_erro("Número da etiqueta", "numero_etiqueta")
    if values["cpf_cnpj"] and not _validar_cpf_cnpj(values["cpf_cnpj"]):
        adicionar_erro("CPF/CNPJ inválido", "cpf_cnpj")
    if not values["frequencias_selecionadas"]:
        adicionar_erro("Selecione ao menos uma frequência", "frequencias_selecionadas")
    frequencia = None
    if values["frequencia_mhz"]:
        try:
            frequencia = float(values["frequencia_mhz"].replace(",", "."))
            if frequencia <= 0:
                frequencia = None
        except (AttributeError, ValueError):
            frequencia = None

    passo_khz = None
    if values["passo"]:
        try:
            passo_khz = float(
                values["passo"]
                .lower()
                .replace("khz", "")
                .strip()
                .replace(".", "")
                .replace(",", ".")
            )
            if passo_khz <= 0 or passo_khz > 100_000:
                raise ValueError
        except (AttributeError, ValueError):
            adicionar_erro("Passo de frequência inválido", "passo")

    if erros:
        return _render_form(
            request,
            values,
            "Preencha os campos corretamente: " + ", ".join(dict.fromkeys(erros)) + ".",
            invalid_fields,
        )

    etiqueta_existente = verificar_etiqueta_existente(
        numero_etiqueta=values["numero_etiqueta"],
        excluir_id=registro_id,
    )
    if etiqueta_existente:
        return _render_form(
            request,
            values,
            "Etiqueta já cadastrada no evento "
            f"{etiqueta_existente['evento']} em {etiqueta_existente['data']}. "
            "Utilizada por: "
            f"{etiqueta_existente['entidade'] or 'Nome não informado'} "
            f"(CPF/CNPJ: {etiqueta_existente['cpf_cnpj'] or 'não informado'}).",
            ["numero_etiqueta"],
        )

    conflito = (
        verificar_frequencia_etiquetagem(
            evento_id=evento_id, freq_digitada=frequencia, excluir_id=registro_id
        )
        if frequencia is not None
        else None
    )
    if conflito:
        return _render_form(
            request,
            values,
            f"Frequência {values['frequencia_mhz']} MHz já cadastrada em {conflito}.",
        )

    dados = values
    if registro_id:
        resultado = atualizar_teste_etiquetagem(
            evento_id=evento_id, registro_id=registro_id, dados=dados
        )
    else:
        resultado = inserir_teste_etiquetagem(evento_id=evento_id, dados=dados)
    if resultado.startswith("ERRO"):
        return _render_form(request, values, resultado)

    request.session["flash_success"] = resultado
    return RedirectResponse("/teste_etiquetagem", status_code=303)


@router.get("/teste_etiquetagem/consultar", response_class=HTMLResponse)
async def consultar_testes_etiquetagem(request: Request):
    """Exibe os registros de etiquetagem do evento atual."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request,
        "teste_etiquetagem_consultar.html",
        _ctx(
            request,
            registros=listar_testes_etiquetagem(evento_id=evento_id),
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/teste_etiquetagem/excluir")
async def excluir_teste_etiquetagem_rota(request: Request):
    """Exclui um registro de etiquetagem do evento atual."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    form = await request.form()
    resultado = excluir_teste_etiquetagem(
        evento_id=evento_id, registro_id=form.get("registro_id")
    )
    chave = "flash_success" if not resultado.startswith("ERRO") else "flash_error"
    request.session[chave] = resultado
    return RedirectResponse("/teste_etiquetagem/consultar", status_code=303)
