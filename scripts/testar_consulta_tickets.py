"""Testes da consulta publica aos usuarios do evento, sem banco real."""

import unittest
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.routers import consulta_tickets


class ConsultaTicketsTests(unittest.TestCase):
    """Valida acesso de fiscais, vinculos clicaveis e isolamento por evento."""

    def setUp(self) -> None:
        self.session = {"spreadsheet_id": 10, "fiscal_id": 7, "tipo_usuario": "Monitoração"}
        app = FastAPI()

        @app.middleware("http")
        async def contexto(request: Request, call_next):
            request.scope["session"] = self.session
            request.state.eventos = {}
            request.state.permissoes = {}
            return await call_next(request)

        app.include_router(consulta_tickets.router)
        self.client = TestClient(app)
        self.ticket = {
            "id": 35, "status": "pendente", "prioridade": "normal",
            "fiscal_ids": [99], "fiscais": "Outro fiscal",
            "ocorrencia_ids": "703", "incidente_ids": "53",
            "observacoes": "Observacao da coordenacao", "providencias": "Providencia",
            "motivo_devolucao": "Motivo", "atualizado_em": "10/10/2026 12:30",
            "emissoes": [{"id": 703, "identificacao": "Sinal de dados", "situacao": "Pendente", "cadastrado_por": "Autor", "observacoes": "Observacao da emissao", "imagens": []}],
            "incidentes": [{"id": 53, "tipo": "BSR", "situacao": "Pendente", "cadastrado_por": "Autor", "observacoes": "Observacao do incidente", "imagens": []}],
        }

    def test_fiscal_consulta_todos_status_e_atribuicoes(self) -> None:
        for status in ("pendente", "concluido_pelos_fiscais", "concluido_pelo_coordenador"):
            with self.subTest(status=status), patch.object(consulta_tickets, "listar_tickets_evento", return_value=[{**self.ticket, "status": status}]) as listar:
                response = self.client.get("/tickets")
                self.assertEqual(response.status_code, 200)
                self.assertIn('href="/tickets/35"', response.text)
                self.assertIn("registro=emissao-703", response.text)
                self.assertIn("registro=incidente-53", response.text)
                self.assertIn("Outro fiscal", response.text)
                listar.assert_called_once_with(10)

    def test_detalhes_e_registros_sem_acoes_de_edicao(self) -> None:
        with (
            patch.object(consulta_tickets, "obter_detalhes_ticket_evento", return_value=self.ticket) as obter,
            patch.object(consulta_tickets, "carregar_imagens_ocorrencias", return_value={}),
        ):
            response = self.client.get("/tickets/35?registro=emissao-703")
        obter.assert_called_once_with(10, 35)
        self.assertEqual(response.status_code, 200)
        for texto in ("Observacao da emissao", "Observacao do incidente", "Providencia", "Motivo", 'id="emissao-703"', 'id="incidente-53"'):
            self.assertIn(texto, response.text)
        self.assertNotIn('method="post"', response.text)
        self.assertEqual(self.client.post("/tickets/35").status_code, 405)

    def test_ticket_de_outro_evento_nao_encontrado(self) -> None:
        with patch.object(consulta_tickets, "obter_detalhes_ticket_evento", return_value=None) as obter:
            self.assertEqual(self.client.get("/tickets/35").status_code, 404)
        obter.assert_called_once_with(10, 35)

    def test_sessao_obrigatoria(self) -> None:
        self.session.clear()
        for caminho in ("/tickets", "/tickets/35"):
            response = self.client.get(caminho, follow_redirects=False)
            self.assertEqual(response.headers["location"], "/")


if __name__ == "__main__":
    unittest.main()