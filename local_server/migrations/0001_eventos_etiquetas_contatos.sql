-- Evolucao aditiva: preserve os registros e as colunas legadas do servidor.
-- As tabelas-base eventos e testes_etiquetagem pertencem a versao existente.
ALTER TABLE eventos ADD COLUMN IF NOT EXISTS cidade TEXT;
ALTER TABLE eventos ADD COLUMN IF NOT EXISTS uf CHAR(2);
ALTER TABLE eventos ADD COLUMN IF NOT EXISTS teste_etiquetagem BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS numero_equipamentos INTEGER NOT NULL DEFAULT 1;
ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS responsavel_contato TEXT;
ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS telefone TEXT;
ALTER TABLE testes_etiquetagem ADD COLUMN IF NOT EXISTS email TEXT;

CREATE TABLE IF NOT EXISTS faixas_numeracao_etiqueta (
    id BIGSERIAL PRIMARY KEY,
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    permissao TEXT NOT NULL CHECK (permissao IN ('permitido', 'todos')),
    numero_inicial INTEGER NOT NULL CHECK (numero_inicial > 0),
    numero_final INTEGER NOT NULL CHECK (numero_final >= numero_inicial),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_faixas_numeracao_evento
    ON faixas_numeracao_etiqueta (evento_id, permissao);
