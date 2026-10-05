"""Domínio: Repositório de Emissão.

Define o protocolo (interface) para operações de persistência relacionadas a emissões.
A implementação concreta (ex: PostgresEmissaoRepository) deve ser fornecida pela camada
de infraestrutura (ex: usando SQLAlchemy, etc.).
"""

from __future__ import annotations

from typing import Protocol, List, Optional

from datetime import date

from .model import Emissao

class EmissaoRepository(Protocol):
    """Protocolo que define as operações necessárias para manipular emissões.

    Implementações concretas devem fornecer acesso ao mecanismo de persistência
    escolhido (banco de dados, arquivo, serviço externo, etc.) mantendo esta
    interface para que a camada de serviço possa trabalhar com abstração.
    """

    def get_by_id(self, emissao_id: int) -> Optional[Emissao]:
        """Busca uma emissão pelo seu identificador único.

        Args:
            emissao_id: ID da emissão na tabela `ocorrencias`.

        Returns:
            Instância de Emissao se encontrada, None caso contrário.
        """
        ...

    def list_by_evento(self, evento_id: int, incluir_todas: bool = False) -> List[Emissao]:
        """Lista todas as emissões associadas a um determinado evento.

        Args:
            evento_id: ID do evento cujas emissões devem ser listadas.
            incluir_todas: Se True, inclui todas as emissões (não filtra por situação pendente/submetida).

        Returns:
            Lista de instâncias de Emissao (pode estar vazia).
        """
        ...

    def list_by_fiscal(self, fiscal_id: int) -> List[Emissao]:
        """Lista todas as emissões registradas por um determinado fiscal.

        Args:
            fiscal_id: ID do fiscal cujas emissões devem ser listadas.

        Returns:
            Lista de instâncias de Emissao (pode estar vazia).
        """
        ...

    def save(self, emissao: Emissao) -> Emissao:
        """Persiste uma nova emissão e retorna a instância com ID gerado (se aplicável).

        Args:
            emissao: Instância de Emissao a ser salva. Deve ter ID 0 ou None para indicar
                    que é um novo registro.

        Returns:
            Instância de Emissao com os campos preenchidos pelo mecanismo de persistência
            (ex: ID gerado, timestamps, etc.).
        """
        ...

    def update(self, emissao: Emissao) -> Emissao:
        """Atualiza uma emissão existente no repositório.

        Args:
            emissao: Instancia de Emissao com ID válido e campos a serem atualizados.

        Returns:
            Instancia de Emissao após a atualização.

        Raises:
            ValueError: Se a emissão com o ID fornecido não existir.
        """
        ...

    def delete(self, emissao_id: int) -> bool:
        """Remove uma emissão do repositório pelo seu ID.

        Args:
            emissao_id: ID da emissão a ser removida.

        Returns:
            True se a emissão foi encontrada e removida, False caso contrário.
        """
        ...

    def update_submetida_coordenador_em(
        self, emissao_id: int, submetida_coordenador_em: bool
    ) -> Optional[Emissao]:
        """Atualiza apenas o flag de submissão à coordenação de uma emissão.

        Args:
            emissao_id: ID da emissão cuja flag será atualizada.
            submetida_coordenador_em: Novo valor para o flag.

        Returns:
            Instancia de Emissao atualizada se encontrada, None caso contrário.
        """
        ...


# Placeholder para implementação concreta (ex: usando SQLAlchemy)
# Esta classe seria implementada na camada de infraestrutura, por exemplo:
# class PostgresEmissaoRepository:
#     def __init__(self, session: Session):
#         self.session = session
#     ...
#     def get_by_id(self, emissao_id: int) -> Optional[Emissao]:
#         ...
#
# Para manter a independência da camada de domínio, a implementação concreta
# fica fora deste módulo (ex: app/infrastructure/persistence/postgres/emissao_repository.py).