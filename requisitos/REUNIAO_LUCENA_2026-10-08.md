---------------------------------------------------------------
REUNIÃO LUCENA

Modificações solicitadas — Sistema de Grandes Eventos

**Reunião:** 08/10/2026.  
**Fonte:** `L! Grandes Eventos-20261008_090233-Meeting Recording.mp4`.  
**Duração da gravação:** aproximadamente 1h32min04s.

Relatório organizado por assunto a partir da transcrição automática local da gravação, com revisão dos pedidos e do contexto e conferência de trechos e telas quando necessário. As referências são intervalos aproximados contados desde o início do vídeo; indicam os trechos de discussão, não necessariamente apenas a frase do pedido.

**Legenda:** todos os itens estão desmarcados (`[ ]`) para acompanhamento; a implementação e os testes ainda precisam ser verificados. Sugestões, pontos adiados e decisões pendentes estão identificados como tais. O conteúdo da reunião foi tratado como fonte para este relatório, sem executar as ações nele mencionadas. Os dados fictícios usados na demonstração não constituem requisitos de cadastro. Comportamentos demonstrados no vídeo não comprovam o funcionamento da versão atual do sistema.

## 1. Acesso, usuários e criação de eventos

- [ ] Disponibilizar a criação de um evento sem exigir que o coordenador entre previamente em outro evento. O problema foi retomado no início do teste e na proposta de organização das telas ao final. A discussão trata da independência em relação ao evento selecionado; não estabelece cadastro público sem autenticação. **Referência: 00:01:09–00:02:18; 01:20:05–01:20:34.**
- [ ] **Evolução futura mencionada:** avaliar a integração do acesso com a autenticação institucional, substituindo o acesso provisório usado na demonstração. Foi citada uma integração já utilizada em outro sistema, sem detalhamento suficiente para fixar o mecanismo ou a implementação. **Referência: 00:05:24–00:06:06.**

## 2. Cadastro de eventos e validação dos formulários

- [ ] Corrigir o tratamento de período inválido no cadastro do evento. No teste, a data final foi preenchida com um ano anterior à data inicial e o fluxo entrou em erro. Exibir um aviso claro para correção, mantendo o usuário no formulário. **Referência: 00:07:19–00:10:07.**
- [ ] Preservar os campos já preenchidos quando a validação falhar e apresentar a mensagem em uma janela de aviso. Na repetição do cadastro, o erro apagou os dados; o mesmo padrão foi solicitado para o cadastro de estações. O teste de etiquetagem foi citado como exemplo em que o formulário já era preservado. **Referência: 00:14:14–00:15:32; 00:21:45–00:22:15; 01:02:01–01:02:25.**
- [ ] **Investigação pendente:** verificar a interrupção e a aparente repetição do erro durante o primeiro cadastro. Foram levantadas hipóteses envolvendo o formulário, a conexão e a configuração do nome de acesso ao servidor. A gravação não confirma uma causa única. **Referência: 00:07:19–00:13:37.**

## 3. Cadastro, desativação e localização das estações

- [ ] Permitir recuperar uma estação desativada. Ao tentar cadastrar novamente a identificação, o sistema informou que ela já existia, sem oferecer uma forma clara de reativação. Foi proposta a exibição do estado ativa/inativa e uma confirmação de reativação ao reutilizar a identificação. Preservar as referências aos registros anteriores. **Referência: 00:20:46–00:22:45; 00:25:40–00:26:22.**
- [ ] **Decisão pendente:** esclarecer a dinâmica das estações móveis e o uso das coordenadas no registro das emissões. A mesma estação pode mudar de local; discutiu-se se o cadastro da estação fornece a localização da captura e como ficam os equipamentos de campo. A equipe decidiu observar o uso no lançamento antes de fechar essa regra. **Referência: 00:22:15–00:25:40; 00:34:39–00:35:18.**

## 4. Escalas e jornadas dos fiscais

- [ ] **Verificação pendente:** revisar o cadastro de jornadas sobrepostas para o mesmo fiscal no mesmo dia. Foram usados os intervalos de 08h às 12h e de 10h às 14h, e o comportamento foi questionado durante o teste. Não ficou definida uma regra final de bloqueio, aviso ou confirmação para essa situação. **Referência: 00:29:24–00:30:28.**
- [ ] **Sugestão:** avaliar um gerador automático de escala diária, especialmente para incluir fiscais que trabalharão em vários dias do evento. A ideia foi mencionada durante o preenchimento da escala, sem especificação de distribuição, rodízio ou restrições. **Referência: 00:28:14–00:29:15.**

## 5. Emissões pendentes, consulta e permissões

- [ ] Corrigir o fluxo de salvar uma emissão sem enviá-la à coordenação. O registro deve continuar disponível para o fiscal que o cadastrou, permitindo complementar os dados e decidir quando submetê-lo. Durante o teste, as emissões apareciam na pesquisa e na coordenação, mas não na área de pendências do cadastrador. O problema foi reproduzido também com o perfil de coordenador. **Referência: 00:32:26–00:38:25; 01:13:25–01:15:40.**
- [ ] Fazer a opção de tratar emissões pendentes e a indicação de pendências refletirem os registros efetivamente em elaboração. O fiscal precisa localizar, abrir, editar e enviar seus registros; a exibição do botão ou do contador não deve dar a impressão de que não existem pendências quando elas foram salvas. **Referência: 00:33:53–00:38:25; 01:13:25–01:15:40.**
- [ ] Rever as ações permitidas antes da submissão à coordenação. Após uma discussão inicial sobre onde o registro deveria aparecer, foi admitido que o coordenador possa consultar registros ainda em elaboração; as ações de movimentação devem respeitar a etapa do fluxo. No teste, foi possível criar um tíquete a partir de uma emissão que o fiscal ainda não havia enviado. **Referência: 00:39:47–00:42:50.**
- [ ] Corrigir a apresentação inconsistente da ação de editar na coordenação. A edição precisa estar vinculada ao responsável e ao estado do registro, em um ponto coerente do fluxo; durante a demonstração, apenas uma das emissões apresentava a ação, sem uma organização clara para o usuário. **Referência: 00:42:50–00:44:28.**
- [ ] Manter a consulta aos registros depois que deixam a área de trabalho do fiscal. Tanto quem cadastrou a ocorrência quanto quem recebeu o tíquete deve conseguir consultar o que passou por sua atuação. **Decisão pendente:** foi levantada a possibilidade de editar depois da conclusão pelo fiscal e antes da aceitação pelo coordenador; o pedido mínimo confirmado foi manter a visualização. **Referência: 00:49:39–00:50:07.**
- [ ] **Proposta de consulta comum:** permitir consultar o conjunto dos registros, com filtros como período, registros próprios e registros destinados ao usuário. Diferenciar a possibilidade de consultar da permissão para editar, que depende do responsável e da etapa do fluxo. A pesquisa existente foi usada como referência para acesso aos registros anteriores. **Referência: 00:50:07–00:51:55; 01:18:39–01:19:41.**
- [ ] **Sugestão; nomenclatura pendente:** tornar clara a diferença entre conclusão pelo fiscal e aprovação ou conclusão pelo coordenador. Foi sugerida uma aproximação com os estados usados no Fiscaliza, mas não foi definida uma nova lista de estados nem um mapeamento obrigatório. **Referência: 00:51:13–00:52:35.**

## 6. Tíquetes, providências e histórico

- [ ] Permitir abrir o tíquete pelo seu identificador, exibindo um formulário ou janela com os dados completos das ocorrências vinculadas, as observações do cadastrador e as informações acrescentadas pelo coordenador. Durante o teste, a tabela mostrava dados incompletos e o clique não abriu a edição esperada. Apresentar ali as ações disponíveis ao fiscal. **Referência: 00:46:25–00:48:40.**
- [ ] Validar o conteúdo das providências antes de concluir o tíquete. O teste mostrou que apenas um espaço permitia finalizar; depois da devolução pelo coordenador, foi possível concluir novamente sem registrar uma nova providência. Exigir informação efetiva a cada nova conclusão e revisar o reaproveitamento automático do texto anterior. **Referência: 00:48:06–00:49:37; 00:56:47–00:58:15.**
- [ ] Disponibilizar, nos detalhes do tíquete, um histórico legível das movimentações: informações do cadastrador, providências do fiscal, conclusão, devolução pelo coordenador, motivo da devolução e movimentações seguintes, com suas datas e responsáveis. O motivo da devolução deve ficar acessível ao fiscal quando o tíquete retornar. **Referência: 00:53:09–00:55:49.**
- [ ] Corrigir o cancelamento de tíquete para liberar tanto as emissões quanto os incidentes vinculados para o fluxo de edição correspondente. No teste de um tíquete misto, apenas a emissão foi liberada; o incidente permaneceu indisponível. **Referência: 01:07:50–01:09:24.**

## 7. Incidentes e submissão à coordenação

- [ ] **Fluxo a consolidar:** definir explicitamente o tratamento de incidentes, considerando a elaboração pelo fiscal, a edição e a submissão à coordenação. Foi explicado que a versão demonstrada seguia provisoriamente a lógica das emissões. Discutiu-se também o caso de uma medida já adotada em campo, que permitiria cadastrar o incidente como concluído pelo fiscal; não ficou fechada uma especificação completa desse caminho. **Referência: 01:04:28–01:07:11.**
- [ ] Disponibilizar na consulta ou no detalhamento do incidente os dados e anexos inseridos, incluindo a fotografia. Durante a revisão do incidente submetido, foi observado que a foto não estava visível na apresentação usada. **Referência: 01:06:21–01:07:11.**

## 8. Teste de etiquetagem e faixas de numeração

- [ ] Corrigir a validação de numeração para considerar também o tipo ou a categoria de liberação da etiqueta. As faixas foram tratadas como independentes para etiquetas permitidas no local e permitidas em todos os locais. Na troca da categoria, o sistema continuou acusando uso da faixa pelo número, embora a categoria selecionada tivesse faixa própria. Manter o impedimento de reutilização dentro da mesma categoria. **Referência: 00:17:00–00:17:46; 01:01:43–01:03:50.**
- [ ] **Ponto a esclarecer:** revisar o campo ainda sem definição na área de dados da etiqueta. Foi sugerida sua retirada por estar sem finalidade clara. A tela mostra um campo denominado “Tipo de etiqueta” nessa região, mas a fala não identifica o campo de maneira inequívoca; confirmar a identificação e a regra antes de decidir sua remoção. **Referência: 01:00:14–01:00:30.**

## 9. Navegação e organização das telas

- [ ] Padronizar o caminho de navegação exibido no alto das telas. “Gerenciar evento” aparecia no caminho a partir do início, enquanto a entrada em “Coordenação do evento” não apresentava a mesma indicação. **Referência: 00:38:29–00:39:47.**
- [ ] Simplificar as tabelas de tíquetes para melhorar a leitura em computador, celular e tablet. Foram sugeridas poucas colunas: identificador com link, prioridade, data e, eventualmente, a última pessoa que movimentou o registro. Exibir informações extensas, observações e histórico ao abrir os detalhes. Rever o tamanho reduzido da fonte e a necessidade de rolagem horizontal. **Referência: 00:54:00–00:56:47.**
- [ ] **Ponto adiado:** padronizar a posição do formulário e da tabela com os registros, bem como a apresentação geral dos cadastros. Foi apontado que algumas telas mostravam a tabela acima do formulário e outras abaixo. A equipe classificou essa inconsistência como ajuste visual que não precisava ser tratado naquele momento. **Referência: 00:20:15–00:21:45; 01:19:41–01:20:34.**
- [ ] **Proposta de simplificação:** reunir os lançamentos em um módulo de cadastro, com escolha do tipo de registro e exibição do formulário correspondente, e as pesquisas em um módulo de consulta. Foram citados teste de etiquetagem, emissão e incidente como cadastros hoje dispersos. Preservar os fluxos próprios da criação de eventos e da coordenação. A proposta não determina uma mudança imediata de toda a aplicação. **Referência: 01:17:38–01:22:10.**
- [ ] **Parte da proposta de simplificação:** manter a indicação de pendências como atalho para a consulta filtrada. Ao clicar no contador, abrir os registros pendentes ou destinados ao usuário, aproveitando o módulo comum de consulta. **Referência: 01:18:39–01:19:41.**

## 10. Prioridade das correções e testes de regressão

- [ ] Priorizar a correção dos erros funcionais identificados antes da reorganização dos módulos e dos ajustes visuais. A equipe concordou que a simplificação das telas pode vir depois da estabilização dos fluxos. **Referência: 01:21:07–01:22:10.**
- [ ] Criar e manter testes reproduzíveis de navegador para as funcionalidades corrigidas, com passos explícitos de navegação, preenchimento, submissão e conferência do resultado. Playwright foi citado como ferramenta; distinguir a execução pontual para investigar um erro da manutenção de testes que possam ser repetidos após outras alterações. **Referência: 01:24:54–01:28:46.**
- [ ] Executar os testes existentes depois de novas alterações para detectar regressões em outras telas. Construir a cobertura por funcionalidade, começando por um item específico e ampliando gradualmente; foram usados como exemplos abrir o cadastro de eventos, preencher coordenadas e enviar um valor inválido. Capturas de tela foram sugeridas para conferir os passos executados. **Referência: 01:28:16–01:31:57.**

## 11. Operação e continuidade

- [ ] **Intenção mencionada; especificação pendente:** avaliar uma rotina diária de backup com envio de uma cópia ao responsável pela manutenção, à medida que o uso se torne contínuo. O assunto apareceu brevemente no início, sem definição de armazenamento, retenção, destinatário definitivo ou teste de restauração. **Referência: 00:00:08–00:00:22.**

**Observação de escopo:** a auditoria, a devolução e aceitação de tíquetes, o agrupamento de ocorrências e outros recursos foram demonstrados durante a reunião. Este relatório registra os ajustes, verificações e propostas identificados, sem atribuir automaticamente novos requisitos a cada funcionalidade apresentada. Os trechos com definição incompleta permanecem assinalados para confirmação.
