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
- **Referência visual**: OutSystems/RF.Fusion, com recursos preservados em `app/static/rf-fusion/`
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
    static/                # CSS, JS, Service Worker, manifest e recursos OutSystems/RF.Fusion
        rf-fusion/         # CSS e recursos visuais de referência do OutSystems/RF.Fusion
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

### Legibilidade para Usuários Humanos

- Escrever código para ser lido e mantido por pessoas, não apenas para executar.
- Preferir nomes descritivos, fluxo explícito e funções pequenas a abreviações, compactação excessiva ou lógica indireta.
- Manter formatação consistente e separar responsabilidades quando um trecho ficar difícil de entender.
- Usar comentários e docstrings para explicar decisões e regras de negócio, sem comentários óbvios ou redundantes.
- Evitar abstrações, encadeamentos e expressões complexas quando uma implementação mais simples tornar o comportamento mais claro.
- Ao alterar código existente, preservar o estilo local e deixar a intenção da mudança evidente.

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
- Botões de adicionar representados por `+` devem seguir o padrão visual `.teq-list-btn` do teste de etiquetagem e ficar alinhados à direita quando estiverem acima de um campo.
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
- Preservar a compatibilidade visual com OutSystems/RF.Fusion ao alterar telas e componentes.
- Não remover, substituir ou reformatar em massa os arquivos de referência em `app/static/rf-fusion/`.
- Cores institucionais (ANATEL): azul escuro predominante
- Interface responsiva e mobile-first (app usado em campo com celular)
- Ícones: emojis (📋, 📝, 📵, etc.) nos botões
- Flash messages para feedback ao usuário
- Em tabelas com ações, a célula de botões deve ocupar somente o espaço necessário dos botões (sem largura fixa sobrando).

## Lembretes Funcionais — Fotos

- Fotos de BSR/Jammer e ERB Fake devem ser nomeadas automaticamente nesta ordem:
  `NomeEvento_Classificacao_ID_Registro_Data_Hora_Sequencia.extensao`.
- O nome deve preservar a extensão original e substituir caracteres inválidos por `_`.
- O nome da foto deve aparecer somente no popup de visualização ampliada, centralizado abaixo da imagem; não exibir nomes nas listas e miniaturas para evitar poluição visual.
- Ao editar um registro BSR/Jammer ou ERB Fake, as fotos já anexadas devem aparecer no formulário junto com o controle para incluir novas fotos.
- Cada foto existente no modo de edição deve possuir lixeira própria, exigir confirmação antes da exclusão e registrar a ação na auditoria BSR/ERB.
- A exclusão de uma foto não pode excluir o registro da ocorrência nem as demais fotos.

## Lembrete Obrigatório — Auditoria

- Sempre lembrar da auditoria ao criar, editar ou excluir dados do sistema.
- Toda alteração relevante deve registrar origem, registro afetado, usuário, campo alterado, valor anterior e valor novo.
- Inclusões e exclusões de imagens, registros e vínculos também devem gerar auditoria específica.
- Antes de concluir uma alteração, verificar se a consulta de auditoria consegue exibir o novo registro corretamente.

## Lembrete Obrigatório — Validação de Frequências

- No **Teste de etiquetagem** e no **Cadastro de emissões**, toda frequência incluída ou alterada deve ser consultada no banco antes da conclusão.
- No teste de etiquetagem, comparar a frequência central e a banda ocupada também com as emissões cadastradas no mesmo evento e localidade, inclusive as emissões dos fiscais de campo.
- Essa comparação é somente informativa: deve alertar o fiscal com a frequência central, a banda e os dados disponíveis da emissão, mas nunca impedir a inclusão, edição ou conclusão do teste de etiquetagem.
- A consulta deve ocorrer tanto para um novo registro quanto para a edição de um registro existente, desconsiderando o próprio registro em edição quando aplicável.
- Se houver conflito com equipamento, emissão ou outro cadastro, a tela deve alertar imediatamente o fiscal responsável pelo processo, identificando a entidade, o tipo, a etiqueta e o local quando esses dados estiverem disponíveis.
- O alerta deve aparecer durante a inclusão/alteração e não pode ficar restrito a uma mensagem genérica após o salvamento.
- A validação de interface não substitui a consulta no backend: o backend deve repetir a consulta no salvamento para gerar o mesmo alerta, inclusive nos fluxos offline/API, sem bloquear a conclusão por conflito de frequência.
- A comparação deve usar a precisão normalizada definida pelo sistema e, quando aplicável, considerar a sobreposição entre frequência central e largura de banda.
