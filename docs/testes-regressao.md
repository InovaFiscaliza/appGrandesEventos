# Base de testes de regressão

O escopo desta base é o funcionamento online do sistema. Offline, filas locais
e sincronização após reconexão estão fora do escopo por decisão do usuário.
Isso não altera nem remove os recursos offline existentes na aplicação.

## Comandos de validação

Camada rápida, antes e depois de cada alteração, sem iniciar servidor ou banco:

```powershell
uv run --locked python -m scripts.testar_regressoes
```

Todas as camadas online, na raiz do projeto, com a máquina do Podman iniciada:

```powershell
.\scripts\testar_todas_camadas.ps1
```

O comando completo executa a camada rápida, cria um PostgreSQL 16 exclusivo,
instala Chromium se necessário e executa persistência e navegador. Remove apenas
o container criado por aquela execução e seu volume anônimo de dados sintéticos,
inclusive quando os testes falham. Não monta volumes de trabalho.

Para executar persistência sem navegador:

```powershell
.\scripts\testar_todas_camadas.ps1 -SemNavegador
```

As dependências de desenvolvimento são gerenciadas pelo `uv`; sincronizar com
`uv sync --locked`. Playwright e pglast não foram adicionados às dependências
de produção. Um resultado verde na camada rápida não substitui as demais.

O executor mantém uma lista explícita de módulos seguros. Durante a importação
e execução, bloqueia conexões SQLAlchemy antes da abertura da conexão. Mesmo
que o código capture o erro e acione um fallback, a tentativa reprova a suíte.
Esse bloqueio não cobre clientes de banco que contornem SQLAlchemy. Os módulos
da camada rápida devem continuar usando dados simulados e sem serviços externos.

**Não incluir `scripts/testar_insercao_emissao.py` nesta suíte:** esse script
grava uma emissão no banco configurado. Não usá-lo como validação de rotina.

## Estado validado

### Conclusão de tickets — 16/10/2026

A conclusão verifica todas as emissões e todos os incidentes vinculados, antes
de gravar qualquer mudança. Havendo pendências, o ticket permanece aberto e a
tela identifica cada registro e seus campos faltantes. Salvar como pendente
continua permitido. Campos opcionais não passam a ser obrigatórios.

Nas emissões, além das regras de conclusão existentes, são exigidos local,
autorização esclarecida e resposta UTE; UTE positiva exige Processo SEI ou Ato.
Classificações de autorização e interferência indefinidas precisam ser esclarecidas.
Nos incidentes, são conferidos tipo, fiscal, local e observações; registros
excluídos não podem ser concluídos pelo ticket. As mudanças de situação e de
responsável pela conclusão geram auditoria específica nos dois tipos de registro.

Validação: 109 testes rápidos e 18 testes PostgreSQL isolados aprovados com
`scripts/testar_todas_camadas.ps1 -SemNavegador`. A nova jornada vincula duas
emissões e dois incidentes, confirma o bloqueio sem alteração, edita todos pelos
formulários reais e verifica a conclusão e a consulta de auditoria. Chromium
não foi executado nesta alteração.

Execução local em 14/10/2026:

| Camada | Casos | Resultado |
| --- | --- | --- |
| Contratos e HTTP sem banco | 98 | Todos passaram |
| PostgreSQL real isolado | 17 | Todos passaram |
| Chromium online | 8 | Todos passaram |
| Total | 123 | Todos passaram |

O comando completo passou com PostgreSQL descartável e Chromium. A contagem
não representa cobertura integral. As falhas registradas em 11/10 foram
resolvidas sem remover ou ignorar os testes. A jornada de pendências agora
cobre salvar, localizar pelo menu, abrir, editar e submeter, em desktop e celular.
O contador também é verificado com diferentes origens, incluindo `FISCAL`.
A consulta operacional da coordenação e sua API excluem emissões com situação
`Concluída Pelo Coordenador`, inclusive com variações de maiúsculas e espaços.
Emissões pendentes e concluídas pelo fiscal permanecem disponíveis conforme
as regras existentes; busca geral e acesso específico por ticket são preservados.
Na etiquetagem, o mesmo intervalo pode ser usado em categorias diferentes;
sobreposições na mesma categoria continuam bloqueadas. A cobertura inclui
troca de categoria, edição do próprio registro, escopo entre eventos e migração
com preservação de etiqueta legada. A migração `0005` deve ser aplicada pela
automação de implantação antes de usar essa regra no servidor existente.

O calendário mensal em `/escalas` preserva o filtro de fiscal na paginação,
permite escolher um mês e mantém as tabelas existentes. Os testes rápidos
cobrem fevereiro bissexto, limites de datas e virada de ano. Playwright verifica
meses anterior/próximo, seleção direta, mês vazio, horários noturnos e ausência
de rolagem horizontal da página em desktop e celular; a tabela do calendário
mantém sua própria rolagem horizontal quando necessário.
O calendário fica abaixo dos totais mensais e reutiliza os estilos de cabeçalho
e jornada da coordenação. As jornadas de navegador verificam cores diferentes
por fiscal e sua estabilidade após filtrar ou mudar de mês, além da posição
do calendário abaixo do resumo de horas.

| Área | Contratos protegidos | Módulo |
| --- | --- | --- |
| Login | Fiscal existente, senha obrigatória, papel permitido, login no evento | `scripts.testar_login_criar_evento` |
| Criação de evento | Sessão restrita, bloqueio de outros módulos, validação preservando formulário, auditoria e liberação do evento criado | `scripts.testar_login_criar_evento` |
| Emissões pendentes | Autoria e tipos nativos, contador, edição das próprias pendentes não submetidas | `scripts.testar_login_criar_evento` |
| Emissões em tickets | Popup e fotos de outro cadastrador, salvamento com usuário da sessão, vínculo, fiscal, evento e somente leitura após conclusão | `scripts.testar_login_criar_evento` |
| Busca e coordenação | Busca do evento, autoria, ordem do cadastro e exclusão de incidentes já vinculados da seleção | `scripts.testar_login_criar_evento` |
| Consulta de tickets | Todos os status e atribuições, detalhes sem edição, isolamento por evento e sessão obrigatória | `scripts.testar_consulta_tickets` |
| Navegação HTTP | Redirecionamento de módulos e gravações sem login, cookie inválido e arquivos estáticos acessíveis | `scripts.testar_fluxos_base` |
| Middleware | Sessão incompleta, permissões por perfil/evento, sessão de criação inválida e histórico sem consulta da lista completa de eventos | `scripts.testar_fluxos_base` |
| Cadastro de emissões | Salvar pendente sem submeter, submissão, autoria pela sessão, consulta de conflitos antes da gravação, aviso não bloqueante, UTE, participantes e anexos | `scripts.testar_fluxos_operacionais` |
| Tratamento e devolução | Providências obrigatórias, papéis/status, ausência de sucesso após erro, auditoria e motivo visível ao fiscal | `scripts.testar_fluxos_operacionais` |
| Etiquetagem | Consulta da central e de todas as frequências da lista, largura/local, API, exclusão do próprio ID na edição, numeração e duplicidades | `scripts.testar_etiquetagem_incidentes` |
| Fotos e segurança dos testes | Exclusão direcionada sem excluir incidente, contexto de ticket, erro/usuário ausente e recusa de banco de trabalho | `scripts.testar_etiquetagem_incidentes` |
| Jornada real de emissão e ticket | Login, cadastro, submissão, vínculo, conclusão pelo fiscal, devolução com motivo, nova conclusão e auditoria consultável | `scripts.testar_persistencia` |
| Fotos e etiquetagem persistidas | Nomes e sequência, exclusão individual preservando outra foto e incidente, cadastro/edição com sobreposição informativa e consulta de auditoria | `scripts.testar_persistencia` |
| Migrações e auditoria | Aplicação sobre registro legado, preservação de frequência/observações, recuperação da autoria, reaplicação com histórico e nulos equivalentes sem falsa alteração | `scripts.testar_persistencia` |
| UTE, estações e escalas | Ordenação e isolamento de UTE; edição/desativação/reativação preservando vínculo; coordenadas/perfil; filtros de escalas e turno noturno | `scripts.testar_persistencia` |
| Navegador | Seleção de evento/usuário por API real, cliques e gravações, formulário mobile sem rolagem horizontal, imagens carregadas e cancelamento/confirmação de exclusão | `scripts.testar_navegador` |

A camada rápida combina testes de rotas, middleware e repositório com dados
simulados; parte dela simula renderização. A camada de persistência usa a aplicação,
sessão, templates e serviços reais com PostgreSQL isolado, inclusive auditoria.
Playwright usa um servidor real em porta livre, encerrado ao terminar a classe.
Service workers ficam bloqueados no navegador para excluir offline do escopo.

## Defeitos corrigidos

| Defeito | Evidência e caminho responsável |
| --- | --- |
| Devolução sem motivo quando o campo é omitido | O teste de persistência confirma a recusa e a preservação do estado anterior. |
| Confirmação duplicada para excluir foto | A lixeira usa a confirmação específica da imagem. O teste cancela e depois confirma uma única vez, preservando a outra foto e o incidente. |
| Feedback de sucesso perdido no cadastro | Os formulários enviados por `AppOffline.interceptarSubmit` usam `X-App-Redirect: json`. O middleware devolve o destino em JSON e o navegador realiza o único GET que consome o flash; os demais formulários mantêm os redirecionamentos HTTP. |
| Emissões de campo ausentes do contador e recusadas na edição | O menu conta os rascunhos sem restringir a origem, e a edição aceita `FISCAL` após validar autoria e permissão. As jornadas verificam persistência da edição e retirada da pendência após submissão. |

Capturas e traces são gerados em `.test-artifacts/`, ignorado pelo Git e publicado
como artefato no job de navegador. Para abrir um trace:

```powershell
uv run --locked playwright show-trace .test-artifacts/test_salvar_emissao_celular.zip
```

Novas reprovações não devem ser ignoradas para publicar uma versão como validada.

## Isolamento do banco

O executor de integração exige `TEST_DATABASE_URL`, recusando servidores remotos,
outros drivers e nomes que não sigam `appeventos_test_<8 hexadecimais>`. Nunca
usa o `DATABASE_URL` do banco de trabalho como fallback.

Cada execução cria um schema novo. O parser PostgreSQL seleciona apenas tabelas,
índices e adições de colunas da definição base, resolve a ordem das referências
e aplica os SQLs versionados de migração em transação. Não executa o schema
legado integral, seus `DROP`, blocos de migração legada ou atualizações em massa.
Os fixtures são sintéticos; não há restauração de dumps de trabalho.

Para usar um PostgreSQL de testes já criado, sem remoção automática:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://testes:testes@127.0.0.1:55432/appeventos_test_a1b2c3d4'
uv run --locked python -m scripts.testar_integracao --navegador
```

## Processo para cada correção

1. Executar a suíte antes da mudança para conhecer o estado inicial.
2. Reproduzir o problema com um teste específico que falhe antes da correção.
3. Corrigir somente o fluxo responsável, preservando os contratos dos demais.
4. Executar o teste específico, a camada rápida e o comando de todas as camadas.
5. Informar os resultados e os fluxos ainda não verificados antes de concluir.

Uma mudança intencional de regra exige confirmar o requisito e atualizar a
expectativa do teste. Não remover, pular ou enfraquecer testes para esconder
falhas. Nesta implantação, a expectativa antiga da consulta comum foi alinhada
ao commit `fe20732`: emissões submetidas deixam a lista de elaboração do fiscal;
o acesso pelo ticket continua protegido por testes próprios.

Para acrescentar cobertura, preferir as classes existentes. Se houver outra
responsabilidade, criar um módulo `scripts/testar_<fluxo>.py` com `TestCase` ou
`IsolatedAsyncioTestCase` e registrá-lo no executor apropriado. Apenas os testes
sem banco entram em `MODULOS_SEGUROS`; testes reais entram no executor de
integração. Não fazer descoberta indiscriminada dos scripts que acessam o banco.

## Automação no GitHub

O workflow `.github/workflows/regressao.yml` contém dois jobs: contratos sem
banco e integração/navegador com serviço PostgreSQL 16 exclusivo. Ambos usam
Python 3.13 e dependências do lockfile. Seu funcionamento remoto deve ser
confirmado após publicar os arquivos; a execução local já foi validada.

Na proteção da branch `main`, exigir a verificação
`Regressao funcional (Python 3.13)` e `Integracao e navegador (Python 3.13)` para
permitir merge. O workflow sozinho não configura essa proteção. As regras só
podem ser selecionadas após a primeira execução. A aprovação local não substitui
a verificação da execução do workflow remoto.

## Lacunas restantes

| Prioridade | Área | Cenários a acrescentar |
| --- | --- | --- |
| Alta | Novos defeitos | Preservar os testes dos defeitos corrigidos e cobrir novas ocorrências |
| Alta | Navegador | Jornada completa de ticket/etiquetagem, edição nos popups, aviso imediato de conflito e upload pela interface |
| Alta | Permissões e concorrência | Tentativas cruzadas entre eventos/usuários em todas as APIs, edição simultânea e repetição de envios |
| Alta | Auditoria | Inclusão/edição/exclusão de todos os tipos, autoria em todos os serviços e combinações de filtros |
| Alta | Migrações | Falha deliberada, rollback e validação do migrador de implantação completo com histórico legado variado |
| Média | Demais cadastros | Criação real de eventos/fiscais, todas as classificações de incidentes, numeração de etiquetas e colisões de identificação de estações |
| Média | Plataformas | Firefox/WebKit, outros tamanhos de tela e acessibilidade por teclado |

Os próximos testes devem descrever resultados observáveis, não apenas a presença
de texto no código. Testes de navegador precisam verificar ações e seus efeitos;
testes de banco devem usar uma instância descartável com dados de teste.
Não restaurar dumps de trabalho nem executar o schema legado destrutivo para testar.