# Backups do banco de dados AppEventos

Este diretório contém os arquivos de backup gerados pelo script:

```bash
uv run python scripts/backup_db.py
```

Os arquivos seguem o padrão: `backup_YYYYMMDD_HHMMSS.sql`

.## Regras
- Backups são **.gitignore** (não versionar)
- Para restaurar: `psql -U appeventos -d appeventos -f bd_backup/<arquivo>.sql`