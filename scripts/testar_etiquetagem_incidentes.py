"""Contratos HTTP da etiquetagem e das fotos de incidentes, sem banco real."""

import unittest
from unittest.mock import call, patch

from app.routers import bsr_erb, teste_etiquetagem
from scripts.testar_fluxos_operacionais import cliente_com_sessao


class EtiquetagemFrequenciasTests(unittest.TestCase):
    """Protege consulta de frequencia no cadastro, edicao e API."""

    def setUp(self) -> None:
        self.sessao = {
            "spreadsheet_id": 10,
            "fiscal_id": 7,
            "fiscal_nome": "Fiscal teste",
        }
        self.client = cliente_com_sessao(teste_etiquetagem.router, self.sessao)
        self.addCleanup(self.client.close)
        self.evento = patch.object(
            teste_etiquetagem,
            "obter_evento",
            return_value={
                "nome": "Evento teste",
                "cidade": "Rio de Janeiro",
                "uf": "RJ",
                "teste_etiquetagem": True,
            },
        ).start()
        self.consultar = patch.object(
            teste_etiquetagem,
            "consultar_equipamentos_frequencia",
            return_value={
                "referencias": [
                    {
                        "origem": "Ocorrência",
                        "detalhe": "Emissao 704, 433.925 MHz, 25 kHz, Arena, Fiscal outro",
                    }
                ],
            },
        ).start()
        self.faixa = patch.object(
            teste_etiquetagem, "faixa_numeracao_disponivel", return_value=True
        ).start()
        self.etiqueta = patch.object(
            teste_etiquetagem, "verificar_etiqueta_existente", return_value=None
        ).start()
        self.inserir = patch.object(
            teste_etiquetagem,
            "inserir_teste_etiquetagem",
            return_value="Equipamento cadastrado",
        ).start()
        self.editar = patch.object(
            teste_etiquetagem,
            "atualizar_teste_etiquetagem",
            return_value="Equipamento atualizado",
        ).start()
        self.addCleanup(patch.stopall)
        self.dados = {
            "entidade": "Equipe teste",
            "permissao": "permitido",
            "numero_etiqueta": "100",
            "numero_equipamentos": "2",
            "frequencia_mhz": "433,925",
            "passo": "⌂ 25 kHz",
        }

    def test_cadastro_consulta_central_banda_e_local_antes_de_salvar(self) -> None:
        def gravar(**kwargs: object) -> str:
            self.consultar.assert_called_once_with(
                evento_id=10,
                freq_digitada=433.925,
                largura_khz=25.0,
                localidade="Evento teste — Rio de Janeiro/RJ",
                excluir_id=None,
            )
            return "Equipamento cadastrado"

        self.inserir.side_effect = gravar
        response = self.client.post(
            "/teste_etiquetagem", data=self.dados, follow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.faixa.assert_called_once_with(
            evento_id=10, permissao="permitido", numero_inicial=100, numero_final=101
        )
        self.assertIn("Emissao 704", self.sessao["flash_success"])
        self.assertIn("25 kHz", self.sessao["flash_success"])

    def test_edicao_desconsidera_proprio_registro_e_nao_insere(self) -> None:
        response = self.client.post(
            "/teste_etiquetagem",
            data={**self.dados, "registro_id": "53"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/teste_etiquetagem?edit_id=53")
        self.assertEqual(self.consultar.call_args.kwargs["excluir_id"], "53")
        self.assertEqual(self.etiqueta.call_args.kwargs["excluir_id"], "53")
        self.editar.assert_called_once()
        self.inserir.assert_not_called()
        self.assertIn("Emissao 704", self.sessao["flash_success"])

    def test_todas_as_frequencias_listadas_sao_consultadas(self) -> None:
        response = self.client.post(
            "/teste_etiquetagem",
            data={
                **self.dados,
                "frequencia_mhz": "",
                "frequencias_selecionadas": [
                    "433,925 MHz ⌂ 25 kHz",
                    "434.000 MHz ⌂ 50 kHz",
                ],
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            self.consultar.call_args_list,
            [
                call(
                    evento_id=10,
                    freq_digitada=433.925,
                    largura_khz=25.0,
                    localidade="Evento teste — Rio de Janeiro/RJ",
                    excluir_id=None,
                ),
                call(
                    evento_id=10,
                    freq_digitada=434.0,
                    largura_khz=50.0,
                    localidade="Evento teste — Rio de Janeiro/RJ",
                    excluir_id=None,
                ),
            ],
        )
        self.inserir.assert_called_once()

    def test_api_repete_mesma_consulta_e_entrega_referencias(self) -> None:
        response = self.client.get(
            "/api/teste-etiquetagem/verificar-frequencia?frequencia=433.925&largura_khz=25&excluir_id=53"
        )
        self.assertEqual(response.status_code, 200)
        self.consultar.assert_called_once_with(
            evento_id=10,
            freq_digitada=433.925,
            largura_khz=25.0,
            localidade="Evento teste — Rio de Janeiro/RJ",
            excluir_id=53,
        )
        self.assertEqual(response.json(), self.consultar.return_value)

    def test_faixa_de_numeracao_invalida_preserva_formulario(self) -> None:
        self.faixa.return_value = False
        response = self.client.post("/teste_etiquetagem", data=self.dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn("fora das faixas", response.context["flash_error"])
        self.assertIn('value="Equipe teste"', response.text)
        self.inserir.assert_not_called()
        self.editar.assert_not_called()

    def test_etiqueta_duplicada_nao_grava(self) -> None:
        self.etiqueta.return_value = {
            "evento": "Evento teste",
            "data": "11/10/2026",
            "numero_inicial": 100,
            "numero_final": 101,
            "entidade": "Equipe anterior",
            "cpf_cnpj": "",
        }
        response = self.client.post("/teste_etiquetagem", data=self.dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Equipe anterior", response.context["flash_error"])
        self.inserir.assert_not_called()

    def test_modulo_desativado_bloqueia_formulario_e_api(self) -> None:
        self.evento.return_value["teste_etiquetagem"] = False
        response = self.client.post(
            "/teste_etiquetagem", data=self.dados, follow_redirects=False
        )
        self.assertEqual(response.headers["location"], "/menu")
        self.assertEqual(
            self.client.get(
                "/api/teste-etiquetagem/verificar-frequencia?frequencia=433.925"
            ).status_code,
            404,
        )
        self.consultar.assert_not_called()
        self.inserir.assert_not_called()

    def test_api_sem_evento_nao_consulta(self) -> None:
        self.sessao.clear()
        response = self.client.get(
            "/api/teste-etiquetagem/verificar-frequencia?frequencia=433.925"
        )
        self.assertEqual(response.status_code, 401)
        self.consultar.assert_not_called()


class FotosIncidentesHTTPTests(unittest.TestCase):
    """Protege alvo, autoria e contexto de ticket na exclusao de uma foto."""

    def setUp(self) -> None:
        self.sessao = {
            "spreadsheet_id": 10,
            "fiscal_id": 7,
            "fiscal_nome": "Fiscal teste",
        }
        self.client = cliente_com_sessao(bsr_erb.router, self.sessao)
        self.addCleanup(self.client.close)
        self.excluir_foto = patch.object(
            bsr_erb, "excluir_imagem_bsr_erb", return_value="Foto excluida"
        ).start()
        self.excluir_registro = patch.object(bsr_erb, "excluir_bsr_erb").start()
        self.addCleanup(patch.stopall)

    def test_excluir_foto_nao_exclui_incidente(self) -> None:
        response = self.client.post(
            "/bsr-erb/53/imagem/81/excluir", follow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.excluir_foto.assert_called_once_with(
            imagem_id=81,
            registro_id=53,
            evento_id=10,
            usuario_fiscal="Fiscal teste",
            criado_por_fiscal_id=7,
            eh_coordenador=False,
            ticket_id=None,
            fiscal_id=7,
        )
        self.excluir_registro.assert_not_called()
        self.assertEqual(response.headers["location"], "/bsr-erb?editar=53")

    def test_exclusao_pelo_ticket_preserva_contexto(self) -> None:
        response = self.client.post(
            "/bsr-erb/53/imagem/81/excluir?ticket_id=35", follow_redirects=False
        )
        self.assertEqual(self.excluir_foto.call_args.kwargs["ticket_id"], 35)
        self.assertEqual(
            response.headers["location"], "/bsr-erb?editar=53&ticket_id=35"
        )
        self.excluir_registro.assert_not_called()

    def test_negativa_do_servico_nao_exibe_sucesso(self) -> None:
        self.excluir_foto.return_value = "ERRO: Foto nao pertence ao registro"
        self.client.post("/bsr-erb/53/imagem/81/excluir", follow_redirects=False)
        self.assertIn("nao pertence", self.sessao["flash_error"])
        self.assertNotIn("flash_success", self.sessao)

    def test_sem_fiscal_nao_exclui_foto(self) -> None:
        del self.sessao["fiscal_id"]
        response = self.client.post(
            "/bsr-erb/53/imagem/81/excluir", follow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.excluir_foto.assert_not_called()


class IsolamentoBancoTests(unittest.TestCase):
    """Protege a recusa de bancos de trabalho na camada de integracao."""

    def test_executor_recusa_banco_real_remoto_ou_driver_diferente(self) -> None:
        from scripts.ambiente_testes import validar_url_testes

        aceita = "postgresql+psycopg://testes:testes@127.0.0.1:55432/appeventos_test_a1b2c3d4"
        self.assertEqual(
            validar_url_testes(aceita).database, "appeventos_test_a1b2c3d4"
        )
        for url in (
            "postgresql+psycopg://testes:testes@127.0.0.1/appeventos",
            "postgresql+psycopg://testes:testes@servidor/appeventos_test_a1b2c3d4",
            "postgresql+psycopg://testes:testes@localhost/appeventos_test_generico",
            "sqlite:///:memory:",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validar_url_testes(url)


if __name__ == "__main__":
    unittest.main()
