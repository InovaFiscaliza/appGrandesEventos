--
-- PostgreSQL database dump
--

\restrict NNI4QDQMQ7lNY4Lttuf3HfSCIh1khg3l4KPnzPWTNO4AeFeW4guU5uKxaXPfos9

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS appeventos;
--
-- Name: appeventos; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE appeventos WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


\unrestrict NNI4QDQMQ7lNY4Lttuf3HfSCIh1khg3l4KPnzPWTNO4AeFeW4guU5uKxaXPfos9
\connect appeventos
\restrict NNI4QDQMQ7lNY4Lttuf3HfSCIh1khg3l4KPnzPWTNO4AeFeW4guU5uKxaXPfos9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- Name: set_atualizado_em(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_atualizado_em() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bsr_erb; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bsr_erb (
    id bigint NOT NULL,
    evento_id bigint NOT NULL,
    tipo text NOT NULL,
    regiao text,
    latitude numeric(9,6),
    longitude numeric(9,6),
    criado_em timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: bsr_erb_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bsr_erb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bsr_erb_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bsr_erb_id_seq OWNED BY public.bsr_erb.id;


--
-- Name: estacoes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estacoes (
    id bigint NOT NULL,
    evento_id bigint NOT NULL,
    nome text NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6)
);


--
-- Name: estacoes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estacoes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estacoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estacoes_id_seq OWNED BY public.estacoes.id;


--
-- Name: eventos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eventos (
    id bigint NOT NULL,
    nome text NOT NULL,
    legacy_sheet_id text,
    latitude numeric(9,6),
    longitude numeric(9,6),
    fuso_horario text DEFAULT 'America/Sao_Paulo'::text,
    criado_em timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: eventos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eventos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eventos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eventos_id_seq OWNED BY public.eventos.id;


--
-- Name: ocorrencias; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ocorrencias (
    id bigint NOT NULL,
    evento_id bigint NOT NULL,
    estacao_id bigint,
    local_regiao text,
    fiscal text,
    data date,
    hora time without time zone,
    frequencia_mhz numeric(12,3),
    largura_khz numeric(12,3),
    faixa text,
    identificacao text,
    autorizado text,
    ute boolean DEFAULT false,
    processo_sei_ute text,
    observacoes text,
    alguem_ciente text,
    interferente text,
    situacao text DEFAULT 'Pendente'::text NOT NULL,
    fonte text,
    criado_em timestamp with time zone DEFAULT now() NOT NULL,
    atualizado_em timestamp with time zone DEFAULT now() NOT NULL,
    id_planilha text
);


--
-- Name: ocorrencias_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ocorrencias_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ocorrencias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ocorrencias_id_seq OWNED BY public.ocorrencias.id;


--
-- Name: opcoes_identificacao; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.opcoes_identificacao (
    id bigint NOT NULL,
    evento_id bigint,
    valor text NOT NULL
);


--
-- Name: opcoes_identificacao_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.opcoes_identificacao_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: opcoes_identificacao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.opcoes_identificacao_id_seq OWNED BY public.opcoes_identificacao.id;


--
-- Name: tabela_ute; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tabela_ute (
    id bigint NOT NULL,
    evento_id bigint NOT NULL,
    pais_entidade text,
    local text,
    frequencia_mhz numeric(12,3),
    processo_sei text,
    id_planilha text
);


--
-- Name: tabela_ute_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tabela_ute_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tabela_ute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tabela_ute_id_seq OWNED BY public.tabela_ute.id;


--
-- Name: bsr_erb id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bsr_erb ALTER COLUMN id SET DEFAULT nextval('public.bsr_erb_id_seq'::regclass);


--
-- Name: estacoes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacoes ALTER COLUMN id SET DEFAULT nextval('public.estacoes_id_seq'::regclass);


--
-- Name: eventos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos ALTER COLUMN id SET DEFAULT nextval('public.eventos_id_seq'::regclass);


--
-- Name: ocorrencias id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocorrencias ALTER COLUMN id SET DEFAULT nextval('public.ocorrencias_id_seq'::regclass);


--
-- Name: opcoes_identificacao id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.opcoes_identificacao ALTER COLUMN id SET DEFAULT nextval('public.opcoes_identificacao_id_seq'::regclass);


--
-- Name: tabela_ute id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabela_ute ALTER COLUMN id SET DEFAULT nextval('public.tabela_ute_id_seq'::regclass);


--
-- Data for Name: bsr_erb; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bsr_erb (id, evento_id, tipo, regiao, latitude, longitude, criado_em) FROM stdin;
19	1	BSR/Jammer	Minha casa	-22.920126	-43.087925	2026-07-09 13:00:29.681156+00
20	1	BSR/Jammer	Santa Rosa	-77.123456	-88.123456	2026-07-09 13:00:29.681156+00
21	1	ERB Fake	São Domingos	-23.123456	-33.123456	2026-07-09 13:00:29.681156+00
22	1	BSR/Jammer	MInha casa ok	-2.291804	-43.086508	2026-07-09 13:00:29.681156+00
23	1	BSR/Jammer	MInha casa ok	-22.918137	-4.308657	2026-07-09 13:00:29.681156+00
24	1	BSR/Jammer	Minha casa 5	-22.123000	-43.123000	2026-07-09 13:00:29.681156+00
25	1	BSR/Jammer	Minha casa 6	-22.777778	-43.777778	2026-07-09 13:00:29.681156+00
26	1	BSR/Jammer	Minha casa 99	-11.110000	-55.550000	2026-07-09 13:00:29.681156+00
27	1	BSR/Jammer	Minha casa 111	-21.110000	-33.110000	2026-07-09 13:00:29.681156+00
\.


--
-- Data for Name: estacoes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estacoes (id, evento_id, nome, latitude, longitude) FROM stdin;
1	1	RFeye002182 - Moto GP	\N	\N
2	2	RFeye002123 - Sapucaí	\N	\N
3	2	ETM - Sapucaí 2	\N	\N
4	3	ERMxBA02 - Campo Grande	\N	\N
5	3	RFEye002102 - Farol da Barra	\N	\N
6	3	ERMxBA01 - Ondina	\N	\N
7	4	CWSM21120033 - IFSP	\N	\N
8	4	RFeye002227 - IFSP	\N	\N
\.


--
-- Data for Name: eventos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.eventos (id, nome, legacy_sheet_id, latitude, longitude, fuso_horario, criado_em) FROM stdin;
1	Moto GP	1cU5jGZQbMoWQVOYEWu-tdRcnT3TDRB64I1v7Q_qDQZs	-16.719076	-49.191969	America/Sao_Paulo	2026-07-07 18:43:00.55986+00
2	Carnaval RJ	1GVDb23FU8EAPyBpRIVogRf_D86s98lv8A3tfFtPVf2Q	-22.911269	-43.196761	America/Sao_Paulo	2026-07-07 18:43:07.612148+00
3	Carnaval BA	1M5c5TZsuVMeoNtTE8_UXa0XeHGkqW1JsEt7PubPj3yI	-13.008738	-38.517323	America/Bahia	2026-07-07 18:43:14.45998+00
4	Carnaval SP	14h_kTzq74fhEPY_u3pFSEvHidwiSdmSbI-pkL7gb1Og	-23.522497	-46.625133	America/Sao_Paulo	2026-07-07 18:43:26.553959+00
\.


--
-- Data for Name: ocorrencias; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ocorrencias (id, evento_id, estacao_id, local_regiao, fiscal, data, hora, frequencia_mhz, largura_khz, faixa, identificacao, autorizado, ute, processo_sei_ute, observacoes, alguem_ciente, interferente, situacao, fonte, criado_em, atualizado_em, id_planilha) FROM stdin;
1	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Marcos Juliano, Devechi, Wesley, Pedro e Lenadro	2026-03-20	12:20:00	\N	\N	Satélite	Comunicação relacionada ao evento	Indefinido	f		Intertrade Brasil Telecomunicações Multimídia e Representações LTDA CNPJ 02.621.577/0001-46 - Serviço Limitado por Satélite Estação nº 1015734305 / Pedro Spinoza Barroso Neto (técnico) / trata-se de subida de satélite referente ao envio de sinais da corrida para outros países (nome fantasia da entidade - Casablanca).\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-01
2	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Marcos Juliano, Devechi, Wesley, Pedro e Lenadro	2026-03-20	12:23:00	\N	\N	Satélite	Comunicação relacionada ao evento	Indefinido	f		Intertrade Brasil Telecomunicações Multimídia e Representações LTDA CNPJ 02.621.577/0001-46 - Serviço Limitado por Satélite Estação nº 1015739420 / Pedro Spinoza Barroso Neto (técnico) / trata-se de subida de satélite referente ao envio de sinais da corrida para outros países (nome fantasia da entidade - Casablanca).\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-02
3	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:54:00	453.350	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-03
4	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:55:00	454.550	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-04
5	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:55:00	455.150	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-05
6	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:55:00	455.200	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-06
7	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:56:00	456.900	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-07
8	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:57:00	457.250	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-08
9	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:57:00	464.325	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-09
10	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	13:58:00	452.300	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de rádio transceptor HP Hytera modelo HP566 usado nas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-10
11	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:00:00	467.650	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência da REPETIDORA  para os HTs. Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-11
12	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:01:00	457.650	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010530/2026-39  -  Ato 3232	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência dos HTs para a REPETIDORA . Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-12
13	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:05:00	458.138	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500011761/2026-60  -  Ato 3236	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência dos HTs para a REPETIDORA . Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-13
67	1	\N	Charitas	André whatsapp	2026-06-30	12:21:00	44444.000	444.000	SLP	Comunicação relacionada ao evento	Indefinido	f	33ewrfseer	-		Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-67
14	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:06:00	458.238	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500011761/2026-60  -  Ato 3236	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência dos HTs para a REPETIDORA . Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-14
15	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:08:00	468.138	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500011761/2026-60  -  Ato 3236	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência da REPETIDORA para os HTs. Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-15
16	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano e Devechi	2026-03-21	14:08:00	468.238	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500011761/2026-60  -  Ato 3236	Internacional Publicity - INTERPUB/André Manhães Barreto (Gerente da VERTIX)/trata-se de frequência da REPETIDORA para os HTs. Usada pelas equipes de produção (bilheteria, área vip, limpeza, segurança e deslocamentos) e equipes esportivas (race control, equipe médica e sinalização bandeiras na pista). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-16
17	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:29:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-17
18	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:29:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-18
19	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:29:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-19
20	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:30:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-20
21	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:30:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-21
22	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:30:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-22
23	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:30:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-23
24	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:31:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-24
25	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:38:00	456.269	8.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-25
26	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:38:00	456.044	8.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-26
27	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:39:00	458.856	8.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-27
28	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:39:00	468.413	8.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-28
29	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:40:00	450.150	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-29
30	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:40:00	450.188	12.500	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-30
31	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:41:00	500.000	150.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-31
32	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:41:00	500.375	150.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-32
33	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:41:00	500.775	150.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-33
34	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:41:00	501.200	150.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-34
35	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:42:00	501.600	150.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-35
36	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:43:00	636.930	100.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-36
37	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:44:00	653.200	100.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-37
38	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:44:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-38
39	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:45:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-39
40	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:45:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-40
41	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:45:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-41
42	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:45:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-42
43	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:46:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-43
44	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:46:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-44
45	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:47:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-45
68	1	\N	qqqqqqqqqqqqqqqqqqqqqqq	qqqqqqqqqqqqqqqqqq	2026-06-30	17:36:00	\N	\N	SMM	Comunicação relacionada ao evento	Não licenciável	f	zzzzzzzzzzzzzzzzzaaaaaaaaaaaaaaaaaaaaaaaaa	1212121212 -	Não ninguem	Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-68
46	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:48:00	708.000	40.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010857/2026-19 - Ato 3235	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-46
47	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:49:00	754.000	40.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010857/2026-19 - Ato 3235	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-47
48	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:49:00	654.880	40.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010857/2026-19 - Ato 3235	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-48
49	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Devechi e Eduardo	2026-03-21	14:49:00	693.600	40.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500010857/2026-19 - Ato 3235	INTERNATIONAL PUBLICITY - INTERPUB/Noemi Lacasa (RF Manager)/trata-se de câmeras sem fio, transmissores de áudio, repetidoras e HTs (geração de imagens, conteúdo e coordenação de equipes). -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-49
50	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Juliano Valim e Eduardo Rege	2026-03-21	15:19:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500010566/2026-12 - Ato 3233	International Publicity - INTERPUB / Noemi Lacasa (RF Manager) / trata-se da frequência da câmera sem fio instalada no helicóptero. Medida através do sensor da RFeye instalada no autódromo. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-50
51	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:43:00	450.500	25.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-51
52	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:44:00	456.600	25.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-52
53	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:44:00	460.480	25.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-53
54	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:45:00	462.480	25.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-54
55	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:45:00	451.150	25.000	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-55
56	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:47:00	510.500	200.000	Radiação Restrita	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamentos rádio HTs, repetidora, câmeras e microfones sem fio e subida de satélite. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-56
57	1	\N	Autódromo Ayrton Senna - Goiânia/GO	Leandro Belo, Wellington Devechi e Juliano	2026-03-22	11:54:00	\N	\N	SLP	Comunicação relacionada ao evento	Indefinido	t	53500.019775/2026-21 - Ato 4029	Rádio e Televisão Bandeirantes S/A CNPJ 60.509.239/0001-13 / Robinson Melo (Engenheiro) / Trata-se de utilização de equipamento subida de satélite; Serviço Limitado por Satélite - Estação nº 699700612. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-57
58	1	\N	Niterói	André Rezende	2026-05-27	16:21:00	550.000	234.000	SMA	Comunicação não relacionada ao evento	Sim	t	5501234-000	Presidência da Republica -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-58
59	1	\N	Niterói	André Rezende	2026-05-27	16:21:00	550.000	234.000	SMA	Comunicação não relacionada ao evento	Indefinido	t	5501234-000	Presidência da Republica -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-59
60	1	\N	Niterói	André Rezende	2026-05-29	09:47:00	606.000	12.000	TV	Espúrio ou Produto de Intermodulação	Indefinido	t	Desconhecido	Cidade do RIo de Janeiro -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-60
61	1	\N	Piratininga	André Rezende	2026-06-02	09:49:00	608.000	13.000	TV	Sinal de dados	Indefinido	f	Desconhecido	-		Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-61
62	1	\N	Piratininga	André Rezende	2026-06-02	09:49:00	608.000	13.000	TV	Sinal de dados	Não licenciável	f	Desconhecido	-	Não ninguem	Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-62
63	1	\N	Icarai	André Rezende	2026-06-02	11:27:00	999.000	123.000	GNSS	Comunicação não relacionada ao evento	Indefinido	f	1233222332	OI Telemar -		Sim	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-63
64	1	\N	Ingá	Marcio Macedo	2026-06-02	15:38:00	\N	6.000	TV	Comunicação não relacionada ao evento	Indefinido	f	540001234	Rede Globo -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-64
65	1	\N	Ingá	Marcio Macedo - FastAPI	2026-06-08	14:57:00	702.000	12.000	SMA	Sinal de dados	Indefinido	t	540001234	Rede TV -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-65
66	1	\N	Niteroi	André Rezende - StreamLit	2026-06-09	11:21:00	609.000	13.000	SMA	Sinal de dados	Indefinido	t	540001234	Rede TV -		Sim	Pendente	ABORDAGEM	2026-07-07 18:43:01.655858+00	2026-07-07 18:43:01.655858+00	Abo-66
69	1	1	rfeye002182	Thiago	2026-03-20	\N	\N	12.500		Comunicação não relacionada ao evento	Sim	f					concluído	ESTACAO	2026-07-07 18:43:02.154212+00	2026-07-07 18:43:02.154212+00	1-RF82
70	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:26:00	650.675	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-01
71	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:27:00	644.650	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-02
72	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:28:00	627.700	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-03
73	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:29:00	630.275	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-04
74	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:29:00	630.850	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-05
75	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:31:00	634.900	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-06
76	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:31:00	544.675	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo - In Ear -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-07
77	2	\N	Sambódromo RJ - Camarote Rio	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:32:00	543.275	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Camarote RIO - Coordenação da BMX - Sistema Spectera do Cantor Belo - In Ear -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-08
78	2	\N	Sambódromo RJ - Rádios	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:39:00	674.175	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		InEar  da rádio Roquete Pinto -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-09
79	2	\N	Sambódromo RJ - Rádios	Fábio Cunha, Patrícia Espírito Santo, Carlos Zenão	2026-02-13	21:40:00	692.125	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		InEar  da rádio Roquete Pinto -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-10
80	2	\N	Sambódromo RJ - Camarote Camisa 10	Fábio Cunha,  Carlos Zenão, Nilson Costa	2026-02-13	21:41:00	480.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Microfone Camarote Camisa 10 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-11
81	2	\N	Sambódromo RJ - Camarote Mar	Fábio Cunha,  Carlos Zenão, Nilson Costa	2026-02-13	21:43:00	500.175	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Microfone Camarote Mar - Responsável: Vinícius - Telefone: (21) 98133-0262. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-12
82	2	\N	Sambódromo RJ - Camarote Mar	Fábio Cunha,  Carlos Zenão, Nilson Costa	2026-02-13	21:46:00	500.525	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Microfone Camarote Mar - Responsável: Vinícius - Telefone: (21) 98133-0262. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-13
83	2	\N	Sambódromo RJ - Camarote Mar	Fábio Cunha,  Carlos Zenão, Nilson Costa	2026-02-13	21:46:00	489.800	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Microfone Camarote Mar - Responsável: Vinícius - Telefone: (21) 98133-0262. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-14
84	2	\N	Imprensa	Zenao e Aluisio	2026-02-14	22:13:00	518.000	20.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Leonardo - Energia produções e eventos\nProdutos não homologados com foto -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-15
85	2	\N	Imprensa	Zenao e Aluisio	2026-02-14	22:17:00	533.000	20.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Leonardo - Energia produções e eventos\nProdutos não homologados com fotos -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-16
86	2	\N	Imprensa	Zenao e Aluisio	2026-02-14	22:17:00	628.650	20.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Leonardo - Energia produções e eventos\nProdutos não homologados com fotos\nNão vai usar essa -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-18
87	2	\N	Imprensa	Zenao e Aluisio	2026-02-14	22:19:00	572.500	20.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		Leonardo - Energia produções e eventos\nProdutos não homologados com fotos. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:08.767546+00	2026-07-07 18:43:08.767546+00	Abo-19
88	2	2	RFeye002123	Daniel	2026-02-12	17:20:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	1-RF23
89	2	2	RFeye002123	Daniel	2026-02-12	17:20:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	2-RF23
90	2	2	RFeye002123	Daniel	2026-02-12	17:20:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	3-RF23
91	2	2	RFeye002123	Daniel	2026-02-12	17:20:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	4-RF23
92	2	2	RFeye002123	Daniel	2026-02-12	17:25:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	5-RF23
93	2	2	RFeye002123	Daniel	2026-02-12	17:25:00	\N	100.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	6-RF23
94	2	2	RFeye002123	Daniel	2026-02-12	17:17:00	\N	35.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	7-RF23
95	2	2	RFeye002123	Daniel	2026-02-12	17:16:00	\N	50.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	8-RF23
96	2	2	RFeye002123	Daniel	2026-02-12	16:55:00	\N	50.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	9-RF23
97	2	2	RFeye002123	Daniel	2026-02-12	17:12:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	10-RF23
98	2	2	RFeye002123	Daniel	2026-02-12	17:06:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	11-RF23
99	2	2	RFeye002123	Daniel	2026-02-12	17:10:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	12-RF23
100	2	2	RFeye002123	Daniel	2026-02-12	17:10:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	13-RF23
101	2	2	RFeye002123	Daniel	2026-02-13	21:07:00	\N	30.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	14-RF23
102	2	2	RFeye002123	Daniel	2026-02-13	21:11:00	\N	30.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	15-RF23
103	2	2	RFeye002123	Daniel	2026-02-13	17:45:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	16-RF23
104	2	2	RFeye002123	Daniel	2026-02-13	17:38:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	17-RF23
105	2	2	RFeye002123	Daniel	2026-02-13	19:16:00	\N	25.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	18-RF23
106	2	2	RFeye002123	Daniel	2026-02-13	19:20:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	19-RF23
107	2	2	RFeye002123	Daniel	2026-02-13	18:22:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	20-RF23
108	2	2	RFeye002123	Daniel	2026-02-13	18:18:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	21-RF23
109	2	2	RFeye002123	Daniel	2026-02-13	18:15:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	22-RF23
110	2	2	RFeye002123	Daniel	2026-02-13	18:23:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	23-RF23
111	2	2	RFeye002123	Daniel	2026-02-13	20:55:00	\N	30.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	24-RF23
112	2	2	RFeye002123	Daniel	2026-02-13	18:20:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	25-RF23
113	2	2	RFeye002123	Daniel	2026-02-13	18:25:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	26-RF23
114	2	2	RFeye002123	Daniel	2026-02-13	18:55:00	\N	25.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	27-RF23
115	2	2	RFeye002123	Daniel	2026-02-13	18:55:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	28-RF23
116	2	2	RFeye002123	Daniel	2026-02-13	18:58:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	29-RF23
117	2	2	RFeye002123	Daniel	2026-02-13	18:58:00	\N	25.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	30-RF23
118	2	2	RFeye002123	Daniel	2026-02-13	18:28:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	31-RF23
119	2	2	RFeye002123	Daniel	2026-02-13	17:05:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	32-RF23
120	2	2	RFeye002123	Daniel	2026-02-13	17:10:00	\N	25.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	33-RF23
121	2	2	RFeye002123	Daniel	2026-02-13	17:11:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	34-RF23
122	2	2	RFeye002123	Daniel	2026-02-13	17:13:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Sim	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	35-RF23
123	2	2	RFeye002123	Daniel	2026-02-13	17:14:00	\N	25.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	36-RF23
124	2	2	RFeye002123	Daniel	2026-02-13	17:18:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Sim	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	37-RF23
125	2	2	RFeye002123	Daniel	2026-02-13	17:19:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Sim	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	38-RF23
126	2	2	RFeye002123	Daniel	2026-02-13	17:25:00	\N	30.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	39-RF23
127	2	2	RFeye002123	Daniel	2026-02-13	17:32:00	\N	25.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	40-RF23
128	2	2	RFeye002123	Daniel	2026-02-14	20:34:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	41-RF23
129	2	2	RFeye002123	Daniel	2026-02-14	20:36:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	42-RF23
130	2	2	RFeye002123	Daniel	2026-02-14	20:27:00	\N	25.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	43-RF23
131	2	2	RFeye002123	Daniel	2026-02-14	20:27:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	44-RF23
132	2	2	RFeye002123	Daniel	2026-02-14	20:30:00	\N	25.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	45-RF23
133	2	2	RFeye002123	Daniel	2026-02-14	20:34:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	46-RF23
134	2	2	RFeye002123	Daniel	2026-02-14	23:56:00	\N	60.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	47-RF23
135	2	2	RFeye002123	Daniel	2026-02-15	00:40:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	48-RF23
136	2	2	RFeye002123	Daniel	2026-02-15	00:40:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	49-RF23
137	2	2	RFeye002123	Daniel	2026-02-15	00:40:00	\N	30.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	50-RF23
138	2	2	RFeye002123	Daniel	2026-02-15	19:30:00	\N	20.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	51-RF23
139	2	2	RFeye002123	Daniel	2026-02-15	19:31:00	\N	20.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	52-RF23
140	2	2	RFeye002123	Daniel	2026-02-15	19:32:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	53-RF23
141	2	2	RFeye002123	Daniel	2026-02-15	19:32:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	54-RF23
142	2	2	RFeye002123	Daniel	2026-02-15	19:34:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	55-RF23
143	2	2	RFeye002123	Daniel	2026-02-15	00:09:00	\N	30.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	56-RF23
144	2	2	RFeye002123	Daniel	2026-02-15	00:17:00	\N	30.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	57-RF23
145	2	2	RFeye002123	Daniel	2026-02-15	00:23:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	58-RF23
146	2	2	RFeye002123	Daniel	2026-02-15	00:23:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	59-RF23
147	2	2	RFeye002123	Daniel	2026-02-15	00:23:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	60-RF23
148	2	2	RFeye002123	Daniel	2026-02-15	00:23:00	\N	50.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	61-RF23
149	2	2	RFeye002123	Daniel	2026-02-16	17:55:00	\N	30.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	62-RF23
150	2	2	RFeye002123	Daniel	2026-02-16	18:39:00	\N	30.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	63-RF23
151	2	2	RFeye002123	Daniel	2026-02-17	21:40:00	\N	25.000		Não identificado	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.187072+00	2026-07-07 18:43:09.187072+00	64-RF23
152	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	1-ETM1
153	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	2-ETM1
154	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	3-ETM1
155	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	4-ETM1
156	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	5-ETM1
157	2	3	ETM007	Aluízio	2026-02-13	17:22:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	6-ETM1
158	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	7-ETM1
159	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	8-ETM1
160	2	3	ETM007	Aluízio	2026-02-13	18:18:00	\N	200.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	9-ETM1
161	2	3	ETM007	Aluízio	2026-02-13	17:30:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	10-ETM1
162	2	3	ETM007	Aluízio	2026-02-13	17:50:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	11-ETM1
163	2	3	ETM007	Aluízio	2026-02-13	17:30:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	12-ETM1
164	2	3	ETM007	Aluízio	2026-02-13	18:22:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	13-ETM1
165	2	3	ETM007	Aluízio	2026-02-13	18:22:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	14-ETM1
166	2	3	ETM007	Aluízio	2026-02-13	17:22:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	15-ETM1
167	2	3	ETM007	Aluízio	2026-02-13	17:30:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	16-ETM1
168	2	3	ETM007	Aluízio	2026-02-13	18:14:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	17-ETM1
169	2	3	ETM007	Aluízio	2026-02-13	17:30:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	18-ETM1
170	2	3	ETM007	Aluízio	2026-02-13	17:40:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	19-ETM1
171	2	3	ETM007	Aluízio	2026-02-13	17:45:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	20-ETM1
172	2	3	ETM007	Daniel	2026-02-15	19:37:00	\N	30.000		Sinal de dados	Sim	t	53500.002079/2026-86			Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	21-ETM1
173	2	3	ETM007	Daniel	2026-02-15	19:41:00	\N	20.000		Sinal de dados	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	22-ETM1
174	2	3	ETM007	Daniel	2026-02-15	19:42:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	23-ETM1
175	2	3	ETM007	Daniel	2026-02-15	19:45:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	24-ETM1
176	2	3	ETM007	Daniel	2026-02-15	19:54:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	25-ETM1
177	2	3	ETM007	Daniel	2026-02-15	19:54:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	26-ETM1
178	2	3	ETM007	Daniel	2026-02-15	19:57:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	27-ETM1
179	2	3	ETM007	Daniel	2026-02-15	19:58:00	\N	30.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	28-ETM1
180	2	3	ETM007	Daniel	2026-02-15	20:00:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	29-ETM1
181	2	3	ETM007	Daniel	2026-02-15	20:00:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	30-ETM1
182	2	3	ETM007	Daniel	2026-02-15	20:01:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	31-ETM1
183	2	3	ETM007	Daniel	2026-02-15	20:01:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	32-ETM1
184	2	3	ETM007	Daniel	2026-02-15	20:03:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	33-ETM1
185	2	3	ETM007	Daniel	2026-02-15	20:03:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	34-ETM1
186	2	3	ETM007	Daniel	2026-02-15	20:03:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	35-ETM1
187	2	3	ETM007	Daniel	2026-02-15	20:05:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	36-ETM1
188	2	3	ETM007	Daniel	2026-02-15	20:05:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	37-ETM1
189	2	3	ETM007	Daniel	2026-02-15	20:07:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	38-ETM1
190	2	3	ETM007	Daniel	2026-02-15	20:08:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	39-ETM1
191	2	3	ETM007	Daniel	2026-02-15	20:08:00	\N	20.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	40-ETM1
192	2	3	ETM007	Daniel	2026-02-15	20:09:00	\N	70.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	41-ETM1
193	2	3	ETM007	Daniel	2026-02-15	20:09:00	\N	20.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	42-ETM1
194	2	3	ETM007	Aluízio	2026-02-15	18:10:00	\N	20.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	43-ETM1
195	2	3	ETM007	Daniel	2026-02-16	00:50:00	\N	25.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	44-ETM1
196	2	3	ETM007	Daniel	2026-02-16	00:50:00	\N	25.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	45-ETM1
197	2	3	ETM007	Daniel	2026-02-16	00:50:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	46-ETM1
198	2	3	ETM007	Daniel	2026-02-16	00:52:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	47-ETM1
199	2	3	ETM007	Daniel	2026-02-16	00:54:00	\N	25.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	48-ETM1
200	2	3	ETM007	Daniel	2026-02-16	00:54:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	49-ETM1
201	2	3	ETM007	Daniel	2026-02-16	01:05:00	\N	25.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	50-ETM1
202	2	3	ETM007	Daniel	2026-02-16	01:05:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	51-ETM1
203	2	3	ETM007	Daniel	2026-02-16	01:08:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	52-ETM1
204	2	3	ETM007	Daniel	2026-02-16	01:08:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	53-ETM1
205	2	3	ETM007	Daniel	2026-02-16	01:08:00	\N	25.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	54-ETM1
206	2	3	ETM007	Daniel	2026-02-16	01:16:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	55-ETM1
207	2	3	ETM007	Daniel	2026-02-16	01:18:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	56-ETM1
208	2	3	ETM007	Daniel	2026-02-16	01:18:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	57-ETM1
209	2	3	ETM007	Daniel	2026-02-16	19:45:00	\N	30.000		Não identificado	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	58-ETM1
210	2	3	ETM007	Aluízio	2026-02-15	21:00:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	59-ETM1
211	2	3	ETM007	Aluízio	2026-02-15	21:30:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	60-ETM1
212	2	3	ETM007	Aluízio	2026-02-15	21:10:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	61-ETM1
213	2	3	ETM007	Aluízio	2026-02-15	21:30:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	62-ETM1
214	2	3	ETM007	Aluízio	2026-02-15	21:45:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	63-ETM1
215	2	3	ETM007	Aluízio	2026-02-15	21:35:00	\N	25.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	64-ETM1
216	2	3	ETM007	Aluízio	2026-02-17	01:20:00	\N	13.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.000854/2026-69			Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	65-ETM1
217	2	3	ETM007	Daniel	2026-02-17	01:32:00	\N	70.000		Sinal de dados	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	66-ETM1
218	2	3	ETM007	Daniel	2026-02-17	01:32:00	\N	25.000		Sinal de dados	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:09.677976+00	2026-07-07 18:43:09.677976+00	67-ETM1
219	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	17:58:00	567.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-01
220	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	17:59:00	695.700	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-02
221	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	17:59:00	591.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-03
222	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	17:59:00	566.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-04
223	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:00:00	595.400	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-05
224	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:00:00	696.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-06
225	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:01:00	613.000	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-07
226	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:01:00	593.000	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-08
227	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:01:00	617.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-09
228	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:02:00	591.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-10
229	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:02:00	619.000	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-11
230	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:02:00	614.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-12
231	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:02:00	595.700	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV ARATU S/A -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-13
232	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:05:00	602.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		EMPRESA METROPOLITANA DE RADIODIFUSÃO LTDA (MACACO GORDO) -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-14
233	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:05:00	557.800	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		EMPRESA METROPOLITANA DE RADIODIFUSÃO LTDA (MACACO GORDO) -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-15
234	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:06:00	557.800	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não	f		EMPRESA METROPOLITANA DE RADIODIFUSÃO LTDA (MACACO GORDO) -		Sim	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-16
235	3	\N	Campo Grande	Muniz, Brasilio, Elna e Arildo	2026-02-12	18:10:00	557.850	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		EMPRESA METROPOLITANA DE RADIODIFUSÃO LTDA (MACACO GORDO) -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-17
236	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:18:00	\N	80.000	Radiação Restrita	Sinal não relacionado ao evento	Indefinido	f		ICARO LOAN SILVA ALMEIDA -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-18
237	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:20:00	641.750	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		LEONAM SAMPAIO -SALVADOR FM		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-19
238	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:20:00	652.150	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		LEONAM SAMPAIO -SALVADOR FM		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-20
239	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:22:00	617.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		PHILIPE LUCIANO CASTRO -		Sim	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-21
240	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:23:00	634.250	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		PHILIPE LUCIANO CASTRO -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-22
241	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:24:00	686.400	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		PHILIPE LUCIANO CASTRO -RECORD TV		Sim	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-23
242	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:25:00	646.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		PHILIPE LUCIANO CASTRO -RECORD TV		Sim	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-24
243	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:26:00	647.250	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		PHILIPE LUCIANO CASTRO -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-25
244	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:26:00	634.250	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Não licenciável	f		PHILIPE LUCIANO CASTRO -RECORD TV		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-26
245	3	\N	Campo Grande	Arildo, Muniz, Brasilio e Elna	2026-02-12	18:37:00	485.350	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		IBT INTERNET DA BAHIA TELECOMUNICAÇÕES- PHILIPE LUCIANO CASTRO -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-27
246	3	\N	Campo Grande	Arildo, Muniz, Brasilio e Elna	2026-02-12	18:38:00	\N	80.000	Radiação Restrita	Sinal não relacionado ao evento	Indefinido	f		IBT INTERNET DA BAHIA TELECOMUNICAÇÕES- PHILIPE LUCIANO CASTRO -		Indefinido	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-28
247	3	\N	Campo Grande	Arildo, Muniz, Brasilio e Elna	2026-02-12	18:41:00	212.063	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		MH COMERCIO SERVIÇOS E LOCAÇÃO DE EQUIPAMENTOS EIRELLI-MARCIO CARDOSO(MEND TELECOMUNICAÇÕES/TV BAHIA) -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-29
248	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:45:00	470.600	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV BANDEIRANTES-UBALDO RIVERA -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-30
249	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:45:00	480.250	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV BANDEIRANTES-UBALDO RIVERA -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-31
250	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:45:00	493.375	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV BANDEIRANTES-UBALDO RIVERA -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-32
251	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:46:00	500.100	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TV BANDEIRANTES-UBALDO RIVERA -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-33
252	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:47:00	642.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		RADIO PRINCESA FM -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-34
253	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:47:00	689.000	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		RADIO PRINCESA FM -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-35
254	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:50:00	663.500	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		SUCESSO FM-FABIO SILVA -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-36
255	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:50:00	682.200	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		SUCESSO FM-FABIO SILVA -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-37
256	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:52:00	616.780	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		LUZBEL - SILVIO JOSÉ PRADO/DANIEL SOUZA 71 9137-4112 -		Indefinido	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-38
257	3	\N	Campo Grande	Arildo, Elna, Muniz e Brasilio	2026-02-12	18:53:00	557.180	25.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		LUZBEL - SILVIO JOSÉ PRADO/DANIEL SOUZA 71 9137-4112 -		Indefinido	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-39
258	3	\N	Ondina	Elna, Muniz e Brasilio	2026-02-14	11:42:00	450.500	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		-		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-40
259	3	\N	Ondina	Elna, Muniz e Brasilio	2026-02-14	11:50:00	459.900	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		SOFT COMP CONERCIO SERVIÇOS  TELECOMUNICAÇÕES E INFORMÁTICA LTDA-ANDRE DIAS 71 99260-5095.OBS. ESSA FREQUENCIA FOI ALTERADA NO MONENTO DA FISCALIZAÇÃO PARA 459.0625 POR NÃO ESTAR AUTORIZADA. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-41
260	3	\N	Ondina	Elna, Muniz e Brasilio	2026-02-14	11:51:00	368.760	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		SOFT COMP COMÉRCIO SERVIÇOS  TELECOMUNICAÇÕES E INFORMÁTICA LTDA-ANDRE DIAS 71  99260-5095. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-42
261	3	\N	Ondina	Elna, Muniz e Brasilio	2026-02-14	11:52:00	368.610	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		SOFT COMP COMÉRCIO SERVIÇOS  TELECOMUNICAÇÕES E INFORMÁTICA LTDA-ANDRE DIAS 71  99260-5095. -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-43
262	3	\N	Ondina Apart Residência	Muniz,Brasilio e Elna	2026-02-13	12:03:00	459.940	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		ZIC ELETRÔNICA E COMUNICAÇÃO LTDA- CAMILA SANTOS 71 98846-7056.OBS Verificar ATO da Sitelco -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-44
263	3	\N	Barra/Ondina  Camarote Mar	Elna, Muniz e Brasilio	2026-02-14	12:10:00	459.000	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		DRM RADIOS EDSON LUCENA 81 99308-1072/DÊNIA 71 99202-0467 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-45
264	3	\N	Barra/Ondina  Camarote Baiano	Elna, Muniz e Brasilio	2026-02-14	12:13:00	161.330	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		Camarote Baiano- EDMILSON   DOS SANTOS BARBOSA SERVIÇOS LTDA/ RENAN SIMOES 71 99336-1494 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-46
265	3	\N	Barra/Ondina  Camarote Baiano	Elna, Muniz e Brasilio	2026-02-14	12:13:00	161.150	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		Camarote Baiano- EDMILSON   DOS SANTOS BARBOSA SERVIÇOS LTDA/ RENAN SIMOES 71 99336-1494 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-47
266	3	\N	Barra/Ondina  IFOOD	Elna, Muniz e Brasilio	2026-02-14	12:16:00	459.210	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		IFOOD - PATRICK SILVA 71 99953-0198 -		Indefinido	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-48
267	3	\N	Barra/Ondina  TRIO DRAGAO	Elna, Muniz e Brasilio	2026-02-14	12:21:00	476.380	200.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TRIO DRAGAO-CAIO VANZO  19 99844-1742 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-49
268	3	\N	Barra/Ondina  TRIO DRAGAO	Elna, Muniz e Brasilio	2026-02-14	12:21:00	658.580	80.000	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f		TRIO DRAGAO-CAIO VANZO  19 99844-1742 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-50
269	3	\N	Barra/Ondina  CAMAROTE CABANA DA BARRA	Elna, Muniz e Brasilio	2026-02-14	12:24:00	462.720	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		JAGUARACI OLIVEIRA  PASSOS- 71 98276-7675 -		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-51
270	3	\N	Barra/Ondina  CAMAROTE VIVA BAHIA	Elna, Muniz e Brasilio	2026-02-14	12:27:00	151.840	25.000	SLP	Comunicação (voz) relacionada ao evento	Não licenciável	f		LEGACY SEGURANÇA E SERVIÇOS LTDA- VERENA ARAUJO 71 99249-4801 - Freq. 151.835 MHz		Não	Pendente	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-52
271	3	\N	Barra/Ondina  CAMAROTE VIVA BAHIA	Elna, Muniz e Brasilio	2026-02-14	12:29:00	459.010	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		EDMILSON  DOS SANTOS BARBOSA SERVIÇOS LTDA - DARA FRANÇA(PRODUÇAO) 71 99357-9124 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-53
272	3	\N	Barra/Ondina  CAMAROTE VIVA BAHIA	Elna, Muniz e Brasilio	2026-02-14	12:30:00	459.110	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f		EDMILSON  DOS SANTOS BARBOSA SERVIÇOS LTDA - DARA FRANÇA(PRODUÇAO) 71 99357-9124 -		Não	Concluído	ABORDAGEM	2026-07-07 18:43:15.620995+00	2026-07-07 18:43:15.620995+00	Abo-54
273	3	4	ERMxBA02	Adriano	2026-02-13	13:30:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	1-ER02
274	3	4	ERMxBA02	Adriano	2026-02-13	13:30:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	2-ER02
275	3	4	ERMxBA02	Adriano	2026-02-13	14:30:00	\N	15.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	3-ER02
276	3	4	ERMxBA02	Adriano	2026-02-13	15:00:00	\N	15.000		Comunicação (voz) não relacionada ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	4-ER02
277	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	56.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	5-ER02
278	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	63.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	6-ER02
279	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	57.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	7-ER02
280	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	58.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	8-ER02
281	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	90.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	9-ER02
282	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	57.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	10-ER02
283	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	72.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	11-ER02
284	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	59.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	12-ER02
285	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	59.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	13-ER02
286	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	56.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	14-ER02
287	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	900.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	15-ER02
288	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	369.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	16-ER02
289	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	1380.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	17-ER02
290	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	260.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	18-ER02
291	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	269.880		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	19-ER02
292	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	847.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	20-ER02
293	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	275.500		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	21-ER02
294	3	4	ERMxBA02	Adriano	2026-02-14	15:00:00	\N	4600.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	22-ER02
295	3	4	ERMxBA02	Adriano	2026-02-17	12:30:00	\N	59.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	23-ER02
296	3	4	ERMxBA02	Adriano	2026-02-17	12:30:00	\N	59.000		Comunicação (voz) não relacionada ao evento	Sim	f	53500.003653/2026-13			Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	24-ER02
297	3	4	ERMxBA02	Adriano	2026-02-17	12:40:00	\N	59.000		Comunicação (voz) relacionada ao evento	Sim	f	53500.003653/2026-13			Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	25-ER02
298	3	4	ERMxBA02	Adriano	2026-02-17	14:00:00	\N	59.000		Comunicação (voz) relacionada ao evento	Sim	f	53500.002842/2026-79			Não	concluído	ESTACAO	2026-07-07 18:43:16.143465+00	2026-07-07 18:43:16.143465+00	26-ER02
299	3	5	RFeye002102	Wilton	2026-02-13	11:40:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	1-RF02
300	3	5	RFeye002102	Wilton	2026-02-13	12:04:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	2-RF02
301	3	5	RFeye002102	Wilton	2026-02-13	12:07:00	\N	25.000		Sinal de dados	Sim	t	53500.003330/2026-20			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	3-RF02
302	3	5	RFeye002102	Wilton	2026-02-13	14:37:00	\N	25.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	4-RF02
303	3	5	RFeye002102	Wilton	2026-02-13	14:56:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	5-RF02
304	3	5	RFeye002102	Wilton	2026-02-13	15:10:00	\N	25.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	6-RF02
305	3	5	RFeye002102	Wilton	2026-02-13	15:16:00	\N	100.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.003330/2026-20			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	7-RF02
306	3	5	RFeye002102	Wilton	2026-02-13	16:14:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	8-RF02
307	3	5	RFeye002102	Wilton	2026-02-13	17:30:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	9-RF02
308	3	5	RFeye002102	Wilton	2026-02-13	17:48:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	10-RF02
309	3	5	RFeye002102	Wilton	2026-02-13	18:54:00	\N	25.000		Comunicação (voz) relacionada ao evento		f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	11-RF02
310	3	5	RFeye002102	Wilton	2026-02-15	14:30:00	\N	3.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	12-RF02
311	3	5	RFeye002102	Wilton	2026-02-15	14:39:00	\N	12.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	13-RF02
312	3	5	RFeye002102	Wilton	2026-02-15	14:49:00	\N	3.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	14-RF02
313	3	5	RFeye002102	Wilton	2026-02-15	15:06:00	\N	50.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	15-RF02
314	3	5	RFeye002102	Wilton	2026-02-15	15:15:00	\N	44.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	16-RF02
315	3	5	RFeye002102	Wilton	2026-02-15	15:16:00	\N	32.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	17-RF02
316	3	5	RFeye002102	Wilton	2026-02-15	15:31:00	\N	1.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	18-RF02
317	3	5	RFeye002102	Wilton	2026-02-15	15:53:00	\N	40.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	19-RF02
318	3	5	RFeye002102	Wilton	2026-02-15	16:07:00	\N	25.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	20-RF02
319	3	5	RFeye002102	Wilton	2026-02-15	16:19:00	\N	15.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	21-RF02
320	3	5	RFeye002102	Wilton	2026-02-15	16:25:00	\N	15.000		Não identificado	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	22-RF02
321	3	5	RFeye002102	Wilton	2026-02-15	16:40:00	\N	10.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	23-RF02
322	3	5	RFeye002102	Wilton	2026-02-16	16:47:00	\N	35.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	24-RF02
323	3	5	RFeye002102	Wilton	2026-02-16	16:58:00	\N	40.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	25-RF02
324	3	5	RFeye002102	Wilton	2026-02-16	17:00:00	\N	35.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	26-RF02
325	3	5	RFeye002102	Wilton	2026-02-16	17:03:00	\N	40.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	27-RF02
326	3	5	RFeye002102	Wilton	2026-02-16	17:05:00	\N	58.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	28-RF02
327	3	5	RFeye002102	Wilton	2026-02-16	17:05:00	\N	35.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	29-RF02
328	3	5	RFeye002102	Wilton	2026-02-16	17:08:00	\N	40.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	30-RF02
329	3	5	RFeye002102	Wilton	2026-02-16	17:10:00	\N	38.000		Ruído	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	31-RF02
330	3	5	RFeye002102	Wilton	2026-02-16	17:15:00	\N	25.000		Sinal de dados	Sim	t	53500.004570/2026-41			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	32-RF02
331	3	5	RFeye002102	Wilton	2026-02-16	17:19:00	\N	25.000		Sinal de dados	Sim	t	53500.004570/2026-41			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	33-RF02
332	3	5	RFeye002102	Wilton	2026-02-16	17:20:00	\N	50.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	34-RF02
333	3	5	RFeye002102	Wilton	2026-02-16	17:25:00	\N	25.000		Sinal de dados	Sim	t	53500.004570/2026-41			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	35-RF02
334	3	5	RFeye002102	Wilton	2026-02-16	17:28:00	\N	25.000		Sinal de dados	Sim	t	53500.004570/2026-41			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	36-RF02
335	3	5	RFeye002102	Wilton	2026-02-16	17:32:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	37-RF02
336	3	5	RFeye002102	Wilton	2026-02-16	17:38:00	\N	25.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	38-RF02
337	3	5	RFeye002102	Wilton	2026-02-16	17:43:00	\N	45.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.003330/2026-20			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	39-RF02
338	3	5	RFeye002102	Wilton	2026-02-16	17:45:00	\N	50.000		Comunicação (voz) relacionada ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	40-RF02
339	3	5	RFeye002102	Wilton	2026-02-16	17:52:00	\N	100.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.006507/2026-40			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	41-RF02
340	3	5	RFeye002102	Wilton	2026-02-16	17:58:00	\N	25.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.003653/2026-13			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	42-RF02
341	3	5	RFeye002102	Wilton	2026-02-16	18:02:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	43-RF02
342	3	5	RFeye002102	Wilton	2026-02-16	18:13:00	\N	100.000		Comunicação (voz) relacionada ao evento	Não licenciável	f				Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	44-RF02
343	3	5	RFeye002102	Wilton	2026-02-16	18:17:00	\N	90.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.007294/2026-73			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	45-RF02
344	3	5	RFeye002102	Wilton	2026-02-17	12:28:00	\N	200.000		Comunicação (voz) relacionada ao evento	Sim	t	53500.007112/2026-64			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	46-RF02
345	3	5	RFeye002102	Wilton	2026-02-17	12:32:00	\N	25.000		Sinal de dados	Sim	t	53500.006132/2026-18			Não	concluído	ESTACAO	2026-07-07 18:43:16.650754+00	2026-07-07 18:43:16.650754+00	47-RF02
346	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	21:52:00	450.500	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-01
347	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	21:53:00	452.100	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-02
348	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	21:59:00	475.500	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-03
349	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	21:59:00	487.000	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-04
350	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:01:00	501.250	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-05
351	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:01:00	503.375	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-06
352	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:06:00	530.275	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-07
353	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:07:00	627.725	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-08
354	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:08:00	618.750	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-09
355	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:08:00	620.275	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-10
356	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:09:00	624.750	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-11
357	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:09:00	629.375	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-12
358	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:10:00	632.175	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se microfone sem fio. Total de 20 (vinte) microfones.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-13
359	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:15:00	547.300	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de transmissor base usado para comunicação com receptores (retorno).\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-14
360	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:17:00	556.400	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de transmissor base usado para comunicação com receptores (retorno). Feito o ajuste da BW de 160 KHz para 100 KHz no ato da conferência espectral.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-15
361	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:18:00	558.100	100.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de transmissor base usado para comunicação com receptores (retorno). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-16
362	4	\N	Sambódromo do Anhembi, São Paulo/SP	Wellington Devechi e Ricardo Marques	2026-02-12	22:18:00	560.300	100.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005113/2026-74	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de transmissor base usado para comunicação com receptores (retorno). \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-17
363	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:23:00	474.675	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-18
364	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:24:00	479.575	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-19
365	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:24:00	480.700	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-20
366	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:25:00	485.675	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-21
367	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:25:00	486.125	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-22
368	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:26:00	487.575	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-23
369	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:26:00	489.225	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-24
370	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:27:00	490.150	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-25
371	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:28:00	491.300	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-26
372	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:28:00	491.750	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-27
373	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:29:00	506.700	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-28
374	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:29:00	508.025	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio. \n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-29
375	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:34:00	456.600	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-30
376	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:34:00	453.300	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-31
377	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:35:00	462.475	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-32
378	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:35:00	468.275	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-33
379	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:35:00	469.775	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-34
380	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:38:00	460.475	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.003339/2026-31	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de estação repetidora para uso com HTs. Total de 6 (seis) repetidoras.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-35
381	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:47:00	482.800	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-36
382	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:47:00	484.000	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-37
383	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:47:00	486.400	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-38
384	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:50:00	487.000	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-39
385	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:50:00	503.200	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-40
386	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	22:51:00	505.000	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de microfone sem fio.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-41
387	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-12	23:03:00	\N	\N	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.007182/2026-12	Rádio e Televisão Bandeirantes S.A. / Jean Pierre (jeanpierre@band.com.br) e Guilherme Boscolo / trata-se de transceptor de radiação restrita acoplado em câmera sem fio. Homologação 04330-24-12261.\n -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-42
388	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:53:00	475.250	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-43
389	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:57:00	486.130	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio. Compartilhada com a Band (Ato UTE 1783). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-44
390	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:58:00	488.230	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-45
391	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:58:00	493.250	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-46
392	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:58:00	517.880	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-47
393	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	16:59:00	539.130	192.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-48
394	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	17:00:00	625.500	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-49
395	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano e Mario Volpini	2026-02-13	17:00:00	625.500	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006799/2026-11	TV Ômega LTDA - Rede TV / Cristiano Gomes Cristal (ccristal@redetv.com.br) / Equipamentos testados referem-se a microfones sem fio.  -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-50
396	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:18:00	381.050	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-51
397	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:18:00	381.100	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-52
398	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:19:00	381.150	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-53
399	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:19:00	381.200	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-54
400	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:20:00	381.250	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-55
401	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:20:00	381.300	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-56
402	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:20:00	381.350	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-57
403	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:20:00	381.400	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-58
404	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:20:00	381.450	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-59
478	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	33.400		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	33-RF27
479	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	42.500		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	34-RF27
405	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:21:00	381.500	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-60
406	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:21:00	381.600	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-61
407	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:21:00	381.650	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-62
408	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:24:00	381.700	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-63
409	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:24:00	381.750	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-64
410	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:26:00	391.050	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-65
411	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:27:00	391.100	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-66
412	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:27:00	391.150	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-67
413	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:27:00	391.200	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-68
414	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:27:00	391.250	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-69
415	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:27:00	391.300	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-70
416	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:28:00	391.350	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-71
417	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:28:00	391.400	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-72
418	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:28:00	391.450	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-73
419	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:28:00	391.500	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-74
420	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:28:00	391.600	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-75
421	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:29:00	391.650	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-76
422	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:29:00	391.700	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-77
423	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:29:00	391.750	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de transceptores HT e estações Base que se comunicam entre si e com estações repetidoras. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-78
424	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Devechi e Marques	2026-02-13	21:30:00	382.200	25.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.005028/2026-14	SISCOM Telecomunicações LTDA / Rodrigo Finoti (rodrigo.finoti@siscomnet.com.br). Trata-se de estações Base. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-79
425	4	\N	Sambódromo do Anhembi	Mario, Devechi e Marques	2026-02-13	22:07:00	\N	\N	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006798/2026-76	Globo / Bruno Campos (bruno.mendonca@g.globo). Trata-se de câmeras sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-80
426	4	\N	Sambódromo do Anhembi	Mario, Devechi e Marques	2026-02-13	22:08:00	\N	\N	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006798/2026-76	Globo / Bruno Campos (bruno.mendonca@g.globo). Trata-se de câmeras sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-81
427	4	\N	Sambódromo do Anhembi	Mario, Devechi e Marques	2026-02-13	22:08:00	\N	\N	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.006798/2026-76	Globo / Bruno Campos (bruno.mendonca@g.globo). Trata-se de câmeras sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-82
428	4	\N	Sambódromo do Anhembi	Mario, Devechi e Marques	2026-02-13	22:13:00	\N	\N	SLP	Comunicação (voz) relacionada ao evento	Indefinido	f	Licença para Funcionamento de Estação nº 1015790175	Globo / Bruno Campos (bruno.mendonca@g.globo). Trata-se de Estação 4G-LTE utilizado pela Licença nº 1015790175 – Limitado Privado (rede corporativa). Tecnologia TDD. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-83
429	4	\N	Sambódromo do Anhembi	Mario, Devechi e Marques	2026-02-13	22:16:00	\N	\N	Radiação Restrita	Comunicação (voz) relacionada ao evento	Indefinido	f	Radiação Restrita	Globo / Bruno Campos (bruno.mendonca@g.globo). Trata-se de sistema de Comunicação de Estúdio – Fabricante Riedel Modelo Bolero (radiação restrita), homologação 05749-17-10493. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-84
430	4	\N	Sambódromo do Anhembi - São Paulo SP	Mario e Devechi	2026-02-14	21:06:00	582.700	125.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500006798/2026-76	Globo / Bruno Mendonça Campos / bruno.mendonca@g.globo. Trata-se de microfone sem fio (retorno para ponto eletrônico). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-85
431	4	\N	Sambódromo do Anhembi - São Paulo SP	Mario e Devechi	2026-02-14	21:07:00	553.600	125.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500006798/2026-76	Globo / Bruno Mendonça Campos / bruno.mendonca@g.globo. Trata-se de microfone sem fio (retorno para ponto eletrônico) utilizado na concentração. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-86
432	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:14:00	610.180	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-87
433	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:15:00	609.250	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-88
434	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:15:00	608.180	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-89
435	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:15:00	608.830	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-90
436	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:16:00	614.150	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-91
437	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:17:00	626.030	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-92
438	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:17:00	566.150	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-93
439	4	\N	Sambódromo do Anhembi, São Paulo/SP	Marcos Juliano, Devechi e Mario Volpini	2026-02-14	23:18:00	590.150	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a microfone sem fio. -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-94
440	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:27:00	611.180	800.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Transmissor Shure – modelo ADTQ (800 KHz BW). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-95
441	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:27:00	613.550	800.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Transmissor Shure – modelo ADTQ (800 KHz BW). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-96
442	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:29:00	500.380	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Shure – modelo ADX1 (utilizado na captação e transmissão de som da bateria das escolas). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-97
443	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:30:00	500.730	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Shure – modelo ADX1 (utilizado na captação e transmissão de som da bateria das escolas). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-98
444	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:30:00	501.530	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Shure – modelo ADX1 (utilizado na captação e transmissão de som da bateria das escolas). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-99
445	4	\N	Sambódromo do Anhembi - São Paulo	Mario Volpini, Marcos Juliano e Devechi	2026-02-14	23:30:00	502.000	200.000	SLP	Comunicação (voz) relacionada ao evento	Indefinido	t	53500.107717/2025-73	Tukason / Lucas Lemos Gondim - email: rf@engenhodaarte.com. Refere-se a transmissor Shure – modelo ADX1 (utilizado na captação e transmissão de som da bateria das escolas). -		Não	Concluído	ABORDAGEM	2026-07-07 18:47:10.445964+00	2026-07-07 18:47:10.445964+00	Abo-100
446	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	171.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	1-RF27
447	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	159.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	2-RF27
448	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	132.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	3-RF27
449	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	139.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	4-RF27
450	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	86.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	5-RF27
451	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	126.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	6-RF27
452	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	7-RF27
453	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	86.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	8-RF27
454	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	208.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	9-RF27
455	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	210.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	10-RF27
456	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	126.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	11-RF27
457	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	81.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	12-RF27
458	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	146.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	13-RF27
459	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	162.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	14-RF27
460	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	47.200		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	15-RF27
461	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	43.100		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	16-RF27
462	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	58.900		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	17-RF27
463	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	43.900		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	18-RF27
464	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	39.800		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	19-RF27
465	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	41.200		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	20-RF27
466	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	38.100		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	21-RF27
467	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	32.600		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	22-RF27
468	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	57.500		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	23-RF27
469	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	67.900		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	24-RF27
470	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	39.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	25-RF27
471	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	34.400		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	26-RF27
472	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	50.700		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	27-RF27
473	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	39.600		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	28-RF27
474	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	62.700		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	29-RF27
475	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	48.300		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	30-RF27
476	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	53.200		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	31-RF27
477	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	40.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	32-RF27
480	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	42.100		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	35-RF27
481	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5675.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	36-RF27
482	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5645.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	37-RF27
483	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5114.600		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	38-RF27
484	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5601.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	39-RF27
485	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5619.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	40-RF27
486	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5621.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	41-RF27
487	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	4814.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	42-RF27
488	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5616.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	43-RF27
489	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5647.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	44-RF27
490	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5632.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	45-RF27
491	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5624.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	46-RF27
492	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5645.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	47-RF27
493	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5162.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	48-RF27
494	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5640.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	49-RF27
495	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5623.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	50-RF27
496	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5619.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	51-RF27
497	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5640.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	52-RF27
498	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5615.200		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	53-RF27
499	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5624.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	54-RF27
500	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	4521.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	55-RF27
501	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5550.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	56-RF27
502	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5632.200		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	57-RF27
503	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5630.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	58-RF27
504	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5638.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	59-RF27
505	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5625.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	60-RF27
506	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5621.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	61-RF27
507	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5648.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	62-RF27
508	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5635.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	63-RF27
509	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5608.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	64-RF27
510	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9152.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	65-RF27
511	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9367.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	66-RF27
512	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5438.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	67-RF27
513	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	6789.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	68-RF27
514	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	5582.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	69-RF27
515	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	4068.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	70-RF27
516	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	3995.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	71-RF27
517	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	4495.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	72-RF27
518	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	4513.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	73-RF27
519	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	13609.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	74-RF27
520	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	15145.100		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	75-RF27
521	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	15229.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	76-RF27
522	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9137.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	77-RF27
523	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	18165.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	78-RF27
524	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	13660.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	79-RF27
525	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	18179.000		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	80-RF27
526	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	10130.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	81-RF27
527	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	13675.200		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	82-RF27
528	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9198.600		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	83-RF27
529	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	8899.200		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	84-RF27
530	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	8807.400		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	85-RF27
531	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9357.700		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	86-RF27
532	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	1651.400		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	87-RF27
533	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	37798.100		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	88-RF27
534	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	9152.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	89-RF27
535	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	18156.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	90-RF27
536	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	18166.600		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	91-RF27
537	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	18168.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	92-RF27
538	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	98348.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	93-RF27
539	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	98321.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	94-RF27
540	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	98344.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	95-RF27
541	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	96-RF27
542	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	97-RF27
543	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	98-RF27
544	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	71.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	99-RF27
545	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	100-RF27
546	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	101-RF27
547	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	68.700		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	102-RF27
548	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	103-RF27
549	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	104-RF27
550	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	105-RF27
551	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	106-RF27
552	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	107-RF27
553	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	70.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	108-RF27
554	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	109-RF27
555	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	110-RF27
556	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	111-RF27
557	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	112-RF27
558	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	113-RF27
559	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	114-RF27
560	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	115-RF27
561	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	116-RF27
562	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	70.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	117-RF27
563	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	118-RF27
564	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	119-RF27
565	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.700		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	120-RF27
566	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	121-RF27
567	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	122-RF27
568	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	123-RF27
569	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	124-RF27
570	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	71.700		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	125-RF27
571	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	71.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	126-RF27
572	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	85.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	127-RF27
573	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	128-RF27
574	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	129-RF27
575	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	130-RF27
576	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	131-RF27
577	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	70.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	132-RF27
578	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	133-RF27
579	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	134-RF27
580	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	79.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	135-RF27
581	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	136-RF27
582	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	137-RF27
583	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	138-RF27
584	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	139-RF27
585	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	140-RF27
586	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	141-RF27
587	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	142-RF27
588	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	143-RF27
589	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	84.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	144-RF27
590	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	145-RF27
591	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	146-RF27
592	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	147-RF27
593	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	148-RF27
594	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	149-RF27
595	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	150-RF27
596	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.700		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	151-RF27
597	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	152-RF27
598	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	153-RF27
599	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	154-RF27
600	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	155-RF27
601	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	156-RF27
602	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	157-RF27
603	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	158-RF27
604	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.700		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	159-RF27
605	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	160-RF27
606	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	161-RF27
607	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	162-RF27
608	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	163-RF27
609	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	72.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	164-RF27
610	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	165-RF27
611	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	81.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	166-RF27
612	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	167-RF27
613	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	168-RF27
614	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	169-RF27
615	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	170-RF27
616	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	171-RF27
617	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	172-RF27
618	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	173-RF27
619	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	174-RF27
620	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	175-RF27
621	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	176-RF27
622	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.600		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	177-RF27
623	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	178-RF27
624	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	82.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	179-RF27
625	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	180-RF27
626	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	181-RF27
627	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	182-RF27
628	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.800		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	183-RF27
629	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.200		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	184-RF27
630	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	185-RF27
631	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	78.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	186-RF27
632	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	187-RF27
633	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.900		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	188-RF27
634	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	80.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	189-RF27
635	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	74.300		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	190-RF27
636	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	191-RF27
637	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	73.100		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	192-RF27
638	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	76.000		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	193-RF27
639	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	75.500		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	194-RF27
640	4	8	RFeye002227	Arthur	2026-02-03	18:30:00	\N	77.400		Espúrio ou Produto de Intermodulação	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	195-RF27
641	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	47.300		Sinal não relacionado ao evento	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	196-RF27
642	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	39.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	197-RF27
643	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	45.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	198-RF27
644	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	49.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	199-RF27
645	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	43.400		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	200-RF27
646	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	57.800		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	201-RF27
647	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	38.900		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	202-RF27
648	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	60.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	203-RF27
649	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	5616.300		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	204-RF27
650	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	5597.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	205-RF27
651	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	5611.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	206-RF27
652	4	8	RFeye002227	Arthur	2026-02-07	01:00:00	\N	5605.200		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	207-RF27
653	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	118.350		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	208-RF27
654	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	120.450		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	209-RF27
655	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	129.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	210-RF27
656	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	131.550		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	211-RF27
657	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	133.850		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	212-RF27
658	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	134.900		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	213-RF27
659	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	392.625		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	214-RF27
660	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	393.425		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	215-RF27
661	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	393.700		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	216-RF27
662	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	394.275		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	217-RF27
663	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	394.500		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	218-RF27
664	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	450.050		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	219-RF27
665	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	469.100		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	220-RF27
666	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	14000.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	221-RF27
667	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	1835.000		Sinal não relacionado ao evento	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	222-RF27
668	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	2310.075		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	223-RF27
669	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	5622.000		Sinal de dados	Sim	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	224-RF27
670	4	8	RFeye002227	Arthur	2026-02-12	01:00:00	\N	5646.000		Sinal de dados	Não	f				Não	concluído	ESTACAO	2026-07-07 18:47:11.56322+00	2026-07-07 18:47:11.56322+00	225-RF27
671	1	\N	Ingá	André Testando o Postgres	2026-07-14	10:55:00	123.000	122.000	FM	Comunicação não relacionada ao evento		f	2222222222222	Teste - 	\N	Sim	Pendente	ABORDAGEM	2026-07-14 14:05:32.403468+00	2026-07-14 14:05:32.403468+00	\N
674	1	\N	NIteroi	André Teste postgres	2026-07-14	10:55:00	123.000	123.000	FM	Comunicação não relacionada ao evento		f	zzzzzzzzzzzzzzzzzzz	zzzzzzzzzzzzzzzzzzzzz - 	\N	Sim	Pendente	ABORDAGEM	2026-07-14 14:30:23.855919+00	2026-07-14 14:30:23.855919+00	\N
675	1	\N	NIteroi	André Teste postgres	2026-07-14	10:55:00	123.000	123.000	FM	Comunicação não relacionada ao evento		f	zzzzzzzzzzzzzzzzzzz	zzzzzzzzzzzzzzzzzzzzz - 	\N	Sim	Pendente	ABORDAGEM	2026-07-14 14:30:23.862021+00	2026-07-14 14:30:23.862021+00	\N
676	1	\N	assdasfdf	André teste pos	2026-07-14	15:33:00	1212.000	1212.000	FM	Comunicação não relacionada ao evento	Indefinido	f	12121212	121221 - 	\N	Sim	Pendente	ABORDAGEM	2026-07-14 18:35:00.57105+00	2026-07-14 18:35:00.57105+00	\N
\.


--
-- Data for Name: opcoes_identificacao; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.opcoes_identificacao (id, evento_id, valor) FROM stdin;
1	1	Sinal de dados
2	1	Comunicação relacionada ao evento
3	1	Comunicação não relacionada ao evento
4	1	Espúrio ou Produto de Intermodulação
5	1	Ruído
6	1	Não identificado
7	2	Sinal de dados
8	2	Comunicação (voz) relacionada ao evento
9	2	Comunicação (voz) não relacionada ao evento
10	2	Sinal não relacionado ao evento
11	2	Espúrio ou Produto de Intermodulação
12	2	Ruído
13	3	Sinal de dados
14	3	Comunicação (voz) relacionada ao evento
15	3	Comunicação (voz) não relacionada ao evento
16	3	Sinal não relacionado ao evento
17	3	Espúrio ou Produto de Intermodulação
18	3	Ruído
19	4	Sinal de dados
20	4	Comunicação (voz) relacionada ao evento
21	4	Comunicação (voz) não relacionada ao evento
22	4	Sinal não relacionado ao evento
23	4	Espúrio ou Produto de Intermodulação
24	4	Ruído
\.


--
-- Data for Name: tabela_ute; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tabela_ute (id, evento_id, pais_entidade, local, frequencia_mhz, processo_sei, id_planilha) FROM stdin;
1	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	440.500	53500.010566/2026-12	\N
2	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	441.306	53500.010824/2026-61	\N
3	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	442.106	53500.010824/2026-61	\N
4	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	443.106	53500.010824/2026-61	\N
5	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	443.462	53500.010824/2026-61	\N
6	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	443.831	53500.010824/2026-61	\N
7	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	445.525	53500.010824/2026-61	\N
8	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.031	53500.010824/2026-61	\N
9	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.044	53500.010824/2026-61	\N
10	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.056	53500.010824/2026-61	\N
11	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.081	53500.010824/2026-61	\N
12	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.500	53500.010824/2026-61	\N
13	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	446.762	53500.010824/2026-61	\N
14	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	447.637	53500.010824/2026-61	\N
15	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	447.962	53500.010824/2026-61	\N
16	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.150	53500.010566/2026-12	\N
17	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.188	53500.010566/2026-12	\N
18	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.212	53500.010566/2026-12	\N
19	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.262	53500.010566/2026-12	\N
20	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.325	53500.010566/2026-12	\N
21	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.375	53500.010566/2026-12	\N
22	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.400	53500.010566/2026-12	\N
23	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	450.425	53500.010566/2026-12	\N
24	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	450.500	53500.019775/2026-21	\N
25	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	450.500	53500.019775/2026-21	\N
26	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	451.150	53500.019775/2026-21	\N
27	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	451.150	53500.019775/2026-21	\N
28	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	452.300	53500.010530/2026-39	\N
29	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	452.300	53500.011761/2026-60	\N
30	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	453.200	53500.010824/2026-61	\N
31	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	453.200	53500.011761/2026-60	\N
32	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	453.350	53500.010530/2026-39	\N
33	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	453.350	53500.011761/2026-60	\N
34	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.325	53500.010566/2026-12	\N
35	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.400	53500.010530/2026-39	\N
36	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.400	53500.011761/2026-60	\N
37	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.450	53500.010530/2026-39	\N
38	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.450	53500.011761/2026-60	\N
39	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.500	53500.010530/2026-39	\N
40	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.500	53500.011761/2026-60	\N
41	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.550	53500.010530/2026-39	\N
42	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.550	53500.011761/2026-60	\N
43	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.613	53500.010824/2026-61	\N
44	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	454.950	53500.010824/2026-61	\N
45	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.150	53500.010530/2026-39	\N
46	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.150	53500.011761/2026-60	\N
47	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.200	53500.010530/2026-39	\N
48	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.200	53500.011761/2026-60	\N
49	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.250	53500.010530/2026-39	\N
50	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.250	53500.011761/2026-60	\N
51	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.281	53500.010824/2026-61	\N
52	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.300	53500.011761/2026-60	\N
53	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.381	53500.010824/2026-61	\N
54	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	455.800	53500.010824/2026-61	\N
55	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.000	53500.010824/2026-61	\N
56	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.044	53500.010566/2026-12	\N
57	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.175	53500.010824/2026-61	\N
58	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.200	53500.010824/2026-61	\N
59	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.269	53500.010566/2026-12	\N
60	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.350	53500.010530/2026-39	\N
61	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.350	53500.011761/2026-60	\N
62	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.450	53500.010530/2026-39	\N
63	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	456.600	53500.019775/2026-21	\N
64	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	456.600	53500.019775/2026-21	\N
65	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.850	53500.010530/2026-39	\N
66	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.850	53500.011761/2026-60	\N
67	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	456.900	53500.010530/2026-39	\N
68	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.150	53500.010530/2026-39	\N
69	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.150	53500.011761/2026-60	\N
70	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.150	53500.011761/2026-60	\N
71	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.250	53500.010530/2026-39	\N
72	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.250	53500.011761/2026-60	\N
73	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.450	53500.010530/2026-39	\N
74	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.450	53500.011761/2026-60	\N
75	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	457.650	53500.010530/2026-39	\N
76	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.100	53500.010530/2026-39	\N
77	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.100	53500.011761/2026-60	\N
78	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.137	53500.010530/2026-39	\N
79	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.137	53500.011761/2026-60	\N
80	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.238	53500.010530/2026-39	\N
81	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.238	53500.011761/2026-60	\N
82	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.312	53500.010530/2026-39	\N
83	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.312	53500.011761/2026-60	\N
84	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.688	53500.010824/2026-61	\N
85	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	458.856	53500.010566/2026-12	\N
86	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	459.113	53500.010824/2026-61	\N
87	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	459.275	53500.010566/2026-12	\N
88	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	459.500	53500.010566/2026-12	\N
89	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.150	53500.010566/2026-12	\N
90	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.188	53500.010566/2026-12	\N
91	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.212	53500.010566/2026-12	\N
92	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.262	53500.010566/2026-12	\N
93	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.325	53500.010566/2026-12	\N
94	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.375	53500.010566/2026-12	\N
95	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.400	53500.010566/2026-12	\N
96	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	460.425	53500.010566/2026-12	\N
97	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	460.475	53500.019775/2026-21	\N
98	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	460.475	53500.019775/2026-21	\N
99	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	462.100	53500.010824/2026-61	\N
100	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	462.150	53500.010530/2026-39	\N
101	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	462.150	53500.011761/2026-60	\N
102	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	462.200	53500.010530/2026-39	\N
103	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	462.200	53500.011761/2026-60	\N
104	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	462.475	53500.019775/2026-21	\N
105	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	462.475	53500.019775/2026-21	\N
106	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.150	53500.010530/2026-39	\N
107	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.150	53500.011761/2026-60	\N
108	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.200	53500.010824/2026-61	\N
109	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.200	53500.011761/2026-60	\N
110	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.706	53500.010824/2026-61	\N
111	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.762	53500.010824/2026-61	\N
112	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	463.925	53500.010824/2026-61	\N
113	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.100	53500.010530/2026-39	\N
114	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.100	53500.011761/2026-60	\N
115	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.200	53500.010530/2026-39	\N
116	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.200	53500.011761/2026-60	\N
117	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.262	53500.010824/2026-61	\N
118	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.325	53500.010530/2026-39	\N
119	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.425	53500.010824/2026-61	\N
120	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.613	53500.010824/2026-61	\N
121	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.644	53500.010824/2026-61	\N
122	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	464.913	53500.010824/2026-61	\N
123	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.100	53500.010530/2026-39	\N
124	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.100	53500.011761/2026-60	\N
125	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.150	53500.010530/2026-39	\N
126	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.150	53500.011761/2026-60	\N
127	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.200	53500.010530/2026-39	\N
128	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.200	53500.011761/2026-60	\N
129	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.438	53500.010824/2026-61	\N
130	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	465.988	53500.010824/2026-61	\N
131	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.200	53500.010530/2026-39	\N
132	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.200	53500.011761/2026-60	\N
133	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.250	53500.010530/2026-39	\N
134	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.250	53500.011761/2026-60	\N
135	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.300	53500.010530/2026-39	\N
136	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.300	53500.011761/2026-60	\N
137	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.350	53500.010530/2026-39	\N
138	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.350	53500.011761/2026-60	\N
139	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	466.750	53500.010824/2026-61	\N
140	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	467.000	53500.010824/2026-61	\N
141	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	467.137	53500.010824/2026-61	\N
142	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	467.150	53500.011761/2026-60	\N
143	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	467.650	53500.010530/2026-39	\N
144	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.137	53500.010530/2026-39	\N
145	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.137	53500.011761/2026-60	\N
146	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.238	53500.010530/2026-39	\N
147	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.238	53500.011761/2026-60	\N
148	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.312	53500.010530/2026-39	\N
149	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.312	53500.011761/2026-60	\N
150	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.413	53500.010566/2026-12	\N
151	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.644	53500.010566/2026-12	\N
152	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	468.875	53500.010824/2026-61	\N
153	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	469.850	53500.010824/2026-61	\N
154	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	470.000	53500.010566/2026-12	\N
155	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	470.200	53500.019775/2026-21	\N
156	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	475.375	53500.019775/2026-21	\N
157	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	476.000	53500.010566/2026-12	\N
158	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	482.000	53500.010857/2026-19	\N
159	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	486.125	53500.019775/2026-21	\N
160	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	488.000	53500.010857/2026-19	\N
161	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	492.100	53500.019775/2026-21	\N
162	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	494.000	53500.010857/2026-19	\N
163	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	498.250	53500.019775/2026-21	\N
164	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	500.000	53500.010566/2026-12	\N
165	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	500.375	53500.010566/2026-12	\N
166	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	500.775	53500.010566/2026-12	\N
167	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	501.200	53500.010566/2026-12	\N
168	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	501.600	53500.010566/2026-12	\N
169	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	502.050	53500.010566/2026-12	\N
170	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	502.400	53500.010566/2026-12	\N
171	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	502.825	53500.010566/2026-12	\N
172	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	503.200	53500.010566/2026-12	\N
173	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	503.625	53500.010566/2026-12	\N
174	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	504.100	53500.010566/2026-12	\N
175	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	504.475	53500.010566/2026-12	\N
176	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	505.000	53500.010566/2026-12	\N
177	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	505.425	53500.010566/2026-12	\N
178	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	505.800	53500.010566/2026-12	\N
179	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	510.500	53500.019775/2026-21	\N
180	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	512.000	53500.010857/2026-19	\N
181	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	515.125	53500.019775/2026-21	\N
182	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	518.000	53500.010857/2026-19	\N
183	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	520.225	53500.019775/2026-21	\N
184	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	521.350	53500.019775/2026-21	\N
185	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	523.100	53500.019775/2026-21	\N
186	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	524.000	53500.010566/2026-12	\N
187	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	524.425	53500.010566/2026-12	\N
188	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	524.800	53500.010566/2026-12	\N
189	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	525.250	53500.010566/2026-12	\N
190	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	525.650	53500.010566/2026-12	\N
191	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	526.075	53500.010566/2026-12	\N
192	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	526.450	53500.010566/2026-12	\N
193	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	526.850	53500.010566/2026-12	\N
194	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	527.300	53500.010566/2026-12	\N
195	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	527.650	53500.010566/2026-12	\N
196	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	528.100	53500.010566/2026-12	\N
197	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	529.000	53500.010857/2026-19	\N
198	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	529.425	53500.010857/2026-19	\N
199	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	529.800	53500.010857/2026-19	\N
200	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	530.225	53500.010857/2026-19	\N
201	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	535.400	53500.010857/2026-19	\N
202	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	535.850	53500.010857/2026-19	\N
203	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	542.150	53500.010857/2026-19	\N
204	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	542.525	53500.010857/2026-19	\N
205	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	543.150	53500.010857/2026-19	\N
206	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	546.800	53500.010857/2026-19	\N
207	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	548.125	53500.010857/2026-19	\N
208	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	548.950	53500.010857/2026-19	\N
607	2	BMX	Santo Cristo	593.000	53500.110707/2025-15	\N
209	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	549.375	53500.010857/2026-19	\N
210	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	549.800	53500.010857/2026-19	\N
211	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	550.225	53500.010857/2026-19	\N
212	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	550.650	53500.010857/2026-19	\N
213	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	560.000	53500.010857/2026-19	\N
214	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	584.200	53500.010857/2026-19	\N
215	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	584.625	53500.010857/2026-19	\N
216	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	585.250	53500.010857/2026-19	\N
217	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	585.650	53500.010857/2026-19	\N
218	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	586.100	53500.010857/2026-19	\N
219	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	586.475	53500.010857/2026-19	\N
220	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	586.950	53500.010857/2026-19	\N
221	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	587.350	53500.010857/2026-19	\N
222	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	588.925	53500.010857/2026-19	\N
223	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	589.375	53500.010857/2026-19	\N
224	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	589.800	53500.010857/2026-19	\N
225	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	595.900	53500.010857/2026-19	\N
226	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	601.925	53500.010857/2026-19	\N
227	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	607.550	53500.010857/2026-19	\N
228	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	613.975	53500.010857/2026-19	\N
229	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	620.000	53500.010857/2026-19	\N
230	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	632.000	53500.010566/2026-12	\N
231	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	632.375	53500.010566/2026-12	\N
232	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	632.800	53500.010566/2026-12	\N
233	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	633.250	53500.010566/2026-12	\N
234	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	633.625	53500.010566/2026-12	\N
235	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	634.025	53500.010566/2026-12	\N
236	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	634.425	53500.010566/2026-12	\N
237	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	634.850	53500.010566/2026-12	\N
238	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	635.250	53500.010566/2026-12	\N
239	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	635.625	53500.010566/2026-12	\N
240	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	636.100	53500.010566/2026-12	\N
241	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	636.525	53500.010566/2026-12	\N
242	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	636.925	53500.010566/2026-12	\N
243	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	637.350	53500.010566/2026-12	\N
244	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	637.700	53500.010566/2026-12	\N
245	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	643.900	53500.010857/2026-19	\N
246	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	650.000	53500.010566/2026-12	\N
247	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	650.450	53500.010566/2026-12	\N
248	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	650.825	53500.010566/2026-12	\N
249	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	651.250	53500.010566/2026-12	\N
250	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	651.650	53500.010566/2026-12	\N
251	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	652.000	53500.010566/2026-12	\N
252	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	652.425	53500.010566/2026-12	\N
253	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	652.825	53500.010566/2026-12	\N
254	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	653.200	53500.010566/2026-12	\N
255	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	654.000	53500.010857/2026-19	\N
256	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	654.875	53500.010857/2026-19	\N
257	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	655.250	53500.010857/2026-19	\N
258	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	655.675	53500.010857/2026-19	\N
259	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	692.200	53500.010857/2026-19	\N
260	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	692.750	53500.010857/2026-19	\N
261	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	693.175	53500.010857/2026-19	\N
262	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	693.600	53500.010857/2026-19	\N
263	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	694.700	53500.010857/2026-19	\N
264	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	695.125	53500.010857/2026-19	\N
265	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	695.500	53500.010857/2026-19	\N
266	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	699.425	53500.010857/2026-19	\N
267	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	700.475	53500.010857/2026-19	\N
268	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	700.475	53500.010857/2026-19	\N
269	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	700.850	53500.010857/2026-19	\N
270	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	701.325	53500.010857/2026-19	\N
271	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	701.750	53500.010857/2026-19	\N
272	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	704.000	53500.010857/2026-19	\N
273	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	705.325	53500.010857/2026-19	\N
274	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	705.750	53500.010857/2026-19	\N
275	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	706.625	53500.010857/2026-19	\N
276	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	707.100	53500.010857/2026-19	\N
277	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	707.525	53500.010857/2026-19	\N
278	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	708.000	53500.010857/2026-19	\N
279	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	708.450	53500.010857/2026-19	\N
280	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	740.550	53500.010857/2026-19	\N
281	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	741.000	53500.010857/2026-19	\N
282	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	741.575	53500.010857/2026-19	\N
283	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	921.500	53500.010566/2026-12	\N
284	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	1890.000	53500.010566/2026-12	\N
285	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2010.000	53500.010566/2026-12	\N
286	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2020.000	53500.010566/2026-12	\N
287	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2030.000	53500.010566/2026-12	\N
288	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2040.000	53500.010566/2026-12	\N
289	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2050.000	53500.010566/2026-12	\N
290	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2060.000	53500.010566/2026-12	\N
291	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2070.000	53500.010566/2026-12	\N
292	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2080.000	53500.010566/2026-12	\N
293	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	2082.250	53500.019775/2026-21	\N
294	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	2090.000	53500.019775/2026-21	\N
295	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2105.000	53500.010566/2026-12	\N
296	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2205.000	53500.010566/2026-12	\N
297	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2215.000	53500.010566/2026-12	\N
298	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2225.000	53500.010566/2026-12	\N
299	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2235.000	53500.010566/2026-12	\N
300	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2245.000	53500.010566/2026-12	\N
301	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2255.000	53500.010566/2026-12	\N
302	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2265.000	53500.010566/2026-12	\N
303	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2275.000	53500.010566/2026-12	\N
304	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2285.000	53500.010566/2026-12	\N
305	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2295.000	53500.010566/2026-12	\N
306	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	2445.000	53500.019775/2026-21	\N
307	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	2445.150	53500.010566/2026-12	\N
308	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	2461.000	53500.019775/2026-21	\N
309	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5300.000	53500.019775/2026-21	\N
310	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	5380.000	53500.010566/2026-12	\N
311	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5510.000	53500.019775/2026-21	\N
312	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5670.000	53500.019775/2026-21	\N
313	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5700.000	53500.019775/2026-21	\N
314	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5770.000	53500.019775/2026-21	\N
315	1	Rádio e Televisão Bandeirantes	Vila Santa Maria - Conjunto Caiçara	5786.000	53500.019775/2026-21	\N
316	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7105.000	53500.010566/2026-12	\N
317	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7115.000	53500.010566/2026-12	\N
318	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7125.000	53500.010566/2026-12	\N
319	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7135.000	53500.010566/2026-12	\N
320	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7145.000	53500.010566/2026-12	\N
321	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7180.000	53500.010566/2026-12	\N
322	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7195.000	53500.010566/2026-12	\N
323	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7245.000	53500.010566/2026-12	\N
324	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7260.000	53500.010566/2026-12	\N
325	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7275.000	53500.010566/2026-12	\N
326	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7290.000	53500.010566/2026-12	\N
327	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7300.000	53500.010566/2026-12	\N
328	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7335.000	53500.010566/2026-12	\N
329	1	International Publicity - Interpub Eventos	Vila Santa Maria - Conjunto Caiçara	7350.000	53500.010566/2026-12	\N
330	2	Vtx Digitalcom Ltda	Santo Cristo	360.550	53500.000854/2026-69	\N
331	2	Vtx Digitalcom Ltda	Santo Cristo	360.575	53500.000854/2026-69	\N
332	2	Vtx Digitalcom Ltda	Santo Cristo	360.600	53500.000854/2026-69	\N
333	2	Vtx Digitalcom Ltda	Santo Cristo	360.625	53500.000854/2026-69	\N
334	2	Vtx Digitalcom Ltda	Santo Cristo	360.650	53500.000854/2026-69	\N
335	2	Vtx Digitalcom Ltda	Santo Cristo	360.675	53500.000854/2026-69	\N
336	2	Vtx Digitalcom Ltda	Santo Cristo	360.700	53500.000854/2026-69	\N
337	2	Vtx Digitalcom Ltda	Santo Cristo	360.725	53500.000854/2026-69	\N
338	2	Vtx Digitalcom Ltda	Santo Cristo	360.750	53500.000854/2026-69	\N
339	2	Vtx Digitalcom Ltda	Santo Cristo	360.775	53500.000854/2026-69	\N
340	2	Vtx Digitalcom Ltda	Santo Cristo	361.025	53500.000854/2026-69	\N
341	2	Vtx Digitalcom Ltda	Santo Cristo	361.050	53500.000854/2026-69	\N
342	2	Vtx Digitalcom Ltda	Santo Cristo	361.075	53500.000854/2026-69	\N
343	2	Vtx Digitalcom Ltda	Santo Cristo	361.100	53500.000854/2026-69	\N
344	2	Vtx Digitalcom Ltda	Santo Cristo	361.150	53500.000854/2026-69	\N
345	2	Vtx Digitalcom Ltda	Santo Cristo	361.175	53500.000854/2026-69	\N
346	2	Vtx Digitalcom Ltda	Santo Cristo	361.200	53500.000854/2026-69	\N
347	2	Vtx Digitalcom Ltda	Santo Cristo	361.750	53500.000854/2026-69	\N
348	2	Vtx Digitalcom Ltda	Santo Cristo	361.775	53500.000854/2026-69	\N
349	2	Vtx Digitalcom Ltda	Santo Cristo	361.800	53500.000854/2026-69	\N
350	2	Vtx Digitalcom Ltda	Santo Cristo	361.825	53500.000854/2026-69	\N
351	2	Vtx Digitalcom Ltda	Santo Cristo	361.850	53500.000854/2026-69	\N
352	2	Vtx Digitalcom Ltda	Santo Cristo	361.875	53500.000854/2026-69	\N
353	2	Vtx Digitalcom Ltda	Santo Cristo	361.900	53500.000854/2026-69	\N
354	2	Vtx Digitalcom Ltda	Santo Cristo	361.925	53500.000854/2026-69	\N
355	2	Vtx Digitalcom Ltda	Santo Cristo	361.950	53500.000854/2026-69	\N
356	2	Vtx Digitalcom Ltda	Santo Cristo	361.975	53500.000854/2026-69	\N
357	2	Vtx Digitalcom Ltda	Santo Cristo	362.000	53500.000854/2026-69	\N
358	2	Vtx Digitalcom Ltda	Santo Cristo	379.300	53500.000854/2026-69	\N
359	2	Vtx Digitalcom Ltda	Santo Cristo	379.325	53500.000854/2026-69	\N
360	2	Vtx Digitalcom Ltda	Santo Cristo	379.350	53500.000854/2026-69	\N
361	2	Vtx Digitalcom Ltda	Santo Cristo	379.375	53500.000854/2026-69	\N
362	2	Vtx Digitalcom Ltda	Santo Cristo	379.400	53500.000854/2026-69	\N
363	2	Vtx Digitalcom Ltda	Santo Cristo	379.425	53500.000854/2026-69	\N
364	2	Vtx Digitalcom Ltda	Santo Cristo	379.450	53500.000854/2026-69	\N
365	2	Vtx Digitalcom Ltda	Santo Cristo	379.475	53500.000854/2026-69	\N
366	2	Vtx Digitalcom Ltda	Santo Cristo	379.500	53500.000854/2026-69	\N
367	2	Vtx Digitalcom Ltda	Santo Cristo	379.775	53500.000854/2026-69	\N
368	2	Vtx Digitalcom Ltda	Santo Cristo	379.800	53500.000854/2026-69	\N
369	2	Vtx Digitalcom Ltda	Santo Cristo	379.825	53500.000854/2026-69	\N
370	2	Vtx Digitalcom Ltda	Santo Cristo	379.850	53500.000854/2026-69	\N
371	2	Vtx Digitalcom Ltda	Santo Cristo	379.875	53500.000854/2026-69	\N
372	2	Vtx Digitalcom Ltda	Santo Cristo	379.900	53500.000854/2026-69	\N
373	2	Vtx Digitalcom Ltda	Santo Cristo	379.925	53500.000854/2026-69	\N
374	2	Vtx Digitalcom Ltda	Santo Cristo	380.525	53500.000854/2026-69	\N
375	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	441.125	53500.002079/2026-86	\N
376	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	442.125	53500.002079/2026-86	\N
377	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	443.225	53500.002079/2026-86	\N
378	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	443.525	53500.002079/2026-86	\N
379	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	443.800	53500.002079/2026-86	\N
380	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	443.800	53500.002079/2026-86	\N
608	2	TV OMEGA LTDA	Santo Cristo	599.200	53500.006797/2026-21	\N
381	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	443.825	53500.002079/2026-86	\N
382	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	447.225	53500.002079/2026-86	\N
383	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	447.235	53500.002079/2026-86	\N
384	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	447.525	53500.002079/2026-86	\N
385	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	447.725	53500.002079/2026-86	\N
386	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	447.825	53500.002079/2026-86	\N
387	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	448.830	53500.002079/2026-86	\N
388	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	449.615	53500.002079/2026-86	\N
389	2	Vtx Digitalcom Ltda	Santo Cristo	450.400	53500.000854/2026-69	\N
390	2	Vtx Digitalcom Ltda	Santo Cristo	450.413	53500.000854/2026-69	\N
391	2	Vtx Digitalcom Ltda	Santo Cristo	450.425	53500.000854/2026-69	\N
392	2	Vtx Digitalcom Ltda	Santo Cristo	450.438	53500.000854/2026-69	\N
393	2	Vtx Digitalcom Ltda	Santo Cristo	450.475	53500.000854/2026-69	\N
394	2	Vtx Digitalcom Ltda	Santo Cristo	450.488	53500.000854/2026-69	\N
395	2	Vtx Digitalcom Ltda	Santo Cristo	450.500	53500.000854/2026-69	\N
396	2	Vtx Digitalcom Ltda	Santo Cristo	450.513	53500.000854/2026-69	\N
397	2	Vtx Digitalcom Ltda	Santo Cristo	450.525	53500.000854/2026-69	\N
398	2	Vtx Digitalcom Ltda	Santo Cristo	450.538	53500.000854/2026-69	\N
399	2	Vtx Digitalcom Ltda	Santo Cristo	450.550	53500.000854/2026-69	\N
400	2	Vtx Digitalcom Ltda	Santo Cristo	450.550	53500.000854/2026-69	\N
401	2	Vtx Digitalcom Ltda	Santo Cristo	450.563	53500.000854/2026-69	\N
402	2	Vtx Digitalcom Ltda	Santo Cristo	450.600	53500.000854/2026-69	\N
403	2	Vtx Digitalcom Ltda	Santo Cristo	450.613	53500.000854/2026-69	\N
404	2	Vtx Digitalcom Ltda	Santo Cristo	450.638	53500.000854/2026-69	\N
405	2	Vtx Digitalcom Ltda	Santo Cristo	450.650	53500.000854/2026-69	\N
406	2	Vtx Digitalcom Ltda	Santo Cristo	450.688	53500.000854/2026-69	\N
407	2	Vtx Digitalcom Ltda	Santo Cristo	450.700	53500.000854/2026-69	\N
408	2	Vtx Digitalcom Ltda	Santo Cristo	450.713	53500.000854/2026-69	\N
409	2	Vtx Digitalcom Ltda	Santo Cristo	450.775	53500.000854/2026-69	\N
410	2	Vtx Digitalcom Ltda	Santo Cristo	450.788	53500.000854/2026-69	\N
411	2	Vtx Digitalcom Ltda	Santo Cristo	450.800	53500.000854/2026-69	\N
412	2	Vtx Digitalcom Ltda	Santo Cristo	450.800	53500.000854/2026-69	\N
413	2	Vtx Digitalcom Ltda	Santo Cristo	450.800	53500.000854/2026-69	\N
414	2	Vtx Digitalcom Ltda	Santo Cristo	450.800	53500.000854/2026-69	\N
415	2	Vtx Digitalcom Ltda	Santo Cristo	451.050	53500.000854/2026-69	\N
416	2	Vtx Digitalcom Ltda	Santo Cristo	451.088	53500.000854/2026-69	\N
417	2	Vtx Digitalcom Ltda	Santo Cristo	451.100	53500.000854/2026-69	\N
418	2	Vtx Digitalcom Ltda	Santo Cristo	451.113	53500.000854/2026-69	\N
419	2	Vtx Digitalcom Ltda	Santo Cristo	451.163	53500.000854/2026-69	\N
420	2	Vtx Digitalcom Ltda	Santo Cristo	451.213	53500.000854/2026-69	\N
421	2	Radio e Televisao Bandeirantes	Santo Cristo	452.100	53500.005588/2026-61	\N
422	2	Radio e Televisao Bandeirantes	Santo Cristo	452.100	53500.005588/2026-61	\N
423	2	Vtx Digitalcom Ltda	Santo Cristo	452.313	53500.000854/2026-69	\N
424	2	Vtx Digitalcom Ltda	Santo Cristo	452.325	53500.000854/2026-69	\N
425	2	Vtx Digitalcom Ltda	Santo Cristo	452.338	53500.000854/2026-69	\N
426	2	Vtx Digitalcom Ltda	Santo Cristo	452.363	53500.000854/2026-69	\N
427	2	Vtx Digitalcom Ltda	Santo Cristo	452.375	53500.000854/2026-69	\N
428	2	Vtx Digitalcom Ltda	Santo Cristo	452.388	53500.000854/2026-69	\N
429	2	Vtx Digitalcom Ltda	Santo Cristo	452.400	53500.000854/2026-69	\N
430	2	Vtx Digitalcom Ltda	Santo Cristo	452.413	53500.000854/2026-69	\N
431	2	Vtx Digitalcom Ltda	Santo Cristo	452.425	53500.000854/2026-69	\N
432	2	Vtx Digitalcom Ltda	Santo Cristo	452.438	53500.000854/2026-69	\N
433	2	Vtx Digitalcom Ltda	Santo Cristo	452.450	53500.000854/2026-69	\N
434	2	Vtx Digitalcom Ltda	Santo Cristo	452.463	53500.000854/2026-69	\N
435	2	Vtx Digitalcom Ltda	Santo Cristo	452.475	53500.000854/2026-69	\N
436	2	Vtx Digitalcom Ltda	Santo Cristo	452.500	53500.000854/2026-69	\N
437	2	Vtx Digitalcom Ltda	Santo Cristo	452.500	53500.000854/2026-69	\N
438	2	Vtx Digitalcom Ltda	Santo Cristo	452.500	53500.000854/2026-69	\N
439	2	Vtx Digitalcom Ltda	Santo Cristo	452.513	53500.000854/2026-69	\N
440	2	Vtx Digitalcom Ltda	Santo Cristo	453.263	53500.000854/2026-69	\N
441	2	Vtx Digitalcom Ltda	Santo Cristo	453.275	53500.000854/2026-69	\N
442	2	Vtx Digitalcom Ltda	Santo Cristo	453.288	53500.000854/2026-69	\N
443	2	Vtx Digitalcom Ltda	Santo Cristo	453.313	53500.000854/2026-69	\N
444	2	Vtx Digitalcom Ltda	Santo Cristo	453.325	53500.000854/2026-69	\N
445	2	Vtx Digitalcom Ltda	Santo Cristo	453.338	53500.000854/2026-69	\N
446	2	Vtx Digitalcom Ltda	Santo Cristo	453.350	53500.000854/2026-69	\N
447	2	Vtx Digitalcom Ltda	Santo Cristo	453.363	53500.000854/2026-69	\N
448	2	Vtx Digitalcom Ltda	Santo Cristo	453.388	53500.000854/2026-69	\N
449	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	453.450	53500.002079/2026-86	\N
450	2	Vtx Digitalcom Ltda	Santo Cristo	453.588	53500.000854/2026-69	\N
451	2	Vtx Digitalcom Ltda	Santo Cristo	454.388	53500.000854/2026-69	\N
452	2	Vtx Digitalcom Ltda	Santo Cristo	454.488	53500.000854/2026-69	\N
453	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.550	53500.005176/2026-21	\N
454	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.600	53500.005176/2026-21	\N
455	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.625	53500.005176/2026-21	\N
456	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.650	53500.005176/2026-21	\N
457	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.675	53500.005176/2026-21	\N
458	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.700	53500.005176/2026-21	\N
459	2	TRANSPORTES CARVALHO LTDA	Santo Cristo	454.735	53500.005176/2026-21	\N
460	2	Radio e Televisao Bandeirantes	Santo Cristo	455.275	53500.005588/2026-61	\N
461	2	Radio e Televisao Bandeirantes	Santo Cristo	455.275	53500.005588/2026-61	\N
462	2	Vtx Digitalcom Ltda	Santo Cristo	455.388	53500.000854/2026-69	\N
463	2	Vtx Digitalcom Ltda	Santo Cristo	455.413	53500.000854/2026-69	\N
464	2	Vtx Digitalcom Ltda	Santo Cristo	455.425	53500.000854/2026-69	\N
465	2	Vtx Digitalcom Ltda	Santo Cristo	455.438	53500.000854/2026-69	\N
466	2	Vtx Digitalcom Ltda	Santo Cristo	455.450	53500.000854/2026-69	\N
467	2	Vtx Digitalcom Ltda	Santo Cristo	455.463	53500.000854/2026-69	\N
468	2	Vtx Digitalcom Ltda	Santo Cristo	455.475	53500.000854/2026-69	\N
469	2	Vtx Digitalcom Ltda	Santo Cristo	455.488	53500.000854/2026-69	\N
470	2	Vtx Digitalcom Ltda	Santo Cristo	455.525	53500.000854/2026-69	\N
471	2	Vtx Digitalcom Ltda	Santo Cristo	455.538	53500.000854/2026-69	\N
472	2	Vtx Digitalcom Ltda	Santo Cristo	455.550	53500.000854/2026-69	\N
473	2	Vtx Digitalcom Ltda	Santo Cristo	455.563	53500.000854/2026-69	\N
474	2	Vtx Digitalcom Ltda	Santo Cristo	455.575	53500.000854/2026-69	\N
475	2	Vtx Digitalcom Ltda	Santo Cristo	455.588	53500.000854/2026-69	\N
476	2	Vtx Digitalcom Ltda	Santo Cristo	455.613	53500.000854/2026-69	\N
477	2	Vtx Digitalcom Ltda	Santo Cristo	455.625	53500.000854/2026-69	\N
478	2	Vtx Digitalcom Ltda	Santo Cristo	455.638	53500.000854/2026-69	\N
479	2	Vtx Digitalcom Ltda	Santo Cristo	455.650	53500.000854/2026-69	\N
480	2	Vtx Digitalcom Ltda	Santo Cristo	455.663	53500.000854/2026-69	\N
481	2	Vtx Digitalcom Ltda	Santo Cristo	455.688	53500.000854/2026-69	\N
482	2	Vtx Digitalcom Ltda	Santo Cristo	455.700	53500.000854/2026-69	\N
483	2	Vtx Digitalcom Ltda	Santo Cristo	455.713	53500.000854/2026-69	\N
484	2	Vtx Digitalcom Ltda	Santo Cristo	455.725	53500.000854/2026-69	\N
485	2	Vtx Digitalcom Ltda	Santo Cristo	455.738	53500.000854/2026-69	\N
486	2	Vtx Digitalcom Ltda	Santo Cristo	455.750	53500.000854/2026-69	\N
487	2	Vtx Digitalcom Ltda	Santo Cristo	455.763	53500.000854/2026-69	\N
488	2	Vtx Digitalcom Ltda	Santo Cristo	455.775	53500.000854/2026-69	\N
489	2	Vtx Digitalcom Ltda	Santo Cristo	455.788	53500.000854/2026-69	\N
490	2	Vtx Digitalcom Ltda	Santo Cristo	455.800	53500.000854/2026-69	\N
491	2	Radio e Televisao Bandeirantes	Santo Cristo	456.600	53500.005588/2026-61	\N
492	2	Radio e Televisao Bandeirantes	Santo Cristo	456.600	53500.005588/2026-61	\N
493	2	Vtx Digitalcom Ltda	Santo Cristo	457.150	53500.000854/2026-69	\N
494	2	Vtx Digitalcom Ltda	Santo Cristo	457.150	53500.000854/2026-69	\N
495	2	Vtx Digitalcom Ltda	Santo Cristo	457.200	53500.000854/2026-69	\N
496	2	Vtx Digitalcom Ltda	Santo Cristo	457.200	53500.000854/2026-69	\N
497	2	Vtx Digitalcom Ltda	Santo Cristo	457.300	53500.000854/2026-69	\N
498	2	Vtx Digitalcom Ltda	Santo Cristo	457.300	53500.000854/2026-69	\N
499	2	Vtx Digitalcom Ltda	Santo Cristo	457.450	53500.000854/2026-69	\N
500	2	Vtx Digitalcom Ltda	Santo Cristo	457.450	53500.000854/2026-69	\N
501	2	Vtx Digitalcom Ltda	Santo Cristo	457.500	53500.000854/2026-69	\N
502	2	Vtx Digitalcom Ltda	Santo Cristo	457.550	53500.000854/2026-69	\N
503	2	Vtx Digitalcom Ltda	Santo Cristo	457.550	53500.000854/2026-69	\N
504	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	457.615	53500.002079/2026-86	\N
505	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	457.615	53500.002079/2026-86	\N
506	2	Vtx Digitalcom Ltda	Santo Cristo	457.650	53500.000854/2026-69	\N
507	2	Vtx Digitalcom Ltda	Santo Cristo	457.650	53500.000854/2026-69	\N
508	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	458.050	53500.002079/2026-86	\N
509	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	458.050	53500.002079/2026-86	\N
510	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	458.322	53500.002079/2026-86	\N
511	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	458.322	53500.002079/2026-86	\N
512	2	Radio e Televisao Bandeirantes	Santo Cristo	458.500	53500.005588/2026-61	\N
513	2	Radio e Televisao Bandeirantes	Santo Cristo	458.500	53500.005588/2026-61	\N
514	2	Radio e Televisao Bandeirantes	Santo Cristo	460.475	53500.005588/2026-61	\N
515	2	Radio e Televisao Bandeirantes	Santo Cristo	460.475	53500.005588/2026-61	\N
516	2	Vtx Digitalcom Ltda	Santo Cristo	460.663	53500.000854/2026-69	\N
517	2	Radio e Televisao Bandeirantes	Santo Cristo	462.475	53500.005588/2026-61	\N
518	2	Radio e Televisao Bandeirantes	Santo Cristo	462.475	53500.005588/2026-61	\N
519	2	Radio e Televisao Bandeirantes	Santo Cristo	465.500	53500.005588/2026-61	\N
520	2	Radio e Televisao Bandeirantes	Santo Cristo	465.500	53500.005588/2026-61	\N
521	2	Vtx Digitalcom Ltda	Santo Cristo	467.150	53500.000854/2026-69	\N
522	2	Vtx Digitalcom Ltda	Santo Cristo	467.200	53500.000854/2026-69	\N
523	2	Vtx Digitalcom Ltda	Santo Cristo	467.300	53500.000854/2026-69	\N
524	2	Vtx Digitalcom Ltda	Santo Cristo	467.450	53500.000854/2026-69	\N
525	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	467.488	53500.002079/2026-86	\N
526	2	Vtx Digitalcom Ltda	Santo Cristo	467.550	53500.000854/2026-69	\N
527	2	Vtx Digitalcom Ltda	Santo Cristo	467.650	53500.000854/2026-69	\N
528	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	468.063	53500.002079/2026-86	\N
529	2	Radio e Televisao Bandeirantes	Santo Cristo	468.275	53500.005588/2026-61	\N
530	2	Radio e Televisao Bandeirantes	Santo Cristo	468.275	53500.005588/2026-61	\N
531	2	RICALLRADIO TELECOMUNICAÇÕES LTDA	Santo Cristo	468.322	53500.002079/2026-86	\N
532	2	Radio e Televisao Bandeirantes	Santo Cristo	470.175	53500.005588/2026-61	\N
533	2	Radio e Televisao Bandeirantes	Santo Cristo	470.375	53500.005588/2026-61	\N
534	2	Radio e Televisao Bandeirantes	Santo Cristo	470.575	53500.005588/2026-61	\N
535	2	Radio e Televisao Bandeirantes	Santo Cristo	470.775	53500.005588/2026-61	\N
536	2	Radio e Televisao Bandeirantes	Santo Cristo	470.975	53500.005588/2026-61	\N
537	2	Radio e Televisao Bandeirantes	Santo Cristo	471.150	53500.005588/2026-61	\N
538	2	TV OMEGA LTDA	Santo Cristo	475.250	53500.006797/2026-21	\N
539	2	Radio e Televisao Bandeirantes	Santo Cristo	475.500	53500.005588/2026-61	\N
540	2	TV OMEGA LTDA	Santo Cristo	486.125	53500.006797/2026-21	\N
541	2	Radio e Televisao Bandeirantes	Santo Cristo	487.000	53500.005588/2026-61	\N
542	2	Radio e Televisao Bandeirantes	Santo Cristo	488.150	53500.005588/2026-61	\N
543	2	TV OMEGA LTDA	Santo Cristo	488.225	53500.006797/2026-21	\N
544	2	BMX	Santo Cristo	489.175	53500.110707/2025-15	\N
545	2	BMX	Santo Cristo	490.025	53500.110707/2025-15	\N
546	2	Radio e Televisao Bandeirantes	Santo Cristo	490.750	53500.005588/2026-61	\N
547	2	BMX	Santo Cristo	491.150	53500.110707/2025-15	\N
548	2	BMX	Santo Cristo	491.650	53500.110707/2025-15	\N
549	2	BMX	Santo Cristo	493.000	53500.110707/2025-15	\N
550	2	TV OMEGA LTDA	Santo Cristo	493.250	53500.006797/2026-21	\N
551	2	Radio e Televisao Bandeirantes	Santo Cristo	500.575	53500.005588/2026-61	\N
552	2	Radio e Televisao Bandeirantes	Santo Cristo	501.325	53500.005588/2026-61	\N
553	2	BMX	Santo Cristo	501.875	53500.110707/2025-15	\N
554	2	Radio e Televisao Bandeirantes	Santo Cristo	502.150	53500.005588/2026-61	\N
555	2	BMX	Santo Cristo	502.850	53500.110707/2025-15	\N
556	2	Radio e Televisao Bandeirantes	Santo Cristo	504.225	53500.005588/2026-61	\N
557	2	BMX	Santo Cristo	505.125	53500.110707/2025-15	\N
558	2	Radio e Televisao Bandeirantes	Santo Cristo	505.375	53500.005588/2026-61	\N
559	2	TV OMEGA LTDA	Santo Cristo	505.500	53500.006797/2026-21	\N
560	2	Radio e Televisao Bandeirantes	Santo Cristo	506.150	53500.005588/2026-61	\N
561	2	Radio e Televisao Bandeirantes	Santo Cristo	506.700	53500.005588/2026-61	\N
562	2	TV OMEGA LTDA	Santo Cristo	517.875	53500.006797/2026-21	\N
563	2	Radio e Televisao Bandeirantes	Santo Cristo	518.100	53500.005588/2026-61	\N
564	2	Radio e Televisao Bandeirantes	Santo Cristo	518.300	53500.005588/2026-61	\N
565	2	Radio e Televisao Bandeirantes	Santo Cristo	518.500	53500.005588/2026-61	\N
566	2	Radio e Televisao Bandeirantes	Santo Cristo	518.700	53500.005588/2026-61	\N
567	2	Radio e Televisao Bandeirantes	Santo Cristo	518.900	53500.005588/2026-61	\N
568	2	Radio e Televisao Bandeirantes	Santo Cristo	519.100	53500.005588/2026-61	\N
569	2	BMX	Santo Cristo	524.125	53500.110707/2025-15	\N
570	2	BMX	Santo Cristo	524.975	53500.110707/2025-15	\N
571	2	Radio e Televisao Bandeirantes	Santo Cristo	525.000	53500.005588/2026-61	\N
572	2	BMX	Santo Cristo	525.575	53500.110707/2025-15	\N
573	2	Radio e Televisao Bandeirantes	Santo Cristo	526.100	53500.005588/2026-61	\N
574	2	BMX	Santo Cristo	526.550	53500.110707/2025-15	\N
575	2	BMX	Santo Cristo	527.125	53500.110707/2025-15	\N
576	2	BMX	Santo Cristo	528.875	53500.110707/2025-15	\N
577	2	BMX	Santo Cristo	529.725	53500.110707/2025-15	\N
578	2	BMX	Santo Cristo	536.575	53500.110707/2025-15	\N
579	2	BMX	Santo Cristo	536.575	53500.110707/2025-15	\N
580	2	BMX	Santo Cristo	536.975	53500.110707/2025-15	\N
581	2	BMX	Santo Cristo	537.075	53500.110707/2025-15	\N
582	2	BMX	Santo Cristo	537.650	53500.110707/2025-15	\N
583	2	Radio e Televisao Bandeirantes	Santo Cristo	538.100	53500.005588/2026-61	\N
584	2	BMX	Santo Cristo	538.650	53500.110707/2025-15	\N
585	2	BMX	Santo Cristo	539.000	53500.110707/2025-15	\N
586	2	BMX	Santo Cristo	539.950	53500.110707/2025-15	\N
587	2	BMX	Santo Cristo	540.475	53500.110707/2025-15	\N
588	2	BMX	Santo Cristo	541.150	53500.110707/2025-15	\N
589	2	BMX	Santo Cristo	541.700	53500.110707/2025-15	\N
590	2	Radio e Televisao Bandeirantes	Santo Cristo	542.300	53500.005588/2026-61	\N
591	2	BMX	Santo Cristo	542.675	53500.110707/2025-15	\N
592	2	Radio e Televisao Bandeirantes	Santo Cristo	547.300	53500.005588/2026-61	\N
593	2	BMX	Santo Cristo	557.000	53500.110707/2025-15	\N
594	2	Radio e Televisao Bandeirantes	Santo Cristo	563.100	53500.005588/2026-61	\N
595	2	TV OMEGA LTDA	Santo Cristo	570.100	53500.006797/2026-21	\N
596	2	BMX	Santo Cristo	578.575	53500.110707/2025-15	\N
597	2	BMX	Santo Cristo	579.350	53500.110707/2025-15	\N
598	2	BMX	Santo Cristo	579.700	53500.110707/2025-15	\N
599	2	BMX	Santo Cristo	580.200	53500.110707/2025-15	\N
600	2	BMX	Santo Cristo	580.600	53500.110707/2025-15	\N
601	2	BMX	Santo Cristo	581.125	53500.110707/2025-15	\N
602	2	BMX	Santo Cristo	582.375	53500.110707/2025-15	\N
603	2	Radio e Televisao Bandeirantes	Santo Cristo	582.975	53500.005588/2026-61	\N
604	2	BMX	Santo Cristo	583.350	53500.110707/2025-15	\N
605	2	BMX	Santo Cristo	583.850	53500.110707/2025-15	\N
606	2	TV OMEGA LTDA	Santo Cristo	584.200	53500.006797/2026-21	\N
609	2	BMX	Santo Cristo	603.725	53500.110707/2025-15	\N
610	2	TV OMEGA LTDA	Santo Cristo	610.300	53500.006797/2026-21	\N
611	2	BMX	Santo Cristo	617.300	53500.110707/2025-15	\N
612	2	BMX	Santo Cristo	618.100	53500.110707/2025-15	\N
613	2	BMX	Santo Cristo	618.750	53500.110707/2025-15	\N
614	2	BMX	Santo Cristo	626.725	53500.110707/2025-15	\N
615	2	BMX	Santo Cristo	627.175	53500.110707/2025-15	\N
616	2	BMX	Santo Cristo	628.625	53500.110707/2025-15	\N
617	2	BMX	Santo Cristo	629.400	53500.110707/2025-15	\N
618	2	BMX	Santo Cristo	629.925	53500.110707/2025-15	\N
619	2	BMX	Santo Cristo	630.625	53500.110707/2025-15	\N
620	2	BMX	Santo Cristo	631.125	53500.110707/2025-15	\N
621	2	Radio e Televisao Bandeirantes	Santo Cristo	638.175	53500.005588/2026-61	\N
622	2	Radio e Televisao Bandeirantes	Santo Cristo	638.350	53500.005588/2026-61	\N
623	2	Radio e Televisao Bandeirantes	Santo Cristo	638.925	53500.005588/2026-61	\N
624	2	Radio e Televisao Bandeirantes	Santo Cristo	639.100	53500.005588/2026-61	\N
625	2	Radio e Televisao Bandeirantes	Santo Cristo	639.325	53500.005588/2026-61	\N
626	2	Radio e Televisao Bandeirantes	Santo Cristo	639.625	53500.005588/2026-61	\N
627	2	Radio e Televisao Bandeirantes	Santo Cristo	640.125	53500.005588/2026-61	\N
628	2	Radio e Televisao Bandeirantes	Santo Cristo	640.125	53500.005588/2026-61	\N
629	2	Radio e Televisao Bandeirantes	Santo Cristo	640.425	53500.005588/2026-61	\N
630	2	Radio e Televisao Bandeirantes	Santo Cristo	640.675	53500.005588/2026-61	\N
631	2	Radio e Televisao Bandeirantes	Santo Cristo	641.225	53500.005588/2026-61	\N
632	2	Radio e Televisao Bandeirantes	Santo Cristo	641.575	53500.005588/2026-61	\N
633	2	Radio e Televisao Bandeirantes	Santo Cristo	642.175	53500.005588/2026-61	\N
634	2	Radio e Televisao Bandeirantes	Santo Cristo	642.650	53500.005588/2026-61	\N
635	2	Radio e Televisao Bandeirantes	Santo Cristo	643.100	53500.005588/2026-61	\N
636	2	Radio e Televisao Bandeirantes	Santo Cristo	643.350	53500.005588/2026-61	\N
637	2	Radio e Televisao Bandeirantes	Santo Cristo	1881.000	53500.005588/2026-61	\N
638	2	Radio e Televisao Bandeirantes	Santo Cristo	1882.600	53500.005588/2026-61	\N
639	2	Radio e Televisao Bandeirantes	Santo Cristo	1883.800	53500.005588/2026-61	\N
640	2	Radio e Televisao Bandeirantes	Santo Cristo	1884.200	53500.005588/2026-61	\N
641	2	Radio e Televisao Bandeirantes	Santo Cristo	1910.000	53500.005588/2026-61	\N
642	2	Radio e Televisao Bandeirantes	Santo Cristo	1910.000	53500.005588/2026-61	\N
643	2	Radio e Televisao Bandeirantes	Santo Cristo	1910.600	53500.005588/2026-61	\N
644	2	Radio e Televisao Bandeirantes	Santo Cristo	1911.200	53500.005588/2026-61	\N
645	2	Radio e Televisao Bandeirantes	Santo Cristo	1912.400	53500.005588/2026-61	\N
646	2	Radio e Televisao Bandeirantes	Santo Cristo	1912.400	53500.005588/2026-61	\N
647	2	Radio e Televisao Bandeirantes	Santo Cristo	1913.000	53500.005588/2026-61	\N
648	2	Radio e Televisao Bandeirantes	Santo Cristo	1913.000	53500.005588/2026-61	\N
649	2	Radio e Televisao Bandeirantes	Santo Cristo	1913.600	53500.005588/2026-61	\N
650	2	Radio e Televisao Bandeirantes	Santo Cristo	1914.200	53500.005588/2026-61	\N
651	2	Radio e Televisao Bandeirantes	Santo Cristo	2061.000	53500.005588/2026-61	\N
652	2	Radio e Televisao Bandeirantes	Santo Cristo	2069.000	53500.005588/2026-61	\N
653	2	Radio e Televisao Bandeirantes	Santo Cristo	2082.250	53500.005588/2026-61	\N
654	2	Radio e Televisao Bandeirantes	Santo Cristo	2090.000	53500.005588/2026-61	\N
655	2	Radio e Televisao Bandeirantes	Santo Cristo	2395.000	53500.005588/2026-61	\N
656	2	Radio e Televisao Bandeirantes	Santo Cristo	2400.000	53500.005588/2026-61	\N
657	2	Radio e Televisao Bandeirantes	Santo Cristo	2445.000	53500.005588/2026-61	\N
658	2	Radio e Televisao Bandeirantes	Santo Cristo	2461.000	53500.005588/2026-61	\N
659	2	Radio e Televisao Bandeirantes	Santo Cristo	5110.000	53500.005588/2026-61	\N
660	2	Radio e Televisao Bandeirantes	Santo Cristo	5190.000	53500.005588/2026-61	\N
661	2	Radio e Televisao Bandeirantes	Santo Cristo	5300.000	53500.005588/2026-61	\N
662	2	Radio e Televisao Bandeirantes	Santo Cristo	5310.000	53500.005588/2026-61	\N
663	2	Radio e Televisao Bandeirantes	Santo Cristo	5350.000	53500.005588/2026-61	\N
664	2	Radio e Televisao Bandeirantes	Santo Cristo	5410.000	53500.005588/2026-61	\N
665	2	Radio e Televisao Bandeirantes	Santo Cristo	5510.000	53500.005588/2026-61	\N
666	2	Radio e Televisao Bandeirantes	Santo Cristo	5570.000	53500.005588/2026-61	\N
667	2	Radio e Televisao Bandeirantes	Santo Cristo	5660.000	53500.005588/2026-61	\N
668	2	Radio e Televisao Bandeirantes	Santo Cristo	5670.000	53500.005588/2026-61	\N
669	2	Radio e Televisao Bandeirantes	Santo Cristo	5700.000	53500.005588/2026-61	\N
670	2	Radio e Televisao Bandeirantes	Santo Cristo	5770.000	53500.005588/2026-61	\N
671	2	Radio e Televisao Bandeirantes	Santo Cristo	5770.000	53500.005588/2026-61	\N
672	2	Radio e Televisao Bandeirantes	Santo Cristo	5786.000	53500.005588/2026-61	\N
673	2	TIM S A	Centro	17755.000	53500.005988/2026-76	\N
674	2	TIM S A	Glória	17755.000	53500.005988/2026-76	\N
675	2	TIM S A	Centro	17865.000	53500.005988/2026-76	\N
676	2	TIM S A	Glória	17865.000	53500.005988/2026-76	\N
677	2	TIM S A	Centro	19315.000	53500.005988/2026-76	\N
678	2	TIM S A	Glória	19315.000	53500.005988/2026-76	\N
679	2	TIM S A	Centro	19425.000	53500.005988/2026-76	\N
680	2	TIM S A	Glória	19425.000	53500.005988/2026-76	\N
681	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	385.300	53500.004570/2026-41	\N
682	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	385.300	53500.004570/2026-41	\N
683	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	385.375	53500.004570/2026-41	\N
684	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	385.375	53500.004570/2026-41	\N
685	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	385.500	53500.004570/2026-41	\N
686	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	385.500	53500.004570/2026-41	\N
687	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	385.900	53500.004570/2026-41	\N
688	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	385.900	53500.004570/2026-41	\N
689	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	386.075	53500.004570/2026-41	\N
690	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	386.075	53500.004570/2026-41	\N
691	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	386.175	53500.004570/2026-41	\N
692	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	386.175	53500.004570/2026-41	\N
693	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	386.750	53500.004570/2026-41	\N
694	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	386.750	53500.004570/2026-41	\N
695	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	387.075	53500.004570/2026-41	\N
696	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	387.075	53500.004570/2026-41	\N
697	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.025	53500.003104/2026-49	\N
698	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.025	53500.003104/2026-49	\N
699	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.050	53500.003104/2026-49	\N
700	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.050	53500.003104/2026-49	\N
701	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.125	53500.003104/2026-49	\N
702	3	SISCOM TELECOMUNICACOES LTDA	Paralela	389.175	53500.003104/2026-49	\N
703	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	395.300	53500.004570/2026-41	\N
704	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	395.375	53500.004570/2026-41	\N
705	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	395.500	53500.004570/2026-41	\N
706	3	Kofre Representacao e Comercio de Telecom. Ltda	Paripe	395.900	53500.004570/2026-41	\N
707	3	Kofre Representacao e Comercio de Telecom. Ltda	Tancredo Neves	396.075	53500.004570/2026-41	\N
708	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	396.175	53500.004570/2026-41	\N
709	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	396.750	53500.004570/2026-41	\N
710	3	Kofre Representacao e Comercio de Telecom. Ltda	Barra	397.075	53500.004570/2026-41	\N
711	3	SISCOM TELECOMUNICACOES LTDA	Paralela	399.025	53500.003104/2026-49	\N
712	3	SISCOM TELECOMUNICACOES LTDA	Paralela	399.050	53500.003104/2026-49	\N
713	3	SISCOM TELECOMUNICACOES LTDA	Paralela	399.125	53500.003104/2026-49	\N
714	3	SISCOM TELECOMUNICACOES LTDA	Paralela	399.175	53500.003104/2026-49	\N
715	3	ANA PAULA CAMPOS PINHEIRO	Centro	450.413	53500.002842/2026-79	\N
716	3	Radio e Televisao Bandeirantes S.a.	Ondina	450.500	53500.003330/2026-20	\N
717	3	Radio e Televisao Bandeirantes S.a.	Ondina	450.500	53500.003330/2026-20	\N
718	3	ANA PAULA CAMPOS PINHEIRO	Ondina	451.375	53500.002842/2026-79	\N
719	3	Radio e Televisao Bandeirantes S.a.	Ondina	453.300	53500.003330/2026-20	\N
720	3	Radio e Televisao Bandeirantes S.a.	Ondina	453.300	53500.003330/2026-20	\N
721	3	ANA PAULA CAMPOS PINHEIRO	Centro	455.413	53500.002842/2026-79	\N
722	3	ANA PAULA CAMPOS PINHEIRO	Ondina	456.375	53500.002842/2026-79	\N
723	3	Radio e Televisao Bandeirantes S.a.	Ondina	456.600	53500.003330/2026-20	\N
724	3	Radio e Televisao Bandeirantes S.a.	Ondina	456.600	53500.003330/2026-20	\N
725	3	Radio e Televisao Bandeirantes S.a.	Ondina	458.500	53500.003330/2026-20	\N
726	3	Radio e Televisao Bandeirantes S.a.	Ondina	458.500	53500.003330/2026-20	\N
727	3	Radio e Televisao Bandeirantes S.a.	Ondina	460.475	53500.003330/2026-20	\N
728	3	Radio e Televisao Bandeirantes S.a.	Ondina	460.475	53500.003330/2026-20	\N
729	3	Radio e Televisao Bandeirantes S.a.	Ondina	462.475	53500.003330/2026-20	\N
730	3	Radio e Televisao Bandeirantes S.a.	Ondina	462.475	53500.003330/2026-20	\N
731	3	Radio e Televisao Bandeirantes S.a.	Ondina	468.275	53500.003330/2026-20	\N
732	3	Radio e Televisao Bandeirantes S.a.	Ondina	468.275	53500.003330/2026-20	\N
733	3	Radio e Televisao Bandeirantes S.a.	Ondina	469.000	53500.003330/2026-20	\N
734	3	Radio e Televisao Bandeirantes S.a.	Ondina	469.000	53500.003330/2026-20	\N
735	3	Produtora Ciel Ltda	Ondina	476.000	53500.007294/2026-73	\N
736	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	476.175	53500.006565/2026-73	\N
737	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	476.350	53500.007112/2026-64	\N
738	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	476.375	53500.007112/2026-64	\N
739	3	Radio e Televisao Bandeirantes S.a.	Ondina	476.475	53500.003330/2026-20	\N
740	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	476.800	53500.007112/2026-64	\N
741	3	TELEVISAO BAHIA S.A.	Centro	477.000	53500.006132/2026-18	\N
742	3	TELEVISAO BAHIA S.A.	Ondina	477.000	53500.006132/2026-18	\N
743	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	477.225	53500.007112/2026-64	\N
744	3	Radio e Televisao Bandeirantes S.a.	Ondina	477.375	53500.003330/2026-20	\N
745	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	477.450	53500.007112/2026-64	\N
746	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	477.775	53500.007112/2026-64	\N
747	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	477.850	53500.006565/2026-73	\N
748	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	477.900	53500.007112/2026-64	\N
749	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	478.275	53500.007112/2026-64	\N
750	3	Produtora Ciel Ltda	Ondina	478.325	53500.007294/2026-73	\N
751	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	478.575	53500.007112/2026-64	\N
752	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	478.725	53500.007112/2026-64	\N
753	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	479.100	53500.006565/2026-73	\N
754	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	479.125	53500.007112/2026-64	\N
755	3	Produtora Ciel Ltda	Ondina	479.550	53500.007294/2026-73	\N
756	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	479.575	53500.007112/2026-64	\N
757	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	479.950	53500.007112/2026-64	\N
758	3	TELEVISAO BAHIA S.A.	Centro	480.000	53500.006132/2026-18	\N
759	3	TELEVISAO BAHIA S.A.	Ondina	480.000	53500.006132/2026-18	\N
760	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	480.350	53500.007112/2026-64	\N
761	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	480.975	53500.006565/2026-73	\N
762	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	481.425	53500.006565/2026-73	\N
763	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	481.750	53500.007112/2026-64	\N
764	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	481.875	53500.006565/2026-73	\N
765	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	482.075	53500.007112/2026-64	\N
766	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	485.675	53500.006565/2026-73	\N
767	3	Radio e Televisao Bandeirantes S.a.	Ondina	494.100	53500.003330/2026-20	\N
768	3	Radio e Televisao Bandeirantes S.a.	Ondina	494.225	53500.003330/2026-20	\N
769	3	Radio e Televisao Bandeirantes S.a.	Ondina	495.175	53500.003330/2026-20	\N
770	3	Radio e Televisao Bandeirantes S.a.	Ondina	495.750	53500.003330/2026-20	\N
771	3	Radio e Televisao Bandeirantes S.a.	Ondina	496.875	53500.003330/2026-20	\N
772	3	TV ARATU S/A	Ondina	497.000	53500.003653/2026-13	\N
773	3	Radio e Televisao Bandeirantes S.a.	Ondina	497.870	53500.003330/2026-20	\N
774	3	Produtora Ciel Ltda	Ondina	500.350	53500.007294/2026-73	\N
775	3	Produtora Ciel Ltda	Ondina	500.900	53500.007294/2026-73	\N
776	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	502.275	53500.006565/2026-73	\N
777	3	Produtora Ciel Ltda	Ondina	502.500	53500.007294/2026-73	\N
778	3	Produtora Ciel Ltda	Ondina	504.200	53500.007294/2026-73	\N
779	3	Produtora Ciel Ltda	Ondina	505.250	53500.007294/2026-73	\N
780	3	Produtora Ciel Ltda	Ondina	505.600	53500.007294/2026-73	\N
781	3	Radio e Televisao Bandeirantes S.a.	Ondina	507.100	53500.003330/2026-20	\N
782	3	Radio e Televisao Bandeirantes S.a.	Ondina	507.400	53500.003330/2026-20	\N
783	3	TELEVISAO BAHIA S.A.	Centro	508.000	53500.006132/2026-18	\N
784	3	TELEVISAO BAHIA S.A.	Ondina	508.000	53500.006132/2026-18	\N
785	3	Radio e Televisao Bandeirantes S.a.	Ondina	508.500	53500.003330/2026-20	\N
786	3	Radio e Televisao Bandeirantes S.a.	Ondina	509.450	53500.003330/2026-20	\N
787	3	TELEVISAO BAHIA S.A.	Centro	510.000	53500.006132/2026-18	\N
788	3	TELEVISAO BAHIA S.A.	Ondina	510.000	53500.006132/2026-18	\N
789	3	Radio e Televisao Bandeirantes S.a.	Ondina	522.850	53500.003330/2026-20	\N
790	3	Radio e Televisao Bandeirantes S.a.	Ondina	525.050	53500.003330/2026-20	\N
791	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	537.600	53500.002478/2026-47	\N
792	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	537.600	53500.002478/2026-47	\N
793	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	537.600	53500.002478/2026-47	\N
794	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	537.600	53500.002478/2026-47	\N
795	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Centro Histórico	537.600	53500.002478/2026-47	\N
796	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Centro Histórico	537.600	53500.002478/2026-47	\N
797	3	Radio e Televisao Bandeirantes S.a.	Ondina	547.300	53500.003330/2026-20	\N
798	3	Radio e Televisao Bandeirantes S.a.	Ondina	550.500	53500.003330/2026-20	\N
799	3	Radio e Televisao Bandeirantes S.a.	Ondina	551.500	53500.003330/2026-20	\N
800	3	EMPRESA METROPOLITANA DE RADIODIFUSAO LTDA	Centro	552.250	53500.005152/2026-71	\N
801	3	EMPRESA METROPOLITANA DE RADIODIFUSAO LTDA	Barra	552.250	53500.005152/2026-71	\N
802	3	Radio e Televisao Bandeirantes S.a.	Ondina	554.150	53500.003330/2026-20	\N
803	3	Radio e Televisao Bandeirantes S.a.	Ondina	554.250	53500.003330/2026-20	\N
804	3	TV ARATU S/A	Ondina	554.400	53500.003653/2026-13	\N
805	3	TV ARATU S/A	Centro	554.800	53500.003653/2026-13	\N
806	3	TELEVISAO BAHIA S.A.	Centro	555.000	53500.006132/2026-18	\N
807	3	TELEVISAO BAHIA S.A.	Ondina	555.000	53500.006132/2026-18	\N
808	3	TV ARATU S/A	Ondina	555.400	53500.003653/2026-13	\N
809	3	TV ARATU S/A	Centro	555.800	53500.003653/2026-13	\N
810	3	Produtora Ciel Ltda	Ondina	555.900	53500.007294/2026-73	\N
811	3	Produtora Ciel Ltda	Ondina	556.200	53500.007294/2026-73	\N
812	3	Radio e Televisao Bandeirantes S.a.	Ondina	556.400	53500.003330/2026-20	\N
813	3	TV ARATU S/A	Ondina	556.600	53500.003653/2026-13	\N
814	3	TV ARATU S/A	Centro	556.800	53500.003653/2026-13	\N
815	3	TV ARATU S/A	Ondina	557.600	53500.003653/2026-13	\N
816	3	TV ARATU S/A	Centro	557.800	53500.003653/2026-13	\N
817	3	TELEVISAO BAHIA S.A.	Centro	558.000	53500.006132/2026-18	\N
818	3	TELEVISAO BAHIA S.A.	Ondina	558.000	53500.006132/2026-18	\N
819	3	Radio e Televisao Bandeirantes S.a.	Ondina	558.100	53500.003330/2026-20	\N
820	3	Produtora Ciel Ltda	Ondina	558.950	53500.007294/2026-73	\N
821	3	TELEVISAO BAHIA S.A.	Centro	560.000	53500.006132/2026-18	\N
822	3	TELEVISAO BAHIA S.A.	Ondina	560.000	53500.006132/2026-18	\N
823	3	Radio e Televisao Bandeirantes S.a.	Ondina	560.300	53500.003330/2026-20	\N
899	3	TELEVISAO BAHIA S.A.	Centro	639.900	53500.006132/2026-18	\N
824	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	563.100	53500.002478/2026-47	\N
825	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	563.100	53500.002478/2026-47	\N
826	3	Radio e Televisao Bandeirantes S.a.	Ondina	564.800	53500.003330/2026-20	\N
827	3	Radio e Televisao Bandeirantes S.a.	Ondina	565.700	53500.003330/2026-20	\N
828	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	566.100	53500.006565/2026-73	\N
829	3	TV ARATU S/A	Centro	566.200	53500.003653/2026-13	\N
830	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	566.475	53500.006565/2026-73	\N
831	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	566.750	53500.006565/2026-73	\N
832	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	566.800	53500.006507/2026-40	\N
833	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	566.925	53500.006565/2026-73	\N
834	3	TV ARATU S/A	Centro	567.200	53500.003653/2026-13	\N
835	3	Produtora Ciel Ltda	Ondina	567.400	53500.007294/2026-73	\N
836	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	567.450	53500.006565/2026-73	\N
837	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	567.700	53500.006507/2026-40	\N
838	3	Radio e Televisao Bandeirantes S.a.	Ondina	567.900	53500.003330/2026-20	\N
839	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	568.050	53500.006565/2026-73	\N
840	3	FOLE FURADO PRODUCOES EIRELI - ME	Centro	568.600	53500.006507/2026-40	\N
841	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	568.725	53500.006565/2026-73	\N
842	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	569.100	53500.006507/2026-40	\N
843	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	569.475	53500.006565/2026-73	\N
844	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	570.000	53500.006507/2026-40	\N
845	3	FOLE FURADO PRODUCOES EIRELI - ME	Centro	570.000	53500.006507/2026-40	\N
846	3	FOLE FURADO PRODUCOES EIRELI - ME	Centro	570.300	53500.006507/2026-40	\N
847	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	570.375	53500.006565/2026-73	\N
848	3	Produtora Ciel Ltda	Ondina	570.500	53500.007294/2026-73	\N
849	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	571.000	53500.006507/2026-40	\N
850	3	FOLE FURADO PRODUCOES EIRELI - ME	Centro	571.000	53500.006507/2026-40	\N
851	3	Produtora Ciel Ltda	Ondina	571.400	53500.007294/2026-73	\N
852	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	571.575	53500.006565/2026-73	\N
853	3	FOLE FURADO PRODUCOES EIRELI - ME	Centro	572.000	53500.006507/2026-40	\N
854	3	Radio e Televisao Bandeirantes S.a.	Ondina	584.150	53500.003330/2026-20	\N
855	3	Produtora Ciel Ltda	Ondina	590.150	53500.007294/2026-73	\N
856	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	590.625	53500.006565/2026-73	\N
857	3	TELEVISAO BAHIA S.A.	Centro	590.750	53500.006132/2026-18	\N
858	3	TELEVISAO BAHIA S.A.	Ondina	590.750	53500.006132/2026-18	\N
859	3	TV ARATU S/A	Centro	591.200	53500.003653/2026-13	\N
860	3	TV ARATU S/A	Centro	591.200	53500.003653/2026-13	\N
861	3	Produtora Ciel Ltda	Ondina	591.350	53500.007294/2026-73	\N
862	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	592.350	53500.006565/2026-73	\N
863	3	TELEVISAO BAHIA S.A.	Centro	592.750	53500.006132/2026-18	\N
864	3	TELEVISAO BAHIA S.A.	Ondina	592.750	53500.006132/2026-18	\N
865	3	TV ARATU S/A	Centro	593.000	53500.003653/2026-13	\N
866	3	Produtora Ciel Ltda	Ondina	594.200	53500.007294/2026-73	\N
867	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	595.050	53500.006565/2026-73	\N
868	3	TELEVISAO BAHIA S.A.	Ondina	595.250	53500.006132/2026-18	\N
869	3	TV ARATU S/A	Centro	595.400	53500.003653/2026-13	\N
870	3	TV ARATU S/A	Centro	595.700	53500.003653/2026-13	\N
871	3	TELEVISAO BAHIA S.A.	Centro	595.750	53500.006132/2026-18	\N
872	3	TV ARATU S/A	Ondina	595.800	53500.003653/2026-13	\N
873	3	Produtora Ciel Ltda	Ondina	602.900	53500.007294/2026-73	\N
874	3	TV ARATU S/A	Centro	613.000	53500.003653/2026-13	\N
875	3	Produtora Ciel Ltda	Ondina	614.200	53500.007294/2026-73	\N
876	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	614.375	53500.002478/2026-47	\N
877	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	614.375	53500.002478/2026-47	\N
878	3	TV ARATU S/A	Centro	614.500	53500.003653/2026-13	\N
879	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	614.600	53500.007112/2026-64	\N
880	3	Produtora Ciel Ltda	Ondina	615.100	53500.007294/2026-73	\N
881	3	Produtora Ciel Ltda	Ondina	615.500	53500.007294/2026-73	\N
882	3	Produtora Ciel Ltda	Ondina	615.650	53500.007294/2026-73	\N
883	3	Produtora Ciel Ltda	Ondina	616.100	53500.007294/2026-73	\N
884	3	Produtora Ciel Ltda	Ondina	616.825	53500.007294/2026-73	\N
885	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	617.450	53500.007112/2026-64	\N
886	3	TV ARATU S/A	Centro	617.500	53500.003653/2026-13	\N
887	3	Produtora Ciel Ltda	Ondina	618.825	53500.007294/2026-73	\N
888	3	TV ARATU S/A	Centro	619.000	53500.003653/2026-13	\N
889	3	Produtora Ciel Ltda	Ondina	619.800	53500.007294/2026-73	\N
890	3	Produtora Ciel Ltda	Ondina	628.950	53500.007294/2026-73	\N
891	3	TELEVISAO BAHIA S.A.	Centro	638.000	53500.006132/2026-18	\N
892	3	TELEVISAO BAHIA S.A.	Ondina	638.000	53500.006132/2026-18	\N
893	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	638.500	53500.006507/2026-40	\N
894	3	TELEVISAO BAHIA S.A.	Centro	638.700	53500.006132/2026-18	\N
895	3	TELEVISAO BAHIA S.A.	Ondina	638.800	53500.006132/2026-18	\N
896	3	TELEVISAO BAHIA S.A.	Centro	639.300	53500.006132/2026-18	\N
897	3	TELEVISAO BAHIA S.A.	Ondina	639.300	53500.006132/2026-18	\N
898	3	Radio e Televisao Bandeirantes S.a.	Ondina	639.700	53500.003330/2026-20	\N
900	3	TELEVISAO BAHIA S.A.	Ondina	639.900	53500.006132/2026-18	\N
901	3	BM PRODUCOES ARTISTICAS - EIRELI - EPP	Ondina	640.300	53500.006565/2026-73	\N
902	3	ANA PAULA CAMPOS PINHEIRO	Ondina	640.500	53500.002842/2026-79	\N
903	3	TELEVISAO BAHIA S.A.	Ondina	640.750	53500.006132/2026-18	\N
904	3	Radio e Televisao Bandeirantes S.a.	Ondina	641.500	53500.003330/2026-20	\N
905	3	Radio e Televisao Bandeirantes S.a.	Ondina	642.100	53500.003330/2026-20	\N
906	3	TELEVISAO BAHIA S.A.	Ondina	643.250	53500.006132/2026-18	\N
907	3	Radio e Televisao Bandeirantes S.a.	Ondina	643.900	53500.003330/2026-20	\N
908	3	Radio e Televisao Bandeirantes S.a.	Ondina	645.300	53500.003330/2026-20	\N
909	3	TELEVISAO BAHIA S.A.	Ondina	650.250	53500.006132/2026-18	\N
910	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	650.350	53500.007112/2026-64	\N
911	3	TV ARATU S/A	Ondina	650.500	53500.003653/2026-13	\N
912	3	ANA PAULA CAMPOS PINHEIRO	Ondina	650.700	53500.002842/2026-79	\N
913	3	ANA PAULA CAMPOS PINHEIRO	Centro	650.700	53500.002842/2026-79	\N
914	3	TV ARATU S/A	Ondina	651.200	53500.003653/2026-13	\N
915	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	651.225	53500.007112/2026-64	\N
916	3	TELEVISAO BAHIA S.A.	Ondina	651.250	53500.006132/2026-18	\N
917	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	651.775	53500.007112/2026-64	\N
918	3	TV ARATU S/A	Ondina	651.900	53500.003653/2026-13	\N
919	3	TV ARATU S/A	Ondina	652.000	53500.003653/2026-13	\N
920	3	ANA PAULA CAMPOS PINHEIRO	Ondina	652.500	53500.002842/2026-79	\N
921	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	652.575	53500.007112/2026-64	\N
922	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	652.925	53500.007112/2026-64	\N
923	3	TV ARATU S/A	Ondina	653.000	53500.003653/2026-13	\N
924	3	Radio e Televisao Bandeirantes S.a.	Ondina	653.500	53500.003330/2026-20	\N
925	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	653.675	53500.007112/2026-64	\N
926	3	TELEVISAO BAHIA S.A.	Ondina	654.000	53500.006132/2026-18	\N
927	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	655.225	53500.007112/2026-64	\N
928	3	TELEVISAO BAHIA S.A.	Ondina	655.750	53500.006132/2026-18	\N
929	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	655.825	53500.007112/2026-64	\N
930	3	TV ARATU S/A	Ondina	656.000	53500.003653/2026-13	\N
931	3	TV ARATU S/A	Ondina	656.300	53500.003653/2026-13	\N
932	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	656.350	53500.007112/2026-64	\N
933	3	TV ARATU S/A	Ondina	657.000	53500.003653/2026-13	\N
934	3	TV ARATU S/A	Ondina	657.200	53500.003653/2026-13	\N
935	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	657.225	53500.007112/2026-64	\N
936	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	657.775	53500.007112/2026-64	\N
937	3	TELEVISAO BAHIA S.A.	Ondina	658.250	53500.006132/2026-18	\N
938	3	ESTRADA VELHA PRODUCOES LTDA	Ondina	658.575	53500.007112/2026-64	\N
939	3	TELEVISAO BAHIA S.A.	Ondina	660.250	53500.006132/2026-18	\N
940	3	TV ARATU S/A	Ondina	661.000	53500.003653/2026-13	\N
941	3	TV ARATU S/A	Ondina	661.500	53500.003653/2026-13	\N
942	3	TV ARATU S/A	Ondina	661.800	53500.003653/2026-13	\N
943	3	TELEVISAO BAHIA S.A.	Ondina	662.000	53500.006132/2026-18	\N
944	3	TELEVISAO BAHIA S.A.	Centro	674.000	53500.006132/2026-18	\N
945	3	TELEVISAO BAHIA S.A.	Centro	675.000	53500.006132/2026-18	\N
946	3	TELEVISAO BAHIA S.A.	Ondina	675.000	53500.006132/2026-18	\N
947	3	TELEVISAO BAHIA S.A.	Ondina	675.000	53500.006132/2026-18	\N
948	3	TELEVISAO BAHIA S.A.	Ondina	675.750	53500.006132/2026-18	\N
949	3	TELEVISAO BAHIA S.A.	Centro	676.000	53500.006132/2026-18	\N
950	3	TELEVISAO BAHIA S.A.	Centro	676.700	53500.006132/2026-18	\N
951	3	TELEVISAO BAHIA S.A.	Ondina	676.700	53500.006132/2026-18	\N
952	3	TV ARATU S/A	Centro	677.000	53500.003653/2026-13	\N
953	3	TELEVISAO BAHIA S.A.	Centro	677.400	53500.006132/2026-18	\N
954	3	TELEVISAO BAHIA S.A.	Ondina	677.750	53500.006132/2026-18	\N
955	3	TELEVISAO BAHIA S.A.	Ondina	679.750	53500.006132/2026-18	\N
956	3	TELEVISAO BAHIA S.A.	Centro	686.500	53500.006132/2026-18	\N
957	3	TELEVISAO BAHIA S.A.	Ondina	686.500	53500.006132/2026-18	\N
958	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	687.400	53500.002478/2026-47	\N
959	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	687.400	53500.002478/2026-47	\N
960	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	687.400	53500.002478/2026-47	\N
961	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	687.400	53500.002478/2026-47	\N
962	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Centro Histórico	687.400	53500.002478/2026-47	\N
963	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Centro Histórico	687.400	53500.002478/2026-47	\N
964	3	TELEVISAO BAHIA S.A.	Ondina	688.500	53500.006132/2026-18	\N
965	3	TELEVISAO BAHIA S.A.	Ondina	690.500	53500.006132/2026-18	\N
966	3	TV ARATU S/A	Centro	691.200	53500.003653/2026-13	\N
967	3	TV ARATU S/A	Ondina	691.300	53500.003653/2026-13	\N
968	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	691.325	53500.002478/2026-47	\N
969	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	691.325	53500.002478/2026-47	\N
970	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	691.325	53500.002478/2026-47	\N
971	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	691.325	53500.002478/2026-47	\N
972	3	TV ARATU S/A	Ondina	692.000	53500.003653/2026-13	\N
973	3	ANA PAULA CAMPOS PINHEIRO	Centro	692.500	53500.002842/2026-79	\N
974	3	ANA PAULA CAMPOS PINHEIRO	Ondina	693.500	53500.002842/2026-79	\N
975	3	ANA PAULA CAMPOS PINHEIRO	Centro	693.500	53500.002842/2026-79	\N
976	3	ANA PAULA CAMPOS PINHEIRO	Ondina	695.100	53500.002842/2026-79	\N
977	3	TV ARATU S/A	Centro	695.700	53500.003653/2026-13	\N
978	3	ANA PAULA CAMPOS PINHEIRO	Ondina	696.500	53500.002842/2026-79	\N
979	3	TV ARATU S/A	Centro	696.500	53500.003653/2026-13	\N
980	3	TV ARATU S/A	Ondina	696.800	53500.003653/2026-13	\N
981	3	ANA PAULA CAMPOS PINHEIRO	Centro	697.100	53500.002842/2026-79	\N
982	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	697.875	53500.002478/2026-47	\N
983	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	697.875	53500.002478/2026-47	\N
984	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	697.875	53500.002478/2026-47	\N
985	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	697.875	53500.002478/2026-47	\N
986	3	TV ARATU S/A	Ondina	704.100	53500.003653/2026-13	\N
987	3	TV ARATU S/A	Centro	704.200	53500.003653/2026-13	\N
988	3	TV ARATU S/A	Ondina	706.200	53500.003653/2026-13	\N
989	3	TV ARATU S/A	Centro	712.100	53500.003653/2026-13	\N
990	3	TV ARATU S/A	Ondina	803.400	53500.003653/2026-13	\N
991	3	TV ARATU S/A	Ondina	813.600	53500.003653/2026-13	\N
992	3	EMPRESA METROPOLITANA DE RADIODIFUSAO LTDA	Centro	925.200	53500.005152/2026-71	\N
993	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	946.200	53500.006507/2026-40	\N
994	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	946.500	53500.006507/2026-40	\N
995	3	FOLE FURADO PRODUCOES EIRELI - ME	Ondina	946.900	53500.006507/2026-40	\N
996	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	1910.000	53500.002478/2026-47	\N
997	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	1910.000	53500.002478/2026-47	\N
998	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	1910.000	53500.002478/2026-47	\N
999	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	1910.000	53500.002478/2026-47	\N
1000	3	EMPRESA METROPOLITANA DE RADIODIFUSAO LTDA	Barra	1924.000	53500.005152/2026-71	\N
1001	3	Radio e Televisao Bandeirantes S.a.	Ondina	2061.000	53500.003330/2026-20	\N
1002	3	Radio e Televisao Bandeirantes S.a.	Ondina	2069.000	53500.003330/2026-20	\N
1003	3	Radio e Televisao Bandeirantes S.a.	Ondina	2090.000	53500.003330/2026-20	\N
1004	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Barra	3775.000	53500.002478/2026-47	\N
1005	3	Instituto de Radiodifusão Educativa da Bahia - IRDEB	Campo Grande	3775.000	53500.002478/2026-47	\N
1006	4	Py2 Radiosom Instalações, Com., Imp. e Exp. Ltda	Consolação	353.500	53500.005401/2026-29	\N
1007	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.050	53500.005028/2026-14	\N
1008	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.050	53500.005028/2026-14	\N
1009	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.050	53500.005028/2026-14	\N
1010	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.100	53500.005028/2026-14	\N
1011	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.100	53500.005028/2026-14	\N
1012	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.100	53500.005028/2026-14	\N
1013	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.150	53500.005028/2026-14	\N
1014	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.150	53500.005028/2026-14	\N
1015	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.150	53500.005028/2026-14	\N
1016	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.200	53500.005028/2026-14	\N
1017	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.200	53500.005028/2026-14	\N
1018	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.200	53500.005028/2026-14	\N
1019	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.250	53500.005028/2026-14	\N
1020	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.250	53500.005028/2026-14	\N
1021	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.250	53500.005028/2026-14	\N
1022	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.300	53500.005028/2026-14	\N
1023	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.300	53500.005028/2026-14	\N
1024	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.350	53500.005028/2026-14	\N
1025	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.350	53500.005028/2026-14	\N
1026	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.400	53500.005028/2026-14	\N
1027	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.400	53500.005028/2026-14	\N
1028	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.450	53500.005028/2026-14	\N
1029	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.450	53500.005028/2026-14	\N
1030	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.500	53500.005028/2026-14	\N
1031	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.500	53500.005028/2026-14	\N
1032	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.600	53500.005028/2026-14	\N
1033	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.600	53500.005028/2026-14	\N
1034	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.650	53500.005028/2026-14	\N
1035	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.650	53500.005028/2026-14	\N
1036	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.700	53500.005028/2026-14	\N
1037	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.700	53500.005028/2026-14	\N
1038	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.750	53500.005028/2026-14	\N
1039	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	381.750	53500.005028/2026-14	\N
1040	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	382.200	53500.005028/2026-14	\N
1041	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.050	53500.005028/2026-14	\N
1042	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.100	53500.005028/2026-14	\N
1043	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.150	53500.005028/2026-14	\N
1044	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.200	53500.005028/2026-14	\N
1045	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.250	53500.005028/2026-14	\N
1046	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.300	53500.005028/2026-14	\N
1047	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.350	53500.005028/2026-14	\N
1048	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.400	53500.005028/2026-14	\N
1049	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.450	53500.005028/2026-14	\N
1050	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.500	53500.005028/2026-14	\N
1051	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.600	53500.005028/2026-14	\N
1052	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.650	53500.005028/2026-14	\N
1053	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.700	53500.005028/2026-14	\N
1054	4	SISCOM TELECOMUNICACOES LTDA - EPP	Santana	391.750	53500.005028/2026-14	\N
1055	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.038	53500.006633/2026-02	\N
1056	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.063	53500.006633/2026-02	\N
1057	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.088	53500.006633/2026-02	\N
1058	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.113	53500.006633/2026-02	\N
1059	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.138	53500.006633/2026-02	\N
1060	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.163	53500.006633/2026-02	\N
1061	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.538	53500.006633/2026-02	\N
1062	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.563	53500.006633/2026-02	\N
1063	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.588	53500.006633/2026-02	\N
1064	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.613	53500.006633/2026-02	\N
1065	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.638	53500.006633/2026-02	\N
1066	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.663	53500.006633/2026-02	\N
1067	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.713	53500.006633/2026-02	\N
1068	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.763	53500.006633/2026-02	\N
1069	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.788	53500.006633/2026-02	\N
1070	4	Engenho da Arte Emp Cult Ltda	Pacaembu	442.813	53500.006633/2026-02	\N
1071	4	Radio e Televisao Bandeirantes S.A.	Santana	450.500	53500.005113/2026-74	\N
1072	4	Radio e Televisao Bandeirantes S.A.	Santana	450.500	53500.005113/2026-74	\N
1073	4	Radio e Televisao Bandeirantes S.A.	Santana	452.100	53500.005113/2026-74	\N
1074	4	Radio e Televisao Bandeirantes S.A.	Santana	452.100	53500.005113/2026-74	\N
1075	4	Radio e Televisao Bandeirantes S.A.	Santana	453.300	53500.003339/2026-31	\N
1076	4	Radio e Televisao Bandeirantes S.A.	Santana	453.300	53500.003339/2026-31	\N
1077	4	Radio e Televisao Bandeirantes S.A.	Santana	456.600	53500.003339/2026-31	\N
1078	4	Radio e Televisao Bandeirantes S.A.	Santana	456.600	53500.003339/2026-31	\N
1079	4	Radio e Televisao Bandeirantes S.A.	Santana	460.475	53500.003339/2026-31	\N
1080	4	Radio e Televisao Bandeirantes S.A.	Santana	460.475	53500.003339/2026-31	\N
1081	4	Radio e Televisao Bandeirantes S.A.	Santana	460.475	53500.005113/2026-74	\N
1082	4	Radio e Televisao Bandeirantes S.A.	Santana	460.475	53500.005113/2026-74	\N
1083	4	Radio e Televisao Bandeirantes S.A.	Santana	462.475	53500.003339/2026-31	\N
1084	4	Radio e Televisao Bandeirantes S.A.	Santana	462.475	53500.003339/2026-31	\N
1085	4	Radio e Televisao Bandeirantes S.A.	Santana	462.475	53500.005113/2026-74	\N
1086	4	Radio e Televisao Bandeirantes S.A.	Santana	462.475	53500.005113/2026-74	\N
1087	4	Radio e Televisao Bandeirantes S.A.	Santana	468.275	53500.003339/2026-31	\N
1088	4	Radio e Televisao Bandeirantes S.A.	Santana	468.275	53500.003339/2026-31	\N
1089	4	Radio e Televisao Bandeirantes S.A.	Santana	469.775	53500.003339/2026-31	\N
1090	4	Radio e Televisao Bandeirantes S.A.	Santana	469.775	53500.003339/2026-31	\N
1091	4	Tukason Locação de Som e Luz EIRELI	Santana	470.150	53500.107717/2025-73	\N
1092	4	Radio e Televisao Bandeirantes S.A.	Santana	474.675	53500.003339/2026-31	\N
1093	4	TV OMEGA LTDA	Parque Anhembi	475.250	53500.006799/2026-11	\N
1094	4	Radio e Televisao Bandeirantes S.A.	Santana	475.500	53500.005113/2026-74	\N
1095	4	Tukason Locação de Som e Luz EIRELI	Santana	476.150	53500.107717/2025-73	\N
1096	4	Radio e Televisao Bandeirantes S.A.	Santana	479.575	53500.003339/2026-31	\N
1097	4	Radio e Televisao Bandeirantes S.A.	Santana	480.700	53500.003339/2026-31	\N
1098	4	Tukason Locação de Som e Luz EIRELI	Santana	482.150	53500.107717/2025-73	\N
1099	4	Radio e Televisao Bandeirantes S.a.	Santana	482.800	53500.007182/2026-12	\N
1100	4	Radio e Televisao Bandeirantes S.a.	Santana	484.000	53500.007182/2026-12	\N
1101	4	Radio e Televisao Bandeirantes S.A.	Santana	485.675	53500.003339/2026-31	\N
1102	4	Radio e Televisao Bandeirantes S.A.	Santana	486.125	53500.003339/2026-31	\N
1103	4	TV OMEGA LTDA	Parque Anhembi	486.125	53500.006799/2026-11	\N
1104	4	Radio e Televisao Bandeirantes S.a.	Santana	486.400	53500.007182/2026-12	\N
1105	4	Radio e Televisao Bandeirantes S.A.	Santana	487.000	53500.005113/2026-74	\N
1106	4	Radio e Televisao Bandeirantes S.a.	Santana	487.000	53500.007182/2026-12	\N
1107	4	Radio e Televisao Bandeirantes S.A.	Santana	487.575	53500.003339/2026-31	\N
1108	4	Tukason Locação de Som e Luz EIRELI	Santana	488.150	53500.107717/2025-73	\N
1109	4	TV OMEGA LTDA	Parque Anhembi	488.225	53500.006799/2026-11	\N
1110	4	Radio e Televisao Bandeirantes S.A.	Santana	489.225	53500.003339/2026-31	\N
1111	4	Radio e Televisao Bandeirantes S.A.	Santana	490.150	53500.003339/2026-31	\N
1112	4	Radio e Televisao Bandeirantes S.A.	Santana	491.300	53500.003339/2026-31	\N
1113	4	Radio e Televisao Bandeirantes S.A.	Santana	491.750	53500.003339/2026-31	\N
1114	4	TV OMEGA LTDA	Parque Anhembi	493.250	53500.006799/2026-11	\N
1115	4	Tukason Locação de Som e Luz EIRELI	Santana	494.125	53500.107717/2025-73	\N
1116	4	Tukason Locação de Som e Luz EIRELI	Santana	500.375	53500.107717/2025-73	\N
1117	4	Tukason Locação de Som e Luz EIRELI	Santana	500.725	53500.107717/2025-73	\N
1118	4	Tukason Locação de Som e Luz EIRELI	Santana	501.100	53500.107717/2025-73	\N
1119	4	Radio e Televisao Bandeirantes S.A.	Santana	501.250	53500.005113/2026-74	\N
1120	4	Tukason Locação de Som e Luz EIRELI	Santana	501.525	53500.107717/2025-73	\N
1121	4	Tukason Locação de Som e Luz EIRELI	Santana	502.000	53500.107717/2025-73	\N
1122	4	Tukason Locação de Som e Luz EIRELI	Santana	502.375	53500.107717/2025-73	\N
1123	4	Tukason Locação de Som e Luz EIRELI	Santana	502.750	53500.107717/2025-73	\N
1124	4	Radio e Televisao Bandeirantes S.a.	Santana	503.200	53500.007182/2026-12	\N
1125	4	Radio e Televisao Bandeirantes S.A.	Santana	503.375	53500.005113/2026-74	\N
1126	4	Tukason Locação de Som e Luz EIRELI	Santana	503.425	53500.107717/2025-73	\N
1127	4	Tukason Locação de Som e Luz EIRELI	Santana	503.775	53500.107717/2025-73	\N
1128	4	Tukason Locação de Som e Luz EIRELI	Santana	504.300	53500.107717/2025-73	\N
1129	4	Radio e Televisao Bandeirantes S.a.	Santana	505.000	53500.007182/2026-12	\N
1130	4	Tukason Locação de Som e Luz EIRELI	Santana	505.250	53500.107717/2025-73	\N
1131	4	TV OMEGA LTDA	Parque Anhembi	505.500	53500.006799/2026-11	\N
1132	4	Tukason Locação de Som e Luz EIRELI	Santana	505.675	53500.107717/2025-73	\N
1133	4	Tukason Locação de Som e Luz EIRELI	Santana	506.025	53500.107717/2025-73	\N
1134	4	Radio e Televisao Bandeirantes S.A.	Santana	506.700	53500.003339/2026-31	\N
1135	4	Radio e Televisao Bandeirantes S.A.	Santana	508.025	53500.003339/2026-31	\N
1136	4	Tukason Locação de Som e Luz EIRELI	Santana	512.125	53500.107717/2025-73	\N
1137	4	TV OMEGA LTDA	Parque Anhembi	517.875	53500.006799/2026-11	\N
1138	4	Tukason Locação de Som e Luz EIRELI	Santana	518.125	53500.107717/2025-73	\N
1139	4	Tukason Locação de Som e Luz EIRELI	Santana	524.150	53500.107717/2025-73	\N
1140	4	Tukason Locação de Som e Luz EIRELI	Santana	530.150	53500.107717/2025-73	\N
1141	4	Radio e Televisao Bandeirantes S.A.	Santana	530.275	53500.005113/2026-74	\N
1142	4	Tukason Locação de Som e Luz EIRELI	Santana	536.150	53500.107717/2025-73	\N
1143	4	TV OMEGA LTDA	Parque Anhembi	539.125	53500.006799/2026-11	\N
1144	4	Tukason Locação de Som e Luz EIRELI	Santana	542.150	53500.107717/2025-73	\N
1145	4	Radio e Televisao Bandeirantes S.A.	Santana	547.300	53500.005113/2026-74	\N
1146	4	Tukason Locação de Som e Luz EIRELI	Santana	548.150	53500.107717/2025-73	\N
1147	4	Globo Comunicação e Participações S/A	Santana	548.875	53500.006798/2026-76	\N
1148	4	Globo Comunicação e Participações S/A	Santana	549.325	53500.006798/2026-76	\N
1149	4	Globo Comunicação e Participações S/A	Santana	549.875	53500.006798/2026-76	\N
1150	4	Globo Comunicação e Participações S/A	Santana	550.775	53500.006798/2026-76	\N
1151	4	Globo Comunicação e Participações S/A	Santana	551.275	53500.006798/2026-76	\N
1152	4	Globo Comunicação e Participações S/A	Santana	552.150	53500.006798/2026-76	\N
1153	4	Globo Comunicação e Participações S/A	Santana	552.750	53500.006798/2026-76	\N
1154	4	Globo Comunicação e Participações S/A	Santana	553.125	53500.006798/2026-76	\N
1155	4	Globo Comunicação e Participações S/A	Santana	553.600	53500.006798/2026-76	\N
1156	4	Tukason Locação de Som e Luz EIRELI	Santana	554.150	53500.107717/2025-73	\N
1157	4	Radio e Televisao Bandeirantes S.A.	Santana	556.300	53500.003339/2026-31	\N
1158	4	Radio e Televisao Bandeirantes S.A.	Santana	556.400	53500.005113/2026-74	\N
1159	4	Radio e Televisao Bandeirantes S.A.	Santana	558.100	53500.005113/2026-74	\N
1160	4	Globo Comunicação e Participações S/A	Santana	559.200	53500.006798/2026-76	\N
1161	4	Globo Comunicação e Participações S/A	Santana	560.000	53500.006798/2026-76	\N
1162	4	Tukason Locação de Som e Luz EIRELI	Santana	560.150	53500.107717/2025-73	\N
1163	4	Radio e Televisao Bandeirantes S.A.	Santana	560.300	53500.005113/2026-74	\N
1164	4	Globo Comunicação e Participações S/A	Santana	561.400	53500.006798/2026-76	\N
1165	4	Globo Comunicação e Participações S/A	Santana	562.400	53500.006798/2026-76	\N
1166	4	Radio e Televisao Bandeirantes S.A.	Santana	564.800	53500.005113/2026-74	\N
1167	4	Radio e Televisao Bandeirantes S.A.	Santana	565.700	53500.005113/2026-74	\N
1168	4	Tukason Locação de Som e Luz EIRELI	Santana	566.150	53500.107717/2025-73	\N
1169	4	TV OMEGA LTDA	Parque Anhembi	570.100	53500.006799/2026-11	\N
1170	4	Tukason Locação de Som e Luz EIRELI	Santana	572.150	53500.107717/2025-73	\N
1171	4	Globo Comunicação e Participações S/A	Santana	572.400	53500.006798/2026-76	\N
1172	4	Globo Comunicação e Participações S/A	Santana	576.100	53500.006798/2026-76	\N
1173	4	Tukason Locação de Som e Luz EIRELI	Santana	578.125	53500.107717/2025-73	\N
1174	4	Globo Comunicação e Participações S/A	Santana	579.500	53500.006798/2026-76	\N
1175	4	Globo Comunicação e Participações S/A	Santana	582.700	53500.006798/2026-76	\N
1176	4	Tukason Locação de Som e Luz EIRELI	Santana	584.125	53500.107717/2025-73	\N
1177	4	TV OMEGA LTDA	Parque Anhembi	584.200	53500.006799/2026-11	\N
1178	4	Tukason Locação de Som e Luz EIRELI	Santana	590.150	53500.107717/2025-73	\N
1179	4	TV OMEGA LTDA	Parque Anhembi	591.150	53500.006799/2026-11	\N
1180	4	Tukason Locação de Som e Luz EIRELI	Santana	596.150	53500.107717/2025-73	\N
1181	4	Tukason Locação de Som e Luz EIRELI	Santana	602.125	53500.107717/2025-73	\N
1182	4	Tukason Locação de Som e Luz EIRELI	Santana	604.675	53500.107717/2025-73	\N
1183	4	Tukason Locação de Som e Luz EIRELI	Santana	608.175	53500.107717/2025-73	\N
1184	4	Tukason Locação de Som e Luz EIRELI	Santana	608.825	53500.107717/2025-73	\N
1185	4	Tukason Locação de Som e Luz EIRELI	Santana	609.250	53500.107717/2025-73	\N
1186	4	Tukason Locação de Som e Luz EIRELI	Santana	610.175	53500.107717/2025-73	\N
1187	4	Tukason Locação de Som e Luz EIRELI	Santana	610.550	53500.107717/2025-73	\N
1188	4	Tukason Locação de Som e Luz EIRELI	Santana	611.175	53500.107717/2025-73	\N
1189	4	Tukason Locação de Som e Luz EIRELI	Santana	612.650	53500.107717/2025-73	\N
1190	4	Tukason Locação de Som e Luz EIRELI	Santana	613.550	53500.107717/2025-73	\N
1191	4	Tukason Locação de Som e Luz EIRELI	Santana	614.150	53500.107717/2025-73	\N
1192	4	Radio e Televisao Bandeirantes S.A.	Santana	618.750	53500.005113/2026-74	\N
1193	4	Tukason Locação de Som e Luz EIRELI	Santana	620.150	53500.107717/2025-73	\N
1194	4	Radio e Televisao Bandeirantes S.A.	Santana	620.275	53500.005113/2026-74	\N
1195	4	Radio e Televisao Bandeirantes S.A.	Santana	624.750	53500.005113/2026-74	\N
1196	4	TV OMEGA LTDA	Parque Anhembi	625.500	53500.006799/2026-11	\N
1197	4	Tukason Locação de Som e Luz EIRELI	Santana	626.025	53500.107717/2025-73	\N
1198	4	Radio e Televisao Bandeirantes S.A.	Santana	627.725	53500.005113/2026-74	\N
1199	4	Radio e Televisao Bandeirantes S.A.	Santana	629.375	53500.005113/2026-74	\N
1200	4	Tukason Locação de Som e Luz EIRELI	Santana	632.100	53500.107717/2025-73	\N
1201	4	Radio e Televisao Bandeirantes S.A.	Santana	632.175	53500.005113/2026-74	\N
1202	4	Radio e Televisao Bandeirantes S.a.	Santana	734.100	53500.007182/2026-12	\N
1203	4	Radio e Televisao Bandeirantes S.a.	Santana	735.275	53500.007182/2026-12	\N
1204	4	Radio e Televisao Bandeirantes S.a.	Santana	736.150	53500.007182/2026-12	\N
1205	4	Radio e Televisao Bandeirantes S.a.	Santana	737.675	53500.007182/2026-12	\N
1206	4	Radio e Televisao Bandeirantes S.a.	Santana	738.250	53500.007182/2026-12	\N
1207	4	Radio e Televisao Bandeirantes S.a.	Santana	739.025	53500.007182/2026-12	\N
1208	4	Radio e Televisao Bandeirantes S.a.	Santana	740.175	53500.007182/2026-12	\N
1209	4	Radio e Televisao Bandeirantes S.a.	Santana	741.300	53500.007182/2026-12	\N
1210	4	Py2 Radiosom Instalacoes, Comercio, Importacao e Exportacao Ltda	Consolação	805.875	53500.005401/2026-29	\N
1211	4	Py2 Radiosom Instalacoes, Comercio, Importacao e Exportacao Ltda	Parque Ibirapuera	938.000	53500.005401/2026-29	\N
1212	4	Py2 Radiosom Instalacoes, Comercio, Importacao e Exportacao Ltda	Pinheiros	938.000	53500.005401/2026-29	\N
1213	4	Radio e Televisao Bandeirantes S.a.	Santana	1881.000	53500.007182/2026-12	\N
1214	4	Radio e Televisao Bandeirantes S.a.	Santana	1882.600	53500.007182/2026-12	\N
1215	4	Radio e Televisao Bandeirantes S.a.	Santana	1883.800	53500.007182/2026-12	\N
1216	4	Radio e Televisao Bandeirantes S.a.	Santana	1884.200	53500.007182/2026-12	\N
1217	4	Radio e Televisao Bandeirantes S.a.	Santana	1910.000	53500.007182/2026-12	\N
1218	4	Radio e Televisao Bandeirantes S.a.	Santana	1910.600	53500.007182/2026-12	\N
1219	4	Radio e Televisao Bandeirantes S.a.	Santana	1911.200	53500.007182/2026-12	\N
1220	4	Radio e Televisao Bandeirantes S.a.	Santana	1911.800	53500.007182/2026-12	\N
1221	4	Radio e Televisao Bandeirantes S.a.	Santana	1912.400	53500.007182/2026-12	\N
1222	4	Radio e Televisao Bandeirantes S.a.	Santana	1913.000	53500.007182/2026-12	\N
1223	4	Radio e Televisao Bandeirantes S.a.	Santana	1913.600	53500.007182/2026-12	\N
1224	4	Radio e Televisao Bandeirantes S.a.	Santana	1914.200	53500.007182/2026-12	\N
1225	4	Radio e Televisao Bandeirantes S.A.	Santana	1921.536	53500.005113/2026-74	\N
1226	4	Radio e Televisao Bandeirantes S.A.	Santana	1923.264	53500.005113/2026-74	\N
1227	4	Radio e Televisao Bandeirantes S.A.	Santana	1924.992	53500.005113/2026-74	\N
1228	4	Radio e Televisao Bandeirantes S.A.	Santana	1926.720	53500.005113/2026-74	\N
1229	4	Radio e Televisao Bandeirantes S.A.	Santana	1928.448	53500.005113/2026-74	\N
1230	4	Globo Comunicação e Participações S/A	Santana	2010.000	53500.006798/2026-76	\N
1231	4	Globo Comunicação e Participações S/A	Santana	2030.000	53500.006798/2026-76	\N
1232	4	Globo Comunicação e Participações S/A	Santana	2050.000	53500.006798/2026-76	\N
1233	4	Globo Comunicação e Participações S/A	Santana	2070.000	53500.006798/2026-76	\N
1234	4	Globo Comunicação e Participações S/A	Santana	2090.000	53500.006798/2026-76	\N
1235	4	Globo Comunicação e Participações S/A	Santana	2210.000	53500.006798/2026-76	\N
1236	4	Globo Comunicação e Participações S/A	Santana	2230.000	53500.006798/2026-76	\N
1237	4	Globo Comunicação e Participações S/A	Santana	2250.000	53500.006798/2026-76	\N
1238	4	Globo Comunicação e Participações S/A	Santana	2270.000	53500.006798/2026-76	\N
1239	4	Globo Comunicação e Participações S/A	Santana	2290.000	53500.006798/2026-76	\N
1240	4	Radio e Televisao Bandeirantes S.a.	Santana	2435.000	53500.007182/2026-12	\N
1241	4	Radio e Televisao Bandeirantes S.a.	Santana	2461.000	53500.007182/2026-12	\N
1242	4	Radio e Televisao Bandeirantes S.a.	Santana	5260.000	53500.007182/2026-12	\N
1243	4	Radio e Televisao Bandeirantes S.a.	Santana	5280.000	53500.007182/2026-12	\N
1244	4	Radio e Televisao Bandeirantes S.a.	Santana	5300.000	53500.007182/2026-12	\N
1245	4	Radio e Televisao Bandeirantes S.a.	Santana	5320.000	53500.007182/2026-12	\N
1246	4	Radio e Televisao Bandeirantes S.a.	Santana	5520.000	53500.007182/2026-12	\N
1247	4	Radio e Televisao Bandeirantes S.a.	Santana	5540.000	53500.007182/2026-12	\N
1248	4	Radio e Televisao Bandeirantes S.a.	Santana	5550.000	53500.007182/2026-12	\N
1249	4	Radio e Televisao Bandeirantes S.a.	Santana	5560.000	53500.007182/2026-12	\N
1250	4	Radio e Televisao Bandeirantes S.a.	Santana	5580.000	53500.007182/2026-12	\N
1251	4	Radio e Televisao Bandeirantes S.a.	Santana	5660.000	53500.007182/2026-12	\N
1252	4	Radio e Televisao Bandeirantes S.a.	Santana	5680.000	53500.007182/2026-12	\N
1253	4	Radio e Televisao Bandeirantes S.a.	Santana	5700.000	53500.007182/2026-12	\N
1254	4	Globo Comunicação e Participações S/A	Santana	7180.000	53500.006798/2026-76	\N
1255	4	Globo Comunicação e Participações S/A	Santana	7220.000	53500.006798/2026-76	\N
\.


--
-- Name: bsr_erb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bsr_erb_id_seq', 27, true);


--
-- Name: estacoes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estacoes_id_seq', 8, true);


--
-- Name: eventos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.eventos_id_seq', 5, true);


--
-- Name: ocorrencias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ocorrencias_id_seq', 676, true);


--
-- Name: opcoes_identificacao_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.opcoes_identificacao_id_seq', 24, true);


--
-- Name: tabela_ute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tabela_ute_id_seq', 1255, true);


--
-- Name: bsr_erb bsr_erb_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bsr_erb
    ADD CONSTRAINT bsr_erb_pkey PRIMARY KEY (id);


--
-- Name: estacoes estacoes_evento_id_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacoes
    ADD CONSTRAINT estacoes_evento_id_nome_key UNIQUE (evento_id, nome);


--
-- Name: estacoes estacoes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacoes
    ADD CONSTRAINT estacoes_pkey PRIMARY KEY (id);


--
-- Name: eventos eventos_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos
    ADD CONSTRAINT eventos_nome_key UNIQUE (nome);


--
-- Name: eventos eventos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos
    ADD CONSTRAINT eventos_pkey PRIMARY KEY (id);


--
-- Name: ocorrencias ocorrencias_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocorrencias
    ADD CONSTRAINT ocorrencias_pkey PRIMARY KEY (id);


--
-- Name: opcoes_identificacao opcoes_identificacao_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.opcoes_identificacao
    ADD CONSTRAINT opcoes_identificacao_pkey PRIMARY KEY (id);


--
-- Name: tabela_ute tabela_ute_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabela_ute
    ADD CONSTRAINT tabela_ute_pkey PRIMARY KEY (id);


--
-- Name: idx_ocorr_busca_trgm; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ocorr_busca_trgm ON public.ocorrencias USING gin (observacoes public.gin_trgm_ops);


--
-- Name: idx_ocorr_evento_situacao; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ocorr_evento_situacao ON public.ocorrencias USING btree (evento_id, situacao);


--
-- Name: idx_ocorr_frequencia; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ocorr_frequencia ON public.ocorrencias USING btree (evento_id, frequencia_mhz);


--
-- Name: idx_ute_evento_freq; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ute_evento_freq ON public.tabela_ute USING btree (evento_id, frequencia_mhz);


--
-- Name: ocorrencias trg_ocorr_upd; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_ocorr_upd BEFORE UPDATE ON public.ocorrencias FOR EACH ROW EXECUTE FUNCTION public.set_atualizado_em();


--
-- Name: bsr_erb bsr_erb_evento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bsr_erb
    ADD CONSTRAINT bsr_erb_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventos(id) ON DELETE CASCADE;


--
-- Name: estacoes estacoes_evento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estacoes
    ADD CONSTRAINT estacoes_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventos(id) ON DELETE CASCADE;


--
-- Name: ocorrencias ocorrencias_estacao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocorrencias
    ADD CONSTRAINT ocorrencias_estacao_id_fkey FOREIGN KEY (estacao_id) REFERENCES public.estacoes(id) ON DELETE SET NULL;


--
-- Name: ocorrencias ocorrencias_evento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocorrencias
    ADD CONSTRAINT ocorrencias_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventos(id) ON DELETE CASCADE;


--
-- Name: opcoes_identificacao opcoes_identificacao_evento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.opcoes_identificacao
    ADD CONSTRAINT opcoes_identificacao_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventos(id) ON DELETE CASCADE;


--
-- Name: tabela_ute tabela_ute_evento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tabela_ute
    ADD CONSTRAINT tabela_ute_evento_id_fkey FOREIGN KEY (evento_id) REFERENCES public.eventos(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict NNI4QDQMQ7lNY4Lttuf3HfSCIh1khg3l4KPnzPWTNO4AeFeW4guU5uKxaXPfos9

