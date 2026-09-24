#requires -Version 5.1
# Tests use a fake Podman command. No containers or real databases are touched.
$ErrorActionPreference = 'Stop'
$testRoot = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')).Path ('.deploy/tests with spaces-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
$originalLocalAppData = $env:LOCALAPPDATA
$env:LOCALAPPDATA = $testRoot
try {
    $global:podmanTestresources = @{}
    $global:podmanTestcontainerRunning = @{}
    $global:podmanTestcalls = New-Object System.Collections.ArrayList
    $global:podmanTestrestoreCount = 0
    $global:podmanTestdatabases = @{ appeventos = 'empty' }
    $global:podmanTestfailRestore = $false
    $global:podmanTestfailMigration = $false
    $global:podmanTestmigrationCount = 0
    $global:podmanTestfailWeb = $false
    $global:podmanTestfailDatabase = $false
    $global:podmanTestdatabaseReadinessFailures = 0
    $global:podmanTestfailReadinessId = $null
    $global:podmanTestfailPull = $false
    $global:podmanTesthttpFailures = 0
    $global:podmanTestforeignNetwork = $false
    $global:podmanTestsourceRunning = $true
    $global:podmanTestdumpCount = 0
    $global:podmanTestsshReachable = $true
    $global:podmanTestkeyAccepted = $true
    $global:podmanTestremoteIdentity = 'PC-TESTE\test-user'

    function Test-NetConnection {
        [CmdletBinding()]
        param([string]$ComputerName, [int]$Port, [string]$InformationLevel)
        $global:podmanTestconnectionTarget = "${ComputerName}:$Port"
        return $global:podmanTestsshReachable
    }

    function podman {
        param([Parameter(ValueFromRemainingArguments)][string[]]$Arguments)
        $global:LASTEXITCODE = 0
        [void]$global:podmanTestcalls.Add($Arguments)
        $operation = $Arguments[0]
        if ($operation -eq 'info') { return 'linux' }
        if ($operation -eq 'system' -and $Arguments[1] -eq 'connection') { return '[{"Default":true,"URI":"ssh://test@localhost:2222/run/podman/podman.sock"}]' }
        if ($operation -eq 'machine') { return '[]' }
        if ($operation -eq 'port') { return '0.0.0.0:8501' }
        if ($operation -eq 'pull') { if ($global:podmanTestfailPull) { $global:LASTEXITCODE = 125 }; return }
        if ($operation -eq 'image') { return 'sha256:simulated-postgres16-image' }
        if ($operation -eq 'stop') { $global:podmanTestcontainerRunning[$Arguments[-1]] = $false; return }
        if ($operation -eq 'start') { $global:podmanTestcontainerRunning[$Arguments[-1]] = $true; return }
        if ($Arguments[1] -eq 'exists') {
            if (-not $global:podmanTestresources.ContainsKey("${operation}:$($Arguments[2])")) { $global:LASTEXITCODE = 1 }
            return
        }
        if ($Arguments[1] -eq 'inspect') {
            $managed = if ($global:podmanTestforeignNetwork -and $operation -eq 'network') { 'false' } else { 'true' }
            return (@{ Id = 'test-container-id'; State = @{ Running = $global:podmanTestsourceRunning }; Labels = @{ 'io.appgrandeseventos.managed' = $managed }; Config = @{ Labels = @{ 'io.appgrandeseventos.managed' = $managed } } } | ConvertTo-Json -Depth 4 -Compress)
        }
        if ($Arguments[1] -eq 'create') {
            $name = if ($operation -eq 'secret') { $Arguments[2] } else { $Arguments[-1] }
            $global:podmanTestresources["${operation}:$name"] = $true
            return 'created'
        }
        if ($operation -eq 'run') {
            if ($Arguments -contains '/app/deployment/migrar.py') {
                if ($global:podmanTestfailMigration) { $global:LASTEXITCODE = 1; return }
                $global:podmanTestmigrationCount++
            }
            $position = [array]::IndexOf($Arguments, '--name')
            if ($position -ge 0) {
                $name = $Arguments[$position + 1]
                if ($name -eq 'appeventos-db') {
                    if (@($global:podmanTestcontainerRunning.Keys | Where-Object { $_ -like 'appeventos-db*' -and $global:podmanTestcontainerRunning[$_] }).Count) {
                        throw 'Two database containers must never run on the same volume'
                    }
                    if ($global:podmanTestfailDatabase) { $global:podmanTestfailDatabase = $false; $global:LASTEXITCODE = 125; return }
                }
                if ($name -eq 'appeventos-web' -and $global:podmanTestfailWeb) {
                    $global:podmanTestfailWeb = $false
                    $global:LASTEXITCODE = 125
                    return
                }
                $global:podmanTestresources["container:$name"] = [guid]::NewGuid().ToString('N')
                $global:podmanTestcontainerRunning[$name] = $true
                if ($name -eq 'appeventos-db' -and $global:podmanTestdatabaseReadinessFailures -gt 0) {
                    $global:podmanTestfailReadinessId = $global:podmanTestresources["container:$name"]
                }
            }
            return 'started'
        }
        if ($operation -eq 'exec') {
            if ($Arguments[2] -eq 'pg_isready' -and $global:podmanTestdatabaseReadinessFailures -gt 0 -and
                $global:podmanTestfailReadinessId -eq $global:podmanTestresources['container:appeventos-db']) {
                $global:podmanTestdatabaseReadinessFailures--
                $global:LASTEXITCODE = 1
                return
            }
            if ($Arguments[2] -eq 'pg_dump') { $global:podmanTestdumpCount++; return }
            if ($Arguments -contains 'server_version_num' -or $Arguments[-1] -eq 'SHOW server_version_num') { return '160014' }
            if ($Arguments[2] -eq 'createdb') {
                $global:podmanTestdatabases[$Arguments[-1]] = if ($Arguments -contains '--template=appeventos') {
                    $global:podmanTestdatabases.appeventos
                } else { 'empty' }
                return
            }
            if ($Arguments[2] -eq 'dropdb') { $global:podmanTestdatabases.Remove($Arguments[-1]); return }
            if ($Arguments[2] -eq 'pg_restore' -and $Arguments -contains '--single-transaction') {
                $global:podmanTestrestoreCount++
                if ($global:podmanTestfailRestore) { $global:LASTEXITCODE = 1; return }
                $target = @($Arguments | Where-Object { $_.StartsWith('--dbname=') })[0].Substring(9)
                $global:podmanTestdatabases[$target] = "local-snapshot-$global:podmanTestrestoreCount"
            }
            if ($Arguments[2] -eq 'psql' -and $Arguments[-1].StartsWith('BEGIN;')) {
                foreach ($rename in [regex]::Matches($Arguments[-1], 'ALTER DATABASE (\w+) RENAME TO (\w+)')) {
                    $oldName = $rename.Groups[1].Value
                    $newName = $rename.Groups[2].Value
                    if (-not $global:podmanTestdatabases.ContainsKey($oldName) -or $global:podmanTestdatabases.ContainsKey($newName)) {
                        throw 'Invalid simulated database rename'
                    }
                    $global:podmanTestdatabases[$newName] = $global:podmanTestdatabases[$oldName]
                    $global:podmanTestdatabases.Remove($oldName)
                }
            }
            if ($Arguments[2] -eq 'psql' -and $Arguments[-1].StartsWith('SELECT count(*) FROM pg_class')) {
                if ($global:podmanTestdatabases.appeventos -eq 'empty') { return '0' }
                return '1'
            }
            return
        }
        if ($operation -eq 'cp' -and $Arguments[1].StartsWith('postgres-appeventos:')) {
            [IO.File]::WriteAllText($Arguments[2], "PGDMP fake database snapshot $global:podmanTestdumpCount")
            return
        }
        if ($operation -eq 'rename') {
            $resourceId = $global:podmanTestresources["container:$($Arguments[1])"]
            $global:podmanTestresources.Remove("container:$($Arguments[1])")
            $global:podmanTestresources["container:$($Arguments[2])"] = $resourceId
            $global:podmanTestcontainerRunning[$Arguments[2]] = $global:podmanTestcontainerRunning[$Arguments[1]]
            $global:podmanTestcontainerRunning.Remove($Arguments[1])
        }
        if ($operation -eq 'rm') {
            $global:podmanTestresources.Remove("container:$($Arguments[-1])")
            $global:podmanTestcontainerRunning.Remove($Arguments[-1])
        }
    }
    function Invoke-WebRequest {
        param($Uri, $TimeoutSec, [switch]$UseBasicParsing, [switch]$DisableKeepAlive)
        if ($global:podmanTesthttpFailures -gt 0) {
            $global:podmanTesthttpFailures--
            throw 'Simulated HTTP startup failure'
        }
        return @{ StatusCode = 200 }
    }
    function Start-Sleep { param([int]$Seconds) }
    function Assert-Test { param([bool]$Condition, [string]$Message) if (-not $Condition) { throw "FAIL: $Message" }; Write-Host "PASS: $Message" }

    $global:podmanTestresources['container:postgres-appeventos'] = $true
    $package = & (Join-Path $PSScriptRoot 'preparar.ps1') -OutputDirectory $testRoot
    Assert-Test (Test-Path -LiteralPath $package) 'Package created with automatic source detection'
    $bundle = $package.Replace('.tar.gz', '')
    $archiveEntries = & tar -tzf $package
    Assert-Test ($LASTEXITCODE -eq 0) 'Generated tar archive can be read'
    Assert-Test ([bool]($archiveEntries -match 'database.dump')) 'Database backup included in package'
    Assert-Test (-not [bool]($archiveEntries -match '__pycache__|\.venv|\.git/|secrets.toml')) 'Local environment and credentials excluded'
    $manifest = Get-Content -LiteralPath (Join-Path $bundle 'manifest.json') -Raw | ConvertFrom-Json
    $root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    Assert-Test ($manifest.source_files_sha256.'main.py' -eq (Get-FileHash -LiteralPath (Join-Path $root 'main.py')).Hash) 'Source manifest matches current project files'

    $installer = Join-Path $PSScriptRoot 'instalar.ps1'
    & (Join-Path $bundle 'instalar.ps1')
    Assert-Test ($global:podmanTestrestoreCount -eq 1 -and $global:podmanTestdatabases.appeventos -eq 'local-snapshot-1') 'Installation puts the local database snapshot into use'
    Assert-Test ($global:podmanTestmigrationCount -eq 1) 'Schema migrations run on the initial database'
    Assert-Test ($global:podmanTestresources.ContainsKey('container:appeventos-web')) 'Web container started'
    $databaseRun = @($global:podmanTestcalls | Where-Object { $_[0] -eq 'run' -and $_ -contains 'appeventos-db' })[0]
    Assert-Test (-not ($databaseRun -contains '--publish')) 'Database port is not exposed'
    $global:podmanTestdatabases.appeventos = 'server-only-records'
    $oldDatabaseId = $global:podmanTestresources['container:appeventos-db']
    $oldWebId = $global:podmanTestresources['container:appeventos-web']
    $callsBefore = $global:podmanTestcalls.Count
    & $installer -BundleDirectory $bundle
    Assert-Test ($global:podmanTestresources['container:appeventos-db'] -ne $oldDatabaseId -and $global:podmanTestresources['container:appeventos-web'] -ne $oldWebId) 'Update replaces both remote containers'
    $updateCalls = @($global:podmanTestcalls | Select-Object -Skip $callsBefore)
    $webStop = -1; $databaseStop = -1; $databaseStart = -1
    for ($i = 0; $i -lt $updateCalls.Count; $i++) {
        if ($updateCalls[$i][0] -eq 'stop' -and $updateCalls[$i][-1] -eq 'appeventos-web') { $webStop = $i }
        if ($updateCalls[$i][0] -eq 'stop' -and $updateCalls[$i][-1] -eq 'appeventos-db') { $databaseStop = $i }
        if ($updateCalls[$i][0] -eq 'run' -and $updateCalls[$i] -contains 'appeventos-db') {
            $databaseStart = $i
            Assert-Test ($updateCalls[$i] -contains 'appeventos-pgdata:/var/lib/postgresql/data') 'Database replacement reuses the persistent volume'
        }
    }
    Assert-Test ($webStop -ge 0 -and $databaseStop -gt $webStop -and $databaseStart -gt $databaseStop) 'Web stops before replacing the database'
    Assert-Test ($global:podmanTestrestoreCount -eq 1 -and $global:podmanTestdatabases.appeventos -eq 'server-only-records') 'Updates preserve server data without restoring the local dump'
    Assert-Test ($global:podmanTestmigrationCount -eq 2) 'Updates execute the migration runner on the server clone'
    Assert-Test ($global:podmanTestdatabases.Values -contains 'server-only-records') 'Previous server data is retained for recovery'

    $oldDatabaseId = $global:podmanTestresources['container:appeventos-db']
    $oldWebId = $global:podmanTestresources['container:appeventos-web']
    $global:podmanTestfailPull = $true
    $callsBefore = $global:podmanTestcalls.Count
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test ($failed -and -not @($global:podmanTestcalls | Select-Object -Skip $callsBefore | Where-Object { $_[0] -eq 'stop' }).Count) 'Image download failure leaves the running containers untouched'
    $global:podmanTestfailPull = $false
    $global:podmanTestfailDatabase = $true
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test ($failed -and $global:podmanTestresources['container:appeventos-db'] -eq $oldDatabaseId -and $global:podmanTestresources['container:appeventos-web'] -eq $oldWebId) 'Failed database replacement recovers both original containers'
    Assert-Test ($global:podmanTestcontainerRunning['appeventos-db'] -and $global:podmanTestcontainerRunning['appeventos-web'] -and $global:podmanTestdatabases.appeventos -eq 'server-only-records') 'Database replacement failure restores service without changing records'
    $global:podmanTestdatabaseReadinessFailures = 60
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test ($failed -and $global:podmanTestresources['container:appeventos-db'] -eq $oldDatabaseId -and $global:podmanTestresources['container:appeventos-web'] -eq $oldWebId) 'Unhealthy new database rolls back to the original containers'
    $heldLock = [IO.File]::Open((Join-Path $testRoot 'AppGrandesEventos/deployment.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        $callsBefore = $global:podmanTestcalls.Count
        $failed = $false
        try { & $installer -BundleDirectory $bundle } catch { $failed = $_.Exception.Message.Contains('trava de instalacao') }
        Assert-Test ($failed -and $global:podmanTestcalls.Count -eq $callsBefore + 1) 'Concurrent installer stops before touching any container'
    } finally { $heldLock.Dispose() }

    $global:podmanTestfailWeb = $true
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test $failed 'Failed web replacement reports an error'
    Assert-Test ($global:podmanTestresources.ContainsKey('container:appeventos-web')) 'Previous web container restored after failure'
    Assert-Test ($global:podmanTestdatabases.appeventos -eq 'server-only-records') 'Web failure restores the previous database too'
    Assert-Test ($global:podmanTestresources['container:appeventos-db'] -eq $oldDatabaseId) 'Web failure recovers the previous database container'
    $global:podmanTesthttpFailures = 60
    $callsBefore = $global:podmanTestcalls.Count
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $_.Exception.Message.Contains('Simulated HTTP startup failure') }
    $failureCalls = @($global:podmanTestcalls | Select-Object -Skip $callsBefore)
    $logIndex = -1
    $removeIndex = -1
    for ($i = 0; $i -lt $failureCalls.Count; $i++) {
        if ($failureCalls[$i][0] -eq 'logs' -and $failureCalls[$i][-1] -eq 'appeventos-web') { $logIndex = $i }
        if ($failureCalls[$i][0] -eq 'rm' -and $failureCalls[$i][-1] -eq 'appeventos-web') { $removeIndex = $i }
    }
    Assert-Test $failed 'HTTP failure reports the last connection error'
    Assert-Test ($logIndex -ge 0 -and $removeIndex -gt $logIndex) 'Startup logs are collected before removing the failed web container'
    Assert-Test ($global:podmanTestdatabases.appeventos -eq 'server-only-records') 'HTTP startup failure preserves server data'
    $global:podmanTestfailMigration = $true
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test $failed 'Migration failure prevents switching the running database'
    Assert-Test ($global:podmanTestdatabases.appeventos -eq 'server-only-records') 'Migration failure preserves the active data'
    Assert-Test (-not [bool]($global:podmanTestdatabases.Keys -match '^appeventos_stage_')) 'Failed staging databases are cleaned up'
    $global:podmanTestfailMigration = $false

    $global:podmanTestforeignNetwork = $true
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test $failed 'Unmanaged network is rejected'
    $global:podmanTestforeignNetwork = $false
    [IO.File]::AppendAllText((Join-Path $bundle 'database.dump'), 'corruption')
    $callsBefore = $global:podmanTestcalls.Count
    $failed = $false
    try { & $installer -BundleDirectory $bundle } catch { $failed = $true }
    Assert-Test $failed 'Corrupted database backup is rejected'
    Assert-Test ($global:podmanTestcalls.Count -eq $callsBefore + 1) 'Corrupted backup fails before any container mutation'

    function scp {
        param([Parameter(ValueFromRemainingArguments)][string[]]$Arguments)
        $global:LASTEXITCODE = 0
        $global:podmanTestScpArguments = $Arguments
    }
    function ssh {
        param([Parameter(ValueFromRemainingArguments)][string[]]$Arguments)
        $global:LASTEXITCODE = 0
        $global:podmanTestSshArguments = $Arguments
        if ($Arguments[-1] -eq 'whoami') {
            if (-not $global:podmanTestkeyAccepted) { $global:LASTEXITCODE = 255; return }
            return $global:podmanTestremoteIdentity
        }
    }
    $dumpsBefore = $global:podmanTestdumpCount
    & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -OutputDirectory $testRoot
    $firstSentPackage = $global:podmanTestScpArguments[0]
    Assert-Test ($global:podmanTestdumpCount -eq $dumpsBefore + 1) 'Sending always generates a fresh database dump'
    Assert-Test ($firstSentPackage -ne $package) 'Sending does not reuse a previously generated package'
    & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -OutputDirectory $testRoot
    $lastSentPackage = $global:podmanTestScpArguments[0]
    Assert-Test ($global:podmanTestdumpCount -eq $dumpsBefore + 2 -and $lastSentPackage -ne $firstSentPackage) 'Every repeated send captures another snapshot'
    $remoteCode = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($global:podmanTestSshArguments[-1]))
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseInput($remoteCode, [ref]$tokens, [ref]$errors) | Out-Null
    Assert-Test ($errors.Count -eq 0) 'Generated remote PowerShell command has valid syntax'
    Assert-Test ($global:podmanTestScpArguments[-1].StartsWith('test-user@192.168.1.11:')) 'Transfer uses the requested Windows account and server'
    Assert-Test ($remoteCode.Contains((Get-FileHash -LiteralPath $lastSentPackage -Algorithm SHA256).Hash)) 'Remote transfer verifies the fresh package hash'
    Assert-Test ($global:podmanTestconnectionTarget -eq '192.168.1.11:22') 'Sending checks the SSH endpoint before preparing the package'
    $global:podmanTestsshReachable = $false
    $dumpsBefore = $global:podmanTestdumpCount
    $failed = $false
    try { & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -ServerAddress '192.0.2.10' -OutputDirectory $testRoot } catch {
        $failed = $_.Exception.Message.Contains('192.0.2.10:22') -and $_.Exception.Message.Contains('Get-Service sshd')
    }
    Assert-Test $failed 'Unreachable SSH reports the selected server and troubleshooting commands'
    Assert-Test ($global:podmanTestconnectionTarget -eq '192.0.2.10:22') 'Connectivity check respects the configured server address'
    Assert-Test ($global:podmanTestdumpCount -eq $dumpsBefore) 'Unreachable SSH stops before generating another database dump'
    Assert-Test ($global:podmanTestScpArguments[0] -eq $lastSentPackage) 'Unreachable SSH never triggers a file transfer'
    $global:podmanTestsshReachable = $true
    $global:podmanTestsourceRunning = $false
    $failed = $false
    try { & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -SourceContainer 'postgres-appeventos' -OutputDirectory $testRoot } catch { $failed = $true }
    Assert-Test $failed 'Sending refuses a stopped source database'
    Assert-Test ($global:podmanTestScpArguments[0] -eq $lastSentPackage) 'Source failure never triggers a transfer of an old package'
    $global:podmanTestsourceRunning = $true
    $testKey = Join-Path $testRoot 'test identity key'
    [IO.File]::WriteAllText($testKey, 'Simulated identity, not a real private key.')
    $dumpsBefore = $global:podmanTestdumpCount
    & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -SshKeyPath $testKey -OutputDirectory $testRoot
    $keyPackage = $global:podmanTestScpArguments[-2]
    Assert-Test ($global:podmanTestdumpCount -eq $dumpsBefore + 1) 'Accepted SSH key permits a fresh deployment package'
    Assert-Test ($global:podmanTestScpArguments[0] -eq '-i' -and $global:podmanTestScpArguments[1] -eq $testKey) 'SCP uses the chosen identity path including spaces'
    Assert-Test ($global:podmanTestSshArguments[0] -eq '-i' -and $global:podmanTestSshArguments[1] -eq $testKey) 'Remote installation uses the same SSH identity'
    Assert-Test ($global:podmanTestScpArguments -contains 'BatchMode=yes' -and $global:podmanTestSshArguments -contains 'PasswordAuthentication=no') 'Key-based deployment does not fall back to a Microsoft password'
    $dumpsBefore = $global:podmanTestdumpCount
    $global:podmanTestkeyAccepted = $false
    $failed = $false
    try { & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -SshKeyPath $testKey -OutputDirectory $testRoot } catch { $failed = $_.Exception.Message.Contains('autenticacao por chave falhou') }
    Assert-Test ($failed -and $global:podmanTestdumpCount -eq $dumpsBefore) 'Rejected key fails before generating a backup'
    Assert-Test ($global:podmanTestScpArguments[-2] -eq $keyPackage) 'Rejected key never starts file transfer'
    $global:podmanTestkeyAccepted = $true
    $global:podmanTestremoteIdentity = 'PC-TESTE\different-user'
    $failed = $false
    try { & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -SshKeyPath $testKey -OutputDirectory $testRoot } catch { $failed = $_.Exception.Message.Contains('identidade retornada') }
    Assert-Test ($failed -and $global:podmanTestdumpCount -eq $dumpsBefore) 'Unexpected remote user blocks the deployment'
    $failed = $false
    try { & (Join-Path $PSScriptRoot 'enviar.ps1') -WindowsUser 'test-user' -SshKeyPath (Join-Path $testRoot 'missing-key') -OutputDirectory $testRoot } catch { $failed = $_.Exception.Message.Contains('chave privada existente') }
    Assert-Test ($failed -and $global:podmanTestdumpCount -eq $dumpsBefore) 'Missing private key stops before any database dump'
    Write-Host 'All deployment workflow tests passed using simulated Podman commands.'
} finally { $env:LOCALAPPDATA = $originalLocalAppData }
