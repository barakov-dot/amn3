[CmdletBinding()]
param([string]$Approval = "")

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "5B55AA29FFCD3DAFC50DEA0D46B772D23FD48F66BBA1C356EB10D4AD9E80DE67"
$expectedExecutorBytes = 160075
$expectedNonce = "6153dac4843cd83610b9175dc7bb02ea8338328deda93ed155e4c18358562b71"
$expectedTransactionSha = "2454512ceee787d905707cbdff1865905cdf7fded30949e9ddf8399db27f5cb2"
$expectedCapsuleSha = "57653921943a6c4b0eb2c0b9b014cc8ad895d7cad78480ab014474fb98efa8cf"
$expectedLedgerSha = "494b3fac58ac79837c802163b03381e98540c11188f12f73064acb01dc0422fc"
$expectedRunnerSha = (
    Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256
).Hash.ToUpperInvariant()
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString(
            $hasher.ComputeHash(
                (New-Object Text.UTF8Encoding($false)).GetBytes($Value)
            )
        )).Replace("-", "")
    } finally {
        $hasher.Dispose()
    }
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (
        ($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1'
    ) + '"'
}

function Invoke-ExactSsh([string[]]$Arguments, [byte[]]$InputBytes) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument $_
    }) -join " ")
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
        $process.StandardInput.BaseStream.Write(
            $InputBytes, 0, $InputBytes.Length
        )
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
        "TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH",
        "EXPECTED_HOST_KEY_SHA256"
    )
    if (
        $values.Count -ne $expected.Count -or
        @(
            $expected |
                Where-Object { -not $values.ContainsKey($_) }
        ).Count -ne 0
    ) {
        throw "Private target binding key set invalid."
    }
    if (
        $values["TARGET_HOST"] -notmatch
            '^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$' -or
        $values["TARGET_HOST"].Contains("..")
    ) {
        throw "Private target host invalid."
    }
    if ($values["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "Private target user invalid."
    }
    if (
        $values["EXPECTED_HOST_KEY_SHA256"] -notmatch
            '^SHA256:[A-Za-z0-9+/=]+$'
    ) {
        throw "Private host pin invalid."
    }
    return $values
}

$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION 6153DA CURRENT TERMINAL READ ONLY AUDIT RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha LEDGER SHA256 $($expectedLedgerSha.ToUpperInvariant()) READ ONLY CURRENT AMN2 LEDGER SYSTEMD OWNED TREE INVENTORY NO FILE WRITE NO INSTALL NO CLEANUP NO AMN2 START NO FOREIGN SERVICE MUTATION NO USA DATA MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) {
    Write-Output $runnerApproval
    throw "Exact current terminal read only audit approval mismatch."
}

$privateRoot = Join-Path (
    [Environment]::GetFolderPath("LocalApplicationData")
) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"
$keyPath = Join-Path $privateRoot "id_ed25519_spain"
$knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if (
    $binding["SSH_KEY_PATH"] -cne $keyPath -or
    -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $sshExe -PathType Leaf)
) {
    throw "Private SSH material unavailable."
}

$transportOptions = @(
    "-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20",
    "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4",
    "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no",
    "-o", "KbdInteractiveAuthentication=no", "-o",
    "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o",
    "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o",
    "StrictHostKeyChecking=yes", "-o",
    "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath
)
$sshBase = @($transportOptions + @("-p", "22"))
$target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$executorPath = "/root/amn2-spain-phase12-executor.pyz"
$transactionPath = (
    "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"
)
$capsulePath = (
    "/var/lib/amn2-spain-phase12-audit/recovery-capsule-$expectedNonce.json"
)
$ledgerPath = (
    "/var/lib/amn2-spain-phase12-audit/mutation-ledger-$expectedNonce.json"
)
$bindingResult = Invoke-ExactSsh (
    @($sshBase + @(
        $target,
        "sha256sum $executorPath $transactionPath $capsulePath $ledgerPath && stat -c '%s' $executorPath && test ! -e /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"
    ))
) ([byte[]]@())
$bindingText = (
    New-Object Text.UTF8Encoding($false, $true)
).GetString($bindingResult.Stdout)
if (
    $bindingResult.ExitCode -ne 0 -or
    $bindingText -notmatch
        "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($executorPath))$" -or
    $bindingText -notmatch
        "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$" -or
    $bindingText -notmatch
        "(?im)^$($expectedCapsuleSha.ToLowerInvariant())  $([regex]::Escape($capsulePath))$" -or
    $bindingText -notmatch
        "(?im)^$($expectedLedgerSha.ToLowerInvariant())  $([regex]::Escape($ledgerPath))$" -or
    $bindingText -notmatch "(?m)^$expectedExecutorBytes$"
) {
    throw "Current audit checksum binding mismatch."
}

$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{
    approval_id = (Get-TextSha256 $Approval).ToLowerInvariant()
    approved_at_epoch = $now
    audit_authorized = $true
    capsule_sha256 = $expectedCapsuleSha
    executor_sha256 = $expectedExecutorSha.ToLowerInvariant()
    expires_at_epoch = $now + 300
    mutation_ledger_sha256 = $expectedLedgerSha
    nonce = $expectedNonce
    schema = "amn2.spain-current-terminal-recovery-audit-intent.v1"
    transaction_sha256 = $expectedTransactionSha
}
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(
    ($intent | ConvertTo-Json -Compress) + "`n"
)
$result = Invoke-ExactSsh (
    @($sshBase + @(
        $target,
        "/usr/bin/python3 -I -B $executorPath current-terminal-recovery-audit-bound"
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
if (
    $receipt["schema"] -cne
        "amn2.spain-current-terminal-recovery-audit-receipt.v1" -or
    $receipt["result"] -cne "passed" -or
    $receipt["nonce"] -cne $expectedNonce -or
    $receipt["transaction_sha256"] -cne $expectedTransactionSha -or
    $receipt["capsule_sha256"] -cne $expectedCapsuleSha -or
    $receipt["mutation_ledger_sha256"] -cne $expectedLedgerSha
) {
    throw "Current terminal read only audit receipt binding mismatch."
}
[Console]::WriteLine($resultText)
