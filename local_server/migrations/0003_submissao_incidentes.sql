-- Novos incidentes ficam salvos até a submissão explícita.
ALTER TABLE bsr_erb
    ADD COLUMN IF NOT EXISTS submetido_coordenador_em TIMESTAMP WITH TIME ZONE;

-- Preserva o fluxo dos incidentes que já foram atribuídos a tickets.
UPDATE bsr_erb b
SET submetido_coordenador_em = b.criado_em
WHERE b.submetido_coordenador_em IS NULL
  AND EXISTS (
      SELECT 1 FROM ticket_incidentes ti
      JOIN tickets t ON t.id = ti.ticket_id
      WHERE ti.incidente_id = b.id AND t.evento_id = b.evento_id
  );
