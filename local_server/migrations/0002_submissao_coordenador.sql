-- 0002_submissao_coordenador.sql
-- Adiciona o campo submetida_coordenador_em à tabela ocorrencias.
-- Apenas emissões com este campo preenchido aparecem na tela de coordenação.
-- Emissões legadas (sem submissão explícita) ficam ocultas do coordenador.

ALTER TABLE ocorrencias
    ADD COLUMN submetida_coordenador_em TIMESTAMP WITH TIME ZONE;

-- Marca como submetidas as emissões que já possuem ticket vinculado,
-- pois elas já passaram pelo fluxo de submissão.
UPDATE ocorrencias o
SET submetida_coordenador_em = o.atualizado_em
WHERE EXISTS (
    SELECT 1
    FROM ticket_ocorrencias toco
    JOIN tickets t ON t.id = toco.ticket_id
    WHERE toco.ocorrencia_id = o.id
      AND t.evento_id = o.evento_id
);

COMMENT ON COLUMN ocorrencias.submetida_coordenador_em
    IS 'Momento em que o fiscal submeteu a emissão ao coordenador. Se NULL, a emissão não foi submetida e não aparece na coordenação.';