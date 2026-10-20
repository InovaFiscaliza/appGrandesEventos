# Auditoria — ajustes de taxonomia dos objetos

Data: 19/10/2026.  
Fontes: [schema.sql](schema.sql), [dump](../bd_backup/dump-appeventos-202610011705.sql) e [.instructions.md](.instructions.md).

## 1. Ajustes a executar

| Objeto | Ajuste |
|---|---|
| Banco | Renomear `appeventos` para `DB_GRANDES_EVENTOS`. |
| Tabelas | Ajustar para singular, CAIXA ALTA e prefixos `TB_`, `TL_` ou `BRIDGE_`. |
| Relações NxN | Nomear `BRIDGE_<NÚCLEO_1>_<NÚCLEO_2>`. |
| Colunas | Ajustar para CAIXA ALTA e classe do conteúdo: `ID_`, `CO_`, `SG_`, `NO_`, `DE_`, `TX_`, `DT_`, `HH_`, `DH_`, `IC_`, `VR_`, `QT_`, `NU_`, `ED_`, `BI_`. |
| PK | Nomear a constraint `PK_<TABELA>`. A coluna permanece `ID_*`, `CO_*` ou `SG_*`, conforme seu conteúdo. |
| FK | Nomear a constraint `FK_<FILHA>_<PAI>[_PAPEL]`. Propagar o nome da chave de origem às colunas de referência. |
| CHECK | Renomear conforme o de/para da seção 7, com prefixo `CC_`. |
| UNIQUE | Nomear `UQ_<TABELA>_<NN>`. |
| Índices | Nomear `IX_<TABELA>_<NN>`. |
| Função e triggers | Ajustar para `FN_*` e `TRG_*`, conforme seção 9. |
| Sequências | Nomear `SEQ_<TABELA>`. |

Tabelas e colunas: **até 32 caracteres**, incluindo prefixos e underscores. Demais objetos: até 63 bytes. Abreviar somente quando necessário, sem ambiguidade.

Caixa alta física no PostgreSQL exige aspas duplas nas definições e referências, inclusive na aplicação: `"TB_EVENTO"."ID_EVENTO"`. [Referência PostgreSQL](https://www.postgresql.org/docs/16/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS).

`BRIDGE_`, `UQ_` e `SEQ_` são convenções complementares adotadas nesta proposta.

## 2. Ajustar taxonomia das tabelas

| Nome atual | Nome proposto | Relação / classe |
|---|---|---|
| `eventos` | `TB_EVENTO` | Entidade |
| `unidades_executantes` | `TB_UNIDADE_EXECUTANTE` | Referência |
| `fiscais` | `TB_FISCAL` | Entidade |
| `municipios` | `TB_MUNICIPIO` | Referência |
| `eventos_fiscais` | `BRIDGE_EVENTO_FISCAL` | NxN |
| `eventos_coordenadores` | `BRIDGE_EVENTO_COORDENADOR` | NxN — coordenadores |
| `tickets` | `TB_TICKET` | Entidade |
| `ticket_ocorrencias` | `BRIDGE_TICKET_OCORRENCIA` | NxN |
| `ticket_incidentes` | `BRIDGE_TICKET_INCIDENTE` | NxN |
| `incidente_fiscais` | `BRIDGE_INCIDENTE_FISCAL` | NxN |
| `ticket_fiscais` | `BRIDGE_TICKET_FISCAL` | NxN |
| `escalas_trabalho` | `TB_ESCALA_TRABALHO` | Entidade de detalhe |
| `eventos_unidades_executantes` | `BRIDGE_EVENTO_UNIDADE_EXECUTANTE` | NxN |
| `estacoes` | `TB_ESTACAO` | Entidade |
| `ocorrencias` | `TB_OCORRENCIA` | Entidade |
| `ocorrencia_fiscais` | `BRIDGE_OCORRENCIA_FISCAL` | NxN |
| `ocorrencia_imagens` | `TB_OCORRENCIA_IMAGEM` | Anexo |
| `auditoria_ocorrencias` | `TL_ALTERACAO_OCORRENCIA` | Log de alteração |
| `auditoria_eventos` | `TL_ALTERACAO_EVENTO` | Log de alteração |
| `tabela_ute` | `TB_REGISTRO_UTE` | Registro operacional |
| `bsr_erb` | `TB_INCIDENTE` | Entidade classificada |
| `bsr_erb_imagens` | `TB_INCIDENTE_IMAGEM` | Anexo |
| `auditoria_bsr_erb` | `TL_ALTERACAO_INCIDENTE` | Log de alteração |
| `opcoes_identificacao` | `TB_OPCAO_IDENTIFICACAO` | Referência por escopo |
| `testes_etiquetagem` | `TB_TESTE_ETIQUETAGEM` | Entidade |
| `teste_etiquetagem_imagens` | `TB_TESTE_ETIQUETAGEM_IMAGEM` | Anexo |
| `auditoria_testes_etiquetagem` | `TL_ALTERACAO_TESTE_ETIQUETAGEM` | Log de alteração |
| `faixas_numeracao_etiqueta` | `TB_FAIXA_NUMERACAO_ETIQUETA` | Entidade de detalhe |

## 3. Ajustar taxonomia das colunas

Tipos atuais informados apenas para referência; sem conversão de tipos.

### eventos → TB_EVENTO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_EVENTO` | `BIGSERIAL` · PK |
| `nome` | `NO_EVENTO` | `TEXT` |
| `latitude` | `VR_LATITUDE` | `NUMERIC(9,6)` |
| `longitude` | `VR_LONGITUDE` | `NUMERIC(9,6)` |
| `fuso_horario` | `CO_FUSO_HORARIO` | `TEXT` |
| `cidade` | `NO_CIDADE` | `TEXT` |
| `uf` | `SG_UF` | `CHAR(2)` |
| `acao_fiscalizacao` | `DE_ACAO_FISCALIZACAO` | `TEXT` |
| `processo_sei` | `CO_PROCESSO_SEI` | `TEXT` |
| `periodo_inicio` | `DT_INICIO_EVENTO` | `DATE` |
| `periodo_fim` | `DT_FIM_EVENTO` | `DATE` |
| `teste_etiquetagem` | `IC_TESTE_ETIQUETAGEM` | `BOOLEAN` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### unidades_executantes → TB_UNIDADE_EXECUTANTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `sigla` | `SG_UNIDADE_EXECUTANTE` | `TEXT` · PK |
| `nome` | `NO_UNIDADE_EXECUTANTE` | `TEXT` |

### fiscais → TB_FISCAL

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_FISCAL` | `BIGSERIAL` · PK |
| `nome` | `NO_FISCAL` | `TEXT` |
| `local_anatel` | `SG_UNIDADE_EXECUTANTE` | `TEXT` · FK |
| `papeis` | `CO_PAPEIS` | `TEXT[]` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### municipios → TB_MUNICIPIO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `codigo_ibge` | `CO_MUNICIPIO_IBGE` | `BIGINT` · PK |
| `nome` | `NO_MUNICIPIO` | `TEXT` |
| `uf` | `SG_UF` | `CHAR(2)` |

### eventos_fiscais → BRIDGE_EVENTO_FISCAL

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `evento_id` | `ID_EVENTO` | `BIGINT` · PK + FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · PK + FK |
| `papeis` | `CO_PAPEIS` | `TEXT[]` |

### eventos_coordenadores → BRIDGE_EVENTO_COORDENADOR

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `evento_id` | `ID_EVENTO` | `BIGINT` · PK + FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · PK + FK |

### tickets → TB_TICKET

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_TICKET` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `ocorrencia_id` | `ID_OCORRENCIA` | `BIGINT` · FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · FK |
| `status` | `CO_SITUACAO_TICKET` | `TEXT` |
| `prioridade` | `CO_PRIORIDADE` | `TEXT` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `motivo_devolucao` | `TX_MOTIVO_DEVOLUCAO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |
| `atualizado_em` | `DH_ATUALIZACAO` | `TIMESTAMPTZ` |
| `providencias` | `TX_PROVIDENCIA` | `TEXT` |

### ticket_ocorrencias → BRIDGE_TICKET_OCORRENCIA

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `ticket_id` | `ID_TICKET` | `BIGINT` · PK + FK |
| `ocorrencia_id` | `ID_OCORRENCIA` | `BIGINT` · PK + FK |

### ticket_incidentes → BRIDGE_TICKET_INCIDENTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `ticket_id` | `ID_TICKET` | `BIGINT` · PK + FK |
| `incidente_id` | `ID_INCIDENTE` | `BIGINT` · PK + FK |

### incidente_fiscais → BRIDGE_INCIDENTE_FISCAL

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `incidente_id` | `ID_INCIDENTE` | `BIGINT` · PK + FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · PK + FK |

### ticket_fiscais → BRIDGE_TICKET_FISCAL

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `ticket_id` | `ID_TICKET` | `BIGINT` · PK + FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · PK + FK |

### escalas_trabalho → TB_ESCALA_TRABALHO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ESCALA_TRABALHO` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · FK |
| `data_trabalho` | `DT_TRABALHO` | `DATE` |
| `turno_inicio` | `HH_INICIO_TURNO` | `TIME` |
| `turno_fim` | `HH_FIM_TURNO` | `TIME` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### eventos_unidades_executantes → BRIDGE_EVENTO_UNIDADE_EXECUTANTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `evento_id` | `ID_EVENTO` | `BIGINT` · PK + FK |
| `unidade_sigla` | `SG_UNIDADE_EXECUTANTE` | `TEXT` · PK + FK |

### estacoes → TB_ESTACAO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ESTACAO` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `nome` | `NO_ESTACAO` | `TEXT` |
| `modelo_equipamento` | `DE_MODELO_EQUIPAMENTO` | `TEXT` |
| `local` | `DE_LOCAL` | `TEXT` |
| `cidade` | `NO_CIDADE` | `TEXT` |
| `latitude` | `VR_LATITUDE` | `NUMERIC(9,6)` |
| `longitude` | `VR_LONGITUDE` | `NUMERIC(9,6)` |
| `desabilitada_em` | `DH_DESABILITACAO` | `TIMESTAMPTZ` |

### ocorrencias → TB_OCORRENCIA

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_OCORRENCIA` | `BIGSERIAL` · PK |
| `id_exibicao` | `CO_OCORRENCIA_EXIBICAO` | `TEXT` |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `criado_por_fiscal_id` | `ID_FISCAL_CRIADOR` | `BIGINT` · FK |
| `estacao_id` | `ID_ESTACAO` | `BIGINT` · FK |
| `origem_captura` | `DE_ORIGEM_CAPTURA` | `TEXT` |
| `id_planilha` | `CO_REGISTRO_PLANILHA` | `TEXT` |
| `local_regiao` | `DE_LOCAL_REGIAO` | `TEXT` |
| `fiscal` | `TX_FISCAL_INFORMADO` | `TEXT` |
| `data` | `DT_OCORRENCIA` | `DATE` |
| `hora` | `HH_OCORRENCIA` | `TIME` |
| `frequencia_mhz` | `VR_FREQUENCIA_MHZ` | `NUMERIC(12,3)` |
| `largura_khz` | `VR_LARGURA_KHZ` | `NUMERIC(12,3)` |
| `faixa` | `DE_FAIXA` | `TEXT` |
| `identificacao` | `DE_IDENTIFICACAO` | `TEXT` |
| `autorizado` | `DE_AUTORIZACAO` | `TEXT` |
| `ute` | `IC_UTE` | `BOOLEAN` |
| `processo_sei_ute` | `CO_PROCESSO_SEI_UTE` | `TEXT` |
| `ato_ute` | `CO_ATO_UTE` | `TEXT` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `alguem_ciente` | `TX_CIENCIA` | `TEXT` |
| `interferente` | `DE_INTERFERENTE` | `TEXT` |
| `situacao` | `CO_SITUACAO` | `TEXT` |
| `concluida_por` | `CO_PAPEL_CONCLUSAO` | `TEXT` |
| `fonte` | `DE_FONTE_REGISTRO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |
| `atualizado_em` | `DH_ATUALIZACAO` | `TIMESTAMPTZ` |
| `submetida_coordenador_em` | `DH_SUBMISSAO_COORDENADOR` | `TIMESTAMPTZ` |

### ocorrencia_fiscais → BRIDGE_OCORRENCIA_FISCAL

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `ocorrencia_id` | `ID_OCORRENCIA` | `BIGINT` · PK + FK |
| `fiscal_id` | `ID_FISCAL` | `BIGINT` · PK + FK |

### ocorrencia_imagens → TB_OCORRENCIA_IMAGEM

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_OCORRENCIA_IMAGEM` | `BIGSERIAL` · PK |
| `ocorrencia_id` | `ID_OCORRENCIA` | `BIGINT` · FK |
| `nome_arquivo` | `NO_ARQUIVO` | `TEXT` |
| `tipo_mime` | `CO_TIPO_MIME` | `TEXT` |
| `tamanho_bytes` | `QT_BYTES` | `INTEGER` |
| `conteudo` | `BI_CONTEUDO` | `BYTEA` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### auditoria_ocorrencias → TL_ALTERACAO_OCORRENCIA

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ALTERACAO_OCORRENCIA` | `BIGSERIAL` · PK |
| `ocorrencia_id` | `ID_OCORRENCIA` | `BIGINT` · FK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `usuario_fiscal` | `NO_USUARIO_AUTOR` | `TEXT` |
| `campo` | `NO_CAMPO_ALTERADO` | `TEXT` |
| `valor_anterior` | `TX_VALOR_ANTERIOR` | `TEXT` |
| `valor_novo` | `TX_VALOR_NOVO` | `TEXT` |
| `modificado_em` | `DH_ALTERACAO` | `TIMESTAMPTZ` |

### auditoria_eventos → TL_ALTERACAO_EVENTO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ALTERACAO_EVENTO` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `usuario_fiscal` | `NO_USUARIO_AUTOR` | `TEXT` |
| `campo` | `NO_CAMPO_ALTERADO` | `TEXT` |
| `valor_anterior` | `TX_VALOR_ANTERIOR` | `TEXT` |
| `valor_novo` | `TX_VALOR_NOVO` | `TEXT` |
| `modificado_em` | `DH_ALTERACAO` | `TIMESTAMPTZ` |

### tabela_ute → TB_REGISTRO_UTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_REGISTRO_UTE` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `id_planilha` | `CO_REGISTRO_PLANILHA` | `TEXT` |
| `pais_entidade` | `TX_PAIS_ENTIDADE` | `TEXT` |
| `local` | `DE_LOCAL` | `TEXT` |
| `frequencia_mhz` | `VR_FREQUENCIA_MHZ` | `NUMERIC(12,3)` |
| `processo_sei` | `CO_PROCESSO_SEI` | `TEXT` |

### bsr_erb → TB_INCIDENTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_INCIDENTE` | `BIGSERIAL` · PK |
| `id_exibicao` | `CO_INCIDENTE_EXIBICAO` | `TEXT` |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `criado_por_fiscal_id` | `ID_FISCAL_CRIADOR` | `BIGINT` · FK |
| `tipo` | `CO_TIPO_INCIDENTE` | `TEXT` |
| `regiao` | `DE_REGIAO` | `TEXT` |
| `latitude` | `VR_LATITUDE` | `NUMERIC(9,6)` |
| `longitude` | `VR_LONGITUDE` | `NUMERIC(9,6)` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `cadastrado_por` | `TX_CADASTRANTE_INFORMADO` | `TEXT` |
| `situacao` | `CO_SITUACAO` | `TEXT` |
| `concluida_por` | `CO_PAPEL_CONCLUSAO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |
| `excluido_em` | `DH_EXCLUSAO` | `TIMESTAMPTZ` |
| `excluido_por` | `TX_AUTOR_EXCLUSAO` | `TEXT` |
| `submetido_coordenador_em` | `DH_SUBMISSAO_COORDENADOR` | `TIMESTAMPTZ` |

### bsr_erb_imagens → TB_INCIDENTE_IMAGEM

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_INCIDENTE_IMAGEM` | `BIGSERIAL` · PK |
| `bsr_erb_id` | `ID_INCIDENTE` | `BIGINT` · FK |
| `nome_arquivo` | `NO_ARQUIVO` | `TEXT` |
| `tipo_mime` | `CO_TIPO_MIME` | `TEXT` |
| `tamanho_bytes` | `QT_BYTES` | `INTEGER` |
| `conteudo` | `BI_CONTEUDO` | `BYTEA` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### auditoria_bsr_erb → TL_ALTERACAO_INCIDENTE

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ALTERACAO_INCIDENTE` | `BIGSERIAL` · PK |
| `bsr_erb_id` | `ID_INCIDENTE` | `BIGINT` · FK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `usuario_fiscal` | `NO_USUARIO_AUTOR` | `TEXT` |
| `campo` | `NO_CAMPO_ALTERADO` | `TEXT` |
| `valor_anterior` | `TX_VALOR_ANTERIOR` | `TEXT` |
| `valor_novo` | `TX_VALOR_NOVO` | `TEXT` |
| `modificado_em` | `DH_ALTERACAO` | `TIMESTAMPTZ` |

### opcoes_identificacao → TB_OPCAO_IDENTIFICACAO

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_OPCAO_IDENTIFICACAO` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `valor` | `DE_OPCAO_IDENTIFICACAO` | `TEXT` |

### testes_etiquetagem → TB_TESTE_ETIQUETAGEM

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_TESTE_ETIQUETAGEM` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `licenca` | `CO_LICENCA` | `TEXT` |
| `perfil` | `CO_PERFIL` | `TEXT` |
| `entidade` | `NO_ENTIDADE` | `TEXT` |
| `contato` | `TX_CONTATO` | `TEXT` |
| `responsavel_contato` | `NO_RESPONSAVEL_CONTATO` | `TEXT` |
| `telefone` | `CO_TELEFONE` | `TEXT` |
| `email` | `ED_EMAIL` | `TEXT` |
| `local` | `DE_LOCAL` | `TEXT` |
| `cpf_cnpj` | `CO_CPF_CNPJ` | `TEXT` |
| `equipamento_homologado` | `IC_EQUIPAMENTO_HOMOLOGADO` | `BOOLEAN` |
| `permissao` | `CO_PERMISSAO` | `TEXT` |
| `frequencias_selecionadas` | `TX_FREQUENCIAS_SELECIONADAS` | `TEXT[]` |
| `tipo_equipamento` | `DE_TIPO_EQUIPAMENTO` | `TEXT` |
| `numero_equipamentos` | `QT_EQUIPAMENTO` | `INTEGER` |
| `numero_etiqueta` | `CO_ETIQUETA` | `TEXT` |
| `observacoes` | `TX_OBSERVACAO` | `TEXT` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |
| `atualizado_em` | `DH_ATUALIZACAO` | `TIMESTAMPTZ` |

### teste_etiquetagem_imagens → TB_TESTE_ETIQUETAGEM_IMAGEM

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_TESTE_ETIQUETAGEM_IMAGEM` | `BIGSERIAL` · PK |
| `teste_etiquetagem_id` | `ID_TESTE_ETIQUETAGEM` | `BIGINT` · FK |
| `nome_arquivo` | `NO_ARQUIVO` | `TEXT` |
| `tipo_mime` | `CO_TIPO_MIME` | `TEXT` |
| `tamanho_bytes` | `QT_BYTES` | `INTEGER` |
| `conteudo` | `BI_CONTEUDO` | `BYTEA` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

### auditoria_testes_etiquetagem → TL_ALTERACAO_TESTE_ETIQUETAGEM

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_ALTERACAO_TESTE_ETIQUETAGEM` | `BIGSERIAL` · PK |
| `teste_etiquetagem_id` | `ID_TESTE_ETIQUETAGEM` | `BIGINT` · FK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `usuario_fiscal` | `NO_USUARIO_AUTOR` | `TEXT` |
| `campo` | `NO_CAMPO_ALTERADO` | `TEXT` |
| `valor_anterior` | `TX_VALOR_ANTERIOR` | `TEXT` |
| `valor_novo` | `TX_VALOR_NOVO` | `TEXT` |
| `modificado_em` | `DH_ALTERACAO` | `TIMESTAMPTZ` |

### faixas_numeracao_etiqueta → TB_FAIXA_NUMERACAO_ETIQUETA

| Coluna atual | Coluna proposta | Tipo atual / chave |
|---|---|---|
| `id` | `ID_FAIXA_NUMERACAO_ETIQUETA` | `BIGSERIAL` · PK |
| `evento_id` | `ID_EVENTO` | `BIGINT` · FK |
| `permissao` | `CO_PERMISSAO` | `TEXT` |
| `numero_inicial` | `NU_ETIQUETA_INICIAL` | `INTEGER` |
| `numero_final` | `NU_ETIQUETA_FINAL` | `INTEGER` |
| `criado_em` | `DH_CRIACAO` | `TIMESTAMPTZ` |

## 4. Ajustar nomes das PKs

| PK exportada | PK proposta | Coluna(s) proposta(s) |
|---|---|---|
| `eventos_pkey` | `PK_TB_EVENTO` | `ID_EVENTO` |
| `unidades_executantes_pkey` | `PK_TB_UNIDADE_EXECUTANTE` | `SG_UNIDADE_EXECUTANTE` |
| `fiscais_pkey` | `PK_TB_FISCAL` | `ID_FISCAL` |
| `municipios_pkey` | `PK_TB_MUNICIPIO` | `CO_MUNICIPIO_IBGE` |
| `eventos_fiscais_pkey` | `PK_BRIDGE_EVENTO_FISCAL` | `ID_EVENTO`, `ID_FISCAL` |
| `eventos_coordenadores_pkey` | `PK_BRIDGE_EVENTO_COORDENADOR` | `ID_EVENTO`, `ID_FISCAL` |
| `tickets_pkey` | `PK_TB_TICKET` | `ID_TICKET` |
| `ticket_ocorrencias_pkey` | `PK_BRIDGE_TICKET_OCORRENCIA` | `ID_TICKET`, `ID_OCORRENCIA` |
| `ticket_incidentes_pkey` | `PK_BRIDGE_TICKET_INCIDENTE` | `ID_TICKET`, `ID_INCIDENTE` |
| `incidente_fiscais_pkey` | `PK_BRIDGE_INCIDENTE_FISCAL` | `ID_INCIDENTE`, `ID_FISCAL` |
| `ticket_fiscais_pkey` | `PK_BRIDGE_TICKET_FISCAL` | `ID_TICKET`, `ID_FISCAL` |
| `escalas_trabalho_pkey` | `PK_TB_ESCALA_TRABALHO` | `ID_ESCALA_TRABALHO` |
| `eventos_unidades_executantes_pkey` | `PK_BRIDGE_EVENTO_UNIDADE_EXECUTANTE` | `ID_EVENTO`, `SG_UNIDADE_EXECUTANTE` |
| `estacoes_pkey` | `PK_TB_ESTACAO` | `ID_ESTACAO` |
| `ocorrencias_pkey` | `PK_TB_OCORRENCIA` | `ID_OCORRENCIA` |
| `ocorrencia_fiscais_pkey` | `PK_BRIDGE_OCORRENCIA_FISCAL` | `ID_OCORRENCIA`, `ID_FISCAL` |
| `ocorrencia_imagens_pkey` | `PK_TB_OCORRENCIA_IMAGEM` | `ID_OCORRENCIA_IMAGEM` |
| `auditoria_ocorrencias_pkey` | `PK_TL_ALTERACAO_OCORRENCIA` | `ID_ALTERACAO_OCORRENCIA` |
| `auditoria_eventos_pkey` | `PK_TL_ALTERACAO_EVENTO` | `ID_ALTERACAO_EVENTO` |
| `tabela_ute_pkey` | `PK_TB_REGISTRO_UTE` | `ID_REGISTRO_UTE` |
| `bsr_erb_pkey` | `PK_TB_INCIDENTE` | `ID_INCIDENTE` |
| `bsr_erb_imagens_pkey` | `PK_TB_INCIDENTE_IMAGEM` | `ID_INCIDENTE_IMAGEM` |
| `auditoria_bsr_erb_pkey` | `PK_TL_ALTERACAO_INCIDENTE` | `ID_ALTERACAO_INCIDENTE` |
| `opcoes_identificacao_pkey` | `PK_TB_OPCAO_IDENTIFICACAO` | `ID_OPCAO_IDENTIFICACAO` |
| `testes_etiquetagem_pkey` | `PK_TB_TESTE_ETIQUETAGEM` | `ID_TESTE_ETIQUETAGEM` |
| `teste_etiquetagem_imagens_pkey` | `PK_TB_TESTE_ETIQUETAGEM_IMAGEM` | `ID_TESTE_ETIQUETAGEM_IMAGEM` |
| `auditoria_testes_etiquetagem_pkey` | `PK_TL_ALTERACAO_TESTE_ETIQUETAGEM` | `ID_ALTERACAO_TESTE_ETIQUETAGEM` |
| `faixas_numeracao_etiqueta_pkey` | `PK_TB_FAIXA_NUMERACAO_ETIQUETA` | `ID_FAIXA_NUMERACAO_ETIQUETA` |

## 5. Ajustar nomes das FKs

| FK exportada | FK proposta |
|---|---|
| `fiscais_local_anatel_fkey` | `FK_TB_FISCAL_TB_UNIDADE_EXECUTANTE` |
| `eventos_fiscais_evento_id_fkey` | `FK_BRIDGE_EVENTO_FISCAL_TB_EVENTO` |
| `eventos_fiscais_fiscal_id_fkey` | `FK_BRIDGE_EVENTO_FISCAL_TB_FISCAL` |
| `eventos_coordenadores_evento_id_fkey` | `FK_BRIDGE_EVENTO_COORDENADOR_TB_EVENTO` |
| `eventos_coordenadores_fiscal_id_fkey` | `FK_BRIDGE_EVENTO_COORDENADOR_TB_FISCAL` |
| `eventos_coordenadores_evento_id_fiscal_id_fkey` | `FK_BRIDGE_EVENTO_COORDENADOR_BRIDGE_EVENTO_FISCAL` |
| `tickets_evento_id_fkey` | `FK_TB_TICKET_TB_EVENTO` |
| `tickets_ocorrencia_id_fkey` | `FK_TB_TICKET_TB_OCORRENCIA` |
| `tickets_fiscal_id_fkey` | `FK_TB_TICKET_TB_FISCAL` |
| `ticket_ocorrencias_ticket_id_fkey` | `FK_BRIDGE_TICKET_OCORRENCIA_TB_TICKET` |
| `ticket_ocorrencias_ocorrencia_id_fkey` | `FK_BRIDGE_TICKET_OCORRENCIA_TB_OCORRENCIA` |
| `ticket_incidentes_ticket_id_fkey` | `FK_BRIDGE_TICKET_INCIDENTE_TB_TICKET` |
| `ticket_incidentes_incidente_id_fkey` | `FK_BRIDGE_TICKET_INCIDENTE_TB_INCIDENTE` |
| `incidente_fiscais_incidente_id_fkey` | `FK_BRIDGE_INCIDENTE_FISCAL_TB_INCIDENTE` |
| `incidente_fiscais_fiscal_id_fkey` | `FK_BRIDGE_INCIDENTE_FISCAL_TB_FISCAL` |
| `ticket_fiscais_ticket_id_fkey` | `FK_BRIDGE_TICKET_FISCAL_TB_TICKET` |
| `ticket_fiscais_fiscal_id_fkey` | `FK_BRIDGE_TICKET_FISCAL_TB_FISCAL` |
| `escalas_trabalho_evento_id_fkey` | `FK_TB_ESCALA_TRABALHO_TB_EVENTO` |
| `escalas_trabalho_fiscal_id_fkey` | `FK_TB_ESCALA_TRABALHO_TB_FISCAL` |
| `eventos_unidades_executantes_evento_id_fkey` | `FK_BRIDGE_EVENTO_UNIDADE_EXECUTANTE_TB_EVENTO` |
| `eventos_unidades_executantes_unidade_sigla_fkey` | `FK_BRIDGE_EVENTO_UNIDADE_EXECUTANTE_TB_UNIDADE_EXECUTANTE` |
| `estacoes_evento_id_fkey` | `FK_TB_ESTACAO_TB_EVENTO` |
| `ocorrencias_evento_id_fkey` | `FK_TB_OCORRENCIA_TB_EVENTO` |
| `ocorrencias_criado_por_fiscal_id_fkey` | `FK_TB_OCORRENCIA_TB_FISCAL_CRIADOR` |
| `ocorrencias_estacao_id_fkey` | `FK_TB_OCORRENCIA_TB_ESTACAO` |
| `ocorrencia_fiscais_ocorrencia_id_fkey` | `FK_BRIDGE_OCORRENCIA_FISCAL_TB_OCORRENCIA` |
| `ocorrencia_fiscais_fiscal_id_fkey` | `FK_BRIDGE_OCORRENCIA_FISCAL_TB_FISCAL` |
| `ocorrencia_imagens_ocorrencia_id_fkey` | `FK_TB_OCORRENCIA_IMAGEM_TB_OCORRENCIA` |
| `auditoria_ocorrencias_ocorrencia_id_fkey` | `FK_TL_ALTERACAO_OCORRENCIA_TB_OCORRENCIA` |
| `auditoria_ocorrencias_evento_id_fkey` | `FK_TL_ALTERACAO_OCORRENCIA_TB_EVENTO` |
| `auditoria_eventos_evento_id_fkey` | `FK_TL_ALTERACAO_EVENTO_TB_EVENTO` |
| `tabela_ute_evento_id_fkey` | `FK_TB_REGISTRO_UTE_TB_EVENTO` |
| `bsr_erb_evento_id_fkey` | `FK_TB_INCIDENTE_TB_EVENTO` |
| `bsr_erb_criado_por_fiscal_id_fkey` | `FK_TB_INCIDENTE_TB_FISCAL_CRIADOR` |
| `bsr_erb_imagens_bsr_erb_id_fkey` | `FK_TB_INCIDENTE_IMAGEM_TB_INCIDENTE` |
| `auditoria_bsr_erb_bsr_erb_id_fkey` | `FK_TL_ALTERACAO_INCIDENTE_TB_INCIDENTE` |
| `auditoria_bsr_erb_evento_id_fkey` | `FK_TL_ALTERACAO_INCIDENTE_TB_EVENTO` |
| `opcoes_identificacao_evento_id_fkey` | `FK_TB_OPCAO_IDENTIFICACAO_TB_EVENTO` |
| `testes_etiquetagem_evento_id_fkey` | `FK_TB_TESTE_ETIQUETAGEM_TB_EVENTO` |
| `teste_etiquetagem_imagens_teste_etiquetagem_id_fkey` | `FK_TB_TESTE_ETIQUETAGEM_IMAGEM_TB_TESTE_ETIQUETAGEM` |
| `auditoria_testes_etiquetagem_teste_etiquetagem_id_fkey` | `FK_TL_ALTERACAO_TESTE_ETIQUETAGEM_TB_TESTE_ETIQUETAGEM` |
| `auditoria_testes_etiquetagem_evento_id_fkey` | `FK_TL_ALTERACAO_TESTE_ETIQUETAGEM_TB_EVENTO` |
| `faixas_numeracao_etiqueta_evento_id_fkey` | `FK_TB_FAIXA_NUMERACAO_ETIQUETA_TB_EVENTO` |

## 6. Ajustar nomes das UNIQUEs

| UNIQUE exportada | Nome proposto | Coluna(s) proposta(s) |
|---|---|---|
| `escalas_trabalho_evento_id_fiscal_id_data_trabalho_turno_in_key` | `UQ_TB_ESCALA_TRABALHO_01` | `ID_EVENTO`, `ID_FISCAL`, `DT_TRABALHO`, `HH_INICIO_TURNO`, `HH_FIM_TURNO` |
| `estacoes_evento_id_nome_key` | `UQ_TB_ESTACAO_01` | `ID_EVENTO`, `NO_ESTACAO` |
| `eventos_nome_key` | `UQ_TB_EVENTO_01` | `NO_EVENTO` |
| `fiscais_nome_local_anatel_key` | `UQ_TB_FISCAL_01` | `NO_FISCAL`, `SG_UNIDADE_EXECUTANTE` |
| `municipios_nome_uf_key` | `UQ_TB_MUNICIPIO_01` | `NO_MUNICIPIO`, `SG_UF` |
| `testes_etiquetagem_evento_id_numero_etiqueta_key` | `UQ_TB_TESTE_ETIQUETAGEM_01` | `ID_EVENTO`, `CO_ETIQUETA` |

## 7. Ajustar nomes dos CHECKs

| CHECK atual | CHECK proposto |
|---|---|
| `eventos_fiscais_papeis_check` | `CC_BRIDGE_EVENTO_FISCAL_01` |
| `faixas_numeracao_etiqueta_check` | `CC_TB_FAIXA_NUMERACAO_ETIQUETA_01` |
| `faixas_numeracao_etiqueta_numero_inicial_check` | `CC_TB_FAIXA_NUMERACAO_ETIQUETA_02` |
| `faixas_numeracao_etiqueta_permissao_check` | `CC_TB_FAIXA_NUMERACAO_ETIQUETA_03` |
| `ocorrencias_concluida_por_check` | `CC_TB_OCORRENCIA_01` |
| `ocorrencias_situacao_check` | `CC_TB_OCORRENCIA_02` |
| `testes_etiquetagem_licenca_check` | `CC_TB_TESTE_ETIQUETAGEM_01` |
| `testes_etiquetagem_perfil_check` | `CC_TB_TESTE_ETIQUETAGEM_02` |
| `testes_etiquetagem_permissao_check` | `CC_TB_TESTE_ETIQUETAGEM_03` |
| `tickets_prioridade_check` | `CC_TB_TICKET_01` |
| `tickets_status_check` | `CC_TB_TICKET_02` |

`fiscais.papeis`: CHECK presente no schema e ausente no dump. Se vigente no destino, usar `CC_TB_FISCAL_01`.

## 8. Ajustar nomes dos índices

| Índice atual | Índice proposto | Tipo / coluna(s) proposta(s) |
|---|---|---|
| `idx_auditoria_bsr_erb_registro` | `IX_TL_ALTERACAO_INCIDENTE_01` | BTREE · `ID_INCIDENTE`, `DH_ALTERACAO` |
| `idx_auditoria_evento_data_historico` | `IX_TL_ALTERACAO_EVENTO_01` | BTREE · `ID_EVENTO`, `DH_ALTERACAO` |
| `idx_auditoria_evento_data` | `IX_TL_ALTERACAO_OCORRENCIA_01` | BTREE · `ID_EVENTO`, `DH_ALTERACAO` |
| `idx_auditoria_ocorrencia_data` | `IX_TL_ALTERACAO_OCORRENCIA_02` | BTREE · `ID_OCORRENCIA`, `DH_ALTERACAO` |
| `idx_auditoria_teste_etiquetagem_data` | `IX_TL_ALTERACAO_TESTE_ETIQUETAGEM_01` | BTREE · `ID_TESTE_ETIQUETAGEM`, `DH_ALTERACAO` |
| `idx_bsr_erb_evento_criador` | `IX_TB_INCIDENTE_01` | BTREE · `ID_EVENTO`, `ID_FISCAL_CRIADOR` |
| `uq_bsr_erb_id_exibicao` | `IX_TB_INCIDENTE_02` | UNIQUE · BTREE · `CO_INCIDENTE_EXIBICAO` |
| `idx_escalas_trabalho_evento_data` | `IX_TB_ESCALA_TRABALHO_01` | BTREE · `ID_EVENTO`, `DT_TRABALHO`, `ID_FISCAL` |
| `idx_eventos_coordenadores_fiscal` | `IX_BRIDGE_EVENTO_COORDENADOR_01` | BTREE · `ID_FISCAL` |
| `idx_faixas_numeracao_evento` | `IX_TB_FAIXA_NUMERACAO_ETIQUETA_01` | BTREE · `ID_EVENTO`, `CO_PERMISSAO` |
| `idx_fiscais_nome` | `IX_TB_FISCAL_01` | BTREE · `NO_FISCAL` |
| `idx_incidente_fiscais_fiscal` | `IX_BRIDGE_INCIDENTE_FISCAL_01` | BTREE · `ID_FISCAL` |
| `idx_municipios_uf_nome` | `IX_TB_MUNICIPIO_01` | BTREE · `SG_UF`, `NO_MUNICIPIO` |
| `idx_ocorrencia_fiscais_fiscal` | `IX_BRIDGE_OCORRENCIA_FISCAL_01` | BTREE · `ID_FISCAL` |
| `idx_ocorrencia_imagens_ocorrencia` | `IX_TB_OCORRENCIA_IMAGEM_01` | BTREE · `ID_OCORRENCIA`, `ID_OCORRENCIA_IMAGEM` |
| `idx_ocorr_busca_trgm` | `IX_TB_OCORRENCIA_01` | GIN · `TX_OBSERVACAO` |
| `idx_ocorr_evento_criador` | `IX_TB_OCORRENCIA_02` | BTREE · `ID_EVENTO`, `ID_FISCAL_CRIADOR` |
| `idx_ocorr_evento_situacao` | `IX_TB_OCORRENCIA_03` | BTREE · `ID_EVENTO`, `CO_SITUACAO` |
| `idx_ocorr_frequencia` | `IX_TB_OCORRENCIA_04` | BTREE · `ID_EVENTO`, `VR_FREQUENCIA_MHZ` |
| `uq_ocorrencias_id_exibicao` | `IX_TB_OCORRENCIA_05` | UNIQUE · BTREE · `CO_OCORRENCIA_EXIBICAO` |
| `idx_ute_evento_freq` | `IX_TB_REGISTRO_UTE_01` | BTREE · `ID_EVENTO`, `VR_FREQUENCIA_MHZ` |
| `idx_teste_etiquetagem_imagens_teste` | `IX_TB_TESTE_ETIQUETAGEM_IMAGEM_01` | BTREE · `ID_TESTE_ETIQUETAGEM`, `ID_TESTE_ETIQUETAGEM_IMAGEM` |
| `idx_etiquetagem_evento_entidade` | `IX_TB_TESTE_ETIQUETAGEM_01` | BTREE · `ID_EVENTO`, `NO_ENTIDADE` |
| `idx_ticket_fiscais_fiscal` | `IX_BRIDGE_TICKET_FISCAL_01` | BTREE · `ID_FISCAL` |
| `idx_ticket_incidentes_incidente` | `IX_BRIDGE_TICKET_INCIDENTE_01` | BTREE · `ID_INCIDENTE` |
| `idx_ticket_ocorrencias_ocorrencia` | `IX_BRIDGE_TICKET_OCORRENCIA_01` | BTREE · `ID_OCORRENCIA` |
| `idx_tickets_evento_status` | `IX_TB_TICKET_01` | BTREE · `ID_EVENTO`, `CO_SITUACAO_TICKET`, `ID_FISCAL` |

Preservar unicidade, ordem ASC/DESC, método, opclass e predicados. Índices de PK/UNIQUE acompanham as respectivas constraints.

## 9. Ajustar função e triggers

| Nome atual | Nome proposto |
|---|---|
| `set_atualizado_em` | `FN_DEFINIR_DH_ATUALIZACAO` |
| `trg_ocorr_upd` | `TRG_TB_OCORRENCIA_ATUALIZACAO_01` |
| `trg_etiquetagem_upd` | `TRG_TB_TESTE_ETIQUETAGEM_ATUALIZACAO_01` |

Na função, ajustar `NEW.atualizado_em` para `NEW."DH_ATUALIZACAO"`; atualizar referências à função e às tabelas.

## 10. Ajustar nomes das sequências

| Sequência exportada | Nome proposto |
|---|---|
| `eventos_id_seq` | `SEQ_TB_EVENTO` |
| `fiscais_id_seq` | `SEQ_TB_FISCAL` |
| `tickets_id_seq` | `SEQ_TB_TICKET` |
| `escalas_trabalho_id_seq` | `SEQ_TB_ESCALA_TRABALHO` |
| `estacoes_id_seq` | `SEQ_TB_ESTACAO` |
| `ocorrencias_id_seq` | `SEQ_TB_OCORRENCIA` |
| `ocorrencia_imagens_id_seq` | `SEQ_TB_OCORRENCIA_IMAGEM` |
| `auditoria_ocorrencias_id_seq` | `SEQ_TL_ALTERACAO_OCORRENCIA` |
| `auditoria_eventos_id_seq` | `SEQ_TL_ALTERACAO_EVENTO` |
| `tabela_ute_id_seq` | `SEQ_TB_REGISTRO_UTE` |
| `bsr_erb_id_seq` | `SEQ_TB_INCIDENTE` |
| `bsr_erb_imagens_id_seq` | `SEQ_TB_INCIDENTE_IMAGEM` |
| `auditoria_bsr_erb_id_seq` | `SEQ_TL_ALTERACAO_INCIDENTE` |
| `opcoes_identificacao_id_seq` | `SEQ_TB_OPCAO_IDENTIFICACAO` |
| `testes_etiquetagem_id_seq` | `SEQ_TB_TESTE_ETIQUETAGEM` |
| `teste_etiquetagem_imagens_id_seq` | `SEQ_TB_TESTE_ETIQUETAGEM_IMAGEM` |
| `auditoria_testes_etiquetagem_id_seq` | `SEQ_TL_ALTERACAO_TESTE_ETIQUETAGEM` |
| `faixas_numeracao_etiqueta_id_seq` | `SEQ_TB_FAIXA_NUMERACAO_ETIQUETA` |

Conferir DEFAULTs `nextval` e vínculos de propriedade das sequências.

## 11. Confirmações antes da implantação

| Ponto | Ação |
|---|---|
| eventos.acao_fiscalizacao | Confirmar se é descrição (`DE_ACAO_FISCALIZACAO`) ou código (`CO_ACAO_FISCALIZACAO`). |
| testes_etiquetagem.frequencias_selecionadas | Usar `TX_FREQUENCIAS_SELECIONADAS` enquanto o array estiver ativo; não chamar de legado. |
| UNIQUE de testes_etiquetagem | Conferir divergência entre dump e migração 0005: evento/número versus evento/permissão/número. Renomear a regra vigente sem alterar suas colunas. |
| Dependências | Atualizar consultas, aplicação, funções e referências dos objetos renomeados. |

## 12. Fora deste ajuste

Criação de catálogos de tipos/papéis, normalização dos arrays e novas bridges exigem decisão separada. Não integram o pacote de renomeação.

**Cobertura:** 28 tabelas, 201 colunas, 28 PKs, 43 FKs, seis UNIQUEs, onze CHECKs exportados, 27 índices explícitos, uma função, duas triggers e dezoito sequências.

