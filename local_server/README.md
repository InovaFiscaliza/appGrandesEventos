# Instalação no Windows com Podman Desktop

Todos os arquivos da automação ficam em `local_server/`, na raiz do projeto, incluindo
os scripts PowerShell, o `Containerfile` e o `.containerignore`. Os pacotes
gerados ficam em `.deploy/`, separados dos arquivos versionados.

**Regra de atualização:** preservar os dados do servidor e aplicar migrações
de estrutura. O backup local só é restaurado na primeira instalação, quando
o banco de destino ainda não contém tabelas. Gere novos pacotes com estes
scripts; pacotes antigos podem conter o instalador que substituía os dados.

**Contêineres remotos:** o `atualiza_serv.bat` atualiza tanto `appeventos-web`
quanto `appeventos-db`. Primeiro constrói a imagem web e baixa a imagem atual
`postgres:16-bookworm`, com os serviços ainda disponíveis. Depois para a web,
para o banco, recria o banco usando o mesmo volume `appeventos-pgdata`, aplica
as migrações e inicia a nova web. O PostgreSQL permanece na versão principal
16; este fluxo não faz atualização automática para PostgreSQL 17 ou superior.

As versões anteriores dos dois contêineres permanecem paradas até a validação
HTTP da nova aplicação. Se a troca ou a migração falhar, o instalador tenta
recuperar o banco e os contêineres anteriores. Na conclusão bem-sucedida,
remove somente os contêineres antigos, preservando o volume e os segredos.
Todas essas etapas aparecem no log. Uma trava no Windows impede atualizações
simultâneas durante a parada e a recriação do contêiner do banco.

**Rede WSL:** o instalador identifica a máquina da conexão ativa do Podman e
configura o encaminhamento TCP da porta web no Windows para o IPv4 atual do
WSL. A regra de firewall permite essa porta apenas para a sub-rede local,
inclusive quando o Windows classifica o Wi-Fi como Público. Essa etapa exige
uma sessão administrativa no servidor e ocorre antes de alterar o banco.
Encaminhamentos existentes que não pertencem a estes scripts são preservados:
nesse caso, a instalação para e informa o conflito.

O endereço interno do WSL pode mudar ao reiniciar. Cada novo envio atualiza
o encaminhamento. Para atualizá-lo sem reinstalar, execute como administrador
`powershell -NoProfile -ExecutionPolicy Bypass -File .\configurar-rede.ps1`
na pasta do pacote instalado (informe `-WebPort` se usar outra porta).

O envio apresenta a saída remota em texto e, quando a aplicação falha,
mostra suas últimas mensagens antes de restaurar a versão anterior.

Destino padrão: **192.168.1.11**, com dois contêineres Linux:

| Recurso | Nome | Finalidade |
| --- | --- | --- |
| Aplicação | `appeventos-web` | FastAPI em `http://192.168.1.11:8501` |
| Banco | `appeventos-db` | PostgreSQL 16, acessível pela rede dos contêineres |
| Volume | `appeventos-pgdata` | Dados persistentes do banco |
| Rede | `appeventos-network` | Comunicação da aplicação com o banco |

Os scripts são compatíveis com Windows PowerShell 5.1. Não exigem Compose,
Python ou Git instalados no destino. O Podman constrói a imagem com Python
3.13 e instala as dependências do `uv.lock` usando `uv sync --locked`.

## 1. Preparar os computadores

- Origem: Podman funcionando, com o banco atual no contêiner
  `postgres-appeventos` ou `postgres_appeventos`, banco/usuário `appeventos`.
  O script detecta o nome quando encontra apenas um desses contêineres.
- Fontes: os arquivos atuais desta pasta do projeto, usada pelo VS Code,
  incluindo alterações ainda sem commit. Salve suas alterações antes do envio.
- Destino: Podman Desktop instalado, máquina Linux inicializada e em
  execução. Abra o Podman Desktop com o mesmo usuário Windows que executará
  a instalação. Confirme `podman ps` nesse usuário.
- Destino: acesso à internet para baixar as imagens e dependências Python.
- Confirme que a porta 8501 está livre e que o IP do destino é 192.168.1.11.

## 2. Gerar o pacote para transferência manual

Execute na raiz do projeto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local_server\preparar.ps1
```

O resultado fica em `.deploy\appeventos-DATA-HORA-ID.tar.gz`. O script mostra
o caminho exato. O pacote inclui os arquivos atuais da aplicação, inclusive
alterações ainda sem commit, o instalador e um backup consistente feito com
`pg_dump --format=custom`. A estrutura, os dados, as sequências e as imagens
armazenadas no PostgreSQL são copiados. A origem não é alterada.
O banco de origem precisa estar em execução. O manifesto registra a pasta dos
fontes, os hashes dos arquivos, o ID do contêiner e a data da cópia. Se um
fonte mudar durante a cópia, o script para e solicita uma nova execução.
O pacote leva os arquivos salvos no disco; ele não extrai módulos antigos
que possam continuar carregados na memória de um processo Python sem reload.

Se os nomes locais forem diferentes:

```powershell
.\local_server\preparar.ps1 -SourceContainer meu_postgres -Database meu_banco -DatabaseUser meu_usuario
```

O script usa a conexão local por socket dentro desse contêiner. Ele interrompe
a execução se não conseguir autenticar ou se o PostgreSQL não for versão 16.
Não utilize um contêiner que aponte para outro banco por configuração própria.

O pacote contém os dados completos da aplicação. `.deploy/` está no
`.gitignore`; guarde e transfira os arquivos apenas para locais autorizados.
O backup fica fora do contexto usado para construir a imagem web.

## 3. Transferir e instalar

### Automático, com OpenSSH Server já habilitado no destino

Use a conta Windows que possui a máquina do Podman no servidor. A autenticação
é feita pelo SSH, com chave ou senha; os scripts não guardam sua senha.
Na primeira conexão, confira a impressão digital da chave do servidor.

Para executar com dois cliques, clique com o botão direito em
[`atualiza_serv.bat`](atualiza_serv.bat), escolha **Editar** e ajuste as linhas
no início do arquivo:

```bat
set "SERVIDOR_IP=192.168.1.11"
set "USUARIO_SERVIDOR=SEU_USUARIO"
set "PORTA_WEB=8501"
set "CHAVE_SSH=%USERPROFILE%\.ssh\id_ed25519_appgrandeseventos"
```

Substitua `SEU_USUARIO` pelo usuário Windows do servidor, salve e dê dois
cliques no arquivo. A janela permanece aberta ao concluir ou apresentar erro.
O `.bat` usa a chave privada indicada em `CHAVE_SSH`, sem pedir a senha da
conta Microsoft. Cadastre a chave pública no servidor conforme a seção abaixo.
Mantenha o arquivo nesta pasta, junto de `enviar.ps1`; se preferir executá-lo
pela área de trabalho, crie um atalho para ele.

Cada execução do `.bat` cria um arquivo UTF-8 em `local_server/logs/`, com nome
`atualiza_serv-DATA-HORA-ID.log`. O log registra os horários, destino, saída
da atualização, erros, duração e código de saída. As mensagens continuam
visíveis na janela, e o caminho do arquivo aparece no início e no fim.
Os logs anteriores são mantidos e a pasta não entra no Git nem nos pacotes.
Para investigar uma falha, consulte ou envie o arquivo daquela execução.
É possível mudar a pasta editando `PASTA_LOG` no `.bat`; caminhos relativos
são resolvidos a partir de `local_server/`.
O auxiliar `atualizar-com-log.ps1` precisa permanecer junto do `.bat`.

Para executar pelo terminal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local_server\enviar.ps1 -WindowsUser SEU_USUARIO
```

Antes de gerar o pacote, o envio verifica o acesso TCP à porta 22 do destino.
Se a conexão falhar, mostra os comandos de diagnóstico e para sem gerar
outro backup. Quando recebe `-SshKeyPath`, também testa o login por chave e
confirma o usuário remoto com `whoami` antes de acessar o banco local.
Chaves rejeitadas interrompem o envio, sem tentar a senha da conta Microsoft.
Sem `-SshKeyPath`, o terminal mantém a autenticação SSH já configurada.

**Cada envio gera um novo backup do banco ativo e uma nova cópia dos
fontes.** O envio não aceita `-Package` e não reutiliza
arquivos antigos. Se a captura falhar, nenhuma transferência é realizada.
Não é necessário executar `preparar.ps1` antes do envio automático.

O script envia a cópia nova para 192.168.1.11, verifica o SHA256, extrai em
`%LOCALAPPDATA%\AppGrandesEventos\releases\` e executa o instalador.
Para outro IP/porta, use `-ServerAddress` e `-WebPort`.
Para outra origem do banco, use `-SourceContainer`, `-Database` e
`-DatabaseUser`, como em `preparar.ps1`.
O OpenSSH Server deve estar instalado e com acesso pela porta 22. Este script
não instala serviços remotos nem altera a configuração SSH do Windows.

### Autenticação por chave SSH

A chave dedicada deste computador fica em
`%USERPROFILE%\.ssh\id_ed25519_appgrandeseventos`; o arquivo de mesmo nome
com extensão `.pub` contém a parte pública. A chave privada fica fora do
projeto e não faz parte dos pacotes de implantação. Ela foi criada sem senha
de proteção para permitir a atualização pelo `.bat`, com permissões de arquivo
restritas ao proprietário, Administradores e SYSTEM.

Para cadastrar a parte pública, copie somente o arquivo `.pub` e
`autorizar-chave.ps1` para o servidor. No servidor, na pasta desses arquivos,
abra o PowerShell **como administrador**, usando a conta que abre o Podman:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\autorizar-chave.ps1 -PublicKeyFile .\id_ed25519_appgrandeseventos.pub -WindowsUser andre
```

O cadastro verifica a configuração efetiva do OpenSSH e usa o arquivo padrão
`%ProgramData%\ssh\administrators_authorized_keys`, com permissões para
Administradores e SYSTEM. Esse arquivo é compartilhado pelas contas
administradoras. O script mantém as chaves existentes, guarda uma cópia do
arquivo anterior e não duplica a chave cadastrada. Ele não modifica a senha
Microsoft, o PIN, os contêineres nem a configuração `sshd_config`.
Se o servidor usa outro caminho de chaves ou outra configuração de autenticação,
o cadastro para e mostra o motivo antes de alterar o arquivo.

De volta ao computador do projeto, teste em PowerShell:

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_appgrandeseventos" -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no andre@192.168.1.11 whoami
```

O resultado esperado neste servidor é `pcmanu\andre`. Depois, execute o `.bat`.
Para enviar pelo terminal com essa chave:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local_server\enviar.ps1 -WindowsUser andre -SshKeyPath "$env:USERPROFILE\.ssh\id_ed25519_appgrandeseventos"
```

A verificação da identidade do servidor permanece habilitada. No primeiro
acesso de um computador novo, compare a impressão digital apresentada com a
chave do servidor antes de aceitar. Se optar por uma chave privada protegida
por senha, carregue-a previamente no `ssh-agent`: o envio por chave opera sem
prompts de autenticação.

### Se aparecer `Connection timed out` na porta 22

A conexão falhou antes da autenticação e da transferência. No **computador
de destino**, abra o PowerShell como administrador e execute:

```powershell
ipconfig
Get-Service sshd
Get-NetTCPConnection -State Listen -LocalPort 22
Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue |
    Format-List Enabled,Direction,Action,Profile
```

Confira se o endereço IPv4 é o IP configurado no `.bat`. O serviço `sshd`
deve estar `Running` e a porta 22 deve escutar no IP da rede ou em
`0.0.0.0`/`::`, não apenas em `127.0.0.1`/`::1`. Se o serviço existir mas
estiver parado, execute `Start-Service sshd`; se não existir, instale o
OpenSSH Server conforme a documentação da Microsoft.

Com serviço e escuta corretos, verifique se a regra de entrada TCP 22 está
habilitada para o perfil ativo da rede e se o endereço do computador de
origem está permitido. VPN, isolamento de clientes no Wi-Fi e regras de
bloqueio também podem impedir a conexão. No computador do projeto, teste:

```powershell
Test-NetConnection 192.168.1.11 -Port 22
```

Só execute o envio novamente quando `TcpTestSucceeded` for `True`.

### Sem SSH, copiando o pacote

Execute `preparar.ps1` novamente antes de cada cópia manual. Copie o `.tar.gz`
recém-gerado por compartilhamento de rede ou pendrive. No servidor,
extraia-o em uma pasta nova e execute:

```powershell
New-Item -ItemType Directory -Path C:\AppGrandesEventos\primeira-instalacao
tar -xzf C:\caminho\appeventos-DATA-HORA-ID.tar.gz -C C:\AppGrandesEventos\primeira-instalacao
powershell -NoProfile -ExecutionPolicy Bypass -File C:\AppGrandesEventos\primeira-instalacao\instalar.ps1
```

O instalador gera uma senha aleatória armazenada como segredo do Podman e
configura `DATABASE_URL` para a aplicação. Na primeira instalação em banco
vazio, restaura o backup local. Nas atualizações, pausa a aplicação e cria
uma cópia do **banco do servidor**, mantendo seus registros, imagens e
sequências. Aplica as migrações nessa cópia, verifica o novo código e a
coloca em uso. O banco anterior permanece guardado para recuperação.
Somente a porta web é publicada; o PostgreSQL não ocupa a porta 5432 do Windows.

## 4. Permitir acesso pela rede local

Se necessário, em PowerShell **como Administrador no servidor**, execute o
script incluído no pacote:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\liberar-porta.ps1
```

No WSL com NAT, ele atualiza o encaminhamento para o IP interno atual e
permite a porta 8501 para a sub-rede local em qualquer perfil do Windows.
Nos demais provedores, a regra de firewall usa os perfis Privado e Domínio.
Se usar outra porta, informe também `-WebPort` aqui. Teste a partir do
computador de desenvolvimento:

```powershell
Test-NetConnection 192.168.1.11 -Port 8501
```

Abra **http://192.168.1.11:8501**. Se localhost funcionar no servidor, mas o
IP continuar inacessível após a regra de firewall, verifique a publicação
de portas da máquina WSL/Hyper-V no Podman Desktop. O instalador verifica
localhost; isso não comprova conectividade de outro computador.

## Atualizações, reinício e recuperação

- Use `enviar.ps1 -WindowsUser SEU_USUARIO` para atualizar o código e aplicar
  as migrações pendentes. Os dados em uso no servidor são a referência:
  registros criados ou alterados nele permanecem após a atualização.
  O backup local acompanha cada envio, mas não substitui nem mescla esses dados.
- Mudanças de estrutura devem ser incluídas em novos arquivos SQL em
  [`migrations/`](migrations/README.md). O executável `migrar.py` aplica cada
  versão uma vez, em transação, e rejeita alterações em migrações já aplicadas.
  O instalador não compara automaticamente esquemas para remover objetos e
  não executa o `db/schema.sql` legado, que contém remoções de colunas.
- A aplicação fica temporariamente indisponível durante a cópia e a migração,
  para que gravações concorrentes não se percam. Uma trava no volume impede
  duas instalações simultâneas. Após uma interrupção abrupta, confirme que
  não há instalador em execução antes de investigar/remover a pasta de trava
  `/var/lib/postgresql/data/.appeventos-deployment-lock` no contêiner do banco.
- O banco anterior fica preservado no mesmo volume, com nome
  `appeventos_previous_DATA_ID` e conexões desabilitadas. O instalador mostra
  esse nome ao concluir. As cópias anteriores não são removidas automaticamente
  e ocupam espaço no volume. Elas permitem recuperação e não são mescladas
  com os dados novos. Para consultá-las, um administrador pode reabilitar
  conexões com `ALTER DATABASE NOME_DO_BANCO ALLOW_CONNECTIONS true`.
- Antes de trocar a aplicação, o instalador constrói a imagem e testa seus
  imports e sua conexão com o banco. Se o novo contêiner web não responder,
  ele recoloca o banco anterior em uso e reinicia os dois contêineres anteriores.
  A chave de sessão atual é gerada pelo aplicativo
  em cada início, portanto os usuários precisarão entrar novamente.
- Não há sincronização de registros entre os bancos. Depois da instalação
  inicial, cadastre os dados de operação no servidor; novos envios atualizam
  a aplicação e sua estrutura sem importar registros do desenvolvimento.
- A política `unless-stopped` atua enquanto a máquina do Podman está ligada.
  Estes scripts não configuram início automático do Windows/Podman. Após
  reiniciar o Windows, abra o Podman Desktop, inicie a máquina e execute:

```powershell
podman start appeventos-db
podman start appeventos-web
powershell -NoProfile -ExecutionPolicy Bypass -File .\configurar-rede.ps1
podman ps
podman logs --tail 100 appeventos-web
```

- Não remova `appeventos-pgdata` nem os segredos `appeventos-db-password` e
  `appeventos-database-url`: eles são necessários para reutilizar o banco.
- Se a restauração inicial, a migração ou a validação do banco temporário
  falhar, o banco anterior é reabilitado e a aplicação anterior é reiniciada.
  Execute um novo envio após corrigir a causa. A remoção automática atinge
  somente a cópia temporária que falhou, sem apagar o banco original.
- O backup original não substitui backups periódicos do banco no servidor.

## Testes dos scripts

Para validar os fluxos dos scripts sem criar contêineres nem acessar bancos:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\local_server\testar.ps1
```

O teste usa comandos simulados de Podman/SSH, gera artefatos em `.deploy/` e
verifica cópias novas a cada envio, restauração inicial, preservação de dados,
migração e recuperação,
proteção de recursos existentes e validação de integridade na transferência.

## Referências

- [Autenticação por chave no OpenSSH para Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- [Instalação do OpenSSH Server no Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [Diagnóstico do OpenSSH e firewall](https://learn.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/troubleshoot-openssh-windows-firewall-port22)
- [Podman no Windows](https://github.com/podman-container-tools/podman/blob/main/docs/tutorials/podman-for-windows.md)
- [Encaminhamento de portas do WSL para a rede local](https://learn.microsoft.com/en-us/windows/wsl/networking#accessing-a-wsl-2-distribution-from-your-local-area-network-lan)
- [Contêineres, volumes, portas e segredos](https://docs.podman.io/en/latest/markdown/podman-run.1.html)
- [uv em contêineres](https://docs.astral.sh/uv/guides/integration/docker/)
- [pg_restore e restauração transacional](https://www.postgresql.org/docs/16/app-pgrestore.html)
- [Troca de nomes e controle de conexões dos bancos](https://www.postgresql.org/docs/16/sql-alterdatabase.html)
- [Criação de uma cópia do banco PostgreSQL](https://www.postgresql.org/docs/16/sql-createdatabase.html)
- [Compatibilidade entre atualizações menores do PostgreSQL](https://www.postgresql.org/docs/16/upgrading.html)
