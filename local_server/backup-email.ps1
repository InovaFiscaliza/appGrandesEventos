#requires -Version 5.1
<#
Execute no pcmanu, com o mesmo usuario Windows que executa o Podman.
Exemplo:
  .\local_server\backup-email.ps1 -SmtpServer smtp.exemplo.gov.br -From usuario@exemplo.gov.br
Informe o servidor SMTP e o remetente autorizados pela sua organizacao.
O backup inclui os dados do sistema: envie somente por canal autorizado.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SmtpServer,
    [Parameter(Mandatory)][string]$From,
    [ValidateRange(1, 65535)][int]$SmtpPort = 587,
    [string]$To = 'andrerezende@anatel.gov.br',
    [string]$Container = 'appeventos-db',
    [string]$Database = 'appeventos',
    [string]$DatabaseUser = 'appeventos',
    [string]$BackupDirectory = (Join-Path $PSScriptRoot '..\bd_backup'),
    [System.Management.Automation.PSCredential]$SmtpCredential,
    [switch]$NoAuthentication
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    throw 'Podman nao encontrado. Execute este script no pcmanu.'
}

$filename = 'backup_pcmanu_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.dump'
New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
$backupPath = Join-Path (Resolve-Path -LiteralPath $BackupDirectory).Path $filename
$containerPath = "/tmp/$filename"

Write-Host 'Gerando backup compactado sem modificar o banco...'
& podman exec $Container pg_dump --no-password --username $DatabaseUser --dbname $Database --format custom --file $containerPath
if ($LASTEXITCODE -ne 0) { throw 'pg_dump falhou. Nenhum email foi enviado.' }
& podman exec $Container pg_restore --list $containerPath | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'O arquivo de backup nao possui um indice valido. Nenhum email foi enviado.' }
& podman cp "${Container}:$containerPath" $backupPath
if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o backup do container. Nenhum email foi enviado.' }
if ((Get-Item -LiteralPath $backupPath).Length -eq 0) { throw 'O arquivo de backup esta vazio.' }
Write-Host "Backup salvo: $backupPath"

if (-not $NoAuthentication -and -not $SmtpCredential) {
    $SmtpCredential = Get-Credential -UserName $From -Message 'Informe a credencial SMTP (nao a senha do banco)'
    if (-not $SmtpCredential) { throw 'Envio cancelado. O backup local foi preservado.' }
}
$message = $null
$attachment = $null
$smtp = $null
try {
    $message = [System.Net.Mail.MailMessage]::new($From, $To)
    $message.Subject = 'Backup AppGrandesEventos - pcmanu - ' + (Get-Date -Format 'yyyy-MM-dd HH:mm')
    $message.Body = "Backup do banco $Database no pcmanu, em formato pg_dump custom, anexado."
    $attachment = [System.Net.Mail.Attachment]::new($backupPath)
    $message.Attachments.Add($attachment)
    $smtp = [System.Net.Mail.SmtpClient]::new($SmtpServer, $SmtpPort)
    $smtp.EnableSsl = $true
    $smtp.UseDefaultCredentials = $false
    $smtp.Timeout = 120000
    if (-not $NoAuthentication) { $smtp.Credentials = $SmtpCredential.GetNetworkCredential() }
    $smtp.Send($message)
    Write-Host "Email enviado para $To. Backup local preservado."
} catch {
    throw "Falha ao enviar email. Backup preservado em ${backupPath}. Detalhes: $($_.Exception.Message)"
} finally {
    if ($smtp) { $smtp.Dispose() }
    if ($message) { $message.Dispose() }
    if ($attachment) { $attachment.Dispose() }
}