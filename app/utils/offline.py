"""
offline.py — Helpers para modo offline nos routers FastAPI.

Centraliza a lógica de:
  - Detecção de falha de conexão com Google Sheets
  - Preparação de dados para fila offline
  - Contexto padronizado para templates em modo offline

Uso nos routers:
    from app.utils.offline import tentar_conexao_ou_offline, pacote_offline_inserir

    client, offline_data = tentar_conexao_ou_offline()
    if client is None:
        return templates.TemplateResponse(..., offline_data)
"""

from typing import Any, Dict, Optional, Tuple


def tentar_conexao_ou_offline(
    obter_cliente: callable,
) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Tenta obter o cliente gspread. Se falhar (offline), retorna um dicionário
    com metadados indicando modo offline para o template.

    Args:
        obter_cliente: Função que retorna o cliente (ex: obter_cliente_gspread)

    Returns:
        (client, None) em caso de sucesso
        (None, offline_ctx) em caso de falha — offline_ctx é dict com offline_salvo e afins
    """
    try:
        client = obter_cliente()
        return client, None
    except Exception:
        return None, {"offline_salvo": False, "offline_dados": None}


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
        "UTE?": "1" if ute else "",
        "Processo SEI ou Ato UTE": form.get("proc", "").strip(),
        "Observações/Detalhes/Contatos": form.get("obs", "").strip(),
        "Responsável pela emissão": "",
        "Interferente?": form.get("interferente", ""),
        "Situação": form.get("situacao", "") or "Pendente",
    }
