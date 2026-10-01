ALTER TABLE ocorrencias
    ADD COLUMN IF NOT EXISTS criado_por_fiscal_id BIGINT
    REFERENCES fiscais(id) ON DELETE SET NULL;

ALTER TABLE bsr_erb
    ADD COLUMN IF NOT EXISTS criado_por_fiscal_id BIGINT
    REFERENCES fiscais(id) ON DELETE SET NULL;

WITH candidatos AS (
    SELECT o.id, MIN(f.id) AS fiscal_id
    FROM ocorrencias o
    JOIN eventos_fiscais ef ON ef.evento_id = o.evento_id
    JOIN fiscais f ON f.id = ef.fiscal_id
    WHERE o.criado_por_fiscal_id IS NULL
      AND NULLIF(TRIM(o.fiscal), '') IS NOT NULL
      AND LOWER(TRIM(f.nome)) = LOWER(TRIM(o.fiscal))
    GROUP BY o.id
    HAVING COUNT(DISTINCT f.id) = 1
)
UPDATE ocorrencias o
SET criado_por_fiscal_id = candidatos.fiscal_id
FROM candidatos
WHERE o.id = candidatos.id;

WITH candidatos AS (
    SELECT b.id, MIN(f.id) AS fiscal_id
    FROM bsr_erb b
    JOIN eventos_fiscais ef ON ef.evento_id = b.evento_id
    JOIN fiscais f ON f.id = ef.fiscal_id
    WHERE b.criado_por_fiscal_id IS NULL
      AND NULLIF(TRIM(b.cadastrado_por), '') IS NOT NULL
      AND LOWER(TRIM(f.nome)) = LOWER(TRIM(b.cadastrado_por))
    GROUP BY b.id
    HAVING COUNT(DISTINCT f.id) = 1
)
UPDATE bsr_erb b
SET criado_por_fiscal_id = candidatos.fiscal_id
FROM candidatos
WHERE b.id = candidatos.id;

CREATE INDEX IF NOT EXISTS idx_ocorr_evento_criador
    ON ocorrencias (evento_id, criado_por_fiscal_id);

CREATE INDEX IF NOT EXISTS idx_bsr_erb_evento_criador
    ON bsr_erb (evento_id, criado_por_fiscal_id);