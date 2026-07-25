[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "4D110B0DC169BE38A65B16A89DD8A9B54AEB5840117E5F4B443CC4538939D4DC"
$expectedExecutorBytes = 147586
$expectedNonce = "52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246"
$expectedTransactionSha = "7beec673258de6b4b68206f8013ab8cc9c8d1fb488e38e39340baa1c571d6e1c"
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($Value)))).Replace("-", "") } finally { $hasher.Dispose() }
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-ExactSsh([string[]]$Arguments, [byte[]]$InputBytes) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $info.UseShellExecute = $false
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $info
    if (-not $process.Start()) { throw "SSH process did not start." }
    try {
        $stdout = [IO.MemoryStream]::new(); $stderr = [IO.MemoryStream]::new()
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length)
        $process.StandardInput.BaseStream.Flush(); $process.StandardInput.Close()
        try {
            $process.WaitForExit(); [Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
            return [pscustomobject]@{ ExitCode=$process.ExitCode; Stdout=$stdout.ToArray(); Stderr=$stderr.ToArray() }
        } finally { $stdout.Dispose(); $stderr.Dispose() }
    } finally { $process.Dispose() }
}

function Read-PrivateBinding([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Private target binding unavailable." }
    $values = @{}
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        if ($line -notmatch '^([A-Z0-9_]+)=([^\r\n]+)$') { throw "Private target binding format invalid." }
        if ($values.ContainsKey($Matches[1])) { throw "Private target binding duplicate key." }
        $values[$Matches[1]] = $Matches[2]
    }
    $expected = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($values.Count -ne $expected.Count -or @($expected | Where-Object { -not $values.ContainsKey($_) }).Count -ne 0) { throw "Private target binding key set invalid." }
    if ($values["TARGET_HOST"] -notmatch '^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$' -or $values["TARGET_HOST"].Contains("..")) { throw "Private target host invalid." }
    if ($values["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$') { throw "Private target user invalid." }
    if ($values["EXPECTED_HOST_KEY_SHA256"] -notmatch '^SHA256:[A-Za-z0-9+/=]+$') { throw "Private host pin invalid." }
    return $values
}

if (-not (Test-Path -LiteralPath $sshExe -PathType Leaf)) { throw "Required local SSH executable is unavailable." }
$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"; $keyPath = Join-Path $privateRoot "id_ed25519_spain"; $knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }
$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION 52FAB7 MANUAL RECOVERY CLEANUP RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha REMOVE ONLY VERIFIED RETAINED PACKAGE TREE /opt/amn2-spain-package PRESERVE TERMINAL LEDGER NO AMN2 START NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact transaction 52FAB7 manual cleanup approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath)
$sshBase = @($transportOptions + @("-p", "22")); $target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteExecutorPath = "/root/amn2-spain-phase12-executor.pyz"
$remoteExecutor = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"))) ([byte[]]@())
$remoteExecutorText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteExecutor.Stdout)
if ($remoteExecutor.ExitCode -ne 0 -or $remoteExecutorText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -or $remoteExecutorText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote transaction 52FAB7 manual cleanup executor checksum/size mismatch." }
$transactionPath = "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"
$precondition = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $transactionPath && test -d /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"))) ([byte[]]@())
$preconditionText = (New-Object Text.UTF8Encoding($false,$true)).GetString($precondition.Stdout)
if ($precondition.ExitCode -ne 0 -or $preconditionText -notmatch "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$") { throw "Transaction 52FAB7 manual cleanup precondition checksum mismatch." }
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now + 300); mutation_authorized=$true; nonce=$expectedNonce; schema="amn2.spain-manual-cleanup-intent.v1" }
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$result = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B $remoteExecutorPath manual-cleanup-bound"))) $intentBytes
if ($result.ExitCode -ne 0) {
    $safeRemoteError = (New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stderr).Trim()
    if (-not [string]::IsNullOrWhiteSpace($safeRemoteError)) { [Console]::Error.WriteLine($safeRemoteError) }
    throw "Transaction 52FAB7 manual cleanup failed; retained package tree was not accepted as safely removable."
}
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stdout))
