"""Políticas centralizadas de visibilidade de módulos e controles."""

MODULO_TESTE_ETIQUETAGEM = "teste_etiquetagem"
MODULO_COORDENACAO = "coordenacao"


def modulo_disponivel(
    modulo: str,
    evento: dict | None = None,
    tipo_usuario: str | None = None,
    coordenador_evento: bool = False,
) -> bool:
    """Informa se um módulo pode ser exibido e acessado no contexto atual.

    A Coordenação exige vínculo explícito do fiscal como coordenador no evento.
    """
    del tipo_usuario
    if modulo == MODULO_COORDENACAO:
        return coordenador_evento
    if modulo == MODULO_TESTE_ETIQUETAGEM and evento is not None:
        return bool(evento.get(MODULO_TESTE_ETIQUETAGEM, True))
    return True


def permissoes_interface(
    evento: dict | None = None,
    tipo_usuario: str | None = None,
    coordenador_evento: bool = False,
) -> dict[str, bool]:
    """Retorna as permissões de módulos e controles da interface."""
    return {
        MODULO_COORDENACAO: modulo_disponivel(
            MODULO_COORDENACAO,
            evento=evento,
            tipo_usuario=tipo_usuario,
            coordenador_evento=coordenador_evento,
        ),
        MODULO_TESTE_ETIQUETAGEM: modulo_disponivel(
            MODULO_TESTE_ETIQUETAGEM,
            evento=evento,
            tipo_usuario=tipo_usuario,
            coordenador_evento=coordenador_evento,
        ),
    }


def controle_disponivel(
    controle: str,
    evento: dict | None = None,
    tipo_usuario: str | None = None,
    coordenador_evento: bool = False,
) -> bool:
    """Ponto central para futuros controles condicionais da interface."""
    return modulo_disponivel(
        controle,
        evento=evento,
        tipo_usuario=tipo_usuario,
        coordenador_evento=coordenador_evento,
    )
