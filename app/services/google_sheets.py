"""
Serviço de integração com Google Sheets via gspread.

Funções a migrar de abordagem.py:
  - obter_cliente_gspread()       → autenticação com credenciais do st.secrets
  - buscar_planilhas(client)      → lista planilhas de "monitoracao" no Drive
  - abrir_planilha_selecionada()  → abre planilha pelo ID
  - listar_abas_estacoes()        → lista abas que não são de sistema
  - carregar_dados_ute()          → carrega tabela UTE da planilha
  - carregar_pendencias_painel_mapeadas()
  - carregar_pendencias_abordagem_pendentes()
  - carregar_pendencias_todas_estacoes()
  - carregar_todas_frequencias()
  - verificar_frequencia_existente()
  - verificar_frequencia_global()
  - obter_fuso_horario_evento()
  - get_city_map_url()
  - atualizar_campos_na_aba_mae()
  - atualizar_campos_abordagem_por_id()
  - inserir_emissao_I_W()
  - inserir_bsr_erb()
  - carregar_opcoes_identificacao()
  - _first_col_match(), _col_to_index(), _first_empty_row_in_block()
  - _first_row_where_col_empty(), _next_sequential_id()
  - _valid_neg_coord()
"""

# TODO: migrar funções acima de abordagem.py para cá
