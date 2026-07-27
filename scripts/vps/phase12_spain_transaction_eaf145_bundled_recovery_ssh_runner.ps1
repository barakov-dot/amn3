[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "D8E51499A4F5CF5CFDE59DF056FF0BFB074B0E251C4AD474F6AED2DE5642F072"
$expectedExecutorBytes = 155830
$expectedNonce = "eaf145ae2372c2dc1ce9e84ec4f0e30c4c29490b1a20bb137cd812a2b7dd355b"
$expectedTransactionSha = "88ca0dfc1c2ab0af972e965b515deb01f5d9fc47166985715eb4fa76284e7693"
$expectedCapsuleSha = "5e10f9fad1ef7c19048743297f4362249cc034e9914b84bead3004fddedab3fb"
$expectedDockerTreeSha = "7e74d39018511064ae9fffaf52016c0e34504142f7105b3388b590a0a22d542e"
$expectedDockerTreeEntries = 51
$expectedDockerTreeBytes = 360503
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
$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION EAF145 BUNDLED RECOVERY RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha DOCKER TREE SHA256 $expectedDockerTreeSha ENTRIES $expectedDockerTreeEntries BYTES $expectedDockerTreeBytes REMOVE ONLY VERIFIED RETAINED PACKAGE TREE /opt/amn2-spain-package THEN ROLLBACK EXACT OWNED CURRENT TRANSACTION VERIFY FOREIGN EQUALITY NO AMN2 START NO FOREIGN SERVICE MUTATION NO USA DATA MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact transaction EAF145 bundled recovery approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath)
$sshBase = @($transportOptions + @("-p", "22")); $target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteHash = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum /root/amn2-spain-phase12-executor.pyz && stat -c '%s' /root/amn2-spain-phase12-executor.pyz"))) ([byte[]]@())
$remoteText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteHash.Stdout)
if ($remoteHash.ExitCode -ne 0 -or $remoteText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  /root/amn2-spain-phase12-executor\.pyz$" -or $remoteText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote EAF145 bundled recovery executor checksum mismatch." }
$transactionPath = "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"
$capsulePath = "/var/lib/amn2-spain-phase12-audit/recovery-capsule-$expectedNonce.json"
$remoteTransaction = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $transactionPath $capsulePath && test -d /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"))) ([byte[]]@())
$remoteTransactionText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteTransaction.Stdout)
if ($remoteTransaction.ExitCode -ne 0 -or $remoteTransactionText -notmatch "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$" -or $remoteTransactionText -notmatch "(?im)^$($expectedCapsuleSha.ToLowerInvariant())  $([regex]::Escape($capsulePath))$") { throw "EAF145 bundled recovery transaction checksum mismatch." }
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now + 300); mutation_authorized=$true; nonce=$expectedNonce; schema="amn2.spain-manual-cleanup-intent.v1" }
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$cleanupResult = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B /root/amn2-spain-phase12-executor.pyz manual-cleanup-bound"))) $intentBytes
if ($cleanupResult.ExitCode -ne 0) {
    $safeRemoteError = (New-Object Text.UTF8Encoding($false,$true)).GetString($cleanupResult.Stderr).Trim()
    if (-not [string]::IsNullOrWhiteSpace($safeRemoteError)) { [Console]::Error.WriteLine($safeRemoteError) }
    throw "EAF145 manual cleanup failed; retained package tree was not accepted as safely removable."
}
$packageAbsent = Invoke-ExactSsh (@($sshBase + @($target, "test ! -e /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"))) ([byte[]]@())
if ($packageAbsent.ExitCode -ne 0) { throw "EAF145 manual cleanup package absence verification failed." }
$terminalIntent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; capsule_sha256=$expectedCapsuleSha; docker_tree_entry_count=$expectedDockerTreeEntries; docker_tree_sha256=$expectedDockerTreeSha; docker_tree_total_bytes=$expectedDockerTreeBytes; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now + 300); mutation_authorized=$true; nonce=$expectedNonce; schema="amn2.spain-terminal-recovery-intent.v1"; transaction_sha256=$expectedTransactionSha }
$terminalIntentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($terminalIntent | ConvertTo-Json -Compress) + "`n")
$terminalResult = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B /root/amn2-spain-phase12-executor.pyz terminal-recovery-bound"))) $terminalIntentBytes
if ($terminalResult.ExitCode -ne 0) {
    $safeRemoteError = (New-Object Text.UTF8Encoding($false,$true)).GetString($terminalResult.Stderr).Trim()
    if (-not [string]::IsNullOrWhiteSpace($safeRemoteError)) { [Console]::Error.WriteLine($safeRemoteError) }
    throw "Transaction EAF145 terminal recovery failed; current transaction remains fail-closed."
}
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($cleanupResult.Stdout))
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($terminalResult.Stdout))
