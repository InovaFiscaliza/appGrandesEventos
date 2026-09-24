#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9_.-]+$')][string]$WindowsUser,
    [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$ServerAddress = '192.168.1.11',
    [ValidateRange(1024, 65535)][int]$WebPort = 8501,
    [string]$SshKeyPath,
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_.-]*$')][string]$SourceContainer,
    [ValidatePattern('^[a-zA-Z_][a-zA-Z0-9_]*$')][string]$Database = 'appeventos',
    [ValidatePattern('^[a-zA-Z_][a-zA-Z0-9_]*$')][string]$DatabaseUser = 'appeventos',
    [string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
foreach ($command in @('ssh', 'scp')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Instale o cliente OpenSSH do Windows: comando $command nao encontrado."
    }
}
$sshOptions = @()
if ($SshKeyPath) {
    if (-not (Test-Path -LiteralPath $SshKeyPath -PathType Leaf) -or $SshKeyPath.EndsWith('.pub', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Informe -SshKeyPath com o arquivo da chave privada existente (sem a extensao .pub).'
    }
    $SshKeyPath = (Resolve-Path -LiteralPath $SshKeyPath).Path
    $sshOptions = @('-i', $SshKeyPath, '-o', 'IdentitiesOnly=yes',
        '-o', 'PreferredAuthentications=publickey', '-o', 'PasswordAuthentication=no',
        '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10')
}
$destination = "$WindowsUser@$ServerAddress"
Write-Host "Verificando acesso ao SSH em ${ServerAddress}:22 antes de gerar o backup..."
if (-not (Test-NetConnection -ComputerName $ServerAddress -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    throw @"
Nao foi possivel conectar a ${ServerAddress}:22. Nenhum novo backup foi gerado e nada foi enviado.
No computador de destino, confira o IP com ipconfig e execute no PowerShell como Administrador:
  Get-Service sshd
  Get-NetTCPConnection -State Listen -LocalPort 22
O servico deve estar Running e escutando no IP da rede ou em 0.0.0.0/::.
Se estiver correto, confira a regra de entrada TCP 22 do firewall e o acesso entre os computadores.
"@
}
if ($SshKeyPath) {
    Write-Host "Testando a chave SSH para $destination..."
    $remoteIdentity = @(& ssh @sshOptions -T $destination whoami)
    if ($LASTEXITCODE -ne 0) {
        throw 'A autenticacao por chave falhou. Confira o cadastro da chave publica no servidor e a chave do host em known_hosts. Nenhum backup foi gerado. Chaves protegidas por senha precisam estar carregadas no ssh-agent.'
    }
    $expectedUser = [regex]::Escape($WindowsUser)
    if (-not ($remoteIdentity -match "(?i)^[^\\]+\\${expectedUser}$")) {
        throw 'A identidade retornada pelo servidor nao corresponde ao usuario solicitado. Nenhum backup foi gerado.'
    }
    Write-Host "Autenticacao confirmada: $($remoteIdentity -join ' ')"
}
# Every transfer starts with a new dump and a new source snapshot.
# Deliberately accept no prebuilt package, which could contain stale data.
$prepareOptions = @{ Database = $Database; DatabaseUser = $DatabaseUser }
if ($SourceContainer) { $prepareOptions.SourceContainer = $SourceContainer }
if ($OutputDirectory) { $prepareOptions.OutputDirectory = $OutputDirectory }
Write-Host 'Gerando uma copia nova do banco e do codigo antes do envio...'
$packagePath = & (Join-Path $PSScriptRoot 'preparar.ps1') @prepareOptions
$packagePath = (Resolve-Path -LiteralPath $packagePath).Path
$filename = Split-Path $packagePath -Leaf
if ($filename -notmatch '^appeventos-[0-9]{8}-[0-9]{6}-[a-f0-9]{8}\.tar\.gz$') {
    throw 'Use o arquivo .tar.gz produzido por preparar.ps1, sem renomea-lo.'
}
$hash = (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash
# Keep SSH host verification and authentication enabled. No password is saved.
& scp @sshOptions $packagePath "${destination}:$filename"
if ($LASTEXITCODE -ne 0) {
    throw 'A transferencia falhou. Verifique o usuario, o OpenSSH Server e a porta 22 no destino.'
}
$remoteScript = @'
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
try {
    $archive = Join-Path $env:USERPROFILE '__FILENAME__'
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne '__HASH__') {
        throw 'O SHA256 do pacote transferido nao confere.'
    }
    $release = '__FILENAME__'.Replace('.tar.gz', '')
    $directory = Join-Path $env:LOCALAPPDATA ('AppGrandesEventos/releases/' + $release)
    if (Test-Path -LiteralPath $directory) {
        throw "Este pacote ja foi extraido. Para executar novamente, use $directory/instalar.ps1."
    }
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    & tar -xzf $archive -C $directory
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao extrair o pacote.' }
    # Windows PowerShell 5.1 serializes information/warning streams as CLIXML
    # over SSH even with OutputFormat Text. Render these streams explicitly.
    & (Join-Path $directory 'instalar.ps1') -BundleDirectory $directory -WebPort __PORT__ -ServerAddress '__SERVER__' 3>&1 4>&1 5>&1 6>&1 |
        ForEach-Object { [Console]::WriteLine($_.ToString()) }
    [Console]::WriteLine("Pacote instalado em $directory")
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    [Console]::Error.WriteLine($_.InvocationInfo.PositionMessage)
    [Console]::Error.WriteLine($_.ScriptStackTrace)
    exit 1
}
'@
$remoteScript = $remoteScript.Replace('__FILENAME__', $filename).Replace('__HASH__', $hash).
    Replace('__PORT__', [string]$WebPort).Replace('__SERVER__', $ServerAddress)
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($remoteScript))
& ssh @sshOptions -T $destination powershell.exe -NoProfile -NonInteractive -OutputFormat Text -ExecutionPolicy Bypass -EncodedCommand $encoded
if ($LASTEXITCODE -ne 0) { throw 'A instalacao remota falhou. Consulte a mensagem acima.' }
Write-Host "Teste o acesso pela rede: http://${ServerAddress}:$WebPort"
