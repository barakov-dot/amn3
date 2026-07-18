param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight", "run")]
    [string]$Mode,
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedRemoteScriptSha = "6D4F801D7A0235C62E8F558B9D9F82DF676F672C0F7972A30F4362BCA12C9526"
$expectedApproval = "APPROVE POST_RELEASE_API_001_REMOTE_SHA_6D4F801D7A0235C62E8F558B9D9F82DF676F672C0F7972A30F4362BCA12C9526_SOURCE_0B858C5_TRANSIENT_LOOPBACK_3040_CLONE_DB_SCOPED_TOKEN_TTL_REVOKE_AUDIT_SIX_ROUTE_SMOKE_MANDATORY_CLEANUP_PRODUCTION_BOT_WEB_DB_AND_AWG_UNTOUCHED"

if ($Mode -eq "preflight") {
    if ($Approval) {
        throw "Preflight mode does not accept approval"
    }
} elseif (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact live approval mismatch"
}

$trustedOpenSshDir = Join-Path $env:WINDIR "System32\OpenSSH"
$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "amn2_private_rc_operator_ed25519"
$knownHostsPath = Join-Path $sshDir "codex_amn2_target_known_hosts"
$remoteScript = Join-Path $PSScriptRoot "post_release_api_001_remote.sh"

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

    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FileName
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.RedirectStandardInput = $true
    foreach ($argument in $Arguments) {
        [void]$startInfo.ArgumentList.Add($argument)
    }

    $process = [Diagnostics.Process]::Start($startInfo)
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
    throw "Remote API-001 script SHA-256 mismatch"
}

if ($Mode -eq "run") {
    $approvalStateDir = Join-Path $env:LOCALAPPDATA "AMN2\post-release"
    $approvalReceipt = Join-Path $approvalStateDir (
        "api-001-" + $expectedRemoteScriptSha + ".run-consumed"
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
        $receipt = [Text.Encoding]::UTF8.GetBytes(
            "mode=run`nremote_sha256=$expectedRemoteScriptSha`n"
        )
        $receiptStream.Write($receipt, 0, $receipt.Length)
        $receiptStream.Flush($true)
    } catch [IO.IOException] {
        throw "API-001 run approval was already consumed"
    } finally {
        if ($null -ne $receiptStream) {
            $receiptStream.Dispose()
        }
    }
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

Invoke-CapturedProcess `
    -FileName $sshExecutable `
    -Arguments $sshArguments `
    -StandardInputBytes $remoteScriptBytes
