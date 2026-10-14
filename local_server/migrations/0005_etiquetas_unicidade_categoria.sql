ALTER TABLE testes_etiquetagem
    ADD CONSTRAINT testes_etiquetagem_evento_permissao_numero_key
    UNIQUE (evento_id, permissao, numero_etiqueta);

ALTER TABLE testes_etiquetagem
    DROP CONSTRAINT IF EXISTS testes_etiquetagem_evento_id_numero_etiqueta_key;