[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Security") -ErrorAction Stop
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Utility") -ErrorAction Stop

$expectedRemoteScriptSha = "16CE3F9E14A72DFB0DC957B2A1CA13F1ADBCA72F41C60FC2D4DD9904D3E74CD6"
$expectedRunId = "spain-fresh-20260720-001"
$AllowedFailureStages = @(
    "bootstrap", "os_kernel", "capacity", "sockets", "firewall",
    "ssh_policy", "docker_inventory", "systemd_inventory",
    "systemd_unit_content", "systemd_cgroup_ports", "render"
)
$actualRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$expectedApproval = "APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_RUNNER_SHA_$actualRunnerSha`_REMOTE_SCRIPT_SHA_$expectedRemoteScriptSha`_SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_TRUST_RUN_ID_SPAIN_FRESH_20260720_001_DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION"
if ([string]::IsNullOrEmpty($Approval)) {
    Write-Output $expectedApproval
    throw "Exact read-only preflight approval mismatch."
}
if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact read-only preflight approval mismatch."
}
if (-not [string]::Equals($RunId, $expectedRunId, [StringComparison]::Ordinal)) {
    throw "Exact Spain trust run id mismatch."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$RemoteScriptPath = Join-Path $PSScriptRoot "post_release_spain_readonly_preflight_remote.sh"
if (-not (Test-Path -LiteralPath $RemoteScriptPath -PathType Leaf)) {
    throw "Reviewed remote probe is missing."
}
$RemoteScriptStream = [IO.File]::Open(
    $RemoteScriptPath,
    [IO.FileMode]::Open,
    [IO.FileAccess]::Read,
    [IO.FileShare]::Read
)
$RemoteReader = $null
try {
    $actualRemoteScriptSha = (Get-FileHash -InputStream $RemoteScriptStream -Algorithm SHA256).Hash.ToUpperInvariant()
    $RemoteScriptStream.Position = 0
    $RemoteReader = [IO.StreamReader]::new(
        $RemoteScriptStream,
        (New-Object Text.UTF8Encoding($false, $true)),
        $true,
        1024,
        $true
    )
    $RemoteText = $RemoteReader.ReadToEnd()
} finally {
    if ($null -ne $RemoteReader) {
        $RemoteReader.Dispose()
    }
    $RemoteScriptStream.Dispose()
}
if ($actualRemoteScriptSha -cne $expectedRemoteScriptSha) {
    $RemoteText = $null
    throw "Reviewed remote probe checksum mismatch."
}

if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$' -or $RunId.Contains("..")) {
    throw "RunId has an invalid format."
}

$ArtifactRoot = Join-Path $RepoRoot "private-artifacts\post-release\spain-migration"
$RunDirectory = Join-Path $ArtifactRoot $RunId
$RunRoot = $RunDirectory
$BindingPath = Join-Path $RunDirectory "target.env"
$KeyPath = Join-Path $RunDirectory "id_ed25519_spain"
$PublicKeyPath = "$KeyPath.pub"
$KnownHostsPath = Join-Path $RunDirectory "known_hosts_spain"
$EvidencePath = Join-Path $RunDirectory "preflight-evidence.json"
$FailureEvidencePath = Join-Path $RunRoot "preflight-failure-evidence.json"
$OutcomeClaimPath = Join-Path $RunRoot "preflight-outcome.claim"
$SshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$SshKeygenExe = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"

function Assert-LocalExecutable([string]$Path, [string]$Label) {
    if (-not [IO.Path]::IsPathRooted($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label executable is unavailable at its required absolute path."
    }
}

function Assert-PrivatePath([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required private artifact is missing."
    }
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $VerifiedAcl = Get-Acl -LiteralPath $Path
    $VerifiedRules = @($VerifiedAcl.Access)
    if (-not $VerifiedAcl.AreAccessRulesProtected -or $VerifiedRules.Count -ne 1 -or
        $VerifiedRules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value -cne $CurrentSid.Value -or
        $VerifiedRules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        (($VerifiedRules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl)) {
        throw "ACL verification did not prove current-user-only access."
    }
}

function Protect-PrivatePath([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required private artifact is missing."
    }
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Acl = Get-Acl -LiteralPath $Path
    $Acl.SetAccessRuleProtection($true, $false)
    foreach ($ExistingRule in @($Acl.Access)) {
        $Acl.RemoveAccessRuleSpecific($ExistingRule)
    }
    $Rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $CurrentSid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.InheritanceFlags]::None,
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $Acl.SetAccessRule($Rule)
    Set-Acl -LiteralPath $Path -AclObject $Acl
    Assert-PrivatePath $Path
}

function Write-EvidenceCreateNew([string]$Path, [string]$Json) {
    $Utf8WithoutBom = New-Object Text.UTF8Encoding($false)
    $EvidenceBytes = $Utf8WithoutBom.GetBytes("$Json`n")
    $EvidenceStream = [IO.File]::Open(
        $Path,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    try {
        $EvidenceStream.Write($EvidenceBytes, 0, $EvidenceBytes.Length)
        $EvidenceStream.Flush($true)
    } finally {
        $EvidenceStream.Dispose()
        [Array]::Clear($EvidenceBytes, 0, $EvidenceBytes.Length)
    }
}

function Read-SafeFailureEnvelope([string[]]$Lines, [int]$ProcessExitCode) {
    if ($ProcessExitCode -lt 1 -or $ProcessExitCode -gt 255) {
        return $null
    }
    $Prefix = "AMN2_SPAIN_PREFLIGHT_FAILURE_V1"
    $PrefixedLines = @(
        $Lines | Where-Object { $_.StartsWith($Prefix, [StringComparison]::Ordinal) }
    )
    if ($PrefixedLines.Count -ne 1) {
        return $null
    }
    $Pattern = '^AMN2_SPAIN_PREFLIGHT_FAILURE_V1\|stage=(?<stage>[a-z_]+)\|exit=(?<exit>[0-9]{1,3})$'
    $Matches = @($Lines | Where-Object { $_ -cmatch $Pattern })
    if ($Matches.Count -ne 1) {
        return $null
    }
    $Parsed = [regex]::Match($Matches[0], $Pattern)
    $Stage = $Parsed.Groups["stage"].Value
    $ExitCode = [int]$Parsed.Groups["exit"].Value
    if ($AllowedFailureStages -cnotcontains $Stage) {
        return $null
    }
    if ($ExitCode -ne $ProcessExitCode) {
        return $null
    }
    return [pscustomobject]@{ Stage = $Stage; ExitCode = $ExitCode }
}

function Assert-TargetHost([string]$Value) {
    if ($Value -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or $Value.Contains("..")) {
        throw "Target host has an invalid format."
    }
}

function Assert-TargetUser([string]$Value) {
    if ($Value -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "Target user has an invalid format."
    }
}

function Assert-Fingerprint([string]$Value) {
    if ($Value -notmatch '^SHA256:[A-Za-z0-9+/]{43}$') {
        throw "Host-key fingerprint has an invalid format."
    }
}

function Read-Binding {
    Assert-PrivatePath $RunDirectory
    Assert-PrivatePath $BindingPath
    $Lines = @(Get-Content -LiteralPath $BindingPath)
    $ExpectedNames = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($Lines.Count -ne $ExpectedNames.Count) {
        throw "Private target binding must contain exactly four lines."
    }
    $Binding = @{}
    for ($Index = 0; $Index -lt $ExpectedNames.Count; $Index++) {
        $Prefix = "$($ExpectedNames[$Index])="
        if (-not $Lines[$Index].StartsWith($Prefix, [StringComparison]::Ordinal)) {
            throw "Private target binding has an invalid schema."
        }
        $Binding[$ExpectedNames[$Index]] = $Lines[$Index].Substring($Prefix.Length)
    }
    Assert-TargetHost $Binding["TARGET_HOST"]
    Assert-TargetUser $Binding["TARGET_USER"]
    Assert-Fingerprint $Binding["EXPECTED_HOST_KEY_SHA256"]
    if ($Binding["SSH_KEY_PATH"] -cne $KeyPath) {
        throw "Private target binding is not bound to the dedicated Spain key."
    }
    return $Binding
}

function Assert-DedicatedKeyPair {
    Assert-PrivatePath $KeyPath
    Assert-PrivatePath $PublicKeyPath
    $DerivedLines = @(& $SshKeygenExe -y -f $KeyPath 2>$null)
    if ($LASTEXITCODE -ne 0 -or $DerivedLines.Count -ne 1) {
        throw "Dedicated Spain private key is invalid."
    }
    $DerivedMatch = [regex]::Match($DerivedLines[0].Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})(?: [^\r\n]+)?$')
    $PublicText = Get-Content -LiteralPath $PublicKeyPath -Raw
    $PublicMatch = [regex]::Match($PublicText.Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})(?: [^\r\n]+)?$')
    if (-not $DerivedMatch.Success -or -not $PublicMatch.Success -or $DerivedMatch.Groups[1].Value -cne $PublicMatch.Groups[1].Value) {
        throw "Dedicated Spain key files are not a matching Ed25519 pair."
    }
}

function Assert-VerifiedHostPin([hashtable]$Binding) {
    Assert-PrivatePath $KnownHostsPath
    $HostLines = @(Get-Content -LiteralPath $KnownHostsPath)
    if ($HostLines.Count -ne 1) {
        throw "Independent Spain host pin must contain exactly one entry."
    }
    $HostMatch = [regex]::Match($HostLines[0], '^([^ ]+) (ssh-ed25519|ecdsa-sha2-nistp256|rsa-sha2-(?:256|512)) ([A-Za-z0-9+/]+={0,2})$')
    if (-not $HostMatch.Success -or $HostMatch.Groups[1].Value -cne $Binding["TARGET_HOST"]) {
        throw "Independent Spain host pin is not bound to the exact private target."
    }
    $FingerprintOutput = @(& $SshKeygenExe -lf $KnownHostsPath 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Independent Spain host pin verification failed."
    }
    $Observed = [regex]::Match(($FingerprintOutput -join " "), 'SHA256:[A-Za-z0-9+/]{43}').Value
    if (-not $Observed -or $Observed -cne $Binding["EXPECTED_HOST_KEY_SHA256"]) {
        throw "Independent Spain host pin fingerprint mismatch."
    }
}

Assert-LocalExecutable $SshExe "OpenSSH client"
Assert-LocalExecutable $SshKeygenExe "OpenSSH key generator"
$Binding = Read-Binding
Assert-DedicatedKeyPair
Assert-VerifiedHostPin $Binding

$ClaimJson = [ordered]@{
    schema = "amn2.spain-readonly-preflight-claim.v1"
    runner_sha256 = $actualRunnerSha
    remote_probe_sha256 = $expectedRemoteScriptSha
    source_revision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
} | ConvertTo-Json -Compress
try {
    Write-EvidenceCreateNew $OutcomeClaimPath $ClaimJson
    Protect-PrivatePath $OutcomeClaimPath
    Assert-PrivatePath $OutcomeClaimPath
} catch {
    $RemoteText = $null
    $ClaimJson = $null
    throw "Single-use Spain preflight outcome claim creation failed."
}
$ClaimJson = $null

$SshArguments = @(
    "-F", "none",
    "-o", "BatchMode=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$KnownHostsPath",
    "-i", $KeyPath,
    "-p", "22",
    "$($Binding['TARGET_USER'])@$($Binding['TARGET_HOST'])",
    "bash -s -- preflight"
)

$SshOutput = @($RemoteText | & $SshExe @SshArguments 2>$null)
$ProcessExitCode = $LASTEXITCODE
if ($ProcessExitCode -ne 0) {
    $FailurePrefixCount = @(
        $SshOutput | Where-Object {
            ([string]$_).StartsWith("AMN2_SPAIN_PREFLIGHT_FAILURE_V1", [StringComparison]::Ordinal)
        }
    ).Count
    $SafeFailure = Read-SafeFailureEnvelope ([string[]]$SshOutput) $ProcessExitCode
    if ($FailurePrefixCount -gt 0 -and $null -eq $SafeFailure) {
        $SshOutput = $null
        $RemoteText = $null
        throw "Read-only Spain preflight returned a malformed failure envelope."
    }
    if ($null -ne $SafeFailure) {
        $FailureClassification = "remote_probe"
        $FailureStage = $SafeFailure.Stage
        $FailureExitCode = $SafeFailure.ExitCode
    } elseif ($ProcessExitCode -ge 1 -and $ProcessExitCode -le 255) {
        $FailureClassification = "transport"
        $FailureStage = "unavailable"
        $FailureExitCode = $ProcessExitCode
    } else {
        $SshOutput = $null
        $RemoteText = $null
        throw "Read-only Spain preflight failed without a safe exit classification."
    }
    $FailureJson = [ordered]@{
        schema = "amn2.spain-readonly-preflight-failure.v1"
        classification = $FailureClassification
        stage = $FailureStage
        exit_code = $FailureExitCode
        runner_sha256 = $actualRunnerSha
        remote_probe_sha256 = $expectedRemoteScriptSha
        source_revision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
    } | ConvertTo-Json -Compress
    $SshOutput = $null
    $RemoteText = $null
    try {
        Write-EvidenceCreateNew $FailureEvidencePath $FailureJson
        Protect-PrivatePath $FailureEvidencePath
        Assert-PrivatePath $FailureEvidencePath
    } catch {
        $FailureJson = $null
        throw "Atomic read-only preflight failure evidence creation failed."
    }
    $FailureJson = $null
    throw "Read-only Spain preflight failed at a sanitized stage; failure evidence created."
}
$RawEvidence = ($SshOutput -join "`n").Trim()
$SshOutput = $null
$RemoteText = $null
if (-not $RawEvidence -or $RawEvidence.Contains($Binding["TARGET_HOST"])) {
    $RawEvidence = $null
    throw "Read-only Spain preflight returned unsafe evidence."
}
try {
    $Evidence = $RawEvidence | ConvertFrom-Json -ErrorAction Stop
} catch {
    $RawEvidence = $null
    throw "Read-only Spain preflight returned invalid JSON."
}
if ($Evidence.schema -cne "amn2.spain-readonly-preflight.v1" -or $Evidence.mode -cne "preflight") {
    throw "Read-only Spain preflight evidence schema mismatch."
}
$EvidenceJson = $Evidence | ConvertTo-Json -Depth 8 -Compress
if ($EvidenceJson -match '(?i)(authorization|bearer|BEGIN [A-Z ]+ KEY|api[_-]?key|credential)') {
    throw "Read-only Spain preflight evidence failed redaction validation."
}
try {
    Write-EvidenceCreateNew $EvidencePath $EvidenceJson
} catch {
    $RawEvidence = $null
    $EvidenceJson = $null
    throw "Atomic read-only preflight evidence creation failed."
}
$RawEvidence = $null
$EvidenceJson = $null
Protect-PrivatePath $EvidencePath
Assert-PrivatePath $EvidencePath
Write-Output "Spain read-only preflight evidence recorded locally."
