#requires -Version 5.1
# Invoked by atualiza_serv.bat. A child process keeps deployment output and
# native stderr in the log without changing the deployment's error handling.
$ErrorActionPreference = 'Stop'
$started = Get-Date
$result = 1
$writer = $null
$logPath = $null

function Write-DeploymentLog {
    param([string]$Message)
    [Console]::WriteLine($Message)
    $writer.WriteLine(('[' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff') + '] ' + $Message))
}

try {
    $logDirectory = $env:PASTA_LOG
    if ([string]::IsNullOrWhiteSpace($logDirectory)) { $logDirectory = Join-Path $PSScriptRoot 'logs' }
    if (-not [IO.Path]::IsPathRooted($logDirectory)) { $logDirectory = Join-Path $PSScriptRoot $logDirectory }
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    $logName = 'atualiza_serv-' + $started.ToString('yyyyMMdd-HHmmss-fff') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.log'
    $logPath = Join-Path (Resolve-Path -LiteralPath $logDirectory).Path $logName
    $writer = [IO.StreamWriter]::new($logPath, $false, [Text.UTF8Encoding]::new($false))
    $writer.AutoFlush = $true

    Write-DeploymentLog "Log desta execucao: $logPath"
    Write-DeploymentLog "Inicio: $($started.ToString('o'))"
    Write-DeploymentLog "Origem: $env:COMPUTERNAME | PowerShell: $($PSVersionTable.PSVersion)"
    Write-DeploymentLog "Destino: $env:USUARIO_SERVIDOR@$env:SERVIDOR_IP | Porta web: $env:PORTA_WEB"
    Write-DeploymentLog "Projeto: $([IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')))"
    Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')

    if ([string]::IsNullOrWhiteSpace($env:USUARIO_SERVIDOR) -or $env:USUARIO_SERVIDOR -eq 'SEU_USUARIO' -or
        [string]::IsNullOrWhiteSpace($env:SERVIDOR_IP) -or [string]::IsNullOrWhiteSpace($env:PORTA_WEB)) {
        $result = 2
        throw 'Edite atualiza_serv.bat e preencha SERVIDOR_IP, USUARIO_SERVIDOR e PORTA_WEB antes de executar.'
    }
    Write-DeploymentLog 'Atualizando o servidor com o codigo e o backup local atuais...'
    Write-DeploymentLog 'Os dados existentes no servidor serao preservados.'
    Write-DeploymentLog 'Os containers web e PostgreSQL 16 remotos serao parados e recriados automaticamente.'
    Write-DeploymentLog 'A conexao SSH usara a chave configurada em CHAVE_SSH.'

    # PS 5.1 wraps native stderr as ErrorRecord objects. Continue here so that
    # normal SSH/Podman stderr is logged; the child retains its own Stop policy.
    $ErrorActionPreference = 'Continue'
    & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $PSScriptRoot 'enviar.ps1') -ServerAddress $env:SERVIDOR_IP `
        -WindowsUser $env:USUARIO_SERVIDOR -WebPort $env:PORTA_WEB -SshKeyPath $env:CHAVE_SSH 2>&1 |
        ForEach-Object -ErrorAction Stop { Write-DeploymentLog $_.ToString() }
    $result = $LASTEXITCODE
} catch {
    $details = $_.Exception.ToString() + [Environment]::NewLine + $_.InvocationInfo.PositionMessage
    [Console]::Error.WriteLine($details)
    if ($writer) { $writer.WriteLine($details) }
} finally {
    $ErrorActionPreference = 'Stop'
    if ($writer) {
        try {
            $status = if ($result -eq 0) { 'SUCESSO' } else { 'FALHA' }
            Write-DeploymentLog "Resultado: $status | Codigo de saida: $result"
            Write-DeploymentLog "Fim: $((Get-Date).ToString('o')) | Duracao: $((Get-Date) - $started)"
        } finally { $writer.Dispose() }
        [Console]::WriteLine("Log salvo em: $logPath")
    } else {
        [Console]::Error.WriteLine('Nao foi possivel criar o log. Verifique a pasta configurada em PASTA_LOG.')
    }
}
exit $result
