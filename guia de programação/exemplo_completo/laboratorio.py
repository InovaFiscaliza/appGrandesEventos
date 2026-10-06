"""Exemplo didático independente. Execute da raiz: uv run uvicorn
laboratorio:app --app-dir "guia de programação/exemplo_completo" --reload --port 8502
"""
import os
from contextlib import asynccontextmanager
import secrets
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import dados_exemplo as dados

BASE = Path(__file__).resolve().parent
@asynccontextmanager
async def lifespan(app):
    dados.preparar()
    yield


app = FastAPI(title="Exemplo PostgreSQL — AppGrandesEventos", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("DEMO_SESSION_SECRET") or secrets.token_hex(32))
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def contexto(request):
    # Sessão simulada para estudar permissões, com IDs fictícios apenas no schema didático.
    request.session.setdefault("spreadsheet_id", 1)
    request.session.setdefault("fiscal_id", 1)
    request.session.setdefault("papel", "fiscal")
    return request.session


def pode_editar(session, tarefa):
    return session["papel"] == "coordenacao" or tarefa["fiscal_id"] == session["fiscal_id"]


def voltar(request, mensagem, erro=False):
    request.session["mensagem"] = {"texto": mensagem, "erro": erro}
    return RedirectResponse("/", status_code=303)


@app.get("/")
async def listar(request: Request):
    session = contexto(request)
    tarefas = dados.listar(session["spreadsheet_id"])
    for tarefa in tarefas:
        tarefa["pode_editar"] = pode_editar(session, tarefa)
    return templates.TemplateResponse(request, "tarefas.html", {
        "request": request, "tarefas": tarefas,
        "fiscais": dados.FISCAIS, "session": session,
        "mensagem": request.session.pop("mensagem", None),
        "total": len(tarefas),
        "pendentes": sum(t["status"] == "pendente" for t in tarefas),
    })


@app.post("/perfil")
async def perfil(request: Request):
    session = contexto(request)
    form = await request.form()
    perfil = str(form.get("perfil", ""))
    # Troca livre apenas nesta demonstração; não é autenticação.
    if perfil not in {"fiscal_1", "fiscal_2", "coordenacao"}:
        return voltar(request, "Perfil inválido.", True)
    session["papel"] = "coordenacao" if perfil == "coordenacao" else "fiscal"
    session["fiscal_id"] = 2 if perfil == "fiscal_2" else 1
    return voltar(request, "Perfil de demonstração alterado.")


@app.post("/tarefas")
async def criar(request: Request):
    session = contexto(request)
    form = await request.form()
    try:
        valores = dados.validar(form)
        if session["papel"] != "coordenacao" and valores["fiscal_id"] != session["fiscal_id"]:
            raise ValueError("O fiscal pode criar tarefas apenas para si.")
        dados.criar(session["spreadsheet_id"], valores)
    except ValueError as exc:
        return voltar(request, str(exc), True)
    return voltar(request, "Tarefa cadastrada.")


@app.post("/tarefas/{tarefa_id}/editar")
async def editar(request: Request, tarefa_id: int):
    session = contexto(request)
    form = await request.form()
    try:
        valores = dados.validar(form)
        # O serviço verifica também o registro atual dentro da transação.
        dados.editar(session["spreadsheet_id"], tarefa_id, valores,
                     session["fiscal_id"], session["papel"] == "coordenacao")
    except (ValueError, PermissionError) as exc:
        return voltar(request, str(exc), True)
    return voltar(request, "Alterações salvas.")


@app.post("/tarefas/{tarefa_id}/excluir")
async def excluir(request: Request, tarefa_id: int):
    session = contexto(request)
    if session["papel"] != "coordenacao":
        return voltar(request, "Somente a coordenação pode excluir tarefas.", True)
    if not dados.excluir(session["spreadsheet_id"], tarefa_id):
        return voltar(request, "Tarefa não encontrada neste evento.", True)
    return voltar(request, "Tarefa excluída.")
