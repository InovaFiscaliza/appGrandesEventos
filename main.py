"""
Entry point da aplicação AppEventos (FastAPI + Jinja2).

Executar com:
    uv run main.py
    uv run uvicorn main:app --reload --port 8501
  ou:
    uvicorn main:app --reload --port 8501
"""

import secrets
import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import (
    bsr_erb,
    busca,
    consultar,
    inserir,
    menu,
    selecao,
    tabela_ute,
    teste_etiquetagem,
)
from app.services.postgres import buscar_planilhas

_inicio_aplicacao = time.perf_counter()


def _mensagem_inicializacao(mensagem: str) -> None:
    """Exibe uma etapa de inicialização imediatamente no terminal."""
    decorrido = time.perf_counter() - _inicio_aplicacao
    print(f"[AppEventos {decorrido:7.2f}s] {mensagem}", flush=True)


_mensagem_inicializacao("Módulos Python carregados")
app = FastAPI(title="AppEventos", docs_url=None, redoc_url=None)
_mensagem_inicializacao("Aplicação FastAPI criada")

# Sessão via cookie assinado; secret aleatório por inicialização (aceitável para este app)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))
_mensagem_inicializacao("Middleware de sessão configurado")


@app.on_event("startup")
async def registrar_aplicacao_pronta():
    """Registra quando o Uvicorn conclui a inicialização da aplicação."""
    _mensagem_inicializacao("Aplicação pronta para receber requisições")


@app.middleware("http")
async def carregar_eventos_no_request(request: Request, call_next):
    """Disponibiliza a lista de eventos para o cabeçalho compartilhado."""
    inicio_requisicao = time.perf_counter()
    caminho = request.url.path

    if (
        caminho.startswith("/static/")
        or caminho == "/sw.js"
        or caminho.startswith("/api/")
    ):
        resposta = await call_next(request)
        return resposta

    _mensagem_inicializacao(
        f"Requisição recebida: {request.method} {caminho}; carregando eventos"
    )
    # A tela de histórico já possui o evento na sessão. Não bloqueie sua
    # abertura com a consulta síncrona da lista completa de eventos.
    if caminho == "/consultar/historico":
        request.state.eventos = {}
    else:
        inicio_eventos = time.perf_counter()
        request.state.eventos = buscar_planilhas()
        _mensagem_inicializacao(
            "Lista de eventos carregada em "
            f"{time.perf_counter() - inicio_eventos:.2f}s"
        )

    resposta = await call_next(request)
    _mensagem_inicializacao(
        f"Resposta concluída em {time.perf_counter() - inicio_requisicao:.2f}s: "
        f"{request.method} {caminho} ({resposta.status_code})"
    )
    return resposta


# Arquivos estáticos (CSS, imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
_mensagem_inicializacao("Arquivos estáticos montados")


# Service Worker deve ser servido da raiz para ter escopo sobre todo o app
@app.get("/sw.js", include_in_schema=False)
async def service_worker():
    return FileResponse("app/static/sw.js", media_type="application/javascript")


# Routers
app.include_router(selecao.router)
app.include_router(menu.router)
app.include_router(inserir.router)
app.include_router(consultar.router)
app.include_router(bsr_erb.router)
app.include_router(busca.router)
app.include_router(tabela_ute.router)
app.include_router(teste_etiquetagem.router)
_mensagem_inicializacao("Rotas carregadas; finalizando inicialização")

if __name__ == "__main__":
    import uvicorn

    _mensagem_inicializacao("Iniciando servidor em http://0.0.0.0:8501")
    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=False)


def start():
    """Função chamada por 'uv run app' (definido em pyproject.toml)."""
    import uvicorn

    _mensagem_inicializacao("Iniciando servidor em http://0.0.0.0:8501")
    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=False)
