[CmdletBinding()]
param(
    [string]$FutureClaimPath,
    [string]$PackageRoot,
    [string]$ExpectedHost,
    [string]$OutcomePath,
    [switch]$FutureAuthorization
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Phase15PackageId = 'phase15-dual-protocol-bootstrap-20260811-001'
$script:Phase15ClaimSchema = 'amn2.phase15.readonly-preflight-claim.v1'
$script:Phase15CollectorSchema = 'amn2.phase15.spain-readonly-collector.v1'
$script:Phase15EvidenceSchema = 'amn2.phase15.readonly-preflight-evidence.v1'
$script:Phase15FailureSchema = 'amn2.phase15.readonly-preflight-failure.v1'
$script:Phase15ProductionStateRoot = 'C:\ProgramData\AMN2\phase15\readonly-preflight'
$script:Phase15StateRootCreationMutexName = 'Global\AMN2-Phase15-ReadonlyPreflight-StateRoot-v1'
$script:Phase15SystemSid = 'S-1-5-18'
$script:Phase15AdministratorsSid = 'S-1-5-32-544'
$script:Phase15TrustedBundleRunId = 'spain-fresh-20260720-001'
$script:Phase15SpainTargetUser = 'root'
$script:Phase15SpainHostKeySha256 = 'SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU'
$script:Phase15MaximumArtifactBytes = 1048576
$script:Phase15TransportOperationMilliseconds = 60000
$script:Phase15TransportBudgetMilliseconds = 65000
$script:Phase15ObservationNames = @(
    'application_state','architecture','awg2_health','backup_capability','bridge_amn2sp3br0',
    'config_path','container_capability','container_cidr_172_29_252_0_28','container_name',
    'database_state','disk_space','firewall','interface_awg3','os_compatibility','python_3_12',
    'recovery_markers_phase14_phase15','routes','service_capability','service_name','state_root',
    'telegram_prerequisites','udp_30002','vpn_cidr_10_212_13_0_24'
)
$script:Phase15StopReasons = @('identity_mismatch','observation_failed','recovery_incomplete','resource_conflict')
$script:Phase15FailureReasons = @('claim_invalid','collector_failed','identity_mismatch','observation_ambiguous','schema_invalid','transport_failed')
$script:Phase15ConflictNames = @('bridge_amn2sp3br0','config_path','container_cidr_172_29_252_0_28','container_name','firewall','interface_awg3','routes','service_name','state_root','udp_30002','vpn_cidr_10_212_13_0_24')

function Get-Phase15BytesSha256 {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $digest = $algorithm.ComputeHash($Bytes) } finally { $algorithm.Dispose() }
    return ([BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
}

function Get-Phase15CanonicalJsonSha256 {
    param([Parameter(Mandatory)][object]$Value)
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase15CanonicalJsonText -Value $Value) + "`n")
    return Get-Phase15BytesSha256 -Bytes $bytes
}

function Read-Phase15BoundedFileBytes {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][int]$MaximumBytes)
    if ($MaximumBytes -lt 1) { throw 'input_size_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -lt 1 -or $item.Length -gt $MaximumBytes) { throw 'input_size_invalid' }
    $stream = [IO.FileStream]::new($item.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $buffer = [IO.MemoryStream]::new()
    $chunk = [byte[]]::new(4096)
    [byte[]]$result = $null
    try {
        while ($true) {
            $remaining = ($MaximumBytes + 1) - [int]$buffer.Length
            if ($remaining -le 0) { throw 'input_size_invalid' }
            $count = $stream.Read($chunk, 0, [Math]::Min($chunk.Length, $remaining))
            if ($count -eq 0) { break }
            $buffer.Write($chunk, 0, $count)
        }
        if ($buffer.Length -lt 1 -or $buffer.Length -gt $MaximumBytes) { throw 'input_size_invalid' }
        $result = [byte[]]$buffer.ToArray()
    } finally {
        [Array]::Clear($chunk, 0, $chunk.Length)
        try {
            $backing = $buffer.GetBuffer()
            [Array]::Clear($backing, 0, $backing.Length)
        } catch { }
        $buffer.Dispose()
        $stream.Dispose()
    }
    Write-Output -NoEnumerate $result
}

function Read-Phase15ManifestArtifact {
    param([Parameter(Mandatory)][string]$Path)
    $bytes = Read-Phase15BoundedFileBytes -Path $Path -MaximumBytes $script:Phase15MaximumArtifactBytes
    try {
        $text = [Text.UTF8Encoding]::new($false, $true).GetString($bytes)
        $value = ConvertFrom-Phase15CanonicalJsonText -Text $text
    } catch { throw 'manifest_invalid' }
    if ($null -eq $value) { throw 'manifest_invalid' }
    return [pscustomobject]@{ Bytes = [byte[]]$bytes; Sha256 = Get-Phase15BytesSha256 -Bytes $bytes; Value = $value }
}

function Read-Phase15CollectorArtifact {
    param([Parameter(Mandatory)][string]$Path)
    $bytes = Read-Phase15BoundedFileBytes -Path $Path -MaximumBytes $script:Phase15MaximumArtifactBytes
    return [pscustomobject]@{
        Bytes = [byte[]]$bytes
        Sha256 = Get-Phase15BytesSha256 -Bytes $bytes
    }
}

function ConvertTo-Phase15CanonicalJsonText {
    param([Parameter(Mandatory = $false)][AllowNull()][object]$Value)
    if ($null -eq $Value) { return 'null' }
    if ($Value -is [string] -or $Value -is [char]) {
        return (ConvertTo-Json -InputObject ([string]$Value) -Compress)
    }
    if ($Value -is [bool]) { return $Value.ToString().ToLowerInvariant() }
    if ($Value -is [System.Collections.IDictionary]) {
        $parts = foreach ($key in @($Value.Keys | ForEach-Object { [string]$_ } | Sort-Object)) {
            (ConvertTo-Json -InputObject $key -Compress) + ':' + (ConvertTo-Phase15CanonicalJsonText -Value $Value[$key])
        }
        return '{' + ($parts -join ',') + '}'
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        $parts = foreach ($item in $Value) { ConvertTo-Phase15CanonicalJsonText -Value $item }
        return '[' + ($parts -join ',') + ']'
    }
    if ($Value -is [byte] -or $Value -is [sbyte] -or $Value -is [int16] -or $Value -is [uint16] -or
        $Value -is [int32] -or $Value -is [uint32] -or $Value -is [int64] -or $Value -is [uint64] -or
        $Value -is [decimal] -or $Value -is [single] -or $Value -is [double]) {
        if (($Value -is [single] -or $Value -is [double]) -and ([double]::IsNaN($Value) -or [double]::IsInfinity($Value))) { throw 'canonical_json_invalid' }
        return ([Convert]::ToString($Value, [Globalization.CultureInfo]::InvariantCulture))
    }
    $properties = @($Value.PSObject.Properties)
    if ($properties.Count -eq 0) { throw 'canonical_json_invalid' }
    $parts = foreach ($property in @($properties | Sort-Object -Property Name)) {
        (ConvertTo-Json -InputObject ([string]$property.Name) -Compress) + ':' + (ConvertTo-Phase15CanonicalJsonText -Value $property.Value)
    }
    return '{' + ($parts -join ',') + '}'
}

function ConvertFrom-Phase15CanonicalJsonFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $bytes = Read-Phase15BoundedFileBytes -Path $Path -MaximumBytes $script:Phase15MaximumArtifactBytes
        $strictUtf8 = [Text.UTF8Encoding]::new($false, $true)
        $text = $strictUtf8.GetString($bytes)
        $value = $text | ConvertFrom-Json
        if ((ConvertTo-Phase15CanonicalJsonText -Value $value) + "`n" -cne $text) { return $null }
        return $value
    } catch {
        return $null
    }
}

function ConvertFrom-Phase15CanonicalJsonText {
    param([Parameter(Mandatory)][string]$Text)
    try {
        $value = $Text | ConvertFrom-Json
        if ((ConvertTo-Phase15CanonicalJsonText -Value $value) + "`n" -cne $Text) { return $null }
        return $value
    } catch { return $null }
}

function ConvertFrom-Phase15JsonFile {
    param([Parameter(Mandatory)][string]$Path)
    return ConvertFrom-Phase15CanonicalJsonFile -Path $Path
}

function Read-Phase15FutureClaim {
    param([Parameter(Mandatory)][string]$ClaimPath)
    return ConvertFrom-Phase15CanonicalJsonFile -Path $ClaimPath
}

function Test-Phase15ExpectedHost {
    param([Parameter(Mandatory)][string]$ExpectedHost)
    return $ExpectedHost -cmatch '^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$'
}

function Test-Phase15ExactProperties {
    param([Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string[]]$Required)
    if ($null -eq $Value) { return $false }
    $actual = @($Value.PSObject.Properties.Name | Sort-Object)
    $expected = @($Required | Sort-Object)
    return ($actual -join '|') -ceq ($expected -join '|')
}

function Test-Phase15UtcTimestamp {
    param([Parameter(Mandatory)][object]$Value)
    if ($Value -isnot [string]) { return $false }
    try {
        $parsed = [DateTimeOffset]::ParseExact($Value, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        return $parsed.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') -ceq $Value
    } catch { return $false }
}

function Test-Phase15ClaimIdentity {
    param(
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ExpectedPackageId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost
    )
    if ($ExpectedPackageId -cne $script:Phase15PackageId) { return $false }
    if ($ExpectedManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $ExpectedCollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
    if (-not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost)) { return $false }
    $required = @('claim_id','collector_sha256','consumed_at','expected_host','expires_at','future_gate','issued_at','manifest_sha256','package_id','schema','status')
    if (-not (Test-Phase15ExactProperties -Value $Claim -Required $required)) { return $false }
    foreach ($field in @('claim_id','collector_sha256','expected_host','expires_at','future_gate','issued_at','manifest_sha256','package_id','schema','status')) {
        if ($Claim.$field -isnot [string]) { return $false }
    }
    if ($Claim.schema -cne $script:Phase15ClaimSchema -or $Claim.package_id -cne $ExpectedPackageId) { return $false }
    if ($Claim.manifest_sha256 -cne $ExpectedManifestSha256 -or $Claim.collector_sha256 -cne $ExpectedCollectorSha256) { return $false }
    if ($Claim.expected_host -cne $ExpectedHost -or $Claim.claim_id -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { return $false }
    if ($Claim.future_gate -cne 'PREFLIGHT' -or $Claim.status -cne 'issued' -or $null -ne $Claim.consumed_at) { return $false }
    if (-not (Test-Phase15UtcTimestamp -Value $Claim.issued_at) -or -not (Test-Phase15UtcTimestamp -Value $Claim.expires_at)) { return $false }
    $issued = [DateTimeOffset]::ParseExact($Claim.issued_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    $expires = [DateTimeOffset]::ParseExact($Claim.expires_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    if ($issued -ge $expires) { return $false }
    return $true
}

function Test-Phase15FutureClaim {
    param(
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ExpectedPackageId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [string]$At
    )
    if (-not (Test-Phase15ClaimIdentity -Claim $Claim -ExpectedPackageId $ExpectedPackageId -ExpectedManifestSha256 $ExpectedManifestSha256 -ExpectedCollectorSha256 $ExpectedCollectorSha256 -ExpectedHost $ExpectedHost)) { return $false }
    if ([string]::IsNullOrWhiteSpace($At)) { $atValue = [DateTimeOffset]::UtcNow } elseif (-not (Test-Phase15UtcTimestamp -Value $At)) { return $false } else {
        $atValue = [DateTimeOffset]::ParseExact($At, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    }
    $issued = [DateTimeOffset]::ParseExact($Claim.issued_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    $expires = [DateTimeOffset]::ParseExact($Claim.expires_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    return $issued -le $atValue -and $atValue -lt $expires
}

function Test-Phase15CollectorDocument {
    param(
        [Parameter(Mandatory)][object]$Document,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedClaimId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$StartedAt,
        [Parameter(Mandatory)][string]$EndedAt
    )
    try {
        $required = @('blocking_reasons','claim_id','collector_sha256','decision','host_identity','manifest_sha256','observed_at','observations','package_id','safety','schema')
        if (-not (Test-Phase15ExactProperties -Value $Document -Required $required)) { return $false }
        foreach ($field in @('claim_id','collector_sha256','decision','host_identity','manifest_sha256','observed_at','package_id','schema')) {
            if ($Document.$field -isnot [string]) { return $false }
        }
        if ($Document.schema -cne $script:Phase15CollectorSchema -or $Document.package_id -cne $script:Phase15PackageId) { return $false }
        if ($ExpectedManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $ExpectedCollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
        if ($Document.manifest_sha256 -isnot [string] -or $Document.collector_sha256 -isnot [string]) { return $false }
        if ($Document.manifest_sha256 -cne $ExpectedManifestSha256 -or $Document.collector_sha256 -cne $ExpectedCollectorSha256) { return $false }
        if (-not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost) -or $Document.host_identity -cne $ExpectedHost -or $Document.claim_id -cne $ExpectedClaimId) { return $false }
        if ($ExpectedClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $Document.observed_at) -or -not (Test-Phase15UtcTimestamp -Value $StartedAt) -or -not (Test-Phase15UtcTimestamp -Value $EndedAt)) { return $false }
        $observed = [DateTimeOffset]::ParseExact($Document.observed_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $started = [DateTimeOffset]::ParseExact($StartedAt, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $ended = [DateTimeOffset]::ParseExact($EndedAt, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        if ($ended -lt $started -or $observed -lt $started -or $observed -gt $ended) { return $false }
        if ($Document.decision -isnot [string] -or $Document.decision -notin @('pass','stop')) { return $false }
        if (-not (Test-Phase15ExactProperties -Value $Document.safety -Required @('live_mutation','raw_output_persisted','remote_file_written'))) { return $false }
        if ($Document.safety.live_mutation -isnot [bool] -or $Document.safety.remote_file_written -isnot [bool] -or $Document.safety.raw_output_persisted -isnot [bool]) { return $false }
        if ($Document.safety.live_mutation -ne $false -or $Document.safety.remote_file_written -ne $false -or $Document.safety.raw_output_persisted -ne $false) { return $false }
        if ($Document.blocking_reasons -isnot [System.Array] -or $Document.observations -isnot [System.Array]) { return $false }
        $reasons = @($Document.blocking_reasons)
        if (@($reasons | Where-Object { $_ -isnot [string] }).Count -ne 0) { return $false }
        if (($reasons -join '|') -cne (@($reasons | Sort-Object -Unique) -join '|')) { return $false }
        if (@($reasons | Where-Object { $_ -cnotin $script:Phase15StopReasons }).Count -ne 0) { return $false }
        $observations = @($Document.observations)
        if ($observations.Count -ne $script:Phase15ObservationNames.Count) { return $false }
        $names = @()
        $mustStop = $false
        $states = @{}
        foreach ($item in $observations) {
            if (-not (Test-Phase15ExactProperties -Value $item -Required @('name','observation_sha256','state'))) { return $false }
            if ($item.name -isnot [string] -or $item.observation_sha256 -isnot [string] -or $item.state -isnot [string]) { return $false }
            if ($item.name -cnotin $script:Phase15ObservationNames -or $item.observation_sha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
            if ($item.state -cnotin @('absent','free','pass','present','stop','unknown')) { return $false }
            if ($item.state -in @('stop','unknown')) { $mustStop = $true }
            $names += [string]$item.name
            $states[[string]$item.name] = [string]$item.state
        }
        if (($names -join '|') -cne ($script:Phase15ObservationNames -join '|')) { return $false }
        $expectedReasons = @()
        if ($states['recovery_markers_phase14_phase15'] -in @('stop','unknown')) { $expectedReasons += 'recovery_incomplete' }
        if (@($script:Phase15ConflictNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'resource_conflict' }
        $ordinaryNames = @($script:Phase15ObservationNames | Where-Object { $_ -cnotin $script:Phase15ConflictNames -and $_ -cne 'recovery_markers_phase14_phase15' })
        if (@($ordinaryNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'observation_failed' }
        $expectedReasons = @($expectedReasons | Sort-Object -Unique)
        $hasReasons = $expectedReasons.Count -gt 0
        if (($reasons -join '|') -cne ($expectedReasons -join '|')) { return $false }
        if (($Document.decision -ceq 'stop') -ne $hasReasons -or $mustStop -ne $hasReasons) { return $false }
        return $true
    } catch { return $false }
}

function ConvertTo-Phase15Evidence {
    param(
        [Parameter(Mandatory)][object]$Document,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$StartedAt,
        [Parameter(Mandatory)][string]$EndedAt
    )
    $observations = @($Document.observations | ForEach-Object {
        [ordered]@{ name = [string]$_.name; observation_sha256 = [string]$_.observation_sha256; state = [string]$_.state }
    })
    return [ordered]@{
        collector_sha256 = $CollectorSha256
        decision = [string]$Document.decision
        ended_at = $EndedAt
        expected_host = $ExpectedHost
        manifest_sha256 = $ManifestSha256
        observations = $observations
        package_id = $script:Phase15PackageId
        safety = [ordered]@{ live_mutation = $false; raw_output_persisted = $false; remote_file_written = $false; ssh_used = $true }
        schema = $script:Phase15EvidenceSchema
        started_at = $StartedAt
        stop_reasons = @($Document.blocking_reasons | ForEach-Object { [string]$_ })
        transport_disposition = 'read_only_completed'
    }
}

function Get-Phase15SpainTrustContract {
    $localAppData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    if ([string]::IsNullOrWhiteSpace($localAppData) -or -not [IO.Path]::IsPathRooted($localAppData)) { throw 'trust_binding_invalid' }
    $trustRoot = Join-Path $localAppData "AMN2\private-artifacts\post-release\spain-migration\$($script:Phase15TrustedBundleRunId)"
    return [pscustomobject]@{
        ExpectedHostKeySha256 = $script:Phase15SpainHostKeySha256
        KeyPath = Join-Path $trustRoot 'id_ed25519_spain'
        KnownHostsPath = Join-Path $trustRoot 'known_hosts_spain'
        TargetUser = $script:Phase15SpainTargetUser
        AnchorPath = $localAppData
        TrustRoot = $trustRoot
    }
}

function Assert-Phase15TrustAnchor {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [IO.Path]::IsPathRooted($Path)) { throw 'trust_binding_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or [IO.Path]::GetFullPath($item.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar)) { throw 'trust_binding_invalid' }
}

function Get-Phase15TrustParentPaths {
    param([Parameter(Mandatory)][string]$AnchorPath, [Parameter(Mandatory)][string]$TrustRoot)
    $anchor = [IO.Path]::GetFullPath($AnchorPath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $root = [IO.Path]::GetFullPath($TrustRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $prefix = $anchor + [IO.Path]::DirectorySeparatorChar
    if (-not $root.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'trust_binding_invalid' }
    $relative = $root.Substring($prefix.Length)
    $segments = @($relative.Split([IO.Path]::DirectorySeparatorChar) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($segments.Count -lt 1) { throw 'trust_binding_invalid' }
    $current = $anchor
    foreach ($segment in $segments) {
        if ($segment -in @('.', '..') -or $segment.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0) { throw 'trust_binding_invalid' }
        $current = [IO.Path]::GetFullPath([IO.Path]::Combine($current, $segment))
        Write-Output $current
    }
}

function Assert-Phase15TrustPath {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$ExpectedOwnerSid, [switch]$RequireLeaf)
    if (-not [IO.Path]::IsPathRooted($Path)) { throw 'trust_binding_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($RequireLeaf -and $item.PSIsContainer) -or (-not $RequireLeaf -and -not $item.PSIsContainer) -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'trust_binding_invalid' }
    $acl = Get-Acl -LiteralPath $item.FullName -ErrorAction Stop
    $ownerSid = $acl.Owner
    try { $ownerSid = ([Security.Principal.NTAccount]$acl.Owner).Translate([Security.Principal.SecurityIdentifier]).Value } catch { }
    $rules = @($acl.Access)
    if ($ownerSid -cne $ExpectedOwnerSid -or -not $acl.AreAccessRulesProtected -or $rules.Count -ne 1 -or $rules[0].IsInherited) { throw 'trust_binding_invalid' }
    $ruleSid = $rules[0].IdentityReference.Value
    try { $ruleSid = $rules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value } catch { }
    if ($ruleSid -cne $ExpectedOwnerSid -or $rules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or (($rules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl)) { throw 'trust_binding_invalid' }
}

function Test-Phase15PrivateKeyBytes {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    $header = [Text.ASCIIEncoding]::new().GetBytes("-----BEGIN OPENSSH PRIVATE KEY-----`n")
    $footer = [Text.ASCIIEncoding]::new().GetBytes("-----END OPENSSH PRIVATE KEY-----`n")
    try {
        if ($Bytes.Length -le ($header.Length + $footer.Length)) { return $false }
        for ($index = 0; $index -lt $Bytes.Length; $index++) {
            if ($Bytes[$index] -eq 0 -or $Bytes[$index] -eq 13 -or $Bytes[$index] -gt 127) { return $false }
        }
        for ($index = 0; $index -lt $header.Length; $index++) {
            if ($Bytes[$index] -ne $header[$index]) { return $false }
        }
        $footerStart = $Bytes.Length - $footer.Length
        for ($index = 0; $index -lt $footer.Length; $index++) {
            if ($Bytes[$footerStart + $index] -ne $footer[$index]) { return $false }
        }
        $lineLength = 0
        for ($index = $header.Length; $index -lt $footerStart; $index++) {
            $value = $Bytes[$index]
            if ($value -eq 10) {
                if ($lineLength -lt 1 -or $lineLength -gt 70) { return $false }
                $lineLength = 0
                continue
            }
            $base64Byte = ($value -ge 65 -and $value -le 90) -or ($value -ge 97 -and $value -le 122) -or ($value -ge 48 -and $value -le 57) -or $value -in @(43, 47, 61)
            if (-not $base64Byte) { return $false }
            $lineLength++
        }
        return $lineLength -eq 0
    } finally {
        [Array]::Clear($header, 0, $header.Length)
        [Array]::Clear($footer, 0, $footer.Length)
    }
}

function Assert-Phase15SpainTrustBundle {
    param([Parameter(Mandatory)][string]$ExpectedHost)
    if (-not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost)) { throw 'trust_binding_invalid' }
    $contract = Get-Phase15SpainTrustContract
    $currentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    Assert-Phase15TrustAnchor -Path $contract.AnchorPath
    foreach ($parentPath in @(Get-Phase15TrustParentPaths -AnchorPath $contract.AnchorPath -TrustRoot $contract.TrustRoot)) {
        Assert-Phase15TrustPath -Path $parentPath -ExpectedOwnerSid $currentSid
    }
    Assert-Phase15TrustPath -Path $contract.KeyPath -ExpectedOwnerSid $currentSid -RequireLeaf
    Assert-Phase15TrustPath -Path $contract.KnownHostsPath -ExpectedOwnerSid $currentSid -RequireLeaf
    [byte[]]$keyBytes = $null
    [byte[]]$knownHostsBytes = $null
    try {
        $keyBytes = Read-Phase15BoundedFileBytes -Path $contract.KeyPath -MaximumBytes 16384
        $knownHostsBytes = Read-Phase15BoundedFileBytes -Path $contract.KnownHostsPath -MaximumBytes 4096
        if (-not (Test-Phase15PrivateKeyBytes -Bytes $keyBytes) -or @($knownHostsBytes | Where-Object { $_ -gt 127 }).Count -ne 0) { throw 'trust_binding_invalid' }
        $strictAscii = [Text.ASCIIEncoding]::new()
        $knownText = $strictAscii.GetString($knownHostsBytes)
        $match = [regex]::Match($knownText, '^([^ \r\n]+) (ssh-ed25519) ([A-Za-z0-9+/]+={0,2})\r?\n$')
        if (-not $match.Success -or $match.Groups[1].Value -cne $ExpectedHost) { throw 'trust_binding_invalid' }
        $blob = [Convert]::FromBase64String($match.Groups[3].Value)
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $digest = $hasher.ComputeHash($blob) } finally { $hasher.Dispose() }
        $fingerprint = 'SHA256:' + [Convert]::ToBase64String($digest).TrimEnd('=')
        if ($fingerprint -cne $contract.ExpectedHostKeySha256) { throw 'trust_binding_invalid' }
    } finally {
        if ($null -ne $keyBytes) { [Array]::Clear($keyBytes, 0, $keyBytes.Length) }
        if ($null -ne $knownHostsBytes) { [Array]::Clear($knownHostsBytes, 0, $knownHostsBytes.Length) }
    }
    return $contract
}

function Assert-Phase15LocalExecutable {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [IO.Path]::IsPathRooted($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'local_executable_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -lt 1 -or $item.Length -gt 33554432) { throw 'local_executable_invalid' }
}

function New-Phase15SshArguments {
    param([Parameter(Mandatory)][string]$ExpectedHost, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ManifestSha256, [Parameter(Mandatory)][string]$CollectorSha256)
    if (-not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost) -or $ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or $ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $CollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'transport_envelope_invalid' }
    $contract = Get-Phase15SpainTrustContract
    $remote = "/usr/bin/bash -s -- '$($script:Phase15PackageId)' '$ManifestSha256' '$CollectorSha256' '$ClaimId' '$ExpectedHost'"
    return @(
        '-T','-F','none',
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','IdentityAgent=none',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no','-o','GSSAPIAuthentication=no',
        '-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','RequestTTY=no',
        '-o','StrictHostKeyChecking=yes','-o',"UserKnownHostsFile=$($contract.KnownHostsPath)",
        '-o','GlobalKnownHostsFile=NUL','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',
        '-i',$contract.KeyPath,'--',"$($contract.TargetUser)@$ExpectedHost",$remote
    )
}

function ConvertTo-Phase15WindowsArgument {
    param([Parameter(Mandatory)][string]$Argument)
    $escaped = $Argument.Replace('\', '\')
    $escaped = $escaped.Replace('"', '\"')
    return '"' + $escaped + '"'
}

function Add-Phase15BoundedBytes {
    param(
        [Parameter(Mandatory)][IO.MemoryStream]$Buffer,
        [Parameter(Mandatory)][byte[]]$Bytes,
        [Parameter(Mandatory)][int]$Count,
        [Parameter(Mandatory)][int]$MaximumBytes
    )
    $remaining = ($MaximumBytes + 1) - [int]$Buffer.Length
    if ($remaining -gt 0 -and $Count -gt 0) {
        $writeCount = [Math]::Min($remaining, $Count)
        $Buffer.Write($Bytes, 0, $writeCount)
    }
    return $Buffer.Length -gt $MaximumBytes
}

function Test-Phase15TransportCompletion {
    param([Parameter(Mandatory)][int]$ExitCode, [Parameter(Mandatory)][long]$StderrLength)
    return $ExitCode -eq 0 -and $StderrLength -eq 0
}

function Stop-Phase15TransportProcess {
    param([Parameter(Mandatory)][object]$Process, [int]$WaitMilliseconds = 2000)
    if (-not $Process.HasExited) { $Process.Kill() }
    if (-not $Process.WaitForExit($WaitMilliseconds)) { throw 'transport_child_retained' }
}

function Get-Phase15TransportRemainingMilliseconds {
    param([Parameter(Mandatory)][Diagnostics.Stopwatch]$Clock, [Parameter(Mandatory)][int]$DeadlineMilliseconds)
    if ($DeadlineMilliseconds -lt 1) { throw 'transport_deadline_invalid' }
    $remaining = [long]$DeadlineMilliseconds - [long]$Clock.ElapsedMilliseconds
    if ($remaining -le 0) { return 0 }
    return [int][Math]::Min([int]::MaxValue, $remaining)
}

function Invoke-Phase15OneSshTransport {
    param(
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][byte[]]$CollectorBytes,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][ref]$Started,
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][object]$Lock
    )
    $Started.Value = $false
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'C:\Windows\System32\OpenSSH\ssh.exe'
    Assert-Phase15LocalExecutable -Path $start.FileName
    $start.Arguments = ((New-Phase15SshArguments -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256) | ForEach-Object { ConvertTo-Phase15WindowsArgument -Argument $_ }) -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.EnvironmentVariables.Clear()
    $start.EnvironmentVariables['SYSTEMROOT'] = $env:SystemRoot
    $start.EnvironmentVariables['WINDIR'] = $env:WINDIR
    $start.EnvironmentVariables['PATH'] = 'C:\Windows\System32\OpenSSH;C:\Windows\System32'
    $start.EnvironmentVariables['HOME'] = 'C:\ProgramData\AMN2\phase15\no-ambient-home'
    $start.EnvironmentVariables['USERPROFILE'] = 'C:\ProgramData\AMN2\phase15\no-ambient-profile'
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    $stdout = $null
    $stderr = $null
    $cancellation = $null
    try {
        if (-not $process.Start()) { throw 'transport_failed' }
        $Started.Value = $true
        [void](Set-Phase15TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'ssh_started' -Lock $Lock)
        $stdout = [IO.MemoryStream]::new()
        $stderr = [IO.MemoryStream]::new()
        $cancellation = [Threading.CancellationTokenSource]::new()
        $stdoutBytes = [byte[]]::new(4096)
        $stderrBytes = [byte[]]::new(4096)
        $stdoutTask = $process.StandardOutput.BaseStream.ReadAsync($stdoutBytes, 0, $stdoutBytes.Length, $cancellation.Token)
        $stderrTask = $process.StandardError.BaseStream.ReadAsync($stderrBytes, 0, $stderrBytes.Length, $cancellation.Token)
        $stdinTask = $process.StandardInput.BaseStream.WriteAsync($CollectorBytes, 0, $CollectorBytes.Length, $cancellation.Token)
        $stdoutDone = $false
        $stderrDone = $false
        $stdinDone = $false
        while (-not ($process.HasExited -and $stdoutDone -and $stderrDone -and $stdinDone)) {
            $remaining = Get-Phase15TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase15TransportOperationMilliseconds
            if ($remaining -le 0) { $cancellation.Cancel(); throw 'transport_failed' }
            if (-not $stdinDone -and $stdinTask.IsCompleted) {
                $stdinTask.GetAwaiter().GetResult()
                $process.StandardInput.Close()
                $stdinDone = $true
            }
            if (-not $stdoutDone -and $stdoutTask.IsCompleted) {
                $count = $stdoutTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stdoutDone = $true } else {
                    if (Add-Phase15BoundedBytes -Buffer $stdout -Bytes $stdoutBytes -Count $count -MaximumBytes 65536) { throw 'transport_failed' }
                    $stdoutTask = $process.StandardOutput.BaseStream.ReadAsync($stdoutBytes, 0, $stdoutBytes.Length, $cancellation.Token)
                }
            }
            if (-not $stderrDone -and $stderrTask.IsCompleted) {
                $count = $stderrTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stderrDone = $true } else {
                    if (Add-Phase15BoundedBytes -Buffer $stderr -Bytes $stderrBytes -Count $count -MaximumBytes 65536) { throw 'transport_failed' }
                    $stderrTask = $process.StandardError.BaseStream.ReadAsync($stderrBytes, 0, $stderrBytes.Length, $cancellation.Token)
                }
            }
            Start-Sleep -Milliseconds ([Math]::Min(10, $remaining))
        }
        if (-not (Test-Phase15TransportCompletion -ExitCode $process.ExitCode -StderrLength $stderr.Length)) { throw 'transport_failed' }
        return [Text.UTF8Encoding]::new($false, $true).GetString($stdout.ToArray())
    } catch {
        if ($Started.Value) {
            $remaining = Get-Phase15TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase15TransportBudgetMilliseconds
            Stop-Phase15TransportProcess -Process $process -WaitMilliseconds $remaining
        }
        throw
    } finally {
        if ($null -ne $cancellation) { $cancellation.Cancel() }
        if ($Started.Value) { try { $process.StandardInput.Close() } catch {} }
        if ($null -ne $cancellation) { $cancellation.Dispose() }
        if ($null -ne $stdout) { $stdout.Dispose() }
        if ($null -ne $stderr) { $stderr.Dispose() }
        if ($Started.Value -and -not $process.HasExited) {
            $remaining = Get-Phase15TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase15TransportBudgetMilliseconds
            Stop-Phase15TransportProcess -Process $process -WaitMilliseconds $remaining
        }
        $clock.Stop()
        $process.Dispose()
    }
}

function Write-Phase15CreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    Write-Phase15AtomicCreateNewJson -Path $Path -Value $Value -OwnerId $OwnerId
}

function Write-Phase15DurableBytes {
    param([Parameter(Mandatory)][object]$Stream, [Parameter(Mandatory)][byte[]]$Bytes)
    foreach ($value in $Bytes) { $Stream.WriteByte($value) }
    $Stream.Flush($true)
}

function Write-Phase15AtomicCreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    if ($OwnerId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'writer_owner_invalid' }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $temporaryPath = $fullPath + '.phase15-' + $OwnerId + '.create-' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase15CanonicalJsonText -Value $Value) + "`n")
    $stream = $null
    try {
        $stream = [IO.FileStream]::new($temporaryPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        Write-Phase15DurableBytes -Stream $stream -Bytes $bytes
        $stream.Dispose()
        $stream = $null
        [IO.File]::Move($temporaryPath, $fullPath)
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { [IO.File]::Delete($temporaryPath) }
    }
}

function Remove-Phase15TransactionTemps {
    param([Parameter(Mandatory)][string]$TransactionPath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'transaction_invalid' }
    $fullPath = [IO.Path]::GetFullPath($TransactionPath)
    $parent = [IO.Path]::GetDirectoryName($fullPath)
    $leaf = [IO.Path]::GetFileName($fullPath)
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { return }
    $owner = [regex]::Escape($ClaimId)
    $allowed = '^' + [regex]::Escape($leaf) + '\.phase15-' + $owner + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase15-' + $owner + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})$'
    foreach ($candidate in [IO.Directory]::EnumerateFiles($parent, $leaf + '.*', [IO.SearchOption]::TopDirectoryOnly)) {
        if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($candidate)) -cne $parent -or [IO.Path]::GetFileName($candidate) -cnotmatch $allowed) { continue }
        if (([IO.File]::GetAttributes($candidate) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
        [IO.File]::Delete($candidate)
    }
}

function Remove-Phase15OwnedStateResidues {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$OutcomePath,
        [string]$RecoveryOutcomePath,
        [Parameter(Mandatory)][string]$ClaimId
    )
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'transaction_invalid' }
    $targets = @(
        [pscustomobject]@{ Path = [IO.Path]::GetFullPath($LifecyclePath); Suffix = 'phase15-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.terminal-[0-9a-f]{32}(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})' },
        [pscustomobject]@{ Path = [IO.Path]::GetFullPath($OutcomePath); Suffix = 'phase15-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.pending-[0-9a-f]{32}(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.staged(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.reservation-backup-[0-9a-f]{32})' }
    )
    if (-not [string]::IsNullOrWhiteSpace($RecoveryOutcomePath)) {
        $targets += [pscustomobject]@{ Path = [IO.Path]::GetFullPath($RecoveryOutcomePath); Suffix = 'phase15-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase15-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})' }
    }
    foreach ($target in $targets) {
        $parent = [IO.Path]::GetDirectoryName($target.Path)
        $leaf = [IO.Path]::GetFileName($target.Path)
        if (-not (Test-Path -LiteralPath $parent -PathType Container)) { continue }
        $pattern = '^' + [regex]::Escape($leaf) + '\.' + $target.Suffix + '$'
        foreach ($candidate in [IO.Directory]::EnumerateFiles($parent, $leaf + '.*', [IO.SearchOption]::TopDirectoryOnly)) {
            if ([IO.Path]::GetFileName($candidate) -cnotmatch $pattern) { continue }
            if (([IO.File]::GetAttributes($candidate) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
            [IO.File]::Delete($candidate)
        }
    }
}

function Write-Phase15AtomicJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    if ($OwnerId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'writer_owner_invalid' }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $temporaryPath = $fullPath + '.phase15-' + $OwnerId + '.atomic-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $fullPath + '.phase15-' + $OwnerId + '.backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase15CreateNewJson -Path $temporaryPath -Value $Value -OwnerId $OwnerId
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            [IO.File]::Replace($temporaryPath, $fullPath, $backupPath, $true)
        } else {
            [IO.File]::Move($temporaryPath, $fullPath)
        }
    } finally {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { [IO.File]::Delete($temporaryPath) }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) { [IO.File]::Delete($backupPath) }
    }
}

function Get-Phase15LifecyclePath {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or [string]::IsNullOrWhiteSpace($LifecycleRoot)) { throw 'claim_lifecycle_invalid' }
    $root = [IO.Path]::GetFullPath($LifecycleRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $path = [IO.Path]::GetFullPath([IO.Path]::Combine($root, $ClaimId + '.json'))
    if ([IO.Path]::GetDirectoryName($path).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'claim_lifecycle_invalid' }
    return $path
}

function Get-Phase15StateDirectoryFacts {
    param([Parameter(Mandatory)][string]$Path)
    $fullPath = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $fullPath)) { return [pscustomobject]@{ Exists = $false; FullName = $fullPath } }
    $item = Get-Item -LiteralPath $fullPath -Force -ErrorAction Stop
    $acl = Get-Acl -LiteralPath $fullPath -ErrorAction Stop
    $rules = @($acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]) | ForEach-Object {
        [pscustomobject]@{
            Inheritance = [int]$_.InheritanceFlags
            IsInherited = [bool]$_.IsInherited
            Propagation = [int]$_.PropagationFlags
            Rights = [int64]$_.FileSystemRights
            Sid = $_.IdentityReference.Value
            Type = $_.AccessControlType.ToString()
        }
    })
    return [pscustomobject]@{
        Exists = $true
        FullName = [IO.Path]::GetFullPath($item.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar)
        IsDirectory = [bool]$item.PSIsContainer
        IsReparse = (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
        OwnerSid = $acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
        Protected = [bool]$acl.AreAccessRulesProtected
        Rules = $rules
    }
}

function Test-Phase15ProgramDataAnchorFacts {
    param([Parameter(Mandatory)][object]$Facts, [Parameter(Mandatory)][string]$ExpectedPath)
    if ($null -eq $Facts -or -not (Test-Phase15ExactProperties -Value $Facts -Required @('Exists','FullName','IsDirectory','IsReparse','OwnerSid','Protected','Rules'))) { return $false }
    if ($Facts.Exists -isnot [bool] -or -not $Facts.Exists -or $Facts.IsDirectory -isnot [bool] -or -not $Facts.IsDirectory -or $Facts.IsReparse -isnot [bool] -or $Facts.IsReparse) { return $false }
    if ($Facts.FullName -isnot [string] -or -not [IO.Path]::IsPathRooted($Facts.FullName) -or -not [IO.Path]::GetFullPath($Facts.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar).Equals([IO.Path]::GetFullPath($ExpectedPath).TrimEnd([IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { return $false }
    if ($Facts.OwnerSid -isnot [string] -or $Facts.OwnerSid -notin @($script:Phase15SystemSid, $script:Phase15AdministratorsSid)) { return $false }
    if ($Facts.Protected -isnot [bool] -or -not $Facts.Protected -or $Facts.Rules -isnot [System.Collections.IEnumerable]) { return $false }
    $expected = @(
        [pscustomobject]@{ Sid = 'S-1-3-0'; Rights = [int64]268435456; Inheritance = 3; Propagation = 2 },
        [pscustomobject]@{ Sid = $script:Phase15SystemSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = $script:Phase15AdministratorsSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]278; Inheritance = 1; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]1179817; Inheritance = 3; Propagation = 0 }
    )
    $rules = @($Facts.Rules)
    if ($rules.Count -ne $expected.Count) { return $false }
    foreach ($wanted in $expected) {
        $matching = @($rules | Where-Object { $_.Sid -is [string] -and $_.Sid -ceq $wanted.Sid -and [int64]$_.Rights -eq $wanted.Rights -and [int]$_.Inheritance -eq $wanted.Inheritance -and [int]$_.Propagation -eq $wanted.Propagation })
        if ($matching.Count -ne 1) { return $false }
        $rule = $matching[0]
        if (-not (Test-Phase15ExactProperties -Value $rule -Required @('Inheritance','IsInherited','Propagation','Rights','Sid','Type')) -or $rule.Type -isnot [string] -or $rule.Type -cne 'Allow' -or $rule.IsInherited -isnot [bool] -or $rule.IsInherited) { return $false }
    }
    return $true
}

function Test-Phase15ManagedStateDirectoryFacts {
    param([Parameter(Mandatory)][object]$Facts, [Parameter(Mandatory)][string]$ExpectedPath, [Parameter(Mandatory)][string]$AuthorizedSid)
    if ($AuthorizedSid -cnotmatch '^S-1-[0-9-]+$' -or $null -eq $Facts -or -not (Test-Phase15ExactProperties -Value $Facts -Required @('Exists','FullName','IsDirectory','IsReparse','OwnerSid','Protected','Rules'))) { return $false }
    if ($Facts.Exists -isnot [bool] -or -not $Facts.Exists -or $Facts.IsDirectory -isnot [bool] -or -not $Facts.IsDirectory -or $Facts.IsReparse -isnot [bool] -or $Facts.IsReparse) { return $false }
    if ($Facts.FullName -isnot [string] -or -not [IO.Path]::IsPathRooted($Facts.FullName) -or -not [IO.Path]::GetFullPath($Facts.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar).Equals([IO.Path]::GetFullPath($ExpectedPath).TrimEnd([IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { return $false }
    if ($Facts.OwnerSid -isnot [string] -or $Facts.OwnerSid -cne $AuthorizedSid -or $Facts.Protected -isnot [bool] -or -not $Facts.Protected) { return $false }
    $expectedSids = @($AuthorizedSid, $script:Phase15SystemSid, $script:Phase15AdministratorsSid)
    $rules = @($Facts.Rules)
    if ($rules.Count -ne $expectedSids.Count) { return $false }
    $fullControl = [int64][Security.AccessControl.FileSystemRights]::FullControl
    $inheritance = [int][Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [int][Security.AccessControl.InheritanceFlags]::ObjectInherit
    foreach ($sid in $expectedSids) {
        $matching = @($rules | Where-Object { $_.Sid -is [string] -and $_.Sid -ceq $sid })
        if ($matching.Count -ne 1) { return $false }
        $rule = $matching[0]
        if (-not (Test-Phase15ExactProperties -Value $rule -Required @('Inheritance','IsInherited','Propagation','Rights','Sid','Type'))) { return $false }
        if ($rule.Type -isnot [string] -or $rule.Type -cne 'Allow' -or [int64]$rule.Rights -ne $fullControl -or $rule.IsInherited -isnot [bool] -or $rule.IsInherited -or [int]$rule.Inheritance -ne $inheritance -or [int]$rule.Propagation -ne 0) { return $false }
    }
    return $true
}

function Enter-Phase15StateRootCreationLock {
    $mutex = [Threading.Mutex]::new($false, $script:Phase15StateRootCreationMutexName)
    $acquired = $false
    try {
        try { $acquired = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $acquired = $true }
        if (-not $acquired) { throw 'state_root_busy' }
        return [pscustomobject]@{ Acquired = $true; Mutex = $mutex }
    } catch {
        if (-not $acquired) { $mutex.Dispose() }
        throw
    }
}

function Exit-Phase15StateRootCreationLock {
    param([Parameter(Mandatory)][object]$Lock)
    if ($null -eq $Lock -or $Lock.Acquired -isnot [bool] -or -not $Lock.Acquired -or $null -eq $Lock.Mutex) { throw 'state_root_lock_invalid' }
    try { $Lock.Mutex.ReleaseMutex() } finally { $Lock.Mutex.Dispose() }
}

function New-Phase15SecureStateDirectory {
    param([Parameter(Mandatory)][string]$ParentPath, [Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$AuthorizedSid)
    $parent = [IO.Path]::GetFullPath($ParentPath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $target = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([IO.Path]::GetDirectoryName($target).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $parent -or $AuthorizedSid -cnotmatch '^S-1-[0-9-]+$') { throw 'state_root_invalid' }
    $security = [Security.AccessControl.DirectorySecurity]::new()
    $security.SetAccessRuleProtection($true, $false)
    $owner = [Security.Principal.SecurityIdentifier]::new($AuthorizedSid)
    $security.SetOwner($owner)
    $inheritance = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
    foreach ($sidValue in @($AuthorizedSid, $script:Phase15SystemSid, $script:Phase15AdministratorsSid)) {
        $sid = [Security.Principal.SecurityIdentifier]::new($sidValue)
        $rule = [Security.AccessControl.FileSystemAccessRule]::new($sid, [Security.AccessControl.FileSystemRights]::FullControl, $inheritance, [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
        [void]$security.AddAccessRule($rule)
    }
    $temporary = Join-Path $parent ('.phase15-state-root.create-' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [void][IO.Directory]::CreateDirectory($temporary, $security)
        $temporaryFacts = Get-Phase15StateDirectoryFacts -Path $temporary
        if (-not (Test-Phase15ManagedStateDirectoryFacts -Facts $temporaryFacts -ExpectedPath $temporary -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        try { [IO.Directory]::Move($temporary, $target) } catch [IO.IOException] {
            $existing = Get-Phase15StateDirectoryFacts -Path $target
            if (-not (Test-Phase15ManagedStateDirectoryFacts -Facts $existing -ExpectedPath $target -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        }
    } finally {
        $remaining = Get-Phase15StateDirectoryFacts -Path $temporary
        if ($remaining.Exists) {
            if (-not (Test-Phase15ManagedStateDirectoryFacts -Facts $remaining -ExpectedPath $temporary -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
            [IO.Directory]::Delete($temporary, $false)
        }
    }
}

function Initialize-Phase15TrustedStateRoot {
    param([Parameter(Mandatory)][string]$AnchorPath, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$AuthorizedSid)
    $anchor = [IO.Path]::GetFullPath($AnchorPath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $expectedRoot = [IO.Path]::Combine($anchor, 'AMN2', 'phase15', 'readonly-preflight')
    if (-not $root.Equals($expectedRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'state_root_invalid' }
    $lock = Enter-Phase15StateRootCreationLock
    try {
        $anchorFacts = Get-Phase15StateDirectoryFacts -Path $anchor
        if (-not (Test-Phase15ProgramDataAnchorFacts -Facts $anchorFacts -ExpectedPath $anchor)) { throw 'state_root_invalid' }
        $current = $anchor
        foreach ($leaf in @('AMN2','phase15','readonly-preflight')) {
            $next = [IO.Path]::Combine($current, $leaf)
            $facts = Get-Phase15StateDirectoryFacts -Path $next
            if (-not $facts.Exists) { New-Phase15SecureStateDirectory -ParentPath $current -Path $next -AuthorizedSid $AuthorizedSid; $facts = Get-Phase15StateDirectoryFacts -Path $next }
            if (-not (Test-Phase15ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $next -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
            $current = $next
        }
        foreach ($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes')) {
            $next = [IO.Path]::Combine($root, $leaf)
            $facts = Get-Phase15StateDirectoryFacts -Path $next
            if (-not $facts.Exists) { New-Phase15SecureStateDirectory -ParentPath $root -Path $next -AuthorizedSid $AuthorizedSid; $facts = Get-Phase15StateDirectoryFacts -Path $next }
            if (-not (Test-Phase15ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $next -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        }
        return $root
    } finally { Exit-Phase15StateRootCreationLock -Lock $lock }
}

function Get-Phase15ProductionStateRoot {
    return $script:Phase15ProductionStateRoot
}

function Initialize-Phase15ProductionStateRoot {
    $anchor = [Environment]::GetFolderPath([Environment+SpecialFolder]::CommonApplicationData)
    if ([string]::IsNullOrWhiteSpace($anchor) -or -not [IO.Path]::IsPathRooted($anchor)) { throw 'state_root_invalid' }
    $authorizedSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    return Initialize-Phase15TrustedStateRoot -AnchorPath $anchor -StateRoot $script:Phase15ProductionStateRoot -AuthorizedSid $authorizedSid
}

function Get-Phase15TransactionPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    return Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $StateRoot 'transactions') -ClaimId $ClaimId
}

function Get-Phase15ClaimLockPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    return Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $StateRoot 'locks') -ClaimId $ClaimId
}

function Enter-Phase15ClaimLock {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'claim_invalid' }
    foreach ($root in @($StateRoot, (Join-Path $StateRoot 'locks'), (Join-Path $StateRoot 'outcome-locks'))) {
        if (-not (Test-Path -LiteralPath $root)) { [void][IO.Directory]::CreateDirectory($root) }
        $item = Get-Item -LiteralPath $root -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    }
    $path = Get-Phase15ClaimLockPath -StateRoot $StateRoot -ClaimId $ClaimId
    try {
        $stream = [IO.FileStream]::new($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch [IO.IOException] { throw 'claim_replay' }
    return [pscustomobject]@{ ClaimId = $ClaimId; Path = $path; Stream = $stream }
}

function Test-Phase15ClaimLock {
    param([Parameter(Mandatory)][object]$Lock, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($null -eq $Lock -or -not (Test-Phase15ExactProperties -Value $Lock -Required @('ClaimId','Path','Stream'))) { return $false }
    $expected = Get-Phase15ClaimLockPath -StateRoot $StateRoot -ClaimId $ClaimId
    return $Lock.ClaimId -is [string] -and $Lock.ClaimId -ceq $ClaimId -and $Lock.Path -is [string] -and [IO.Path]::GetFullPath($Lock.Path) -ceq [IO.Path]::GetFullPath($expected) -and $Lock.Stream -is [IO.FileStream] -and $Lock.Stream.CanWrite
}

function Get-Phase15OutcomeLockPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $lockRoot = [IO.Path]::GetFullPath((Join-Path $root 'outcome-locks')).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([IO.Path]::GetDirectoryName($lockRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'outcome_lock_invalid' }
    $canonicalOutcome = [IO.Path]::GetFullPath($OutcomePath).TrimEnd([IO.Path]::DirectorySeparatorChar).ToUpperInvariant()
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($canonicalOutcome)
    $digest = Get-Phase15BytesSha256 -Bytes $bytes
    return [IO.Path]::Combine($lockRoot, $digest + '.lock')
}

function Enter-Phase15OutcomeLock {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'outcome_lock_invalid' }
    $lockRoot = Join-Path ([IO.Path]::GetFullPath($StateRoot)) 'outcome-locks'
    if (-not (Test-Path -LiteralPath $lockRoot -PathType Container)) { throw 'outcome_lock_invalid' }
    $lockItem = Get-Item -LiteralPath $lockRoot -Force -ErrorAction Stop
    if (($lockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'outcome_lock_invalid' }
    $path = Get-Phase15OutcomeLockPath -StateRoot $StateRoot -OutcomePath $OutcomePath
    try { $stream = [IO.FileStream]::new($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None) } catch [IO.IOException] { throw 'outcome_replay' }
    return [pscustomobject]@{ ClaimId = $ClaimId; OutcomePath = [IO.Path]::GetFullPath($OutcomePath); Path = $path; Stream = $stream }
}

function Test-Phase15OutcomeLock {
    param([Parameter(Mandatory)][object]$Lock, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId)
    if ($null -eq $Lock -or -not (Test-Phase15ExactProperties -Value $Lock -Required @('ClaimId','OutcomePath','Path','Stream'))) { return $false }
    $expectedPath = Get-Phase15OutcomeLockPath -StateRoot $StateRoot -OutcomePath $OutcomePath
    return (
        $Lock.ClaimId -is [string] -and $Lock.ClaimId -ceq $ClaimId -and
        $Lock.OutcomePath -is [string] -and [IO.Path]::GetFullPath($Lock.OutcomePath).Equals([IO.Path]::GetFullPath($OutcomePath), [StringComparison]::OrdinalIgnoreCase) -and
        $Lock.Path -is [string] -and [IO.Path]::GetFullPath($Lock.Path) -ceq [IO.Path]::GetFullPath($expectedPath) -and
        $Lock.Stream -is [IO.FileStream] -and $Lock.Stream.CanWrite
    )
}

function Reserve-Phase15Claim {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $ReservedAt)) { throw 'claim_invalid' }
    if (-not (Test-Path -LiteralPath $LifecycleRoot -PathType Container)) { throw 'claim_lifecycle_invalid' }
    $rootItem = Get-Item -LiteralPath $LifecycleRoot -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    $lifecyclePath = Get-Phase15LifecyclePath -LifecycleRoot $LifecycleRoot -ClaimId $ClaimId
    Write-Phase15CreateNewJson -Path $lifecyclePath -Value ([ordered]@{ claim_id = $ClaimId; reason_code = 'not_applicable'; reserved_at = $ReservedAt; status = 'reserved' }) -OwnerId $ClaimId
    return $lifecyclePath
}

function Reserve-Phase15OutcomeSlot {
    param([Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $ReservedAt)) { throw 'outcome_reservation_invalid' }
    $fullPath = [IO.Path]::GetFullPath($OutcomePath)
    $parent = [IO.Path]::GetDirectoryName($fullPath)
    if ([string]::IsNullOrWhiteSpace($parent) -or -not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'outcome_reservation_invalid' }
    Write-Phase15CreateNewJson -Path $fullPath -Value ([ordered]@{ claim_id = $ClaimId; reserved_at = $ReservedAt; status = 'reserved' }) -OwnerId $ClaimId
    return $fullPath
}

function Test-Phase15OutcomeOwnership {
    param([Parameter(Mandatory)][string]$ReservationPath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { return $false }
    $reservation = ConvertFrom-Phase15CanonicalJsonFile -Path $ReservationPath
    if ($null -eq $reservation -or -not (Test-Phase15ExactProperties -Value $reservation -Required @('claim_id','reserved_at','status'))) { return $false }
    return (
        $reservation.claim_id -is [string] -and $reservation.claim_id -ceq $ClaimId -and
        $reservation.status -is [string] -and $reservation.status -ceq 'reserved' -and
        $reservation.reserved_at -is [string] -and (Test-Phase15UtcTimestamp -Value $reservation.reserved_at)
    )
}

function Release-Phase15OutcomeSlot {
    param([Parameter(Mandatory)][string]$ReservationPath, [Parameter(Mandatory)][string]$ClaimId)
    if (Test-Phase15OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId) {
        [IO.File]::Delete($ReservationPath)
        if (Test-Path -LiteralPath $ReservationPath) { throw 'outcome_reservation_release_failed' }
    }
}

function Start-Phase15Transaction {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$OutcomePath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][object]$Lock
    )
    if ($ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $CollectorSha256 -cnotmatch '^[0-9a-f]{64}$' -or -not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost)) { throw 'transaction_invalid' }
    if (-not (Test-Phase15ClaimLock -Lock $Lock -StateRoot $StateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    if (-not (Test-Path -LiteralPath $StateRoot)) { [void][IO.Directory]::CreateDirectory($StateRoot) }
    $stateItem = Get-Item -LiteralPath $StateRoot -Force
    if (($stateItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
    $lifecycleRoot = Join-Path $StateRoot 'claims'
    $transactionRoot = Join-Path $StateRoot 'transactions'
    foreach ($root in @($lifecycleRoot, $transactionRoot)) {
        if (-not (Test-Path -LiteralPath $root)) { [void][IO.Directory]::CreateDirectory($root) }
        $item = Get-Item -LiteralPath $root -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
    }
    $reservationPath = [IO.Path]::GetFullPath($OutcomePath)
    $outcomeLock = Enter-Phase15OutcomeLock -StateRoot $StateRoot -OutcomePath $reservationPath -ClaimId $ClaimId
    try {
        $lifecyclePath = Get-Phase15LifecyclePath -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId
        $journalPath = Get-Phase15TransactionPath -StateRoot $StateRoot -ClaimId $ClaimId
        Remove-Phase15TransactionTemps -TransactionPath $journalPath -ClaimId $ClaimId
        Remove-Phase15OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $reservationPath -ClaimId $ClaimId
        $stagedPath = $reservationPath + '.phase15-' + $ClaimId + '.staged'
        if (Test-Path -LiteralPath $lifecyclePath) { throw 'claim_replay' }
        if (Test-Path -LiteralPath $journalPath) { throw 'transaction_pending' }
        if (Test-Path -LiteralPath $reservationPath) { throw 'outcome_reservation_invalid' }
        $journal = [ordered]@{
            claim_id = $ClaimId
            collector_sha256 = $CollectorSha256
            expected_host = $ExpectedHost
            manifest_sha256 = $ManifestSha256
            outcome_path = $reservationPath
            phase = 'owned'
            reserved_at = $ReservedAt
            schema = 'amn2.phase15.readonly-preflight-transaction.v1'
            ssh_used = $false
            staged_path = $stagedPath
            terminal_ended_at = $null
            terminal_outcome_sha256 = $null
            terminal_path = $null
            terminal_reason_code = $null
            terminal_status = $null
        }
        Write-Phase15AtomicCreateNewJson -Path $journalPath -Value $journal -OwnerId $ClaimId
        $createdReservation = Reserve-Phase15OutcomeSlot -OutcomePath $reservationPath -ClaimId $ClaimId -ReservedAt $ReservedAt
        $createdLifecycle = Reserve-Phase15Claim -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId -ReservedAt $ReservedAt
        return [pscustomobject]@{ JournalPath = $journalPath; LifecyclePath = $createdLifecycle; OutcomeLock = $outcomeLock; ReservationPath = $createdReservation; StagedPath = $stagedPath }
    } catch {
        $outcomeLock.Stream.Dispose()
        throw
    }
}

function Set-Phase15TransactionPhase {
    param(
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][ValidateSet('owned','transport_attempted','ssh_started','outcome_staged','finalizing')][string]$Phase,
        [Parameter(Mandatory)][object]$Lock
    )
    $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
    if (-not (Test-Phase15ClaimLock -Lock $Lock -StateRoot $stateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    $journal = ConvertFrom-Phase15CanonicalJsonFile -Path $TransactionPath
    if ($null -eq $journal -or $journal.claim_id -isnot [string] -or $journal.claim_id -cne $ClaimId -or $journal.phase -isnot [string]) { throw 'transaction_invalid' }
    $phases = @('owned','transport_attempted','ssh_started','outcome_staged','finalizing')
    $currentPhaseIndex = [Array]::IndexOf($phases, [string]$journal.phase)
    $nextPhaseIndex = [Array]::IndexOf($phases, $Phase)
    if ($currentPhaseIndex -lt 0 -or $nextPhaseIndex -lt 0 -or $nextPhaseIndex -lt $currentPhaseIndex) { throw 'transaction_invalid' }
    $journal.phase = $Phase
    if ($nextPhaseIndex -ge 1) { $journal.ssh_used = $true }
    Write-Phase15AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
    return $TransactionPath
}

function Reconcile-Phase15Transaction {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$EndedAt,
        [Parameter(Mandatory)][object]$Lock,
        [object]$OutcomeLock
    )
    if (-not (Test-Phase15UtcTimestamp -Value $EndedAt)) { throw 'transaction_invalid' }
    if (-not (Test-Phase15ClaimLock -Lock $Lock -StateRoot $StateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    $transactionRoot = Join-Path $StateRoot 'transactions'
    if (-not (Test-Path -LiteralPath $transactionRoot -PathType Container)) { return [pscustomobject]@{ Recovered = $false; OutcomePath = $null } }
    $journalPath = Get-Phase15TransactionPath -StateRoot $StateRoot -ClaimId $ClaimId
    Remove-Phase15TransactionTemps -TransactionPath $journalPath -ClaimId $ClaimId
    if (-not (Test-Path -LiteralPath $journalPath -PathType Leaf)) { return [pscustomobject]@{ Recovered = $false; OutcomePath = $null } }
    $journal = ConvertFrom-Phase15CanonicalJsonFile -Path $journalPath
    $required = @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','ssh_used','staged_path','terminal_ended_at','terminal_outcome_sha256','terminal_path','terminal_reason_code','terminal_status')
    if ($null -eq $journal -or -not (Test-Phase15ExactProperties -Value $journal -Required $required)) { throw 'transaction_invalid' }
    foreach ($field in @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','staged_path')) {
        if ($journal.$field -isnot [string]) { throw 'transaction_invalid' }
    }
    if ($journal.ssh_used -isnot [bool]) { throw 'transaction_invalid' }
    $terminalValues = @($journal.terminal_ended_at, $journal.terminal_outcome_sha256, $journal.terminal_path, $journal.terminal_reason_code, $journal.terminal_status)
    if (@($terminalValues | Where-Object { $null -ne $_ }).Count -notin @(0, 5)) { throw 'transaction_invalid' }
    if ($null -ne $journal.terminal_status -and (
        $journal.terminal_ended_at -isnot [string] -or -not (Test-Phase15UtcTimestamp -Value $journal.terminal_ended_at) -or
        $journal.terminal_outcome_sha256 -isnot [string] -or $journal.terminal_outcome_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        $journal.terminal_path -isnot [string] -or $journal.terminal_reason_code -isnot [string] -or $journal.terminal_status -isnot [string] -or
        $journal.terminal_status -notin @('completed','failed')
    )) { throw 'transaction_invalid' }
    if ($journal.claim_id -cne $ClaimId -or $journal.schema -cne 'amn2.phase15.readonly-preflight-transaction.v1') { throw 'transaction_invalid' }
    $phaseValid = $journal.phase -in @('owned','transport_attempted','ssh_started','outcome_staged','finalizing')
    if ($journal.manifest_sha256 -cnotmatch '^[0-9a-f]{64}$' -or $journal.collector_sha256 -cnotmatch '^[0-9a-f]{64}$' -or -not (Test-Phase15ExpectedHost -ExpectedHost $journal.expected_host) -or -not (Test-Phase15UtcTimestamp -Value $journal.reserved_at)) { throw 'transaction_invalid' }
    $expectedStagedPath = [IO.Path]::GetFullPath($journal.outcome_path) + '.phase15-' + $ClaimId + '.staged'
    if ([IO.Path]::GetFullPath($journal.staged_path) -cne $expectedStagedPath) { throw 'transaction_invalid' }
    $ownsOutcomeLock = $false
    if ($null -eq $OutcomeLock) {
        $OutcomeLock = Enter-Phase15OutcomeLock -StateRoot $StateRoot -OutcomePath $journal.outcome_path -ClaimId $ClaimId
        $ownsOutcomeLock = $true
    } elseif (-not (Test-Phase15OutcomeLock -Lock $OutcomeLock -StateRoot $StateRoot -OutcomePath $journal.outcome_path -ClaimId $ClaimId)) { throw 'outcome_lock_invalid' }
    try {
    $lifecycleRoot = Join-Path $StateRoot 'claims'
    if (-not (Test-Path -LiteralPath $lifecycleRoot)) { [void][IO.Directory]::CreateDirectory($lifecycleRoot) }
    $lifecyclePath = Get-Phase15LifecyclePath -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId
    $recoveryRoot = Join-Path $StateRoot 'recovery-outcomes'
    $recoveryOutcomePath = Get-Phase15LifecyclePath -LifecycleRoot $recoveryRoot -ClaimId $ClaimId
    Remove-Phase15OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
    if ($null -ne $journal.terminal_path) {
        $published = ConvertFrom-Phase15CanonicalJsonFile -Path $journal.terminal_path
        $lifecycle = ConvertFrom-Phase15CanonicalJsonFile -Path $lifecyclePath
        $lifecycleValid = $null -ne $lifecycle -and (Test-Phase15ExactProperties -Value $lifecycle -Required @('claim_id','ended_at','reason_code','status'))
        $publishedDigest = if ($null -ne $published) { Get-Phase15CanonicalJsonSha256 -Value $published } else { '' }
        if ($lifecycleValid -and $publishedDigest -ceq $journal.terminal_outcome_sha256 -and $lifecycle.claim_id -ceq $ClaimId -and $lifecycle.status -ceq $journal.terminal_status -and $lifecycle.reason_code -ceq $journal.terminal_reason_code -and $lifecycle.ended_at -ceq $journal.terminal_ended_at) {
            if (Test-Path -LiteralPath $journal.staged_path -PathType Leaf) { [IO.File]::Delete($journal.staged_path) }
            [IO.File]::Delete($journalPath)
            return [pscustomobject]@{ Recovered = $true; OutcomePath = [IO.Path]::GetFullPath($journal.terminal_path) }
        }
    }
    $sshUsed = if ($phaseValid) { [bool]$journal.ssh_used } else { $true }
    $failure = New-Phase15FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 $journal.manifest_sha256 -CollectorSha256 $journal.collector_sha256 -ExpectedHost $journal.expected_host -StartedAt $journal.reserved_at -EndedAt $EndedAt -SshUsed $sshUsed
    if (Test-Phase15OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId) {
        $publishedPath = [IO.Path]::GetFullPath($journal.outcome_path)
    } else {
        if (-not (Test-Path -LiteralPath $recoveryRoot)) { [void][IO.Directory]::CreateDirectory($recoveryRoot) }
        $recoveryItem = Get-Item -LiteralPath $recoveryRoot -Force
        if (($recoveryItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
        $publishedPath = $recoveryOutcomePath
    }
    $journal.phase = 'finalizing'
    $journal.terminal_ended_at = $EndedAt
    $journal.terminal_outcome_sha256 = Get-Phase15CanonicalJsonSha256 -Value $failure
    $journal.terminal_path = $publishedPath
    $journal.terminal_reason_code = 'transport_failed'
    $journal.terminal_status = 'failed'
    Write-Phase15AtomicJson -Path $journalPath -Value $journal -OwnerId $ClaimId
    $terminal = [ordered]@{ claim_id = $ClaimId; ended_at = $EndedAt; reason_code = 'transport_failed'; status = 'failed' }
    Write-Phase15AtomicJson -Path $lifecyclePath -Value $terminal -OwnerId $ClaimId
    Write-Phase15AtomicJson -Path $publishedPath -Value $failure -OwnerId $ClaimId
    if (Test-Path -LiteralPath $journal.staged_path -PathType Leaf) { [IO.File]::Delete($journal.staged_path) }
    [IO.File]::Delete($journalPath)
    if (Test-Path -LiteralPath $journalPath) { throw 'transaction_reconciliation_failed' }
    return [pscustomobject]@{ Recovered = $true; OutcomePath = $publishedPath }
    } finally {
        if ($ownsOutcomeLock) { $OutcomeLock.Stream.Dispose() }
    }
}

function Set-Phase15ClaimTerminal {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][ValidateSet('completed','failed')][string]$Status,
        [Parameter(Mandatory)][string]$EndedAt,
        [Parameter(Mandatory)][string]$ReasonCode
    )
    if (-not (Test-Path -LiteralPath $LifecyclePath -PathType Leaf) -or -not (Test-Phase15UtcTimestamp -Value $EndedAt)) { throw 'claim_lifecycle_invalid' }
    if (($Status -ceq 'completed' -and $ReasonCode -cne 'not_applicable') -or ($Status -ceq 'failed' -and $ReasonCode -cnotin $script:Phase15FailureReasons)) { throw 'claim_lifecycle_invalid' }
    $current = ConvertFrom-Phase15CanonicalJsonFile -Path $LifecyclePath
    if ($null -eq $current -or $current.claim_id -cne $ClaimId -or $current.status -notin @('reserved','completed','failed')) { throw 'claim_lifecycle_invalid' }
    if ($Status -ceq 'completed' -and $current.status -cne 'reserved') { throw 'claim_lifecycle_invalid' }
    $temporaryPath = $LifecyclePath + '.phase15-' + $ClaimId + '.terminal-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $LifecyclePath + '.phase15-' + $ClaimId + '.backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase15CreateNewJson -Path $temporaryPath -Value ([ordered]@{ claim_id = $ClaimId; ended_at = $EndedAt; reason_code = $ReasonCode; status = $Status }) -OwnerId $ClaimId
        [IO.File]::Replace($temporaryPath, $LifecyclePath, $backupPath, $true)
    } finally {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { Remove-Item -LiteralPath $temporaryPath -Force }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) { Remove-Item -LiteralPath $backupPath -Force }
    }
    return $LifecyclePath
}

function Publish-Phase15TerminalOutcome {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$ReservationPath,
        [Parameter(Mandatory)][string]$OutcomePath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][ValidateSet('completed','failed')][string]$Status,
        [Parameter(Mandatory)][string]$EndedAt,
        [Parameter(Mandatory)][string]$ReasonCode,
        [Parameter(Mandatory)][object]$Outcome,
        [string]$TransactionPath,
        [object]$Lock,
        [object]$OutcomeLock
    )
    if ([IO.Path]::GetFullPath($ReservationPath) -cne [IO.Path]::GetFullPath($OutcomePath) -or -not (Test-Phase15OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
    if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) {
        $journal = ConvertFrom-Phase15CanonicalJsonFile -Path $TransactionPath
        $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
        if (-not (Test-Phase15ClaimLock -Lock $Lock -StateRoot $stateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
        if (-not (Test-Phase15OutcomeLock -Lock $OutcomeLock -StateRoot $stateRoot -OutcomePath $OutcomePath -ClaimId $ClaimId)) { throw 'outcome_lock_invalid' }
        if ($null -eq $journal -or $journal.claim_id -cne $ClaimId -or $journal.outcome_path -cne [IO.Path]::GetFullPath($OutcomePath) -or $journal.phase -notin @('ssh_started','transport_attempted')) { throw 'transaction_invalid' }
        $pendingPath = [string]$journal.staged_path
        $journal.terminal_ended_at = $EndedAt
        $journal.terminal_outcome_sha256 = Get-Phase15CanonicalJsonSha256 -Value $Outcome
        $journal.terminal_path = [IO.Path]::GetFullPath($OutcomePath)
        $journal.terminal_reason_code = $ReasonCode
        $journal.terminal_status = $Status
        Write-Phase15AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
    } else {
        $pendingPath = $OutcomePath + '.phase15-' + $ClaimId + '.pending-' + [Guid]::NewGuid().ToString('N')
    }
    $backupPath = $OutcomePath + '.phase15-' + $ClaimId + '.reservation-backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase15CreateNewJson -Path $pendingPath -Value $Outcome -OwnerId $ClaimId
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Set-Phase15TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'outcome_staged' -Lock $Lock) }
        [void](Set-Phase15ClaimTerminal -LifecyclePath $LifecyclePath -ClaimId $ClaimId -Status $Status -EndedAt $EndedAt -ReasonCode $ReasonCode)
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Set-Phase15TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'finalizing' -Lock $Lock) }
        if (-not (Test-Phase15OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
        [IO.File]::Replace($pendingPath, $OutcomePath, $backupPath, $true)
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) {
            [IO.File]::Delete($TransactionPath)
            if (Test-Path -LiteralPath $TransactionPath) { throw 'transaction_finalize_failed' }
        }
    } finally {
        if (Test-Path -LiteralPath $pendingPath -PathType Leaf) { Remove-Item -LiteralPath $pendingPath -Force }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) { Remove-Item -LiteralPath $backupPath -Force }
    }
}

function New-Phase15FailureOutcome {
    param([string]$ReasonCode, [string]$ManifestSha256, [string]$CollectorSha256, [string]$ExpectedHost, [string]$StartedAt, [string]$EndedAt, [bool]$SshUsed)
    if ($ReasonCode -cnotin $script:Phase15FailureReasons) { throw 'failure_reason_invalid' }
    return [ordered]@{
        collector_sha256 = $CollectorSha256
        decision = 'stop'
        ended_at = $EndedAt
        expected_host = $ExpectedHost
        manifest_sha256 = $ManifestSha256
        package_id = $script:Phase15PackageId
        reason_code = $ReasonCode
        safety = [ordered]@{ live_mutation = $false; raw_output_persisted = $false; remote_file_written = $false; ssh_used = $SshUsed }
        schema = $script:Phase15FailureSchema
        started_at = $StartedAt
        transport_disposition = $(if ($SshUsed) { 'read_only_failed' } else { 'not_run' })
    }
}

function Invoke-Phase15RunnerMain {
    if (-not $FutureAuthorization -or [string]::IsNullOrWhiteSpace($FutureClaimPath)) { throw 'future_claim_required' }
    if ([string]::IsNullOrWhiteSpace($PackageRoot) -or [string]::IsNullOrWhiteSpace($OutcomePath) -or -not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost)) { throw 'runner_arguments_invalid' }
    $outcomeParent = Split-Path -Parent ([IO.Path]::GetFullPath($OutcomePath))
    if (-not (Test-Path -LiteralPath $outcomeParent -PathType Container)) { throw 'runner_arguments_invalid' }
    $startedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $manifestPath = Join-Path $PackageRoot 'manifest.json'
    $collectorPath = Join-Path $PackageRoot 'tooling\scripts\vps\phase15_spain_readonly_preflight_remote.sh'
    $manifestArtifact = Read-Phase15ManifestArtifact -Path $manifestPath
    $manifest = $manifestArtifact.Value
    if ($null -eq $manifest -or $manifest.package_id -cne $script:Phase15PackageId) { throw 'package_identity_invalid' }
    $manifestSha256 = $manifestArtifact.Sha256
    $collectorArtifact = Read-Phase15CollectorArtifact -Path $collectorPath
    $collectorSha256 = $collectorArtifact.Sha256
    $entry = @($manifest.entries | Where-Object { $_.path -ceq 'tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh' })
    if ($entry.Count -ne 1 -or $entry[0].sha256 -cne $collectorSha256) { throw 'collector_checksum_invalid' }
    [void](Assert-Phase15SpainTrustBundle -ExpectedHost $ExpectedHost)
    $claim = Read-Phase15FutureClaim -ClaimPath $FutureClaimPath
    if ($null -eq $claim -or -not (Test-Phase15ClaimIdentity -Claim $claim -ExpectedPackageId $script:Phase15PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost)) { throw 'claim_invalid' }
    $stateRoot = Initialize-Phase15ProductionStateRoot
    $claimLock = Enter-Phase15ClaimLock -StateRoot $stateRoot -ClaimId $claim.claim_id
    $transaction = $null
    try {
        $reconciled = Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $startedAt -Lock $claimLock
        if ($reconciled.Recovered) { throw 'claim_replay' }
        $lifecyclePath = Get-Phase15LifecyclePath -LifecycleRoot (Join-Path $stateRoot 'claims') -ClaimId $claim.claim_id
        if (Test-Path -LiteralPath $lifecyclePath) { throw 'claim_replay' }
        $reservationAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
        if (-not (Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId $script:Phase15PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -At $reservationAt)) { throw 'claim_invalid' }
        $transaction = Start-Phase15Transaction -StateRoot $stateRoot -OutcomePath $OutcomePath -ClaimId $claim.claim_id -ReservedAt $reservationAt -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -Lock $claimLock
        $sshUsed = $false
        $failureReason = 'transport_failed'
        $transportStarted = $false
        try {
            [void](Set-Phase15TransactionPhase -TransactionPath $transaction.JournalPath -ClaimId $claim.claim_id -Phase 'transport_attempted' -Lock $claimLock)
            $rawDocument = Invoke-Phase15OneSshTransport -ExpectedHost $ExpectedHost -CollectorBytes $collectorArtifact.Bytes -ClaimId $claim.claim_id -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -Started ([ref]$transportStarted) -TransactionPath $transaction.JournalPath -Lock $claimLock
            $sshUsed = $transportStarted
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            $document = ConvertFrom-Phase15CanonicalJsonText -Text $rawDocument
            if ($null -eq $document) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            if (-not (Test-Phase15CollectorDocument -Document $document -ExpectedHost $ExpectedHost -ExpectedClaimId $claim.claim_id -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -StartedAt $startedAt -EndedAt $endedAt)) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            $evidence = ConvertTo-Phase15Evidence -Document $document -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt
            Publish-Phase15TerminalOutcome -LifecyclePath $transaction.LifecyclePath -ReservationPath $transaction.ReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'completed' -EndedAt $endedAt -ReasonCode 'not_applicable' -Outcome $evidence -TransactionPath $transaction.JournalPath -Lock $claimLock -OutcomeLock $transaction.OutcomeLock
        } catch {
            $sshUsed = $sshUsed -or $transportStarted
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            try {
                if (Test-Phase15OutcomeOwnership -ReservationPath $transaction.ReservationPath -ClaimId $claim.claim_id) {
                    $failure = New-Phase15FailureOutcome -ReasonCode $failureReason -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt -SshUsed $sshUsed
                    Publish-Phase15TerminalOutcome -LifecyclePath $transaction.LifecyclePath -ReservationPath $transaction.ReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'failed' -EndedAt $endedAt -ReasonCode $failureReason -Outcome $failure -TransactionPath $transaction.JournalPath -Lock $claimLock -OutcomeLock $transaction.OutcomeLock
                } elseif (Test-Path -LiteralPath $transaction.JournalPath -PathType Leaf) {
                    [void](Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $endedAt -Lock $claimLock -OutcomeLock $transaction.OutcomeLock)
                }
            } catch {
                if (Test-Path -LiteralPath $transaction.JournalPath -PathType Leaf) {
                    [void](Reconcile-Phase15Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $endedAt -Lock $claimLock -OutcomeLock $transaction.OutcomeLock)
                }
            }
            throw
        }
    } finally {
        if ($null -ne $transaction -and $null -ne $transaction.OutcomeLock) { $transaction.OutcomeLock.Stream.Dispose() }
        $claimLock.Stream.Dispose()
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-Phase15RunnerMain
        exit 0
    } catch {
        [Console]::Error.WriteLine('AMN2_PHASE15_PREFLIGHT_RUNNER_STOP')
        exit 64
    }
}
