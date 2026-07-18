param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("fingerprint", "preflight", "apply")]
    [string]$Mode,
    [string]$TargetFingerprint = "",
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedRemoteScriptSha = "F533CF7EFCB49EE494CE1E75B80F4CCC6EA6C06D2DB46D72669AC6FC23BA623F"
$approvalPrefix = (
    "APPROVE POST_RELEASE_TELEGRAM_GROUP_ICON_001_REMOTE_SHA_" +
    $expectedRemoteScriptSha +
    "_SOURCE_0B858C5_TARGET_SHA256_"
)
$approvalSuffix = (
    "_EXACT_GROUP_PHOTO_SINGLE_SETCHATPHOTO_POSTFLIGHT_OR_ROLLBACK_" +
    "NO_MESSAGES_BOT_DB_WEB_AND_AWG_UNTOUCHED"
)

if ($Mode -eq "fingerprint") {
    if ($Approval -or $TargetFingerprint) {
        throw "Fingerprint mode does not accept approval or target fingerprint"
    }
} else {
    if ($TargetFingerprint -notmatch "^[A-F0-9]{64}$") {
        throw "Target fingerprint required"
    }
    $expectedApproval = $approvalPrefix + $TargetFingerprint + $approvalSuffix
    if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
        throw "Exact live approval mismatch"
    }
}

$trustedOpenSshDir = Join-Path $env:WINDIR "System32\OpenSSH"
$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "amn2_private_rc_operator_ed25519"
$knownHostsPath = Join-Path $sshDir "codex_amn2_target_known_hosts"
$remoteScript = Join-Path $PSScriptRoot "post_release_telegram_group_icon_001_remote.sh"

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
    throw "Remote group icon script SHA-256 mismatch"
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
if ($Mode -ne "fingerprint") {
    $sshArguments += @($TargetFingerprint)
}

if ($Mode -eq "apply") {
    $approvalStateDir = Join-Path $env:LOCALAPPDATA "AMN2\post-release"
    $approvalReceipt = Join-Path $approvalStateDir (
        "telegram-group-icon-001-" +
        $expectedRemoteScriptSha +
        "-" +
        $TargetFingerprint +
        ".apply-consumed"
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
            "mode=apply`nremote_sha=$expectedRemoteScriptSha`n" +
            "target_fingerprint=$TargetFingerprint`n"
        )
        $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
        $receiptStream.Flush()
    } catch {
        throw "Apply approval already consumed or receipt unavailable"
    } finally {
        if ($null -ne $receiptStream) {
            $receiptStream.Dispose()
        }
    }
}

Invoke-CapturedProcess `
    -FileName $sshExecutable `
    -Arguments $sshArguments `
    -StandardInputBytes $remoteScriptBytes
