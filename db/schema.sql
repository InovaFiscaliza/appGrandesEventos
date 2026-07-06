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
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Estações (substitui "abas de estação")
CREATE TABLE IF NOT EXISTS estacoes (
    id          BIGSERIAL PRIMARY KEY,
    evento_id   BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    nome        TEXT NOT NULL,
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    UNIQUE (evento_id, nome)
);

-- Ocorrências/emissões (unifica PAINEL + Abordagem + abas de estação)
CREATE TABLE IF NOT EXISTS ocorrencias (
    id                BIGSERIAL PRIMARY KEY,
    evento_id         BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    estacao_id        BIGINT REFERENCES estacoes(id) ON DELETE SET NULL,
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

-- Tabela UTE
CREATE TABLE IF NOT EXISTS tabela_ute (
    id              BIGSERIAL PRIMARY KEY,
    evento_id       BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
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