"""
Entry point da aplicação AppEventos (FastAPI + Jinja2).

Executar com:
    python main.py
  ou:
    uvicorn main:app --reload --port 8501
"""

import secrets

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import bsr_erb, busca, consultar, inserir, menu, selecao, tabela_ute

app = FastAPI(title="AppEventos", docs_url=None, redoc_url=None)

# Sessão via cookie assinado; secret aleatório por inicialização (aceitável para este app)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# Arquivos estáticos (CSS, imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=True)
