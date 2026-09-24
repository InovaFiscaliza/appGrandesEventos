#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$BundleDirectory,
    [ValidateRange(1024, 65535)][int]$WebPort = 8501,
    [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$ServerAddress = '192.168.1.11'
)
if (-not $BundleDirectory) { $BundleDirectory = $PSScriptRoot }
. (Join-Path $PSScriptRoot 'comum.ps1')
Assert-PodmanReady
$bundle = (Resolve-Path -LiteralPath $BundleDirectory).Path
$manifest = Get-Content -LiteralPath (Join-Path $bundle 'manifest.json') -Raw | ConvertFrom-Json
if (-not ($manifest.PSObject.Properties.Name -contains 'database_update_mode') -or
    $manifest.database_update_mode -ne 'preserve_data_with_migrations') {
    throw 'Pacote antigo: gere um novo pacote com o envio atual, que preserva os dados do servidor.'
}
$dump = Join-Path $bundle 'database.dump'
if ($manifest.postgres_major -ne 16) { throw 'Versao de PostgreSQL incompativel.' }
if ($manifest.release -notmatch '^appeventos-[0-9]{8}-[0-9]{6}-[a-f0-9]{8}$') { throw 'Identificador de pacote invalido.' }
if ((Get-FileHash -LiteralPath $dump -Algorithm SHA256).Hash -ne $manifest.dump_sha256) {
    throw 'O backup nao confere com o SHA256 do pacote. Transfira o pacote novamente.'
}
# This Windows lock also covers the interval when the database container is
# stopped/renamed. A second installer must never start it on the same volume.
$lockDirectory = Join-Path $env:LOCALAPPDATA 'AppGrandesEventos'
New-Item -ItemType Directory -Path $lockDirectory -Force | Out-Null
try {
    $installationLock = [IO.File]::Open((Join-Path $lockDirectory 'deployment.lock'),
        [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
} catch { throw "Nao foi possivel obter a trava de instalacao. Confira se outra atualizacao esta em andamento: $($_.Exception.Message)" }
try {
    $label = 'io.appgrandeseventos.managed=true'
    $network = 'appeventos-network'
    $volume = 'appeventos-pgdata'
    $databaseContainer = 'appeventos-db'
    $webContainer = 'appeventos-web'
    $passwordSecret = 'appeventos-db-password'
    $urlSecret = 'appeventos-database-url'
    $image = "localhost/appeventos-web:$($manifest.release)"
    $postgresImage = 'docker.io/library/postgres:16-bookworm'

    # Refuse to modify resources from other installations.
    foreach ($resource in @(@('network', $network), @('volume', $volume),
        @('container', $databaseContainer), @('container', $webContainer))) {
        if (Test-PodmanResource $resource[0] $resource[1]) {
            Assert-ManagedResource $resource[0] $resource[1]
        }
    }
    $hasVolume = Test-PodmanResource 'volume' $volume
    $hasPassword = Test-PodmanResource 'secret' $passwordSecret
    $hasUrl = Test-PodmanResource 'secret' $urlSecret
    if ($hasPassword -ne $hasUrl -or ($hasVolume -and -not $hasPassword)) {
        throw 'Segredos ausentes ou incompletos. Recupere os segredos desta instalacao antes de continuar.'
    }
    & (Join-Path $PSScriptRoot 'configurar-rede.ps1') -WebPort $WebPort

    Write-Host 'Construindo a imagem da aplicacao com as dependencias do uv.lock...'
    Invoke-Podman -Arguments @('build', '--tag', $image, '--file', (Join-Path $bundle 'project/Containerfile'),
        (Join-Path $bundle 'project'))
    Write-Host 'Obtendo a imagem atual do PostgreSQL 16 antes de parar os containers...'
    Invoke-Podman -Arguments @('pull', $postgresImage)
    $postgresImageId = @(Invoke-Podman -Arguments @('image', 'inspect', '--format', '{{.Id}}', $postgresImage))[-1]
    if (-not $hasPassword) {
        $password = New-RandomHex
        New-PodmanSecret $passwordSecret $password
        New-PodmanSecret $urlSecret "postgresql+psycopg://appeventos:${password}@${databaseContainer}:5432/appeventos"
        $password = $null
    }
    if (-not (Test-PodmanResource 'network' $network)) {
        Invoke-Podman -Arguments @('network', 'create', '--label', $label, $network) | Out-Null
    }
    if (-not $hasVolume) {
        Invoke-Podman -Arguments @('volume', 'create', '--label', $label, $volume) | Out-Null
    }
    function Start-NewDatabaseContainer {
        Invoke-Podman -Arguments @('run', '-d', '--name', $databaseContainer, '--label', $label,
            '--network', $network, '--restart=unless-stopped',
            '--env', 'POSTGRES_USER=appeventos', '--env', 'POSTGRES_DB=appeventos',
            '--env', 'POSTGRES_PASSWORD_FILE=/run/secrets/db-password',
            '--secret', "${passwordSecret},target=db-password",
            '--volume', "${volume}:/var/lib/postgresql/data", $postgresImageId) | Out-Null
    }
    $hasDatabaseContainer = Test-PodmanResource 'container' $databaseContainer
    if (-not $hasDatabaseContainer) {
        Write-Host "Criando o container do banco: $databaseContainer"
        Start-NewDatabaseContainer
    } else {
        Invoke-Podman -Arguments @('start', $databaseContainer) | Out-Null
    }
    Wait-Database $databaseContainer
    $serverVersion = @(Invoke-Podman -Arguments @('exec', $databaseContainer, 'psql', '-X', '-At',
        '-U', 'appeventos', '-d', 'postgres', '-c', 'SHOW server_version_num'))[-1]
    if ([int]$serverVersion -lt 160000 -or [int]$serverVersion -ge 170000) {
        throw 'O banco remoto precisa ser PostgreSQL 16. A atualizacao de versao principal exige uma migracao propria.'
    }

    function Invoke-DatabaseSql {
        param([string]$Sql)
        Invoke-Podman -Arguments @('exec', $databaseContainer, 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
            '-U', 'appeventos', '-d', 'postgres', '-c', $Sql) | Out-Null
    }

    $deploymentId = (Get-Date -Format 'yyyyMMddHHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $stagingDatabase = "appeventos_stage_$deploymentId"
    $previousDatabase = "appeventos_previous_$deploymentId"
    $containerDump = "/tmp/$deploymentId.dump"
    $databaseSwapped = $false
    $connectionsBlocked = $false
    $oldWeb = $null
    $oldWebStopped = $false
    $oldDatabaseContainer = $null
    $oldDatabaseStopped = $false
    $newDatabaseAttempted = $false
    $newWebAttempted = $false
    $stagingCreated = $false
    # Any existing user table, sequence or view means this is an update, even
    # when every application table is empty. Never seed over an existing schema.
    $deploymentLock = '/var/lib/postgresql/data/.appeventos-deployment-lock'
    Invoke-Podman -Arguments @('exec', $databaseContainer, 'mkdir', $deploymentLock)
    try {
        $objectCount = Invoke-Podman -Arguments @('exec', $databaseContainer, 'psql', '-X', '-At',
            '-v', 'ON_ERROR_STOP=1', '-U', 'appeventos', '-d', 'appeventos', '-c',
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r', 'p', 'S', 'v', 'm', 'f') AND n.nspname <> 'information_schema' AND n.nspname !~ '^pg_'")
        $firstInstallation = [int]($objectCount | Select-Object -Last 1) -eq 0
        # Pause writers before cloning, so writes made on the server are retained.
        if (Test-PodmanResource 'container' $webContainer) {
            Write-Host "Parando o container web remoto: $webContainer"
            Invoke-Podman -Arguments @('stop', '--time', '30', $webContainer) | Out-Null
            $oldWebStopped = $true
            $previousWebName = "$webContainer-previous-$deploymentId"
            Invoke-Podman -Arguments @('rename', $webContainer, $previousWebName)
            $oldWeb = $previousWebName
        }
        if ($hasDatabaseContainer) {
            Write-Host "Parando o container do banco remoto: $databaseContainer"
            Invoke-Podman -Arguments @('stop', '--time', '60', $databaseContainer) | Out-Null
            $oldDatabaseStopped = $true
            $previousDatabaseContainerName = "$databaseContainer-previous-$deploymentId"
            Invoke-Podman -Arguments @('rename', $databaseContainer, $previousDatabaseContainerName)
            $oldDatabaseContainer = $previousDatabaseContainerName
            $newDatabaseAttempted = $true
            Write-Host "Recriando $databaseContainer com PostgreSQL 16 e o mesmo volume de dados..."
            Start-NewDatabaseContainer
            Wait-Database $databaseContainer
            Write-Host 'Container do banco atualizado e pronto para as migracoes.'
        }
        Invoke-DatabaseSql 'ALTER DATABASE appeventos ALLOW_CONNECTIONS false'
        $connectionsBlocked = $true
        Invoke-DatabaseSql "SELECT pg_terminate_backend(pid, 5000) FROM pg_stat_activity WHERE datname = 'appeventos'"

        if ($firstInstallation) {
            Write-Host 'Primeira instalacao: restaurando a copia local em um banco vazio...'
            Invoke-Podman -Arguments @('exec', $databaseContainer, 'createdb', '-U', 'appeventos',
                '--template=template0', $stagingDatabase)
        } else {
            Write-Host 'Atualizacao: copiando os dados do servidor e aplicando somente migracoes de estrutura...'
            Invoke-Podman -Arguments @('exec', $databaseContainer, 'createdb', '-U', 'appeventos',
                '--template=appeventos', $stagingDatabase)
        }
        $stagingCreated = $true
        if ($firstInstallation) {
            Invoke-Podman -Arguments @('cp', $dump, "${databaseContainer}:$containerDump")
            try {
                Invoke-Podman -Arguments @('exec', $databaseContainer, 'pg_restore', '--username=appeventos', "--dbname=$stagingDatabase",
                    '--no-owner', '--no-privileges', '--single-transaction', '--exit-on-error', $containerDump)
            } finally {
                Invoke-Podman -Arguments @('exec', $databaseContainer, 'rm', '-f', $containerDump)
            }
        }
        Invoke-Podman -Arguments @('run', '--rm', '--network', $network,
            '--secret', "${urlSecret},type=env,target=DATABASE_URL", '--env', "DEPLOY_CHECK_DATABASE=$stagingDatabase",
            $image, 'python', '/app/deployment/migrar.py')
        Invoke-Podman -Arguments @('exec', $databaseContainer, 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
            '-U', 'appeventos', '-d', $stagingDatabase, '-c',
            'SELECT count(*) AS eventos FROM eventos; SELECT count(*) AS faixas FROM faixas_numeracao_etiqueta;')

        # Test the new code against the migrated server data before promoting it.
        $probe = "import os; from sqlalchemy.engine import make_url; os.environ['DATABASE_URL'] = make_url(os.environ['DATABASE_URL']).set(database=os.environ['DEPLOY_CHECK_DATABASE']).render_as_string(hide_password=False); from sqlalchemy import text; from app.services.db import get_engine; c = get_engine().connect(); c.execute(text('SELECT 1 FROM eventos LIMIT 1')); c.close(); import main; print('Database and imports OK')"
        Invoke-Podman -Arguments @('run', '--rm', '--network', $network,
            '--secret', "${urlSecret},type=env,target=DATABASE_URL", '--env', "DEPLOY_CHECK_DATABASE=$stagingDatabase",
            $image, 'python', '-c', $probe)
        Invoke-DatabaseSql "BEGIN; ALTER DATABASE appeventos RENAME TO $previousDatabase; ALTER DATABASE $stagingDatabase RENAME TO appeventos; ALTER DATABASE appeventos ALLOW_CONNECTIONS true; COMMIT;"
        $databaseSwapped = $true
        $connectionsBlocked = $false
        $newWebAttempted = $true
        Write-Host "Iniciando o novo container web remoto: $webContainer"
        Invoke-Podman -Arguments @('run', '-d', '--name', $webContainer, '--label', $label,
            '--network', $network, '--restart=unless-stopped',
            '--secret', "${urlSecret},type=env,target=DATABASE_URL",
            '--publish', "0.0.0.0:${WebPort}:8501", $image) | Out-Null
        Wait-WebApplication $WebPort
    } catch {
        $failure = $_
        Write-Warning "Atualizacao interrompida: $($failure.Exception.Message)"
        if ($newWebAttempted -and (Test-PodmanResource 'container' $webContainer)) {
            # Capture the startup error before removing the failed container.
            # Diagnostic failures must not prevent restoring the previous version.
            Show-DeploymentContainerLog $webContainer
            Invoke-Podman -Arguments @('rm', '-f', $webContainer) | Out-Null
        }
        # Recover the previous PostgreSQL executable before reverting schema names.
        # Both containers use the same persistent volume, one at a time, on PG 16.
        if ($newDatabaseAttempted -and (Test-PodmanResource 'container' $databaseContainer)) {
            Show-DeploymentContainerLog $databaseContainer
            Invoke-Podman -Arguments @('stop', '--time', '60', $databaseContainer) | Out-Null
            Invoke-Podman -Arguments @('rm', $databaseContainer) | Out-Null
        }
        if ($oldDatabaseContainer) { Invoke-Podman -Arguments @('rename', $oldDatabaseContainer, $databaseContainer) }
        if ($oldDatabaseStopped) {
            Invoke-Podman -Arguments @('start', $databaseContainer) | Out-Null
            Wait-Database $databaseContainer
            Write-Warning 'O container anterior do banco foi reiniciado com o volume preservado.'
        }
        if ($databaseSwapped) {
            Invoke-DatabaseSql 'ALTER DATABASE appeventos ALLOW_CONNECTIONS false'
            Invoke-DatabaseSql "SELECT pg_terminate_backend(pid, 5000) FROM pg_stat_activity WHERE datname = 'appeventos'"
            Invoke-DatabaseSql "BEGIN; ALTER DATABASE appeventos RENAME TO $stagingDatabase; ALTER DATABASE $previousDatabase RENAME TO appeventos; ALTER DATABASE appeventos ALLOW_CONNECTIONS true; COMMIT;"
            $databaseSwapped = $false
            Write-Warning 'O banco anterior foi recolocado em uso.'
        } elseif ($connectionsBlocked) {
            Invoke-DatabaseSql 'ALTER DATABASE appeventos ALLOW_CONNECTIONS true'
        }
        if ($oldWeb) { Invoke-Podman -Arguments @('rename', $oldWeb, $webContainer) }
        if ($oldWebStopped) {
            Invoke-Podman -Arguments @('start', $webContainer) | Out-Null
            $previousPort = @(Invoke-Podman -Arguments @('port', $webContainer, '8501/tcp'))[0]
            Wait-WebApplication ([int]($previousPort.Split(':')[-1]))
            Write-Warning 'A versao web anterior foi reiniciada.'
        }
        throw $failure
    } finally {
        try {
            if ($stagingCreated -and -not $databaseSwapped) {
                Invoke-Podman -Arguments @('exec', $databaseContainer, 'dropdb', '-U', 'appeventos', '--if-exists', $stagingDatabase)
            }
        } finally {
            Invoke-Podman -Arguments @('exec', $databaseContainer, 'rmdir', $deploymentLock)
        }
    }
    if ($oldWeb) { Invoke-Podman -Arguments @('rm', $oldWeb) | Out-Null }
    if ($oldDatabaseContainer) { Invoke-Podman -Arguments @('rm', $oldDatabaseContainer) | Out-Null }
    Write-Host 'Containers remotos atualizados: appeventos-db e appeventos-web.'
    Write-Host "Estrutura atualizada com dados preservados. Banco anterior: $previousDatabase"
    Write-Host "Aplicacao pronta no servidor. Endereco na rede: http://${ServerAddress}:$WebPort"
    Write-Host 'Se o acesso pela rede falhar, execute liberar-porta.ps1 no servidor como Administrador.'
    Write-Host 'O banco usa o volume appeventos-pgdata e nao publica a porta 5432.'
} finally { $installationLock.Dispose() }
