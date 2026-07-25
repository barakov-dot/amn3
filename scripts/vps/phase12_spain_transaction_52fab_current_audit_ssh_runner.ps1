[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "AA4602CF011790EBDB3DC8C4D815361FA683E2B378958620BC9BEE9D02D9821A"
$expectedExecutorBytes = 149242
$expectedPriorExecutorSha = "84BB2D4BB04E375351823AEBD22D5A1D23745BA4389EEAA6970B3AC0226B1DE9"
$expectedPriorExecutorBytes = 149069
$expectedNonce = "52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246"
$expectedTransactionSha = "7beec673258de6b4b68206f8013ab8cc9c8d1fb488e38e39340baa1c571d6e1c"
$expectedCapsuleSha = "eb6b3ee6864504f724f7ac7d8839983bdec717c576871cadc7c98b95337cf088"
$expectedLedgerSha = "0ee87dfa762739457eafa5d6c8c81168f99da745b6ddd0f30bc60388f7e660c9"
$uploadTimeoutMilliseconds = 60000
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$artifactRoot = Join-Path $repoRoot "private-artifacts\phase12-spain-current-terminal-audit-v2-52fab7-20260725"
$executorPath = Join-Path $artifactRoot "executor-a.pyz"
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString(
            $hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($Value))
        )).Replace("-", "")
    } finally {
        $hasher.Dispose()
    }
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-ExactSsh([string[]]$Arguments, [byte[]]$InputBytes) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument $_
    }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "SSH process did not start." }
    try {
        $stdout = [IO.MemoryStream]::new()
        $stderr = [IO.MemoryStream]::new()
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length)
        $process.StandardInput.BaseStream.Flush()
        $process.StandardInput.Close()
        try {
            $process.WaitForExit()
            [Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
            return [pscustomobject]@{
                ExitCode = $process.ExitCode
                Stdout = $stdout.ToArray()
                Stderr = $stderr.ToArray()
            }
        } finally {
            $stdout.Dispose()
            $stderr.Dispose()
        }
    } finally {
        $process.Dispose()
    }
}

function Invoke-BoundedSshUpload([string]$SourcePath, [string]$Destination) {
    if ($Destination -cne "/root/amn2-spain-phase12-current-audit-executor-a.pyz") {
        throw "Approved current audit artifact destination invalid."
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
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "Approved current audit executor upload did not start." }
    $input = $null
    $timedOut = $false
    try {
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        $input = [IO.File]::Open(
            $SourcePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read
        )
        $copyTask = $input.CopyToAsync($process.StandardInput.BaseStream)
        $deadline = [Diagnostics.Stopwatch]::StartNew()
        if (-not $copyTask.Wait($uploadTimeoutMilliseconds)) {
            $timedOut = $true
            throw "Approved current audit executor upload exceeded 60 seconds."
        }
        [void]$copyTask.GetAwaiter().GetResult()
        $process.StandardInput.Close()
        $remaining = [Math]::Max(
            0, $uploadTimeoutMilliseconds - [int]$deadline.ElapsedMilliseconds
        )
        if (-not $process.WaitForExit($remaining)) {
            $timedOut = $true
            throw "Approved current audit executor upload exceeded 60 seconds."
        }
        [void][Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
        if ($process.ExitCode -ne 0) { throw "Approved current audit executor upload failed." }
    } catch {
        if ($timedOut) { throw }
        throw "Approved current audit executor upload failed."
    } finally {
        if (-not $process.HasExited) {
            try { $process.Kill($true) } catch { }
            $process.WaitForExit()
        }
        if ($null -ne $input) { $input.Dispose() }
        $process.Dispose()
    }
}

function Read-PrivateBinding([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Private target binding unavailable."
    }
    $values = @{}
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        if ($line -notmatch '^([A-Z0-9_]+)=([^\r\n]+)$') {
            throw "Private target binding format invalid."
        }
        if ($values.ContainsKey($Matches[1])) {
            throw "Private target binding duplicate key."
        }
        $values[$Matches[1]] = $Matches[2]
    }
    $expected = @(
        "TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256"
    )
    if (
        $values.Count -ne $expected.Count -or
        @($expected | Where-Object { -not $values.ContainsKey($_) }).Count -ne 0
    ) {
        throw "Private target binding key set invalid."
    }
    if (
        $values["TARGET_HOST"] -notmatch '^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$' -or
        $values["TARGET_HOST"].Contains("..")
    ) {
        throw "Private target host invalid."
    }
    if ($values["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "Private target user invalid."
    }
    if ($values["EXPECTED_HOST_KEY_SHA256"] -notmatch '^SHA256:[A-Za-z0-9+/=]+$') {
        throw "Private host pin invalid."
    }
    return $values
}

foreach ($path in @($executorPath, $sshExe)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required local current audit artifact is unavailable."
    }
}
if (
    (Get-Item -LiteralPath $executorPath).Length -ne $expectedExecutorBytes -or
    (Get-FileHash -LiteralPath $executorPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne
        $expectedExecutorSha
) {
    throw "Current audit executor checksum/size mismatch."
}

$privateRoot = Join-Path (
    [Environment]::GetFolderPath('LocalApplicationData')
) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"
$keyPath = Join-Path $privateRoot "id_ed25519_spain"
$knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if (
    $binding["SSH_KEY_PATH"] -cne $keyPath -or
    -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)
) {
    throw "Private SSH material unavailable."
}

$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION 52FAB7 CURRENT TERMINAL READ ONLY AUDIT RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes PRIOR EXECUTOR SHA256 $expectedPriorExecutorSha PRIOR EXECUTOR BYTES $expectedPriorExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha LEDGER SHA256 $($expectedLedgerSha.ToUpperInvariant()) READ ONLY CURRENT AMN2 LEDGER SYSTEMD OWNED TREE INVENTORY NO INSTALL NO CLEANUP NO AMN2 START NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) {
    Write-Output $runnerApproval
    throw "Exact current terminal read only audit approval mismatch."
}

$transportOptions = @(
    "-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20",
    "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4",
    "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no",
    "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no",
    "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes",
    "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath
)
$sshBase = @($transportOptions + @("-p", "22"))
$target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteExecutorPath = "/root/amn2-spain-phase12-executor.pyz"
$remoteExecutorState = Invoke-ExactSsh (
    @($sshBase + @(
        $target,
        "sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"
    ))
) ([byte[]]@())
$remoteExecutorText = (
    New-Object Text.UTF8Encoding($false, $true)
).GetString($remoteExecutorState.Stdout)
$remoteHasPriorExecutor = (
    $remoteExecutorState.ExitCode -eq 0 -and
    $remoteExecutorText -match
        "(?im)^$($expectedPriorExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and
    $remoteExecutorText -match "(?m)^$expectedPriorExecutorBytes$"
)
$remoteHasCurrentExecutor = (
    $remoteExecutorState.ExitCode -eq 0 -and
    $remoteExecutorText -match
        "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and
    $remoteExecutorText -match "(?m)^$expectedExecutorBytes$"
)
if (-not ($remoteHasPriorExecutor -or $remoteHasCurrentExecutor)) {
    throw "Remote executor checksum/size precondition mismatch."
}

$transactionPath = "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"
$capsulePath = "/var/lib/amn2-spain-phase12-audit/recovery-capsule-$expectedNonce.json"
$ledgerPath = "/var/lib/amn2-spain-phase12-audit/mutation-ledger-$expectedNonce.json"
$bindingResult = Invoke-ExactSsh (
    @($sshBase + @(
        $target,
        "sha256sum $transactionPath $capsulePath $ledgerPath && test ! -e /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"
    ))
) ([byte[]]@())
$bindingText = (
    New-Object Text.UTF8Encoding($false, $true)
).GetString($bindingResult.Stdout)
if (
    $bindingResult.ExitCode -ne 0 -or
    $bindingText -notmatch
        "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$" -or
    $bindingText -notmatch
        "(?im)^$($expectedCapsuleSha.ToLowerInvariant())  $([regex]::Escape($capsulePath))$" -or
    $bindingText -notmatch
        "(?im)^$($expectedLedgerSha.ToLowerInvariant())  $([regex]::Escape($ledgerPath))$"
) {
    throw "Current audit transaction/capsule/ledger binding mismatch."
}

if (-not $remoteHasCurrentExecutor) {
    $stagingPath = "/root/amn2-spain-phase12-current-audit-executor-a.pyz"
    Invoke-BoundedSshUpload $executorPath $stagingPath
    $uploaded = Invoke-ExactSsh (
        @($sshBase + @(
            $target,
            "sha256sum $stagingPath && stat -c '%s' $stagingPath"
        ))
    ) ([byte[]]@())
    $uploadedText = (
        New-Object Text.UTF8Encoding($false, $true)
    ).GetString($uploaded.Stdout)
    if (
        $uploaded.ExitCode -ne 0 -or
        $uploadedText -notmatch
            "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($stagingPath))$" -or
        $uploadedText -notmatch "(?m)^$expectedExecutorBytes$"
    ) {
        throw "Remote current audit executor checksum mismatch."
    }
    $activation = Invoke-ExactSsh (
        @($sshBase + @(
            $target,
            "mv -f $stagingPath $remoteExecutorPath && chmod 0644 $remoteExecutorPath && sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"
        ))
    ) ([byte[]]@())
    $activationText = (
        New-Object Text.UTF8Encoding($false, $true)
    ).GetString($activation.Stdout)
    if (
        $activation.ExitCode -ne 0 -or
        $activationText -notmatch
            "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -or
        $activationText -notmatch "(?m)^$expectedExecutorBytes$"
    ) {
        throw "Remote current audit executor activation mismatch."
    }
}

$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{
    approval_id = (Get-TextSha256 $Approval).ToLowerInvariant()
    approved_at_epoch = $now
    audit_authorized = $true
    capsule_sha256 = $expectedCapsuleSha
    executor_sha256 = $expectedExecutorSha.ToLowerInvariant()
    expires_at_epoch = ($now + 300)
    mutation_ledger_sha256 = $expectedLedgerSha
    nonce = $expectedNonce
    schema = "amn2.spain-current-terminal-recovery-audit-intent.v1"
    transaction_sha256 = $expectedTransactionSha
}
$intentBytes = (
    New-Object Text.UTF8Encoding($false)
).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$result = Invoke-ExactSsh (
    @($sshBase + @(
        $target,
        "/usr/bin/python3 -I -B $remoteExecutorPath current-terminal-recovery-audit-bound"
    ))
) $intentBytes
if ($result.ExitCode -ne 0) {
    $safeRemoteError = (
        New-Object Text.UTF8Encoding($false, $true)
    ).GetString($result.Stderr).Trim()
    if ($safeRemoteError -match '^[a-z0-9_ ]{1,160}$') {
        [Console]::Error.WriteLine($safeRemoteError)
    }
    throw "Current terminal read only audit failed."
}
$resultText = (
    New-Object Text.UTF8Encoding($false, $true)
).GetString($result.Stdout).Trim()
try {
    $receipt = $resultText | ConvertFrom-Json -AsHashtable
} catch {
    throw "Current terminal read only audit receipt JSON invalid."
}
$inventoryKeys = @($receipt["owned_tree_inventories"].Keys | Sort-Object)
$expectedInventoryKeys = @("etc", "opt", "var")
$inventoryKeysEqual = (
    $inventoryKeys.Count -eq $expectedInventoryKeys.Count -and
    @(Compare-Object -ReferenceObject $expectedInventoryKeys -DifferenceObject $inventoryKeys).Count -eq 0
)
if (
    $receipt["schema"] -cne
        "amn2.spain-current-terminal-recovery-audit-receipt.v1" -or
    $receipt["result"] -cne "passed" -or
    $receipt["nonce"] -cne $expectedNonce -or
    $receipt["transaction_sha256"] -cne $expectedTransactionSha -or
    $receipt["capsule_sha256"] -cne $expectedCapsuleSha -or
    $receipt["mutation_ledger_sha256"] -cne $expectedLedgerSha -or
    @($receipt["committed_owned_objects"]).Count -eq 0 -or
    @($receipt["removed_owned_objects"]).Count -eq 0 -or
    -not $inventoryKeysEqual
) {
    throw "Current terminal read only audit receipt binding mismatch."
}
[Console]::WriteLine($resultText)
