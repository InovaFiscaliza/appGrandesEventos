# AppGrandesEventos

Sistema de monitoração de espectro eletromagnético para grandes eventos (Carnaval, Moto GP, etc.).

## Stack

- **Backend**: Python 3.13+, FastAPI + Jinja2
- **Banco**: PostgreSQL 16
- **Frontend**: HTML/CSS/JS com Jinja2 Templates

---

## 1. Subindo o PostgreSQL com Podman

### 1.1. Criar e iniciar o contêiner

Instalar o podman desktop, No PowerShell (Administrador): 

wsl--install

```PowerShell
podman run -d --name postgres_appeventos ^
  -e POSTGRES_USER=appeventos ^
  -e POSTGRES_PASSWORD=appeventos ^
  -e POSTGRES_DB=appeventos ^
  -p 5432:5432 ^
  docker.io/postgres:16
```

### 1.2. Verificar se o contêiner está rodando

```PowerShell
podman ps
```

Deverá listar o contêiner `postgres_appeventos` com status `Up`.

---

## 2. Restaurar o banco de dados

### 2.1. Copiar o dump para dentro do contêiner

```PowerShell
podman cp bd_backup/backup_20260714_154519.sql postgres_appeventos:/tmp/backup.sql
```

> Substitua o nome do arquivo pelo dump mais recente disponível em `bd_backup/`.

### 2.2. Executar o restore de dentro do contêiner

```PowerShell
podman exec -i postgres_appeventos psql -U appeventos -d appeventos -f /tmp/backup.sql
```

### 2.3. Verificar se o restore funcionou

```PowerShell
podman exec -i postgres_appeventos psql -U appeventos -d appeventos -c "\dt"
```

Deverá listar as tabelas: `eventos`, `estacoes`, `ocorrencias`, `tabela_ute`, `bsr_erb`, `opcoes_identificacao`.

---

## 3. Iniciar a aplicação

Com o PostgreSQL rodando e o banco restaurado:

```PowerShell
uv run main.py
```

A aplicação estará disponível em: **http://localhost:8501**

### Modo desenvolvimento (com reload automático)

```PowerShell
uv run uvicorn main:app --reload --port 8501
```

### Personalizar a conexão com o banco

Por padrão a aplicação usa:

```
postgresql+psycopg://appeventos:appeventos@localhost:5432/appeventos
```

Para usar credenciais diferentes, defina a variável de ambiente `DATABASE_URL`:

```PowerShell
set DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/nome_banco
uv run main.py
```

---

## 4. Parando o ambiente

```PowerShell
podman stop postgres_appeventos
podman rm postgres_appeventos    # remove o contêiner
```

---

## Comandos úteis do Podman

| Ação                        | Comando                                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Ver logs do banco             | `podman logs postgres_appeventos`                                                                                   |
| Acessar o shell do contêiner | `podman exec -it postgres_appeventos bash`                                                                          |
| Conectar direto no psql       | `podman exec -it postgres_appeventos psql -U appeventos -d appeventos`                                              |
| Backup do banco               | `podman exec postgres_appeventos pg_dump -U appeventos -d appeventos > bd_backup/backup_$(date +%Y%m%d_%H%M%S).sql` |
