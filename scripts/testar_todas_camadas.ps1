param([switch]$SemNavegador)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$sufixo = [guid]::NewGuid().ToString('N').Substring(0, 8)
$nomeContainer = "appgrandeseventos-testes-$sufixo"
$nomeBanco = "appeventos_test_$sufixo"
$containerId = $null
$urlAnterior = $env:TEST_DATABASE_URL
$codigoSaida = 1

Push-Location $raiz
try {
    & uv run --locked python -m scripts.testar_regressoes
    if ($LASTEXITCODE -ne 0) { throw 'A camada sem banco falhou.' }

    $containerId = & podman run --detach --name $nomeContainer `
        --label appgrandeseventos.finalidade=testes `
        --publish '127.0.0.1::5432' `
        --env POSTGRES_USER=testes --env POSTGRES_PASSWORD=testes `
        --env "POSTGRES_DB=$nomeBanco" `
        --health-cmd "pg_isready -U testes -d $nomeBanco" `
        --health-interval 1s --health-timeout 3s --health-retries 30 `
        docker.io/library/postgres:16
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel criar o PostgreSQL de testes.' }
    $containerId = ([string]$containerId).Trim()
    if ($containerId -notmatch '^[a-f0-9]{64}$') { throw 'ID inesperado do container de testes.' }

    & podman wait --condition healthy --condition unhealthy $containerId
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao aguardar o banco de testes.' }
    & podman exec $containerId pg_isready -U testes -d $nomeBanco
    if ($LASTEXITCODE -ne 0) { throw 'O PostgreSQL de testes nao ficou pronto.' }

    $inspecao = (& podman inspect $containerId | Out-String | ConvertFrom-Json)[0]
    $porta = $inspecao.NetworkSettings.Ports.'5432/tcp'[0].HostPort
    $env:TEST_DATABASE_URL = "postgresql+psycopg://testes:testes@127.0.0.1:$porta/$nomeBanco"
    if ($SemNavegador) {
        & uv run --locked python -m scripts.testar_integracao
    } else {
        & uv run --locked playwright install chromium
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar Chromium.' }
        & uv run --locked python -m scripts.testar_integracao --navegador
    }
    $codigoSaida = $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    $codigoSaida = 1
} finally {
    if ($containerId -and $containerId -match '^[a-f0-9]{64}$') {
        $inspecaoFinal = (& podman inspect $containerId | Out-String | ConvertFrom-Json)[0]
        $rotulo = $inspecaoFinal.Config.Labels.'appgrandeseventos.finalidade'
        if ($LASTEXITCODE -eq 0 -and $rotulo -eq 'testes') {
            & podman rm --force --volumes $containerId
            if ($LASTEXITCODE -ne 0) { $codigoSaida = 1 }
        } else {
            Write-Warning "Container nao removido: rotulo de teste nao confirmado para $nomeContainer."
            $codigoSaida = 1
        }
    }
    $env:TEST_DATABASE_URL = $urlAnterior
    Pop-Location
}
exit $codigoSaida