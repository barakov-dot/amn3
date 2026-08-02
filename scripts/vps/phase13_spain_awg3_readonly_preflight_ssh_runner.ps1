[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("preflight")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$OutcomeId,

    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Security") -ErrorAction Stop
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Utility") -ErrorAction Stop
$script:Utf8NoBom = New-Object Text.UTF8Encoding($false)
[Console]::OutputEncoding = $script:Utf8NoBom
[Console]::InputEncoding = $script:Utf8NoBom
$OutputEncoding = $script:Utf8NoBom

$script:SourceHead = "ff115b63ca1329640ca13ae0a502d155f99b456b"
$script:TrustedBundleRunId = "spain-fresh-20260720-001"
$script:AllowedRemoteFailureStages = @(
    "bootstrap", "candidate_sockets", "candidate_links",
    "candidate_addresses_routes", "candidate_docker", "candidate_systemd",
    "candidate_paths", "awg2_projection", "foreign_projection", "render"
)

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$Path)
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $Item.PSIsContainer) {
        throw "Artifact must be a regular non-reparse file."
    }
    $Stream = [IO.File]::Open($Item.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($Hasher.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    } finally {
        $Hasher.Dispose()
        $Stream.Dispose()
    }
}

function Read-StrictUtf8Bytes {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$MaximumBytes = 1048576
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $Item.PSIsContainer) {
        throw "Input must be a regular non-reparse file."
    }
    if ($Item.Length -lt 1 -or $Item.Length -gt $MaximumBytes) {
        throw "Input length is outside the bounded range."
    }
    $Bytes = [IO.File]::ReadAllBytes($Item.FullName)
    $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    [void]$StrictUtf8.GetString($Bytes)
    return $Bytes
}

function Read-CanonicalManifest {
    param([Parameter(Mandatory = $true)][string]$Path)
    $Bytes = Read-StrictUtf8Bytes -Path $Path
    if (@($Bytes | Where-Object { $_ -eq 13 }).Count -ne 0 -or $Bytes[$Bytes.Length - 1] -ne 10) {
        throw "Manifest bytes are not canonical LF UTF-8."
    }
    $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    $Text = $StrictUtf8.GetString($Bytes)
    if ($Text.Substring(0, $Text.Length - 1).Contains("`n")) {
        throw "Manifest must contain exactly one canonical JSON document."
    }
    try { $Manifest = $Text | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "Manifest JSON is invalid." }
    return [pscustomobject]@{ Bytes = $Bytes; Value = $Manifest }
}

function Assert-OutcomeId {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$') {
        throw "Outcome id is invalid."
    }
}

function Assert-ManifestContract {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][string]$ExpectedOutcomeId
    )
    if ($Manifest.schema -cne "amn2.phase13.awg3-readonly-preflight-manifest.v1" -or
        $Manifest.outcome_id -cne $ExpectedOutcomeId -or
        $Manifest.source_base -cne "55dc243b8e6c6bdb57f8301b56326e4cd4072d19" -or
        $Manifest.source_head -cne $script:SourceHead -or
        $Manifest.spain_overlay -cne "f1bf099ddb47da26a4080714376babaf5b0de92c" -or
        $Manifest.target_role -cne "spain-primary" -or
        [int]$Manifest.max_attempts -ne 1 -or
        $Manifest.remote_write_allowed -ne $false -or
        $Manifest.package_build_allowed -ne $false -or
        $Manifest.live_action_authorized -ne $false) {
        throw "Manifest identity or safety contract mismatch."
    }
    try { $ExpiresAt = [DateTimeOffset]::Parse($Manifest.expires_at, [Globalization.CultureInfo]::InvariantCulture) }
    catch { throw "Manifest expiry is invalid." }
    if ($ExpiresAt -le [DateTimeOffset]::UtcNow) {
        throw "Manifest outcome is expired."
    }
}

function Assert-ManifestArtifacts {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot
    )
    $Root = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\') + '\'
    if ($null -eq $Manifest.artifacts -or @($Manifest.artifacts).Count -lt 1) {
        throw "Manifest artifact set is empty."
    }
    foreach ($Artifact in @($Manifest.artifacts)) {
        $Relative = [string]$Artifact.path
        if ([IO.Path]::IsPathRooted($Relative) -or $Relative.Contains("..") -or $Relative.Contains(':')) {
            throw "Manifest artifact path is unsafe."
        }
        $Resolved = [IO.Path]::GetFullPath((Join-Path $RepositoryRoot ($Relative -replace '/', '\')))
        if (-not $Resolved.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Manifest artifact escapes repository root."
        }
        $Item = Get-Item -LiteralPath $Resolved -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $Item.PSIsContainer -or
            [Int64]$Artifact.size -ne $Item.Length -or
            (Get-Sha256Hex -Path $Resolved) -cne ([string]$Artifact.sha256).ToLowerInvariant()) {
            throw "Manifest artifact checksum mismatch."
        }
    }
}

function Get-ManifestArtifactSha {
    param(
        [Parameter(Mandatory = $true)]$Manifest,
        [Parameter(Mandatory = $true)][string]$FileName
    )
    $ArtifactMatches = @($Manifest.artifacts | Where-Object { [IO.Path]::GetFileName([string]$_.path) -ceq $FileName })
    if ($ArtifactMatches.Count -ne 1 -or -not [regex]::IsMatch([string]($ArtifactMatches[0].sha256), '^[0-9a-f]{64}$')) {
        throw "Required manifest artifact binding is missing."
    }
    return ([string]($ArtifactMatches[0].sha256)).ToLowerInvariant()
}

function New-ExactApprovalPhrase {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeId,
        [Parameter(Mandatory = $true)][string]$ManifestSha256,
        [Parameter(Mandatory = $true)][string]$RunnerSha256,
        [Parameter(Mandatory = $true)][string]$CollectorSha256,
        [Parameter(Mandatory = $true)][string]$SchemaSha256,
        [Parameter(Mandatory = $true)][string]$FoundationSha256
    )
    $RussianPrefix = [Text.Encoding]::UTF8.GetString(
        [Convert]::FromBase64String("0KPQotCS0JXQoNCW0JTQkNCuINCe0JTQmNCd")
    )
    return "$RussianPrefix READ-ONLY SPAIN PREFLIGHT OUTCOME_$OutcomeId MANIFEST_SHA_$ManifestSha256 RUNNER_SHA_$RunnerSha256 COLLECTOR_SHA_$CollectorSha256 SCHEMA_SHA_$SchemaSha256 FOUNDATION_SHA_$FoundationSha256 NO_PACKAGE_BUILD_NO_DEPLOY_NO_MUTATION"
}

function Resolve-Phase13ClaimFailure {
    param([Parameter(Mandatory = $true)][string]$ClaimSubreason)

    switch -CaseSensitive ($ClaimSubreason) {
        "existing_valid_claim" {
            return [pscustomobject][ordered]@{
                ExitCode = 66
                Stage = "outcome_claim"
                ReasonCode = "outcome_replay"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "private_root_preparation_failed" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "private_root_validation"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "private_root_unsafe" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "private_root_validation"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "outcome_directory_partial" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "outcome_directory_create_failed" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "outcome_directory_protection_failed" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "claim_write_failed" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "claim_validation_failed" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        "claim_internal_failure" {
            return [pscustomobject][ordered]@{
                ExitCode = 75
                Stage = "outcome_claim"
                ReasonCode = "observation_ambiguous"
                ClaimSubreason = $ClaimSubreason
            }
        }
        default { throw "Claim subreason is not allowlisted." }
    }
}

function Resolve-Phase13ExpiredManifestFailure {
    return [pscustomobject][ordered]@{
        ExitCode = 64
        Stage = "argument_validation"
        ReasonCode = "schema_validation_failed"
        ClaimSubreason = "not_applicable"
    }
}

function Write-BytesCreateNew {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][byte[]]$Bytes
    )
    $Stream = New-Object IO.FileStream(
        $Path,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None,
        4096,
        [IO.FileOptions]::WriteThrough
    )
    try {
        $Stream.Write($Bytes, 0, $Bytes.Length)
        $Stream.Flush($true)
    } finally {
        $Stream.Dispose()
    }
}

function Protect-Phase13PrivateDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$OwnerSid
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        [IO.Directory]::CreateDirectory($Path) | Out-Null
    }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Private outcome directory is unsafe."
    }
    $Owner = New-Object Security.Principal.SecurityIdentifier($OwnerSid)
    $Acl = Get-Acl -LiteralPath $Item.FullName
    $Acl.SetOwner($Owner)
    $Acl.SetAccessRuleProtection($true, $false)
    foreach ($Rule in @($Acl.Access)) {
        $Acl.RemoveAccessRuleSpecific($Rule)
    }
    $Acl.SetAccessRule((New-Object Security.AccessControl.FileSystemAccessRule(
        $Owner,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit',
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )))
    Set-Acl -LiteralPath $Item.FullName -AclObject $Acl
    Assert-PrivatePath -Path $Item.FullName -ExpectedOwnerSid $OwnerSid
}

function Throw-Phase13ClaimFailure {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet(
            "existing_valid_claim",
            "private_root_preparation_failed",
            "private_root_unsafe",
            "outcome_directory_partial",
            "outcome_directory_create_failed",
            "outcome_directory_protection_failed",
            "claim_write_failed",
            "claim_validation_failed",
            "claim_internal_failure"
        )]
        [string]$ClaimSubreason
    )
    $Exception = New-Object InvalidOperationException "Phase 13 outcome claim failed."
    $Exception.Data["AMN2_PHASE13_CLAIM_SUBREASON"] = $ClaimSubreason
    throw $Exception
}

function Get-Phase13ClaimFailureSubreason {
    param([Parameter(Mandatory = $true)][Exception]$Exception)
    $Allowed = @(
        "existing_valid_claim",
        "private_root_preparation_failed",
        "private_root_unsafe",
        "outcome_directory_partial",
        "outcome_directory_create_failed",
        "outcome_directory_protection_failed",
        "claim_write_failed",
        "claim_validation_failed",
        "claim_internal_failure"
    )
    $Current = $Exception
    for ($Index = 0; $Index -lt 4 -and $null -ne $Current; $Index++) {
        if ($Current.Data.Contains("AMN2_PHASE13_CLAIM_SUBREASON")) {
            $Candidate = [string]$Current.Data["AMN2_PHASE13_CLAIM_SUBREASON"]
            if ($Candidate -cin $Allowed) {
                return $Candidate
            }
        }
        $Current = $Current.InnerException
    }
    return "claim_internal_failure"
}

function Get-Phase13ExistingOutcomeClaimSubreason {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeDirectory,
        [Parameter(Mandatory = $true)][string]$OutcomeId,
        [Parameter(Mandatory = $true)][string]$ManifestSha256,
        [Parameter(Mandatory = $true)][string]$RunnerSha256,
        [Parameter(Mandatory = $true)][string]$CollectorSha256,
        [Parameter(Mandatory = $true)][string]$TargetRole
    )
    try {
        $DirectoryItem = Get-Item -LiteralPath $OutcomeDirectory -Force -ErrorAction Stop
        if (-not $DirectoryItem.PSIsContainer -or ($DirectoryItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            return "outcome_directory_partial"
        }
        $ClaimPath = Join-Path $DirectoryItem.FullName "outcome-claim.json"
        if (-not (Test-Path -LiteralPath $ClaimPath -PathType Leaf)) {
            return "outcome_directory_partial"
        }
        $ClaimItem = Get-Item -LiteralPath $ClaimPath -Force -ErrorAction Stop
        if ($ClaimItem.PSIsContainer -or ($ClaimItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            return "claim_validation_failed"
        }
        $ClaimBytes = Read-StrictUtf8Bytes -Path $ClaimItem.FullName -MaximumBytes 4096
        try {
            if (@($ClaimBytes | Where-Object { $_ -eq 13 }).Count -ne 0 -or $ClaimBytes[$ClaimBytes.Length - 1] -ne 10) {
                return "claim_validation_failed"
            }
            $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
            $ClaimText = $StrictUtf8.GetString($ClaimBytes)
            if ($ClaimText.Substring(0, $ClaimText.Length - 1).Contains("`n")) {
                return "claim_validation_failed"
            }
            $Claim = $ClaimText | ConvertFrom-Json -ErrorAction Stop
            $ExpectedProperties = @(
                "schema", "outcome_id", "manifest_sha256", "runner_sha256",
                "collector_sha256", "target_role", "created_at"
            )
            $ActualProperties = @($Claim.PSObject.Properties.Name)
            if ($ActualProperties.Count -ne $ExpectedProperties.Count) {
                return "claim_validation_failed"
            }
            foreach ($Name in $ExpectedProperties) {
                if ($ActualProperties -cnotcontains $Name) {
                    return "claim_validation_failed"
                }
            }
            if ([string]$Claim.schema -cne "amn2.phase13.awg3-readonly-preflight-claim.v1" -or
                [string]$Claim.outcome_id -cne $OutcomeId -or
                [string]$Claim.manifest_sha256 -cne $ManifestSha256 -or
                [string]$Claim.runner_sha256 -cne $RunnerSha256 -or
                [string]$Claim.collector_sha256 -cne $CollectorSha256 -or
                [string]$Claim.target_role -cne $TargetRole -or
                $ClaimText -cnotmatch '"created_at":"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"') {
                return "claim_validation_failed"
            }
            return "existing_valid_claim"
        } finally {
            [Array]::Clear($ClaimBytes, 0, $ClaimBytes.Length)
        }
    } catch {
        return "claim_validation_failed"
    }
}

function New-Phase13OutcomeClaim {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)][string]$OutcomeId,
        [Parameter(Mandatory = $true)][string]$OwnerSid,
        [Parameter(Mandatory = $true)][string]$ManifestSha256,
        [Parameter(Mandatory = $true)][string]$RunnerSha256,
        [Parameter(Mandatory = $true)][string]$CollectorSha256,
        [Parameter(Mandatory = $true)][string]$TargetRole
    )
    Assert-OutcomeId -Value $OutcomeId
    foreach ($Hash in @($ManifestSha256, $RunnerSha256, $CollectorSha256)) {
        if ($Hash -cnotmatch '^[0-9a-f]{64}$') {
            throw "Outcome claim checksum is invalid."
        }
    }
    if ($TargetRole -cne "spain-primary") {
        throw "Outcome claim target role is invalid."
    }
    try {
        if (Test-Path -LiteralPath $OutcomeRoot) {
            $OutcomeRootItem = Get-Item -LiteralPath $OutcomeRoot -Force -ErrorAction Stop
            if (-not $OutcomeRootItem.PSIsContainer -or ($OutcomeRootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Throw-Phase13ClaimFailure -ClaimSubreason "private_root_unsafe"
            }
        }
    } catch {
        $Subreason = Get-Phase13ClaimFailureSubreason -Exception $_.Exception
        if ($Subreason -ceq "private_root_unsafe") {
            throw
        }
        Throw-Phase13ClaimFailure -ClaimSubreason "private_root_preparation_failed"
    }
    try {
        Protect-Phase13PrivateDirectory -Path $OutcomeRoot -OwnerSid $OwnerSid
    } catch {
        Throw-Phase13ClaimFailure -ClaimSubreason "private_root_preparation_failed"
    }
    $OutcomeDirectory = Join-Path $OutcomeRoot $OutcomeId
    if (Test-Path -LiteralPath $OutcomeDirectory) {
        Throw-Phase13ClaimFailure -ClaimSubreason (Get-Phase13ExistingOutcomeClaimSubreason -OutcomeDirectory $OutcomeDirectory -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha256 -RunnerSha256 $RunnerSha256 -CollectorSha256 $CollectorSha256 -TargetRole $TargetRole)
    }
    try {
        [IO.Directory]::CreateDirectory($OutcomeDirectory) | Out-Null
    } catch {
        Throw-Phase13ClaimFailure -ClaimSubreason "outcome_directory_create_failed"
    }
    try {
        Protect-Phase13PrivateDirectory -Path $OutcomeDirectory -OwnerSid $OwnerSid
    } catch {
        Throw-Phase13ClaimFailure -ClaimSubreason "outcome_directory_protection_failed"
    }
    $Claim = [ordered]@{
        schema = "amn2.phase13.awg3-readonly-preflight-claim.v1"
        outcome_id = $OutcomeId
        manifest_sha256 = $ManifestSha256
        runner_sha256 = $RunnerSha256
        collector_sha256 = $CollectorSha256
        target_role = $TargetRole
        created_at = [DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
    $ClaimPath = Join-Path $OutcomeDirectory "outcome-claim.json"
    $ClaimBytes = $script:Utf8NoBom.GetBytes(($Claim | ConvertTo-Json -Compress) + "`n")
    try {
        Write-BytesCreateNew -Path $ClaimPath -Bytes $ClaimBytes
    } catch {
        $Subreason = Get-Phase13ExistingOutcomeClaimSubreason -OutcomeDirectory $OutcomeDirectory -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha256 -RunnerSha256 $RunnerSha256 -CollectorSha256 $CollectorSha256 -TargetRole $TargetRole
        if ($Subreason -ceq "existing_valid_claim") {
            Throw-Phase13ClaimFailure -ClaimSubreason $Subreason
        }
        Throw-Phase13ClaimFailure -ClaimSubreason "claim_write_failed"
    } finally {
        [Array]::Clear($ClaimBytes, 0, $ClaimBytes.Length)
    }
    return $ClaimPath
}

function Assert-PrivatePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Private path reparse point rejected."
    }
    $Acl = Get-Acl -LiteralPath $Item.FullName
    $OwnerSid = $Acl.Owner
    try { $OwnerSid = ([Security.Principal.NTAccount]$Acl.Owner).Translate([Security.Principal.SecurityIdentifier]).Value }
    catch { }
    if ($OwnerSid -cne $ExpectedOwnerSid -or -not $Acl.AreAccessRulesProtected) {
        throw "Private path owner or ACL protection mismatch."
    }
    $Allowed = @($ExpectedOwnerSid, "S-1-5-18", "S-1-5-32-544")
    foreach ($Rule in $Acl.Access) {
        if ($Rule.IsInherited) { throw "Inherited private ACL rejected." }
        $RuleSid = $Rule.IdentityReference.Value
        try { $RuleSid = $Rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value }
        catch { }
        if ($Rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and $Allowed -cnotcontains $RuleSid) {
            throw "Foreign principal in private ACL rejected."
        }
    }
}

function Assert-Phase13TrustPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    Assert-PrivatePath -Path $Path -ExpectedOwnerSid $ExpectedOwnerSid
    $Acl = Get-Acl -LiteralPath $Path
    $Rules = @($Acl.Access)
    if ($Rules.Count -ne 1) {
        throw "Trust path ACL is not current-user-only."
    }
    $RuleSid = $Rules[0].IdentityReference.Value
    try { $RuleSid = $Rules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value }
    catch { }
    if ($RuleSid -cne $ExpectedOwnerSid -or
        $Rules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        (($Rules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl)) {
        throw "Trust path ACL is not current-user-only."
    }
}

function Assert-Phase13LocalExecutable {
    param([string]$Path)
    if (-not [IO.Path]::IsPathRooted($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required local executable is unavailable."
    }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Local executable reparse point rejected."
    }
}

function Assert-Phase13TargetHost([string]$Value) {
    if ($Value -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or $Value.Contains("..")) {
        throw "Private target host format rejected."
    }
}

function Assert-Phase13TargetUser([string]$Value) {
    if ($Value -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "Private target user format rejected."
    }
}

function Assert-Phase13Fingerprint([string]$Value) {
    if ($Value -notmatch '^SHA256:[A-Za-z0-9+/]{43}$') {
        throw "Private host-key fingerprint format rejected."
    }
}

function Read-Phase13TrustBinding {
    param(
        [Parameter(Mandatory = $true)][string]$TrustRoot,
        [Parameter(Mandatory = $true)][string]$BindingPath,
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    Assert-Phase13TrustPath -Path $TrustRoot -ExpectedOwnerSid $ExpectedOwnerSid
    Assert-Phase13TrustPath -Path $BindingPath -ExpectedOwnerSid $ExpectedOwnerSid
    $Lines = @(Get-Content -LiteralPath $BindingPath)
    $ExpectedNames = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($Lines.Count -ne $ExpectedNames.Count) {
        throw "Private target binding schema rejected."
    }
    $Binding = @{}
    for ($Index = 0; $Index -lt $ExpectedNames.Count; $Index++) {
        $Prefix = "$($ExpectedNames[$Index])="
        if (-not $Lines[$Index].StartsWith($Prefix, [StringComparison]::Ordinal)) {
            throw "Private target binding schema rejected."
        }
        $Binding[$ExpectedNames[$Index]] = $Lines[$Index].Substring($Prefix.Length)
    }
    Assert-Phase13TargetHost $Binding["TARGET_HOST"]
    Assert-Phase13TargetUser $Binding["TARGET_USER"]
    Assert-Phase13Fingerprint $Binding["EXPECTED_HOST_KEY_SHA256"]
    if ($Binding["SSH_KEY_PATH"] -cne $KeyPath) {
        throw "Private target binding dedicated key mismatch."
    }
    return $Binding
}

function Assert-Phase13DedicatedEd25519KeyPair {
    param(
        [Parameter(Mandatory = $true)][string]$PrivateKeyPath,
        [Parameter(Mandatory = $true)][string]$PublicKeyPath,
        [Parameter(Mandatory = $true)][string]$SshKeygenExecutable,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    Assert-Phase13LocalExecutable -Path $SshKeygenExecutable
    Assert-Phase13TrustPath -Path $PrivateKeyPath -ExpectedOwnerSid $ExpectedOwnerSid
    Assert-Phase13TrustPath -Path $PublicKeyPath -ExpectedOwnerSid $ExpectedOwnerSid
    $DerivedLines = @(& $SshKeygenExecutable -y -f $PrivateKeyPath 2>$null)
    if ($LASTEXITCODE -ne 0 -or $DerivedLines.Count -ne 1) {
        throw "Dedicated Ed25519 private key rejected."
    }
    $DerivedMatch = [regex]::Match($DerivedLines[0].Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})(?: [^\r\n]+)?$')
    $PublicMatch = [regex]::Match((Get-Content -LiteralPath $PublicKeyPath -Raw).Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})(?: [^\r\n]+)?$')
    if (-not $DerivedMatch.Success -or -not $PublicMatch.Success -or
        $DerivedMatch.Groups[1].Value -cne $PublicMatch.Groups[1].Value) {
        throw "Dedicated Ed25519 key pair mismatch."
    }
}

function Assert-Phase13VerifiedHostPin {
    param(
        [Parameter(Mandatory = $true)][string]$KnownHostsPath,
        [Parameter(Mandatory = $true)][hashtable]$Binding,
        [Parameter(Mandatory = $true)][string]$SshKeygenExecutable,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    Assert-Phase13LocalExecutable -Path $SshKeygenExecutable
    Assert-Phase13TrustPath -Path $KnownHostsPath -ExpectedOwnerSid $ExpectedOwnerSid
    $HostLines = @(Get-Content -LiteralPath $KnownHostsPath)
    if ($HostLines.Count -ne 1) {
        throw "Independent host-key pin schema rejected."
    }
    $HostMatch = [regex]::Match($HostLines[0], '^([^ ]+) (ssh-ed25519|ecdsa-sha2-nistp256|rsa-sha2-(?:256|512)) ([A-Za-z0-9+/]+={0,2})$')
    if (-not $HostMatch.Success -or $HostMatch.Groups[1].Value -cne $Binding["TARGET_HOST"]) {
        throw "Independent host-key pin target mismatch."
    }
    $FingerprintOutput = @(& $SshKeygenExecutable -lf $KnownHostsPath 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Independent host-key pin verification failed."
    }
    $ObservedFingerprint = [regex]::Match(($FingerprintOutput -join " "), 'SHA256:[A-Za-z0-9+/]{43}').Value
    if (-not $ObservedFingerprint -or $ObservedFingerprint -cne $Binding["EXPECTED_HOST_KEY_SHA256"]) {
        throw "Independent host-key fingerprint mismatch."
    }
}

function New-Phase13SshArguments {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Binding,
        [Parameter(Mandatory = $true)][string]$KnownHostsPath,
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$OutcomeId,
        [Parameter(Mandatory = $true)][string]$ManifestSha256,
        [Parameter(Mandatory = $true)][string]$RunnerSha256,
        [Parameter(Mandatory = $true)][string]$CollectorSha256,
        [Parameter(Mandatory = $true)][string]$SchemaSha256,
        [Parameter(Mandatory = $true)][string]$FoundationSha256
    )
    Assert-OutcomeId -Value $OutcomeId
    Assert-Phase13TargetHost -Value $Binding["TARGET_HOST"]
    Assert-Phase13TargetUser -Value $Binding["TARGET_USER"]
    foreach ($Hash in @($ManifestSha256, $RunnerSha256, $CollectorSha256, $SchemaSha256, $FoundationSha256)) {
        if ($Hash -cnotmatch '^[0-9a-f]{64}$') {
            throw "Remote checksum binding rejected."
        }
    }
    $RemoteCommand = @(
        "AMN2_PHASE13_OUTCOME_ID=$OutcomeId",
        "AMN2_PHASE13_MANIFEST_SHA256=$ManifestSha256",
        "AMN2_PHASE13_RUNNER_SHA256=$RunnerSha256",
        "AMN2_PHASE13_COLLECTOR_SHA256=$CollectorSha256",
        "AMN2_PHASE13_SCHEMA_SHA256=$SchemaSha256",
        "AMN2_PHASE13_FOUNDATION_SHA256=$FoundationSha256",
        "bash -s -- preflight"
    ) -join ' '
    return @(
        "-T",
        "-F", "none",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=$KnownHostsPath",
        "-o", "ConnectTimeout=10",
        "-o", "ConnectionAttempts=1",
        "-o", "ServerAliveInterval=5",
        "-o", "ServerAliveCountMax=1",
        "-i", $KeyPath,
        "-p", "22",
        "$($Binding['TARGET_USER'])@$($Binding['TARGET_HOST'])",
        $RemoteCommand
    )
}

function ConvertTo-ProcessArgumentString {
    param([string[]]$Arguments)
    $Quoted = foreach ($Argument in $Arguments) {
        if ($Argument -notmatch '[\s"]') { $Argument }
        else { '"' + ($Argument -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"' }
    }
    return ($Quoted -join ' ')
}

function New-BoundedTransportLocalProcessFailure {
    param([Parameter(Mandatory = $true)][int]$MaximumOutputBytes)
    return [pscustomobject]@{
        ExitCode = -1
        TimedOut = $false
        OutputLimitExceeded = $false
        LocalFailureReason = "local_process_failure"
        StdoutBytes = [byte[]]@()
        StderrBytes = [byte[]]@()
        MaximumOutputBytes = $MaximumOutputBytes
    }
}

function Invoke-BoundedTransport {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [string[]]$Arguments = @(),
        [byte[]]$InputBytes = ([byte[]]@()),
        [int]$TimeoutMilliseconds = 15000,
        [int]$MaximumOutputBytes = 65536,
        [int]$MaximumInputBytes = 1048576
    )
    if ($TimeoutMilliseconds -lt 1 -or $TimeoutMilliseconds -gt 60000 -or
        $MaximumOutputBytes -lt 1 -or $MaximumOutputBytes -gt 1048576 -or
        $InputBytes.Length -gt $MaximumInputBytes) {
        throw "Transport bounds are invalid."
    }
    $StartInfo = New-Object Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $Executable
    $StartInfo.Arguments = ConvertTo-ProcessArgumentString -Arguments $Arguments
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardInput = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $Process = New-Object Diagnostics.Process
    $Process.StartInfo = $StartInfo
    $Stdout = New-Object IO.MemoryStream
    $Stderr = New-Object IO.MemoryStream
    $ProcessStarted = $false
    try {
        try {
            if (-not $Process.Start()) {
                return New-BoundedTransportLocalProcessFailure -MaximumOutputBytes $MaximumOutputBytes
            }
            $ProcessStarted = $true
        } catch {
            return New-BoundedTransportLocalProcessFailure -MaximumOutputBytes $MaximumOutputBytes
        }
        $StdoutBuffer = New-Object byte[] 4096
        $StderrBuffer = New-Object byte[] 4096
        $StdoutEof = $false
        $StderrEof = $false
        $StdoutTask = $Process.StandardOutput.BaseStream.ReadAsync($StdoutBuffer, 0, $StdoutBuffer.Length)
        $StderrTask = $Process.StandardError.BaseStream.ReadAsync($StderrBuffer, 0, $StderrBuffer.Length)
        try {
            if ($InputBytes.Length -gt 0) {
                $Process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length)
                $Process.StandardInput.BaseStream.Flush()
            }
            $Process.StandardInput.Close()
        } catch {
            return New-BoundedTransportLocalProcessFailure -MaximumOutputBytes $MaximumOutputBytes
        }
        $Deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
        $TimedOut = $false
        $OutputLimitExceeded = $false
        while (-not ($Process.HasExited -and $StdoutEof -and $StderrEof)) {
            if (-not $StdoutEof -and $StdoutTask.IsCompleted) {
                $Count = $StdoutTask.GetAwaiter().GetResult()
                if ($Count -eq 0) {
                    $StdoutEof = $true
                } elseif ($Stdout.Length + $Count -gt $MaximumOutputBytes) {
                    $OutputLimitExceeded = $true
                } else {
                    $Stdout.Write($StdoutBuffer, 0, $Count)
                    $StdoutTask = $Process.StandardOutput.BaseStream.ReadAsync($StdoutBuffer, 0, $StdoutBuffer.Length)
                }
            }
            if (-not $StderrEof -and $StderrTask.IsCompleted) {
                $Count = $StderrTask.GetAwaiter().GetResult()
                if ($Count -eq 0) {
                    $StderrEof = $true
                } elseif ($Stderr.Length + $Count -gt $MaximumOutputBytes) {
                    $OutputLimitExceeded = $true
                } else {
                    $Stderr.Write($StderrBuffer, 0, $Count)
                    $StderrTask = $Process.StandardError.BaseStream.ReadAsync($StderrBuffer, 0, $StderrBuffer.Length)
                }
            }
            if ($OutputLimitExceeded) { break }
            if ([DateTime]::UtcNow -ge $Deadline -and -not ($Process.HasExited -and $StdoutEof -and $StderrEof)) {
                $TimedOut = $true
                break
            }
            [Threading.Thread]::Sleep(5)
        }
        if ($TimedOut -or $OutputLimitExceeded) {
            try { $Process.Kill() } catch { }
            [void]$Process.WaitForExit(5000)
        }
        $ExitCode = if ($TimedOut) { -1 } else { $Process.ExitCode }
        return [pscustomobject]@{
            ExitCode = $ExitCode
            TimedOut = $TimedOut
            OutputLimitExceeded = $OutputLimitExceeded
            LocalFailureReason = $null
            StdoutBytes = $Stdout.ToArray()
            StderrBytes = $Stderr.ToArray()
            MaximumOutputBytes = $MaximumOutputBytes
        }
    } finally {
        if ($ProcessStarted) {
            try {
                if (-not $Process.HasExited) {
                    $Process.Kill()
                    [void]$Process.WaitForExit(5000)
                }
            } catch { }
        }
        try {
            if ($Stdout.Length -gt 0) {
                $StdoutBufferToClear = $Stdout.GetBuffer()
                [Array]::Clear($StdoutBufferToClear, 0, $StdoutBufferToClear.Length)
            }
        } catch { }
        try {
            if ($Stderr.Length -gt 0) {
                $StderrBufferToClear = $Stderr.GetBuffer()
                [Array]::Clear($StderrBufferToClear, 0, $StderrBufferToClear.Length)
            }
        } catch { }
        $Process.Dispose()
        $Stdout.Dispose()
        $Stderr.Dispose()
    }
}

function ConvertFrom-BoundedCollectorEnvelope {
    param([Parameter(Mandatory = $true)]$Transport)
    if ($Transport.LocalFailureReason -ceq "local_process_failure") {
        return [pscustomobject]@{ Reason = "local_process_failure"; Document = $null }
    }
    if ($null -ne $Transport.LocalFailureReason) {
        return [pscustomobject]@{ Reason = "transport_internal_failure"; Document = $null }
    }
    if ($Transport.TimedOut) { return [pscustomobject]@{ Reason = "transport_timeout"; Document = $null } }
    if ($Transport.OutputLimitExceeded -or $Transport.StdoutBytes.Length -gt $Transport.MaximumOutputBytes -or $Transport.StderrBytes.Length -gt $Transport.MaximumOutputBytes) {
        return [pscustomobject]@{ Reason = "output_oversized"; Document = $null }
    }
    if ($Transport.ExitCode -ne 0 -and ($Transport.ExitCode -lt 64 -or $Transport.ExitCode -gt 74)) {
        return [pscustomobject]@{ Reason = "unknown_remote_outcome"; Document = $null }
    }
    $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    try {
        $StdoutText = $StrictUtf8.GetString([byte[]]$Transport.StdoutBytes)
        $StderrText = $StrictUtf8.GetString([byte[]]$Transport.StderrBytes)
    } catch {
        return [pscustomobject]@{ Reason = "invalid_utf8"; Document = $null }
    }
    if ($StdoutText.Contains("`r") -or $StderrText.Contains("`r")) {
        return [pscustomobject]@{ Reason = "crlf_corruption"; Document = $null }
    }
    if (-not [string]::IsNullOrEmpty($StderrText) -or -not $StdoutText.EndsWith("`n")) {
        return [pscustomobject]@{ Reason = "extra_output"; Document = $null }
    }
    $Document = $StdoutText.Substring(0, $StdoutText.Length - 1)
    if ($Document.Contains("`n") -or [string]::IsNullOrEmpty($Document)) {
        return [pscustomobject]@{ Reason = "extra_output"; Document = $null }
    }
    if ($Transport.ExitCode -eq 0) {
        try { [void]($Document | ConvertFrom-Json -ErrorAction Stop) }
        catch { return [pscustomobject]@{ Reason = "schema_validation_failed"; Document = $null } }
        return [pscustomobject]@{ Reason = "success"; Document = $Document }
    }
    $Pattern = '^AMN2_PHASE13_AWG3_PREFLIGHT_FAILURE_V1\|stage=([a-z0-9_]+)\|exit=([0-9]+)$'
    $Match = [regex]::Match($Document, $Pattern)
    if (-not $Match.Success -or $script:AllowedRemoteFailureStages -cnotcontains $Match.Groups[1].Value -or [int]$Match.Groups[2].Value -ne $Transport.ExitCode) {
        return [pscustomobject]@{ Reason = "extra_output"; Document = $null }
    }
    return [pscustomobject]@{ Reason = "collector_failure"; Document = $Document }
}

function Invoke-Phase13OneSshTransport {
    param(
        [Parameter(Mandatory = $true)][string]$SshExecutable,
        [Parameter(Mandatory = $true)][string[]]$SshArguments,
        [Parameter(Mandatory = $true)][byte[]]$CollectorBytes,
        [int]$TimeoutMilliseconds = 15000,
        [int]$MaximumOutputBytes = 65536
    )
    $Transport = $null
    try {
        try {
            $Transport = Invoke-BoundedTransport -Executable $SshExecutable -Arguments $SshArguments -InputBytes $CollectorBytes -TimeoutMilliseconds $TimeoutMilliseconds -MaximumOutputBytes $MaximumOutputBytes -MaximumInputBytes 1048576
            $Envelope = ConvertFrom-BoundedCollectorEnvelope -Transport $Transport
            return [pscustomobject]@{
                Reason = $Envelope.Reason
                Document = $Envelope.Document
                ExitCode = $Transport.ExitCode
            }
        } catch {
            return [pscustomobject]@{
                Reason = "transport_internal_failure"
                Document = $null
                ExitCode = -1
            }
        }
    } finally {
        if ($null -ne $Transport) {
            if ($null -ne $Transport.StdoutBytes) {
                [Array]::Clear($Transport.StdoutBytes, 0, $Transport.StdoutBytes.Length)
            }
            if ($null -ne $Transport.StderrBytes) {
                [Array]::Clear($Transport.StderrBytes, 0, $Transport.StderrBytes.Length)
            }
        }
        $Transport = $null
    }
}

function Test-Phase13EvidenceSecretSafe {
    param(
        [Parameter(Mandatory = $true)][byte[]]$EvidenceBytes,
        [string[]]$SensitiveValues = @()
    )
    $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    try { $Text = $StrictUtf8.GetString($EvidenceBytes) }
    catch { return $false }
    if ([regex]::IsMatch($Text, '(?i)BEGIN [^-\r\n]*PRIVATE KEY|PrivateKey"?\s*[=:]|PresharedKey"?\s*[=:]|HeaderProtectionKey"?\s*[=:]|vpn://|password"?\s*[=:]|token"?\s*[=:]')) {
        return $false
    }
    foreach ($Value in @($SensitiveValues)) {
        if (-not [string]::IsNullOrEmpty($Value) -and $Text.Contains($Value)) {
            return $false
        }
    }
    return $true
}

function Resolve-Phase13TransportFailure {
    param([Parameter(Mandatory = $true)]$TransportResult)

    if ($TransportResult.Reason -ceq "collector_failure") {
        $ExitCode = if ($TransportResult.ExitCode -ge 64 -and $TransportResult.ExitCode -le 74) {
            [int]$TransportResult.ExitCode
        }
        else {
            67
        }
        return [pscustomobject]@{
            Stage = "collector"
            ReasonCode = "observation_ambiguous"
            TransportSubreason = "not_applicable"
            ExitCode = $ExitCode
        }
    }

    if ($TransportResult.Reason -cin @("schema_validation_failed", "invalid_utf8", "crlf_corruption", "extra_output")) {
        return [pscustomobject]@{
            Stage = "schema_validation"
            ReasonCode = "schema_validation_failed"
            TransportSubreason = "not_applicable"
            ExitCode = 68
        }
    }

    $TransportSubreason = switch -CaseSensitive ($TransportResult.Reason) {
        "transport_timeout" { "timeout"; break }
        "output_oversized" { "output_oversized"; break }
        "unknown_remote_outcome" { "ssh_exit_unclassified"; break }
        "local_process_failure" { "local_process_failure"; break }
        default { "transport_internal_failure" }
    }

    return [pscustomobject]@{
        Stage = "transport"
        ReasonCode = "observation_ambiguous"
        TransportSubreason = $TransportSubreason
        ExitCode = 67
    }
}

function Test-EvidenceContract {
    param(
        [Parameter(Mandatory = $true)][string]$PythonExecutable,
        [Parameter(Mandatory = $true)][string]$ContractPath,
        [Parameter(Mandatory = $true)][string]$ManifestPath,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][byte[]]$EvidenceBytes
    )
    foreach ($RequiredPath in @($PythonExecutable, $ContractPath, $ManifestPath)) {
        $Item = Get-Item -LiteralPath $RequiredPath -Force -ErrorAction Stop
        if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            return $false
        }
    }
    $ContractDirectory = Split-Path -Parent $ContractPath
    $PythonCode = "sys=__import__('sys');Path=__import__('pathlib',fromlist=['Path']).Path;sys.path.insert(0,sys.argv[1]);c=__import__('phase13_awg3_preflight_contract');raw_m=Path(sys.argv[2]).read_bytes();m=c.load_json_object_strict(raw_m,label='manifest');c.validate_manifest(m,artifact_root=Path(sys.argv[3]));raw=sys.stdin.buffer.read();e=c.load_json_object_strict(raw,label='evidence');c.validate_success_evidence(e,manifest=m);a={Path(x['path']).name:x['sha256'] for x in m['artifacts']};assert e['runner_sha256']==a['phase13_spain_awg3_readonly_preflight_ssh_runner.ps1'];assert e['collector_sha256']==a['phase13_spain_awg3_readonly_preflight_remote.sh'];assert e['schema_sha256']==a['evidence.schema.json'];sys.stdout.buffer.write(b'passed\n')"
    try {
        $Validation = Invoke-BoundedTransport -Executable $PythonExecutable -Arguments @("-I", "-B", "-c", $PythonCode, $ContractDirectory, $ManifestPath, $RepositoryRoot) -InputBytes $EvidenceBytes -TimeoutMilliseconds 5000 -MaximumOutputBytes 4096
    } catch {
        return $false
    }
    if ($Validation.TimedOut -or $Validation.ExitCode -ne 0 -or $Validation.StderrBytes.Length -ne 0) {
        return $false
    }
    $StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    try { $Text = $StrictUtf8.GetString([byte[]]$Validation.StdoutBytes) }
    catch { return $false }
    return $Text -ceq "passed`n"
}

function Write-SanitizedFailureCreateNew {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$OutcomeId,
        [Parameter(Mandatory = $true)][string]$ManifestSha256,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$ReasonCode,
        [Parameter(Mandatory = $true)][string]$TransportSubreason
    )
    $AllowedStages = @(
        "argument_validation", "checksum_verification", "approval_validation",
        "private_root_validation", "outcome_claim", "trust_binding", "transport",
        "collector", "schema_validation"
    )
    $AllowedReasons = @(
        "udp_port_conflict", "interface_conflict", "vpn_cidr_overlap",
        "container_cidr_overlap", "container_name_conflict", "service_name_conflict",
        "state_path_conflict", "runtime_capability_unavailable", "awg2_equality_mismatch",
        "foreign_equality_mismatch", "observation_ambiguous", "artifact_checksum_mismatch",
        "outcome_replay", "schema_validation_failed", "secret_pattern_detected"
    )
    $TransportSubreasons = @(
        "timeout", "output_oversized", "ssh_exit_unclassified",
        "local_process_failure", "transport_internal_failure"
    )
    if ($Stage -cnotin $AllowedStages -or $ReasonCode -cnotin $AllowedReasons) {
        throw "Failure receipt contract rejected."
    }
    if ($Stage -ceq "transport") {
        if ($ReasonCode -cne "observation_ambiguous" -or $TransportSubreason -cnotin $TransportSubreasons) {
            throw "Failure receipt contract rejected."
        }
    }
    elseif ($TransportSubreason -cne "not_applicable") {
        throw "Failure receipt contract rejected."
    }
    $Safety = [ordered]@{
        container_action_attempted = $false
        firewall_action_attempted = $false
        mutation_attempted = $false
        raw_output_persisted = $false
        raw_peer_identifiers_emitted = $false
        remote_file_written = $false
        secret_bearing_config_accessed = $false
        service_action_attempted = $false
    }
    $Receipt = [ordered]@{
        checked_at = [DateTimeOffset]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        decision = "stop"
        manifest_sha256 = $ManifestSha256
        outcome_id = $OutcomeId
        reason_code = $ReasonCode
        safety_receipt = $Safety
        schema = "amn2.phase13.awg3-readonly-preflight-failure.v2"
        source_head = $script:SourceHead
        stage = $Stage
        transport_subreason = $TransportSubreason
    }
    $Json = ($Receipt | ConvertTo-Json -Depth 8 -Compress) + "`n"
    Write-BytesCreateNew -Path $Path -Bytes ((New-Object Text.UTF8Encoding($false)).GetBytes($Json))
}

function Write-RunnerFailureLine {
    param([string]$Stage, [string]$Reason)
    [Console]::Out.WriteLine("AMN2_PHASE13_AWG3_RUNNER_FAILURE_V1|stage=$Stage|reason=$Reason")
}

function Invoke-RunnerMain {
    param([string]$Mode, [string]$OutcomeId, [string]$Approval)
    try { Assert-OutcomeId -Value $OutcomeId }
    catch { Write-RunnerFailureLine "argument_validation" "schema_validation_failed"; return 64 }

    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
    $PackageRoot = Join-Path $RepositoryRoot "packaging\phase13-awg3-preflight"
    $ManifestPath = Join-Path $PackageRoot "phase13-awg3-preflight-manifest.json"
    try {
        $ManifestDocument = Read-CanonicalManifest -Path $ManifestPath
        $Manifest = $ManifestDocument.Value
        Assert-ManifestContract -Manifest $Manifest -ExpectedOutcomeId $OutcomeId
    } catch {
        if ($_.Exception.Message -like '*expired*') {
            Write-RunnerFailureLine "outcome_claim" "outcome_replay"
            return 66
        }
        Write-RunnerFailureLine "checksum_verification" "artifact_checksum_mismatch"
        return 65
    }
    try { Assert-ManifestArtifacts -Manifest $Manifest -RepositoryRoot $PackageRoot }
    catch { Write-RunnerFailureLine "checksum_verification" "artifact_checksum_mismatch"; return 65 }

    $ManifestSha = ([BitConverter]::ToString((New-Object Security.Cryptography.SHA256Managed).ComputeHash($ManifestDocument.Bytes))).Replace('-', '').ToLowerInvariant()
    try {
        $RunnerSha = Get-ManifestArtifactSha -Manifest $Manifest -FileName "phase13_spain_awg3_readonly_preflight_ssh_runner.ps1"
        $CollectorSha = Get-ManifestArtifactSha -Manifest $Manifest -FileName "phase13_spain_awg3_readonly_preflight_remote.sh"
        $SchemaSha = Get-ManifestArtifactSha -Manifest $Manifest -FileName "evidence.schema.json"
        $FoundationSha = Get-ManifestArtifactSha -Manifest $Manifest -FileName "phase12-equality-foundation.json"
        if ((Get-Sha256Hex -Path $PSCommandPath) -cne $RunnerSha) {
            throw "Executing runner checksum mismatch."
        }
    } catch { Write-RunnerFailureLine "checksum_verification" "artifact_checksum_mismatch"; return 65 }
    $ExpectedApproval = New-ExactApprovalPhrase -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -RunnerSha256 $RunnerSha -CollectorSha256 $CollectorSha -SchemaSha256 $SchemaSha -FoundationSha256 $FoundationSha
    if ([string]::IsNullOrEmpty($Approval)) {
        [Console]::Out.WriteLine($ExpectedApproval)
        return 64
    }
    if (-not [string]::Equals($Approval, $ExpectedApproval, [StringComparison]::Ordinal)) {
        Write-RunnerFailureLine "approval_validation" "schema_validation_failed"
        return 64
    }

    $LocalAppData = [Environment]::GetFolderPath('LocalApplicationData')
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $PrivateArtifactsRoot = Join-Path $LocalAppData "AMN2\private-artifacts"
    try { Assert-PrivatePath -Path $PrivateArtifactsRoot -ExpectedOwnerSid $CurrentSid }
    catch { Write-RunnerFailureLine "private_root_validation" "observation_ambiguous"; return 72 }
    $OutcomeRoot = Join-Path $PrivateArtifactsRoot "phase13-awg3-preflight\outcomes"
    try {
        $ClaimPath = New-Phase13OutcomeClaim -OutcomeRoot $OutcomeRoot -OutcomeId $OutcomeId -OwnerSid $CurrentSid -ManifestSha256 $ManifestSha -RunnerSha256 $RunnerSha -CollectorSha256 $CollectorSha -TargetRole "spain-primary"
    } catch {
        Write-RunnerFailureLine "outcome_claim" "outcome_replay"
        return 66
    }

    $TrustRoot = Join-Path $PrivateArtifactsRoot "post-release\spain-migration\$($script:TrustedBundleRunId)"
    $BindingPath = Join-Path $TrustRoot "target.env"
    $KeyPath = Join-Path $TrustRoot "id_ed25519_spain"
    $PublicKeyPath = "$KeyPath.pub"
    $KnownHostsPath = Join-Path $TrustRoot "known_hosts_spain"
    $SshExecutable = "C:\Windows\System32\OpenSSH\ssh.exe"
    $SshKeygenExecutable = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"
    try {
        Assert-Phase13LocalExecutable -Path $SshExecutable
        Assert-Phase13LocalExecutable -Path $SshKeygenExecutable
        $Binding = Read-Phase13TrustBinding -TrustRoot $TrustRoot -BindingPath $BindingPath -KeyPath $KeyPath -ExpectedOwnerSid $CurrentSid
        Assert-Phase13DedicatedEd25519KeyPair -PrivateKeyPath $KeyPath -PublicKeyPath $PublicKeyPath -SshKeygenExecutable $SshKeygenExecutable -ExpectedOwnerSid $CurrentSid
        Assert-Phase13VerifiedHostPin -KnownHostsPath $KnownHostsPath -Binding $Binding -SshKeygenExecutable $SshKeygenExecutable -ExpectedOwnerSid $CurrentSid
    } catch {
        Write-RunnerFailureLine "trust_binding" "runtime_capability_unavailable"
        return 73
    }

    $CollectorPath = Join-Path $PackageRoot "phase13_spain_awg3_readonly_preflight_remote.sh"
    $ContractPath = Join-Path $RepositoryRoot "scripts\phase13_awg3_preflight_contract.py"
    $PythonExecutable = Join-Path $RepositoryRoot "worktrees\amn2-phase13-awg2-awg3-local\.venv\Scripts\python.exe"
    $OutcomeDirectory = Split-Path -Parent $ClaimPath
    $EvidencePath = Join-Path $OutcomeDirectory "preflight-evidence.json"
    $FailurePath = Join-Path $OutcomeDirectory "preflight-failure.json"
    $CollectorBytes = $null
    $SshArguments = $null
    $TransportResult = $null
    try {
        $CollectorBytes = Read-StrictUtf8Bytes -Path $CollectorPath -MaximumBytes 1048576
        $SshArguments = New-Phase13SshArguments -Binding $Binding -KnownHostsPath $KnownHostsPath -KeyPath $KeyPath -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -RunnerSha256 $RunnerSha -CollectorSha256 $CollectorSha -SchemaSha256 $SchemaSha -FoundationSha256 $FoundationSha
        $TransportResult = Invoke-Phase13OneSshTransport -SshExecutable $SshExecutable -SshArguments $SshArguments -CollectorBytes $CollectorBytes -TimeoutMilliseconds 15000 -MaximumOutputBytes 65536
    } catch {
        try {
            Write-SanitizedFailureCreateNew -Path $FailurePath -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -Stage "transport" -ReasonCode "observation_ambiguous" -TransportSubreason "transport_internal_failure"
        } catch {
            Write-RunnerFailureLine "private_root_validation" "observation_ambiguous"
            return 75
        }
        Write-RunnerFailureLine "transport" "observation_ambiguous"
        return 67
    } finally {
        if ($null -ne $CollectorBytes) {
            [Array]::Clear($CollectorBytes, 0, $CollectorBytes.Length)
        }
        $CollectorBytes = $null
        $SshArguments = $null
    }

    if ($TransportResult.Reason -cne "success") {
        $Failure = Resolve-Phase13TransportFailure -TransportResult $TransportResult
        $TransportResult = $null
        try {
            Write-SanitizedFailureCreateNew -Path $FailurePath -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -Stage $Failure.Stage -ReasonCode $Failure.ReasonCode -TransportSubreason $Failure.TransportSubreason
        } catch {
            Write-RunnerFailureLine "private_root_validation" "observation_ambiguous"
            return 75
        }
        Write-RunnerFailureLine $Failure.Stage $Failure.ReasonCode
        return $Failure.ExitCode
    }

    $EvidenceBytes = $script:Utf8NoBom.GetBytes($TransportResult.Document + "`n")
    $TransportResult = $null
    $SensitiveValues = @(
        $Binding["TARGET_HOST"],
        $Binding["TARGET_USER"],
        $Binding["EXPECTED_HOST_KEY_SHA256"],
        $KeyPath,
        $PublicKeyPath,
        $KnownHostsPath
    )
    try {
        if (-not (Test-EvidenceContract -PythonExecutable $PythonExecutable -ContractPath $ContractPath -ManifestPath $ManifestPath -RepositoryRoot $PackageRoot -EvidenceBytes $EvidenceBytes)) {
            throw "Evidence contract rejected."
        }
        if (-not (Test-Phase13EvidenceSecretSafe -EvidenceBytes $EvidenceBytes -SensitiveValues $SensitiveValues)) {
            Write-SanitizedFailureCreateNew -Path $FailurePath -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -Stage "schema_validation" -ReasonCode "secret_pattern_detected" -TransportSubreason "not_applicable"
            Write-RunnerFailureLine "schema_validation" "secret_pattern_detected"
            return 74
        }
        Write-BytesCreateNew -Path $EvidencePath -Bytes $EvidenceBytes
        $EvidenceSha256 = Get-Sha256Hex -Path $EvidencePath
    } catch {
        if (-not (Test-Path -LiteralPath $FailurePath)) {
            try {
                Write-SanitizedFailureCreateNew -Path $FailurePath -OutcomeId $OutcomeId -ManifestSha256 $ManifestSha -Stage "schema_validation" -ReasonCode "schema_validation_failed" -TransportSubreason "not_applicable"
            } catch {
                Write-RunnerFailureLine "private_root_validation" "observation_ambiguous"
                return 75
            }
        }
        Write-RunnerFailureLine "schema_validation" "schema_validation_failed"
        return 68
    } finally {
        [Array]::Clear($EvidenceBytes, 0, $EvidenceBytes.Length)
        $EvidenceBytes = $null
        $SensitiveValues = $null
        $Binding = $null
    }
    [Console]::Out.WriteLine("AMN2_PHASE13_AWG3_RUNNER_SUCCESS_V1|outcome_id=$OutcomeId|evidence_sha256=$EvidenceSha256")
    return 0
}

if ($MyInvocation.InvocationName -ne '.') {
    $ExitCode = Invoke-RunnerMain -Mode $Mode -OutcomeId $OutcomeId -Approval $Approval
    exit $ExitCode
}
