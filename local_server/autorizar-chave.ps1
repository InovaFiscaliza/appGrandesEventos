#requires -Version 5.1
#requires -RunAsAdministrator
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$PublicKeyFile,
    [ValidatePattern('^[a-zA-Z0-9_.-]+$')][string]$WindowsUser = 'andre',
    [string]$ClientAddress = '192.168.1.5'
)
$ErrorActionPreference = 'Stop'

# Run locally on the server, under the same account that owns Podman.
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
if (($identity.Name -split '\\')[-1] -ine $WindowsUser) {
    throw "Abra o PowerShell como Administrador na conta $WindowsUser, que executa o Podman."
}
$publicKeyPath = (Resolve-Path -LiteralPath $PublicKeyFile).Path
$publicKey = [IO.File]::ReadAllText($publicKeyPath).Trim()
if ($publicKey -notmatch '^ssh-ed25519 [A-Za-z0-9+/]+={0,2}(?: [^\r\n]+)?$') {
    throw 'Informe somente o arquivo .pub da chave Ed25519. Nunca copie a chave privada.'
}
& ssh-keygen -lf $publicKeyPath
if ($LASTEXITCODE -ne 0) { throw 'Chave publica invalida.' }

$sshdPath = Join-Path $env:SystemRoot 'System32/OpenSSH/sshd.exe'
$effectiveConfig = @(& $sshdPath -T -C "user=$WindowsUser,host=$env:COMPUTERNAME,addr=$ClientAddress")
if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel validar a configuracao do OpenSSH Server.' }
if ($effectiveConfig -notcontains 'pubkeyauthentication yes') {
    throw 'A configuracao do sshd nao permite PubkeyAuthentication. Habilite essa opcao antes de cadastrar a chave.'
}
$authorizedFile = Join-Path $env:ProgramData 'ssh/administrators_authorized_keys'
$authorizedSetting = @($effectiveConfig | Where-Object { $_.StartsWith('authorizedkeysfile ') })
$expectedSettingPath = $authorizedFile.Replace('\', '/')
$usesAdminFile = $false
foreach ($setting in $authorizedSetting) {
    foreach ($configuredPath in $setting.Substring('authorizedkeysfile '.Length).Split(' ')) {
        $resolvedSettingPath = $configuredPath.Replace('__PROGRAMDATA__', $env:ProgramData).Replace('\', '/')
        if ($resolvedSettingPath -ieq $expectedSettingPath) { $usesAdminFile = $true }
    }
}
if (-not $usesAdminFile) {
    throw 'Este instalador espera o arquivo padrao de chaves dos administradores. A configuracao atual usa outro caminho; nenhum arquivo foi alterado.'
}

$existing = ''
if (Test-Path -LiteralPath $authorizedFile) {
    $existing = [IO.File]::ReadAllText($authorizedFile)
    $backup = $authorizedFile + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    Copy-Item -LiteralPath $authorizedFile -Destination $backup
    Write-Host "Copia anterior preservada em: $backup"
}
$keyData = ($publicKey -split ' ')[1]
if ($existing -notmatch ('(?m)^\s*(?:[^\r\n]*\s)?ssh-ed25519\s+' + [regex]::Escape($keyData) + '(?:\s|$)')) {
    $separator = if ($existing.Length -gt 0 -and -not $existing.EndsWith("`n")) { "`r`n" } else { '' }
    [IO.File]::WriteAllText($authorizedFile, $existing + $separator + $publicKey + "`r`n", [Text.UTF8Encoding]::new($false))
}

# Numeric SIDs work on Windows in Portuguese as well as English.
& icacls.exe $authorizedFile /inheritance:r /grant:r '*S-1-5-32-544:(F)' '*S-1-5-18:(F)'
if ($LASTEXITCODE -ne 0) { throw 'Falha ao configurar as permissoes das chaves autorizadas.' }
$allowedSids = @('S-1-5-32-544', 'S-1-5-18')
foreach ($rule in (Get-Acl -LiteralPath $authorizedFile).Access) {
    $sid = $rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
    if ($sid -notin $allowedSids) {
        & icacls.exe $authorizedFile /remove ('*' + $sid)
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao remover uma permissao incompativel com OpenSSH.' }
    }
}
Write-Host "Chave publica cadastrada para acesso SSH de administradores, incluindo $WindowsUser."
Write-Host 'Agora teste a conexao por chave no computador do projeto.'
