-- Schema do banco de dados AppEventos
-- PostgreSQL 16+
-- Criado conforme documento de migração Google Sheets → PostgreSQL

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================
-- Tabelas
-- ============================================================

-- Um registro por evento (substitui "1 planilha = 1 evento")
CREATE TABLE IF NOT EXISTS eventos (
    id              BIGSERIAL PRIMARY KEY,
    nome            TEXT NOT NULL UNIQUE,
    legacy_sheet_id TEXT,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    fuso_horario    TEXT DEFAULT 'America/Sao_Paulo',
    observacoes     TEXT,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Estações (substitui "abas de estação")
CREATE TABLE IF NOT EXISTS estacoes (
    id          BIGSERIAL PRIMARY KEY,
    evento_id   BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    nome        TEXT NOT NULL,
    modelo_equipamento TEXT,
    local       TEXT,
    cidade      TEXT,
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    UNIQUE (evento_id, nome)
);

-- Ocorrências/emissões (unifica PAINEL + Abordagem + abas de estação)
CREATE TABLE IF NOT EXISTS ocorrencias (
    id                BIGSERIAL PRIMARY KEY,
    evento_id         BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    estacao_id        BIGINT REFERENCES estacoes(id) ON DELETE SET NULL,
    id_planilha       TEXT,        -- ID original da planilha (ex: "Abo-100", "1-RF02")
    local_regiao      TEXT,
    fiscal            TEXT,
    data              DATE,
    hora              TIME,
    frequencia_mhz    NUMERIC(12,3),
    largura_khz       NUMERIC(12,3),
    faixa             TEXT,
    identificacao     TEXT,
    autorizado        TEXT,
    ute               BOOLEAN DEFAULT FALSE,
    processo_sei_ute  TEXT,
    observacoes       TEXT,
    alguem_ciente     TEXT,
    interferente      TEXT,
    situacao          TEXT NOT NULL DEFAULT 'Pendente',
    fonte             TEXT,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_ocorr_evento_situacao ON ocorrencias (evento_id, situacao);
CREATE INDEX IF NOT EXISTS idx_ocorr_frequencia      ON ocorrencias (evento_id, frequencia_mhz);
CREATE INDEX IF NOT EXISTS idx_ocorr_busca_trgm      ON ocorrencias USING gin (observacoes gin_trgm_ops);

-- Imagens anexadas às emissões/ocorrências.
CREATE TABLE IF NOT EXISTS ocorrencia_imagens (
    id              BIGSERIAL PRIMARY KEY,
    ocorrencia_id   BIGINT NOT NULL REFERENCES ocorrencias(id) ON DELETE CASCADE,
    nome_arquivo    TEXT NOT NULL,
    tipo_mime       TEXT NOT NULL,
    tamanho_bytes   INTEGER NOT NULL,
    conteudo        BYTEA NOT NULL,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ocorrencia_imagens_ocorrencia
    ON ocorrencia_imagens (ocorrencia_id, id);

-- Histórico de alterações das ocorrências para auditoria do sistema.
CREATE TABLE IF NOT EXISTS auditoria_ocorrencias (
    id              BIGSERIAL PRIMARY KEY,
    ocorrencia_id   BIGINT NOT NULL REFERENCES ocorrencias(id) ON DELETE CASCADE,
    evento_id       BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    usuario_fiscal  TEXT NOT NULL,
    campo           TEXT NOT NULL,
    valor_anterior  TEXT,
    valor_novo      TEXT,
    modificado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_ocorrencia_data
    ON auditoria_ocorrencias (ocorrencia_id, modificado_em DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_evento_data
    ON auditoria_ocorrencias (evento_id, modificado_em DESC);

-- Tabela UTE
CREATE TABLE IF NOT EXISTS tabela_ute (
    id              BIGSERIAL PRIMARY KEY,
    evento_id       BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    id_planilha     TEXT,        -- ID original da planilha
    pais_entidade   TEXT,
    local           TEXT,
    frequencia_mhz  NUMERIC(12,3),
    processo_sei    TEXT
);
CREATE INDEX IF NOT EXISTS idx_ute_evento_freq ON tabela_ute (evento_id, frequencia_mhz);

-- BSR / Jammer / ERB
CREATE TABLE IF NOT EXISTS bsr_erb (
    id          BIGSERIAL PRIMARY KEY,
    evento_id   BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    tipo        TEXT NOT NULL,
    regiao      TEXT,
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Opções de identificação (substitui LISTAS)
CREATE TABLE IF NOT EXISTS opcoes_identificacao (
    id          BIGSERIAL PRIMARY KEY,
    evento_id   BIGINT REFERENCES eventos(id) ON DELETE CASCADE,
    valor       TEXT NOT NULL
);

-- Teste e etiquetagem de equipamentos
CREATE TABLE IF NOT EXISTS testes_etiquetagem (
    id                        BIGSERIAL PRIMARY KEY,
    evento_id                 BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    licenca                   TEXT NOT NULL CHECK (licenca IN (
                                  'ute', 'outorgado', 'nao_outorgado', 'radiacao_restrita'
                              )),
    perfil                    TEXT NOT NULL CHECK (perfil IN (
                                  'pf', 'pj', 'estrangeiro'
                              )),
    entidade                  TEXT NOT NULL,
    contato                   TEXT,
    local                     TEXT NOT NULL,
    cpf_cnpj                  TEXT,
    equipamento_homologado   BOOLEAN NOT NULL DEFAULT FALSE,
    permissao                 TEXT NOT NULL CHECK (permissao IN (
                                  'permitido', 'todos', 'nao'
                              )),
    frequencias_selecionadas  TEXT[] NOT NULL DEFAULT '{}',
    tipo_equipamento          TEXT NOT NULL,
    numero_etiqueta           TEXT NOT NULL,
    observacoes               TEXT,
    criado_em                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em             TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (evento_id, numero_etiqueta)
);

-- Migra os valores legados para a etiqueta completa antes de remover as colunas.
DO $do$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'testes_etiquetagem'
          AND column_name = 'frequencia_mhz'
    ) THEN
        EXECUTE $migration$
            UPDATE testes_etiquetagem
            SET frequencias_selecionadas = array_append(
                COALESCE(frequencias_selecionadas, '{}'),
                replace(to_char(frequencia_mhz, 'FM999999990.000'), '.', ',')
                    || ' MHz ⌂ '
                    || COALESCE(rtrim(rtrim(to_char(passo_khz, 'FM999999990.999'), '0'), '.'), '')
                    || ' kHz • ' || COALESCE(faixa, '')
            )
            WHERE frequencia_mhz IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM unnest(COALESCE(frequencias_selecionadas, '{}')) AS existente
                  WHERE existente LIKE replace(to_char(frequencia_mhz, 'FM999999990.000'), '.', ',')
                      || ' MHz ⌂%'
              )
        $migration$;
    END IF;
    END $do$;

-- Remove campos legados: a etiqueta completa fica em frequencias_selecionadas.
ALTER TABLE testes_etiquetagem DROP COLUMN IF EXISTS frequencia_mhz;
ALTER TABLE testes_etiquetagem DROP COLUMN IF EXISTS passo_khz;
ALTER TABLE testes_etiquetagem DROP COLUMN IF EXISTS faixa;

CREATE INDEX IF NOT EXISTS idx_etiquetagem_evento_entidade
    ON testes_etiquetagem (evento_id, entidade);

-- ============================================================
-- Trigger para atualizar atualizado_em automaticamente
-- ============================================================
CREATE OR REPLACE FUNCTION set_atualizado_em() RETURNS trigger AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ocorr_upd ON ocorrencias;
CREATE TRIGGER trg_ocorr_upd
    BEFORE UPDATE ON ocorrencias
    FOR EACH ROW
    EXECUTE FUNCTION set_atualizado_em();

DROP TRIGGER IF EXISTS trg_etiquetagem_upd ON testes_etiquetagem;
CREATE TRIGGER trg_etiquetagem_upd
    BEFORE UPDATE ON testes_etiquetagem
    FOR EACH ROW
    EXECUTE FUNCTION set_atualizado_em();