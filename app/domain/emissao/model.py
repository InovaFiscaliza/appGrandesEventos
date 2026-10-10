"""Domínio: Entidade Emissão.

Representa uma medição de radiação não ionizante (RNI) realizada por um fiscal.
Este modelo é independente da camada de persistência (SQLAlchemy, etc.) e das
camadas de aplicação (FastAPI, templates, etc.). Contém apenas os atributos e
comportamentos intrínsecos ao conceito de emissão no domínio da fiscalização.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time


@dataclass
class Emissao:
    """Registro de uma medição de radiação não ionizante (RNI).

    Attributes:
        id: Identificador único da emissão na tabela `ocorrencias`.
        evento_id: FK para o evento ao qual esta emissão pertence.
        frequencia_mhz: Frequência medida em MHz (ex: 125.500).
        largura_khz: Largura de banda medida em kHz (ex: 12.5).
        local_regiao: Descrição textual do local da medição (ex: 'Próximo ao poste 123').
        identificacao: Código ou etiqueta que identifica a emissão (ex: 'ETQ-001').
        autorizado: Indica se a emissão está dentro dos limites autorizados (Q).
                   None se não aplicável ou não informado.
        ute: Indica se a emissão corresponde a uma UTE (Unidade de Teste e Ensaios).
        processo_sei_ute: Número do processo SEI associado à UTE, se aplicável.
        ato_ute: Ato ou descrição específica da UTE, se aplicável.
        observacoes: Campo livre para observações do fiscal sobre a medição.
        alguem_ciente: Indica se havia alguém mais ciente presente durante a medição.
        interferente: Indica se foi detectado sinal interferente na frequência.
        situacao: Status atual da emissão (ex: 'pendente', 'concluido', 'cancelado').
        fonte: Origem da emissão ('PAINEL' ou 'ESTACAO').
        data: Data em que a medição foi realizada.
        hora: Hora em que a medição foi realizada.
        fiscal_id: ID do fiscal que realizou e registrou esta emissão.
        id_exibicao: Campo formatado para exibição (ex: '000123'), pode ser None.
        equipamento: Nome ou modelo do equipamento utilizado, se disponível.
        fiscal_nome: Nome do fiscal (para exibição em relatórios e interfaces).
    """

    id: int
    evento_id: int
    frequencia_mhz: float
    largura_khz: float
    local_regiao: str
    identificacao: str
    autorizado: bool | None = None
    ute: bool = False
    processo_sei_ute: str | None = None
    ato_ute: str | None = None
    observacoes: str = ""
    alguem_ciente: bool | None = None
    interferente: bool = False
    situacao: str = "pendente"
    fonte: str = "PAINEL"
    data: date = field(default_factory=date.today)
    hora: time = field(default_factory=time.min)
    fiscal_id: int = 0
    id_exibicao: str | None = None
    equipamento: str | None = None
    fiscal_nome: str | None = None
    submetida_coordenador_em: datetime | None = None
    faixa: str = ""

    def __post_init__(self) -> None:
        """Validações básicas de consistência após a inicialização."""
        if self.frequencia_mhz <= 0:
            raise ValueError("frequencia_mhz deve ser positivo")
        if self.largura_khz < 0:
            raise ValueError("largura_khz não pode ser negativo")
        if not self.local_regiao.strip():
            raise ValueError("local_regiao não pode ser vazio")
        if not self.identificacao.strip():
            raise ValueError("identificacao não pode ser vazia")
