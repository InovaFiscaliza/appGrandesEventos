"""
offline.py — Helpers para modo offline nos routers FastAPI.

Centraliza a lógica de:
  - Preparação de dados para fila offline (modo WhatsApp)
  - Contexto padronizado para templates em modo offline

As funções aqui são usadas pelo frontend (IndexedDB / sync.js) para
armazenar e reenviar dados quando o servidor FastAPI estiver inacessível
(ex: uso em campo sem internet).

Uso nos routers:
    from app.utils.offline import preparar_offline_ctx, extrair_dados_inserir

    dados_json = extrair_dados_inserir(form)
    return templates.TemplateResponse(..., **preparar_offline_ctx(dados_json))
"""

from typing import Any, Dict


def preparar_offline_ctx(
    form_data: Dict[str, str],
    store_name: str = "fila_envio",
) -> Dict[str, Any]:
    """
    Prepara o contexto para o template quando o servidor detecta modo offline.
    O frontend (app.js) captura offline_salvo=True e salva no IndexedDB.

    Args:
        form_data: Dicionário com os dados do formulário para enviar depois
        store_name: Nome da store no IndexedDB (padrão: fila_envio)

    Returns:
        Dict com offline_salvo=True, offline_dados, offline_store
    """
    return {
        "offline_salvo": True,
        "offline_dados": form_data,
        "offline_store": store_name,
    }


def extrair_dados_inserir(form) -> Dict[str, str]:
    """
    Extrai os dados do formulário de inserção no formato esperado
    pela fila offline e pela API /api/inserir.

    Pode ser usado tanto pelo router quanto pelo frontend.
    """
    ute = bool(form.get("ute"))
    return {
        "Dia": form.get("dia", ""),
        "Hora": form.get("hora", ""),
        "Fiscal": form.get("fiscal", "").strip(),
        "Local/Região": form.get("local", "").strip(),
        "Frequência em MHz": form.get("freq", ""),
        "Largura em kHz": form.get("larg", ""),
        "Faixa de Frequência": form.get("faixa", ""),
        "Identificação": form.get("ident", ""),
        "Autorizado? (Q)": "",
        "Estação ID": form.get("estacao_id", "").strip(),
        "Fiscais participantes": form.getlist("fiscais_participantes"),
        "UTE?": "1" if ute else "",
        "Processo SEI ou Ato UTE": form.get("proc", "").strip(),
        "Observações/Detalhes/Contatos": form.get("obs", "").strip(),
        "Responsável pela emissão": "",
        "Interferente?": form.get("interferente", ""),
        "Situação": form.get("situacao", "") or "Pendente",
    }


def extrair_dados_edicao(form) -> Dict[str, str]:
    """
    Extrai os dados do formulário de edição de pendência (consultar) no formato
    esperado pela fila offline e pela API /api/consultar-salvar.
    """
    return {
        "fonte": form.get("fonte", ""),
        "id_val": form.get("id_val", ""),
        "estacao_raw": form.get("estacao_raw", ""),
        "estacao_id": form.get("estacao_id", "").strip(),
        "row_key": form.get("row_key", ""),
        "Identificação": form.get("ident_edit", ""),
        "Autorizado?": form.get("autz_edit", ""),
        "UTE?": "Sim" if form.get("ute_check") else "Não",
        "Processo SEI UTE": form.get("proc_edit", "").strip(),
        "Ocorrência (observações)": form.get("obs_edit", "").strip(),
        "Alguém mais ciente?": form.get("cient_edit", "").strip(),
        "Interferente?": form.get("interf_edit", ""),
        "Situação": form.get("situ_edit", ""),
    }
