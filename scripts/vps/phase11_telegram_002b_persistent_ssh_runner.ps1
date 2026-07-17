param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight", "stage", "accept", "postflight")]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$Approval,
    [string]$RunId = "",
    [string]$Confirmation = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedRemoteScriptSha = "FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F"
$expectedApproval = "APPROVE PHASE11_TELEGRAM_002B_REMOTE_ORCHESTRATOR_SHA_FA3F979E3D2DEEB0EF2F53E97A79ECECCADCA6F853C8587A9973D192C49CEB3F_0B858C5_EXACT_UNIT_ENV_TELEGRAM_PREFLIGHT_DISABLED_FIRST_STAGE_FIRST_CONFIGURED_ADMIN_SINGLE_START_WIDE_HEADER_EXACT_CONFIRM_ACCEPT_ENABLE_POSTFLIGHT_AUTOROLLBACK240_NO_BLIND_DB_RESTORE_WEB_UNTOUCHED_AND_AWG_UNTOUCHED"
$expectedConfirmation = "CONFIRM PHASE11_TELEGRAM_002B_FIRST_ADMIN_WIDE_HEADER_RESPONSE"

if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact live approval mismatch"
}

if ($Mode -eq "accept") {
    if ($RunId -notmatch "^[0-9]{8}T[0-9]{6}Z$") {
        throw "Safe run id required"
    }
    if (-not [string]::Equals(
        $Confirmation,
        $expectedConfirmation,
        [StringComparison]::Ordinal
    )) {
        throw "Exact acceptance confirmation mismatch"
    }
} elseif ($RunId -or $Confirmation) {
    throw "Run id and confirmation are accept-only"
}

$approvalStateDir = Join-Path $env:LOCALAPPDATA "AMN2\phase11"
$approvalReceipt = Join-Path $approvalStateDir (
    "telegram-002b-" + $expectedRemoteScriptSha + ".stage-consumed"
)
if ($Mode -eq "stage") {
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
            "mode=stage`nremote_sha=$expectedRemoteScriptSha`n"
        )
        $receiptStream.Write($receiptBytes, 0, $receiptBytes.Length)
        $receiptStream.Flush()
    } catch {
        throw "Approval already consumed or receipt unavailable"
    } finally {
        if ($null -ne $receiptStream) {
            $receiptStream.Dispose()
        }
    }
} elseif ($Mode -eq "accept") {
    if (-not (Test-Path -LiteralPath $approvalReceipt -PathType Leaf)) {
        throw "Stage approval receipt missing"
    }
}

$trustedOpenSshDir = Join-Path $env:WINDIR "System32\OpenSSH"
$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "amn2_private_rc_operator_ed25519"
$knownHostsPath = Join-Path $sshDir "codex_amn2_target_known_hosts"
$remoteScript = Join-Path $PSScriptRoot "phase11_telegram_002b_persistent_remote.sh"

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
    throw "Remote activation script SHA-256 mismatch"
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
if ($Mode -eq "accept") {
    $confirmationToken = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes($Confirmation)
    )
    $sshArguments += @($RunId, $confirmationToken)
}

Invoke-CapturedProcess -FileName $sshExecutable -Arguments $sshArguments -StandardInputBytes $remoteScriptBytes
