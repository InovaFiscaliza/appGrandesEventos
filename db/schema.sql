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
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    fuso_horario    TEXT DEFAULT 'America/Sao_Paulo',
    cidade          TEXT,
    uf              CHAR(2),
    acao_fiscalizacao TEXT,
    processo_sei    TEXT,
    periodo_inicio  DATE,
    periodo_fim     DATE,
    teste_etiquetagem BOOLEAN NOT NULL DEFAULT TRUE,
    observacoes     TEXT,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE eventos ADD COLUMN IF NOT EXISTS cidade TEXT;
ALTER TABLE eventos ADD COLUMN IF NOT EXISTS uf CHAR(2);
ALTER TABLE eventos ADD COLUMN IF NOT EXISTS teste_etiquetagem BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE eventos DROP COLUMN IF EXISTS local;

CREATE TABLE IF NOT EXISTS unidades_executantes (
    sigla TEXT PRIMARY KEY,
    nome TEXT NOT NULL
);

-- Fiscais disponíveis globalmente para todos os eventos
CREATE TABLE IF NOT EXISTS fiscais (
    id            BIGSERIAL PRIMARY KEY,
    nome          TEXT NOT NULL,
    local_anatel  TEXT NOT NULL REFERENCES unidades_executantes(sigla),
    funcao_evento TEXT NOT NULL CHECK (funcao_evento IN ('Coordenação', 'Abordagem', 'Monitoração')),
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (nome, local_anatel, funcao_evento)
);

CREATE INDEX IF NOT EXISTS idx_fiscais_nome ON fiscais (nome);

CREATE TABLE IF NOT EXISTS municipios (
    codigo_ibge BIGINT PRIMARY KEY,
    nome        TEXT NOT NULL,
    uf          CHAR(2) NOT NULL,
    UNIQUE (nome, uf)
);

CREATE INDEX IF NOT EXISTS idx_municipios_uf_nome
    ON municipios (uf, nome);

CREATE TABLE IF NOT EXISTS eventos_fiscais (
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    fiscal_id BIGINT NOT NULL REFERENCES fiscais(id) ON DELETE CASCADE,
    PRIMARY KEY (evento_id, fiscal_id)
);

CREATE TABLE IF NOT EXISTS eventos_coordenadores (
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    fiscal_id BIGINT NOT NULL REFERENCES fiscais(id) ON DELETE CASCADE,
    PRIMARY KEY (evento_id, fiscal_id),
    FOREIGN KEY (evento_id, fiscal_id)
        REFERENCES eventos_fiscais(evento_id, fiscal_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_eventos_coordenadores_fiscal
    ON eventos_coordenadores (fiscal_id);

CREATE TABLE IF NOT EXISTS tickets (
    id BIGSERIAL PRIMARY KEY,
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    ocorrencia_id BIGINT REFERENCES ocorrencias(id) ON DELETE CASCADE,
    fiscal_id BIGINT REFERENCES fiscais(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'concluido')),
    prioridade TEXT NOT NULL DEFAULT 'normal' CHECK (prioridade IN ('baixa', 'normal', 'alta')),
    observacoes TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tickets_evento_status
    ON tickets (evento_id, status, fiscal_id);

CREATE TABLE IF NOT EXISTS ticket_ocorrencias (
    ticket_id BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    ocorrencia_id BIGINT NOT NULL REFERENCES ocorrencias(id) ON DELETE CASCADE,
    PRIMARY KEY (ticket_id, ocorrencia_id)
);

INSERT INTO ticket_ocorrencias (ticket_id, ocorrencia_id)
SELECT id, ocorrencia_id
FROM tickets
WHERE ocorrencia_id IS NOT NULL
ON CONFLICT DO NOTHING;

ALTER TABLE tickets ALTER COLUMN ocorrencia_id DROP NOT NULL;
ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_evento_id_ocorrencia_id_key;

CREATE INDEX IF NOT EXISTS idx_ticket_ocorrencias_ocorrencia
    ON ticket_ocorrencias (ocorrencia_id);

CREATE TABLE IF NOT EXISTS ticket_fiscais (
    ticket_id BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    fiscal_id BIGINT NOT NULL REFERENCES fiscais(id) ON DELETE CASCADE,
    PRIMARY KEY (ticket_id, fiscal_id)
);

CREATE INDEX IF NOT EXISTS idx_ticket_fiscais_fiscal
    ON ticket_fiscais (fiscal_id);

CREATE TABLE IF NOT EXISTS escalas_trabalho (
    id BIGSERIAL PRIMARY KEY,
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    fiscal_id BIGINT NOT NULL REFERENCES fiscais(id) ON DELETE CASCADE,
    data_trabalho DATE NOT NULL,
    turno_inicio TIME,
    turno_fim TIME,
    observacoes TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (evento_id, fiscal_id, data_trabalho, turno_inicio, turno_fim)
);

CREATE INDEX IF NOT EXISTS idx_escalas_trabalho_evento_data
    ON escalas_trabalho (evento_id, data_trabalho, fiscal_id);

ALTER TABLE eventos DROP COLUMN IF EXISTS coordenador_responsavel;

CREATE TABLE IF NOT EXISTS eventos_unidades_executantes (
    evento_id BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    unidade_sigla TEXT NOT NULL REFERENCES unidades_executantes(sigla),
    PRIMARY KEY (evento_id, unidade_sigla)
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

-- Histórico de alterações dos eventos.
CREATE TABLE IF NOT EXISTS auditoria_eventos (
    id              BIGSERIAL PRIMARY KEY,
    evento_id       BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    usuario_fiscal  TEXT NOT NULL,
    campo           TEXT NOT NULL,
    valor_anterior  TEXT,
    valor_novo      TEXT,
    modificado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_evento_data_historico
    ON auditoria_eventos (evento_id, modificado_em DESC);

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
    observacoes TEXT,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    excluido_em TIMESTAMPTZ,
    excluido_por TEXT
);

ALTER TABLE bsr_erb ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMPTZ;
ALTER TABLE bsr_erb ADD COLUMN IF NOT EXISTS excluido_por TEXT;

CREATE TABLE IF NOT EXISTS bsr_erb_imagens (
    id            BIGSERIAL PRIMARY KEY,
    bsr_erb_id    BIGINT NOT NULL REFERENCES bsr_erb(id) ON DELETE CASCADE,
    nome_arquivo  TEXT NOT NULL,
    tipo_mime     TEXT NOT NULL,
    tamanho_bytes INTEGER NOT NULL,
    conteudo      BYTEA NOT NULL,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auditoria_bsr_erb (
    id            BIGSERIAL PRIMARY KEY,
    bsr_erb_id    BIGINT NOT NULL REFERENCES bsr_erb(id) ON DELETE CASCADE,
    evento_id     BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    usuario_fiscal TEXT NOT NULL,
    campo         TEXT NOT NULL,
    valor_anterior TEXT,
    valor_novo    TEXT,
    modificado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_bsr_erb_registro
    ON auditoria_bsr_erb (bsr_erb_id, modificado_em DESC);

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

-- Imagens dos equipamentos registrados no teste de etiquetagem.
CREATE TABLE IF NOT EXISTS teste_etiquetagem_imagens (
    id                    BIGSERIAL PRIMARY KEY,
    teste_etiquetagem_id  BIGINT NOT NULL REFERENCES testes_etiquetagem(id) ON DELETE CASCADE,
    nome_arquivo          TEXT NOT NULL,
    tipo_mime             TEXT NOT NULL,
    tamanho_bytes         INTEGER NOT NULL,
    conteudo              BYTEA NOT NULL,
    criado_em             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_teste_etiquetagem_imagens_teste
    ON teste_etiquetagem_imagens (teste_etiquetagem_id, id);

-- Auditoria das imagens anexadas aos equipamentos etiquetados.
CREATE TABLE IF NOT EXISTS auditoria_testes_etiquetagem (
    id                    BIGSERIAL PRIMARY KEY,
    teste_etiquetagem_id  BIGINT NOT NULL REFERENCES testes_etiquetagem(id) ON DELETE CASCADE,
    evento_id             BIGINT NOT NULL REFERENCES eventos(id) ON DELETE CASCADE,
    usuario_fiscal        TEXT NOT NULL,
    campo                 TEXT NOT NULL,
    valor_anterior        TEXT,
    valor_novo            TEXT,
    modificado_em         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_teste_etiquetagem_data
    ON auditoria_testes_etiquetagem (teste_etiquetagem_id, modificado_em DESC);

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