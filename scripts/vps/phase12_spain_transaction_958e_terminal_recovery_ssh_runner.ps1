[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "8196CDD272FCA5ADE5C1DBCEE036597926C6A003DC8D380985DE80EE45A41B67"
$expectedExecutorBytes = 153172
$expectedPriorExecutorSha = "E621C0CC23B89FB7109DDEFA665EF16B3F3A8105D31AE9B7589A102E9ED1E8D4"
$expectedPriorExecutorBytes = 153174
$expectedNonce = "958e91b682d226fc1f229b1bee2592dfe6340443fb768f3e2c9a9df45f6979b8"
$expectedTransactionSha = "b66e6540582fc328b89c559fda2b08263f27c56e28010aec81aff4eb28375810"
$expectedCapsuleSha = "0b4890a6b9786a13145879f604924cbe4162d8d6eb94716e0f1b0f76f8e02e0f"
$expectedDockerTreeSha = "642b64adf9cf3b5b8ec4d8f141e24603dc0723c6db544c94025d202b1aef588b"
$expectedDockerTreeEntries = 49
$expectedDockerTreeBytes = 262199
$uploadTimeoutMilliseconds = 60000
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$artifactRoot = Join-Path $repoRoot "private-artifacts\phase12-spain-transaction-958e-terminal-recovery-v1-20260725"
$executorPath = Join-Path $artifactRoot "executor-a.pyz"
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

function Invoke-BoundedSshUpload([string]$SourcePath, [string]$Destination) {
    if ($Destination -cne "/root/amn2-spain-phase12-terminal-958e-executor-a.pyz") {
        throw "Approved terminal recovery artifact destination invalid."
    }
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $remoteCommand = 'destination=' + $Destination + '; umask 077; cat > "$destination"'
    $info.Arguments = ((@($sshBase + @($target, $remoteCommand)) | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument $_
    }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $info
    if (-not $process.Start()) { throw "Approved terminal recovery executor upload did not start." }
    $input = $null; $timedOut = $false
    try {
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        $input = [IO.File]::Open($SourcePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $copyTask = $input.CopyToAsync($process.StandardInput.BaseStream)
        $deadline = [Diagnostics.Stopwatch]::StartNew()
        if (-not $copyTask.Wait($uploadTimeoutMilliseconds)) { $timedOut = $true; throw "Approved terminal recovery executor upload exceeded 60 seconds." }
        [void]$copyTask.GetAwaiter().GetResult(); $process.StandardInput.Close()
        $remaining = [Math]::Max(0, $uploadTimeoutMilliseconds - [int]$deadline.ElapsedMilliseconds)
        if (-not $process.WaitForExit($remaining)) { $timedOut = $true; throw "Approved terminal recovery executor upload exceeded 60 seconds." }
        [void][Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
        if ($process.ExitCode -ne 0) { throw "Approved terminal recovery executor upload failed." }
    } catch {
        if ($timedOut) { throw }
        throw "Approved terminal recovery executor upload failed."
    } finally {
        if (-not $process.HasExited) { try { $process.Kill($true) } catch { }; $process.WaitForExit() }
        if ($null -ne $input) { $input.Dispose() }
        $process.Dispose()
    }
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

foreach ($path in @($executorPath, $sshExe)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required local terminal recovery artifact is unavailable." }
}
if ((Get-Item -LiteralPath $executorPath).Length -ne $expectedExecutorBytes -or (Get-FileHash -LiteralPath $executorPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedExecutorSha) { throw "Terminal recovery executor checksum/size mismatch." }
$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"; $keyPath = Join-Path $privateRoot "id_ed25519_spain"; $knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }
$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION 958E91 TERMINAL RECOVERY RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes PRIOR EXECUTOR SHA256 $expectedPriorExecutorSha PRIOR EXECUTOR BYTES $expectedPriorExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha DOCKER TREE SHA256 $expectedDockerTreeSha ENTRIES $expectedDockerTreeEntries BYTES $expectedDockerTreeBytes ROOT MODE 0710 SINGLE FILESYSTEM NO NESTED MOUNTS ROLLBACK EXACT OWNED CURRENT TRANSACTION VERIFY FOREIGN EQUALITY NO AMN2 START NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact transaction 958E91 terminal recovery approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath)
$sshBase = @($transportOptions + @("-p", "22")); $target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteExecutorPath = "/root/amn2-spain-phase12-executor.pyz"
$remoteExecutor = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"))) ([byte[]]@())
$remoteExecutorText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteExecutor.Stdout)
$remoteHasPriorExecutor = $remoteExecutor.ExitCode -eq 0 -and $remoteExecutorText -match "(?im)^$($expectedPriorExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and $remoteExecutorText -match "(?m)^$expectedPriorExecutorBytes$"
$remoteHasCurrentExecutor = $remoteExecutor.ExitCode -eq 0 -and $remoteExecutorText -match "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and $remoteExecutorText -match "(?m)^$expectedExecutorBytes$"
if (-not ($remoteHasPriorExecutor -or $remoteHasCurrentExecutor)) { throw "Remote transaction 958E91 terminal recovery executor precondition mismatch." }
if (-not $remoteHasCurrentExecutor) {
    $stagingPath = "/root/amn2-spain-phase12-terminal-958e-executor-a.pyz"
    Invoke-BoundedSshUpload $executorPath $stagingPath
    $uploaded = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $stagingPath && stat -c '%s' $stagingPath"))) ([byte[]]@())
    $uploadedText = (New-Object Text.UTF8Encoding($false,$true)).GetString($uploaded.Stdout)
    if ($uploaded.ExitCode -ne 0 -or $uploadedText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($stagingPath))$" -or $uploadedText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote transaction 958E91 terminal recovery uploaded executor mismatch." }
    $activation = Invoke-ExactSsh (@($sshBase + @($target, "mv -f $stagingPath $remoteExecutorPath && chmod 0644 $remoteExecutorPath && sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"))) ([byte[]]@())
    $activationText = (New-Object Text.UTF8Encoding($false,$true)).GetString($activation.Stdout)
    if ($activation.ExitCode -ne 0 -or $activationText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -or $activationText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote transaction 958E91 terminal recovery executor activation mismatch." }
}
$transactionPath = "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"
$capsulePath = "/var/lib/amn2-spain-phase12-audit/recovery-capsule-$expectedNonce.json"
$precondition = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $transactionPath $capsulePath && test ! -e /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"))) ([byte[]]@())
$preconditionText = (New-Object Text.UTF8Encoding($false,$true)).GetString($precondition.Stdout)
if ($precondition.ExitCode -ne 0 -or $preconditionText -notmatch "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$" -or $preconditionText -notmatch "(?im)^$($expectedCapsuleSha.ToLowerInvariant())  $([regex]::Escape($capsulePath))$") { throw "Transaction 958E91 terminal recovery precondition checksum mismatch." }
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; capsule_sha256=$expectedCapsuleSha; docker_tree_entry_count=$expectedDockerTreeEntries; docker_tree_sha256=$expectedDockerTreeSha; docker_tree_total_bytes=$expectedDockerTreeBytes; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now + 300); mutation_authorized=$true; nonce=$expectedNonce; schema="amn2.spain-terminal-recovery-intent.v1"; transaction_sha256=$expectedTransactionSha }
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$result = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B $remoteExecutorPath terminal-recovery-bound"))) $intentBytes
if ($result.ExitCode -ne 0) {
    $safeRemoteError = (New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stderr).Trim()
    if (-not [string]::IsNullOrWhiteSpace($safeRemoteError)) { [Console]::Error.WriteLine($safeRemoteError) }
    throw "Transaction 958E91 terminal recovery failed; current transaction remains fail-closed."
}
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stdout))
