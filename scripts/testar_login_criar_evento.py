"""Testes do login para criar eventos, sem acessar o banco de dados.

Executar da raiz: uv run python -m unittest scripts.testar_login_criar_evento
"""

import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from starlette.middleware.sessions import SessionMiddleware

from app.routers import criar_evento, selecao


class LoginCriarEventoTests(unittest.TestCase):
    """Verifica a entrada restrita aos coordenadores cadastrados."""

    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="teste-login")
        self.app.include_router(selecao.router)
        self.client = TestClient(self.app)
        self.fiscais = [
            {
                "id": 1,
                "nome": "Coordenador",
                "local_anatel": "RJ",
                "papeis": ["Coordenação", "Monitoração"],
            },
            {
                "id": 2,
                "nome": "Fiscal",
                "local_anatel": "RJ",
                "papeis": ["Monitoração"],
            },
        ]
        self.mock_fiscais = patch.object(
            selecao, "listar_fiscais", return_value=self.fiscais
        ).start()
        self.mock_vinculos = patch.object(
            selecao, "listar_fiscais_evento", return_value={1: {}, 2: {}}
        ).start()
        self.mock_auditoria = patch.object(selecao, "registrar_login_evento").start()
        self.addCleanup(patch.stopall)

    def login(self, fiscal_id: int, papel: str, senha: str = "teste") -> Response:
        return self.client.post(
            "/",
            data={
                "evento_key": "__novo__",
                "fiscal_id": fiscal_id,
                "senha": senha,
                "papel": papel,
            },
            follow_redirects=False,
        )

    def test_coordenador_entra_sem_evento(self) -> None:
        response = self.login(1, "Coordenação")
        self.assertEqual(response.headers["location"], "/criar-evento?novo=1")
        self.mock_vinculos.assert_not_called()
        self.mock_auditoria.assert_not_called()
        self.assertEqual(
            self.client.get("/", follow_redirects=False).headers["location"],
            "/criar-evento?novo=1",
        )

    def test_fiscal_nao_pode_forjar_papel_coordenacao(self) -> None:
        self.assertEqual(self.login(2, "Coordenação").headers["location"], "/")

    def test_coordenador_nao_entra_com_outro_papel(self) -> None:
        self.assertEqual(self.login(1, "Monitoração").headers["location"], "/")

    def test_senha_obrigatoria(self) -> None:
        self.assertEqual(self.login(1, "Coordenação", "").headers["location"], "/")

    def test_usuario_inexistente(self) -> None:
        self.assertEqual(self.login(999, "Coordenação").headers["location"], "/")

    def test_login_evento_existente_preservado(self) -> None:
        response = self.client.post(
            "/",
            data={
                "evento_key": "Evento|||10",
                "fiscal_id": "1",
                "senha": "teste",
                "papel": "Coordenação",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.headers["location"], "/menu")
        self.mock_auditoria.assert_called_once_with(
            evento_id=10, usuario_fiscal="Coordenador"
        )


class CriarEventoIntegracaoTests(LoginCriarEventoTests):
    """Exercita a sessao restrita no middleware e nas rotas reais."""

    def setUp(self) -> None:
        super().setUp()
        import main

        self.client = TestClient(main.app)
        patch.object(main, "buscar_planilhas", return_value={"Evento": 10}).start()
        patch.object(main, "obter_evento", return_value=None).start()
        patch.object(criar_evento, "listar_fiscais", return_value=self.fiscais).start()
        for nome in (
            "listar_eventos_detalhes",
            "listar_municipios",
            "listar_ufs_municipios",
            "listar_unidades_executantes",
        ):
            patch.object(criar_evento, nome, return_value=[]).start()
        self.mock_criar = patch.object(
            criar_evento, "criar_evento", return_value=20
        ).start()
        self.mock_snapshot = patch.object(
            criar_evento,
            "obter_snapshot_auditoria_evento",
            return_value={"nome": "Novo evento"},
        ).start()
        self.mock_auditoria_evento = patch.object(
            criar_evento, "registrar_auditoria_evento"
        ).start()

    def test_tela_somente_de_criacao(self) -> None:
        self.login(1, "Coordenação")
        response = self.client.get("/criar-evento")
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="nome"', response.text)
        self.assertNotIn("Eventos existentes", response.text)
        self.assertNotIn('href="/menu"', response.text)
        criar_evento.listar_eventos_detalhes.assert_not_called()

    def test_modulos_e_apis_bloqueados(self) -> None:
        self.login(1, "Coordenação")
        for caminho in ("/menu", "/coordenacao", "/inserir", "/busca", "/estacoes"):
            with self.subTest(caminho=caminho):
                response = self.client.get(caminho, follow_redirects=False)
                self.assertEqual(response.headers["location"], "/criar-evento?novo=1")
        for caminho in ("/api/eventos", "/api/eventos/10/fiscais"):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.get(caminho).status_code, 403)

    def test_edicao_e_exclusao_bloqueadas(self) -> None:
        self.login(1, "Coordenação")
        response = self.client.get("/criar-evento?editar=10", follow_redirects=False)
        self.assertEqual(response.headers["location"], "/criar-evento?novo=1")
        for caminho in (
            "/criar-evento/10/editar",
            "/fiscais/2/excluir",
            "/criar-evento/10/faixas-etiqueta",
            "/inserir/salvar",
        ):
            with self.subTest(caminho=caminho):
                self.assertEqual(self.client.post(caminho).status_code, 403)

    def test_troca_pelo_cabecalho_nao_libera_restricao(self) -> None:
        self.login(1, "Coordenação")
        self.client.post(
            "/", data={"evento_key": "Evento|||10"}, follow_redirects=False
        )
        response = self.client.get("/menu", follow_redirects=False)
        self.assertEqual(response.headers["location"], "/criar-evento?novo=1")

    def test_salvar_evento_registra_auditoria_e_libera_evento_criado(self) -> None:
        self.login(1, "Coordenação")
        response = self.client.post(
            "/criar-evento", data={"nome": "Novo evento"}, follow_redirects=False
        )
        self.assertEqual(response.headers["location"], "/menu")
        self.mock_criar.assert_called_once()
        self.mock_auditoria_evento.assert_called_once_with(
            20, {}, {"nome": "Novo evento"}
        )
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.headers["location"], "/menu")

    def test_validacao_preserva_restricao(self) -> None:
        self.login(1, "Coordenação")
        response = self.client.post(
            "/criar-evento", data={"nome": ""}, follow_redirects=False
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="nome-evento"', response.text)
        self.assertIn('id="popup-erro-global"', response.text)
        self.assertNotIn(
            'class="flash flash-error">Informe o nome do evento.', response.text
        )
        self.assertEqual(self.client.get("/api/eventos").status_code, 403)
        self.mock_criar.assert_not_called()
        self.mock_auditoria_evento.assert_not_called()

    def test_validacao_preserva_dados_digitados(self) -> None:
        self.login(1, "Coordenação")
        with (
            patch.object(
                criar_evento,
                "listar_ufs_municipios",
                return_value=["RJ"],
            ),
            patch.object(
                criar_evento,
                "listar_municipios",
                return_value=[{"nome": "Rio de Janeiro", "uf": "RJ"}],
            ),
            patch.object(
                criar_evento,
                "listar_unidades_executantes",
                return_value=[{"sigla": "RJ", "nome": "Rio de Janeiro"}],
            ),
            patch.object(criar_evento, "cidade_pertence_uf", return_value=True),
        ):
            response = self.client.post(
                "/criar-evento",
                data={
                    "nome": "Evento preenchido",
                    "latitude": "-22.91",
                    "longitude": "-43.20",
                    "uf": "RJ",
                    "cidade": "Rio de Janeiro",
                    "acao_fiscalizacao": "Operação de teste",
                    "unidades_executantes": "RJ",
                    "fiscais_evento": "1",
                    "papeis_fiscal_1": "Coordenação",
                    "coordenador_responsavel": "1",
                    "processo_sei": "12345.000001/2026-10",
                    "periodo_inicio": "2026-10-20",
                    "periodo_fim": "2026-10-10",
                    "teste_etiquetagem": "nao",
                    "observacoes": "Observação que deve permanecer",
                },
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="popup-erro-global"', response.text)
        self.assertNotIn(
            'class="flash flash-error">Informe um período válido', response.text
        )
        self.assertIn('value="Evento preenchido"', response.text)
        self.assertIn('value="-22.91"', response.text)
        self.assertIn('value="-43.20"', response.text)
        self.assertIn('<option value="RJ" selected>RJ</option>', response.text)
        self.assertIn(
            '<option value="Rio de Janeiro" data-uf="RJ" selected>Rio de Janeiro</option>',
            response.text,
        )
        self.assertIn('value="Operação de teste"', response.text)
        self.assertIn('name="unidades_executantes" value="RJ" checked', response.text)
        self.assertIn('name="fiscais_evento" value="1"', response.text)
        self.assertIn('name="coordenador_responsavel" value="1" checked', response.text)
        self.assertIn('value="12345.000001/2026-10"', response.text)
        self.assertIn('value="2026-10-20"', response.text)
        self.assertIn('value="2026-10-10"', response.text)
        self.assertIn('value="nao" selected', response.text)
        self.assertIn("Observação que deve permanecer", response.text)
        self.assertIn(
            r'mostrarPopup("Informe um per\u00edodo v\u00e1lido', response.text
        )
        self.mock_criar.assert_not_called()
        self.mock_auditoria_evento.assert_not_called()

    def test_logout_encerra_sessao_restrita(self) -> None:
        self.login(1, "Coordenação")
        self.client.get("/logout", follow_redirects=False)
        response = self.client.get("/criar-evento", follow_redirects=False)
        self.assertEqual(response.headers["location"], "/")

    def test_login_sem_eventos_disponiveis(self) -> None:
        with (
            patch.object(selecao, "buscar_planilhas", return_value={}),
            patch.object(selecao, "_img_b64", return_value=""),
        ):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('value="__novo__"', response.text)
        self.assertIn('id="coordenadores-login"', response.text)


if __name__ == "__main__":
    unittest.main()
