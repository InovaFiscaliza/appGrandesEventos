"""Testes do login para criar eventos, sem acessar o banco de dados.

Executar da raiz: uv run python -m unittest scripts.testar_login_criar_evento
"""

import json
import unittest
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch

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


class EmissoesPendentesTests(unittest.IsolatedAsyncioTestCase):
    """Verifica a leitura e a visibilidade das pendências sem banco real."""

    def setUp(self) -> None:
        from starlette.requests import Request
        from app.infrastructure.persistence.postgres.emissao_repository import (
            PostgresEmissaoRepository,
        )

        self.repository = PostgresEmissaoRepository()
        self.request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/menu",
                "query_string": b"",
                "headers": [],
                "scheme": "http",
                "server": ("testserver", 80),
                "session": {
                    "spreadsheet_id": "10",
                    "fiscal_id": 7,
                    "fiscal_nome": "Fiscal teste",
                    "tipo_usuario": "monitoração",
                },
            }
        )
        self.record = {
            "id": 1,
            "evento_id": 10,
            "frequencia_mhz": 433.925,
            "largura_khz": 25,
            "local_regiao": "Local teste",
            "identificacao": "Não identificado",
            "situacao": "Pendente",
            "fonte": "ESTACAO",
            "data": date(2026, 10, 10),
            "hora": time(12, 30),
            "criado_por_fiscal_id": 7,
            "cadastrado_por": "Fiscal teste",
            "submetida_coordenador_em": None,
        }

    def listar(self, records: list[dict]) -> list:
        """Executa o repositório com os tipos nativos retornados pelo PostgreSQL."""
        engine = MagicMock()
        engine.connect.return_value.__enter__.return_value.execute.return_value.mappings.return_value.all.return_value = (
            records
        )
        with patch(
            "app.infrastructure.persistence.postgres.emissao_repository.get_engine",
            return_value=engine,
        ):
            return self.repository.list_by_evento(10, incluir_todas=True)

    def test_leitura_preserva_tipos_e_autoria(self) -> None:
        emissao = self.listar([self.record])[0]
        self.assertEqual(emissao.data, self.record["data"])
        self.assertEqual(emissao.hora, self.record["hora"])
        self.assertEqual(emissao.fiscal_id, 7)
        textual = {**self.record, "data": "2026-10-10", "hora": "12:30:00"}
        self.assertEqual(self.listar([textual])[0].data, emissao.data)

    async def test_menu_conta_apenas_pendencias_proprias_nao_submetidas(self) -> None:
        from app.routers import menu

        records = [
            {**self.record, "cadastrado_por": "Nome atualizado"},
            {**self.record, "id": 2, "criado_por_fiscal_id": 8},
            {**self.record, "id": 3, "situacao": "Concluída Pelo Fiscal"},
            {
                **self.record,
                "id": 4,
                "submetida_coordenador_em": datetime(2026, 10, 10),
            },
            {**self.record, "id": 5, "criado_por_fiscal_id": None, "fonte": None},
        ]
        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(records)
        with (
            patch.object(menu, "get_city_map_url", return_value=""),
            patch.object(menu, "listar_tickets_evento", return_value=[]),
            patch.object(menu, "_img_b64", return_value=""),
            patch.object(menu.templates, "TemplateResponse") as template,
        ):
            await menu.get_menu(self.request, service)
        context = template.call_args.args[2]
        self.assertEqual(context["total"], 2)
        self.assertTrue(context["exibir_tratamento_pendencias"])

    async def test_menu_sem_pendencias_oculta_modulo(self) -> None:
        from app.routers import menu

        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(
            [
                {**self.record, "situacao": "Concluída Pelo Fiscal"},
            ]
        )
        with (
            patch.object(menu, "get_city_map_url", return_value=""),
            patch.object(menu, "listar_tickets_evento", return_value=[]),
            patch.object(menu, "_img_b64", return_value=""),
            patch.object(menu.templates, "TemplateResponse") as template,
        ):
            await menu.get_menu(self.request, service)
        self.assertEqual(template.call_args.args[2]["total"], 0)
        self.assertFalse(template.call_args.args[2]["exibir_tratamento_pendencias"])

    async def test_consulta_permite_editar_propria_pendente(self) -> None:
        from app.routers import consultar

        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(
            [
                self.record,
                {**self.record, "id": 2, "criado_por_fiscal_id": 8},
                {
                    **self.record,
                    "id": 3,
                    "submetida_coordenador_em": datetime(2026, 10, 10),
                },
                {**self.record, "id": 4, "situacao": "Concluída Pelo Fiscal"},
                {**self.record, "id": 5, "criado_por_fiscal_id": None},
                {**self.record, "id": 6, "situacao": "Concluída Pelo Coordenador"},
            ]
        )
        rows = await consultar._load_pendencias(self.request, 10, service)
        self.assertEqual(rows["ID"].tolist(), [1, 3, 5])
        self.assertEqual(rows["PodeEditar"].tolist(), [True, False, True])
        self.assertEqual(rows["CadastradoPor"].tolist(), ["Fiscal teste"] * 3)

    async def test_api_preserva_cadastrador(self) -> None:
        from app.routers import consultar

        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(
            [
                {**self.record, "cadastrado_por": "Lobão"},
                {**self.record, "id": 2, "cadastrado_por": None},
                {**self.record, "id": 3, "criado_por_fiscal_id": 8},
                {**self.record, "id": 4, "situacao": "Concluída Pelo Coordenador"},
            ]
        )
        with patch.object(consultar, "carregar_imagens_ocorrencia", return_value=[]):
            response = await consultar.api_pendencias(self.request, service)
        records = json.loads(response.body)
        self.assertEqual([record["id"] for record in records], ["1", "2"])
        self.assertEqual(records[0]["cadastrado_por"], "Lobão")
        self.assertEqual(records[1]["cadastrado_por"], "Não informado")

    async def test_ticket_nao_amplia_consulta_comum(self) -> None:
        from app.routers import consultar

        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(
            [
                self.record,
                {**self.record, "id": 2, "criado_por_fiscal_id": 8},
                {**self.record, "id": 3, "situacao": "Concluída Pelo Coordenador"},
                {**self.record, "id": 4, "situacao": "Concluída Pelo Fiscal"},
                {**self.record, "id": 5, "situacao": "Cancelada"},
                {**self.record, "id": 6, "situacao": ""},
            ]
        )
        for query in (b"", b"ticket_id=99", b"ticket_id=99&popup=1"):
            with self.subTest(query=query):
                self.request.scope["query_string"] = query
                rows = await consultar._load_pendencias(self.request, 10, service)
                self.assertEqual(rows["ID"].tolist(), [1])

    def preparar_emissao_ticket(self) -> tuple[MagicMock, dict]:
        """Prepara uma emissao de outro cadastrador atribuida ao fiscal por ticket."""
        from starlette.requests import Request

        self.request = Request(
            {
                **self.request.scope,
                "query_string": b"popup=1&emissao_id=703&ticket_id=99",
            }
        )
        service = MagicMock()
        service.listar_por_evento.return_value = self.listar(
            [
                {
                    **self.record,
                    "id": 703,
                    "criado_por_fiscal_id": 8,
                    "cadastrado_por": "Outro fiscal",
                    "submetida_coordenador_em": datetime(2026, 10, 10),
                },
                {**self.record, "id": 704},
            ]
        )
        ticket = {
            "id": 99,
            "evento_id": 10,
            "ocorrencia_ids": "703, 705",
            "fiscal_ids": [7],
            "status": "pendente",
        }
        return service, ticket

    async def test_popup_ticket_abre_emissao_de_outro_fiscal(self) -> None:
        from app.routers import consultar

        service, ticket = self.preparar_emissao_ticket()
        with (
            patch.object(consultar, "listar_tickets_evento", return_value=[ticket]),
            patch.object(consultar, "listar_estacoes_evento", return_value=[]),
            patch.object(consultar, "_img_b64", return_value=""),
            patch.object(consultar.templates, "TemplateResponse") as template,
            patch.object(consultar, "carregar_imagens_ocorrencia", return_value=[]),
        ):
            await consultar.get_consultar(self.request, emissao_id=703, emissao_service=service)
            self.assertEqual(template.call_args.args[2]["selected_row"]["ID"], 703)
            response = await consultar.api_pendencias(self.request, service)
            imagens = await consultar.api_ocorrencia_imagens(self.request, 703, service)
            self.assertEqual(imagens.status_code, 200)
        records = json.loads(response.body)
        self.assertEqual([record["id"] for record in records], ["703"])
        self.assertTrue(records[0]["pode_editar"])
        self.assertEqual(records[0]["cadastrado_por"], "Outro fiscal")

    async def test_popup_ticket_salva_emissao_com_usuario_da_sessao(self) -> None:
        from starlette.datastructures import FormData
        from app.routers import consultar

        service, ticket = self.preparar_emissao_ticket()
        self.request._form = FormData(
            {
                "id_val": "703",
                "fonte": "ESTACAO",
                "ident_edit": "Sinal de dados",
                "ute_check": "Não",
                "estacao_id": "1",
                "obs_edit": "Providencia registrada",
            }
        )
        with (
            patch.object(consultar, "listar_tickets_evento", return_value=[ticket]),
            patch.object(consultar, "atualizar_campos_na_aba_mae", return_value="Salvo") as salvar,
        ):
            response = await consultar.post_consultar_salvar(self.request, service)
        salvar.assert_called_once()
        self.assertEqual(salvar.call_args.kwargs["id_ocorrencia"], "703")
        self.assertEqual(salvar.call_args.kwargs["usuario_fiscal"], "Fiscal teste")
        self.assertEqual(response.status_code, 303)
        self.assertIn("emissao_id=703&ticket_id=99&popup=1", response.headers["location"])

    async def test_popup_ticket_valida_vinculo_fiscal_evento_e_status(self) -> None:
        from app.routers import consultar

        casos = [
            ({"fiscal_ids": [8]}, [], None),
            ({"ocorrencia_ids": "704"}, [], None),
            ({"id": 100}, [], None),
            ({"status": "concluido_pelos_fiscais"}, [703], False),
            ({"status": "concluido_pelo_coordenador"}, [703], False),
        ]
        for alteracoes, ids, pode_editar in casos:
            with self.subTest(alteracoes=alteracoes):
                service, ticket = self.preparar_emissao_ticket()
                with patch.object(consultar, "listar_tickets_evento", return_value=[{**ticket, **alteracoes}]):
                    rows = await consultar._load_pendencias(self.request, 10, service)
                self.assertEqual(rows["ID"].tolist(), ids)
                if ids:
                    self.assertEqual(bool(rows.iloc[0]["PodeEditar"]), pode_editar)
        service, ticket = self.preparar_emissao_ticket()
        service.listar_por_evento.return_value[0].evento_id = 20
        with patch.object(consultar, "listar_tickets_evento", return_value=[ticket]):
            rows = await consultar._load_pendencias(self.request, 10, service)
        self.assertTrue(rows.empty)

    async def test_popup_ticket_bloqueia_salvar_emissao_nao_vinculada(self) -> None:
        from starlette.datastructures import FormData
        from app.routers import consultar

        service, ticket = self.preparar_emissao_ticket()
        self.request._form = FormData({"id_val": "704"})
        with (
            patch.object(consultar, "listar_tickets_evento", return_value=[ticket]),
            patch.object(consultar, "atualizar_campos_na_aba_mae") as salvar,
        ):
            response = await consultar.post_consultar_salvar(self.request, service)
        salvar.assert_not_called()
        self.assertEqual(response.status_code, 303)
        self.assertIn("permissão", self.request.session["flash_error"])

    async def test_coordenacao_oculta_incidentes_vinculados_na_inspecao(self) -> None:
        from app.routers import coordenacao

        self.request.session["tipo_usuario"] = "Coordenação"
        incidente_disponivel = {"id": 54, "ja_possui_ticket": False}
        ticket = {"id": 37, "status": "pendente", "incidente_ids": "53"}
        emissao_submetida = {
            "id": 709,
            "submetida_coordenador_em": datetime(2026, 10, 10),
        }
        emissao_em_elaboracao = {"id": 708, "submetida_coordenador_em": None}
        with (
            patch.object(coordenacao, "listar_fiscais_evento", return_value={}),
            patch.object(coordenacao, "listar_fiscais", return_value=[]),
            patch.object(coordenacao, "listar_tickets_evento", return_value=[ticket]),
            patch.object(
                coordenacao,
                "listar_emissoes_evento",
                return_value=[emissao_em_elaboracao, emissao_submetida],
            ) as listar_emissoes,
            patch.object(coordenacao, "listar_bsr_erb", return_value=[incidente_disponivel]) as listar_incidentes,
            patch.object(coordenacao, "listar_escalas_evento", return_value=[]),
            patch.object(coordenacao, "resumir_horas_escalas", return_value=[]),
            patch.object(coordenacao, "_img_b64", return_value=""),
            patch.object(coordenacao.templates, "TemplateResponse") as template,
        ):
            await coordenacao.get_coordenacao(self.request)
        listar_incidentes.assert_called_once_with(
            10, ocultar_vinculados=True, somente_submetidos=True
        )
        context = template.call_args.args[2]
        self.assertEqual(context["incidentes"], [incidente_disponivel])
        self.assertEqual(context["tickets"], [ticket])
        listar_emissoes.assert_called_once_with(10, ocultar_vinculadas=True)
        self.assertEqual(context["emissões"], [emissao_submetida])
        self.assertEqual(emissao_submetida["acompanhamento"], "Submetida à coordenação")

    async def test_busca_lista_cadastros_ao_abrir(self) -> None:
        import pandas as pd
        from app.routers import busca

        registros = pd.DataFrame([{"ID": "709"}, {"ID": "703"}])
        with (
            patch.object(busca, "_buscar_por_texto_livre", return_value=registros) as pesquisar,
            patch.object(busca, "carregar_imagens_ocorrencias", return_value={}),
            patch.object(busca, "_img_b64", return_value=""),
            patch.object(busca.templates, "TemplateResponse") as template,
        ):
            await busca.get_busca(self.request)
        pesquisar.assert_called_once_with(
            evento_id="10", termos="", fiscal_id=None, somente_submetidas=False
        )
        self.assertEqual(
            [item["id"] for item in template.call_args.args[2]["resultados"]],
            ["709", "703"],
        )

    async def test_busca_coordenador_inclui_emissoes_nao_submetidas(self) -> None:
        import pandas as pd
        from app.routers import busca

        self.request.session["tipo_usuario"] = "Coordenação"
        registros = pd.DataFrame(
            [{"ID": str(identificador)} for identificador in (708, 706, 705, 704, 703)]
        )
        with (
            patch.object(busca, "_buscar_por_texto_livre", return_value=registros) as pesquisar,
            patch.object(busca, "carregar_imagens_ocorrencias", return_value={}),
            patch.object(busca, "sugerir_busca_emissoes", return_value=[]) as sugerir,
            patch.object(busca, "_img_b64", return_value=""),
            patch.object(busca.templates, "TemplateResponse") as template,
        ):
            await busca.get_busca(self.request)
            await busca.get_sugestoes_busca(self.request, termo="703")
        pesquisar.assert_called_once_with(
            evento_id="10", termos="", fiscal_id=None, somente_submetidas=False
        )
        sugerir.assert_called_once_with(
            evento_id="10", termo="703", fiscal_id=None, somente_submetidas=False
        )
        self.assertEqual(len(template.call_args.args[2]["resultados"]), 5)

    async def test_busca_fiscal_pesquisa_todas_emissoes_do_evento(self) -> None:
        import pandas as pd
        from starlette.datastructures import FormData
        from app.routers import busca

        self.request._form = FormData({"termo": "Sinal"})
        with (
            patch.object(busca, "_buscar_por_texto_livre", return_value=pd.DataFrame()) as pesquisar,
            patch.object(busca, "carregar_imagens_ocorrencias", return_value={}),
            patch.object(busca, "sugerir_busca_emissoes", return_value=[]) as sugerir,
            patch.object(busca, "_img_b64", return_value=""),
            patch.object(busca.templates, "TemplateResponse"),
        ):
            await busca.post_busca(self.request)
            await busca.get_sugestoes_busca(self.request, termo="Sinal")
        pesquisar.assert_called_once_with(
            evento_id="10", termos="Sinal", fiscal_id=None, somente_submetidas=False
        )
        sugerir.assert_called_once_with(
            evento_id="10", termo="Sinal", fiscal_id=None, somente_submetidas=False
        )

    async def test_busca_exibe_cadastrador_na_lista_principal(self) -> None:
        import pandas as pd
        from app.routers import busca

        self.request.state.eventos = {}
        self.request.state.permissoes = {}
        registros = pd.DataFrame(
            [
                {"ID": "709", "Cadastrado por": "Fiscal teste"},
                {"ID": "703", "Cadastrado por": None},
            ]
        )
        with (
            patch.object(busca, "_buscar_por_texto_livre", return_value=registros),
            patch.object(busca, "carregar_imagens_ocorrencias", return_value={}),
            patch.object(busca, "_img_b64", return_value=""),
        ):
            response = await busca.get_busca(self.request)
        html = response.body.decode("utf-8")
        self.assertIn("<th>Cadastrado por</th>", html)
        self.assertIn("<td>Fiscal teste</td>", html)
        self.assertIn("<td>Não informado</td>", html)

    def test_busca_ordena_por_ultimo_cadastro(self) -> None:
        from app.services import postgres

        with (
            patch.object(postgres, "get_engine", return_value=MagicMock()),
            patch.object(postgres.pd, "read_sql", return_value=postgres.pd.DataFrame()) as consultar_sql,
        ):
            postgres._buscar_por_texto_livre(evento_id=10, termos="")
        sql = str(consultar_sql.call_args.args[0])
        self.assertIn("ORDER BY o.id DESC", sql)
        self.assertNotIn("ORDER BY o.data", sql)
        self.assertNotIn("LIMIT", sql)
        self.assertTrue(consultar_sql.call_args.kwargs["params"]["listar_tratadas"])

    async def test_menu_renderiza_modulo_monitoracao(self) -> None:
        from app.routers import menu

        self.request.state.permissoes = {
            "coordenacao": False,
            "teste_etiquetagem": False,
        }
        self.request.state.eventos = {}
        service = MagicMock()
        service.listar_por_evento.return_value = self.listar([self.record])
        with (
            patch.object(menu, "get_city_map_url", return_value=""),
            patch.object(menu, "listar_tickets_evento", return_value=[]),
            patch.object(menu, "_img_b64", return_value=""),
        ):
            response = await menu.get_menu(self.request, service)
        html = response.body.decode("utf-8")
        self.assertIn('href="/consultar"', html)
        self.assertIn("Tratar emissões pendentes", html)
        self.assertIn("1 pendência(s)", html)


if __name__ == "__main__":
    unittest.main()
