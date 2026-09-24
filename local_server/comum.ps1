# Helpers shared by the Windows PowerShell 5.1 deployment scripts.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Podman {
    param([Parameter(Mandatory)][string[]]$Arguments)
    & podman @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Podman falhou na operacao '$($Arguments[0])' (codigo $LASTEXITCODE)."
    }
}

function Test-PodmanResource {
    param([string]$Kind, [string]$Name)
    & podman $Kind exists $Name
    if ($LASTEXITCODE -eq 0) { return $true }
    if ($LASTEXITCODE -eq 1) { return $false }
    throw "Nao foi possivel consultar $Kind '$Name'."
}

function Assert-ManagedResource {
    param([string]$Kind, [string]$Name)
    $item = @(Invoke-Podman -Arguments @($Kind, 'inspect', $Name) | ConvertFrom-Json)[0]
    $labels = if ($Kind -eq 'container') { $item.Config.Labels } else { $item.Labels }
    if (-not $labels -or $labels.'io.appgrandeseventos.managed' -ne 'true') {
        throw "O recurso '$Name' ja existe e nao pertence a estes scripts. Nada foi removido."
    }
}

function Assert-PodmanReady {
    if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
        throw 'Instale o Podman Desktop e inicialize a maquina Linux antes de continuar.'
    }
    # Do not silently select another connection or initialize a second machine.
    & podman info --format '{{.Host.OS}}' 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Abra o Podman Desktop, inicie a maquina e verifique podman ps neste mesmo usuario Windows.'
    }
}

function Wait-Database {
    param([string]$Container)
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        & podman exec $Container pg_isready --host 127.0.0.1 --username appeventos --dbname appeventos 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { return }
        Start-Sleep -Seconds 2
    }
    throw "Banco nao ficou pronto. Consulte: podman logs $Container"
}

function Show-DeploymentContainerLog {
    param([string]$Container)
    $previousPreference = $ErrorActionPreference
    try {
        Write-Host "Ultimas mensagens de ${Container}:"
        $ErrorActionPreference = 'Continue'
        & podman logs --tail 80 $Container 2>&1 | ForEach-Object { Write-Host "$_" }
    } catch { Write-Warning "Nao foi possivel obter o log de $Container." }
    finally { $ErrorActionPreference = $previousPreference }
}

function Wait-WebApplication {
    param([int]$Port)
    $lastFailure = 'Nenhuma resposta HTTP recebida.'
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -DisableKeepAlive -Uri "http://127.0.0.1:$Port/" -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return }
            $lastFailure = "HTTP $($response.StatusCode)"
        } catch { $lastFailure = $_.Exception.Message }
        Start-Sleep -Seconds 2
    }
    throw "Aplicacao nao respondeu em http://127.0.0.1:$Port/. Ultima falha: $lastFailure"
}

function New-RandomHex {
    $bytes = New-Object byte[] 32
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
    return [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
}

function New-PodmanSecret {
    param([string]$Name, [string]$Value)
    $temporaryFile = [IO.Path]::GetTempFileName()
    try {
        [IO.File]::WriteAllText($temporaryFile, $Value, [Text.UTF8Encoding]::new($false))
        Invoke-Podman -Arguments @('secret', 'create', $Name, $temporaryFile) | Out-Null
    } finally {
        Remove-Item -LiteralPath $temporaryFile -Force
    }
}
