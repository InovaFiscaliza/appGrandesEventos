#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')]
    [string]$SourceContainer,
    [ValidatePattern('^[a-zA-Z_][a-zA-Z0-9_]*$')]
    [string]$Database = 'appeventos',
    [ValidatePattern('^[a-zA-Z_][a-zA-Z0-9_]*$')]
    [string]$DatabaseUser = 'appeventos',
    [string]$OutputDirectory
)
. (Join-Path $PSScriptRoot 'comum.ps1')
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $projectRoot '.deploy' }
Assert-PodmanReady
if (-not (Get-Command tar -ErrorAction SilentlyContinue)) { throw 'tar.exe nao encontrado.' }
if (-not $SourceContainer) {
    $candidates = @('postgres-appeventos', 'postgres_appeventos') | Where-Object {
        if (Test-PodmanResource 'container' $_) {
            $candidate = @(Invoke-Podman -Arguments @('container', 'inspect', $_) | ConvertFrom-Json)[0]
            $candidate.State.Running
        }
    }
    if (@($candidates).Count -ne 1) {
        throw 'Informe -SourceContainer com o nome do container do banco local.'
    }
    $SourceContainer = @($candidates)[0]
}
if (-not (Test-PodmanResource 'container' $SourceContainer)) {
    throw "Container de origem '$SourceContainer' nao encontrado. Use -SourceContainer."
}
$databaseContainer = @(Invoke-Podman -Arguments @('container', 'inspect', $SourceContainer) | ConvertFrom-Json)[0]
if (-not $databaseContainer.State.Running) {
    throw "O banco de origem '$SourceContainer' nao esta rodando. Nenhum pacote antigo sera enviado."
}
$snapshotStarted = [DateTime]::UtcNow.ToString('o')
$version = Invoke-Podman -Arguments @('exec', $SourceContainer, 'psql', '-X', '-A', '-t',
    '-U', $DatabaseUser, '-d', $Database, '-c', 'SHOW server_version_num')
if ([int]($version | Select-Object -Last 1) -lt 160000 -or
    [int]($version | Select-Object -Last 1) -ge 170000) {
    throw 'Este pacote espera PostgreSQL 16 na origem e no destino.'
}

$release = 'appeventos-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$bundle = Join-Path ([IO.Path]::GetFullPath($OutputDirectory)) $release
$source = Join-Path $bundle 'project'
New-Item -ItemType Directory -Path $source -Force | Out-Null
$dump = Join-Path $bundle 'database.dump'
$containerDump = "/tmp/$release.dump"
Write-Host 'Exportando uma copia consistente do banco local (sem alterar registros)...'
try {
    Invoke-Podman -Arguments @('exec', $SourceContainer, 'pg_dump', '--username', $DatabaseUser,
        '--dbname', $Database, '--no-password', '--format=custom', '--no-owner',
        '--no-privileges', '--file', $containerDump)
    Invoke-Podman -Arguments @('exec', $SourceContainer, 'pg_restore', '--list', $containerDump) | Out-Null
    Invoke-Podman -Arguments @('cp', "${SourceContainer}:$containerDump", $dump)
} finally {
    & podman exec $SourceContainer rm -f -- $containerDump
    if ($LASTEXITCODE -ne 0) { Write-Warning "Remova manualmente o temporario $containerDump na origem." }
}
if ((Get-Item -LiteralPath $dump).Length -eq 0) { throw 'O backup esta vazio.' }

# Explicitly include only runtime files; never copy .git, .venv or credentials.
$sourceHashes = [ordered]@{}
foreach ($name in @('main.py', 'anatel.png', 'pyproject.toml', 'uv.lock')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $name) -Destination $source
    $sourceHashes[$name] = (Get-FileHash -LiteralPath (Join-Path $source $name) -Algorithm SHA256).Hash
}
foreach ($name in @('Containerfile', '.containerignore')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $source
}
$deploymentSource = Join-Path $source 'deployment'
New-Item -ItemType Directory -Path $deploymentSource -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'migrar.py') -Destination $deploymentSource
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'migrations') -Destination $deploymentSource -Recurse
$appRoot = Join-Path $projectRoot 'app'
Get-ChildItem -LiteralPath $appRoot -Recurse -File -Force | Where-Object {
    $_.FullName -notmatch '[\\/]__pycache__[\\/]' -and
    $_.Extension -ne '.pyc' -and $_.Name -notlike '.env*' -and $_.Name -ne 'secrets.toml'
} | ForEach-Object {
    $relative = $_.FullName.Substring($projectRoot.Length + 1)
    $destination = Join-Path $source $relative
    New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $destination
    $sourceHashes[$relative.Replace('\', '/')] = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
}
foreach ($relative in $sourceHashes.Keys) {
    if ((Get-FileHash -LiteralPath (Join-Path $projectRoot $relative) -Algorithm SHA256).Hash -ne $sourceHashes[$relative]) {
        throw "O fonte '$relative' mudou durante a copia. Execute novamente para enviar um pacote consistente."
    }
}
foreach ($name in @('instalar.ps1', 'comum.ps1', 'configurar-rede.ps1', 'liberar-porta.ps1', 'README.md')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $bundle
}
$manifest = [ordered]@{
    release = $release
    created_utc = [DateTime]::UtcNow.ToString('o')
    snapshot_started_utc = $snapshotStarted
    postgres_major = 16
    database_update_mode = 'preserve_data_with_migrations'
    source_container = $SourceContainer
    source_container_id = $databaseContainer.Id
    source_database = $Database
    source_directory = $projectRoot
    source_files_sha256 = $sourceHashes
    dump_sha256 = (Get-FileHash -LiteralPath $dump -Algorithm SHA256).Hash
}
[IO.File]::WriteAllText((Join-Path $bundle 'manifest.json'),
    ($manifest | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
$archive = "$bundle.tar.gz"
& tar -czf $archive -C $bundle .
if ($LASTEXITCODE -ne 0) { throw 'Falha ao compactar o pacote.' }
Write-Host "Pacote pronto: $archive"
Write-Host 'O pacote contem uma copia completa dos dados; mantenha-o em local restrito.'
Write-Output $archive
