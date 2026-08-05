# AppGrandesEventos — Instruções para IA

## Descrição do Projeto

AppGrandesEventos é um sistema de monitoração de espectro eletromagnético para grandes eventos (Carnaval, Moto GP, etc.). Ele permite o registro e consulta de emissões de radiofrequência, incluindo:

- **Ocorrências** (emissões monitoradas)
- **BSR/Jammer e ERB Fake** (interferências)
- **Tabela UTE** (usuários de espectro)
- **Estações de monitoração**

## Stack Tecnológica

- **Backend**: Python 3.13+, FastAPI + Jinja2
- **Banco**: PostgreSQL 16 via SQLAlchemy + psycopg (binary)
- **Frontend**: FastAPI com Jinja2 Templates e arquivos estáticos (CSS/JS)
- **Autenticação**: N/A (aplicação local/institucional)
- **PWA**: Service Worker para funcionalidade offline parcial (`app/static/sw.js`)
- **Dependências**: gerenciadas via `pyproject.toml` + `uv`
- **Gerenciador de pacotes**: `uv` — usar `uv add <pacote>` para instalar, `uv sync` para sincronizar, `uv run <script.py>` para executar scripts (não usar `pip install`)

## Estrutura do Projeto

```
app/
    __init__.py
    config.py              # Constantes e configurações centralizadas
    routers/               # Rotas FastAPI (menu, consultar, inserir, bsr_erb, etc.)
        menu.py            #   Rota principal /menu
        consultar.py       #   Rota /consultar
        inserir.py         #   Rota /inserir
        bsr_erb.py         #   Rota /bsr_erb
        busca.py           #   Rota /busca
        selecao.py         #   Rota / (seleção de evento)
        tabela_ute.py      #   Rota /tabela_ute
    services/
        db.py              # Engine SQLAlchemy central
        postgres.py        # Serviço de dados via PostgreSQL
    static/                # CSS, JS, Service Worker, manifest
    templates/             # Jinja2 templates HTML
        base.html          # Template base com layout padronizado
        partials/          # Componentes parciais (header)
    utils/
        formatters.py      # Funções utilitárias (imagens, normalização, coordenadas)
        offline.py         # Utilitários para modo offline
db/
    schema.sql             # Schema completo do PostgreSQL
scripts/
    executa_schema.py      # Script para executar schema.sql no banco
requisitos/                # Documentação de requisitos
```

## Padrões de Código

### Python
- **Versão**: Python 3.13+ (type hints obrigatórios, union types com `X | Y`)
- **Identação**: 4 espaços (PEP 8)
- **Docstrings**: """Docstrings descritivas""" em módulos e funções públicas
- **Imports**: ordem padrão: built-in → third-party → módulos do app
- **Nomes**: `snake_case` para funções/variáveis, `CamelCase` para classes
- **Banco**: SQLAlchemy core (text()) — NÃO usar ORM models
- **Erros**: try/except com logging, evitar silenciar exceções

### FastAPI (principal)
- Rotas definidas com `APIRouter()` nomeado como `router`
- Templates Jinja2 carregados com `Jinja2Templates(directory="app/templates")`
- Sessão gerenciada via `SessionMiddleware` com cookie assinado
- Dados da sessão: `spreadsheet_id`, `evento_nome`, `view`
- Respostas: `HTMLResponse`, `RedirectResponse` ou `TemplateResponse`
- Rotas sempre assíncronas (`async def`)
- Flash messages via `request.session.pop("flash_success/error", None)`

### Frontend (HTML/CSS/JS)
- HTML com Jinja2 (herança via `{% extends "base.html" %}`)
- CSS em `app/static/style.css`
- JavaScript modular em `app/static/*.js`
- Botões padronizados com altura via variável CSS `BTN_HEIGHT`
- PWA: arquivos em `app/static/` (sw.js, manifest.json, offline.html)

### Configurações
- Constantes centralizadas em `app/config.py`
- Conexão DB em `app/services/db.py` (lê: env → secrets.toml → fallback local)
- Variáveis de ambiente: `DATABASE_URL`

### Scripts
- `sys.path.insert(0, ".")` necessário para executar scripts da raiz
- Execução via `uv run scripts/<script>.py` ou `python <script>.py`

## Regras de Estilo para Frontend

- No FastAPI, botões e links seguem design consistente via `base.html`
- Cores institucionais (ANATEL): azul escuro predominante
- Interface responsiva e mobile-first (app usado em campo com celular)
- Ícones: emojis (📋, 📝, 📵, etc.) nos botões
- Flash messages para feedback ao usuário
