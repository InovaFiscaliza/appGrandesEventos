"""Testes de persistencia reais, restritos ao executor de integracao isolado."""

import os
import unittest
from io import BytesIO
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from scripts.ambiente_testes import (
    aplicar_migracoes_testes,
    preparar_banco,
    validar_url_testes,
)


def criar_dados_evento(engine: Engine) -> dict[str, Any]:
    """Cria evento, equipe, estacao e faixas sinteticas para cada jornada."""
    sufixo = uuid4().hex[:8]
    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO unidades_executantes (sigla, nome) VALUES ('RJ', 'Unidade teste')
            ON CONFLICT DO NOTHING
        """))
        evento_nome = f"Evento sintetico {sufixo}"
        evento_id = connection.execute(
            text("""
            INSERT INTO eventos (nome, cidade, uf)
            VALUES (:nome, 'Rio de Janeiro', 'RJ') RETURNING id
        """),
            {"nome": evento_nome},
        ).scalar_one()
        fiscais: dict[str, Any] = {}
        for chave, papel in (
            ("coordenador", "Coordenação"),
            ("fiscal", "Monitoração"),
            ("outro", "Monitoração"),
        ):
            nome = f"{chave.capitalize()} sintetico {sufixo}"
            fiscal_id = connection.execute(
                text("""
                INSERT INTO fiscais (nome, local_anatel, papeis)
                VALUES (:nome, 'RJ', CAST(:papeis AS TEXT[])) RETURNING id
            """),
                {"nome": nome, "papeis": [papel]},
            ).scalar_one()
            connection.execute(
                text("""
                INSERT INTO eventos_fiscais (evento_id, fiscal_id, papeis)
                VALUES (:evento_id, :fiscal_id, CAST(:papeis AS TEXT[]))
            """),
                {"evento_id": evento_id, "fiscal_id": fiscal_id, "papeis": [papel]},
            )
            fiscais[chave] = fiscal_id
            fiscais[f"{chave}_nome"] = nome
        connection.execute(
            text("""
            INSERT INTO eventos_coordenadores (evento_id, fiscal_id) VALUES (:evento_id, :fiscal_id)
        """),
            {"evento_id": evento_id, "fiscal_id": fiscais["coordenador"]},
        )
        connection.execute(
            text("""
            INSERT INTO faixas_numeracao_etiqueta (evento_id, permissao, numero_inicial, numero_final)
            VALUES (:evento_id, 'permitido', 100, 999), (:evento_id, 'todos', 1000, 1999)
        """),
            {"evento_id": evento_id},
        )
        estacao_id = connection.execute(
            text("""
            INSERT INTO estacoes (evento_id, nome, modelo_equipamento, local, cidade)
            VALUES (:evento_id, 'Estacao teste', 'RFeye', 'Arena', 'Rio de Janeiro') RETURNING id
        """),
            {"evento_id": evento_id},
        ).scalar_one()
    return {
        "evento_id": evento_id,
        "evento_nome": evento_nome,
        "estacao_id": estacao_id,
        **fiscais,
    }


def imagem_sintetica(nome: str = "foto.png", formato: str = "PNG") -> dict[str, Any]:
    """Gera uma imagem pequena real, sem depender de arquivos ou dados do usuario."""
    arquivo = BytesIO()
    Image.new("RGB", (8, 8), "red").save(arquivo, format=formato)
    conteudo = arquivo.getvalue()
    return {
        "nome_arquivo": nome,
        "tipo_mime": "image/png" if formato == "PNG" else "image/jpeg",
        "tamanho_bytes": len(conteudo),
        "conteudo": conteudo,
    }


class PersistenciaTests(unittest.TestCase):
    """Valida dados sinteticos com os servicos e PostgreSQL reais."""

    def setUp(self) -> None:
        validar_url_testes(os.environ.get("DATABASE_URL", ""))
        from app.services.db import get_engine
        import main

        self.engine = get_engine()
        self.dados = criar_dados_evento(self.engine)
        self.evento_id = self.dados["evento_id"]
        self.client = TestClient(main.app)
        self.addCleanup(self.client.close)
        self.login("fiscal")

    def login(self, perfil: str) -> None:
        """Autentica via formulario real com usuario e papel do evento sintetico."""
        self.client.cookies.clear()
        response = self.client.post(
            "/",
            data={
                "evento_key": f"{self.dados['evento_nome']}|||{self.evento_id}",
                "fiscal_id": str(self.dados[perfil]),
                "senha": "teste",
                "papel": "Coordenação" if perfil == "coordenador" else "Monitoração",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/menu")

    def cadastrar_emissao(self, local: str = "Arena") -> int:
        """Salva pela rota real e retorna o ID persistido no evento de teste."""
        response = self.client.post(
            "/inserir/salvar",
            data={
                "dia": "2026-10-11",
                "hora": "12:30",
                "local": local,
                "freq": "433,925",
                "larg": "25 kHz",
                "faixa": "SLP",
                "ident": "Sinal de dados",
                "estacao_id": "campo_analisador",
                "interferente": "Não",
                "ute": "Não",
                "obs": "Jornada sintetica",
                "situacao": "Pendente",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        with self.engine.connect() as connection:
            return connection.execute(
                text(
                    "SELECT id FROM ocorrencias WHERE evento_id = :evento_id ORDER BY id DESC LIMIT 1"
                ),
                {"evento_id": self.evento_id},
            ).scalar_one()

    def esclarecer_emissao(self, ocorrencia_id: int, ticket_id: int) -> None:
        """Preenche pela edição real os campos pendentes da emissão atribuída."""
        resposta = self.client.post(
            f"/consultar/salvar?popup=1&emissao_id={ocorrencia_id}&ticket_id={ticket_id}",
            data={
                "fonte": "FISCAL",
                "id_val": str(ocorrencia_id),
                "ident_edit": "Sinal de dados",
                "autz_edit": "Não licenciável",
                "ute_check": "Sim",
                "proc_edit": "SEI-12345",
                "ato_ute_edit": "Ato 678",
                "obs_edit": "Emissão esclarecida pelo fiscal",
                "cient_edit": "Responsável local",
                "interf_edit": "Não",
                "situ_edit": "Pendente",
                "estacao_id": str(self.dados["estacao_id"]),
            },
            follow_redirects=False,
        )
        self.assertEqual(resposta.status_code, 303)

    def test_salvar_emissao_persiste_e_aparece_nas_pendencias(self) -> None:
        ocorrencia_id = self.cadastrar_emissao()
        with self.engine.connect() as connection:
            registro = (
                connection.execute(
                    text("""
                SELECT situacao, fiscal, criado_por_fiscal_id, frequencia_mhz, submetida_coordenador_em
                FROM ocorrencias WHERE id = :id
            """),
                    {"id": ocorrencia_id},
                )
                .mappings()
                .one()
            )
        self.assertEqual(registro["situacao"], "Pendente")
        self.assertEqual(registro["fiscal"], self.dados["fiscal_nome"])
        self.assertEqual(registro["criado_por_fiscal_id"], self.dados["fiscal"])
        self.assertAlmostEqual(float(registro["frequencia_mhz"]), 433.925)
        self.assertIsNone(registro["submetida_coordenador_em"])
        response = self.client.get("/api/pendencias")
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(ocorrencia_id), response.text)
        self.assertIn(self.dados["fiscal_nome"], response.text)

    def test_edicao_emissao_por_ticket_salva_e_recarrega_todos_os_campos(self) -> None:
        from app.services import postgres

        ocorrencia_id = self.cadastrar_emissao()
        self.client.post(
            f"/consultar/submeter-ticket/{ocorrencia_id}", follow_redirects=False
        )
        self.login("coordenador")
        ticket_id = postgres.salvar_ticket_evento(
            evento_id=self.evento_id,
            ocorrencia_ids=[ocorrencia_id],
            fiscal_ids=[self.dados["fiscal"]],
        )
        self.login("fiscal")

        self.esclarecer_emissao(ocorrencia_id, ticket_id)

        with self.engine.connect() as connection:
            registro = (
                connection.execute(
                    text("""
                    SELECT identificacao, autorizado, ute, processo_sei_ute,
                           ato_ute, observacoes, alguem_ciente, interferente,
                           situacao, estacao_id, origem_captura
                    FROM ocorrencias WHERE id = :id
                """),
                    {"id": ocorrencia_id},
                )
                .mappings()
                .one()
            )
        self.assertEqual(
            dict(registro),
            {
                "identificacao": "Sinal de dados",
                "autorizado": "Não licenciável",
                "ute": True,
                "processo_sei_ute": "SEI-12345",
                "ato_ute": "Ato 678",
                "observacoes": "Emissão esclarecida pelo fiscal",
                "alguem_ciente": "Responsável local",
                "interferente": "Não",
                "situacao": "Pendente",
                "estacao_id": self.dados["estacao_id"],
                "origem_captura": None,
            },
        )

        resposta = self.client.get(
            f"/api/pendencias?popup=1&emissao_id={ocorrencia_id}&ticket_id={ticket_id}"
        )
        self.assertEqual(resposta.status_code, 200)
        emissao = resposta.json()[0]
        self.assertEqual(emissao["estacao_id"], str(self.dados["estacao_id"]))
        self.assertEqual(emissao["autorizado"], "Não licenciável")
        self.assertEqual(emissao["interferente"], "Não")
        self.assertEqual(emissao["processo_sei"], "SEI-12345")

    def test_edicao_incidente_por_ticket_salva_campos_audita_e_mantem_popup(
        self,
    ) -> None:
        from app.services import postgres

        with self.engine.begin() as connection:
            incidente_id = connection.execute(
                text("""
                    INSERT INTO bsr_erb (
                        evento_id, tipo, regiao, latitude, longitude, observacoes,
                        criado_por_fiscal_id, submetido_coordenador_em
                    ) VALUES (
                        :evento_id, 'Bloqueador de sinal (BSR)', 'Local original',
                        -22.9, -43.2, 'Observação original', :fiscal_id, now()
                    ) RETURNING id
                """),
                {
                    "evento_id": self.evento_id,
                    "fiscal_id": self.dados["fiscal"],
                },
            ).scalar_one()
        ticket_id = postgres.salvar_ticket_evento(
            evento_id=self.evento_id,
            ocorrencia_ids=[],
            incidente_ids=[incidente_id],
            fiscal_ids=[self.dados["fiscal"]],
        )

        pagina = self.client.get(
            f"/bsr-erb?editar={incidente_id}&ticket_id={ticket_id}&popup=1"
        )
        self.assertEqual(pagina.status_code, 200)
        self.assertIn(f'action="/bsr-erb/{incidente_id}/editar?popup=1"', pagina.text)

        resposta = self.client.post(
            f"/bsr-erb/{incidente_id}/editar?popup=1",
            data={
                "ticket_id": str(ticket_id),
                "tipo": "ERB Fake",
                "regiao": "Local atualizado",
                "lat": "-23.1",
                "lon": "-44.3",
                "observacoes": "Providência do fiscal",
                "situacao": "Concluída Pelo Fiscal",
                "fiscais_participantes": str(self.dados["outro"]),
            },
            follow_redirects=False,
        )
        self.assertEqual(resposta.status_code, 303)
        pagina_retorno = self.client.get(resposta.headers["location"])
        self.assertIn("atualizado com sucesso.", pagina_retorno.text)
        self.assertEqual(
            resposta.headers["location"],
            f"/bsr-erb?editar={incidente_id}&ticket_id={ticket_id}&popup=1",
        )

        with self.engine.connect() as connection:
            registro = (
                connection.execute(
                    text("""
                    SELECT tipo, regiao, latitude, longitude, observacoes,
                           situacao, concluida_por
                    FROM bsr_erb WHERE id = :id
                """),
                    {"id": incidente_id},
                )
                .mappings()
                .one()
            )
            participantes = (
                connection.execute(
                    text("""
                    SELECT fiscal_id FROM incidente_fiscais
                    WHERE incidente_id = :id
                """),
                    {"id": incidente_id},
                )
                .scalars()
                .all()
            )
            campos_auditados = (
                connection.execute(
                    text("""
                    SELECT campo FROM auditoria_bsr_erb WHERE bsr_erb_id = :id
                """),
                    {"id": incidente_id},
                )
                .scalars()
                .all()
            )

        self.assertEqual(
            {
                chave: registro[chave]
                for chave in dict(registro)
                if chave not in {"latitude", "longitude"}
            },
            {
                "tipo": "ERB Fake",
                "regiao": "Local atualizado",
                "observacoes": "Providência do fiscal",
                "situacao": "Concluída Pelo Fiscal",
                "concluida_por": "Fiscal",
            },
        )
        self.assertAlmostEqual(float(registro["latitude"]), -23.1)
        self.assertAlmostEqual(float(registro["longitude"]), -44.3)
        self.assertEqual(participantes, [self.dados["outro"]])
        self.assertTrue(
            {
                "Tipo",
                "Local",
                "Latitude",
                "Longitude",
                "Observações",
                "Situação",
                "Fiscais participantes",
            }.issubset(campos_auditados)
        )

    def test_coordenador_cadastrador_edita_propria_emissao_pendente(self) -> None:
        self.login("coordenador")
        propria_id = self.cadastrar_emissao()
        self.login("fiscal")
        outra_id = self.cadastrar_emissao()
        self.login("coordenador")

        response = self.client.get("/api/pendencias")

        self.assertEqual(response.status_code, 200)
        registros = {int(item["id"]): item for item in response.json()}
        self.assertTrue(registros[propria_id]["pode_editar"])
        self.assertFalse(registros[outra_id]["pode_editar"])

    def test_jornada_emissao_ticket_devolucao_conclusao_e_auditoria(self) -> None:
        ocorrencia_id = self.cadastrar_emissao()
        self.client.post(
            f"/consultar/submeter-ticket/{ocorrencia_id}", follow_redirects=False
        )
        self.login("coordenador")
        response = self.client.post(
            "/coordenacao/ticket",
            data={
                "ocorrencia_ids": str(ocorrencia_id),
                "fiscais": str(self.dados["fiscal"]),
                "prioridade": "normal",
                "observacoes": "Jornada completa de teste",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        with self.engine.connect() as connection:
            ticket_id = connection.execute(
                text("SELECT id FROM tickets WHERE evento_id = :evento_id"),
                {"evento_id": self.evento_id},
            ).scalar_one()
        self.login("fiscal")
        self.esclarecer_emissao(ocorrencia_id, ticket_id)
        self.client.post(
            f"/tratamento-tickets/{ticket_id}",
            data={
                "status": "concluido_pelos_fiscais",
                "providencias": "Inspecao concluida",
            },
            follow_redirects=False,
        )
        self.login("coordenador")
        self.client.post(
            f"/coordenacao/ticket/{ticket_id}/status",
            data={
                "status": "pendente",
                "motivo_devolucao": "Rever antena secundaria",
            },
            follow_redirects=False,
        )
        self.login("fiscal")
        tela = self.client.get("/tratamento-tickets")
        self.assertIn("Rever antena secundaria", tela.text)
        self.assertIn("fa-exclamation-circle", tela.text)
        self.client.post(
            f"/tratamento-tickets/{ticket_id}",
            data={
                "status": "concluido_pelos_fiscais",
                "providencias": "Antena secundaria verificada",
            },
            follow_redirects=False,
        )
        self.login("coordenador")
        self.client.post(
            f"/coordenacao/ticket/{ticket_id}/status",
            data={
                "status": "concluido_pelo_coordenador",
            },
            follow_redirects=False,
        )
        with self.engine.connect() as connection:
            ticket = connection.execute(
                text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
            ).scalar_one()
            emissao = connection.execute(
                text("SELECT situacao, concluida_por FROM ocorrencias WHERE id = :id"),
                {"id": ocorrencia_id},
            ).one()
        self.assertEqual(ticket, "concluido_pelo_coordenador")
        self.assertEqual(tuple(emissao), ("Concluída Pelo Coordenador", "Coordenador"))
        auditoria = self.client.get("/auditoria?origem=Coordenação")
        self.assertEqual(auditoria.status_code, 200)
        self.assertIn("Rever antena secundaria", auditoria.text)
        self.assertIn(self.dados["coordenador_nome"], auditoria.text)

    def test_conclusao_exige_todas_emissoes_e_incidentes_e_audita(self) -> None:
        from app.services import postgres

        emissoes = [self.cadastrar_emissao(), self.cadastrar_emissao()]
        for ocorrencia_id in emissoes:
            self.client.post(
                f"/consultar/submeter-ticket/{ocorrencia_id}", follow_redirects=False
            )
        with self.engine.begin() as conexao:
            incidentes = [
                conexao.execute(
                    text("""
                        INSERT INTO bsr_erb (
                            evento_id, tipo, regiao, criado_por_fiscal_id,
                            submetido_coordenador_em
                        ) VALUES (
                            :evento_id, 'Bloqueador de sinal (BSR)', 'Arena', :fiscal_id, now()
                        ) RETURNING id
                    """),
                    {"evento_id": self.evento_id, "fiscal_id": self.dados["fiscal"]},
                ).scalar_one()
                for _ in range(2)
            ]
        ticket_id = postgres.salvar_ticket_evento(
            self.evento_id,
            emissoes,
            incidente_ids=incidentes,
            fiscal_ids=[self.dados["fiscal"]],
        )

        def concluir() -> None:
            resposta = self.client.post(
                f"/tratamento-tickets/{ticket_id}",
                data={
                    "status": "concluido_pelos_fiscais",
                    "providencias": "Verificação realizada",
                },
                follow_redirects=False,
            )
            self.assertEqual(resposta.status_code, 303)

        concluir()
        tela = self.client.get("/tratamento-tickets")
        for ocorrencia_id in emissoes:
            self.assertIn(f"Emissão #{ocorrencia_id}", tela.text)
        for incidente_id in incidentes:
            self.assertIn(f"Incidente #{incidente_id}", tela.text)
        with self.engine.connect() as conexao:
            self.assertEqual(
                conexao.execute(
                    text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
                ).scalar_one(),
                "pendente",
            )
            self.assertEqual(
                conexao.execute(
                    text(
                        "SELECT COUNT(*) FROM auditoria_bsr_erb WHERE evento_id = :id"
                    ),
                    {"id": self.evento_id},
                ).scalar_one(),
                0,
            )

        for ocorrencia_id in emissoes:
            self.esclarecer_emissao(ocorrencia_id, ticket_id)
        for incidente_id in incidentes:
            resposta = self.client.post(
                f"/bsr-erb/{incidente_id}/editar",
                data={
                    "ticket_id": str(ticket_id),
                    "tipo": "Bloqueador de sinal (BSR)",
                    "regiao": "Arena",
                    "observacoes": "Incidente esclarecido pelo fiscal",
                    "situacao": "Pendente",
                    "fiscais_participantes": str(self.dados["fiscal"]),
                },
                follow_redirects=False,
            )
            self.assertEqual(resposta.status_code, 303)
        concluir()
        with self.engine.connect() as conexao:
            self.assertEqual(
                conexao.execute(
                    text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
                ).scalar_one(),
                "concluido_pelos_fiscais",
            )
            for tabela in ("ocorrencias", "bsr_erb"):
                registros = conexao.execute(
                    text(
                        f"SELECT situacao, concluida_por FROM {tabela} WHERE evento_id = :id"
                    ),
                    {"id": self.evento_id},
                ).all()
                self.assertEqual(
                    [tuple(item) for item in registros],
                    [
                        ("Concluída Pelo Fiscal", "Fiscal"),
                        ("Concluída Pelo Fiscal", "Fiscal"),
                    ],
                )
        auditoria = self.client.get("/auditoria?origem=Incidentes")
        self.assertIn("Concluída Pelo Fiscal", auditoria.text)
        self.assertIn(self.dados["fiscal_nome"], auditoria.text)

    def test_ticket_duplicado_e_evento_incorreto_nao_alteram_vinculos(self) -> None:
        from app.services import postgres

        ocorrencia_id = self.cadastrar_emissao()
        ticket_id = postgres.salvar_ticket_evento(
            self.evento_id, [ocorrencia_id], fiscal_ids=[self.dados["fiscal"]]
        )
        with self.assertRaises(ValueError):
            postgres.salvar_ticket_evento(self.evento_id, [ocorrencia_id])
        with self.assertRaises(ValueError):
            postgres.atualizar_ticket_evento(
                ticket_id, self.evento_id + 100000, "pendente"
            )
        with self.engine.connect() as connection:
            quantidade = connection.execute(
                text("SELECT COUNT(*) FROM tickets WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
        self.assertEqual(quantidade, 1)

    def test_sobreposicao_considera_banda_local_e_exclusao_do_proprio_id(self) -> None:
        from app.services import postgres

        ocorrencia_id = self.cadastrar_emissao()
        for frequencia, local, excluir_id, esperado in (
            (433.940, " arena ", None, True),
            (434.000, "Arena", None, False),
            (433.925, "Outro local", None, False),
            (433.925, "Arena", ocorrencia_id, False),
        ):
            with self.subTest(
                frequencia=frequencia, local=local, excluir_id=excluir_id
            ):
                conflitos = postgres.consultar_conflitos_frequencia(
                    evento_id=self.evento_id,
                    freq_digitada=frequencia,
                    largura_khz=25,
                    localidade=local,
                    excluir_id=excluir_id,
                )
                self.assertEqual(
                    any(
                        item["id"] == ocorrencia_id and item["origem"] == "Ocorrência"
                        for item in conflitos
                    ),
                    esperado,
                )

    def test_excluir_uma_foto_preserva_incidente_outra_foto_e_auditoria(self) -> None:
        from app.services import postgres

        resultado = postgres.inserir_bsr_erb(
            evento_id=self.evento_id,
            tipo="ERB Fake",
            regiao="Arena",
            lat="-22.9",
            lon="-43.2",
            observacoes="Incidente sintetico",
            cadastrado_por=self.dados["fiscal_nome"],
            criado_por_fiscal_id=self.dados["fiscal"],
            imagens=[
                imagem_sintetica("foto.png"),
                imagem_sintetica("foto.jpg", "JPEG"),
            ],
        )
        self.assertFalse(resultado.startswith("ERRO"), resultado)
        with self.engine.connect() as connection:
            registro_id = connection.execute(
                text("SELECT id FROM bsr_erb WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
            fotos = (
                connection.execute(
                    text(
                        "SELECT id, nome_arquivo FROM bsr_erb_imagens WHERE bsr_erb_id = :id ORDER BY id"
                    ),
                    {"id": registro_id},
                )
                .mappings()
                .all()
            )
        self.assertEqual(len(fotos), 2)
        prefixo = self.dados["evento_nome"].replace(" ", "_")
        self.assertRegex(
            fotos[0]["nome_arquivo"],
            rf"^{prefixo}_ERB_Fake_ID_{registro_id}_\d{{8}}_\d{{6}}_01\.png$",
        )
        self.assertRegex(
            fotos[1]["nome_arquivo"],
            rf"^{prefixo}_ERB_Fake_ID_{registro_id}_\d{{8}}_\d{{6}}_02\.jpg$",
        )
        self.assertIn("ERB_Fake", fotos[0]["nome_arquivo"])
        self.client.post(
            f"/bsr-erb/{registro_id}/imagem/{fotos[0]['id']}/excluir",
            follow_redirects=False,
        )
        with self.engine.connect() as connection:
            restante = (
                connection.execute(
                    text("SELECT id FROM bsr_erb_imagens WHERE bsr_erb_id = :id"),
                    {"id": registro_id},
                )
                .scalars()
                .all()
            )
            excluido_em = connection.execute(
                text("SELECT excluido_em FROM bsr_erb WHERE id = :id"),
                {"id": registro_id},
            ).scalar_one()
        self.assertEqual(restante, [fotos[1]["id"]])
        self.assertIsNone(excluido_em)
        auditoria = self.client.get("/auditoria?origem=Incidentes")
        self.assertEqual(auditoria.status_code, 200)
        self.assertIn("Imagem excluída", auditoria.text)
        self.assertIn(fotos[0]["nome_arquivo"], auditoria.text)

    def test_tabelas_essenciais_e_colunas_de_migracoes_existem(self) -> None:
        with self.engine.connect() as connection:
            tabelas = set(connection.execute(text("""
                SELECT tablename FROM pg_tables WHERE schemaname = current_schema()
            """)).scalars())
            for nome in (
                "ocorrencias",
                "tickets",
                "bsr_erb",
                "testes_etiquetagem",
                "auditoria_ocorrencias",
            ):
                self.assertIn(nome, tabelas)
            connection.execute(
                text("SELECT submetida_coordenador_em FROM ocorrencias LIMIT 0")
            )
            connection.execute(
                text("SELECT submetido_coordenador_em FROM bsr_erb LIMIT 0")
            )

    def test_migracoes_sobre_legados_preservam_frequencia_e_recuperam_autoria(
        self,
    ) -> None:
        url = preparar_banco(os.environ["TEST_DATABASE_URL"], migrar=False)
        engine_legado = create_engine(url, hide_parameters=True)
        self.addCleanup(engine_legado.dispose)
        dados = criar_dados_evento(engine_legado)
        with engine_legado.begin() as connection:
            etiqueta_id = connection.execute(
                text("""
                    INSERT INTO testes_etiquetagem (
                        evento_id, licenca, perfil, entidade, local,
                        permissao, tipo_equipamento, numero_etiqueta,
                        numero_equipamentos, observacoes
                    ) VALUES (
                        :evento_id, 'radiacao_restrita', 'pj', 'Equipe legada',
                        'Arena', 'permitido', 'Radio', '150', 3,
                        'Etiqueta legada preservada'
                    ) RETURNING id
                """),
                {"evento_id": dados["evento_id"]},
            ).scalar_one()
            ocorrencia_id = connection.execute(
                text("""
                INSERT INTO ocorrencias (evento_id, fiscal, frequencia_mhz, observacoes)
                VALUES (:evento_id, :fiscal, 433.925, 'Registro legado preservado') RETURNING id
            """),
                {"evento_id": dados["evento_id"], "fiscal": dados["fiscal_nome"]},
            ).scalar_one()
            ticket_id = connection.execute(
                text("""
                INSERT INTO tickets (evento_id, ocorrencia_id) VALUES (:evento_id, :ocorrencia_id)
                RETURNING id
            """),
                {"evento_id": dados["evento_id"], "ocorrencia_id": ocorrencia_id},
            ).scalar_one()
            connection.execute(
                text("""
                INSERT INTO ticket_ocorrencias (ticket_id, ocorrencia_id) VALUES (:ticket_id, :ocorrencia_id)
            """),
                {"ticket_id": ticket_id, "ocorrencia_id": ocorrencia_id},
            )
        aplicar_migracoes_testes(engine_legado)
        with engine_legado.connect() as connection:
            registro = (
                connection.execute(
                    text("""
                SELECT frequencia_mhz, observacoes, criado_por_fiscal_id, submetida_coordenador_em
                FROM ocorrencias WHERE id = :id
            """),
                    {"id": ocorrencia_id},
                )
                .mappings()
                .one()
            )
        self.assertAlmostEqual(float(registro["frequencia_mhz"]), 433.925)
        self.assertEqual(registro["observacoes"], "Registro legado preservado")
        self.assertEqual(registro["criado_por_fiscal_id"], dados["fiscal"])
        self.assertIsNotNone(registro["submetida_coordenador_em"])
        aplicar_migracoes_testes(engine_legado)
        with engine_legado.begin() as connection:
            etiqueta = (
                connection.execute(
                    text("""
                    SELECT numero_etiqueta, numero_equipamentos, observacoes
                    FROM testes_etiquetagem WHERE id = :id
                """),
                    {"id": etiqueta_id},
                )
                .mappings()
                .one()
            )
            self.assertEqual(etiqueta["numero_etiqueta"], "150")
            self.assertEqual(etiqueta["numero_equipamentos"], 3)
            self.assertEqual(etiqueta["observacoes"], "Etiqueta legada preservada")
            connection.execute(
                text("""
                    INSERT INTO testes_etiquetagem (
                        evento_id, licenca, perfil, entidade, local,
                        permissao, tipo_equipamento, numero_etiqueta
                    ) VALUES (
                        :evento_id, 'radiacao_restrita', 'pj', 'Outra categoria',
                        'Arena', 'todos', 'Radio', '150'
                    )
                """),
                {"evento_id": dados["evento_id"]},
            )

    def test_etiquetagem_cadastra_edita_com_conflito_sem_bloquear_e_audita_foto(
        self,
    ) -> None:
        local = f"{self.dados['evento_nome']} — Rio de Janeiro/RJ"
        self.cadastrar_emissao(local=local)
        dados = {
            "licenca": "radiacao_restrita",
            "perfil": "pj",
            "entidade": "Equipe sintetica",
            "tipo_equipamento": "Radio",
            "permissao": "permitido",
            "numero_etiqueta": "150",
            "numero_equipamentos": "1",
            "frequencias_selecionadas": ["433,925 MHz ⌂ 25 kHz"],
        }
        imagem = imagem_sintetica()
        response = self.client.post(
            "/teste_etiquetagem",
            data=dados,
            files={
                "imagens": (
                    imagem["nome_arquivo"],
                    imagem["conteudo"],
                    imagem["tipo_mime"],
                ),
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        with self.engine.connect() as connection:
            teste = (
                connection.execute(
                    text(
                        "SELECT id, frequencias_selecionadas FROM testes_etiquetagem WHERE evento_id = :id"
                    ),
                    {"id": self.evento_id},
                )
                .mappings()
                .one()
            )
        tela = self.client.get(response.headers["location"])
        self.assertIn("AVISO", tela.text)
        self.assertIn("433,925", tela.text)
        self.assertEqual(teste["frequencias_selecionadas"], ["433,925 MHz ⌂ 25 kHz"])
        response = self.client.post(
            "/teste_etiquetagem",
            data={
                **dados,
                "registro_id": str(teste["id"]),
                "frequencias_selecionadas": ["433,930 MHz ⌂ 25 kHz"],
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        with self.engine.connect() as connection:
            registros = (
                connection.execute(
                    text(
                        "SELECT frequencias_selecionadas FROM testes_etiquetagem WHERE evento_id = :id"
                    ),
                    {"id": self.evento_id},
                )
                .scalars()
                .all()
            )
        self.assertEqual(registros, [["433,930 MHz ⌂ 25 kHz"]])
        auditoria = self.client.get("/auditoria?origem=Teste%20de%20etiquetagem")
        self.assertEqual(auditoria.status_code, 200)
        self.assertIn("Imagem anexada", auditoria.text)

    def test_etiquetas_separam_categorias_e_bloqueiam_sobreposicao(self) -> None:
        from app.services import postgres

        postgres.criar_faixa_numeracao_etiqueta(
            evento_id=self.evento_id,
            permissao="todos",
            numero_inicial=100,
            numero_final=999,
        )
        dados = {
            "licenca": "radiacao_restrita",
            "perfil": "pj",
            "entidade": f"Equipe categorias {self.evento_id}",
            "tipo_equipamento": "Radio",
            "numero_etiqueta": "150",
            "numero_equipamentos": "3",
        }
        registros = {}
        for categoria in ("permitido", "todos"):
            with self.subTest(categoria=categoria):
                imagem = imagem_sintetica()
                response = self.client.post(
                    "/teste_etiquetagem",
                    data={**dados, "permissao": categoria},
                    files={
                        "imagens": (
                            imagem["nome_arquivo"],
                            imagem["conteudo"],
                            imagem["tipo_mime"],
                        )
                    },
                    follow_redirects=False,
                )
                self.assertEqual(response.status_code, 303, response.text)
                with self.engine.connect() as connection:
                    registros[categoria] = connection.execute(
                        text("""
                            SELECT id FROM testes_etiquetagem
                            WHERE evento_id = :evento_id AND permissao = :permissao
                        """),
                        {"evento_id": self.evento_id, "permissao": categoria},
                    ).scalar_one()
                repetida = self.client.post(
                    "/teste_etiquetagem",
                    data={**dados, "permissao": categoria, "numero_etiqueta": "151"},
                    follow_redirects=False,
                )
                self.assertEqual(repetida.status_code, 200)
                self.assertIn(
                    "Faixa de etiquetas já utilizada", repetida.context["flash_error"]
                )
                editada = self.client.post(
                    "/teste_etiquetagem",
                    data={
                        **dados,
                        "permissao": categoria,
                        "registro_id": str(registros[categoria]),
                        "observacoes": "Revisao da categoria",
                    },
                    follow_redirects=False,
                )
                self.assertEqual(editada.status_code, 303, editada.text)

        troca = self.client.post(
            "/teste_etiquetagem",
            data={
                **dados,
                "permissao": "todos",
                "registro_id": str(registros["permitido"]),
            },
            follow_redirects=False,
        )
        self.assertEqual(troca.status_code, 200)
        self.assertIn("Faixa de etiquetas já utilizada", troca.context["flash_error"])
        with self.engine.connect() as connection:
            categorias = (
                connection.execute(
                    text("""
                    SELECT permissao FROM testes_etiquetagem
                    WHERE evento_id = :evento_id ORDER BY permissao
                """),
                    {"evento_id": self.evento_id},
                )
                .scalars()
                .all()
            )
        self.assertEqual(categorias, ["permitido", "todos"])
        outro_evento = criar_dados_evento(self.engine)
        self.assertIsNone(
            postgres.verificar_etiqueta_existente(
                evento_id=outro_evento["evento_id"],
                permissao="permitido",
                numero_etiqueta="150",
                numero_final=152,
            )
        )
        self.assertIsNotNone(
            postgres.verificar_etiqueta_existente(
                evento_id=outro_evento["evento_id"],
                permissao="todos",
                numero_etiqueta="151",
                numero_final=153,
            )
        )
        troca_livre = self.client.post(
            "/teste_etiquetagem",
            data={
                **dados,
                "permissao": "todos",
                "numero_etiqueta": "160",
                "registro_id": str(registros["permitido"]),
            },
            follow_redirects=False,
        )
        self.assertEqual(troca_livre.status_code, 303, troca_livre.text)
        with self.engine.connect() as connection:
            alterada = (
                connection.execute(
                    text("""
                    SELECT permissao, numero_etiqueta
                    FROM testes_etiquetagem WHERE id = :id
                """),
                    {"id": registros["permitido"]},
                )
                .mappings()
                .one()
            )
        self.assertEqual(alterada["permissao"], "todos")
        self.assertEqual(alterada["numero_etiqueta"], "160")
        auditoria = self.client.get("/auditoria?origem=Teste%20de%20etiquetagem")
        self.assertEqual(auditoria.status_code, 200)
        self.assertIn("Imagem anexada", auditoria.text)

    def test_auditoria_ignora_nulos_equivalentes_e_registra_edicao_real(self) -> None:
        from app.services import postgres

        ocorrencia_id = self.cadastrar_emissao()
        with self.engine.connect() as connection:
            antes = connection.execute(
                text(
                    "SELECT COUNT(*) FROM auditoria_ocorrencias WHERE ocorrencia_id = :id"
                ),
                {"id": ocorrencia_id},
            ).scalar_one()
        resultado = postgres.atualizar_campos_na_aba_mae(
            evento_id=self.evento_id,
            id_ocorrencia=str(ocorrencia_id),
            novos_valores={"Processo SEI UTE": "none", "Alguém mais ciente?": "null"},
            usuario_fiscal=self.dados["fiscal_nome"],
        )
        self.assertFalse(resultado.startswith("ERRO"), resultado)
        with self.engine.connect() as connection:
            depois = connection.execute(
                text(
                    "SELECT COUNT(*) FROM auditoria_ocorrencias WHERE ocorrencia_id = :id"
                ),
                {"id": ocorrencia_id},
            ).scalar_one()
        self.assertEqual(depois, antes)
        resultado = postgres.atualizar_campos_na_aba_mae(
            evento_id=self.evento_id,
            id_ocorrencia=str(ocorrencia_id),
            novos_valores={"Ocorrência (observações)": "Observacao realmente alterada"},
            usuario_fiscal=self.dados["fiscal_nome"],
        )
        self.assertFalse(resultado.startswith("ERRO"), resultado)
        auditoria = self.client.get("/auditoria?origem=Emissão")
        self.assertIn("Observacao realmente alterada", auditoria.text)
        self.assertIn(self.dados["fiscal_nome"], auditoria.text)

    def test_migracoes_reaplicadas_preservam_dados_existentes(self) -> None:
        aplicar_migracoes_testes(self.engine)
        aplicar_migracoes_testes(self.engine)
        with self.engine.connect() as connection:
            evento = connection.execute(
                text("SELECT cidade, uf FROM eventos WHERE id = :id"),
                {"id": self.evento_id},
            ).one()
        self.assertEqual(tuple(evento), ("Rio de Janeiro", "RJ"))

    def test_ute_ordenacao_numerica_e_isolamento_por_evento(self) -> None:
        outro = criar_dados_evento(self.engine)
        with self.engine.begin() as connection:
            for entidade, frequencia, evento_id in (
                ("Entidade dez", 10, self.evento_id),
                ("Entidade dois", 2, self.evento_id),
                ("Entidade de outro evento", 1, outro["evento_id"]),
            ):
                connection.execute(
                    text("""
                    INSERT INTO tabela_ute (evento_id, pais_entidade, local, frequencia_mhz, processo_sei)
                    VALUES (:evento_id, :entidade, 'Arena', :frequencia, '12345.000001/2026-10')
                """),
                    {
                        "evento_id": evento_id,
                        "entidade": entidade,
                        "frequencia": frequencia,
                    },
                )
        for direcao, esperado in (
            ("asc", ["Entidade dois", "Entidade dez"]),
            ("desc", ["Entidade dez", "Entidade dois"]),
        ):
            with self.subTest(direcao=direcao):
                response = self.client.get(f"/ute?dir={direcao}&page_size=999")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [row["País/Entidade"] for row in response.context["rows"]], esperado
                )
                self.assertEqual(response.context["page_size"], 10)
                self.assertNotIn("Entidade de outro evento", response.text)

    def test_estacao_edicao_desativacao_reativacao_preserva_emissoes(self) -> None:
        ocorrencia_id = self.cadastrar_emissao()
        estacao_id = self.dados["estacao_id"]
        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE ocorrencias SET estacao_id = :estacao_id WHERE id = :id"),
                {"estacao_id": estacao_id, "id": ocorrencia_id},
            )
        self.login("coordenador")
        response = self.client.post(
            f"/estacoes/{estacao_id}/editar",
            data={
                "evento_id": str(self.evento_id),
                "nome": "Estacao editada",
                "modelo": "RFeye",
                "local": "Arena",
                "latitude": "-22.9",
                "longitude": "-43.2",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.client.post(
            f"/estacoes/{estacao_id}/excluir",
            data={"evento_id": self.evento_id},
            follow_redirects=False,
        )
        with self.engine.connect() as connection:
            inativa = connection.execute(
                text("SELECT desabilitada_em FROM estacoes WHERE id = :id"),
                {"id": estacao_id},
            ).scalar_one()
        self.assertIsNotNone(inativa)
        self.client.post(
            f"/estacoes/{estacao_id}/reativar",
            data={"evento_id": self.evento_id},
            follow_redirects=False,
        )
        with self.engine.connect() as connection:
            estacao = connection.execute(
                text("SELECT nome, desabilitada_em FROM estacoes WHERE id = :id"),
                {"id": estacao_id},
            ).one()
            vinculo = connection.execute(
                text("SELECT estacao_id FROM ocorrencias WHERE id = :id"),
                {"id": ocorrencia_id},
            ).scalar_one()
        self.assertEqual(tuple(estacao), ("Estacao editada", None))
        self.assertEqual(vinculo, estacao_id)
        self.assertIn(
            "Estação reativada", self.client.get("/auditoria?origem=Coordenação").text
        )

    def test_estacao_nao_aceita_coordenada_invalida_nem_fiscal_comum(self) -> None:
        formulario = {
            "evento_id": str(self.evento_id),
            "nome": "Estacao nao criada",
            "modelo": "RFeye",
            "local": "Arena",
            "latitude": "91",
            "longitude": "-43.2",
        }
        response = self.client.post(
            "/estacoes", data=formulario, follow_redirects=False
        )
        self.assertEqual(response.headers["location"], "/menu")
        self.login("coordenador")
        self.client.post("/estacoes", data=formulario, follow_redirects=False)
        with self.engine.connect() as connection:
            quantidade = connection.execute(
                text("SELECT COUNT(*) FROM estacoes WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
        self.assertEqual(quantidade, 1)

    def test_escala_criacao_filtros_e_turno_que_cruza_meia_noite(self) -> None:
        self.login("coordenador")
        for fiscal_id, inicio, fim in (
            (self.dados["fiscal"], "22:00", "02:00"),
            (self.dados["outro"], "08:00", "10:30"),
        ):
            response = self.client.post(
                "/coordenacao/escala",
                data={
                    "fiscal_id": str(fiscal_id),
                    "data_trabalho": "2026-10-11",
                    "turno_inicio": inicio,
                    "turno_fim": fim,
                },
                follow_redirects=False,
            )
            self.assertEqual(response.status_code, 303)

        with self.engine.connect() as connection:
            quantidade_antes = connection.execute(
                text("SELECT COUNT(*) FROM escalas_trabalho WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
        resposta_sobreposta = self.client.post(
            "/coordenacao/escala",
            data={
                "fiscal_id": str(self.dados["fiscal"]),
                "data_trabalho": "2026-10-12",
                "turno_inicio": "01:00",
                "turno_fim": "03:00",
            },
            follow_redirects=False,
        )
        self.assertEqual(resposta_sobreposta.status_code, 303)
        self.assertIn(
            "se sobrepõe a outra escala deste fiscal",
            self.client.get("/coordenacao?aba=escala").text,
        )
        with self.engine.connect() as connection:
            quantidade_apos_rejeicao = connection.execute(
                text("SELECT COUNT(*) FROM escalas_trabalho WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
        self.assertEqual(quantidade_apos_rejeicao, quantidade_antes)

        self.login("fiscal")
        proprias = self.client.get("/escalas?visualizacao=proprias")
        outra_fiscal = self.client.get(f"/escalas?visualizacao={self.dados['outro']}")
        self.assertEqual(
            [item["fiscal_id"] for item in proprias.context["escalas"]],
            [self.dados["fiscal"]],
        )
        self.assertEqual(
            [item["fiscal_id"] for item in outra_fiscal.context["escalas"]],
            [self.dados["outro"]],
        )
        self.assertIn(
            f'<option value="{self.dados["outro"]}" selected>',
            outra_fiscal.text,
        )
        self.assertEqual(proprias.context["resumo_horas"][0]["total_minutos"], 240)
        self.assertEqual(outra_fiscal.context["resumo_horas"][0]["total_minutos"], 150)
        self.assertIn(
            "Escala criada", self.client.get("/auditoria?origem=Coordenação").text
        )

        self.login("coordenador")
        resposta_contigua = self.client.post(
            "/coordenacao/escala",
            data={
                "fiscal_id": str(self.dados["fiscal"]),
                "data_trabalho": "2026-10-12",
                "turno_inicio": "02:00",
                "turno_fim": "04:00",
            },
            follow_redirects=False,
        )
        self.assertEqual(resposta_contigua.status_code, 303)
        with self.engine.connect() as connection:
            quantidade_apos_contigua = connection.execute(
                text("SELECT COUNT(*) FROM escalas_trabalho WHERE evento_id = :id"),
                {"id": self.evento_id},
            ).scalar_one()
        self.assertEqual(quantidade_apos_contigua, quantidade_antes + 1)

    def test_devolver_ticket_sem_campo_motivo_deve_ser_recusado(self) -> None:
        from app.services import postgres

        ocorrencia_id = self.cadastrar_emissao()
        ticket_id = postgres.salvar_ticket_evento(
            self.evento_id, [ocorrencia_id], fiscal_ids=[self.dados["fiscal"]]
        )
        self.esclarecer_emissao(ocorrencia_id, ticket_id)
        postgres.atualizar_ticket_evento(
            ticket_id,
            self.evento_id,
            "concluido_pelos_fiscais",
            providencias="Inspecao feita",
        )
        self.login("coordenador")
        self.client.post(
            f"/coordenacao/ticket/{ticket_id}/status",
            data={"status": "pendente"},
            follow_redirects=False,
        )
        with self.engine.connect() as connection:
            status = connection.execute(
                text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
            ).scalar_one()
        self.assertEqual(
            status,
            "concluido_pelos_fiscais",
            "Devolucao sem motivo nao pode alterar o ticket",
        )
        with self.assertRaisesRegex(ValueError, "motivo"):
            postgres.atualizar_ticket_evento(ticket_id, self.evento_id, "pendente")
        with self.engine.connect() as connection:
            status = connection.execute(
                text("SELECT status FROM tickets WHERE id = :id"), {"id": ticket_id}
            ).scalar_one()
        self.assertEqual(status, "concluido_pelos_fiscais")


if __name__ == "__main__":
    unittest.main()
