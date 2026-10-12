#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ComputerName,
    [ValidateRange(1, 65535)][int]$Port = 22,
    [ValidateRange(1, 60000)][int]$TimeoutMilliseconds = 5000
)
# Test the actual socket without relying on ICMP or NetTCPIP diagnostics.
$client = New-Object Net.Sockets.TcpClient
try {
    $connection = $client.ConnectAsync($ComputerName, $Port)
    Write-Output ([bool]($connection.Wait($TimeoutMilliseconds) -and $client.Connected))
} catch {
    Write-Output $false
} finally {
    $client.Dispose()
}
