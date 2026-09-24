#requires -Version 5.1
[CmdletBinding()]
param([ValidateRange(1024, 65535)][int]$WebPort = 8501)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# Match the active Podman connection to its WSL machine. Do not change
# another machine or the global WSL networking configuration.
$connections = & podman system connection list --format json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar a conexao do Podman.' }
$active = @($connections | Where-Object { $_.Default })
$machines = & podman machine list --format json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar as maquinas do Podman.' }
if ($active.Count -ne 1) { throw 'Nao foi possivel identificar a conexao ativa do Podman.' }
$connectionPort = ([uri]$active[0].URI).Port
$matching = @($machines | Where-Object { $_.Running -and $_.VMType -eq 'wsl' -and $_.Port -eq $connectionPort })
if ($matching.Count -eq 0) { return }
if ($matching.Count -ne 1) { throw 'Mais de uma maquina WSL corresponde a conexao do Podman.' }
$machineName = $matching[0].Name
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { throw 'Para configurar a porta do WSL, execute a instalacao como Administrador no servidor.' }

$routes = @(& wsl.exe -d $machineName -- ip -4 -j route show default | ConvertFrom-Json | ForEach-Object { $_ })
if ($LASTEXITCODE -ne 0 -or $routes.Count -ne 1) { throw 'Nao foi possivel identificar a interface de rede do WSL.' }
$interfaces = @(& wsl.exe -d $machineName -- ip -4 -j address show dev $routes[0].dev | ConvertFrom-Json | ForEach-Object { $_ })
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar o IPv4 do WSL.' }
$addresses = @($interfaces.addr_info | Where-Object { $_.family -eq 'inet' -and $_.scope -eq 'global' })
if ($addresses.Count -ne 1) { throw 'O WSL precisa ter um IPv4 identificavel para o encaminhamento.' }
$wslAddress = $addresses[0].local
$parsedAddress = $null
if (-not [Net.IPAddress]::TryParse($wslAddress, [ref]$parsedAddress) -or
    $parsedAddress.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) {
    throw 'O endereco IPv4 retornado pelo WSL e invalido.'
}
# Mirrored networking uses a host address and must not proxy back to itself.
if (Get-NetIPAddress -AddressFamily IPv4 -IPAddress $wslAddress -ErrorAction SilentlyContinue) {
    Write-Host 'WSL compartilha o endereco do Windows; encaminhamento NAT dispensado.'
    return
}

$stateDirectory = Join-Path $env:LOCALAPPDATA 'AppGrandesEventos/network'
$statePath = Join-Path $stateDirectory "port-$WebPort.json"
$state = if (Test-Path -LiteralPath $statePath) { Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } else { $null }
$proxyLines = @(& netsh interface portproxy show v4tov4)
if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar os encaminhamentos de porta do Windows.' }
$existing = @($proxyLines | Where-Object { $_ -match "^\s*\d+\.\d+\.\d+\.\d+\s+$WebPort\s+" })
if ($existing.Count -gt 0) {
    $expected = if ($state) { '^\s*0\.0\.0\.0\s+' + $WebPort + '\s+' + [regex]::Escape($state.address) + '\s+' + $WebPort + '\s*$' } else { '' }
    if (-not $state -or $state.machine -ne $machineName -or $existing.Count -ne 1 -or $existing[0] -notmatch $expected) {
        throw "A porta $WebPort ja possui encaminhamento nao reconhecido. Nenhuma regra foi substituida."
    }
} elseif (Get-NetTCPConnection -State Listen -LocalPort $WebPort -ErrorAction SilentlyContinue) {
    throw "A porta $WebPort ja esta em uso no Windows. Nenhum encaminhamento foi criado."
}

Start-Service iphlpsvc
$operation = if ($existing.Count -gt 0) { 'set' } else { 'add' }
& netsh interface portproxy $operation v4tov4 listenaddress=0.0.0.0 "listenport=$WebPort" "connectaddress=$wslAddress" "connectport=$WebPort" protocol=tcp | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar o encaminhamento da porta da aplicacao.' }
New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
@{ machine = $machineName; address = $wslAddress; port = $WebPort } | ConvertTo-Json |
    Set-Content -LiteralPath $statePath -Encoding UTF8

# The server may classify its home Wi-Fi as Public. Limit this one application
# port to the local subnet without changing the network profile or SSH rules.
$ruleName = "AppGrandesEventos-Web-$WebPort"
$existingRule = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
if ($existingRule) {
    Set-NetFirewallRule -Name $ruleName -Enabled True -Direction Inbound -Action Allow -Profile Any -RemoteAddress LocalSubnet | Out-Null
} else {
    New-NetFirewallRule -Name $ruleName -DisplayName "AppGrandesEventos Web TCP $WebPort" `
        -Direction Inbound -Action Allow -Protocol TCP -LocalPort $WebPort `
        -Profile Any -RemoteAddress LocalSubnet | Out-Null
}
Write-Host "Rede configurada: Windows TCP $WebPort -> ${wslAddress}:$WebPort (WSL), acesso pela rede local."
