"""Testes HTTP dos fluxos online, com persistencia simulada e templates reais."""

import unittest
from collections.abc import Awaitable, Callable
from datetime import date, time
from io import BytesIO
from typing import Any
from unittest.mock import patch

from fastapi import APIRouter, FastAPI, Request
from fastapi.testclient import TestClient
from httpx import Response as HTTPResponse
from PIL import Image
from starlette.responses import Response

from app.config import (
    STATUS_TICKET_CONCLUIDO_COORDENADOR,
    STATUS_TICKET_CONCLUIDO_FISCAIS,
    STATUS_TICKET_PENDENTE,
)
from app.routers import coordenacao, inserir, tratamento_tickets


def cliente_com_sessao(router: APIRouter, sessao: dict) -> TestClient:
    """Executa um router real com contexto controlado, sem simular suas decisoes."""
    app = FastAPI()

    @app.middleware("http")
    async def contexto(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.scope["session"] = sessao
        request.state.eventos = {}
        request.state.permissoes = {
            "teste_etiquetagem": True,
            "coordenacao": sessao.get("tipo_usuario") == "coordenação",
        }
        return await call_next(request)

    app.include_router(router)
    return TestClient(app)


class TratamentoTicketsTests(unittest.TestCase):
    """Protege conclusao pelo fiscal, autorizacao e auditoria do tratamento."""

    def setUp(self) -> None:
        self.sessao = {
            "spreadsheet_id": 10,
            "fiscal_id": 7,
            "fiscal_nome": "Fiscal teste",
            "tipo_usuario": "monitoração",
        }
        self.client = cliente_com_sessao(tratamento_tickets.router, self.sessao)
        self.addCleanup(self.client.close)
        self.ticket = {
            "id": 35,
            "status": STATUS_TICKET_PENDENTE,
            "fiscal_ids": [7],
            "providencias": "Em investigacao",
        }
        self.listar = patch.object(
            tratamento_tickets, "listar_tickets_evento", return_value=[self.ticket]
        ).start()
        self.atualizar = patch.object(
            tratamento_tickets, "atualizar_ticket_evento"
        ).start()
        self.auditar = patch.object(
            tratamento_tickets, "registrar_auditoria_coordenacao"
        ).start()
        self.addCleanup(patch.stopall)

    def enviar(self, **dados: str) -> HTTPResponse:
        """Envia o formulario real sem seguir o redirecionamento."""
        return self.client.post(
            "/tratamento-tickets/35", data=dados, follow_redirects=False
        )

    def test_concluir_exige_providencias(self) -> None:
        response = self.enviar(
            status=STATUS_TICKET_CONCLUIDO_FISCAIS, providencias="   "
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn("providências", self.sessao["flash_error"])
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()

    def test_concluir_persiste_autoria_e_auditoria(self) -> None:
        response = self.enviar(
            status=STATUS_TICKET_CONCLUIDO_FISCAIS,
            providencias="  Interferencia resolvida  ",
        )
        self.assertEqual(response.status_code, 303)
        self.atualizar.assert_called_once_with(
            ticket_id=35,
            evento_id=10,
            status=STATUS_TICKET_CONCLUIDO_FISCAIS,
            providencias="Interferencia resolvida",
            usuario_fiscal="Fiscal teste",
        )
        self.auditar.assert_called_once()
        auditoria = self.auditar.call_args.kwargs
        self.assertEqual(auditoria["evento_id"], 10)
        self.assertEqual(auditoria["usuario_fiscal"], "Fiscal teste")
        self.assertIn("Em investigacao", auditoria["valor_anterior"])
        self.assertIn(STATUS_TICKET_CONCLUIDO_FISCAIS, auditoria["valor_novo"])
        self.assertIn("Interferencia resolvida", auditoria["valor_novo"])
        self.assertIn("flash_success", self.sessao)

    def test_salvar_andamento_sem_concluir(self) -> None:
        response = self.enviar(
            status=STATUS_TICKET_PENDENTE, providencias="Inspecao iniciada"
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            self.atualizar.call_args.kwargs["status"], STATUS_TICKET_PENDENTE
        )
        self.auditar.assert_called_once()

    def test_fiscal_nao_pode_concluir_como_coordenador(self) -> None:
        for status in (STATUS_TICKET_CONCLUIDO_COORDENADOR, "inexistente", ""):
            with self.subTest(status=status):
                self.enviar(status=status, providencias="Resolvido")
                self.assertIn("inválido", self.sessao["flash_error"])
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()

    def test_ticket_de_outro_fiscal_nao_pode_ser_tratado(self) -> None:
        self.ticket["fiscal_ids"] = [99]
        self.enviar(status=STATUS_TICKET_PENDENTE, providencias="Alteracao indevida")
        self.assertIn("permissão", self.sessao["flash_error"])
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()
        self.listar.assert_called_once_with(10)

    def test_ticket_concluido_nao_pode_ser_reaberto_pelo_fiscal(self) -> None:
        for status in (
            STATUS_TICKET_CONCLUIDO_FISCAIS,
            STATUS_TICKET_CONCLUIDO_COORDENADOR,
        ):
            with self.subTest(status=status):
                self.ticket["status"] = status
                self.enviar(status=STATUS_TICKET_PENDENTE)
                self.assertIn("permissão", self.sessao["flash_error"])
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()

    def test_erro_de_atualizacao_nao_registra_sucesso_nem_auditoria(self) -> None:
        self.atualizar.side_effect = ValueError("Ticket alterado por outro usuario")
        self.enviar(status=STATUS_TICKET_PENDENTE)
        self.assertEqual(
            self.sessao["flash_error"], "Ticket alterado por outro usuario"
        )
        self.assertNotIn("flash_success", self.sessao)
        self.auditar.assert_not_called()

    def test_sem_evento_nao_consulta_nem_altera_ticket(self) -> None:
        self.sessao.clear()
        response = self.enviar(status=STATUS_TICKET_PENDENTE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "/")
        self.listar.assert_not_called()
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()


class CoordenacaoTicketsTests(unittest.TestCase):
    """Protege devolucao com motivo, papel selecionado e auditoria."""

    def setUp(self) -> None:
        self.sessao = {
            "spreadsheet_id": 10,
            "fiscal_id": 1,
            "fiscal_nome": "Coordenador teste",
            "tipo_usuario": "coordenação",
        }
        self.client = cliente_com_sessao(coordenacao.router, self.sessao)
        self.addCleanup(self.client.close)
        self.ticket = {
            "id": 35,
            "status": STATUS_TICKET_CONCLUIDO_FISCAIS,
            "fiscal_ids": [7],
            "prioridade": "normal",
            "observacoes": "Inspecao",
            "providencias": "Resolvido",
            "motivo_devolucao": None,
        }
        self.listar = patch.object(
            coordenacao, "listar_tickets_evento", return_value=[self.ticket]
        ).start()
        self.atualizar = patch.object(coordenacao, "atualizar_ticket_evento").start()
        self.auditar = patch.object(
            coordenacao, "registrar_auditoria_coordenacao"
        ).start()
        self.addCleanup(patch.stopall)

    def test_devolucao_com_campo_vazio_nao_atualiza(self) -> None:
        response = self.client.post(
            "/coordenacao/ticket/35/status",
            data={"status": STATUS_TICKET_PENDENTE, "motivo_devolucao": "   "},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn("motivo", self.sessao["flash_error"])
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()

    def test_devolucao_persiste_motivo_e_audita_estado_anterior(self) -> None:
        response = self.client.post(
            "/coordenacao/ticket/35/status",
            data={
                "status": STATUS_TICKET_PENDENTE,
                "motivo_devolucao": "  Verificar outra antena  ",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.atualizar.assert_called_once()
        dados = self.atualizar.call_args.kwargs
        self.assertEqual(dados["motivo_devolucao"], "Verificar outra antena")
        self.assertEqual(dados["usuario_fiscal"], "Coordenador teste")
        self.assertEqual(dados["evento_id"], 10)
        auditoria = self.auditar.call_args.kwargs
        self.assertEqual(auditoria["acao"], "Ticket devolvido")
        self.assertEqual(auditoria["usuario_fiscal"], "Coordenador teste")
        self.assertIn(STATUS_TICKET_CONCLUIDO_FISCAIS, auditoria["valor_anterior"])
        self.assertIn(STATUS_TICKET_PENDENTE, auditoria["valor_novo"])
        self.assertIn("Verificar outra antena", auditoria["valor_novo"])

    def test_fiscal_nao_altera_status_na_coordenacao(self) -> None:
        self.sessao["tipo_usuario"] = "monitoração"
        response = self.client.post(
            "/coordenacao/ticket/35/status",
            data={"status": STATUS_TICKET_CONCLUIDO_COORDENADOR},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/menu")
        self.listar.assert_not_called()
        self.atualizar.assert_not_called()
        self.auditar.assert_not_called()

    def test_falha_na_devolucao_nao_audita_sucesso(self) -> None:
        self.atualizar.side_effect = ValueError("Ticket pertence a outro evento")
        self.client.post(
            "/coordenacao/ticket/35/status",
            data={"status": STATUS_TICKET_PENDENTE, "motivo_devolucao": "Revisar"},
            follow_redirects=False,
        )
        self.assertEqual(self.sessao["flash_error"], "Ticket pertence a outro evento")
        self.assertNotIn("flash_success", self.sessao)
        self.auditar.assert_not_called()


class TicketDevolvidoNaTelaTests(unittest.TestCase):
    """Verifica o motivo e o alerta no HTML efetivamente entregue ao fiscal."""

    def test_motivo_e_alerta_aparecem_na_lista_do_fiscal(self) -> None:
        sessao = {"spreadsheet_id": 10, "fiscal_id": 7, "fiscal_nome": "Fiscal teste"}
        client = cliente_com_sessao(tratamento_tickets.router, sessao)
        self.addCleanup(client.close)
        ticket = {
            "id": 35,
            "status": STATUS_TICKET_PENDENTE,
            "fiscal_ids": [7],
            "motivo_devolucao": "Verificar outra antena",
            "ocorrencia_ids": "703",
        }
        with patch.object(
            tratamento_tickets, "listar_tickets_evento", return_value=[ticket]
        ):
            response = client.get("/tratamento-tickets")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Verificar outra antena", response.text)
        self.assertIn("fa-exclamation-circle", response.text)
        self.assertIn('data-ticket-id="35"', response.text)
        self.assertIn('data-ocorrencia-id="703"', response.text)


class CadastroEmissoesTests(unittest.TestCase):
    """Protege salvar/submeter, validacoes, conflitos informativos e anexos."""

    def setUp(self) -> None:
        self.sessao = {
            "spreadsheet_id": 10,
            "fiscal_id": 7,
            "fiscal_nome": "Fiscal teste",
            "tipo_usuario": "monitoração",
        }
        self.client = cliente_com_sessao(inserir.router, self.sessao)
        self.addCleanup(self.client.close)
        self.dados = {
            "dia": "2026-10-11",
            "hora": "12:30",
            "local": "Arena",
            "freq": "433,925",
            "larg": "25 kHz",
            "faixa": "SLP",
            "ident": "Sinal de dados",
            "estacao_id": "campo_analisador",
            "interferente": "Não",
            "ute": "Não",
            "obs": "Registro de teste",
            "situacao": "Pendente",
        }
        patch.object(
            inserir, "carregar_opcoes_identificacao", return_value=["Sinal de dados"]
        ).start()
        patch.object(
            inserir,
            "listar_estacoes_evento",
            return_value=[{"id": 4, "nome": "Estacao teste"}],
        ).start()
        patch.object(
            inserir, "listar_fiscais_evento", return_value={7: {}, 8: {}}
        ).start()
        patch.object(
            inserir,
            "listar_fiscais",
            return_value=[
                {"id": 7, "nome": "Fiscal teste"},
                {"id": 8, "nome": "Participante"},
            ],
        ).start()
        patch.object(
            inserir, "obter_fuso_horario_evento", return_value="America/Sao_Paulo"
        ).start()
        self.equipamento = patch.object(
            inserir, "verificar_equipamento_frequencia", return_value=None
        ).start()
        self.conflitos = patch.object(
            inserir, "consultar_conflitos_frequencia", return_value=[]
        ).start()
        self.salvar = patch.object(
            inserir, "inserir_emissao_I_W", return_value=703
        ).start()
        self.addCleanup(patch.stopall)

    def enviar(
        self, caminho: str = "/inserir/salvar", **alteracoes: Any
    ) -> HTTPResponse:
        """Submete o formulario real com dados validos por padrao."""
        return self.client.post(
            caminho, data={**self.dados, **alteracoes}, follow_redirects=False
        )

    def test_salvar_forca_pendente_sem_submeter(self) -> None:
        response = self.enviar(
            situacao="Concluída Pelo Coordenador", fiscal="Outro fiscal"
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/inserir")
        self.salvar.assert_called_once()
        dados = self.salvar.call_args.kwargs["dados_formulario"]
        self.assertEqual(dados["Situação"], "Pendente")
        self.assertFalse(dados.get("Submeter ao coordenador", False))
        self.assertEqual(dados["Fiscal"], "Fiscal teste")
        self.assertEqual(dados["Criador fiscal ID"], 7)
        self.assertEqual(dados["Frequência em MHz"], 433.925)
        self.assertEqual(dados["Largura em kHz"], 25)
        self.assertEqual(dados["Dia"], date(2026, 10, 11))
        self.assertEqual(dados["Hora"], time(12, 30))
        self.assertIsNone(dados["Estação ID"])
        self.assertEqual(dados["Origem da captura"], "Analisador de espectro - campo")

    def test_submeter_preserva_acao_e_status_do_fiscal(self) -> None:
        response = self.enviar(
            "/inserir", situacao="Concluída Pelo Fiscal", estacao_id="4"
        )
        self.assertEqual(response.status_code, 303)
        dados = self.salvar.call_args.kwargs["dados_formulario"]
        self.assertTrue(dados["Submeter ao coordenador"])
        self.assertEqual(dados["Situação"], "Concluída Pelo Fiscal")
        self.assertEqual(dados["Estação ID"], 4)
        self.assertIsNone(dados["Origem da captura"])

    def test_conflitos_sao_consultados_antes_de_ambas_as_gravacoes(self) -> None:
        def gravar(**kwargs: Any) -> int:
            self.equipamento.assert_called_once_with(
                evento_id=10,
                freq_digitada=433.925,
                largura_khz=25.0,
                localidade="Arena",
            )
            self.conflitos.assert_called_once_with(
                evento_id=10, freq_digitada=433.925, largura_khz=25.0, localidade=""
            )
            return 703

        self.salvar.side_effect = gravar
        for caminho in ("/inserir/salvar", "/inserir"):
            with self.subTest(caminho=caminho):
                self.equipamento.reset_mock()
                self.conflitos.reset_mock()
                self.assertEqual(self.enviar(caminho).status_code, 303)

    def test_conflito_informa_entidade_sem_bloquear_salvamento(self) -> None:
        self.equipamento.return_value = "Equipamento etiqueta E-123"
        self.conflitos.return_value = [
            {
                "origem": "Ocorrência",
                "id": 704,
                "frequencia": 433.925,
                "largura_khz": 25,
                "local": "Palco",
                "etiqueta": "Radio teste",
                "criador_fiscal_id": 8,
                "responsavel": "Outro fiscal",
            }
        ]
        for caminho in ("/inserir/salvar", "/inserir"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.enviar(caminho).status_code, 303)
                for texto in ("E-123", "704", "433.925", "Palco", "Outro fiscal"):
                    self.assertIn(texto, self.sessao["flash_success"])
        self.assertEqual(self.salvar.call_count, 2)

    def test_formulario_invalido_preserva_dados_e_nao_grava(self) -> None:
        casos = (
            {"freq": "0"},
            {"freq": "invalida"},
            {"larg": "13 kHz"},
            {"ute": ""},
            {"ute": "Sim", "proc": "", "ato_ute": ""},
            {"estacao_id": "999"},
            {"fiscais_participantes": "99"},
        )
        for caminho in ("/inserir/salvar", "/inserir"):
            for alteracoes in casos:
                with self.subTest(caminho=caminho, alteracoes=alteracoes):
                    response = self.enviar(caminho, **alteracoes)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn('value="Arena"', response.text)
                    self.assertIn("Registro de teste", response.text)
                    self.assertIn('id="popup-erro-global"', response.text)
                    self.assertIn(
                        "Preencha os campos obrigatórios",
                        response.context["flash_error"],
                    )
        self.salvar.assert_not_called()
        self.equipamento.assert_not_called()
        self.conflitos.assert_not_called()

    def test_participantes_validos_sao_deduplicados(self) -> None:
        response = self.enviar(fiscais_participantes=["8", "8"])
        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            self.salvar.call_args.kwargs["dados_formulario"]["Fiscais participantes"],
            [8],
        )

    def test_submissao_nao_aceita_status_do_coordenador(self) -> None:
        response = self.enviar("/inserir", situacao="Concluída Pelo Coordenador")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Status", response.text)
        self.salvar.assert_not_called()

    def test_ute_aceita_processo_ou_ato(self) -> None:
        for autorizacao in ({"proc": "12345.000001/2026-10"}, {"ato_ute": "Ato 123"}):
            with self.subTest(autorizacao=autorizacao):
                response = self.enviar(ute="Sim", **autorizacao)
                self.assertEqual(response.status_code, 303)
                self.assertEqual(
                    self.salvar.call_args.kwargs["dados_formulario"]["UTE?"], "Sim"
                )

    def test_foto_png_e_encaminhada_com_conteudo(self) -> None:
        arquivo = BytesIO()
        Image.new("RGB", (2, 2), "red").save(arquivo, format="PNG")
        response = self.client.post(
            "/inserir/salvar",
            data=self.dados,
            files={"imagens": ("foto.png", arquivo.getvalue(), "image/png")},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        imagens = self.salvar.call_args.kwargs["imagens"]
        self.assertEqual(len(imagens), 1)
        self.assertEqual(imagens[0]["nome_arquivo"], "foto.png")
        self.assertEqual(imagens[0]["conteudo"], arquivo.getvalue())

    def test_anexo_invalido_ou_vazio_nao_grava(self) -> None:
        for nome, conteudo, mime in (
            ("foto.exe", b"arquivo", "application/octet-stream"),
            ("foto.png", b"", "image/png"),
            ("foto.png", b"arquivo", "text/plain"),
        ):
            with self.subTest(nome=nome, mime=mime, vazio=not conteudo):
                response = self.client.post(
                    "/inserir/salvar",
                    data=self.dados,
                    files={"imagens": (nome, conteudo, mime)},
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("Imagem", response.context["flash_error"])
        self.salvar.assert_not_called()

    def test_sem_fiscal_nao_chega_a_persistencia(self) -> None:
        del self.sessao["fiscal_id"]
        response = self.enviar()
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/menu")
        self.salvar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
