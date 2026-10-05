"""Domínio: Serviço de Emissão.

Contém a lógica de negócio relacionada às emissões, trabalhando com o
repositório através de interface (protocol) para manter o baixo acoplamento.
Nenhuma dependência direta em frameworks de web, ORM ou bibliotecas externas
além da stdlib e do próprio domínio.
"""

from __future__ import annotations

from typing import List, Optional
from datetime import date

from .model import Emissao
from .repository import EmissaoRepository


class EmissaoService:
    """Serviço que encapsula as regras de negócio para operações com emissões.

    Depende abstratamente de um EmissaoRepository (via injeção de dependência)
    para realizar operações de persistência, sem conhecer a implementação concreta.
    """

    def __init__(self, repository: EmissaoRepository) -> None:
        """Inicializa o serviço com uma instância de repositório.

        Args:
            repository: Implementação de EmissaoRepository a ser usada.
        """
        self._repository = repository

    def submeter_para_coordenacao(self, emissao_id: int) -> Optional[Emissao]:
        """Submete uma emissão para análise da coordenação.

        Regra de negócio: apenas emissões com situação 'pendente' podem ser
        submetidas para coordenação.

        Args:
            emissao_id: ID da emissão a ser submetida.

        Returns:
            Instancia de Emissao atualizada se a operação for bem-sucedida,
            None se a emissão não existir ou não puder ser submetida.
        """
        emissao = self._repository.get_by_id(emissao_id)
        if emissao is None:
            return None

        # Regra de negócio: apenas emissões pendentes podem ser submetidas
        if emissao.situacao != "pendente":
            return None

        # Atualiza o flag de submissão à coordenação
        return self._repository.update_submetida_coordenador_em(
            emissao_id, True
        )

    def validar_conflitos(self, emissao_id: int) -> bool:
        """Verifica se há conflitos de frequência para a emissão dada.

        Regra de negócio: neste momento, delegamos a verificação completa
        para uma função externa ou serviço especializado. Por enquanto,
        retornamos True (sem conflitos) como placeholder.

        Args:
            emissao_id: ID da emissão a ser verificada.

        Returns:
            True se não houver conflitos, False se houver conflitos detectados.
        """
        # Placeholder: em uma implementação real, aqui seria feita a consulta
        # ao banco de dados ou serviço externo para verificar sobreposição
        # de frequência com outras emissões do mesmo evento/local.
        # Por enquanto, assumimos que não há conflitos.
        emissao = self._repository.get_by_id(emissao_id)
        return emissao is not None

    def salvar_como_pendente(self, emissao: Emissao) -> Emissao:
        """Salva uma nova emissão com situação inicial 'pendente'.

        Args:
            emissao: Instancia de Emissao a ser salva. Deve ter ID 0 ou None.

        Returns:
            Instancia de Emissao salva com ID gerado e situação 'pendente'.
        """
        # Garante que a situação inicial seja 'pendente'
        emissao.situacao = "pendente"
        return self._repository.save(emissao)

    def concluir_emissao(self, emissao_id: int) -> Optional[Emissao]:
        """Marca uma emissão como concluída.

        Regra de negócio: apenas emissões em coordenação ou pendentes
        podem ser marcadas como concluídas.

        Args:
            emissao_id: ID da emissão a ser concluída.

        Returns:
            Instancia de Emissao atualizada se bem-sucedida, None caso contrário.
        """
        emissao = self._repository.get_by_id(emissao_id)
        if emissao is None:
            return None

        # Regra de negócio: permite concluir de pendente ou em_coordenacao
        if emissao.situacao not in ("pendente", "em_coordenacao"):
            return None

        emissao.situacao = "concluido"
        return self._repository.update(emissao)

    def cancelar_emissao(self, emissao_id: int) -> Optional[Emissao]:
        """Cancela uma emissão.

        Regra de negócio: apenas emissões pendentes podem ser canceladas diretamente.

        Args:
            emissao_id: ID da emissão a ser cancelada.

        Returns:
            Instancia de Emissao atualizada se bem-sucedida, None caso contrário.
        """
        emissao = self._repository.get_by_id(emissao_id)
        if emissao is None:
            return None

        # Regra de negócio: apenas pendentes podem ser cancelados diretamente
        if emissao.situacao != "pendente":
            return None

        emissao.situacao = "cancelado"
        return self._repository.update(emissao)

    def listar_por_evento(self, evento_id: int, incluir_todas: bool = False) -> List[Emissao]:
        """Lista todas as emissões de um determinado evento.

        Args:
            evento_id: ID do evento cuyas emissões devem ser listadas.
            incluir_todas: Se True, inclui todas as emissões.

        Returns:
            Lista de emissões associadas ao evento (pode estar vazia).
        """
        return self._repository.list_by_evento(evento_id, incluir_todas)

    def listar_por_fiscal(self, fiscal_id: int) -> List[Emissao]:
        """Lista todas as emissões registradas por um determinado fiscal.

        Args:
            fiscal_id: ID do fiscal cujas emissões devem ser listadas.

        Returns:
            Lista de emissões registradas pelo fiscal (pode estar vazia).
        """
        return self._repository.list_by_fiscal(fiscal_id)

    def obter_emissao(self, emissao_id: int) -> Optional[Emissao]:
        """Obtém uma emissão pelo seu ID.

        Args:
            emissao_id: ID da emissão a ser buscada.

        Returns:
            Instancia de Emissao se encontrada, None caso contrário.
        """
        return self._repository.get_by_id(emissao_id)