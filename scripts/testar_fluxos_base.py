"""Contratos de navegacao, sessao e permissoes da aplicacao real."""

import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response

import main


class CalendarioEscalasTests(unittest.TestCase):
    """Protege dias, jornadas e navegacao mensal do calendario."""

    def test_fevereiro_bissexto_distribui_as_escalas(self) -> None:
        from app.utils.escalas import montar_calendario_escalas

        escala = {"data_trabalho": "2028-02-29", "fiscal_nome": "Fiscal teste"}
        calendario = montar_calendario_escalas([escala], "2028-02")
        dias = [dia for semana in calendario["semanas"] for dia in semana]
        self.assertEqual(sum(bool(dia["numero"]) for dia in dias), 29)
        self.assertEqual(
            next(dia for dia in dias if dia["numero"] == 29)["escalas"], [escala]
        )
        self.assertEqual(calendario["total"], 1)
        self.assertEqual(calendario["anterior"], "2028-01")
        self.assertEqual(calendario["proximo"], "2028-03")

    def test_paginacao_cruza_ano_e_nao_mistura_meses(self) -> None:
        from app.utils.escalas import montar_calendario_escalas

        escalas = [{"data_trabalho": "2026-12-31"}, {"data_trabalho": "2027-01-01"}]
        calendario = montar_calendario_escalas(escalas, "2026-12")
        self.assertEqual(calendario["proximo"], "2027-01")
        self.assertEqual(calendario["total"], 1)
        self.assertEqual(
            montar_calendario_escalas(escalas, "2027-01")["anterior"], "2026-12"
        )

    def test_mes_invalido_e_limites_nao_quebram_calendario(self) -> None:
        from app.utils.escalas import montar_calendario_escalas

        escala = {"data_trabalho": "2026-10-13"}
        self.assertEqual(
            montar_calendario_escalas([escala], "invalido")["mes"], "2026-10"
        )
        self.assertIsNone(montar_calendario_escalas([], "0001-01")["anterior"])
        self.assertIsNone(montar_calendario_escalas([], "9999-12")["proximo"])


class NavegacaoEstruturalTests(unittest.TestCase):
    """Protege o nome da tela atual no cabecalho compartilhado."""

    def test_cabecalho_identifica_coordenacao_e_preserva_outros_caminhos(self) -> None:
        template = main.coordenacao.templates.env.get_template("partials/header.html")
        for caminho, titulo in (
            ("/coordenacao", "Coordenação do evento"),
            ("/coordenacao/", "Coordenação do evento"),
            ("/escalas", "Escalas dos fiscais"),
            ("/criar-evento", "Gerenciar eventos"),
        ):
            with self.subTest(caminho=caminho):
                request = Request(
                    {
                        "type": "http",
                        "scheme": "http",
                        "server": ("testserver", 80),
                        "path": caminho,
                        "query_string": b"aba=escala",
                        "headers": [],
                        "session": {},
                    }
                )
                html = template.render(request=request)
                self.assertIn('<a href="/menu">Início</a>', html)
                self.assertIn(f'<span aria-current="page">{titulo}</span>', html)


class NavegacaoHTTPTests(unittest.TestCase):
    """Protege os pontos de entrada comuns usando o app e os cookies reais."""

    def setUp(self) -> None:
        self.client = TestClient(main.app)
        self.addCleanup(self.client.close)
        self.eventos = patch.object(main, "buscar_planilhas").start()
        self.evento = patch.object(main, "obter_evento").start()
        self.addCleanup(patch.stopall)

    def test_modulos_exigem_login(self) -> None:
        for caminho in (
            "/menu",
            "/inserir",
            "/consultar",
            "/consultar/historico",
            "/coordenacao",
            "/tickets",
            "/bsr_erb",
            "/busca",
            "/estacoes",
            "/tabela_ute",
            "/auditoria",
            "/escalas",
        ):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho, follow_redirects=False)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["location"], "/")
        self.eventos.assert_not_called()
        self.evento.assert_not_called()

    def test_gravacoes_sem_sessao_nao_chegam_as_rotas(self) -> None:
        for caminho in ("/inserir/salvar", "/criar-evento", "/consultar"):
            with self.subTest(caminho=caminho):
                response = self.client.post(caminho, follow_redirects=False)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["location"], "/")
        self.eventos.assert_not_called()
        self.evento.assert_not_called()

    def test_cookie_sem_assinatura_nao_libera_acesso(self) -> None:
        self.client.cookies.set("session", "sessao-adulterada")
        response = self.client.get("/menu", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "/")
        self.eventos.assert_not_called()

    def test_recursos_estaticos_acessiveis_sem_login_e_sem_banco(self) -> None:
        for caminho in ("/static/style.css", "/static/app.js"):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.content)
        self.eventos.assert_not_called()
        self.evento.assert_not_called()


class ContextoEPermissoesTests(unittest.IsolatedAsyncioTestCase):
    """Exercita o middleware real sem substituir sua decisao de acesso."""

    def setUp(self) -> None:
        self.session = {
            "spreadsheet_id": "10",
            "fiscal_id": 7,
            "fiscal_nome": "Fiscal teste",
            "tipo_usuario": "monitoração",
        }
        self.eventos = patch.object(
            main, "buscar_planilhas", return_value={"Evento teste": 10}
        ).start()
        self.evento = patch.object(
            main, "obter_evento", return_value={"teste_etiquetagem": True}
        ).start()
        self.addCleanup(patch.stopall)
        self.proxima_rota = AsyncMock(return_value=Response(status_code=200))

    def request(self, caminho: str, sessao: dict | None = None) -> Request:
        """Cria um contexto de requisicao com os dados da sessao do fiscal."""
        return Request(
            {
                "type": "http",
                "method": "GET",
                "path": caminho,
                "query_string": b"",
                "headers": [],
                "scheme": "http",
                "server": ("testserver", 80),
                "session": self.session if sessao is None else sessao,
            }
        )

    async def test_sessao_incompleta_redireciona_sem_consultar_banco(self) -> None:
        for sessao in ({}, {"spreadsheet_id": "10"}, {"fiscal_id": 7}):
            with self.subTest(sessao=sessao):
                response = await main.carregar_eventos_no_request(
                    self.request("/menu", sessao), self.proxima_rota
                )
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["location"], "/")
        self.proxima_rota.assert_not_awaited()
        self.eventos.assert_not_called()
        self.evento.assert_not_called()

    async def test_fiscal_recebe_contexto_sem_permissao_de_coordenacao(self) -> None:
        request = self.request("/menu")
        response = await main.carregar_eventos_no_request(request, self.proxima_rota)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.state.eventos, {"Evento teste": 10})
        self.assertFalse(request.state.permissoes["coordenacao"])
        self.assertTrue(request.state.permissoes["teste_etiquetagem"])
        self.evento.assert_called_once_with(10)
        self.proxima_rota.assert_awaited_once_with(request)

    async def test_coordenador_recebe_permissao_do_papel_selecionado(self) -> None:
        self.session["tipo_usuario"] = " Coordenação "
        request = self.request("/menu")
        await main.carregar_eventos_no_request(request, self.proxima_rota)
        self.assertTrue(request.state.permissoes["coordenacao"])

    async def test_evento_pode_desativar_teste_etiquetagem(self) -> None:
        self.evento.return_value = {"teste_etiquetagem": False}
        request = self.request("/menu")
        await main.carregar_eventos_no_request(request, self.proxima_rota)
        self.assertFalse(request.state.permissoes["teste_etiquetagem"])

    async def test_historico_nao_carrega_lista_completa_de_eventos(self) -> None:
        request = self.request("/consultar/historico")
        response = await main.carregar_eventos_no_request(request, self.proxima_rota)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.state.eventos, {})
        self.eventos.assert_not_called()
        self.evento.assert_called_once_with(10)
        self.proxima_rota.assert_awaited_once_with(request)

    async def test_sessao_de_criacao_invalida_e_encerrada(self) -> None:
        for sessao in (
            {"criacao_evento": True, "tipo_usuario": "coordenação"},
            {**self.session, "criacao_evento": True},
        ):
            with self.subTest(sessao=sessao.copy()):
                response = await main.carregar_eventos_no_request(
                    self.request("/menu", sessao), self.proxima_rota
                )
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["location"], "/")
                self.assertEqual(sessao, {})
        self.proxima_rota.assert_not_awaited()
        self.eventos.assert_not_called()
        self.evento.assert_not_called()


if __name__ == "__main__":
    unittest.main()
