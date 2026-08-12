# ================= Configuração do Banco de Dados =================
DATABASE_URL = "postgresql+psycopg://appeventos:appeventos@localhost:5432/appeventos"
# ================================================================

# Usuário institucional atualmente utilizado como valor provisório.
# Quando o login real estiver disponível, substituir este valor pelo
# usuário autenticado da ANATEL ou carregá-lo da sessão de autenticação.
USR_FISCAL_ANATEL = "andrerezende"

# ================= AJUSTES RÁPIDOS (estilo) =================
BTN_HEIGHT = "3.8em"
BTN_GAP = "0px"
# ============================================================

ABAS_SISTEMA = ["PAINEL", "Tabela UTE", "Escala", "LISTAS"]

TITULO_PRINCIPAL = "AppEventos"
OBRIG = ":red[**\\***]"

IDENT_OPCOES = [
    "Sinal de dados",
    "Comunicação relacionada ao evento",
    "Comunicação não relacionada ao evento",
    "Espúrio ou Produto de Intermodulação",
    "Ruído",
    "Não identificado",
]

FAIXA_OPCOES = [
    "FM",
    "SMA",
    "SMM",
    "SLP",
    "TV",
    "SMP",
    "GNSS",
    "Satélite",
    "Radiação Restrita",
]

MODELOS_EQUIPAMENTO = [
    "Analisador de espectro",
    "RFeye",
    "Celplan",
    "Miaer",
    "UMS300",
    "ETM",
    "ERM",
]
