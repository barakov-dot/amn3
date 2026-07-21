[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Security") -ErrorAction Stop
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Utility") -ErrorAction Stop

$expectedRemoteScriptSha = "70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A"
$expectedFingerprintSetSha = "2B4794DC286334B9D08F155A22C59571F351468800A69897D1204BB3A27C50EC"
$expectedFingerprintSetBytes = 48205
$expectedPackageResourcePlanSha = "29BE4B5E301EDBDEAA39B2596833D4A850BEC883C75A2CE3738D51DB13846264"
$run009EvidenceSha = "8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8"
$run009RawOrderFingerprintSha = "E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5"
$run009FirewallBackend = "nft"
$run009FirewallRulesSha = "35ED9383AE9E73268E3D1AB7F57612BC60EA59C0531D6A96372E5F3731883D00"
$run009FirewallRuleCount = 129
$trustedBundleRunId = "spain-fresh-20260720-001"
$expectedRunId = "spain-resource-confirmation-20260721-008"
$sourceRevision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
$actualRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$RepositoryRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$PackageResourcePlanPath = Join-Path $RepositoryRoot "packaging\phase12-spain\resource-plan.json"
if (-not (Test-Path -LiteralPath $PackageResourcePlanPath -PathType Leaf) -or
    (Get-FileHash -LiteralPath $PackageResourcePlanPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedPackageResourcePlanSha) {
    throw "Reviewed package resource plan checksum mismatch."
}

$RemoteScriptPath = Join-Path $PSScriptRoot "phase12_spain_resource_confirmation_remote.sh"
if (-not (Test-Path -LiteralPath $RemoteScriptPath -PathType Leaf)) {
    throw "Reviewed resource-confirmation collector is missing."
}
$actualRemoteScriptSha = (Get-FileHash -LiteralPath $RemoteScriptPath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualRemoteScriptSha -cne $expectedRemoteScriptSha) {
    throw "Reviewed resource-confirmation collector checksum mismatch."
}
$RemoteScriptBytes = [IO.File]::ReadAllBytes($RemoteScriptPath)
if ($RemoteScriptBytes.Length -lt 1 -or $RemoteScriptBytes.Length -gt 1048576) {
    [Array]::Clear($RemoteScriptBytes, 0, $RemoteScriptBytes.Length)
    throw "Reviewed resource-confirmation collector length is unsafe."
}
$StrictUtf8 = New-Object Text.UTF8Encoding($false, $true)
[void]$StrictUtf8.GetString($RemoteScriptBytes)

$LocalAppDataRoot = [Environment]::GetFolderPath('LocalApplicationData')
if ([string]::IsNullOrWhiteSpace($LocalAppDataRoot)) {
    throw "Local private-state root is unavailable."
}
$Amn2PrivateRoot = Join-Path $LocalAppDataRoot "AMN2"
$PrivateArtifactsRoot = Join-Path $Amn2PrivateRoot "private-artifacts"
$PostReleaseArtifactRoot = Join-Path $PrivateArtifactsRoot "post-release"
$ArtifactRoot = Join-Path $PostReleaseArtifactRoot "spain-migration"
$TrustDirectory = Join-Path $ArtifactRoot $trustedBundleRunId
$RunDirectory = Join-Path $ArtifactRoot $expectedRunId
$BindingPath = Join-Path $TrustDirectory "target.env"
$KeyPath = Join-Path $TrustDirectory "id_ed25519_spain"
$PublicKeyPath = "$KeyPath.pub"
$KnownHostsPath = Join-Path $TrustDirectory "known_hosts_spain"
$OutcomeClaimPath = Join-Path $RunDirectory "resource-confirmation-outcome.claim"
$EvidencePath = Join-Path $RunDirectory "resource-confirmation-evidence.json"
$ReceiptPath = Join-Path $RunDirectory "resource-confirmation-receipt.json"
$SshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$SshKeygenExe = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"

function Assert-ExactProperties([object]$Object, [string[]]$Expected, [string]$Context) {
    if ($null -eq $Object) {
        throw "$Context is missing."
    }
    $Actual = @($Object.PSObject.Properties.Name)
    if ($Actual.Count -ne $Expected.Count) {
        throw "$Context property count mismatch."
    }
    foreach ($Name in $Expected) {
        if ($Name -cnotin $Actual) {
            throw "$Context property set mismatch."
        }
    }
}

function Assert-CanonicalJsonEncoding([string]$RawText) {
    try { $Parsed = $RawText | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "Resource-confirmation stdout is not exact JSON." }
    $Canonical = $Parsed | ConvertTo-Json -Depth 64 -Compress
    if ($Canonical -cne $RawText) {
        throw "Resource-confirmation JSON is non-canonical or contains duplicate keys."
    }
    return $Parsed
}

function Assert-ResourceConfirmationSchema([object]$Evidence) {
    Assert-ExactProperties $Evidence @(
        "schema", "mode", "host_identity", "platform", "capacity", "candidates",
        "listening_sockets", "network_state", "systemd", "cgroup_diagnostics", "firewall",
        "unrelated_service_fingerprint"
    ) "evidence"
    if ($Evidence.schema -cne "amn2.phase12-spain-resource-confirmation.v1" -or
        $Evidence.mode -cne "read_only_resource_confirmation") {
        throw "Resource-confirmation schema identity mismatch."
    }
    Assert-ExactProperties $Evidence.host_identity @("machine_id_sha256", "boot_id_sha256") "host_identity"
    foreach ($Hash in @($Evidence.host_identity.machine_id_sha256, $Evidence.host_identity.boot_id_sha256)) {
        if ($Hash -cnotmatch '^[a-f0-9]{64}$') { throw "Host identity hash format mismatch." }
    }
    Assert-ExactProperties $Evidence.platform @("kernel", "os_release", "architecture", "python3", "glibc_version") "platform"
    Assert-ExactProperties $Evidence.platform.kernel @("system", "release") "platform.kernel"
    Assert-ExactProperties $Evidence.platform.os_release @("id", "version_id") "platform.os_release"
    Assert-ExactProperties $Evidence.platform.python3 @("version", "soabi") "platform.python3"
    if ($Evidence.platform.kernel.system -cne "Linux" -or $Evidence.platform.architecture -cne "x86_64" -or
        $Evidence.platform.python3.version -cnotmatch '^[0-9]+\.[0-9]+\.[0-9]+$' -or
        [string]::IsNullOrWhiteSpace($Evidence.platform.python3.soabi)) {
        throw "Platform scalar value mismatch."
    }
    Assert-ExactProperties $Evidence.capacity @("mem_available_bytes", "filesystems") "capacity"
    foreach ($Filesystem in @($Evidence.capacity.filesystems)) {
        Assert-ExactProperties $Filesystem @("path", "available_bytes", "available_inodes") "capacity.filesystem"
    }
    if ((@($Evidence.capacity.filesystems.path) -join '|') -cne '/|/opt|/etc|/var|/run') {
        throw "Filesystem candidate list mismatch."
    }
    Assert-ExactProperties $Evidence.candidates @("paths", "identities", "units", "docker", "network", "sockets", "runtime_directories") "candidates"
    foreach ($Path in @($Evidence.candidates.paths)) {
        Assert-ExactProperties $Path @("path", "exists") "candidates.path"
    }
    if ((@($Evidence.candidates.paths.path) -join '|') -cne '/opt/amn2-spain-package|/opt/amn2-spain|/etc/amn2-spain|/var/lib/amn2-spain|/var/lib/amn2-spain-docker|/var/lib/amn2-spain-phase12-audit') {
        throw "Candidate path list mismatch."
    }
    if (@($Evidence.candidates.paths | Where-Object { $_.exists -isnot [bool] }).Count -ne 0) {
        throw "Candidate path observation type mismatch."
    }
    Assert-ExactProperties $Evidence.candidates.identities @(
        "user_name", "user_exists", "user_id", "uid_exists",
        "group_name", "group_exists", "group_id", "gid_exists"
    ) "candidates.identities"
    if ($Evidence.candidates.identities.user_name -cne "amn2-spain" -or
        $Evidence.candidates.identities.user_id -ne 61212 -or
        $Evidence.candidates.identities.group_name -cne "amn2-spain" -or
        $Evidence.candidates.identities.group_id -ne 61212 -or
        $Evidence.candidates.identities.user_exists -isnot [bool] -or
        $Evidence.candidates.identities.uid_exists -isnot [bool] -or
        $Evidence.candidates.identities.group_exists -isnot [bool] -or
        $Evidence.candidates.identities.gid_exists -isnot [bool]) {
        throw "Candidate identity observation mismatch."
    }
    foreach ($Unit in @($Evidence.candidates.units)) {
        Assert-ExactProperties $Unit @("name", "exists") "candidates.unit"
    }
    if ((@($Evidence.candidates.units.name) -join '|') -cne 'amn2-spain-web.service|amn2-spain-bot.service|amn2-spain-docker.service|amn2-spain-network.service') {
        throw "Candidate unit list mismatch."
    }
    if (@($Evidence.candidates.units | Where-Object { $_.exists -isnot [bool] }).Count -ne 0) {
        throw "Candidate unit observation type mismatch."
    }
    Assert-ExactProperties $Evidence.candidates.docker @(
        "binary_present", "potential_socket_present", "daemon_process_present", "observation_safe",
        "container_name", "container_exists", "container_collision_unknown",
        "network_name", "network_exists", "network_collision_unknown"
    ) "candidates.docker"
    $DockerObservationBooleans = @(
        $Evidence.candidates.docker.binary_present,
        $Evidence.candidates.docker.potential_socket_present,
        $Evidence.candidates.docker.daemon_process_present,
        $Evidence.candidates.docker.observation_safe,
        $Evidence.candidates.docker.container_exists,
        $Evidence.candidates.docker.container_collision_unknown,
        $Evidence.candidates.docker.network_exists,
        $Evidence.candidates.docker.network_collision_unknown
    )
    if ($Evidence.candidates.docker.container_name -cne "amn2-spain-awg" -or
        $Evidence.candidates.docker.network_name -cne "amn2-spain-net" -or
        @($DockerObservationBooleans | Where-Object { $_ -isnot [bool] }).Count -ne 0) {
        throw "Docker observation contract mismatch."
    }
    Assert-ExactProperties $Evidence.candidates.network @("bridge_name", "bridge_exists", "interface_name", "interface_exists") "candidates.network"
    if ($Evidence.candidates.network.bridge_name -cne "amn2spbr0" -or
        $Evidence.candidates.network.interface_name -cne "awgsp0" -or
        $Evidence.candidates.network.bridge_exists -isnot [bool] -or
        $Evidence.candidates.network.interface_exists -isnot [bool]) {
        throw "Candidate network-link observation mismatch."
    }
    foreach ($Socket in @($Evidence.candidates.sockets)) {
        Assert-ExactProperties $Socket @("path", "exists") "candidates.socket"
    }
    if (@($Evidence.candidates.sockets).Count -ne 1 -or
        $Evidence.candidates.sockets[0].path -cne "/run/amn2-spain-docker/docker.sock" -or
        $Evidence.candidates.sockets[0].exists -isnot [bool]) {
        throw "Candidate socket observation mismatch."
    }
    foreach ($Directory in @($Evidence.candidates.runtime_directories)) {
        Assert-ExactProperties $Directory @("path", "exists") "candidates.runtime_directory"
    }
    if (@($Evidence.candidates.runtime_directories).Count -ne 1 -or
        $Evidence.candidates.runtime_directories[0].path -cne "/run/amn2-spain-docker" -or
        $Evidence.candidates.runtime_directories[0].exists -isnot [bool]) {
        throw "Candidate runtime-directory observation mismatch."
    }
    foreach ($Listener in @($Evidence.listening_sockets)) {
        Assert-ExactProperties $Listener @("protocol", "address", "port") "listening_socket"
        if ($Listener.protocol -cnotin @("tcp", "udp") -or $Listener.port -lt 1 -or $Listener.port -gt 65535) {
            throw "Listening socket scalar mismatch."
        }
    }
    Assert-ExactProperties $Evidence.network_state @("addresses", "routes") "network_state"
    foreach ($Address in @($Evidence.network_state.addresses)) {
        Assert-ExactProperties $Address @("interface", "family", "address", "prefix_length", "scope") "network_state.address"
    }
    foreach ($Route in @($Evidence.network_state.routes)) {
        Assert-ExactProperties $Route @("family", "destination", "gateway", "interface", "table", "protocol", "scope", "type", "multipath") "network_state.route"
        if ($Route.family -cnotin @("inet", "inet6")) { throw "Route family mismatch." }
        foreach ($Hop in @($Route.multipath)) {
            Assert-ExactProperties $Hop @("gateway", "interface", "weight") "network_state.route.multipath"
        }
    }
    Assert-ExactProperties $Evidence.systemd @("present", "unit_count") "systemd"
    $CgroupDiagnostics = @($Evidence.cgroup_diagnostics)
    if ($CgroupDiagnostics.Count -ne 148) { throw "Cgroup diagnostic count mismatch." }
    $CgroupSeen = @{}
    foreach ($Diagnostic in $CgroupDiagnostics) {
        Assert-ExactProperties $Diagnostic @("unit_sha256", "descendant_pid_count", "pid_set_stable") "cgroup_diagnostic"
        if ($Diagnostic.unit_sha256 -cnotmatch '^[a-f0-9]{64}$' -or
            $Diagnostic.descendant_pid_count -lt 0 -or $Diagnostic.pid_set_stable -ne $true -or
            $CgroupSeen.ContainsKey($Diagnostic.unit_sha256)) {
            throw "Cgroup diagnostic scalar or identity mismatch."
        }
        $CgroupSeen[$Diagnostic.unit_sha256] = $true
    }
    Assert-ExactProperties $Evidence.firewall @(
        "backend", "raw_sha256", "raw_rule_count", "structured_snapshot_sha256",
        "semantic_sha256", "stability_observations", "stable", "structured_snapshot"
    ) "firewall"
    Assert-ExactProperties $Evidence.firewall.structured_snapshot @("nftables") "firewall.structured_snapshot"
    if ($Evidence.firewall.backend -cne "nft" -or $Evidence.firewall.stability_observations -ne 2 -or
        $Evidence.firewall.stable -ne $true -or
        $Evidence.firewall.raw_sha256 -cnotmatch '^[a-f0-9]{64}$' -or
        $Evidence.firewall.structured_snapshot_sha256 -cnotmatch '^[a-f0-9]{64}$' -or
        $Evidence.firewall.semantic_sha256 -cnotmatch '^[a-f0-9]{64}$') {
        throw "Firewall observation contract mismatch."
    }
    $Fingerprint = @($Evidence.unrelated_service_fingerprint)
    if ($Fingerprint.Count -ne 148) {
        throw "Unrelated-service fingerprint count mismatch."
    }
    $Seen = @{}
    foreach ($Entry in $Fingerprint) {
        if ($Entry.kind -ceq "unit") {
            Assert-ExactProperties $Entry @("kind", "name_sha256", "image_or_unit_sha256", "active_state", "restart_count", "bound_port_set", "unit_content_status", "bound_port_status") "fingerprint.unit"
        } elseif ($Entry.kind -ceq "container") {
            Assert-ExactProperties $Entry @("kind", "name_sha256", "image_or_unit_sha256", "active_state", "restart_count", "bound_port_set") "fingerprint.container"
        } else {
            throw "Fingerprint kind is not allowlisted."
        }
        if ($Entry.name_sha256 -cnotmatch '^[A-Fa-f0-9]{64}$' -or
            $Entry.image_or_unit_sha256 -cnotmatch '^[A-Fa-f0-9]{64}$') {
            throw "Fingerprint hash format mismatch."
        }
        $Identity = "$($Entry.kind)|$($Entry.name_sha256.ToUpperInvariant())"
        if ($Seen.ContainsKey($Identity)) {
            throw "Duplicate fingerprint identity."
        }
        $Seen[$Identity] = $true
    }
    foreach ($UnitHash in $CgroupSeen.Keys) {
        if (-not $Seen.ContainsKey("unit|$($UnitHash.ToUpperInvariant())")) {
            throw "Cgroup diagnostic is not bound to the run009 unit set."
        }
    }
}

function Get-FingerprintSetReceipt([object[]]$Entries) {
    $Canonical = @()
    foreach ($Entry in @($Entries | Sort-Object @{Expression = { $_.kind }}, @{Expression = { $_.name_sha256 }})) {
        if ($Entry.kind -ceq "unit") {
            $Canonical += [ordered]@{
                active_state = $Entry.active_state
                bound_port_set = @($Entry.bound_port_set)
                bound_port_status = $Entry.bound_port_status
                image_or_unit_sha256 = $Entry.image_or_unit_sha256
                kind = $Entry.kind
                name_sha256 = $Entry.name_sha256
                restart_count = $Entry.restart_count
                unit_content_status = $Entry.unit_content_status
            }
        } else {
            $Canonical += [ordered]@{
                active_state = $Entry.active_state
                bound_port_set = @($Entry.bound_port_set)
                image_or_unit_sha256 = $Entry.image_or_unit_sha256
                kind = $Entry.kind
                name_sha256 = $Entry.name_sha256
                restart_count = $Entry.restart_count
            }
        }
    }
    $Json = ConvertTo-Json -InputObject @($Canonical) -Depth 8 -Compress
    $Bytes = (New-Object Text.UTF8Encoding($false)).GetBytes($Json)
    try {
        $Hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes))
    } catch {
        $Hasher = [Security.Cryptography.SHA256]::Create()
        try { $Hash = ([BitConverter]::ToString($Hasher.ComputeHash($Bytes))).Replace("-", "") }
        finally { $Hasher.Dispose() }
    }
    return [pscustomobject]@{ Sha256 = $Hash; ByteLength = $Bytes.Length }
}

function Assert-FingerprintBaseline([object[]]$Entries, [string]$ExpectedSha, [int]$ExpectedBytes) {
    $Receipt = Get-FingerprintSetReceipt $Entries
    if ($Receipt.Sha256 -cne $ExpectedSha -or $Receipt.ByteLength -ne $ExpectedBytes) {
        throw "Unrelated-service fingerprint set does not equal run009."
    }
    return $Receipt
}

function Assert-CurrentUserOwner([string]$Path) {
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $OwnerSid = (Get-Acl -LiteralPath $Path).GetOwner([Security.Principal.SecurityIdentifier])
    if ($OwnerSid.Value -cne $CurrentSid.Value) { throw "Private artifact owner mismatch." }
}

function Assert-PrivatePath([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required private artifact is missing." }
    Assert-NotReparseFile $Path
    Assert-CurrentUserOwner $Path
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Acl = Get-Acl -LiteralPath $Path
    $Rules = @($Acl.Access)
    if (-not $Acl.AreAccessRulesProtected -or $Rules.Count -ne 1 -or
        $Rules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value -cne $CurrentSid.Value -or
        $Rules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        (($Rules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl)) {
        throw "Private artifact ACL mismatch."
    }
}

function Assert-NotReparseFile([string]$Path) {
    $Item = Get-Item -LiteralPath $Path -Force
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Private artifact must not be a reparse point."
    }
}

function Protect-PrivatePath([string]$Path) {
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Acl = Get-Acl -LiteralPath $Path
    $Acl.SetOwner($CurrentSid)
    $Acl.SetAccessRuleProtection($true, $false)
    foreach ($Rule in @($Acl.Access)) { $Acl.RemoveAccessRuleSpecific($Rule) }
    $OnlyRule = New-Object Security.AccessControl.FileSystemAccessRule(
        $CurrentSid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.InheritanceFlags]::None,
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $Acl.SetAccessRule($OnlyRule)
    Set-Acl -LiteralPath $Path -AclObject $Acl
    Assert-PrivatePath $Path
}

function Assert-NotReparsePoint([string]$Path) {
    $Item = Get-Item -LiteralPath $Path -Force
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Private directory must not be a reparse point."
    }
}

function Assert-PrivateRootChain() {
    Assert-NotReparsePoint $LocalAppDataRoot
    Assert-CurrentUserOwner $LocalAppDataRoot
    foreach ($Path in @($Amn2PrivateRoot, $PrivateArtifactsRoot, $PostReleaseArtifactRoot, $ArtifactRoot, $TrustDirectory)) {
        Assert-NotReparsePoint $Path
        Assert-PrivatePath $Path
    }
}

function Initialize-OutcomeDirectory([string]$Path) {
    Assert-PrivateRootChain
    if (Test-Path -LiteralPath $Path) { throw "Single-use resource-confirmation run already exists." }
    [IO.Directory]::CreateDirectory($Path) | Out-Null
    Assert-NotReparsePoint $Path
    Protect-PrivatePath $Path
}

function New-PrivateFileSecurity() {
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Security = New-Object Security.AccessControl.FileSecurity
    $Security.SetOwner($CurrentSid)
    $Security.SetAccessRuleProtection($true, $false)
    $Rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $CurrentSid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $Security.SetAccessRule($Rule)
    return [Security.AccessControl.FileSecurity]$Security
}

function Write-BytesCreateNew([string]$Path, [byte[]]$Bytes) {
    $Security = New-PrivateFileSecurity
    $Stream = New-Object IO.FileStream(
        $Path,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None,
        4096,
        [IO.FileOptions]::WriteThrough,
        $Security
    )
    try { $Stream.Write($Bytes, 0, $Bytes.Length); $Stream.Flush($true) }
    finally { $Stream.Dispose() }
    Assert-PrivatePath $Path
}

function Write-EvidenceCreateNew([string]$Path, [string]$Json) {
    $Bytes = (New-Object Text.UTF8Encoding($false)).GetBytes("$Json`n")
    try { Write-BytesCreateNew $Path $Bytes }
    finally { [Array]::Clear($Bytes, 0, $Bytes.Length) }
}

function Write-AtomicPrivateJsonCreateNew([string]$Path, [string]$Json) {
    $PendingPath = "$Path.pending"
    if ((Test-Path -LiteralPath $Path) -or (Test-Path -LiteralPath $PendingPath)) {
        throw "Single-use outcome receipt already exists."
    }
    $Bytes = (New-Object Text.UTF8Encoding($false)).GetBytes("$Json`n")
    try {
        Write-BytesCreateNew $PendingPath $Bytes
        Protect-PrivatePath $PendingPath
        [IO.File]::Move($PendingPath, $Path)
        Assert-PrivatePath $Path
    } finally {
        [Array]::Clear($Bytes, 0, $Bytes.Length)
    }
}

function Write-SanitizedOutcomeReceipt(
    [string]$Path,
    [string]$Status,
    [string]$Stage,
    [string]$Reason,
    [string]$ClaimSha,
    [string]$ResourcePlanSha,
    [string[]]$ConflictCodes
) {
    $AllowedStages = @(
        "ssh", "framing", "content", "json", "schema", "fingerprint", "conflict", "persist", "completion",
        "bootstrap", "host_identity", "platform", "capacity", "candidate_inventory", "listeners", "network_state",
        "firewall", "systemd_inventory", "systemd_unit_content", "systemd_cgroup_ports", "render"
    )
    $AllowedReasons = @(
        "SSH_COLLECTION_FAILED", "STDOUT_FRAMING_INVALID", "STDOUT_CONTENT_UNSAFE",
        "JSON_INVALID", "SCHEMA_INVALID", "FINGERPRINT_MISMATCH",
        "CONFLICT_FREE_REQUIRED", "EVIDENCE_PERSIST_FAILED", "OUTCOME_PERSIST_FAILED",
        "UNEXPECTED_POST_CLAIM_FAILURE"
    )
    $AllowedConflictCodes = @(
        "TCP_3031_BIND_CONFLICT", "UDP_30001_BIND_CONFLICT",
        "ADDRESS_OVERLAP_172_29_251_0_28", "ADDRESS_OVERLAP_10_212_12_0_24",
        "ROUTE_OVERLAP_172_29_251_0_28", "ROUTE_OVERLAP_10_212_12_0_24",
        "CANDIDATE_PATH_PRESENT", "CANDIDATE_IDENTITY_PRESENT", "CANDIDATE_UNIT_PRESENT",
        "DOCKER_PRESENCE_OR_UNKNOWN", "CANDIDATE_NETWORK_LINK_PRESENT",
        "CANDIDATE_SOCKET_PRESENT", "CANDIDATE_RUNTIME_DIRECTORY_PRESENT"
    )
    if ($Status -cnotin @("failed", "blocked") -or $Stage -cnotin $AllowedStages -or
        $Reason -cnotin $AllowedReasons -or $ClaimSha -cnotmatch '^[A-F0-9]{64}$' -or
        $ResourcePlanSha -cnotmatch '^[A-F0-9]{64}$') {
        throw "Sanitized outcome receipt value mismatch."
    }
    $SafeCodes = [string[]]@($ConflictCodes | Sort-Object -Unique)
    if (@($SafeCodes | Where-Object { $_ -cnotin $AllowedConflictCodes }).Count -ne 0 -or
        ($Status -ceq "failed" -and $SafeCodes.Count -ne 0) -or
        ($Status -ceq "blocked" -and ($Reason -cne "CONFLICT_FREE_REQUIRED" -or $SafeCodes.Count -eq 0))) {
        throw "Sanitized conflict-code set mismatch."
    }
    $Schema = if ($Status -ceq "blocked") {
        "amn2.phase12-spain-resource-confirmation-blocked-receipt.v1"
    } else {
        "amn2.phase12-spain-resource-confirmation-failure-receipt.v1"
    }
    $Receipt = [ordered]@{
        schema = $Schema
        run_id = $expectedRunId
        status = $Status
        stage = $Stage
        reason = $Reason
        claim_sha256 = $ClaimSha
        resource_plan_sha256 = $ResourcePlanSha
        conflict_free = $false
        conflict_codes = $SafeCodes
        instruction = "USE_NEW_RUN_ID_AND_NEW_EXACT_APPROVAL"
    } | ConvertTo-Json -Depth 8 -Compress
    Write-AtomicPrivateJsonCreateNew $Path $Receipt
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($null -eq $Value) { throw "Native process argument is null." }
    $Builder = [Text.StringBuilder]::new()
    [void]$Builder.Append([char]34)
    $Backslashes = 0
    foreach ($Character in $Value.ToCharArray()) {
        if ([int]$Character -eq 92) { $Backslashes += 1; continue }
        if ([int]$Character -eq 34) {
            [void]$Builder.Append(('\' * (($Backslashes * 2) + 1)))
            [void]$Builder.Append([char]34)
        } else {
            if ($Backslashes -gt 0) { [void]$Builder.Append(('\' * $Backslashes)) }
            [void]$Builder.Append($Character)
        }
        $Backslashes = 0
    }
    if ($Backslashes -gt 0) { [void]$Builder.Append(('\' * ($Backslashes * 2))) }
    [void]$Builder.Append([char]34)
    return $Builder.ToString()
}

function Invoke-SshWithExactInput([string]$FileName, [string[]]$Arguments, [byte[]]$StandardInputBytes) {
    if ($FileName -cne $SshExe) { throw "SSH executable path mismatch." }
    $Info = [Diagnostics.ProcessStartInfo]::new()
    $Info.FileName = $FileName
    $Info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $Info.UseShellExecute = $false
    $Info.CreateNoWindow = $true
    $Info.RedirectStandardInput = $true
    $Info.RedirectStandardOutput = $true
    $Info.RedirectStandardError = $true
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = $Info
    $Stdout = [IO.MemoryStream]::new()
    $Stderr = [IO.MemoryStream]::new()
    try {
        if (-not $Process.Start()) { throw "Trusted OpenSSH client did not start." }
        $StdoutTask = $Process.StandardOutput.BaseStream.CopyToAsync($Stdout)
        $StderrTask = $Process.StandardError.BaseStream.CopyToAsync($Stderr)
        $Process.StandardInput.BaseStream.Write($StandardInputBytes, 0, $StandardInputBytes.Length)
        $Process.StandardInput.BaseStream.Flush()
        $Process.StandardInput.Close()
        $Process.WaitForExit()
        [void]$StdoutTask.GetAwaiter().GetResult()
        [void]$StderrTask.GetAwaiter().GetResult()
        return [pscustomobject]@{
            ExitCode = [int]$Process.ExitCode
            StdoutBytes = $Stdout.ToArray()
            StderrBytes = $Stderr.ToArray()
        }
    } finally {
        $Process.Dispose()
        $Stdout.Dispose()
        $Stderr.Dispose()
    }
}

function Get-SafeRemoteFailureStage([byte[]]$Bytes, [int]$ExitCode) {
    if ($ExitCode -lt 1 -or $ExitCode -gt 255 -or $Bytes.Length -lt 1 -or $Bytes.Length -gt 256) { return "ssh" }
    try { $Text = $StrictUtf8.GetString($Bytes) } catch { return "ssh" }
    $Match = [regex]::Match($Text, '^AMN2_PHASE12_RESOURCE_CONFIRMATION_FAILURE_V1\|stage=(?<stage>bootstrap|host_identity|platform|capacity|candidate_inventory|listeners|network_state|firewall|systemd_inventory|systemd_unit_content|systemd_cgroup_ports|render)\|exit=(?<exit>[0-9]{1,3})\r?\n$')
    if (-not $Match.Success -or [int]$Match.Groups['exit'].Value -ne $ExitCode) { return "ssh" }
    return $Match.Groups['stage'].Value
}

function Read-Binding() {
    Assert-PrivatePath $BindingPath
    $Lines = @(Get-Content -LiteralPath $BindingPath)
    $Names = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($Lines.Count -ne $Names.Count) { throw "Target binding schema mismatch." }
    $Binding = @{}
    for ($Index = 0; $Index -lt $Names.Count; $Index++) {
        $Prefix = "$($Names[$Index])="
        if (-not $Lines[$Index].StartsWith($Prefix, [StringComparison]::Ordinal)) { throw "Target binding order mismatch." }
        $Binding[$Names[$Index]] = $Lines[$Index].Substring($Prefix.Length)
    }
    if ($Binding["TARGET_HOST"] -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or
        $Binding["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$' -or
        $Binding["EXPECTED_HOST_KEY_SHA256"] -notmatch '^SHA256:[A-Za-z0-9+/]{43}$' -or
        $Binding["SSH_KEY_PATH"] -cne $KeyPath) {
        throw "Target binding value mismatch."
    }
    return $Binding
}

function Assert-HostPin([hashtable]$Binding) {
    Assert-PrivatePath $KeyPath
    Assert-PrivatePath $PublicKeyPath
    Assert-PrivatePath $KnownHostsPath
    $HostLines = @(Get-Content -LiteralPath $KnownHostsPath)
    $HostPattern = '^' + [regex]::Escape($Binding['TARGET_HOST']) + ' ssh-ed25519 [A-Za-z0-9+/]+={0,2}$'
    if ($HostLines.Count -ne 1 -or $HostLines[0] -cnotmatch $HostPattern) {
        throw "Independent host pin target mismatch."
    }
    $Observed = @(& $SshKeygenExe -lf $KnownHostsPath 2>$null) -join " "
    if ($LASTEXITCODE -ne 0 -or $Observed -notmatch [regex]::Escape($Binding["EXPECTED_HOST_KEY_SHA256"])) {
        throw "Independent host pin fingerprint mismatch."
    }
    $Derived = @(& $SshKeygenExe -y -f $KeyPath 2>$null)
    $Public = (Get-Content -LiteralPath $PublicKeyPath -Raw).Trim()
    if ($LASTEXITCODE -ne 0 -or $Derived.Count -ne 1 -or
        $Derived[0] -cnotmatch '^ssh-ed25519 [A-Za-z0-9+/]+={0,2}(?: .+)?$' -or
        $Public -cnotmatch '^ssh-ed25519 [A-Za-z0-9+/]+={0,2}(?: .+)?$' -or
        (($Derived[0] -split ' ')[1] -cne (($Public -split ' ')[1]))) {
        throw "Dedicated Ed25519 key pair mismatch."
    }
}

function Get-TextSha256([string]$Value) {
    $Bytes = (New-Object Text.UTF8Encoding($false)).GetBytes($Value)
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($Hasher.ComputeHash($Bytes))).Replace("-", "") }
    finally { $Hasher.Dispose(); [Array]::Clear($Bytes, 0, $Bytes.Length) }
}

function ConvertTo-IPv4UInt32([string]$Address) {
    $Parsed = $null
    if (-not [Net.IPAddress]::TryParse($Address, [ref]$Parsed) -or
        $Parsed.AddressFamily -ne [Net.Sockets.AddressFamily]::InterNetwork) {
        throw "IPv4 observation format mismatch."
    }
    $Bytes = $Parsed.GetAddressBytes()
    return [uint64]$Bytes[0] * 16777216 + [uint64]$Bytes[1] * 65536 +
        [uint64]$Bytes[2] * 256 + [uint64]$Bytes[3]
}

function Test-IPv4NetworkOverlap([string]$ObservedAddress, [int]$ObservedPrefix, [string]$PlannedCidr) {
    if ($ObservedPrefix -lt 0 -or $ObservedPrefix -gt 32 -or
        $PlannedCidr -cnotmatch '^([0-9]{1,3}(?:\.[0-9]{1,3}){3})/([0-9]|[12][0-9]|3[0-2])$') {
        throw "IPv4 prefix observation mismatch."
    }
    $PlannedPrefix = [int]$Matches[2]
    $ObservedValue = ConvertTo-IPv4UInt32 $ObservedAddress
    $PlannedValue = ConvertTo-IPv4UInt32 $Matches[1]
    $ObservedSize = [uint64][Math]::Pow(2, 32 - $ObservedPrefix)
    $PlannedSize = [uint64][Math]::Pow(2, 32 - $PlannedPrefix)
    $ObservedStart = [uint64]([Math]::Floor($ObservedValue / $ObservedSize) * $ObservedSize)
    $PlannedStart = [uint64]([Math]::Floor($PlannedValue / $PlannedSize) * $PlannedSize)
    $ObservedEnd = $ObservedStart + $ObservedSize - 1
    $PlannedEnd = $PlannedStart + $PlannedSize - 1
    return ($ObservedStart -le $PlannedEnd -and $PlannedStart -le $ObservedEnd)
}

function Get-ResourcePlanReceipt() {
    if (-not (Test-Path -LiteralPath $PackageResourcePlanPath -PathType Leaf)) {
        throw "Reviewed package resource plan is missing."
    }
    $ActualSha = (Get-FileHash -LiteralPath $PackageResourcePlanPath -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($ActualSha -cne $expectedPackageResourcePlanSha) {
        throw "Reviewed package resource plan checksum mismatch."
    }
    try { $Plan = Get-Content -Raw -LiteralPath $PackageResourcePlanPath | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "Reviewed package resource plan JSON is invalid." }
    if ($Plan.schema -cne "amn2.spain-resource-plan.v1") {
        throw "Reviewed package resource plan schema mismatch."
    }
    $CanonicalPlan = @(
        "target=$($Plan.target.os_family)|$($Plan.target.os_release)|$($Plan.target.kernel_prefix)|$($Plan.target.architecture)|$($Plan.target.python_major_minor)|$($Plan.target.python_soabi)|$($Plan.target.glibc_minimum)",
        "capacity=$($Plan.capacity_minimums.disk_available_bytes)|$($Plan.capacity_minimums.inodes_available)|$($Plan.capacity_minimums.memory_available_kib)",
        "capacity_filesystems=$(@($Plan.capacity_filesystems) -join ',')",
        "paths=$(@($Plan.resources.paths) -join ',')",
        "retained_paths=$(@($Plan.resources.retained_paths) -join ',')",
        "uids=$(@($Plan.resources.uids) -join ',')",
        "gids=$(@($Plan.resources.gids) -join ',')",
        "units=$(@($Plan.resources.units) -join ',')",
        "listeners=$(@($Plan.listeners) -join ',')",
        "networks=$($Plan.docker_cidr)|$($Plan.vpn_cidr)",
        "firewall=$($Plan.firewall_namespace.family)|$($Plan.firewall_namespace.table)|$(@($Plan.resources.firewall_objects) -join ',')",
        "owned_routes=$(@($Plan.resources.owned_routes) -join ',')",
        "sysctls=$(@($Plan.resources.sysctls) -join ',')"
    ) -join "`n"
    return [pscustomobject]@{
        Sha256 = $ActualSha
        DecisionBasisSha256 = Get-TextSha256 $CanonicalPlan
        Plan = $Plan
    }
}

function Test-VersionAtLeast([string]$Observed, [string]$Minimum) {
    try {
        $ObservedVersion = [version]$Observed
        $MinimumVersion = [version]$Minimum
    } catch {
        return $false
    }
    return $ObservedVersion -ge $MinimumVersion
}

function Get-Run009EvidenceReceipt() {
    $Run009Path = Join-Path (Join-Path $ArtifactRoot "spain-fresh-20260721-009") "preflight-evidence.json"
    Assert-PrivatePath $Run009Path
    $Info = Get-Item -LiteralPath $Run009Path -Force
    if ($Info.Length -lt 1 -or $Info.Length -gt 2097152) {
        throw "Protected run009 evidence length is unsafe."
    }
    $EvidenceSha = (Get-FileHash -LiteralPath $Run009Path -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($EvidenceSha -cne $run009EvidenceSha) {
        throw "Protected run009 evidence checksum mismatch."
    }
    try { $Evidence = Get-Content -Raw -LiteralPath $Run009Path | ConvertFrom-Json -ErrorAction Stop }
    catch { throw "Protected run009 evidence JSON is invalid." }
    Assert-ExactProperties $Evidence.firewall @("backend", "rules_sha256", "rule_count") "run009.firewall"
    if ($Evidence.firewall.backend -cne $run009FirewallBackend -or
        $Evidence.firewall.rules_sha256.ToUpperInvariant() -cne $run009FirewallRulesSha -or
        [int]$Evidence.firewall.rule_count -ne $run009FirewallRuleCount) {
        throw "Protected run009 firewall receipt mismatch."
    }
    return [pscustomobject]@{
        EvidenceSha256 = $EvidenceSha
        FirewallBackend = $Evidence.firewall.backend
        FirewallRulesSha256 = $Evidence.firewall.rules_sha256.ToUpperInvariant()
        FirewallRuleCount = [int]$Evidence.firewall.rule_count
    }
}

function Get-ConflictDecision([object]$Evidence) {
    $Codes = [Collections.Generic.List[string]]::new()
    $PlanReceipt = Get-ResourcePlanReceipt
    $Plan = $PlanReceipt.Plan
    if ($Evidence.platform.os_release.id -cne $Plan.target.os_family -or
        $Evidence.platform.os_release.version_id -cne $Plan.target.os_release -or
        $Evidence.platform.architecture -cne $Plan.target.architecture) {
        $Codes.Add("PLATFORM_OS_INCOMPATIBLE")
    }
    if (-not $Evidence.platform.kernel.release.StartsWith([string]$Plan.target.kernel_prefix, [StringComparison]::Ordinal)) {
        $Codes.Add("PLATFORM_KERNEL_INCOMPATIBLE")
    }
    if (-not $Evidence.platform.python3.version.StartsWith("$($Plan.target.python_major_minor).", [StringComparison]::Ordinal) -or
        $Evidence.platform.python3.soabi -cne $Plan.target.python_soabi) {
        $Codes.Add("PLATFORM_PYTHON_INCOMPATIBLE")
    }
    if (-not (Test-VersionAtLeast ([string]$Evidence.platform.glibc_version) ([string]$Plan.target.glibc_minimum))) {
        $Codes.Add("PLATFORM_GLIBC_INCOMPATIBLE")
    }
    $MemoryMinimumBytes = [int64]$Plan.capacity_minimums.memory_available_kib * 1024
    if ([int64]$Evidence.capacity.mem_available_bytes -lt $MemoryMinimumBytes) {
        $Codes.Add("CAPACITY_MEMORY_INSUFFICIENT")
    }
    $RequiredFilesystems = @($Plan.capacity_filesystems)
    foreach ($FilesystemPath in $RequiredFilesystems) {
        $ObservedFilesystems = @($Evidence.capacity.filesystems | Where-Object { $_.path -ceq $FilesystemPath })
        if ($ObservedFilesystems.Count -ne 1 -or
            [int64]$ObservedFilesystems[0].available_bytes -lt [int64]$Plan.capacity_minimums.disk_available_bytes) {
            $Codes.Add("CAPACITY_DISK_INSUFFICIENT")
        }
        if ($ObservedFilesystems.Count -ne 1 -or
            [int64]$ObservedFilesystems[0].available_inodes -lt [int64]$Plan.capacity_minimums.inodes_available) {
            $Codes.Add("CAPACITY_INODES_INSUFFICIENT")
        }
    }
    foreach ($NftObject in @($Evidence.firewall.structured_snapshot.nftables)) {
        if ($null -ne $NftObject.table -and
            $NftObject.table.family -ceq $Plan.firewall_namespace.family -and
            $NftObject.table.name -ceq $Plan.firewall_namespace.table) {
            $Codes.Add("FIREWALL_NAMESPACE_PRESENT")
        }
    }
    foreach ($Listener in @($Evidence.listening_sockets)) {
        if ($Listener.protocol -ceq "tcp" -and [int]$Listener.port -eq 3031 -and
            $Listener.address -cin @("127.0.0.1", "0.0.0.0", "::", "*")) {
            $Codes.Add("TCP_3031_BIND_CONFLICT")
        }
        if ($Listener.protocol -ceq "udp" -and [int]$Listener.port -eq 30001) {
            $Codes.Add("UDP_30001_BIND_CONFLICT")
        }
    }
    foreach ($Address in @($Evidence.network_state.addresses)) {
        if ($Address.family -cne "inet") { continue }
        if (Test-IPv4NetworkOverlap $Address.address ([int]$Address.prefix_length) "172.29.251.0/28") {
            $Codes.Add("ADDRESS_OVERLAP_172_29_251_0_28")
        }
        if (Test-IPv4NetworkOverlap $Address.address ([int]$Address.prefix_length) "10.212.12.0/24") {
            $Codes.Add("ADDRESS_OVERLAP_10_212_12_0_24")
        }
    }
    foreach ($Route in @($Evidence.network_state.routes)) {
        if ($Route.family -cne "inet" -or $Route.destination -ceq "default") { continue }
        if ($Route.destination -cnotmatch '^([0-9]{1,3}(?:\.[0-9]{1,3}){3})(?:/([0-9]|[12][0-9]|3[0-2]))?$') {
            throw "IPv4 route observation format mismatch."
        }
        $RouteAddress = $Matches[1]
        $RoutePrefix = if ([string]::IsNullOrEmpty($Matches[2])) { 32 } else { [int]$Matches[2] }
        if (Test-IPv4NetworkOverlap $RouteAddress $RoutePrefix "172.29.251.0/28") {
            $Codes.Add("ROUTE_OVERLAP_172_29_251_0_28")
        }
        if (Test-IPv4NetworkOverlap $RouteAddress $RoutePrefix "10.212.12.0/24") {
            $Codes.Add("ROUTE_OVERLAP_10_212_12_0_24")
        }
    }
    if (@($Evidence.candidates.paths | Where-Object { $_.exists -eq $true }).Count -ne 0) {
        $Codes.Add("CANDIDATE_PATH_PRESENT")
    }
    if ($Evidence.candidates.identities.user_exists -eq $true -or
        $Evidence.candidates.identities.uid_exists -eq $true -or
        $Evidence.candidates.identities.group_exists -eq $true -or
        $Evidence.candidates.identities.gid_exists -eq $true) {
        $Codes.Add("CANDIDATE_IDENTITY_PRESENT")
    }
    if (@($Evidence.candidates.units | Where-Object { $_.exists -eq $true }).Count -ne 0) {
        $Codes.Add("CANDIDATE_UNIT_PRESENT")
    }
    $Docker = $Evidence.candidates.docker
    if ($Docker.binary_present -eq $true -or $Docker.potential_socket_present -eq $true -or
        $Docker.daemon_process_present -eq $true -or $Docker.observation_safe -ne $true -or
        $Docker.container_exists -eq $true -or $Docker.container_collision_unknown -eq $true -or
        $Docker.network_exists -eq $true -or $Docker.network_collision_unknown -eq $true) {
        $Codes.Add("DOCKER_PRESENCE_OR_UNKNOWN")
    }
    if ($Evidence.candidates.network.bridge_exists -eq $true -or
        $Evidence.candidates.network.interface_exists -eq $true) {
        $Codes.Add("CANDIDATE_NETWORK_LINK_PRESENT")
    }
    if (@($Evidence.candidates.sockets | Where-Object { $_.exists -eq $true }).Count -ne 0) {
        $Codes.Add("CANDIDATE_SOCKET_PRESENT")
    }
    if (@($Evidence.candidates.runtime_directories | Where-Object { $_.exists -eq $true }).Count -ne 0) {
        $Codes.Add("CANDIDATE_RUNTIME_DIRECTORY_PRESENT")
    }
    $UniqueCodes = [string[]]@($Codes | Sort-Object -Unique)
    return [pscustomobject][ordered]@{
        resource_plan_sha256 = $PlanReceipt.Sha256
        conflict_free = ($UniqueCodes.Count -eq 0)
        conflict_codes = $UniqueCodes
    }
}

function Get-TrustBundleReceipt() {
    Assert-PrivateRootChain
    $Binding = Read-Binding
    Assert-HostPin $Binding
    $TargetBindingSha = (Get-FileHash -LiteralPath $BindingPath -Algorithm SHA256).Hash.ToUpperInvariant()
    $TargetHostSha = Get-TextSha256 $Binding["TARGET_HOST"]
    $TargetUserSha = Get-TextSha256 $Binding["TARGET_USER"]
    $HostPinSha = Get-TextSha256 $Binding["EXPECTED_HOST_KEY_SHA256"]
    $KnownHostsSha = (Get-FileHash -LiteralPath $KnownHostsPath -Algorithm SHA256).Hash.ToUpperInvariant()
    $AuthPublicKeySha = (Get-FileHash -LiteralPath $PublicKeyPath -Algorithm SHA256).Hash.ToUpperInvariant()
    $Canonical = @(
        "target_binding_sha256=$TargetBindingSha",
        "target_host_sha256=$TargetHostSha",
        "target_user_sha256=$TargetUserSha",
        "host_key_fingerprint_sha256=$HostPinSha",
        "known_hosts_sha256=$KnownHostsSha",
        "auth_public_key_sha256=$AuthPublicKeySha"
    ) -join "`n"
    return [pscustomobject]@{
        Binding = $Binding
        BundleSha256 = Get-TextSha256 $Canonical
        target_binding_sha256 = $TargetBindingSha
        target_host_sha256 = $TargetHostSha
        target_user_sha256 = $TargetUserSha
        host_key_fingerprint_sha256 = $HostPinSha
        host_pin_sha256 = $HostPinSha
        known_hosts_sha256 = $KnownHostsSha
        auth_public_key_sha256 = $AuthPublicKeySha
    }
}

if (-not (Test-Path -LiteralPath $SshExe -PathType Leaf) -or
    -not (Test-Path -LiteralPath $SshKeygenExe -PathType Leaf)) {
    throw "Required OpenSSH executable is unavailable."
}
$PreviewTrust = Get-TrustBundleReceipt
$PreviewResourcePlan = Get-ResourcePlanReceipt
$PreviewRun009 = Get-Run009EvidenceReceipt
$expectedApproval = "APPROVE PHASE12 SPAIN READ ONLY RESOURCE CONFIRMATION RUN $expectedRunId RUNNER SHA256 $actualRunnerSha REMOTE SHA256 $expectedRemoteScriptSha SOURCE $sourceRevision RUN009 EVIDENCE SHA256 $run009EvidenceSha RUN009 REFERENCE SHA256 $($PreviewRun009.EvidenceSha256) FINGERPRINT SET SHA256 $expectedFingerprintSetSha RESOURCE PLAN SHA256 $($PreviewResourcePlan.Sha256) TRUST BUNDLE SHA256 $($PreviewTrust.BundleSha256) EXACT PRIVATE TARGET DEDICATED ED25519 KEY INDEPENDENT HOST PIN STDIN ONLY NO REMOTE WRITE NO INSTALL NO SERVICE OR NETWORK MUTATION"
if ([string]::IsNullOrEmpty($Approval)) {
    Write-Output $expectedApproval
    throw "Exact read-only resource-confirmation approval mismatch."
}
if (-not [string]::Equals($Approval, $expectedApproval, [StringComparison]::Ordinal)) {
    throw "Exact read-only resource-confirmation approval mismatch."
}
$ApprovalSha = Get-TextSha256 $Approval
$ExecutionTrust = Get-TrustBundleReceipt
if ($ExecutionTrust.BundleSha256 -cne $PreviewTrust.BundleSha256) {
    throw "Trust bundle changed after approval preview."
}
$ExecutionRun009 = Get-Run009EvidenceReceipt
if ($ExecutionRun009.EvidenceSha256 -cne $PreviewRun009.EvidenceSha256 -or
    $ExecutionRun009.FirewallRulesSha256 -cne $PreviewRun009.FirewallRulesSha256) {
    throw "Protected run009 reference changed after approval preview."
}
$Binding = $ExecutionTrust.Binding
$TargetBindingSha = $ExecutionTrust.target_binding_sha256
Initialize-OutcomeDirectory $RunDirectory
$ClaimJson = [ordered]@{
    schema = "amn2.phase12-spain-resource-confirmation-claim.v1"
    run_id = $expectedRunId
    runner_sha256 = $actualRunnerSha
    remote_collector_sha256 = $expectedRemoteScriptSha
    approval_sha256 = $ApprovalSha
    resource_plan_sha256 = $PreviewResourcePlan.Sha256
    trust_bundle_sha256 = $ExecutionTrust.BundleSha256
    target_binding_sha256 = $TargetBindingSha
    target_host_sha256 = $ExecutionTrust.target_host_sha256
    target_user_sha256 = $ExecutionTrust.target_user_sha256
    host_pin_sha256 = $ExecutionTrust.host_pin_sha256
    known_hosts_sha256 = $ExecutionTrust.known_hosts_sha256
    auth_public_key_sha256 = $ExecutionTrust.auth_public_key_sha256
    run009_reference_sha256 = $ExecutionRun009.EvidenceSha256
    run009_reference_verified = "true"
    source_revision = $sourceRevision
} | ConvertTo-Json -Compress
$ClaimSha = Get-TextSha256 "$ClaimJson`n"
Write-EvidenceCreateNew $OutcomeClaimPath $ClaimJson
Protect-PrivatePath $OutcomeClaimPath

$SshArguments = @(
    "-F", "none",
    "-o", "BatchMode=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "PreferredAuthentications=publickey",
    "-o", "PasswordAuthentication=no",
    "-o", "KbdInteractiveAuthentication=no",
    "-o", "GSSAPIAuthentication=no",
    "-o", "ForwardAgent=no",
    "-o", "ClearAllForwardings=yes",
    "-o", "RequestTTY=no",
    "-o", "ConnectTimeout=10",
    "-o", "ServerAliveInterval=10",
    "-o", "ServerAliveCountMax=2",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$KnownHostsPath",
    "-i", $KeyPath,
    "-p", "22",
    "$($Binding['TARGET_USER'])@$($Binding['TARGET_HOST'])",
    "bash -s --"
)
$ResourcePlan = Get-ResourcePlanReceipt
$OutcomeStage = "ssh"
$OutcomeReason = "SSH_COLLECTION_FAILED"
$RawBytes = $null
$Result = $null
try {
    try { $Result = Invoke-SshWithExactInput $SshExe $SshArguments $RemoteScriptBytes }
    finally { [Array]::Clear($RemoteScriptBytes, 0, $RemoteScriptBytes.Length) }
    if ($Result.ExitCode -ne 0) {
        if ($Result.ExitCode -ne 0) {
            $OutcomeStage = Get-SafeRemoteFailureStage $Result.StdoutBytes $Result.ExitCode
        }
        [Array]::Clear($Result.StdoutBytes, 0, $Result.StdoutBytes.Length)
        [Array]::Clear($Result.StderrBytes, 0, $Result.StderrBytes.Length)
        throw "Sanitized SSH collection failure."
    }
    $RawBytes = [byte[]]$Result.StdoutBytes
    [Array]::Clear($Result.StderrBytes, 0, $Result.StderrBytes.Length)

    $OutcomeStage = "framing"
    $OutcomeReason = "STDOUT_FRAMING_INVALID"
    if ($RawBytes.Length -lt 3 -or $RawBytes.Length -gt 2097152 -or
        $RawBytes[$RawBytes.Length - 1] -ne 10 -or 13 -in $RawBytes) {
        throw "Sanitized stdout framing failure."
    }

    $OutcomeStage = "content"
    $OutcomeReason = "STDOUT_CONTENT_UNSAFE"
    $RawText = $StrictUtf8.GetString($RawBytes, 0, $RawBytes.Length - 1)
    if ($RawText.Contains("`n") -or
        $RawText -match '(?i)(authorization|bearer|BEGIN [A-Z ]+ KEY|api[_-]?key|credential|password|token|secret)') {
        throw "Sanitized stdout content failure."
    }

    $OutcomeStage = "json"
    $OutcomeReason = "JSON_INVALID"
    $Evidence = Assert-CanonicalJsonEncoding $RawText
    $OutcomeStage = "schema"
    $OutcomeReason = "SCHEMA_INVALID"
    Assert-ResourceConfirmationSchema $Evidence
    $OutcomeStage = "fingerprint"
    $OutcomeReason = "FINGERPRINT_MISMATCH"
    $FingerprintReceipt = Assert-FingerprintBaseline @($Evidence.unrelated_service_fingerprint) $expectedFingerprintSetSha $expectedFingerprintSetBytes

    $OutcomeStage = "conflict"
    $OutcomeReason = "UNEXPECTED_POST_CLAIM_FAILURE"
    $ConflictDecision = Get-ConflictDecision $Evidence

    $RawHasher = [Security.Cryptography.SHA256]::Create()
    try { $RawStdoutSha = ([BitConverter]::ToString($RawHasher.ComputeHash($RawBytes))).Replace("-", "") }
    finally { $RawHasher.Dispose() }
    $CanonicalText = $Evidence | ConvertTo-Json -Depth 64 -Compress
    $CanonicalBytes = (New-Object Text.UTF8Encoding($false)).GetBytes($CanonicalText)
    $CanonicalHasher = [Security.Cryptography.SHA256]::Create()
    try { $CanonicalEvidenceSha = ([BitConverter]::ToString($CanonicalHasher.ComputeHash($CanonicalBytes))).Replace("-", "") }
    finally { $CanonicalHasher.Dispose(); [Array]::Clear($CanonicalBytes, 0, $CanonicalBytes.Length) }

    $OutcomeStage = "persist"
    $OutcomeReason = "EVIDENCE_PERSIST_FAILED"
    Write-BytesCreateNew $EvidencePath $RawBytes
    Protect-PrivatePath $EvidencePath
    if ($ConflictDecision.conflict_free -ne $true) {
        $OutcomeStage = "conflict"
        $OutcomeReason = "CONFLICT_FREE_REQUIRED"
        Write-SanitizedOutcomeReceipt $ReceiptPath "blocked" $OutcomeStage $OutcomeReason $ClaimSha $ConflictDecision.resource_plan_sha256 @($ConflictDecision.conflict_codes)
        [Array]::Clear($RawBytes, 0, $RawBytes.Length)
        $ReceiptSha = (Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash.ToUpperInvariant()
        Write-Output "PHASE12_SPAIN_RESOURCE_CONFIRMATION_BLOCKED_RECEIPT_SHA256_$ReceiptSha"
        exit 20
    }

    $OutcomeStage = "completion"
    $OutcomeReason = "OUTCOME_PERSIST_FAILED"
    $ReceiptJson = [ordered]@{
        schema = "amn2.phase12-spain-resource-confirmation-receipt.v1"
        run_id = $expectedRunId
        status = "passed"
        claim_sha256 = $ClaimSha
        resource_plan_sha256 = $ConflictDecision.resource_plan_sha256
        conflict_free = $true
        conflict_codes = @()
        runner_sha256 = $actualRunnerSha
        remote_collector_sha256 = $expectedRemoteScriptSha
        approval_sha256 = $ApprovalSha
        trust_bundle_sha256 = $ExecutionTrust.BundleSha256
        target_binding_sha256 = $TargetBindingSha
        target_host_sha256 = $ExecutionTrust.target_host_sha256
        target_user_sha256 = $ExecutionTrust.target_user_sha256
        host_pin_sha256 = $ExecutionTrust.host_pin_sha256
        known_hosts_sha256 = $ExecutionTrust.known_hosts_sha256
        auth_public_key_sha256 = $ExecutionTrust.auth_public_key_sha256
        raw_stdout_sha256 = $RawStdoutSha
        raw_stdout_bytes = $RawBytes.Length
        canonical_evidence_sha256 = $CanonicalEvidenceSha
        fingerprint_set_sha256 = $FingerprintReceipt.Sha256
        fingerprint_set_bytes = $FingerprintReceipt.ByteLength
        fingerprint_count = 148
        run009_evidence_sha256 = $run009EvidenceSha
        run009_raw_order_fingerprint_sha256 = $run009RawOrderFingerprintSha
        run009_firewall_backend = $run009FirewallBackend
        run009_firewall_rules_sha256 = $run009FirewallRulesSha
        run009_firewall_rule_count = $run009FirewallRuleCount
        run009_reference_verified = $true
        source_revision = $sourceRevision
        instruction = "INSTALL_APPROVAL_MAY_BE_PREPARED_FROM_PROTECTED_RECEIPT"
    } | ConvertTo-Json -Depth 8 -Compress
    Write-AtomicPrivateJsonCreateNew $ReceiptPath $ReceiptJson
    [Array]::Clear($RawBytes, 0, $RawBytes.Length)
    Assert-PrivatePath $EvidencePath
    Assert-PrivatePath $ReceiptPath
    $ReceiptSha = (Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash.ToUpperInvariant()
    Write-Output "PHASE12_SPAIN_RESOURCE_CONFIRMATION_RECEIPT_SHA256_$ReceiptSha"
} catch {
    if ($null -ne $RawBytes) { [Array]::Clear($RawBytes, 0, $RawBytes.Length) }
    if ($null -ne $Result) {
        if ($null -ne $Result.StdoutBytes) { [Array]::Clear($Result.StdoutBytes, 0, $Result.StdoutBytes.Length) }
        if ($null -ne $Result.StderrBytes) { [Array]::Clear($Result.StderrBytes, 0, $Result.StderrBytes.Length) }
    }
    if (-not (Test-Path -LiteralPath $ReceiptPath)) {
        Write-SanitizedOutcomeReceipt $ReceiptPath "failed" $OutcomeStage $OutcomeReason $ClaimSha $ResourcePlan.Sha256 @()
    }
    $FailureReceiptSha = (Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash.ToUpperInvariant()
    Write-Output "PHASE12_SPAIN_RESOURCE_CONFIRMATION_FAILURE_RECEIPT_SHA256_$FailureReceiptSha"
    throw "Read-only resource confirmation failed after claim; use a new run_id and exact approval."
}
