param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight", "cleanup")]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$Approval
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedRemoteScriptSha = "8CF3DBF6ECF261B11852133D112A343FFB2EB8735B0AFD87938A940453D9DBD7"
$expectedApproval = "APPROVE PHASE11_TELEGRAM_002B_STALE_START_CLEANUP_REMOTE_SHA_8CF3DBF6ECF261B11852133D112A343FFB2EB8735B0AFD87938A940453D9DBD7_0B858C5_EXACT_ONE_PRIVATE_FIRST_ADMIN_START_ACK_ONLY_NO_RESPONSE_DB_WEB_PROFILE_AND_AWG_UNTOUCHED"

if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact live cleanup approval mismatch"
}

$trustedOpenSshDir = Join-Path $env:WINDIR "System32\OpenSSH"
$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "amn2_private_rc_operator_ed25519"
$knownHostsPath = Join-Path $sshDir "codex_amn2_target_known_hosts"
$remoteScript = Join-Path $PSScriptRoot "phase11_telegram_002b_stale_start_cleanup_remote.sh"

foreach ($required in @($sshExecutable, $keyPath, $knownHostsPath, $remoteScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required local input missing"
    }
}

$resolvedTrustedDir = [IO.Path]::GetFullPath($trustedOpenSshDir).TrimEnd("\")
$resolvedSshExecutable = (Resolve-Path -LiteralPath $sshExecutable).Path
if (-not [string]::Equals(
    [IO.Path]::GetDirectoryName($resolvedSshExecutable),
    $resolvedTrustedDir,
    [StringComparison]::OrdinalIgnoreCase
)) {
    throw "Trusted OpenSSH path resolution mismatch"
}

$knownHostLines = @(
    Get-Content -LiteralPath $knownHostsPath |
        Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") }
)
if ($knownHostLines.Count -ne 1) {
    throw "Known-host binding must contain exactly one target"
}
$target = ($knownHostLines[0] -split "\s+", 2)[0]
if (-not $target -or $target.Contains(",")) {
    throw "Known-host target could not be resolved unambiguously"
}

function Invoke-CapturedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [byte[]]$StandardInputBytes = @()
    )

    if (-not [IO.Path]::IsPathFullyQualified($FileName)) {
        throw "Executable path must be absolute"
    }
    if (-not [string]::Equals(
        $FileName,
        $sshExecutable,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Executable path is outside the trusted OpenSSH installation"
    }

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FileName
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.RedirectStandardInput = $true
    foreach ($argument in $Arguments) {
        [void]$startInfo.ArgumentList.Add($argument)
    }

    $process = [System.Diagnostics.Process]::Start($startInfo)
    try {
        if ($StandardInputBytes.Length -gt 0) {
            $process.StandardInput.BaseStream.Write(
                $StandardInputBytes,
                0,
                $StandardInputBytes.Length
            )
            $process.StandardInput.BaseStream.Flush()
        }
        $process.StandardInput.Close()
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()

        $safeOutput = (($stdout + $stderr) -replace [regex]::Escape($target), "<target>")
        if ($safeOutput.Trim()) {
            Write-Output $safeOutput.TrimEnd()
        }
        if ($process.ExitCode -ne 0) {
            throw "Remote process failed with exit code $($process.ExitCode)"
        }
    } finally {
        $process.Dispose()
    }
}

$remoteScriptBytes = [IO.File]::ReadAllBytes($remoteScript)
$sha256 = [Security.Cryptography.SHA256]::Create()
try {
    $actualRemoteScriptSha = (
        [BitConverter]::ToString($sha256.ComputeHash($remoteScriptBytes))
    ).Replace("-", "")
} finally {
    $sha256.Dispose()
}
if (-not [string]::Equals(
    $actualRemoteScriptSha,
    $expectedRemoteScriptSha,
    [StringComparison]::Ordinal
)) {
    throw "Remote cleanup script SHA-256 mismatch"
}

$commonOptions = @(
    "-F", "none",
    "-i", $keyPath,
    "-o", "BatchMode=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "GlobalKnownHostsFile=none",
    "-o", "KnownHostsCommand=none",
    "-o", "UserKnownHostsFile=$knownHostsPath",
    "-o", "ConnectTimeout=15",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=4"
)
$sshArguments = @($commonOptions) + @(
    "root@$target",
    "bash", "-s", "--", $Mode
)

if ($Mode -eq "cleanup") {
    $approvalStateDir = Join-Path $env:LOCALAPPDATA "AMN2\phase11"
    $approvalReceipt = Join-Path $approvalStateDir (
        "telegram-002b-stale-start-" +
        $expectedRemoteScriptSha +
        ".cleanup-consumed"
    )
    New-Item -ItemType Directory -Force -Path $approvalStateDir | Out-Null
    $receiptStream = $null
    try {
        $receiptStream = [IO.File]::Open(
            $approvalReceipt,
            [IO.FileMode]::CreateNew,
            [IO.FileAccess]::Write,
            [IO.FileShare]::None
        )
        $receiptBytes = [Text.Encoding]::UTF8.GetBytes(
            "mode=cleanup`nremote_sha=$expectedRemoteScriptSha`n"
        )
        $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
        $receiptStream.Flush()
    } catch {
        throw "Cleanup approval already consumed or receipt unavailable"
    } finally {
        if ($null -ne $receiptStream) {
            $receiptStream.Dispose()
        }
    }
}

Invoke-CapturedProcess -FileName $sshExecutable -Arguments $sshArguments -StandardInputBytes $remoteScriptBytes
