# Tela de exemplo baseada no AppGrandesEventos — PostgreSQL

Stack: FastAPI + Jinja2 + HTML/CSS/JavaScript + SQLAlchemy + psycopg + PostgreSQL.
O serviço importa `get_engine` de `app/services/db.py`, o mesmo módulo de conexão
usado por `app/services/postgres.py` no sistema real.

## Executar no PowerShell, a partir da raiz do projeto

Aponte DATABASE_URL para um PostgreSQL de desenvolvimento já existente.
Substitua os valores abaixo; o exemplo não cria um banco PostgreSQL.

```powershell
$env:DATABASE_URL = "postgresql+psycopg://USUARIO:SENHA@127.0.0.1:5432/BANCO_DESENVOLVIMENTO"
uv run uvicorn laboratorio:app --app-dir "guia de programação/exemplo_completo" --reload --port 8502
```

Abra http://localhost:8502. Ctrl+C encerra. Não é necessário parar o sistema
na porta 8501. O nome `laboratorio.py` evita conflito com o pacote `app` real.

Ao iniciar, `schema.sql` cria `guia_programacao.tarefas`. O usuário PostgreSQL
precisa poder criar esse schema e suas tabelas. O exemplo não escreve nas
tabelas reais de ocorrências, incidentes, tickets ou fiscais.

## O que estudar

- `dados_exemplo.py`: `get_engine().connect()` para leitura,
  `get_engine().begin()` para gravação, `text()` e parâmetros nomeados.
- `schema.sql`: BIGINT IDENTITY, TIMESTAMPTZ, CHECK e índice PostgreSQL.
- `laboratorio.py`: FastAPI, sessão, rotas GET/POST e redirecionamento 303.
- `templates/tarefas.html`: contexto Jinja2, tabela e formulário de popup.
- `static/tarefas.js`: seleção da tarefa, preenchimento e busca.

Na sessão do exemplo, `spreadsheet_id` representa o evento, seguindo a
convenção do AppGrandesEventos. O evento 1 e os fiscais Ana/Bruno são fictícios
apenas no schema didático; não são vínculos às tabelas reais do sistema.

## Experimente

1. Como Ana, crie e edite uma tarefa; recarregue e confirme a persistência.
2. Troque para Bruno: a tarefa de Ana fica somente para leitura.
3. Como Coordenação, reatribua ou exclua a tarefa.
4. Tente título curto ou status inválido: o serviço deve recusar.
5. Em Network, siga POST → 303 → GET.

A troca livre de perfil é uma simulação para aprender autorização e não é
login real. Para integrar ao sistema, use APIRouter, os templates base e
as permissões reais, prepare migração e relações com eventos/fiscais.
O laboratório não implementa anexos, auditoria, offline ou CSRF de produção.
A chave da sessão é temporária; DEMO_SESSION_SECRET permite definir um segredo
estável de desenvolvimento. O guia inclui trechos dos arquivos reais do sistema.
