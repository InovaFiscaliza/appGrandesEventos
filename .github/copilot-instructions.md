# AppGrandesEventos — Instruções para IA

## Descrição do Projeto

AppGrandesEventos é um sistema de monitoração de espectro eletromagnético para grandes eventos (Carnaval, Moto GP, etc.). Ele permite o registro e consulta de emissões de radiofrequência, incluindo:

- **Ocorrências** (emissões monitoradas)
- **BSR/Jammer e ERB Fake** (interferências)
- **Tabela UTE** (usuários de espectro)
- **Estações de monitoração**

## Stack Tecnológica

- **Backend**: Python 3.13+, FastAPI + Jinja2 (primário), Streamlit (legado)
- **Banco**: PostgreSQL 16 via SQLAlchemy + psycopg (binary)
- **Frontend**: FastAPI com Jinja2 Templates e arquivos estáticos (CSS/JS)
- **Autenticação**: N/A (aplicação local/institucional)
- **Google Sheets**: Integração via `gspread` (leitura de dados legados)
- **PWA**: Service Worker para funcionalidade offline parcial (`app/static/sw.js`)
- **Dependências**: gerenciadas via `pyproject.toml` + `uv`
- **Gerenciador de pacotes**: `uv` — usar `uv add <pacote>` para instalar, `uv sync` para sincronizar, `uv run <script.py>` para executar scripts (não usar `pip install`)

## Estrutura do Projeto

```
app/
    __init__.py
    config.py              # Constantes e configurações centralizadas
    router.py              # Roteador Streamlit (legado)
    components/            # Componentes reutilizáveis Streamlit (header, botoes)
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
        google_sheets.py   # Serviço legado de acesso ao Google Sheets
        postgres.py        # Serviço de dados via PostgreSQL (substituto)
    static/                # CSS, JS, Service Worker, manifest
    templates/             # Jinja2 templates HTML
        base.html          # Template base com layout padronizado
        partials/          # Componentes parciais (header)
    utils/
        formatters.py      # Funções utilitárias (imagens, normalização, coordenadas)
        offline.py         # Utilitários para modo offline
    views/                 # Views Streamlit (legado)
db/
    schema.sql             # Schema completo do PostgreSQL
scripts/
    migrar_sheets_to_pg.py # Migração Google Sheets → PostgreSQL
    validar_migracao.py    # Validação de consistência dos dados
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

### Streamlit (legado)
- Views recebem `(client, spread_id)` como parâmetros
- Navegação via `st.session_state.view`
- Componentes em `app/components/` e views em `app/views/`
- `st.rerun()` após alterar `st.session_state.view`

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

- Botões devem usar `use_container_width=True` no Streamlit
- No FastAPI, botões e links seguem design consistente via `base.html`
- Cores institucionais (ANATEL): azul escuro predominante
- Interface responsiva e mobile-first (app usado em campo com celular)
- Ícones: emojis (📋, 📝, 📵, etc.) nos botões
- Flash messages para feedback ao usuário

## Regras para Migração (Google Sheets → PostgreSQL)

- Funções `_parse_float`, `_parse_date`, `_parse_time` para normalizar dados
- Vírgula como separador decimal, ponto como separador de milhar
- Scripts idempotentes (`ON CONFLICT`, `DELETE` antes de reinserir)
- Dados do Sheets lidos via `gspread` com intervalo de colunas (ex: `"H1:W"`)
- Tabelas: `eventos`, `estacoes`, `ocorrencias`, `tabela_ute`, `bsr_erb`, `opcoes_identificacao`