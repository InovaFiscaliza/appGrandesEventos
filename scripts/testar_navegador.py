"""Jornadas Playwright online com aplicacao e PostgreSQL isolados reais."""

import os
import socket
import threading
import unittest
from pathlib import Path

import httpx
import uvicorn
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    expect,
    sync_playwright,
)
from sqlalchemy import text

from scripts.ambiente_testes import RAIZ, validar_url_testes
from scripts.testar_persistencia import criar_dados_evento, imagem_sintetica


class NavegadorTests(unittest.TestCase):
    """Verifica cliques, JavaScript, imagens, layout e efeitos persistidos."""

    playwright: Playwright
    browser: Browser
    servidor: uvicorn.Server
    thread: threading.Thread
    endereco: str

    @classmethod
    def setUpClass(cls) -> None:
        validar_url_testes(os.environ.get("DATABASE_URL", ""))
        import main

        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        cls.addClassCleanup(listener.close)
        cls.endereco = f"http://127.0.0.1:{listener.getsockname()[1]}"
        cls.servidor = uvicorn.Server(uvicorn.Config(main.app, log_level="warning"))
        cls.thread = threading.Thread(
            target=cls.servidor.run,
            kwargs={"sockets": [listener]},
            daemon=True,
        )
        cls.thread.start()
        cls.addClassCleanup(cls.parar_servidor)
        response = httpx.get(f"{cls.endereco}/static/app.js", timeout=15)
        if response.status_code != 200:
            raise RuntimeError("Servidor de testes nao ficou pronto.")
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        cls.browser = cls.playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    @classmethod
    def parar_servidor(cls) -> None:
        """Encerra o servidor local de teste, inclusive quando uma jornada falha."""
        cls.servidor.should_exit = True
        cls.thread.join(timeout=10)
        if cls.thread.is_alive():
            raise RuntimeError("Servidor de testes nao encerrou.")

    def setUp(self) -> None:
        from app.services.db import get_engine

        self.engine = get_engine()
        self.dados = criar_dados_evento(self.engine)
        self.context: BrowserContext = self.browser.new_context(service_workers="block")
        self.addCleanup(self.context.close)
        self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.page: Page = self.context.new_page()
        self.page.set_default_timeout(10000)
        self.erros_js: list[str] = []
        self.page.on("pageerror", lambda erro: self.erros_js.append(str(erro)))
        self.artefatos = RAIZ / ".test-artifacts"
        self.artefatos.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        nome = self.id().split(".")[-1]
        try:
            self.page.screenshot(
                path=str(self.artefatos / f"{nome}.png"), full_page=True
            )
        finally:
            self.context.tracing.stop(path=str(self.artefatos / f"{nome}.zip"))

    def login(self) -> None:
        """Seleciona evento, fiscal e papel pelo formulario e API reais."""
        self.page.goto(self.endereco)
        self.page.locator("#evento_key").select_option(
            f"{self.dados['evento_nome']}|||{self.dados['evento_id']}"
        )
        self.page.locator("#fiscal_id").select_option(str(self.dados["fiscal"]))
        self.page.locator("#papel").select_option("Monitoração")
        self.page.locator("#senha").fill("teste")
        self.page.get_by_role("button", name="Entrar", exact=True).click()
        self.page.wait_for_url("**/menu")

    def preencher_e_salvar_emissao(self, largura: int, altura: int) -> None:
        """Cadastra uma emissao em elaboracao pelo formulario real."""
        self.page.set_viewport_size({"width": largura, "height": altura})
        self.login()
        self.page.goto(f"{self.endereco}/inserir")
        expect(self.page.locator("#form-inserir")).to_be_visible()
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), largura + 1
        )
        self.page.locator('[name="dia"]').fill("2026-10-11")
        self.page.locator('[name="hora"]').fill("12:30")
        self.page.locator('[name="local"]').fill("Arena")
        self.page.locator('[name="estacao_id"]').select_option("campo_analisador")
        self.page.locator('[name="freq"]').fill("433.925")
        self.page.locator('[name="larg"]').select_option("25 kHz")
        self.page.locator('[name="faixa"]').select_option("SLP")
        self.page.locator('[name="ident"]').select_option("Sinal de dados")
        self.page.locator('[name="interferente"]').select_option("Não")
        self.page.locator('[name="ute"]').select_option("Não")
        self.page.locator('[name="obs"]').fill("Cadastro pelo navegador")
        self.page.locator('[name="situacao"]').select_option("Pendente")
        with (
            self.page.expect_response(
                lambda response: "/inserir/salvar" in response.url
                and response.request.method == "POST"
            ) as resposta,
        ):
            self.page.locator('button[formaction="/inserir/salvar"]').click()
        self.assertEqual(resposta.value.status, 200)
        expect(self.page.locator('[name="obs"]')).to_have_value("")

    def salvar_emissao(self, largura: int, altura: int) -> None:
        """Preenche e aciona o botao de salvar; confere ausencia de submissao."""
        self.preencher_e_salvar_emissao(largura, altura)
        expect(self.page.locator(".flash-success").first).to_contain_text(
            "Emissão salva com sucesso"
        )
        with self.engine.connect() as connection:
            emissao = (
                connection.execute(
                    text("""
                SELECT situacao, criado_por_fiscal_id, submetida_coordenador_em
                FROM ocorrencias WHERE evento_id = :evento_id
            """),
                    {"evento_id": self.dados["evento_id"]},
                )
                .mappings()
                .one()
            )
        self.assertEqual(emissao["situacao"], "Pendente")
        self.assertEqual(emissao["criado_por_fiscal_id"], self.dados["fiscal"])
        self.assertIsNone(emissao["submetida_coordenador_em"])
        self.assertEqual(self.erros_js, [])

    def test_salvar_emissao_desktop(self) -> None:
        self.salvar_emissao(1280, 900)

    def test_salvar_emissao_celular(self) -> None:
        self.salvar_emissao(390, 844)

    def tratar_emissao_pendente(self, largura: int, altura: int) -> None:
        """Localiza, edita e submete um rascunho pelo atalho do menu."""
        self.preencher_e_salvar_emissao(largura, altura)
        self.page.goto(f"{self.endereco}/menu")
        expect(self.page.locator(".module-count")).to_have_text("1 pendência(s)")
        self.page.get_by_role("link", name="Tratar emissões pendentes").click()
        self.page.wait_for_url("**/consultar")
        linha = self.page.locator("#pendencias-tbody tr")
        expect(linha).to_have_count(1)
        linha.click()
        expect(self.page.locator("#form-consultar")).to_be_visible()
        self.page.locator("#f-estacao").select_option("campo_analisador")
        self.page.locator("#f-autz").select_option("Não")
        self.page.locator("#f-obs").fill("Rascunho revisado pelo fiscal")
        self.page.get_by_role("button", name="Salvar alterações", exact=True).click()
        expect(self.page.locator(".confirmacao-overlay")).to_be_visible()
        with self.page.expect_response(
            lambda response: "/consultar/salvar" in response.url
            and response.request.method == "POST"
        ):
            self.page.locator(".confirmacao-confirmar").click()
        expect(
            self.page.get_by_role("status").filter(has_text="Atualizado no banco")
        ).to_be_visible()
        self.page.goto(f"{self.endereco}/menu")
        expect(self.page.locator(".module-count")).to_have_text("1 pendência(s)")
        self.page.get_by_role("link", name="Tratar emissões pendentes").click()
        self.page.locator("#pendencias-tbody tr").click()
        expect(self.page.locator("#f-obs")).to_have_value(
            "Rascunho revisado pelo fiscal"
        )
        self.page.once("dialog", lambda dialog: dialog.accept())
        with self.page.expect_response(
            lambda response: "/consultar/submeter-ticket/" in response.url
            and response.request.method == "POST"
        ) as resposta:
            self.page.locator("#btn-submeter-ticket").click()
        self.assertEqual(resposta.value.status, 303)
        expect(self.page.locator("#msg-vazio")).to_be_visible()
        self.page.goto(f"{self.endereco}/menu")
        expect(self.page.locator(".module-count")).to_have_text("0 pendência(s)")
        expect(
            self.page.get_by_role("link", name="Tratar emissões pendentes")
        ).to_have_count(0)
        with self.engine.connect() as connection:
            emissao = (
                connection.execute(
                    text("""
                    SELECT observacoes, submetida_coordenador_em
                    FROM ocorrencias WHERE evento_id = :evento_id
                """),
                    {"evento_id": self.dados["evento_id"]},
                )
                .mappings()
                .one()
            )
        self.assertEqual(emissao["observacoes"], "Rascunho revisado pelo fiscal")
        self.assertIsNotNone(emissao["submetida_coordenador_em"])
        self.assertEqual(self.erros_js, [])

    def test_tratar_emissao_pendente_desktop(self) -> None:
        self.tratar_emissao_pendente(1280, 900)

    def test_tratar_emissao_pendente_celular(self) -> None:
        self.tratar_emissao_pendente(390, 844)

    def consultar_calendario_escalas(self, largura: int, altura: int) -> None:
        """Pagina meses e preserva o filtro do fiscal na agenda mensal."""
        with self.engine.begin() as connection:
            for fiscal, dia, inicio, fim in (
                ("fiscal", "2026-12-31", "22:15", "02:45"),
                ("outro", "2026-12-31", "08:00", "10:30"),
                ("fiscal", "2027-01-01", "09:15", "11:30"),
            ):
                connection.execute(
                    text("""
                        INSERT INTO escalas_trabalho (
                            evento_id, fiscal_id, data_trabalho, turno_inicio, turno_fim
                        ) VALUES (:evento, :fiscal, :dia, :inicio, :fim)
                    """),
                    {
                        "evento": self.dados["evento_id"],
                        "fiscal": self.dados[fiscal],
                        "dia": dia,
                        "inicio": inicio,
                        "fim": fim,
                    },
                )
        self.page.set_viewport_size({"width": largura, "height": altura})
        self.login()
        self.page.goto(f"{self.endereco}/escalas?mes=2026-12")
        titulo = self.page.locator("#escala-mes-titulo")
        turnos = self.page.locator(".escala-mes-turno")
        expect(titulo).to_have_text("Dezembro de 2026")
        expect(turnos).to_have_count(2)
        cor_fiscal = turnos.filter(has_text=self.dados["fiscal_nome"]).evaluate(
            "elemento => getComputedStyle(elemento).backgroundColor"
        )
        cor_outro = turnos.filter(has_text=self.dados["outro_nome"]).evaluate(
            "elemento => getComputedStyle(elemento).backgroundColor"
        )
        self.assertNotEqual(cor_fiscal, cor_outro)
        self.assertNotIn(cor_fiscal, ("rgba(0, 0, 0, 0)", "rgb(255, 255, 255)"))
        self.assertTrue(
            self.page.locator(".escala-mes-secao").evaluate(
                "elemento => elemento.getBoundingClientRect().top >= "
                "document.querySelector('[aria-label=\"Totais mensais de horas por fiscal\"]').getBoundingClientRect().bottom"
            )
        )
        self.page.locator("#filtro-visualizacao-escalas").select_option("proprias")
        self.page.get_by_role("button", name="Filtrar", exact=True).click()
        self.page.wait_for_url("**visualizacao=proprias")
        expect(turnos).to_have_count(1)
        expect(turnos).to_contain_text("22:15 às 02:45 (+1 dia)")
        self.assertEqual(
            turnos.evaluate("elemento => getComputedStyle(elemento).backgroundColor"),
            cor_fiscal,
        )
        self.page.get_by_role("link", name="Próximo mês", exact=True).click()
        expect(titulo).to_have_text("Janeiro de 2027")
        expect(turnos).to_have_count(1)
        expect(turnos).to_contain_text("09:15 às 11:30")
        self.assertEqual(
            turnos.evaluate("elemento => getComputedStyle(elemento).backgroundColor"),
            cor_fiscal,
        )
        expect(self.page.locator("#filtro-visualizacao-escalas")).to_have_value(
            "proprias"
        )
        self.page.get_by_role("link", name="Mês anterior", exact=True).click()
        expect(titulo).to_have_text("Dezembro de 2026")
        expect(turnos).to_have_count(1)
        self.page.locator("#escala-mes").fill("2027-02")
        self.page.get_by_role("button", name="Exibir mês", exact=True).click()
        expect(titulo).to_have_text("Fevereiro de 2027")
        expect(turnos).to_have_count(0)
        expect(
            self.page.get_by_text(
                "Nenhuma escala neste mês para o filtro selecionado.", exact=True
            )
        ).to_be_visible()
        self.page.get_by_role("link", name="Mês anterior", exact=True).click()
        expect(titulo).to_have_text("Janeiro de 2027")
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), largura + 1
        )
        self.page.locator(".escala-mes-secao").screenshot(
            path=str(self.artefatos / f"calendario-escalas-{largura}.png")
        )
        self.assertEqual(self.erros_js, [])

    def test_calendario_escalas_desktop(self) -> None:
        self.consultar_calendario_escalas(1280, 900)

    def test_calendario_escalas_celular(self) -> None:
        self.consultar_calendario_escalas(390, 844)

    def test_escalas_adjacentes_permanecem_visiveis(self) -> None:
        self.page.goto(self.endereco)
        self.page.locator("#evento_key").select_option(
            f"{self.dados['evento_nome']}|||{self.dados['evento_id']}"
        )
        self.page.locator("#fiscal_id").select_option(str(self.dados["coordenador"]))
        self.page.locator("#papel").select_option("Coordenação")
        self.page.locator("#senha").fill("teste")
        self.page.get_by_role("button", name="Entrar", exact=True).click()
        self.page.wait_for_url("**/menu")
        self.page.goto(f"{self.endereco}/coordenacao")
        self.page.get_by_role("tab", name="Escala").click()

        formulario = self.page.locator(".coordenacao-escala-form")
        formulario.locator('[name="fiscal_id"]').select_option(
            str(self.dados["fiscal"])
        )
        formulario.locator('[name="data_trabalho"]').fill("2026-10-13")
        formulario.locator('[name="turno_inicio"]').fill("10:00")
        formulario.locator('[name="turno_fim"]').fill("12:00")
        formulario.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("domcontentloaded")

        formulario = self.page.locator(".coordenacao-escala-form")
        formulario.locator('[name="fiscal_id"]').select_option(
            str(self.dados["fiscal"])
        )
        formulario.locator('[name="data_trabalho"]').fill("2026-10-13")
        formulario.locator('[name="turno_inicio"]').fill("12:00")
        formulario.locator('[name="turno_fim"]').fill("14:00")
        formulario.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("domcontentloaded")

        formulario = self.page.locator(".coordenacao-escala-form")
        formulario.locator('[name="fiscal_id"]').select_option(str(self.dados["outro"]))
        formulario.locator('[name="data_trabalho"]').fill("2026-10-13")
        formulario.locator('[name="turno_inicio"]').fill("10:00")
        formulario.locator('[name="turno_fim"]').fill("12:00")
        formulario.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("domcontentloaded")

        blocos = self.page.locator(".escala-jornada-bloco")
        expect(blocos).to_have_count(3)
        blocos_fiscal = blocos.filter(has_text=self.dados["fiscal_nome"])
        blocos_outro = blocos.filter(has_text=self.dados["outro_nome"])
        expect(blocos_fiscal).to_have_count(2)
        expect(blocos_outro).to_have_count(1)
        expect(blocos_fiscal.nth(0)).to_contain_text("10:00")
        expect(blocos_fiscal.nth(0)).to_contain_text("12:00")
        expect(blocos_fiscal.nth(1)).to_contain_text("12:00")
        expect(blocos_fiscal.nth(1)).to_contain_text("14:00")
        self.assertEqual(
            blocos_fiscal.nth(0).evaluate(
                "element => getComputedStyle(element).backgroundColor"
            ),
            blocos_fiscal.nth(1).evaluate(
                "element => getComputedStyle(element).backgroundColor"
            ),
        )
        self.assertNotEqual(
            blocos_fiscal.nth(0).evaluate(
                "element => getComputedStyle(element).backgroundColor"
            ),
            blocos_outro.nth(0).evaluate(
                "element => getComputedStyle(element).backgroundColor"
            ),
        )
        with self.engine.connect() as connection:
            quantidade = connection.execute(
                text("SELECT COUNT(*) FROM escalas_trabalho WHERE evento_id = :id"),
                {"id": self.dados["evento_id"]},
            ).scalar_one()
        self.assertEqual(quantidade, 3)
        self.assertEqual(self.erros_js, [])

    def test_excluir_foto_exige_confirmacao_e_preserva_outra(self) -> None:
        from app.services import postgres

        resultado = postgres.inserir_bsr_erb(
            evento_id=self.dados["evento_id"],
            tipo="ERB Fake",
            regiao="Arena",
            lat="-22.9",
            lon="-43.2",
            observacoes="Fotos pelo navegador",
            cadastrado_por=self.dados["fiscal_nome"],
            criado_por_fiscal_id=self.dados["fiscal"],
            imagens=[imagem_sintetica("primeira.png"), imagem_sintetica("segunda.png")],
        )
        self.assertFalse(resultado.startswith("ERRO"), resultado)
        with self.engine.connect() as connection:
            registro_id = connection.execute(
                text("SELECT id FROM bsr_erb WHERE evento_id = :id"),
                {"id": self.dados["evento_id"]},
            ).scalar_one()
        self.login()
        self.page.goto(f"{self.endereco}/bsr-erb?editar={registro_id}")
        fotos = self.page.locator("#form-bsr-erb .imagem-preview-item")
        expect(fotos).to_have_count(2)
        self.assertTrue(
            fotos.locator("img").evaluate_all(
                "imagens => imagens.every(imagem => imagem.complete && imagem.naturalWidth > 0)"
            )
        )
        fotos.first.locator("button").click()
        expect(self.page.locator(".confirmacao-overlay")).to_be_visible()
        self.page.locator(".confirmacao-cancelar").click()
        expect(fotos).to_have_count(2)
        with self.engine.connect() as connection:
            quantidade = connection.execute(
                text("SELECT COUNT(*) FROM bsr_erb_imagens WHERE bsr_erb_id = :id"),
                {"id": registro_id},
            ).scalar_one()
        self.assertEqual(quantidade, 2)
        fotos.first.locator("button").click()
        self.page.locator(".confirmacao-confirmar").click()
        expect(fotos).to_have_count(1)
        with self.engine.connect() as connection:
            quantidade = connection.execute(
                text("SELECT COUNT(*) FROM bsr_erb_imagens WHERE bsr_erb_id = :id"),
                {"id": registro_id},
            ).scalar_one()
            excluido_em = connection.execute(
                text("SELECT excluido_em FROM bsr_erb WHERE id = :id"),
                {"id": registro_id},
            ).scalar_one()
        self.assertEqual(quantidade, 1)
        self.assertIsNone(excluido_em)
        self.assertEqual(self.erros_js, [])


if __name__ == "__main__":
    unittest.main()
