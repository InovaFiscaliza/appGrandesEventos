"""Políticas centralizadas de visibilidade de módulos e controles."""

MODULO_TESTE_ETIQUETAGEM = "teste_etiquetagem"


def modulo_disponivel(
    modulo: str,
    evento: dict | None = None,
    tipo_usuario: str | None = None,
) -> bool:
    """Informa se um módulo pode ser exibido e acessado no contexto atual.

    ``tipo_usuario`` fica disponível para as futuras regras de coordenador,
    abordagem e monitoração. Até essas regras serem definidas, ele não altera
    o resultado.
    """
    del tipo_usuario
    if modulo == MODULO_TESTE_ETIQUETAGEM and evento is not None:
        return bool(evento.get(MODULO_TESTE_ETIQUETAGEM, True))
    return True


def permissoes_interface(
    evento: dict | None = None,
    tipo_usuario: str | None = None,
) -> dict[str, bool]:
    """Retorna as permissões de módulos e controles da interface."""
    return {
        MODULO_TESTE_ETIQUETAGEM: modulo_disponivel(
            MODULO_TESTE_ETIQUETAGEM,
            evento=evento,
            tipo_usuario=tipo_usuario,
        ),
    }


def controle_disponivel(
    controle: str,
    evento: dict | None = None,
    tipo_usuario: str | None = None,
) -> bool:
    """Ponto central para futuros controles condicionais da interface."""
    return modulo_disponivel(controle, evento=evento, tipo_usuario=tipo_usuario)
