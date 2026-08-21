import re

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile

from app.config import TITULO_PRINCIPAL
from app.services.postgres import (
    atualizar_teste_etiquetagem,
    carregar_imagens_teste_etiquetagem,
    excluir_teste_etiquetagem,
    inserir_teste_etiquetagem,
    listar_testes_etiquetagem,
    consultar_equipamentos_frequencia,
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
EXTENSOES_IMAGEM = {".jpeg", ".jpg", ".png"}
TIPOS_IMAGEM = {"image/jpeg", "image/png"}
TAMANHO_MAXIMO_IMAGEM = 10 * 1024 * 1024


def _formatar_banda(valor: int) -> str:
    """Formata a largura de banda em kHz para exibição do formulário."""
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


def _frequencia_da_etiqueta(valor: str) -> float | None:
    """Extrai a frequência de etiquetas novas e de registros legados."""
    correspondencia = re.match(r"\s*([\d.,]+)(?:\s+MHz\b|(?=\s|$))", str(valor or ""))
    if not correspondencia:
        return None
    try:
        frequencia = float(correspondencia.group(1).replace(",", "."))
    except ValueError:
        return None
    return frequencia if frequencia > 0 else None


def _largura_da_etiqueta(valor: str) -> float:
    """Extrai a largura em kHz embutida no texto da frequência."""
    correspondencia = re.search(r"⌂\s*([\d.,]+)\s*kHz", str(valor or ""), re.I)
    if not correspondencia:
        return 0.0
    try:
        return max(
            float(correspondencia.group(1).replace(".", "").replace(",", ".")),
            0.0,
        )
    except ValueError:
        return 0.0


async def _ler_imagens(form) -> tuple[list[dict], list[str]]:
    """Lê e valida fotos anexadas ao equipamento."""
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
        imagens.append(
            {
                "nome_arquivo": nome,
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
        "imagens": [],
        "imagens_novas": [],
        "imagens_excluir": [],
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
            modo_consulta=bool(values.get("modo_consulta")),
            registros=(
                listar_testes_etiquetagem(
                    evento_id=request.session.get("spreadsheet_id")
                )
                if values.get("modo_consulta")
                else []
            ),
            flash_error=error,
            flash_success=None,
        ),
    )


@router.get("/teste_etiquetagem", response_class=HTMLResponse)
async def get_teste_etiquetagem(
    request: Request, edit_id: int | None = None, consultar: bool = False
):
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
        "imagens": [],
        "imagens_excluir": [],
        "invalid_fields": [],
        "modo_consulta": consultar,
    }
    if edit_id is not None:
        registro = obter_teste_etiquetagem(evento_id=sp_id, registro_id=edit_id)
        if registro:
            values = _record_values(registro)
            values["registro_id"] = edit_id
            values["imagens"] = carregar_imagens_teste_etiquetagem(
                evento_id=sp_id, teste_id=edit_id
            )

    return templates.TemplateResponse(
        request,
        "teste_etiquetagem.html",
        _ctx(
            request,
            values=values,
            modo_consulta=consultar,
            registros=(listar_testes_etiquetagem(evento_id=sp_id) if consultar else []),
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.get("/api/teste-etiquetagem/verificar-frequencia")
async def verificar_frequencia_teste(
    request: Request,
    frequencia: float,
    largura_khz: float = 0,
    local: str = "",
    excluir_id: int | None = None,
):
    """Consulta equipamentos e referências da frequência no evento atual."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    return JSONResponse(
        consultar_equipamentos_frequencia(
            evento_id=evento_id,
            freq_digitada=frequencia,
            largura_khz=largura_khz,
            localidade=local,
            excluir_id=excluir_id,
        )
    )


@router.post("/teste_etiquetagem", response_class=HTMLResponse)
async def post_teste_etiquetagem(request: Request):
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    imagens, erros_imagens = await _ler_imagens(form)
    values = _form_values(form)
    values["imagens_novas"] = imagens
    values["imagens_excluir"] = [
        int(valor) for valor in form.getlist("imagens_excluir") if str(valor).isdigit()
    ]
    values["modo_consulta"] = bool(form.get("modo_consulta"))
    registro_id = form.get("registro_id")

    frequencia = _frequencia_da_etiqueta(values["frequencia_mhz"])
    passo_khz = _largura_da_etiqueta(values["passo"])

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

    alertas_frequencia = []
    consultas = []
    if frequencia is not None:
        consultas.append((frequencia, passo_khz or 0, values["frequencia_mhz"]))
    for frequencia_lista in values["frequencias_selecionadas"]:
        frequencia_cadastrada = _frequencia_da_etiqueta(frequencia_lista)
        if frequencia_cadastrada is not None:
            consultas.append(
                (
                    frequencia_cadastrada,
                    _largura_da_etiqueta(frequencia_lista),
                    frequencia_lista,
                )
            )
    for frequencia_consulta, largura_consulta, rotulo in consultas:
        consulta = consultar_equipamentos_frequencia(
            evento_id=evento_id,
            freq_digitada=frequencia_consulta,
            largura_khz=largura_consulta,
            localidade=values["local"],
            excluir_id=registro_id,
        )
        alertas_frequencia.extend(
            f"{rotulo}: {referencia.get('detalhe', 'emissão cadastrada')}"
            for referencia in consulta.get("referencias", [])
            if referencia.get("origem") == "Ocorrência"
        )

    dados = values
    dados["imagens"] = imagens
    if registro_id:
        resultado = atualizar_teste_etiquetagem(
            evento_id=evento_id, registro_id=registro_id, dados=dados
        )
    else:
        resultado = inserir_teste_etiquetagem(evento_id=evento_id, dados=dados)
    if resultado.startswith("ERRO"):
        return _render_form(request, values, resultado)

    if alertas_frequencia:
        resultado += (
            " ⚠️ AVISO: a frequência central e a banda informadas coincidem "
            "com emissão(ões) cadastrada(s): " + " ; ".join(alertas_frequencia)
        )
    request.session["flash_success"] = resultado
    if registro_id:
        consulta_query = "&consultar=1" if values["modo_consulta"] else ""
        return RedirectResponse(
            f"/teste_etiquetagem?edit_id={registro_id}{consulta_query}",
            status_code=303,
        )
    return RedirectResponse(
        (
            "/teste_etiquetagem?consultar=1"
            if values["modo_consulta"]
            else "/teste_etiquetagem"
        ),
        status_code=303,
    )


@router.get("/teste_etiquetagem/consultar", response_class=HTMLResponse)
async def consultar_testes_etiquetagem(request: Request):
    """Abre a consulta com a lista e o formulário no mesmo momento."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    return await get_teste_etiquetagem(request, consultar=True)


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
