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

SITUACAO_PENDENTE = "Pendente"
SITUACAO_CONCLUIDA_FISCAL = "Concluída Pelo Fiscal"
SITUACAO_CONCLUIDA_COORDENADOR = "Concluída Pelo Coordenador"
SITUACOES_DISPONIVEIS_AO_FISCAL = {
    SITUACAO_PENDENTE,
    SITUACAO_CONCLUIDA_FISCAL,
}

STATUS_TICKET_PENDENTE = "pendente"
STATUS_TICKET_CONCLUIDO_FISCAIS = "concluido_pelos_fiscais"
STATUS_TICKET_CONCLUIDO_COORDENADOR = "concluido_pelo_coordenador"
STATUS_TICKET_VALIDOS = {
    STATUS_TICKET_PENDENTE,
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    STATUS_TICKET_CONCLUIDO_COORDENADOR,
}
STATUS_TICKET_ROTULOS = {
    STATUS_TICKET_PENDENTE: "Pendente",
    STATUS_TICKET_CONCLUIDO_FISCAIS: "Concluído pelos Fiscais",
    STATUS_TICKET_CONCLUIDO_COORDENADOR: "Concluído pelo Coordenador",
}

IDENT_OPCOES = [
    "Sinal de dados",
    "Comunicação relacionada ao evento",
    "Comunicação não relacionada ao evento",
    "Espúrio ou Produto de Intermodulação",
    "Ruído",
    "Não identificado",
]

BANDA_OPCOES = [
    f"{valor:,}".replace(",", ".") + " kHz"
    for valor in [5, 10, *range(25, 501, 25), *range(1_000, 100_001, 1_000)]
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
    "ERMx",
]

ORIGENS_CAMPO = {
    "campo_analisador": "Analisador de espectro - campo",
    "campo_etm": "ETM - campo",
}

UNIDADES_EXECUTANTES = [
    ("GR01", "Gerência Regional no Estado de São Paulo"),
    ("GR02", "Gerência Regional nos Estados do Rio de Janeiro e Espírito Santo"),
    ("GR03", "Gerência Regional nos Estados do Paraná e Santa Catarina"),
    ("GR04", "Gerência Regional no Estado de Minas Gerais"),
    ("GR05", "Gerência Regional no Estado do Rio Grande do Sul"),
    ("GR06", "Gerência Regional nos Estados de Pernambuco, Paraíba e Alagoas"),
    (
        "GR07",
        "Gerência Regional nos Estados de Goiás, Mato Grosso, Mato Grosso do Sul e Tocantins",
    ),
    ("GR08", "Gerência Regional nos Estados da Bahia e Sergipe"),
    ("GR09", "Gerência Regional nos Estados do Ceará, Rio Grande do Norte e Piauí"),
    ("GR10", "Gerência Regional nos Estados do Pará, Maranhão e Amapá"),
    ("GR11", "Gerência Regional nos Estados do Amazonas, Acre, Rondônia e Roraima"),
    ("UO00.1", "Unidade Operacional do Distrito Federal"),
    ("UO02.1", "Unidade Operacional no Estado do Espírito Santo"),
    ("UO03.1", "Unidade Operacional no Estado de Santa Catarina"),
    ("UO06.1", "Unidade Operacional no Estado de Alagoas"),
    ("UO06.2", "Unidade Operacional no Estado da Paraíba"),
    ("UO07.1", "Unidade Operacional no Estado de Mato Grosso"),
    ("UO07.2", "Unidade Operacional no Estado de Mato Grosso do Sul"),
    ("UO07.3", "Unidade Operacional no Estado de Tocantins"),
    ("UO08.1", "Unidade Operacional no Estado de Sergipe"),
    ("UO09.1", "Unidade Operacional no Estado do Rio Grande do Norte"),
    ("UO09.2", "Unidade Operacional no Estado do Piauí"),
    ("UO10.1", "Unidade Operacional no Estado do Maranhão"),
    ("UO10.2", "Unidade Operacional no Estado do Amapá"),
    ("UO11.1", "Unidade Operacional no Estado de Rondônia"),
    ("UO11.2", "Unidade Operacional no Estado do Acre"),
    ("UO11.3", "Unidade Operacional no Estado de Roraima"),
]
