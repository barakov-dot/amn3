param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight", "postflight", "upload", "apply")]
    [string]$Mode,
    [Parameter(Mandatory = $true)]
    [string]$Approval
)

$ErrorActionPreference = "Stop"

$expectedApproval = "APPROVE PHASE11_0B858C5_REMOTE_ORCHESTRATOR_SHA_A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72_TRUSTED_OPENSSH_ABSOLUTE_PATH_BOUND_COMBINED_SQUARE_LOGO_WIDE_LANGUAGE_HEADER_AND_TELEGRAM_HARDENING_PRIVATE_OVERLAY_UPLOAD_WEB_FREEZE_SNAPSHOT_OFFLINE_APPLY_VERIFY_AND_ROLLBACK_WITH_REGULAR_BOT_DISABLED_TELEGRAM_PROFILE_UNCHANGED_AND_AWG_UNTOUCHED"
if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact live approval mismatch"
}

$expectedPackageSha = "7866BDD9FEBE1D6EEA701B37A6E4206A8267766A56993F3C02A0C7B30C394B54"
$expectedRemoteScriptSha = "A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72"
$trustedOpenSshDir = Join-Path $env:WINDIR "System32\OpenSSH"
$sshExecutable = Join-Path $trustedOpenSshDir "ssh.exe"
$scpExecutable = Join-Path $trustedOpenSshDir "scp.exe"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "amn2_private_rc_operator_ed25519"
$knownHostsPath = Join-Path $sshDir "codex_amn2_target_known_hosts"
$remoteScript = Join-Path $PSScriptRoot "phase11_0b858c5_combined_remote_rollout.sh"
$workspace = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$packagePath = Join-Path $workspace "dist\amn2-combined-overlay-0b858c5.zip"
$checksumPath = Join-Path $workspace "dist\amn2-combined-overlay-0b858c5.zip.sha256.txt"

if (-not (Test-Path -LiteralPath $sshExecutable -PathType Leaf)) {
    throw "Trusted OpenSSH ssh.exe is missing"
}
if (-not (Test-Path -LiteralPath $scpExecutable -PathType Leaf)) {
    throw "Trusted OpenSSH scp.exe is missing"
}

foreach ($required in @($keyPath, $knownHostsPath, $remoteScript, $sshExecutable, $scpExecutable)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required local input missing"
    }
}

$knownHostLine = Get-Content -LiteralPath $knownHostsPath |
    Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") } |
    Select-Object -First 1
if (-not $knownHostLine) {
    throw "Known-host binding is empty"
}
$target = ($knownHostLine -split "\s+", 2)[0]
if (-not $target) {
    throw "Known-host target could not be resolved"
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
    $trustedExecutable =
        [string]::Equals($FileName, $sshExecutable, [StringComparison]::OrdinalIgnoreCase) -or
        [string]::Equals($FileName, $scpExecutable, [StringComparison]::OrdinalIgnoreCase)
    if (-not $trustedExecutable) {
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
    if ($StandardInputBytes.Length -gt 0) {
        $process.StandardInput.BaseStream.Write($StandardInputBytes, 0, $StandardInputBytes.Length)
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
}

$commonOptions = @(
    "-i", $keyPath,
    "-o", "BatchMode=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$knownHostsPath",
    "-o", "ConnectTimeout=15",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=4"
)

if ($Mode -eq "upload") {
    foreach ($required in @($packagePath, $checksumPath)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Package input missing"
        }
    }

    $actualPackageSha = (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash
    if ($actualPackageSha -ne $expectedPackageSha) {
        throw "Local package SHA-256 mismatch"
    }
    $receiptToken = ((Get-Content -LiteralPath $checksumPath -Raw).Trim() -split "\s+", 2)[0]
    if ($receiptToken.ToUpperInvariant() -ne $expectedPackageSha) {
        throw "Local checksum receipt mismatch"
    }

    $scpArgs = @($commonOptions) + @(
        $packagePath,
        $checksumPath,
        "root@${target}:/root/"
    )
    Invoke-CapturedProcess -FileName $scpExecutable -Arguments $scpArgs

    $chmodArgs = @($commonOptions) + @(
        "root@$target",
        "chmod 600 /root/amn2-combined-overlay-0b858c5.zip /root/amn2-combined-overlay-0b858c5.zip.sha256.txt"
    )
    Invoke-CapturedProcess -FileName $sshExecutable -Arguments $chmodArgs
    Write-Output "upload=pass"
    return
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
if (-not [string]::Equals($actualRemoteScriptSha, $expectedRemoteScriptSha, [StringComparison]::Ordinal)) {
    throw "Remote rollout script SHA-256 mismatch"
}

$sshArgs = @($commonOptions) + @(
    "root@$target",
    "bash", "-s", "--", $Mode
)
Invoke-CapturedProcess -FileName $sshExecutable -Arguments $sshArgs -StandardInputBytes $remoteScriptBytes
