#requires -Version 5.1
#requires -RunAsAdministrator
[CmdletBinding()]
param([ValidateRange(1024, 65535)][int]$WebPort = 8501)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'configurar-rede.ps1') -WebPort $WebPort
$ruleName = "AppGrandesEventos-Web-$WebPort"
if (-not (Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name $ruleName -DisplayName "AppGrandesEventos Web TCP $WebPort" `
        -Direction Inbound -Action Allow -Protocol TCP -LocalPort $WebPort `
        -Profile Private,Domain -RemoteAddress LocalSubnet | Out-Null
}
Write-Host "Regra da porta TCP $WebPort conferida para acesso pela rede local."
