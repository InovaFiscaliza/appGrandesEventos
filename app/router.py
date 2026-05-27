"""
Roteador central da aplicação.

Centraliza o mapeamento view → função de tela, eliminando o bloco if/elif
atualmente no final de abordagem.py.

Ao migrar, este módulo substituirá o bloco '# === MAIN ===' de abordagem.py:

    from app.views.selecao_evento import tela_selecao_evento
    from app.views.menu_principal import tela_menu_principal
    from app.views.abordagem_view import tela_consultar, tela_inserir
    from app.views.bsr_erb import tela_bsr_erb
    from app.views.busca import tela_busca
    from app.views.tabela_ute import tela_tabela_ute

Mapeamento de rotas (session_state["view"] → função):
  "selecao"    → tela_selecao_evento
  "main_menu"  → tela_menu_principal
  "consultar"  → tela_consultar
  "inserir"    → tela_inserir
  "bsr_erb"    → tela_bsr_erb
  "busca"      → tela_busca
  "tabela_ute" → tela_tabela_ute
"""

# TODO: migrar lógica de roteamento de abordagem.py para cá
