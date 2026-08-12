from urllib.parse import quote

import logging

import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.datastructures import UploadFile

from app.services.postgres import (
    atualizar_campos_na_aba_mae,
    carregar_imagens_ocorrencia,
    carregar_imagem_ocorrencia,
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    consultar_historico_ocorrencia,
    listar_estacoes_evento,
)
from app.utils.formatters import _data_hora_foto, _img_b64
from app.utils.offline import extrair_dados_edicao, preparar_offline_ctx
from app.config import IDENT_OPCOES, TITULO_PRINCIPAL, USR_FISCAL_ANATEL

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
        "ident_opcoes": IDENT_OPCOES,
        **kwargs,
    }


def _load_pendencias(sp_id) -> pd.DataFrame:
    dfs = [
        d
        for d in [
            carregar_pendencias_painel_mapeadas(evento_id=sp_id),
            carregar_pendencias_todas_estacoes(evento_id=sp_id),
        ]
        if d is not None and not d.empty
    ]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def _make_row_key(row: pd.Series) -> str:
    return f"{row['Fonte']}|||{row['ID']}|||{row.get('EstacaoRaw', '')}"


def _make_label(row: pd.Series) -> str:
    parts = [
        str(row.get("Local", "")),
        str(row.get("Data", "")),
        f"{row.get('Frequência (MHz)', '')} MHz",
        str(row.get("Ocorrência (observações)", "")),
        f"ID {row.get('ID', '')}",
    ]
    return " | ".join(p for p in parts if p.strip() and p.strip() != " MHz")


@router.get("/consultar", response_class=HTMLResponse)
async def get_consultar(request: Request, key: str = ""):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    df = _load_pendencias(sp_id)
    estacoes = listar_estacoes_evento(evento_id=sp_id)

    pendencias = []
    selected_row = None

    if not df.empty:
        for _, row in df.iterrows():
            rk = _make_row_key(row)
            pendencias.append({"row_key": rk, "label": _make_label(row)})
            if key and rk == key:
                selected_row = row.to_dict()

    return templates.TemplateResponse(
        request,
        "consultar.html",
        _ctx(
            request,
            pendencias=pendencias,
            selected_key=key,
            selected_row=selected_row,
            estacoes=estacoes,
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.get("/consultar/historico", response_class=HTMLResponse)
async def get_historico_ocorrencia(request: Request, id: int | None = None):
    """Exibe o histórico de alterações da ocorrência selecionada."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return RedirectResponse("/", status_code=302)
    if id is None:
        request.session["flash_error"] = (
            "Selecione uma ocorrência para consultar o histórico."
        )
        return RedirectResponse("/consultar", status_code=303)

    historico = consultar_historico_ocorrencia(evento_id=evento_id, ocorrencia_id=id)
    return templates.TemplateResponse(
        request,
        "consultar_historico.html",
        {
            "request": request,
            "titulo": TITULO_PRINCIPAL,
            "img_b64_esq": _img_b64("anatel.png"),
            "img_b64_dir": _img_b64("anatelS.png"),
            "evento_nome": request.session.get("evento_nome", ""),
            "ocorrencia_id": id,
            "historico": historico,
        },
    )


@router.get("/consultar/historico/imagem/{imagem_id}")
async def get_imagem_historico(request: Request, imagem_id: int, ocorrencia_id: int):
    """Entrega uma imagem do histórico validando evento e ocorrência da sessão."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return Response(status_code=401)
    imagem = carregar_imagem_ocorrencia(evento_id, ocorrencia_id, imagem_id)
    if not imagem:
        return Response(status_code=404)
    return Response(content=bytes(imagem["conteudo"]), media_type=imagem["tipo_mime"])


@router.post("/consultar/salvar")
async def post_consultar_salvar(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    imagens, erros_imagens = await _ler_imagens(form)
    imagens_excluir = [
        int(valor)
        for valor in form.get("imagens_excluir", "").split(",")
        if valor.strip().isdigit()
    ]
    fonte = form.get("fonte", "")
    id_val = form.get("id_val", "")
    estacao_raw = form.get("estacao_raw", "")
    row_key = form.get("row_key", "")
    ident_edit = form.get("ident_edit", "")
    autz_edit = form.get("autz_edit", "")
    ute_check = bool(form.get("ute_check"))
    proc_edit = form.get("proc_edit", "").strip()
    obs_edit = form.get("obs_edit", "").strip()
    cient_edit = form.get("cient_edit", "").strip()
    interf_edit = form.get("interf_edit", "")
    situ_edit = form.get("situ_edit", "")
    estacao_id = form.get("estacao_id", "").strip()
    acao = form.get("acao", "salvar")

    erros = list(erros_imagens)
    if not ident_edit:
        erros.append("Identificação")
    if ute_check and not proc_edit:
        erros.append("Processo SEI (UTE)")
    if not estacao_id or not estacao_id.isdigit():
        erros.append("Estação utilizada")

    if erros:
        request.session["flash_error"] = "Faltam dados: " + ", ".join(erros)
        return RedirectResponse(f"/consultar?key={quote(row_key)}", status_code=303)

    pac = {
        "Identificação": ident_edit,
        "Autorizado?": autz_edit,
        "UTE?": "Sim" if ute_check else "Não",
        "Processo SEI UTE": proc_edit,
        "Ocorrência (observações)": obs_edit,
        "Alguém mais ciente?": cient_edit,
        "Interferente?": interf_edit,
        "Situação": situ_edit,
        "Estação ID": estacao_id,
    }

    res = ""
    falhou_conexao = False
    try:
        if fonte == "PAINEL":
            res = atualizar_campos_na_aba_mae(
                evento_id=sp_id,
                estacao_raw="PAINEL",
                id_ocorrencia=id_val,
                novos_valores=pac,
                usuario_fiscal=USR_FISCAL_ANATEL,
                imagens=imagens,
                imagens_excluir=imagens_excluir,
            )
        elif fonte == "ESTACAO":
            res = atualizar_campos_na_aba_mae(
                evento_id=sp_id,
                estacao_raw=estacao_raw,
                id_ocorrencia=id_val,
                novos_valores=pac,
                usuario_fiscal=USR_FISCAL_ANATEL,
                imagens=imagens,
                imagens_excluir=imagens_excluir,
            )
        else:
            res = "ERRO: origem da ocorrência inválida."
    except Exception as e:
        logging.error(f"Falha ao salvar edição (offline?): {e}")
        falhou_conexao = True

    # Offline / falha de conexão → devolve página com dados para fila local
    if falhou_conexao:
        dados_json = extrair_dados_edicao(form)
        return templates.TemplateResponse(
            request,
            "consultar.html",
            _ctx(
                request,
                pendencias=[],
                selected_key=row_key,
                selected_row=None,
                estacoes=listar_estacoes_evento(evento_id=sp_id),
                flash_success=None,
                flash_error=None,
                **preparar_offline_ctx(dados_json, "fila_edicoes"),
            ),
        )

    if res.startswith("ERRO") or res.startswith("Erro"):
        request.session["flash_error"] = res
    else:
        request.session["flash_success"] = res
    if acao == "salvar_proxima":
        proximas = _load_pendencias(sp_id)
        proxima_key = ""
        if not proximas.empty:
            for _, row in proximas.iterrows():
                candidata = _make_row_key(row)
                if candidata != row_key:
                    proxima_key = candidata
                    break
        destino = (
            f"/consultar?key={quote(proxima_key)}" if proxima_key else "/consultar"
        )
        return RedirectResponse(destino, status_code=303)
    return RedirectResponse("/consultar", status_code=303)


@router.get("/api/pendencias")
async def api_pendencias(request: Request):
    """Retorna pendências como JSON para uso offline (IndexedDB)."""
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    df = _load_pendencias(sp_id)
    if df.empty:
        return JSONResponse([])
    records = []
    for _, row in df.iterrows():
        id_ocorrencia = str(row.get("ID", ""))
        imagens = []
        if id_ocorrencia.isdigit():
            imagens = carregar_imagens_ocorrencia(
                evento_id=sp_id, ocorrencia_id=int(id_ocorrencia)
            )[:2]
        records.append(
            {
                "row_key": _make_row_key(row),
                "label": _make_label(row),
                "fonte": str(row.get("Fonte", "")),
                "id": str(row.get("ID", "")),
                "local": str(row.get("Local", "")),
                "fiscal": str(row.get("Fiscal", "")),
                "data": str(row.get("Data", "")),
                "hora": str(row.get("HH:mm", "")),
                "freq": str(row.get("Frequência (MHz)", "")),
                "largura": str(row.get("Largura (kHz)", "")),
                "faixa": str(row.get("Faixa de Frequência Envolvida", "")),
                "identificacao": str(row.get("Identificação", "")),
                "autorizado": str(row.get("Autorizado?", "")),
                "ute": str(row.get("UTE?", "")),
                "processo_sei": str(row.get("Processo SEI UTE", "")),
                "ocorrencia": str(row.get("Ocorrência (observações)", "")),
                "ciente": str(row.get("Alguém mais ciente?", "")),
                "interferente": str(row.get("Interferente?", "")),
                "situacao": str(row.get("Situação", "")),
                "estacao_raw": str(row.get("EstacaoRaw", "")),
                "estacao_id": str(row.get("EstacaoID", "")),
                "imagens": imagens,
            }
        )
    return JSONResponse(records)


@router.get("/api/ocorrencia-imagens")
async def api_ocorrencia_imagens(request: Request, id: int):
    """Retorna as imagens da ocorrência selecionada para exibição em miniatura."""
    evento_id = request.session.get("spreadsheet_id")
    if not evento_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    return JSONResponse(carregar_imagens_ocorrencia(evento_id, id))


@router.post("/api/consultar-salvar")
async def api_consultar_salvar(request: Request):
    """Recebe JSON da fila offline (IndexedDB/sync.js) e salva a edição na planilha."""
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return JSONResponse({"erro": "Sessão expirada"}, status_code=401)
    try:
        dados = await request.json()
    except Exception:
        return JSONResponse({"erro": "JSON inválido"}, status_code=400)

    fonte = dados.get("fonte", "")
    id_val = dados.get("id_val", "")
    estacao_raw = dados.get("estacao_raw", "")
    pac = {
        "Identificação": dados.get("Identificação", ""),
        "Autorizado?": dados.get("Autorizado?", ""),
        "UTE?": dados.get("UTE?", "Não"),
        "Processo SEI UTE": dados.get("Processo SEI UTE", ""),
        "Ocorrência (observações)": dados.get("Ocorrência (observações)", ""),
        "Alguém mais ciente?": dados.get("Alguém mais ciente?", ""),
        "Interferente?": dados.get("Interferente?", ""),
        "Situação": dados.get("Situação", ""),
        "Estação ID": str(dados.get("estacao_id", "")),
    }

    if fonte == "PAINEL":
        res = atualizar_campos_na_aba_mae(
            evento_id=sp_id,
            estacao_raw="PAINEL",
            id_ocorrencia=id_val,
            novos_valores=pac,
            usuario_fiscal=USR_FISCAL_ANATEL,
        )
    elif fonte == "ESTACAO":
        res = atualizar_campos_na_aba_mae(
            evento_id=sp_id,
            estacao_raw=estacao_raw,
            id_ocorrencia=id_val,
            novos_valores=pac,
            usuario_fiscal=USR_FISCAL_ANATEL,
        )
    else:
        return JSONResponse({"erro": "Origem da ocorrência inválida."}, status_code=400)

    if res.startswith("ERRO") or res.startswith("Erro"):
        return JSONResponse({"erro": res}, status_code=500)
    return JSONResponse({"ok": True})
