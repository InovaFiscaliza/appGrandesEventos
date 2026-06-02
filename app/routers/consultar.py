from urllib.parse import quote

import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.google_sheets import (
    atualizar_campos_abordagem_por_id,
    atualizar_campos_na_aba_mae,
    carregar_pendencias_abordagem_pendentes,
    carregar_pendencias_painel_mapeadas,
    carregar_pendencias_todas_estacoes,
    obter_cliente_gspread,
)
from app.utils.formatters import _img_b64
from app.config import IDENT_OPCOES, TITULO_PRINCIPAL

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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


def _load_pendencias(client, sp_id) -> pd.DataFrame:
    dfs = [
        d
        for d in [
            carregar_pendencias_painel_mapeadas(client, sp_id),
            carregar_pendencias_abordagem_pendentes(client, sp_id),
            carregar_pendencias_todas_estacoes(client, sp_id),
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

    client = obter_cliente_gspread()
    df = _load_pendencias(client, sp_id)

    pendencias = []
    selected_row = None

    if not df.empty:
        for _, row in df.iterrows():
            rk = _make_row_key(row)
            pendencias.append({"row_key": rk, "label": _make_label(row)})
            if key and rk == key:
                selected_row = row.to_dict()

    return templates.TemplateResponse(
        "consultar.html",
        _ctx(
            request,
            pendencias=pendencias,
            selected_key=key,
            selected_row=selected_row,
            flash_success=request.session.pop("flash_success", None),
            flash_error=request.session.pop("flash_error", None),
        ),
    )


@router.post("/consultar/salvar")
async def post_consultar_salvar(request: Request):
    sp_id = request.session.get("spreadsheet_id")
    if not sp_id:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
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

    erros = []
    if not ident_edit:
        erros.append("Identificação")
    if ute_check and not proc_edit:
        erros.append("Processo SEI (UTE)")

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
    }

    client = obter_cliente_gspread()
    if fonte in ("PAINEL", "ESTACAO"):
        res = atualizar_campos_na_aba_mae(client, sp_id, estacao_raw, id_val, pac)
    else:
        res = atualizar_campos_abordagem_por_id(client, sp_id, id_val, pac)

    request.session["flash_success"] = res
    return RedirectResponse("/consultar", status_code=303)
