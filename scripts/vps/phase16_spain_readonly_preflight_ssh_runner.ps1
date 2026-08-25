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

$script:Phase16PackageId = 'phase16-awg3-family-3-1-spain-pilot-20260824-010'
$script:Phase16ClaimSchema = 'amn2.phase16.readonly-preflight-claim.v1'
$script:Phase16CollectorSchema = 'amn2.phase16.spain-readonly-collector.v1'
$script:Phase16EvidenceSchema = 'amn2.phase16.readonly-preflight-evidence.v1'
$script:Phase16FailureSchema = 'amn2.phase16.readonly-preflight-failure.v1'
$script:Phase16ProductionStateRoot = 'C:\ProgramData\AMN2\phase16\readonly-preflight'
$script:Phase16StateRootCreationMutexName = 'Global\AMN2-Phase16-ReadonlyPreflight-StateRoot-v1'
$script:Phase16SystemSid = 'S-1-5-18'
$script:Phase16AdministratorsSid = 'S-1-5-32-544'
$script:Phase16AuthorizationClock = $null
$script:Phase16TrustedBundleRunId = 'spain-fresh-20260720-001'
$script:Phase16SpainTargetUser = 'root'
$script:Phase16SpainHostKeySha256 = 'SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU'
$script:Phase16MaximumArtifactBytes = 1048576
$script:Phase16TransportOperationMilliseconds = 60000
$script:Phase16TransportBudgetMilliseconds = 65000
$script:Phase16MaximumFutureClockSkewSeconds = 15
$script:Phase16ObservationNames = @(
    'application_state','architecture','awg2_health','backup_capability','bridge_amn2sp3br0',
    'config_path','container_capability','container_cidr_172_29_252_0_28','container_name',
    'database_state','disk_space','firewall','interface_awg3','os_compatibility','python_3_12',
    'recovery_markers_phase14_phase15_phase16','routes','service_capability','service_name','state_root',
    'telegram_prerequisites','udp_30002','vpn_cidr_10_212_13_0_24'
)
$script:Phase16StopReasons = @('identity_mismatch','observation_failed','recovery_incomplete','resource_conflict')
$script:Phase16FailureReasons = @('claim_invalid','collector_failed','identity_mismatch','observation_ambiguous','schema_invalid','transport_failed')
$script:Phase16ConflictNames = @('bridge_amn2sp3br0','config_path','container_cidr_172_29_252_0_28','container_name','firewall','interface_awg3','routes','service_name','state_root','udp_30002','vpn_cidr_10_212_13_0_24')

function Get-Phase16BytesSha256 {
    param([Parameter(Mandatory)][AllowEmptyCollection()][byte[]]$Bytes)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $digest = $algorithm.ComputeHash($Bytes) } finally { $algorithm.Dispose() }
    return ([BitConverter]::ToString($digest)).Replace('-', '').ToLowerInvariant()
}

function Complete-Phase16VoidTask {
    param([Parameter(Mandatory)][Threading.Tasks.Task]$Task)
    [void]$Task.GetAwaiter().GetResult()
}

function Get-Phase16CanonicalJsonSha256 {
    param([Parameter(Mandatory)][object]$Value)
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase16CanonicalJsonText -Value $Value) + "`n")
    return Get-Phase16BytesSha256 -Bytes $bytes
}

function Read-Phase16BoundedFileBytes {
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

function Read-Phase16ManifestArtifact {
    param([Parameter(Mandatory)][string]$Path)
    $bytes = Read-Phase16BoundedFileBytes -Path $Path -MaximumBytes $script:Phase16MaximumArtifactBytes
    try {
        $text = [Text.UTF8Encoding]::new($false, $true).GetString($bytes)
        $value = ConvertFrom-Phase16CanonicalJsonText -Text $text
    } catch { throw 'manifest_invalid' }
    if ($null -eq $value) { throw 'manifest_invalid' }
    return [pscustomobject]@{ Bytes = [byte[]]$bytes; Sha256 = Get-Phase16BytesSha256 -Bytes $bytes; Value = $value }
}

function Read-Phase16CollectorArtifact {
    param([Parameter(Mandatory)][string]$Path)
    $bytes = Read-Phase16BoundedFileBytes -Path $Path -MaximumBytes $script:Phase16MaximumArtifactBytes
    return [pscustomobject]@{
        Bytes = [byte[]]$bytes
        Sha256 = Get-Phase16BytesSha256 -Bytes $bytes
    }
}

function ConvertTo-Phase16CanonicalJsonText {
    param([Parameter(Mandatory = $false)][AllowNull()][object]$Value)
    if ($null -eq $Value) { return 'null' }
    if ($Value -is [string] -or $Value -is [char]) {
        return (ConvertTo-Json -InputObject ([string]$Value) -Compress)
    }
    if ($Value -is [bool]) { return $Value.ToString().ToLowerInvariant() }
    if ($Value -is [System.Collections.IDictionary]) {
        $parts = foreach ($key in @($Value.Keys | ForEach-Object { [string]$_ } | Sort-Object)) {
            (ConvertTo-Json -InputObject $key -Compress) + ':' + (ConvertTo-Phase16CanonicalJsonText -Value $Value[$key])
        }
        return '{' + ($parts -join ',') + '}'
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        $parts = foreach ($item in $Value) { ConvertTo-Phase16CanonicalJsonText -Value $item }
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
        (ConvertTo-Json -InputObject ([string]$property.Name) -Compress) + ':' + (ConvertTo-Phase16CanonicalJsonText -Value $property.Value)
    }
    return '{' + ($parts -join ',') + '}'
}

function ConvertFrom-Phase16CanonicalJsonFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $bytes = Read-Phase16BoundedFileBytes -Path $Path -MaximumBytes $script:Phase16MaximumArtifactBytes
        $strictUtf8 = [Text.UTF8Encoding]::new($false, $true)
        $text = $strictUtf8.GetString($bytes)
        $value = $text | ConvertFrom-Json
        if ((ConvertTo-Phase16CanonicalJsonText -Value $value) + "`n" -cne $text) { return $null }
        return $value
    } catch {
        return $null
    }
}

function ConvertFrom-Phase16CanonicalJsonText {
    param([Parameter(Mandatory)][string]$Text)
    try {
        $value = $Text | ConvertFrom-Json
        if ((ConvertTo-Phase16CanonicalJsonText -Value $value) + "`n" -cne $Text) { return $null }
        return $value
    } catch { return $null }
}

function ConvertFrom-Phase16JsonFile {
    param([Parameter(Mandatory)][string]$Path)
    return ConvertFrom-Phase16CanonicalJsonFile -Path $Path
}

function Read-Phase16FutureClaim {
    param([Parameter(Mandatory)][string]$ClaimPath)
    return ConvertFrom-Phase16CanonicalJsonFile -Path $ClaimPath
}

function Test-Phase16ExpectedHost {
    param([Parameter(Mandatory)][string]$ExpectedHost)
    return $ExpectedHost -cmatch '^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$'
}

function Test-Phase16ExactProperties {
    param([Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string[]]$Required)
    if ($null -eq $Value) { return $false }
    $actual = @($Value.PSObject.Properties.Name | Sort-Object)
    $expected = @($Required | Sort-Object)
    return ($actual -join '|') -ceq ($expected -join '|')
}

function Test-Phase16UtcTimestamp {
    param([Parameter(Mandatory)][object]$Value)
    if ($Value -isnot [string]) { return $false }
    try {
        $parsed = [DateTimeOffset]::ParseExact($Value, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        return $parsed.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') -ceq $Value
    } catch { return $false }
}

function Test-Phase16ClaimIdentity {
    param(
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ExpectedPackageId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost
    )
    if ($ExpectedPackageId -cne $script:Phase16PackageId) { return $false }
    if ($ExpectedManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $ExpectedCollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
    if (-not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost)) { return $false }
    $required = @('claim_id','collector_sha256','consumed_at','expected_host','expires_at','future_gate','issued_at','manifest_sha256','package_id','schema','status')
    if (-not (Test-Phase16ExactProperties -Value $Claim -Required $required)) { return $false }
    foreach ($field in @('claim_id','collector_sha256','expected_host','expires_at','future_gate','issued_at','manifest_sha256','package_id','schema','status')) {
        if ($Claim.$field -isnot [string]) { return $false }
    }
    if ($Claim.schema -cne $script:Phase16ClaimSchema -or $Claim.package_id -cne $ExpectedPackageId) { return $false }
    if ($Claim.manifest_sha256 -cne $ExpectedManifestSha256 -or $Claim.collector_sha256 -cne $ExpectedCollectorSha256) { return $false }
    if ($Claim.expected_host -cne $ExpectedHost -or $Claim.claim_id -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { return $false }
    if ($Claim.future_gate -cne 'PREFLIGHT' -or $Claim.status -cne 'issued' -or $null -ne $Claim.consumed_at) { return $false }
    if (-not (Test-Phase16UtcTimestamp -Value $Claim.issued_at) -or -not (Test-Phase16UtcTimestamp -Value $Claim.expires_at)) { return $false }
    $issued = [DateTimeOffset]::ParseExact($Claim.issued_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    $expires = [DateTimeOffset]::ParseExact($Claim.expires_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    if ($issued -ge $expires) { return $false }
    return $true
}

function Test-Phase16FutureClaim {
    param(
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ExpectedPackageId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [string]$At
    )
    if (-not (Test-Phase16ClaimIdentity -Claim $Claim -ExpectedPackageId $ExpectedPackageId -ExpectedManifestSha256 $ExpectedManifestSha256 -ExpectedCollectorSha256 $ExpectedCollectorSha256 -ExpectedHost $ExpectedHost)) { return $false }
    if ([string]::IsNullOrWhiteSpace($At)) { $atValue = [DateTimeOffset]::UtcNow } elseif (-not (Test-Phase16UtcTimestamp -Value $At)) { return $false } else {
        $atValue = [DateTimeOffset]::ParseExact($At, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    }
    $issued = [DateTimeOffset]::ParseExact($Claim.issued_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    $expires = [DateTimeOffset]::ParseExact($Claim.expires_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
    return $issued -le $atValue -and $atValue -lt $expires
}

function Get-Phase16AuthorizationInstant {
    $now = if ($null -eq $script:Phase16AuthorizationClock) { [DateTimeOffset]::UtcNow } else { & $script:Phase16AuthorizationClock }
    if ($now -isnot [DateTimeOffset]) { throw 'clock_invalid' }
    return $now
}

function Test-Phase16CollectorDocument {
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
        if (-not (Test-Phase16ExactProperties -Value $Document -Required $required)) { return $false }
        foreach ($field in @('claim_id','collector_sha256','decision','host_identity','manifest_sha256','observed_at','package_id','schema')) {
            if ($Document.$field -isnot [string]) { return $false }
        }
        if ($Document.schema -cne $script:Phase16CollectorSchema -or $Document.package_id -cne $script:Phase16PackageId) { return $false }
        if ($ExpectedManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $ExpectedCollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
        if ($Document.manifest_sha256 -isnot [string] -or $Document.collector_sha256 -isnot [string]) { return $false }
        if ($Document.manifest_sha256 -cne $ExpectedManifestSha256 -or $Document.collector_sha256 -cne $ExpectedCollectorSha256) { return $false }
        if (-not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost) -or $Document.host_identity -cne $ExpectedHost -or $Document.claim_id -cne $ExpectedClaimId) { return $false }
        if ($ExpectedClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase16UtcTimestamp -Value $Document.observed_at) -or -not (Test-Phase16UtcTimestamp -Value $StartedAt) -or -not (Test-Phase16UtcTimestamp -Value $EndedAt)) { return $false }
        $observed = [DateTimeOffset]::ParseExact($Document.observed_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $started = [DateTimeOffset]::ParseExact($StartedAt, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $ended = [DateTimeOffset]::ParseExact($EndedAt, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $maximumObserved = $ended.AddSeconds($script:Phase16MaximumFutureClockSkewSeconds)
        if ($ended -lt $started -or $observed -lt $started -or $observed -gt $maximumObserved) { return $false }
        if ($Document.decision -isnot [string] -or $Document.decision -cnotin @('pass','stop')) { return $false }
        if (-not (Test-Phase16ExactProperties -Value $Document.safety -Required @('live_mutation','raw_output_persisted','remote_file_written'))) { return $false }
        if ($Document.safety.live_mutation -isnot [bool] -or $Document.safety.remote_file_written -isnot [bool] -or $Document.safety.raw_output_persisted -isnot [bool]) { return $false }
        if ($Document.safety.live_mutation -ne $false -or $Document.safety.remote_file_written -ne $false -or $Document.safety.raw_output_persisted -ne $false) { return $false }
        if ($Document.blocking_reasons -isnot [System.Array] -or $Document.observations -isnot [System.Array]) { return $false }
        $reasons = @($Document.blocking_reasons)
        if (@($reasons | Where-Object { $_ -isnot [string] }).Count -ne 0) { return $false }
        if (($reasons -join '|') -cne (@($reasons | Sort-Object -Unique) -join '|')) { return $false }
        if (@($reasons | Where-Object { $_ -cnotin $script:Phase16StopReasons }).Count -ne 0) { return $false }
        $observations = @($Document.observations)
        if ($observations.Count -ne $script:Phase16ObservationNames.Count) { return $false }
        $names = @()
        $mustStop = $false
        $states = @{}
        foreach ($item in $observations) {
            if (-not (Test-Phase16ExactProperties -Value $item -Required @('name','observation_sha256','state'))) { return $false }
            if ($item.name -isnot [string] -or $item.observation_sha256 -isnot [string] -or $item.state -isnot [string]) { return $false }
            if ($item.name -cnotin $script:Phase16ObservationNames -or $item.observation_sha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
            if ($item.state -cnotin @('absent','free','pass','present','stop','unknown')) { return $false }
            if ($item.state -in @('stop','unknown')) { $mustStop = $true }
            $names += [string]$item.name
            $states[[string]$item.name] = [string]$item.state
        }
        if (($names -join '|') -cne ($script:Phase16ObservationNames -join '|')) { return $false }
        $expectedReasons = @()
        if ($states['recovery_markers_phase14_phase15_phase16'] -in @('stop','unknown')) { $expectedReasons += 'recovery_incomplete' }
        if (@($script:Phase16ConflictNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'resource_conflict' }
        $ordinaryNames = @($script:Phase16ObservationNames | Where-Object { $_ -cnotin $script:Phase16ConflictNames -and $_ -cne 'recovery_markers_phase14_phase15_phase16' })
        if (@($ordinaryNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'observation_failed' }
        $expectedReasons = @($expectedReasons | Sort-Object -Unique)
        $hasReasons = $expectedReasons.Count -gt 0
        if (($reasons -join '|') -cne ($expectedReasons -join '|')) { return $false }
        if (($Document.decision -ceq 'stop') -ne $hasReasons -or $mustStop -ne $hasReasons) { return $false }
        return $true
    } catch { return $false }
}

function ConvertTo-Phase16Evidence {
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
        package_id = $script:Phase16PackageId
        safety = [ordered]@{ live_mutation = $false; raw_output_persisted = $false; remote_file_written = $false; ssh_used = $true }
        schema = $script:Phase16EvidenceSchema
        started_at = $StartedAt
        stop_reasons = @($Document.blocking_reasons | ForEach-Object { [string]$_ })
        transport_disposition = 'read_only_completed'
    }
}

function Get-Phase16SpainTrustContract {
    $localAppData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    if ([string]::IsNullOrWhiteSpace($localAppData) -or -not [IO.Path]::IsPathRooted($localAppData)) { throw 'trust_binding_invalid' }
    $trustRoot = Join-Path $localAppData "AMN2\private-artifacts\post-release\spain-migration\$($script:Phase16TrustedBundleRunId)"
    return [pscustomobject]@{
        ExpectedHostKeySha256 = $script:Phase16SpainHostKeySha256
        KeyPath = Join-Path $trustRoot 'id_ed25519_spain'
        KnownHostsPath = Join-Path $trustRoot 'known_hosts_spain'
        TargetUser = $script:Phase16SpainTargetUser
        AnchorPath = $localAppData
        TrustRoot = $trustRoot
    }
}

function Assert-Phase16TrustAnchor {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [IO.Path]::IsPathRooted($Path)) { throw 'trust_binding_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or [IO.Path]::GetFullPath($item.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar)) { throw 'trust_binding_invalid' }
}

function Get-Phase16TrustParentPaths {
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

function Assert-Phase16TrustPath {
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

function Test-Phase16PrivateKeyBytes {
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

function Assert-Phase16SpainTrustBundle {
    param([Parameter(Mandatory)][string]$ExpectedHost)
    if (-not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost)) { throw 'trust_binding_invalid' }
    $contract = Get-Phase16SpainTrustContract
    $currentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    Assert-Phase16TrustAnchor -Path $contract.AnchorPath
    foreach ($parentPath in @(Get-Phase16TrustParentPaths -AnchorPath $contract.AnchorPath -TrustRoot $contract.TrustRoot)) {
        Assert-Phase16TrustPath -Path $parentPath -ExpectedOwnerSid $currentSid
    }
    Assert-Phase16TrustPath -Path $contract.KeyPath -ExpectedOwnerSid $currentSid -RequireLeaf
    Assert-Phase16TrustPath -Path $contract.KnownHostsPath -ExpectedOwnerSid $currentSid -RequireLeaf
    [byte[]]$keyBytes = $null
    [byte[]]$knownHostsBytes = $null
    try {
        $keyBytes = Read-Phase16BoundedFileBytes -Path $contract.KeyPath -MaximumBytes 16384
        $knownHostsBytes = Read-Phase16BoundedFileBytes -Path $contract.KnownHostsPath -MaximumBytes 4096
        if (-not (Test-Phase16PrivateKeyBytes -Bytes $keyBytes) -or @($knownHostsBytes | Where-Object { $_ -gt 127 }).Count -ne 0) { throw 'trust_binding_invalid' }
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

function Assert-Phase16LocalExecutable {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [IO.Path]::IsPathRooted($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw 'local_executable_invalid' }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -lt 1 -or $item.Length -gt 33554432) { throw 'local_executable_invalid' }
}

function Get-Phase16PowerShell5StdinFilterCode {
    return 'import hashlib,sys; source=sys.stdin.buffer; data=source.read(1048580); bom=bytes((239,187,191)); len(data)<=1048579 or sys.exit(65); data=data[3:] if data.startswith(bom) else data; data and not data.startswith(bom) and hashlib.sha256(data).hexdigest()==sys.argv[1] or sys.exit(65); sys.stdout.buffer.write(data)'
}

function New-Phase16SshArguments {
    param([Parameter(Mandatory)][string]$ExpectedHost, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ManifestSha256, [Parameter(Mandatory)][string]$CollectorSha256)
    if (-not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost) -or $ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or $ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $CollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'transport_envelope_invalid' }
    $contract = Get-Phase16SpainTrustContract
    $filterCode = Get-Phase16PowerShell5StdinFilterCode
    $remote = '/usr/bin/bash -o pipefail -c ''/usr/bin/python3 -I -B -c "{0}" "$3" | /usr/bin/bash -s -- "$@"'' -- ''{1}'' ''{2}'' ''{3}'' ''{4}'' ''{5}''' -f $filterCode,$script:Phase16PackageId,$ManifestSha256,$CollectorSha256,$ClaimId,$ExpectedHost
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

function ConvertTo-Phase16WindowsArgument {
    param([Parameter(Mandatory)][string]$Argument)
    $escaped = $Argument.Replace('\', '\')
    $escaped = $escaped.Replace('"', '\"')
    return '"' + $escaped + '"'
}

function Get-Phase16ValidatedProgramDataEnvironmentValue {
    $candidate = $env:ProgramData
    if ([string]::IsNullOrWhiteSpace($candidate)) { throw 'local_environment_invalid' }
    try {
        $expected = [IO.Path]::GetFullPath('C:\ProgramData').TrimEnd([IO.Path]::DirectorySeparatorChar)
        $actual = [IO.Path]::GetFullPath($candidate).TrimEnd([IO.Path]::DirectorySeparatorChar)
    } catch {
        throw 'local_environment_invalid'
    }
    if (-not $actual.Equals($expected, [StringComparison]::OrdinalIgnoreCase)) { throw 'local_environment_invalid' }
    return 'C:\ProgramData'
}

function New-Phase16SshProcessStartInfo {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $programData = Get-Phase16ValidatedProgramDataEnvironmentValue
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'C:\Windows\System32\OpenSSH\ssh.exe'
    Assert-Phase16LocalExecutable -Path $start.FileName
    $start.Arguments = ($Arguments | ForEach-Object { ConvertTo-Phase16WindowsArgument -Argument $_ }) -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.EnvironmentVariables.Clear()
    $start.EnvironmentVariables['SYSTEMROOT'] = $env:SystemRoot
    $start.EnvironmentVariables['WINDIR'] = $env:WINDIR
    $start.EnvironmentVariables['PATH'] = 'C:\Windows\System32\OpenSSH;C:\Windows\System32'
    $start.EnvironmentVariables['PROGRAMDATA'] = $programData
    $start.EnvironmentVariables['HOME'] = 'C:\ProgramData\AMN2\phase16\no-ambient-home'
    $start.EnvironmentVariables['USERPROFILE'] = 'C:\ProgramData\AMN2\phase16\no-ambient-profile'
    return $start
}

function Add-Phase16BoundedBytes {
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

function Test-Phase16TransportCompletion {
    param([Parameter(Mandatory)][int]$ExitCode, [Parameter(Mandatory)][long]$StderrLength)
    return $ExitCode -eq 0 -and $StderrLength -eq 0
}

function Stop-Phase16TransportProcess {
    param([Parameter(Mandatory)][object]$Process, [int]$WaitMilliseconds = 2000)
    if (-not $Process.HasExited) { $Process.Kill() }
    if (-not $Process.WaitForExit($WaitMilliseconds)) { throw 'transport_child_retained' }
}

function Get-Phase16TransportRemainingMilliseconds {
    param([Parameter(Mandatory)][Diagnostics.Stopwatch]$Clock, [Parameter(Mandatory)][int]$DeadlineMilliseconds)
    if ($DeadlineMilliseconds -lt 1) { throw 'transport_deadline_invalid' }
    $remaining = [long]$DeadlineMilliseconds - [long]$Clock.ElapsedMilliseconds
    if ($remaining -le 0) { return 0 }
    return [int][Math]::Min([int]::MaxValue, $remaining)
}

function Test-Phase16ExactNonterminalTransactionJournal {
    param(
        [Parameter(Mandatory)][object]$Journal,
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][ValidateSet('owned','transport_attempted','ssh_started')][string]$ExpectedPhase,
        [Parameter(Mandatory)][bool]$ExpectedSshUsed
    )
    try {
        $required = @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','ssh_used','staged_path','started_at','terminal_ended_at','terminal_outcome_sha256','terminal_path','terminal_reason_code','terminal_status')
        if ($null -eq $Journal -or -not (Test-Phase16ExactProperties -Value $Journal -Required $required)) { return $false }
        foreach ($field in @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','staged_path','started_at')) {
            if ($Journal.$field -isnot [string]) { return $false }
        }
        if ($Journal.ssh_used -isnot [bool]) { return $false }
        $terminalValues = @($Journal.terminal_ended_at,$Journal.terminal_outcome_sha256,$Journal.terminal_path,$Journal.terminal_reason_code,$Journal.terminal_status)
        if (@($terminalValues | Where-Object { $null -ne $_ }).Count -ne 0) { return $false }
        $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
        $expectedTransactionPath = Get-Phase16TransactionPath -StateRoot $stateRoot -ClaimId $ClaimId
        $expectedOutcomeFullPath = [IO.Path]::GetFullPath($ExpectedOutcomePath)
        $expectedStagedPath = $expectedOutcomeFullPath + '.phase16-' + $ClaimId + '.staged'
        return (
            [IO.Path]::GetFullPath($TransactionPath) -ceq [IO.Path]::GetFullPath($expectedTransactionPath) -and
            $Journal.schema -ceq 'amn2.phase16.readonly-preflight-transaction.v2' -and
            $Journal.claim_id -ceq $ClaimId -and
            $Journal.manifest_sha256 -ceq $ManifestSha256 -and $Journal.manifest_sha256 -cmatch '^[0-9a-f]{64}$' -and
            $Journal.collector_sha256 -ceq $CollectorSha256 -and $Journal.collector_sha256 -cmatch '^[0-9a-f]{64}$' -and
            $Journal.expected_host -ceq $ExpectedHost -and (Test-Phase16ExpectedHost -ExpectedHost $Journal.expected_host) -and
            $Journal.outcome_path -ceq $expectedOutcomeFullPath -and $Journal.staged_path -ceq $expectedStagedPath -and
            $Journal.reserved_at -ceq $ReservedAt -and (Test-Phase16UtcTimestamp -Value $Journal.reserved_at) -and
            (Test-Phase16UtcTimestamp -Value $Journal.started_at) -and
            $Journal.phase -ceq $ExpectedPhase -and $Journal.ssh_used -eq $ExpectedSshUsed
        )
    } catch {
        return $false
    }
}

function Reset-Phase16UnstartedTransaction {
    param(
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][object]$Lock
    )
    $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
    if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $stateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $TransactionPath
    if (-not (Test-Phase16ExactNonterminalTransactionJournal -Journal $journal -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -ExpectedPhase 'transport_attempted' -ExpectedSshUsed $true)) { throw 'transaction_invalid' }
    $journal.phase = 'owned'
    $journal.ssh_used = $false
    Write-Phase16AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
    return $TransactionPath
}

function Test-Phase16TransactionRequiresConservativeSshUsed {
    param(
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][object]$Lock
    )
    try {
        $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
        if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $stateRoot -ClaimId $ClaimId)) { return $true }
        $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $TransactionPath
        return -not (Test-Phase16ExactNonterminalTransactionJournal -Journal $journal -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -ExpectedPhase 'owned' -ExpectedSshUsed $false)
    } catch {
        return $true
    }
}

function Start-Phase16AuthorizedSshProcess {
    param(
        [Parameter(Mandatory)][object]$Process,
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][object]$Lock
    )
    [void](Set-Phase16TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'transport_attempted' -Lock $Lock)
    $launchNow = Get-Phase16AuthorizationInstant
    $launchAt = $launchNow.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    if (-not (Test-Phase16FutureClaim -Claim $Claim -ExpectedPackageId $script:Phase16PackageId -ExpectedManifestSha256 $ManifestSha256 -ExpectedCollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -At $launchAt)) {
        [void](Reset-Phase16UnstartedTransaction -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -Lock $Lock)
        throw 'claim_invalid'
    }
    return $Process.Start()
}

function Invoke-Phase16OneSshTransport {
    param(
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][byte[]]$CollectorBytes,
        [Parameter(Mandatory)][object]$Claim,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][ref]$Started,
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][object]$Lock
    )
    $Started.Value = $false
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $sshArguments = New-Phase16SshArguments -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256
    $start = New-Phase16SshProcessStartInfo -Arguments $sshArguments
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    $stdout = $null
    $stderr = $null
    $cancellation = $null
    try {
        if (-not (Start-Phase16AuthorizedSshProcess -Process $process -Claim $Claim -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedOutcomePath $ExpectedOutcomePath -ReservedAt $ReservedAt -TransactionPath $TransactionPath -Lock $Lock)) { throw 'transport_failed' }
        $Started.Value = $true
        [void](Set-Phase16TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'ssh_started' -Lock $Lock)
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
            $remaining = Get-Phase16TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase16TransportOperationMilliseconds
            if ($remaining -le 0) { $cancellation.Cancel(); throw 'transport_failed' }
            if (-not $stdinDone -and $stdinTask.IsCompleted) {
                Complete-Phase16VoidTask -Task $stdinTask
                $process.StandardInput.Close()
                $stdinDone = $true
            }
            if (-not $stdoutDone -and $stdoutTask.IsCompleted) {
                $count = $stdoutTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stdoutDone = $true } else {
                    if (Add-Phase16BoundedBytes -Buffer $stdout -Bytes $stdoutBytes -Count $count -MaximumBytes 65536) { throw 'transport_failed' }
                    $stdoutTask = $process.StandardOutput.BaseStream.ReadAsync($stdoutBytes, 0, $stdoutBytes.Length, $cancellation.Token)
                }
            }
            if (-not $stderrDone -and $stderrTask.IsCompleted) {
                $count = $stderrTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stderrDone = $true } else {
                    if (Add-Phase16BoundedBytes -Buffer $stderr -Bytes $stderrBytes -Count $count -MaximumBytes 65536) { throw 'transport_failed' }
                    $stderrTask = $process.StandardError.BaseStream.ReadAsync($stderrBytes, 0, $stderrBytes.Length, $cancellation.Token)
                }
            }
            Start-Sleep -Milliseconds ([Math]::Min(10, $remaining))
        }
        if (-not (Test-Phase16TransportCompletion -ExitCode $process.ExitCode -StderrLength $stderr.Length)) { throw 'transport_failed' }
        return [Text.UTF8Encoding]::new($false, $true).GetString($stdout.ToArray())
    } catch {
        if ($Started.Value) {
            $remaining = Get-Phase16TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase16TransportBudgetMilliseconds
            Stop-Phase16TransportProcess -Process $process -WaitMilliseconds $remaining
        }
        throw
    } finally {
        if ($null -ne $cancellation) { $cancellation.Cancel() }
        if ($Started.Value) { try { $process.StandardInput.Close() } catch {} }
        if ($null -ne $cancellation) { $cancellation.Dispose() }
        if ($null -ne $stdout) { $stdout.Dispose() }
        if ($null -ne $stderr) { $stderr.Dispose() }
        if ($Started.Value -and -not $process.HasExited) {
            $remaining = Get-Phase16TransportRemainingMilliseconds -Clock $clock -DeadlineMilliseconds $script:Phase16TransportBudgetMilliseconds
            Stop-Phase16TransportProcess -Process $process -WaitMilliseconds $remaining
        }
        $clock.Stop()
        $process.Dispose()
    }
}

function Write-Phase16CreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    Write-Phase16AtomicCreateNewJson -Path $Path -Value $Value -OwnerId $OwnerId
}

function Write-Phase16DurableBytes {
    param([Parameter(Mandatory)][object]$Stream, [Parameter(Mandatory)][byte[]]$Bytes)
    foreach ($value in $Bytes) { $Stream.WriteByte($value) }
    $Stream.Flush($true)
}

function Write-Phase16AtomicCreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    if ($OwnerId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'writer_owner_invalid' }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $temporaryPath = $fullPath + '.phase16-' + $OwnerId + '.create-' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase16CanonicalJsonText -Value $Value) + "`n")
    $stream = $null
    try {
        $stream = [IO.FileStream]::new($temporaryPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        Write-Phase16DurableBytes -Stream $stream -Bytes $bytes
        $stream.Dispose()
        $stream = $null
        [IO.File]::Move($temporaryPath, $fullPath)
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { [IO.File]::Delete($temporaryPath) }
    }
}

function Remove-Phase16TransactionTemps {
    param([Parameter(Mandatory)][string]$TransactionPath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'transaction_invalid' }
    $fullPath = [IO.Path]::GetFullPath($TransactionPath)
    $parent = [IO.Path]::GetDirectoryName($fullPath)
    $leaf = [IO.Path]::GetFileName($fullPath)
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { return }
    $owner = [regex]::Escape($ClaimId)
    $allowed = '^' + [regex]::Escape($leaf) + '\.phase16-' + $owner + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase16-' + $owner + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})$'
    foreach ($candidate in [IO.Directory]::EnumerateFiles($parent, $leaf + '.*', [IO.SearchOption]::TopDirectoryOnly)) {
        if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($candidate)) -cne $parent -or [IO.Path]::GetFileName($candidate) -cnotmatch $allowed) { continue }
        if (([IO.File]::GetAttributes($candidate) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
        [IO.File]::Delete($candidate)
    }
}

function Get-Phase16OwnedStateResiduePaths {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$OutcomePath,
        [string]$RecoveryOutcomePath,
        [Parameter(Mandatory)][string]$ClaimId
    )
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'transaction_invalid' }
    $targets = @(
        [pscustomobject]@{ Path = [IO.Path]::GetFullPath($LifecyclePath); Suffix = 'phase16-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.terminal-[0-9a-f]{32}(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})' },
        [pscustomobject]@{ Path = [IO.Path]::GetFullPath($OutcomePath); Suffix = 'phase16-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.pending-[0-9a-f]{32}(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.staged(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.(?:backup|reservation-backup|recovery-backup)-[0-9a-f]{32})' }
    )
    if (-not [string]::IsNullOrWhiteSpace($RecoveryOutcomePath)) {
        $targets += [pscustomobject]@{ Path = [IO.Path]::GetFullPath($RecoveryOutcomePath); Suffix = 'phase16-' + [regex]::Escape($ClaimId) + '(?:\.create-[0-9a-f]{32}\.tmp|\.atomic-[0-9a-f]{32}(?:\.phase16-' + [regex]::Escape($ClaimId) + '\.create-[0-9a-f]{32}\.tmp)?|\.backup-[0-9a-f]{32})' }
    }
    $residuePaths = [Collections.Generic.List[string]]::new()
    foreach ($target in $targets) {
        $parent = [IO.Path]::GetDirectoryName($target.Path)
        $leaf = [IO.Path]::GetFileName($target.Path)
        if (-not (Test-Path -LiteralPath $parent -PathType Container)) { continue }
        $pattern = '^' + [regex]::Escape($leaf) + '\.' + $target.Suffix + '$'
        foreach ($candidate in [IO.Directory]::EnumerateFiles($parent, $leaf + '.*', [IO.SearchOption]::TopDirectoryOnly)) {
            if ([IO.Path]::GetFileName($candidate) -cnotmatch $pattern) { continue }
            if (([IO.File]::GetAttributes($candidate) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
            [void]$residuePaths.Add([IO.Path]::GetFullPath($candidate))
        }
    }
    return @($residuePaths)
}

function Assert-Phase16OwnedStateResiduesAbsent {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$OutcomePath,
        [string]$RecoveryOutcomePath,
        [Parameter(Mandatory)][string]$ClaimId
    )
    if (@(Get-Phase16OwnedStateResiduePaths -LifecyclePath $LifecyclePath -OutcomePath $OutcomePath -RecoveryOutcomePath $RecoveryOutcomePath -ClaimId $ClaimId).Count -ne 0) {
        throw 'transaction_finalize_failed'
    }
}

function Remove-Phase16OwnedStateResidues {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$OutcomePath,
        [string]$RecoveryOutcomePath,
        [Parameter(Mandatory)][string]$ClaimId
    )
    foreach ($candidate in @(Get-Phase16OwnedStateResiduePaths -LifecyclePath $LifecyclePath -OutcomePath $OutcomePath -RecoveryOutcomePath $RecoveryOutcomePath -ClaimId $ClaimId)) {
        [IO.File]::Delete($candidate)
    }
    Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $LifecyclePath -OutcomePath $OutcomePath -RecoveryOutcomePath $RecoveryOutcomePath -ClaimId $ClaimId
}

function Write-Phase16AtomicJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value, [Parameter(Mandatory)][string]$OwnerId)
    if ($OwnerId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'writer_owner_invalid' }
    $fullPath = [IO.Path]::GetFullPath($Path)
    $temporaryPath = $fullPath + '.phase16-' + $OwnerId + '.atomic-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $fullPath + '.phase16-' + $OwnerId + '.backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase16CreateNewJson -Path $temporaryPath -Value $Value -OwnerId $OwnerId
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

function Get-Phase16LifecyclePath {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or [string]::IsNullOrWhiteSpace($LifecycleRoot)) { throw 'claim_lifecycle_invalid' }
    $root = [IO.Path]::GetFullPath($LifecycleRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $path = [IO.Path]::GetFullPath([IO.Path]::Combine($root, $ClaimId + '.json'))
    if ([IO.Path]::GetDirectoryName($path).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'claim_lifecycle_invalid' }
    return $path
}

function Get-Phase16StateDirectoryFacts {
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

function Test-Phase16ProgramDataAnchorFacts {
    param([Parameter(Mandatory)][object]$Facts, [Parameter(Mandatory)][string]$ExpectedPath)
    if ($null -eq $Facts -or -not (Test-Phase16ExactProperties -Value $Facts -Required @('Exists','FullName','IsDirectory','IsReparse','OwnerSid','Protected','Rules'))) { return $false }
    if ($Facts.Exists -isnot [bool] -or -not $Facts.Exists -or $Facts.IsDirectory -isnot [bool] -or -not $Facts.IsDirectory -or $Facts.IsReparse -isnot [bool] -or $Facts.IsReparse) { return $false }
    if ($Facts.FullName -isnot [string] -or -not [IO.Path]::IsPathRooted($Facts.FullName) -or -not [IO.Path]::GetFullPath($Facts.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar).Equals([IO.Path]::GetFullPath($ExpectedPath).TrimEnd([IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { return $false }
    if ($Facts.OwnerSid -isnot [string] -or $Facts.OwnerSid -notin @($script:Phase16SystemSid, $script:Phase16AdministratorsSid)) { return $false }
    if ($Facts.Protected -isnot [bool] -or -not $Facts.Protected -or $Facts.Rules -isnot [System.Collections.IEnumerable]) { return $false }
    $expected = @(
        [pscustomobject]@{ Sid = 'S-1-3-0'; Rights = [int64]268435456; Inheritance = 3; Propagation = 2 },
        [pscustomobject]@{ Sid = $script:Phase16SystemSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = $script:Phase16AdministratorsSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]278; Inheritance = 1; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]1179817; Inheritance = 3; Propagation = 0 }
    )
    $rules = @($Facts.Rules)
    if ($rules.Count -ne $expected.Count) { return $false }
    foreach ($wanted in $expected) {
        $matching = @($rules | Where-Object { $_.Sid -is [string] -and $_.Sid -ceq $wanted.Sid -and [int64]$_.Rights -eq $wanted.Rights -and [int]$_.Inheritance -eq $wanted.Inheritance -and [int]$_.Propagation -eq $wanted.Propagation })
        if ($matching.Count -ne 1) { return $false }
        $rule = $matching[0]
        if (-not (Test-Phase16ExactProperties -Value $rule -Required @('Inheritance','IsInherited','Propagation','Rights','Sid','Type')) -or $rule.Type -isnot [string] -or $rule.Type -cne 'Allow' -or $rule.IsInherited -isnot [bool] -or $rule.IsInherited) { return $false }
    }
    return $true
}

function Test-Phase16ManagedStateDirectoryFacts {
    param([Parameter(Mandatory)][object]$Facts, [Parameter(Mandatory)][string]$ExpectedPath, [Parameter(Mandatory)][string]$AuthorizedSid)
    if ($AuthorizedSid -cnotmatch '^S-1-[0-9-]+$' -or $null -eq $Facts -or -not (Test-Phase16ExactProperties -Value $Facts -Required @('Exists','FullName','IsDirectory','IsReparse','OwnerSid','Protected','Rules'))) { return $false }
    if ($Facts.Exists -isnot [bool] -or -not $Facts.Exists -or $Facts.IsDirectory -isnot [bool] -or -not $Facts.IsDirectory -or $Facts.IsReparse -isnot [bool] -or $Facts.IsReparse) { return $false }
    if ($Facts.FullName -isnot [string] -or -not [IO.Path]::IsPathRooted($Facts.FullName) -or -not [IO.Path]::GetFullPath($Facts.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar).Equals([IO.Path]::GetFullPath($ExpectedPath).TrimEnd([IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { return $false }
    if ($Facts.OwnerSid -isnot [string] -or $Facts.OwnerSid -cne $AuthorizedSid -or $Facts.Protected -isnot [bool] -or -not $Facts.Protected) { return $false }
    $expectedSids = @(Get-Phase16AllowedStateSids -AuthorizedSid $AuthorizedSid)
    $rules = @($Facts.Rules)
    if ($rules.Count -ne $expectedSids.Count) { return $false }
    $fullControl = [int64][Security.AccessControl.FileSystemRights]::FullControl
    $inheritance = [int][Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [int][Security.AccessControl.InheritanceFlags]::ObjectInherit
    foreach ($sid in $expectedSids) {
        $matching = @($rules | Where-Object { $_.Sid -is [string] -and $_.Sid -ceq $sid })
        if ($matching.Count -ne 1) { return $false }
        $rule = $matching[0]
        if (-not (Test-Phase16ExactProperties -Value $rule -Required @('Inheritance','IsInherited','Propagation','Rights','Sid','Type'))) { return $false }
        if ($rule.Type -isnot [string] -or $rule.Type -cne 'Allow' -or [int64]$rule.Rights -ne $fullControl -or $rule.IsInherited -isnot [bool] -or $rule.IsInherited -or [int]$rule.Inheritance -ne $inheritance -or [int]$rule.Propagation -ne 0) { return $false }
    }
    return $true
}

function Test-Phase16SharedNamespaceDirectoryFacts {
    param([Parameter(Mandatory)][object]$Facts, [Parameter(Mandatory)][string]$ExpectedPath)
    if ($null -eq $Facts -or -not (Test-Phase16ExactProperties -Value $Facts -Required @('Exists','FullName','IsDirectory','IsReparse','OwnerSid','Protected','Rules'))) { return $false }
    if ($Facts.Exists -isnot [bool] -or -not $Facts.Exists -or $Facts.IsDirectory -isnot [bool] -or -not $Facts.IsDirectory -or $Facts.IsReparse -isnot [bool] -or $Facts.IsReparse) { return $false }
    if ($Facts.FullName -isnot [string] -or -not [IO.Path]::IsPathRooted($Facts.FullName) -or -not [IO.Path]::GetFullPath($Facts.FullName).TrimEnd([IO.Path]::DirectorySeparatorChar).Equals([IO.Path]::GetFullPath($ExpectedPath).TrimEnd([IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) { return $false }
    if ($Facts.OwnerSid -isnot [string] -or $Facts.OwnerSid -notin @($script:Phase16SystemSid, $script:Phase16AdministratorsSid)) { return $false }
    if ($Facts.Protected -isnot [bool] -or $Facts.Protected -or $Facts.Rules -isnot [System.Collections.IEnumerable]) { return $false }
    $expected = @(
        [pscustomobject]@{ Sid = 'S-1-3-0'; Rights = [int64]268435456; Inheritance = 3; Propagation = 2 },
        [pscustomobject]@{ Sid = $script:Phase16SystemSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = $script:Phase16AdministratorsSid; Rights = [int64]2032127; Inheritance = 3; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]278; Inheritance = 1; Propagation = 0 },
        [pscustomobject]@{ Sid = 'S-1-5-32-545'; Rights = [int64]1179817; Inheritance = 3; Propagation = 0 }
    )
    $rules = @($Facts.Rules)
    if ($rules.Count -ne $expected.Count) { return $false }
    foreach ($wanted in $expected) {
        $matching = @($rules | Where-Object { $_.Sid -is [string] -and $_.Sid -ceq $wanted.Sid -and [int64]$_.Rights -eq $wanted.Rights -and [int]$_.Inheritance -eq $wanted.Inheritance -and [int]$_.Propagation -eq $wanted.Propagation })
        if ($matching.Count -ne 1) { return $false }
        $rule = $matching[0]
        if (-not (Test-Phase16ExactProperties -Value $rule -Required @('Inheritance','IsInherited','Propagation','Rights','Sid','Type')) -or $rule.Type -isnot [string] -or $rule.Type -cne 'Allow' -or $rule.IsInherited -isnot [bool] -or -not $rule.IsInherited) { return $false }
    }
    return $true
}

function Get-Phase16AllowedStateSids {
    param([Parameter(Mandatory)][string]$AuthorizedSid)
    if ($AuthorizedSid -cnotmatch '^S-1-[0-9-]+$') { throw 'state_root_invalid' }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $ordered = [Collections.Generic.List[string]]::new()
    foreach ($sid in @($AuthorizedSid, $script:Phase16SystemSid, $script:Phase16AdministratorsSid)) {
        if ($seen.Add($sid)) { [void]$ordered.Add($sid) }
    }
    return [string[]]$ordered.ToArray()
}

function New-Phase16ManagedStateDirectorySecurity {
    param([Parameter(Mandatory)][string]$AuthorizedSid)
    $allowedSids = @(Get-Phase16AllowedStateSids -AuthorizedSid $AuthorizedSid)
    $security = [Security.AccessControl.DirectorySecurity]::new()
    $security.SetAccessRuleProtection($true, $false)
    $security.SetOwner([Security.Principal.SecurityIdentifier]::new($AuthorizedSid))
    $inheritance = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
    foreach ($sidValue in $allowedSids) {
        $sid = [Security.Principal.SecurityIdentifier]::new($sidValue)
        $rule = [Security.AccessControl.FileSystemAccessRule]::new($sid, [Security.AccessControl.FileSystemRights]::FullControl, $inheritance, [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
        [void]$security.AddAccessRule($rule)
    }
    return $security
}

function Enter-Phase16StateRootCreationLock {
    $mutex = [Threading.Mutex]::new($false, $script:Phase16StateRootCreationMutexName)
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

function Exit-Phase16StateRootCreationLock {
    param([Parameter(Mandatory)][object]$Lock)
    if ($null -eq $Lock -or $Lock.Acquired -isnot [bool] -or -not $Lock.Acquired -or $null -eq $Lock.Mutex) { throw 'state_root_lock_invalid' }
    try { $Lock.Mutex.ReleaseMutex() } finally { $Lock.Mutex.Dispose() }
}

function New-Phase16SecureStateDirectory {
    param([Parameter(Mandatory)][string]$ParentPath, [Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$AuthorizedSid)
    $parent = [IO.Path]::GetFullPath($ParentPath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $target = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([IO.Path]::GetDirectoryName($target).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $parent -or $AuthorizedSid -cnotmatch '^S-1-[0-9-]+$') { throw 'state_root_invalid' }
    $security = New-Phase16ManagedStateDirectorySecurity -AuthorizedSid $AuthorizedSid
    $temporary = Join-Path $parent ('.phase16-state-root.create-' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [void][IO.Directory]::CreateDirectory($temporary, $security)
        $temporaryFacts = Get-Phase16StateDirectoryFacts -Path $temporary
        if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $temporaryFacts -ExpectedPath $temporary -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        try { [IO.Directory]::Move($temporary, $target) } catch [IO.IOException] {
            $existing = Get-Phase16StateDirectoryFacts -Path $target
            if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $existing -ExpectedPath $target -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        }
    } finally {
        $remaining = Get-Phase16StateDirectoryFacts -Path $temporary
        if ($remaining.Exists) {
            if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $remaining -ExpectedPath $temporary -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
            [IO.Directory]::Delete($temporary, $false)
        }
    }
}

function Initialize-Phase16TrustedStateRoot {
    param([Parameter(Mandatory)][string]$AnchorPath, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$AuthorizedSid)
    $anchor = [IO.Path]::GetFullPath($AnchorPath).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $expectedRoot = [IO.Path]::Combine($anchor, 'AMN2', 'phase16', 'readonly-preflight')
    if (-not $root.Equals($expectedRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'state_root_invalid' }
    $lock = Enter-Phase16StateRootCreationLock
    try {
        $anchorFacts = Get-Phase16StateDirectoryFacts -Path $anchor
        if (-not (Test-Phase16ProgramDataAnchorFacts -Facts $anchorFacts -ExpectedPath $anchor)) { throw 'state_root_invalid' }
        $current = $anchor
        $namespace = [IO.Path]::Combine($current, 'AMN2')
        $namespaceFacts = Get-Phase16StateDirectoryFacts -Path $namespace
        if (-not $namespaceFacts.Exists) { New-Phase16SecureStateDirectory -ParentPath $current -Path $namespace -AuthorizedSid $AuthorizedSid; $namespaceFacts = Get-Phase16StateDirectoryFacts -Path $namespace }
        if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $namespaceFacts -ExpectedPath $namespace -AuthorizedSid $AuthorizedSid) -and -not (Test-Phase16SharedNamespaceDirectoryFacts -Facts $namespaceFacts -ExpectedPath $namespace)) { throw 'state_root_invalid' }
        $current = $namespace
        foreach ($leaf in @('phase16','readonly-preflight')) {
            $next = [IO.Path]::Combine($current, $leaf)
            $facts = Get-Phase16StateDirectoryFacts -Path $next
            if (-not $facts.Exists) { New-Phase16SecureStateDirectory -ParentPath $current -Path $next -AuthorizedSid $AuthorizedSid; $facts = Get-Phase16StateDirectoryFacts -Path $next }
            if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $next -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
            $current = $next
        }
        foreach ($leaf in @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')) {
            $next = [IO.Path]::Combine($root, $leaf)
            $facts = Get-Phase16StateDirectoryFacts -Path $next
            if (-not $facts.Exists) { New-Phase16SecureStateDirectory -ParentPath $root -Path $next -AuthorizedSid $AuthorizedSid; $facts = Get-Phase16StateDirectoryFacts -Path $next }
            if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $next -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
        }
        return $root
    } finally { Exit-Phase16StateRootCreationLock -Lock $lock }
}

function Get-Phase16ProductionStateRoot {
    return $script:Phase16ProductionStateRoot
}

function Initialize-Phase16ProductionStateRoot {
    $anchor = [Environment]::GetFolderPath([Environment+SpecialFolder]::CommonApplicationData)
    if ([string]::IsNullOrWhiteSpace($anchor) -or -not [IO.Path]::IsPathRooted($anchor)) { throw 'state_root_invalid' }
    $authorizedSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    return Initialize-Phase16TrustedStateRoot -AnchorPath $anchor -StateRoot $script:Phase16ProductionStateRoot -AuthorizedSid $authorizedSid
}

function Test-Phase16TrustedOutcomeParentFacts {
    param(
        [Parameter(Mandatory)][object]$Facts,
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$OutcomePath,
        [Parameter(Mandatory)][string]$AuthorizedSid
    )
    try {
        $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
        $expectedParent = [IO.Path]::Combine($root, 'outcomes')
        $fullOutcome = [IO.Path]::GetFullPath($OutcomePath)
        $actualParent = [IO.Path]::GetDirectoryName($fullOutcome).TrimEnd([IO.Path]::DirectorySeparatorChar)
        $leaf = [IO.Path]::GetFileName($fullOutcome)
        if ([string]::IsNullOrWhiteSpace($leaf) -or $actualParent -cne $expectedParent) { return $false }
        return Test-Phase16ManagedStateDirectoryFacts -Facts $Facts -ExpectedPath $expectedParent -AuthorizedSid $AuthorizedSid
    } catch {
        return $false
    }
}

function Assert-Phase16TrustedOutcomeParent {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$OutcomePath,
        [Parameter(Mandatory)][string]$AuthorizedSid
    )
    $fullOutcome = [IO.Path]::GetFullPath($OutcomePath)
    $parent = [IO.Path]::GetDirectoryName($fullOutcome)
    $facts = Get-Phase16StateDirectoryFacts -Path $parent
    if (-not (Test-Phase16TrustedOutcomeParentFacts -Facts $facts -StateRoot $StateRoot -OutcomePath $fullOutcome -AuthorizedSid $AuthorizedSid)) { throw 'outcome_parent_invalid' }
    return $fullOutcome
}

function Assert-Phase16TrustedManagedStateChain {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$AuthorizedSid,
        [Parameter(Mandatory)][string[]]$RequiredChildren
    )
    $anchor = [Environment]::GetFolderPath([Environment+SpecialFolder]::CommonApplicationData)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $expectedRoot = [IO.Path]::GetFullPath($script:Phase16ProductionStateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([string]::IsNullOrWhiteSpace($anchor) -or -not $root.Equals($expectedRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'state_root_invalid' }
    $anchor = [IO.Path]::GetFullPath($anchor).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $anchorFacts = Get-Phase16StateDirectoryFacts -Path $anchor
    if (-not (Test-Phase16ProgramDataAnchorFacts -Facts $anchorFacts -ExpectedPath $anchor)) { throw 'state_root_invalid' }
    $current = [IO.Path]::Combine($anchor, 'AMN2')
    $namespaceFacts = Get-Phase16StateDirectoryFacts -Path $current
    if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $namespaceFacts -ExpectedPath $current -AuthorizedSid $AuthorizedSid) -and -not (Test-Phase16SharedNamespaceDirectoryFacts -Facts $namespaceFacts -ExpectedPath $current)) { throw 'state_root_invalid' }
    foreach ($leaf in @('phase16','readonly-preflight')) {
        $current = [IO.Path]::Combine($current, $leaf)
        $facts = Get-Phase16StateDirectoryFacts -Path $current
        if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $current -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
    }
    $allowedChildren = @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes')
    foreach ($leaf in @($RequiredChildren | Sort-Object -Unique)) {
        if ($leaf -cnotin $allowedChildren) { throw 'state_root_invalid' }
        $path = [IO.Path]::Combine($root, $leaf)
        $facts = Get-Phase16StateDirectoryFacts -Path $path
        if (-not (Test-Phase16ManagedStateDirectoryFacts -Facts $facts -ExpectedPath $path -AuthorizedSid $AuthorizedSid)) { throw 'state_root_invalid' }
    }
    return $root
}

function Get-Phase16TransactionPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    return Get-Phase16LifecyclePath -LifecycleRoot (Join-Path $StateRoot 'transactions') -ClaimId $ClaimId
}

function Get-Phase16ClaimLockPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    return Get-Phase16LifecyclePath -LifecycleRoot (Join-Path $StateRoot 'locks') -ClaimId $ClaimId
}

function Enter-Phase16ClaimLock {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'claim_invalid' }
    foreach ($root in @($StateRoot, (Join-Path $StateRoot 'locks'), (Join-Path $StateRoot 'outcome-locks'))) {
        if (-not (Test-Path -LiteralPath $root)) { [void][IO.Directory]::CreateDirectory($root) }
        $item = Get-Item -LiteralPath $root -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    }
    $path = Get-Phase16ClaimLockPath -StateRoot $StateRoot -ClaimId $ClaimId
    try {
        $stream = [IO.FileStream]::new($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch [IO.IOException] { throw 'claim_replay' }
    return [pscustomobject]@{ ClaimId = $ClaimId; Path = $path; Stream = $stream }
}

function Test-Phase16ClaimLock {
    param([Parameter(Mandatory)][object]$Lock, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($null -eq $Lock -or -not (Test-Phase16ExactProperties -Value $Lock -Required @('ClaimId','Path','Stream'))) { return $false }
    $expected = Get-Phase16ClaimLockPath -StateRoot $StateRoot -ClaimId $ClaimId
    return $Lock.ClaimId -is [string] -and $Lock.ClaimId -ceq $ClaimId -and $Lock.Path -is [string] -and [IO.Path]::GetFullPath($Lock.Path) -ceq [IO.Path]::GetFullPath($expected) -and $Lock.Stream -is [IO.FileStream] -and $Lock.Stream.CanWrite
}

function Get-Phase16OutcomeLockPath {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $lockRoot = [IO.Path]::GetFullPath((Join-Path $root 'outcome-locks')).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([IO.Path]::GetDirectoryName($lockRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'outcome_lock_invalid' }
    $canonicalOutcome = [IO.Path]::GetFullPath($OutcomePath).TrimEnd([IO.Path]::DirectorySeparatorChar).ToUpperInvariant()
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($canonicalOutcome)
    $digest = Get-Phase16BytesSha256 -Bytes $bytes
    return [IO.Path]::Combine($lockRoot, $digest + '.lock')
}

function Get-Phase16OutcomesNamespaceLockPath {
    param([Parameter(Mandatory)][string]$StateRoot)
    $root = [IO.Path]::GetFullPath($StateRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $lockRoot = [IO.Path]::GetFullPath((Join-Path $root 'outcome-locks')).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if ([IO.Path]::GetDirectoryName($lockRoot).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'outcome_namespace_invalid' }
    return [IO.Path]::Combine($lockRoot, 'outcomes.namespace.lock')
}

function Enter-Phase16OutcomesNamespaceLock {
    param([Parameter(Mandatory)][string]$StateRoot)
    $lockRoot = Join-Path ([IO.Path]::GetFullPath($StateRoot)) 'outcome-locks'
    if (-not (Test-Path -LiteralPath $lockRoot -PathType Container)) { throw 'outcome_namespace_invalid' }
    $lockItem = Get-Item -LiteralPath $lockRoot -Force -ErrorAction Stop
    if (($lockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'outcome_namespace_invalid' }
    $path = Get-Phase16OutcomesNamespaceLockPath -StateRoot $StateRoot
    try { $stream = [IO.FileStream]::new($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None) } catch [IO.IOException] { throw 'outcome_namespace_busy' }
    return [pscustomobject]@{ Path = $path; Stream = $stream }
}

function Test-Phase16OutcomesNamespaceLock {
    param([Parameter(Mandatory)][object]$Lock, [Parameter(Mandatory)][string]$StateRoot)
    if ($null -eq $Lock -or -not (Test-Phase16ExactProperties -Value $Lock -Required @('Path','Stream'))) { return $false }
    $expected = Get-Phase16OutcomesNamespaceLockPath -StateRoot $StateRoot
    return $Lock.Path -is [string] -and [IO.Path]::GetFullPath($Lock.Path) -ceq [IO.Path]::GetFullPath($expected) -and $Lock.Stream -is [IO.FileStream] -and $Lock.Stream.CanWrite
}

function Enter-Phase16OutcomeLock {
    param([Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { throw 'outcome_lock_invalid' }
    $lockRoot = Join-Path ([IO.Path]::GetFullPath($StateRoot)) 'outcome-locks'
    if (-not (Test-Path -LiteralPath $lockRoot -PathType Container)) { throw 'outcome_lock_invalid' }
    $lockItem = Get-Item -LiteralPath $lockRoot -Force -ErrorAction Stop
    if (($lockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'outcome_lock_invalid' }
    $path = Get-Phase16OutcomeLockPath -StateRoot $StateRoot -OutcomePath $OutcomePath
    try { $stream = [IO.FileStream]::new($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None) } catch [IO.IOException] { throw 'outcome_replay' }
    return [pscustomobject]@{ ClaimId = $ClaimId; OutcomePath = [IO.Path]::GetFullPath($OutcomePath); Path = $path; Stream = $stream }
}

function Test-Phase16OutcomeLock {
    param([Parameter(Mandatory)][object]$Lock, [Parameter(Mandatory)][string]$StateRoot, [Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId)
    if ($null -eq $Lock -or -not (Test-Phase16ExactProperties -Value $Lock -Required @('ClaimId','OutcomePath','Path','Stream'))) { return $false }
    $expectedPath = Get-Phase16OutcomeLockPath -StateRoot $StateRoot -OutcomePath $OutcomePath
    return (
        $Lock.ClaimId -is [string] -and $Lock.ClaimId -ceq $ClaimId -and
        $Lock.OutcomePath -is [string] -and [IO.Path]::GetFullPath($Lock.OutcomePath).Equals([IO.Path]::GetFullPath($OutcomePath), [StringComparison]::OrdinalIgnoreCase) -and
        $Lock.Path -is [string] -and [IO.Path]::GetFullPath($Lock.Path) -ceq [IO.Path]::GetFullPath($expectedPath) -and
        $Lock.Stream -is [IO.FileStream] -and $Lock.Stream.CanWrite
    )
}

function Reserve-Phase16Claim {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase16UtcTimestamp -Value $ReservedAt)) { throw 'claim_invalid' }
    if (-not (Test-Path -LiteralPath $LifecycleRoot -PathType Container)) { throw 'claim_lifecycle_invalid' }
    $rootItem = Get-Item -LiteralPath $LifecycleRoot -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    $lifecyclePath = Get-Phase16LifecyclePath -LifecycleRoot $LifecycleRoot -ClaimId $ClaimId
    Write-Phase16CreateNewJson -Path $lifecyclePath -Value ([ordered]@{ claim_id = $ClaimId; reason_code = 'not_applicable'; reserved_at = $ReservedAt; status = 'reserved' }) -OwnerId $ClaimId
    return $lifecyclePath
}

function Reserve-Phase16OutcomeSlot {
    param([Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase16UtcTimestamp -Value $ReservedAt)) { throw 'outcome_reservation_invalid' }
    $fullPath = [IO.Path]::GetFullPath($OutcomePath)
    $parent = [IO.Path]::GetDirectoryName($fullPath)
    if ([string]::IsNullOrWhiteSpace($parent) -or -not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'outcome_reservation_invalid' }
    Write-Phase16CreateNewJson -Path $fullPath -Value ([ordered]@{ claim_id = $ClaimId; reserved_at = $ReservedAt; status = 'reserved' }) -OwnerId $ClaimId
    return $fullPath
}

function Test-Phase16OutcomeOwnership {
    param([Parameter(Mandatory)][string]$ReservationPath, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$') { return $false }
    $reservation = ConvertFrom-Phase16CanonicalJsonFile -Path $ReservationPath
    if ($null -eq $reservation -or -not (Test-Phase16ExactProperties -Value $reservation -Required @('claim_id','reserved_at','status'))) { return $false }
    return (
        $reservation.claim_id -is [string] -and $reservation.claim_id -ceq $ClaimId -and
        $reservation.status -is [string] -and $reservation.status -ceq 'reserved' -and
        $reservation.reserved_at -is [string] -and (Test-Phase16UtcTimestamp -Value $reservation.reserved_at)
    )
}

function Release-Phase16OutcomeSlot {
    param([Parameter(Mandatory)][string]$ReservationPath, [Parameter(Mandatory)][string]$ClaimId)
    if (Test-Phase16OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId) {
        [IO.File]::Delete($ReservationPath)
        if (Test-Path -LiteralPath $ReservationPath) { throw 'outcome_reservation_release_failed' }
    }
}

function Start-Phase16Transaction {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$OutcomePath,
        [Parameter(Mandatory)][string]$ClaimId,
        [string]$StartedAt,
        [Parameter(Mandatory)][string]$ReservedAt,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [string]$AuthorizedSid,
        [Parameter(Mandatory)][object]$Lock
    )
    if ([string]::IsNullOrWhiteSpace($StartedAt)) { $StartedAt = $ReservedAt }
    if ($ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $CollectorSha256 -cnotmatch '^[0-9a-f]{64}$' -or -not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost) -or
        -not (Test-Phase16UtcTimestamp -Value $StartedAt) -or -not (Test-Phase16UtcTimestamp -Value $ReservedAt)) { throw 'transaction_invalid' }
    if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $StateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
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
    if (-not [string]::IsNullOrWhiteSpace($AuthorizedSid)) { $reservationPath = Assert-Phase16TrustedOutcomeParent -StateRoot $StateRoot -OutcomePath $reservationPath -AuthorizedSid $AuthorizedSid }
    $outcomeLock = Enter-Phase16OutcomeLock -StateRoot $StateRoot -OutcomePath $reservationPath -ClaimId $ClaimId
    try {
        $lifecyclePath = Get-Phase16LifecyclePath -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId
        $journalPath = Get-Phase16TransactionPath -StateRoot $StateRoot -ClaimId $ClaimId
        Remove-Phase16TransactionTemps -TransactionPath $journalPath -ClaimId $ClaimId
        Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $reservationPath -ClaimId $ClaimId
        $stagedPath = $reservationPath + '.phase16-' + $ClaimId + '.staged'
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
            schema = 'amn2.phase16.readonly-preflight-transaction.v2'
            ssh_used = $false
            staged_path = $stagedPath
            started_at = $StartedAt
            terminal_ended_at = $null
            terminal_outcome_sha256 = $null
            terminal_path = $null
            terminal_reason_code = $null
            terminal_status = $null
        }
        Write-Phase16AtomicCreateNewJson -Path $journalPath -Value $journal -OwnerId $ClaimId
        if (-not [string]::IsNullOrWhiteSpace($AuthorizedSid)) { [void](Assert-Phase16TrustedOutcomeParent -StateRoot $StateRoot -OutcomePath $reservationPath -AuthorizedSid $AuthorizedSid) }
        $createdReservation = Reserve-Phase16OutcomeSlot -OutcomePath $reservationPath -ClaimId $ClaimId -ReservedAt $ReservedAt
        $createdLifecycle = Reserve-Phase16Claim -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId -ReservedAt $ReservedAt
        return [pscustomobject]@{ JournalPath = $journalPath; LifecyclePath = $createdLifecycle; OutcomeLock = $outcomeLock; ReservationPath = $createdReservation; StagedPath = $stagedPath }
    } catch {
        $outcomeLock.Stream.Dispose()
        throw
    }
}

function Set-Phase16TransactionPhase {
    param(
        [Parameter(Mandatory)][string]$TransactionPath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][ValidateSet('owned','transport_attempted','ssh_started','outcome_staged','finalizing')][string]$Phase,
        [Parameter(Mandatory)][object]$Lock
    )
    $stateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
    if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $stateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $TransactionPath
    if ($null -eq $journal -or $journal.claim_id -isnot [string] -or $journal.claim_id -cne $ClaimId -or $journal.phase -isnot [string]) { throw 'transaction_invalid' }
    $phases = @('owned','transport_attempted','ssh_started','outcome_staged','finalizing')
    $currentPhaseIndex = [Array]::IndexOf($phases, [string]$journal.phase)
    $nextPhaseIndex = [Array]::IndexOf($phases, $Phase)
    if ($currentPhaseIndex -lt 0 -or $nextPhaseIndex -lt 0 -or $nextPhaseIndex -lt $currentPhaseIndex) { throw 'transaction_invalid' }
    $journal.phase = $Phase
    $preTransportClaimFailure = $journal.terminal_reason_code -ceq 'claim_invalid' -and $journal.ssh_used -eq $false
    if ($nextPhaseIndex -ge 1 -and -not $preTransportClaimFailure) { $journal.ssh_used = $true }
    Write-Phase16AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
    return $TransactionPath
}

function Test-Phase16ExactPublishedTerminalOutcome {
    param(
        [Parameter(Mandatory)][object]$Document,
        [Parameter(Mandatory)][object]$Journal
    )
    try {
        if ($Journal.terminal_status -ceq 'failed') {
            $required = @('collector_sha256','decision','ended_at','expected_host','manifest_sha256','package_id','reason_code','safety','schema','started_at','transport_disposition')
            if (-not (Test-Phase16ExactProperties -Value $Document -Required $required)) { return $false }
            foreach ($field in @('collector_sha256','decision','ended_at','expected_host','manifest_sha256','package_id','reason_code','schema','started_at','transport_disposition')) {
                if ($Document.$field -isnot [string]) { return $false }
            }
            if ($Document.schema -cne $script:Phase16FailureSchema -or $Document.package_id -cne $script:Phase16PackageId -or
                $Document.decision -cne 'stop' -or $Document.reason_code -cne $Journal.terminal_reason_code -or
                $Document.transport_disposition -cne $(if ($Journal.ssh_used) { 'read_only_failed' } else { 'not_run' })) { return $false }
        } elseif ($Journal.terminal_status -ceq 'completed') {
            $required = @('collector_sha256','decision','ended_at','expected_host','manifest_sha256','observations','package_id','safety','schema','started_at','stop_reasons','transport_disposition')
            if (-not (Test-Phase16ExactProperties -Value $Document -Required $required)) { return $false }
            foreach ($field in @('collector_sha256','decision','ended_at','expected_host','manifest_sha256','package_id','schema','started_at','transport_disposition')) {
                if ($Document.$field -isnot [string]) { return $false }
            }
            if ($Document.schema -cne $script:Phase16EvidenceSchema -or $Document.package_id -cne $script:Phase16PackageId -or
                $Document.decision -cnotin @('pass','stop') -or $Document.transport_disposition -cne 'read_only_completed' -or
                $Document.stop_reasons -isnot [System.Array] -or $Document.observations -isnot [System.Array]) { return $false }
            $reasons = @($Document.stop_reasons)
            if (@($reasons | Where-Object { $_ -isnot [string] -or $_ -cnotin $script:Phase16StopReasons }).Count -ne 0 -or
                ($reasons -join '|') -cne (@($reasons | Sort-Object -Unique) -join '|')) { return $false }
            $observations = @($Document.observations)
            if ($observations.Count -ne $script:Phase16ObservationNames.Count) { return $false }
            $names = @()
            $states = @{}
            foreach ($item in $observations) {
                if (-not (Test-Phase16ExactProperties -Value $item -Required @('name','observation_sha256','state')) -or
                    $item.name -isnot [string] -or $item.observation_sha256 -isnot [string] -or $item.state -isnot [string] -or
                    $item.name -cnotin $script:Phase16ObservationNames -or $item.observation_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
                    $item.state -cnotin @('absent','free','pass','present','stop','unknown')) { return $false }
                $names += $item.name
                $states[$item.name] = $item.state
            }
            if (($names -join '|') -cne ($script:Phase16ObservationNames -join '|')) { return $false }
            $expectedReasons = @()
            if ($states['recovery_markers_phase14_phase15_phase16'] -in @('stop','unknown')) { $expectedReasons += 'recovery_incomplete' }
            if (@($script:Phase16ConflictNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'resource_conflict' }
            $ordinaryNames = @($script:Phase16ObservationNames | Where-Object { $_ -cnotin $script:Phase16ConflictNames -and $_ -cne 'recovery_markers_phase14_phase15_phase16' })
            if (@($ordinaryNames | Where-Object { $states[$_] -in @('stop','unknown') }).Count -ne 0) { $expectedReasons += 'observation_failed' }
            $expectedReasons = @($expectedReasons | Sort-Object -Unique)
            if (($reasons -join '|') -cne ($expectedReasons -join '|') -or
                (($Document.decision -ceq 'stop') -ne ($expectedReasons.Count -gt 0))) { return $false }
        } else { return $false }
        if ($Document.manifest_sha256 -cne $Journal.manifest_sha256 -or $Document.collector_sha256 -cne $Journal.collector_sha256 -or
            $Document.expected_host -cne $Journal.expected_host -or $Document.ended_at -cne $Journal.terminal_ended_at -or
            $Document.started_at -cne $Journal.started_at -or -not (Test-Phase16UtcTimestamp -Value $Document.started_at) -or
            -not (Test-Phase16UtcTimestamp -Value $Document.ended_at)) { return $false }
        $started = [DateTimeOffset]::ParseExact($Document.started_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        $ended = [DateTimeOffset]::ParseExact($Document.ended_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal)
        if ($ended -lt $started -or -not (Test-Phase16ExactProperties -Value $Document.safety -Required @('live_mutation','raw_output_persisted','remote_file_written','ssh_used')) -or
            $Document.safety.live_mutation -isnot [bool] -or $Document.safety.raw_output_persisted -isnot [bool] -or
            $Document.safety.remote_file_written -isnot [bool] -or $Document.safety.ssh_used -isnot [bool] -or
            $Document.safety.live_mutation -ne $false -or $Document.safety.raw_output_persisted -ne $false -or
            $Document.safety.remote_file_written -ne $false -or $Document.safety.ssh_used -ne $Journal.ssh_used) { return $false }
        return $true
    } catch { return $false }
}

function Test-Phase16ExactTerminalJournalBinding {
    param(
        [Parameter(Mandatory)][object]$Journal,
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ExpectedOutcomePath,
        [Parameter(Mandatory)][string]$RecoveryOutcomePath
    )
    try {
        if ($Journal.phase -isnot [string] -or $Journal.phase -cnotin @('owned','transport_attempted','ssh_started','outcome_staged','finalizing') -or
            $Journal.terminal_path -isnot [string] -or $Journal.terminal_status -isnot [string] -or
            $Journal.terminal_reason_code -isnot [string] -or $Journal.terminal_ended_at -isnot [string] -or
            $Journal.terminal_outcome_sha256 -isnot [string]) { return $false }
        $current = [IO.Path]::GetFullPath($ExpectedOutcomePath)
        $derivedRecovery = Get-Phase16LifecyclePath -LifecycleRoot (Join-Path ([IO.Path]::GetFullPath($StateRoot)) 'recovery-outcomes') -ClaimId $ClaimId
        $recovery = [IO.Path]::GetFullPath($RecoveryOutcomePath)
        if ($recovery -cne [IO.Path]::GetFullPath($derivedRecovery)) { return $false }
        $terminal = [IO.Path]::GetFullPath($Journal.terminal_path)
        $pathIsCurrent = $terminal -ceq $current
        $pathIsRecovery = $terminal -ceq $recovery
        if (-not $pathIsCurrent -and -not $pathIsRecovery) { return $false }
        $statusReasonValid = (
            ($Journal.terminal_status -ceq 'completed' -and $Journal.terminal_reason_code -ceq 'not_applicable') -or
            ($Journal.terminal_status -ceq 'failed' -and $Journal.terminal_reason_code -cin $script:Phase16FailureReasons)
        )
        if (-not $statusReasonValid) { return $false }
        if ($pathIsRecovery -and ($Journal.terminal_status -cne 'failed' -or $Journal.terminal_reason_code -cne 'transport_failed')) { return $false }
        if ($Journal.ssh_used -isnot [bool]) { return $false }
        if ($Journal.phase -ceq 'owned' -and ($Journal.terminal_status -cne 'failed' -or $Journal.terminal_reason_code -cne 'claim_invalid' -or $Journal.ssh_used -ne $false)) { return $false }
        if ($Journal.phase -ceq 'transport_attempted' -and ($Journal.terminal_status -cne 'failed' -or $Journal.terminal_reason_code -cne 'transport_failed' -or $Journal.ssh_used -ne $true)) { return $false }
        if ($Journal.phase -ceq 'ssh_started' -and $Journal.ssh_used -ne $true) { return $false }
        if ($Journal.phase -cin @('outcome_staged','finalizing') -and $Journal.ssh_used -eq $false -and ($Journal.terminal_status -cne 'failed' -or $Journal.terminal_reason_code -cne 'claim_invalid')) { return $false }
        return (Test-Phase16UtcTimestamp -Value $Journal.terminal_ended_at) -and $Journal.terminal_outcome_sha256 -cmatch '^[0-9a-f]{64}$'
    } catch { return $false }
}

function Get-Phase16NoFollowPathState {
    param([Parameter(Mandatory)][string]$Path)
    try {
        $fullPath = [IO.Path]::GetFullPath($Path)
        $parentPath = [IO.Path]::GetDirectoryName($fullPath)
        $leaf = [IO.Path]::GetFileName($fullPath)
        if ([string]::IsNullOrWhiteSpace($parentPath) -or [string]::IsNullOrWhiteSpace($leaf)) { throw 'transaction_invalid' }
        $parent = [IO.DirectoryInfo]::new($parentPath)
        if (-not $parent.Exists -or ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
        $matches = @(
            $parent.EnumerateFileSystemInfos() | Where-Object {
                $_.Name.Equals($leaf, [StringComparison]::OrdinalIgnoreCase)
            }
        )
        if ($matches.Count -eq 0) { return 'absent' }
        if ($matches.Count -ne 1) { throw 'transaction_invalid' }
        $item = $matches[0]
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { return 'reparse' }
        if ($item -is [IO.FileInfo]) { return 'file' }
        if ($item -is [IO.DirectoryInfo]) { return 'directory' }
        return 'other'
    } catch {
        throw 'transaction_invalid'
    }
}

function Reconcile-Phase16Transaction {
    param(
        [Parameter(Mandatory)][string]$StateRoot,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$EndedAt,
        [Parameter(Mandatory)][object]$Lock,
        [object]$OutcomeLock,
        [object]$NamespaceLock,
        [string]$ExpectedManifestSha256,
        [string]$ExpectedCollectorSha256,
        [string]$ExpectedHost,
        [string]$ExpectedOutcomePath,
        [string]$ExpectedReservedAt,
        [string]$AuthorizedSid
    )
    if (-not (Test-Phase16UtcTimestamp -Value $EndedAt)) { throw 'transaction_invalid' }
    if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $StateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
    $expectedValues = @($ExpectedManifestSha256,$ExpectedCollectorSha256,$ExpectedHost,$ExpectedOutcomePath,$AuthorizedSid)
    $hasExpectedBindings = @($expectedValues | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count -gt 0
    if ($hasExpectedBindings -and @($expectedValues | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -gt 0) { throw 'transaction_invalid' }
    $transactionRoot = Join-Path $StateRoot 'transactions'
    if (-not (Test-Path -LiteralPath $transactionRoot -PathType Container)) { return [pscustomobject]@{ Recovered = $false; OutcomePath = $null } }
    $ownsNamespaceLock = $false
    if ($null -eq $NamespaceLock) {
        $NamespaceLock = Enter-Phase16OutcomesNamespaceLock -StateRoot $StateRoot
        $ownsNamespaceLock = $true
    } elseif (-not (Test-Phase16OutcomesNamespaceLock -Lock $NamespaceLock -StateRoot $StateRoot)) { throw 'outcome_namespace_invalid' }
    try {
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('outcome-locks','transactions')) }
    $journalPath = Get-Phase16TransactionPath -StateRoot $StateRoot -ClaimId $ClaimId
    if (-not (Test-Path -LiteralPath $journalPath -PathType Leaf)) {
        if ($hasExpectedBindings) { Remove-Phase16TransactionTemps -TransactionPath $journalPath -ClaimId $ClaimId }
        return [pscustomobject]@{ Recovered = $false; OutcomePath = $null }
    }
    if (-not $hasExpectedBindings) { throw 'transaction_invalid' }
    $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $journalPath
    $v2Required = @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','ssh_used','staged_path','started_at','terminal_ended_at','terminal_outcome_sha256','terminal_path','terminal_reason_code','terminal_status')
    $v1Required = @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','ssh_used','staged_path','terminal_ended_at','terminal_outcome_sha256','terminal_path','terminal_reason_code','terminal_status')
    $isV2 = $null -ne $journal -and (Test-Phase16ExactProperties -Value $journal -Required $v2Required) -and $journal.schema -is [string] -and $journal.schema -ceq 'amn2.phase16.readonly-preflight-transaction.v2'
    $isImmediatePredecessorV1 = $null -ne $journal -and (Test-Phase16ExactProperties -Value $journal -Required $v2Required) -and $journal.schema -is [string] -and $journal.schema -ceq 'amn2.phase16.readonly-preflight-transaction.v1'
    $isLegacyV1 = $null -ne $journal -and (Test-Phase16ExactProperties -Value $journal -Required $v1Required) -and $journal.schema -is [string] -and $journal.schema -ceq 'amn2.phase16.readonly-preflight-transaction.v1'
    if (-not $isV2 -and -not $isImmediatePredecessorV1 -and -not $isLegacyV1) { throw 'transaction_invalid' }
    $hasStoredStartedAt = $isV2 -or $isImmediatePredecessorV1
    $stringFields = @('claim_id','collector_sha256','expected_host','manifest_sha256','outcome_path','phase','reserved_at','schema','staged_path')
    if ($hasStoredStartedAt) { $stringFields += 'started_at' }
    foreach ($field in $stringFields) {
        if ($journal.$field -isnot [string]) { throw 'transaction_invalid' }
    }
    if ($journal.ssh_used -isnot [bool]) { throw 'transaction_invalid' }
    $terminalValues = @($journal.terminal_ended_at, $journal.terminal_outcome_sha256, $journal.terminal_path, $journal.terminal_reason_code, $journal.terminal_status)
    if (@($terminalValues | Where-Object { $null -ne $_ }).Count -notin @(0, 5)) { throw 'transaction_invalid' }
    if ($null -ne $journal.terminal_status -and (
        $journal.terminal_ended_at -isnot [string] -or -not (Test-Phase16UtcTimestamp -Value $journal.terminal_ended_at) -or
        $journal.terminal_outcome_sha256 -isnot [string] -or $journal.terminal_outcome_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        $journal.terminal_path -isnot [string] -or $journal.terminal_reason_code -isnot [string] -or $journal.terminal_status -isnot [string] -or
        $journal.terminal_status -cnotin @('completed','failed')
    )) { throw 'transaction_invalid' }
    if ($journal.claim_id -cne $ClaimId) { throw 'transaction_invalid' }
    $phaseValid = $journal.phase -cin @('owned','transport_attempted','ssh_started','outcome_staged','finalizing')
    if ($journal.manifest_sha256 -cnotmatch '^[0-9a-f]{64}$' -or $journal.collector_sha256 -cnotmatch '^[0-9a-f]{64}$' -or -not (Test-Phase16ExpectedHost -ExpectedHost $journal.expected_host) -or
        -not (Test-Phase16UtcTimestamp -Value $journal.reserved_at) -or ($hasStoredStartedAt -and -not (Test-Phase16UtcTimestamp -Value $journal.started_at))) { throw 'transaction_invalid' }
    if ($hasExpectedBindings -and (
        $journal.manifest_sha256 -cne $ExpectedManifestSha256 -or
        $journal.collector_sha256 -cne $ExpectedCollectorSha256 -or
        $journal.expected_host -cne $ExpectedHost -or
        [IO.Path]::GetFullPath($journal.outcome_path) -cne [IO.Path]::GetFullPath($ExpectedOutcomePath)
    )) { throw 'transaction_invalid' }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedReservedAt) -and $journal.reserved_at -cne $ExpectedReservedAt) { throw 'transaction_invalid' }
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedOutcomeParent -StateRoot $StateRoot -OutcomePath $journal.outcome_path -AuthorizedSid $AuthorizedSid) }
    $expectedStagedPath = [IO.Path]::GetFullPath($journal.outcome_path) + '.phase16-' + $ClaimId + '.staged'
    if ([IO.Path]::GetFullPath($journal.staged_path) -cne $expectedStagedPath) { throw 'transaction_invalid' }
    $ownsOutcomeLock = $false
    if ($null -eq $OutcomeLock) {
        $OutcomeLock = Enter-Phase16OutcomeLock -StateRoot $StateRoot -OutcomePath $journal.outcome_path -ClaimId $ClaimId
        $ownsOutcomeLock = $true
    } elseif (-not (Test-Phase16OutcomeLock -Lock $OutcomeLock -StateRoot $StateRoot -OutcomePath $journal.outcome_path -ClaimId $ClaimId)) { throw 'outcome_lock_invalid' }
    try {
    $lifecycleRoot = Join-Path $StateRoot 'claims'
    if (-not (Test-Path -LiteralPath $lifecycleRoot)) {
        if ($hasExpectedBindings) { throw 'state_root_invalid' }
        [void][IO.Directory]::CreateDirectory($lifecycleRoot)
    }
    $lifecyclePath = Get-Phase16LifecyclePath -LifecycleRoot $lifecycleRoot -ClaimId $ClaimId
    $lifecycleExists = Test-Path -LiteralPath $lifecyclePath -PathType Leaf
    $reservedLifecycle = ConvertFrom-Phase16CanonicalJsonFile -Path $lifecyclePath
    if ($lifecycleExists -and $null -eq $reservedLifecycle) { throw 'transaction_invalid' }
    if ($lifecycleExists -and @($reservedLifecycle.PSObject.Properties.Name) -cnotcontains 'status') { throw 'transaction_invalid' }
    $outcomeExists = Test-Path -LiteralPath $journal.outcome_path -PathType Leaf
    $reservedOutcome = ConvertFrom-Phase16CanonicalJsonFile -Path $journal.outcome_path
    if ($outcomeExists -and $null -eq $reservedOutcome) { throw 'transaction_invalid' }
    if ($lifecycleExists) {
        if ($reservedLifecycle.status -isnot [string]) { throw 'transaction_invalid' }
        if ($reservedLifecycle.status -ceq 'reserved') {
            if (
            -not (Test-Phase16ExactProperties -Value $reservedLifecycle -Required @('claim_id','reason_code','reserved_at','status')) -or
            $reservedLifecycle.claim_id -isnot [string] -or $reservedLifecycle.claim_id -cne $ClaimId -or
            $reservedLifecycle.reason_code -isnot [string] -or $reservedLifecycle.reason_code -cne 'not_applicable' -or
            $reservedLifecycle.reserved_at -isnot [string] -or $reservedLifecycle.reserved_at -cne $journal.reserved_at
            ) { throw 'transaction_invalid' }
        } elseif ($reservedLifecycle.status -cin @('completed','failed')) {
            if (-not (Test-Phase16ExactProperties -Value $reservedLifecycle -Required @('claim_id','ended_at','reason_code','status')) -or
                $reservedLifecycle.claim_id -isnot [string] -or $reservedLifecycle.claim_id -cne $ClaimId -or
                $reservedLifecycle.ended_at -isnot [string] -or -not (Test-Phase16UtcTimestamp -Value $reservedLifecycle.ended_at) -or
                $reservedLifecycle.reason_code -isnot [string] -or
                ($reservedLifecycle.status -ceq 'completed' -and $reservedLifecycle.reason_code -cne 'not_applicable') -or
                ($reservedLifecycle.status -ceq 'failed' -and $reservedLifecycle.reason_code -cnotin $script:Phase16FailureReasons)
            ) { throw 'transaction_invalid' }
        } else { throw 'transaction_invalid' }
    }
    if ($outcomeExists -and @($reservedOutcome.PSObject.Properties.Name) -ccontains 'status') {
        if ($reservedOutcome.status -isnot [string] -or $reservedOutcome.status -cne 'reserved' -or
            -not (Test-Phase16ExactProperties -Value $reservedOutcome -Required @('claim_id','reserved_at','status')) -or
            $reservedOutcome.claim_id -isnot [string] -or $reservedOutcome.claim_id -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or
            $reservedOutcome.reserved_at -isnot [string] -or -not (Test-Phase16UtcTimestamp -Value $reservedOutcome.reserved_at)
        ) { throw 'transaction_invalid' }
        if ($reservedOutcome.claim_id -ceq $ClaimId -and $reservedOutcome.reserved_at -cne $journal.reserved_at) { throw 'transaction_invalid' }
        }
    $recoveryRoot = Join-Path $StateRoot 'recovery-outcomes'
    $recoveryOutcomePath = Get-Phase16LifecyclePath -LifecycleRoot $recoveryRoot -ClaimId $ClaimId
    if ($isImmediatePredecessorV1 -or $isLegacyV1) {
        [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('locks','outcome-locks','claims','transactions','recovery-outcomes','outcomes'))
        if ($isLegacyV1 -and $null -eq $journal.terminal_path) {
            $stagedPathState = Get-Phase16NoFollowPathState -Path $journal.staged_path
            $outcomePathState = Get-Phase16NoFollowPathState -Path $journal.outcome_path
            $recoveryPathState = Get-Phase16NoFollowPathState -Path $recoveryOutcomePath
            $legacyReservation = if ($outcomePathState -ceq 'file') { ConvertFrom-Phase16CanonicalJsonFile -Path $journal.outcome_path } else { $null }
            $outcomeIsExactReservation = $outcomePathState -ceq 'file' -and $null -ne $legacyReservation -and
                (Test-Phase16ExactProperties -Value $legacyReservation -Required @('claim_id','reserved_at','status')) -and
                $legacyReservation.claim_id -is [string] -and $legacyReservation.claim_id -ceq $ClaimId -and
                $legacyReservation.reserved_at -is [string] -and $legacyReservation.reserved_at -ceq $journal.reserved_at -and
                $legacyReservation.status -is [string] -and $legacyReservation.status -ceq 'reserved'
            if ($stagedPathState -cne 'absent' -or $recoveryPathState -cne 'absent' -or ($outcomePathState -cne 'absent' -and -not $outcomeIsExactReservation)) {
                throw 'transaction_invalid'
            }
        }
        $migrationStartedAt = if ($isImmediatePredecessorV1) { $journal.started_at } elseif ($null -eq $journal.terminal_path) { $journal.reserved_at } else { $null }
        if ($isLegacyV1 -and $null -eq $journal.terminal_path) {
            $journal | Add-Member -NotePropertyName started_at -NotePropertyValue $migrationStartedAt
        }
        if ($isImmediatePredecessorV1 -or $null -ne $migrationStartedAt) {
            $journal.schema = 'amn2.phase16.readonly-preflight-transaction.v2'
        }
        if ($null -ne $journal.terminal_path) {
            if (-not (Test-Phase16ExactTerminalJournalBinding -Journal $journal -StateRoot $StateRoot -ClaimId $ClaimId -ExpectedOutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath)) { throw 'transaction_invalid' }
            $predecessorTerminalPath = [IO.Path]::GetFullPath($journal.terminal_path)
            $authoritativeArtifactFound = $false
            foreach ($artifactPath in @($journal.staged_path, $predecessorTerminalPath)) {
                if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) { continue }
                if ([IO.Path]::GetFullPath($artifactPath) -ceq [IO.Path]::GetFullPath($journal.outcome_path) -and
                    (Test-Phase16OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId)) { continue }
                $artifact = ConvertFrom-Phase16CanonicalJsonFile -Path $artifactPath
                if ($null -eq $artifact -or (Get-Phase16CanonicalJsonSha256 -Value $artifact) -cne $journal.terminal_outcome_sha256) { throw 'transaction_invalid' }
                if ($isLegacyV1) {
                    if (@($artifact.PSObject.Properties.Name) -cnotcontains 'started_at' -or $artifact.started_at -isnot [string] -or
                        -not (Test-Phase16UtcTimestamp -Value $artifact.started_at)) { throw 'transaction_invalid' }
                    if ($null -eq $migrationStartedAt) {
                        $migrationStartedAt = $artifact.started_at
                        $journal | Add-Member -NotePropertyName started_at -NotePropertyValue $migrationStartedAt
                        $journal.schema = 'amn2.phase16.readonly-preflight-transaction.v2'
                    } elseif ($artifact.started_at -cne $migrationStartedAt) { throw 'transaction_invalid' }
                }
                if (-not (Test-Phase16ExactPublishedTerminalOutcome -Document $artifact -Journal $journal)) { throw 'transaction_invalid' }
                $authoritativeArtifactFound = $true
            }
            if ($isLegacyV1 -and -not $authoritativeArtifactFound) { throw 'transaction_invalid' }
        }
        [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
        Write-Phase16AtomicJson -Path $journalPath -Value $journal -OwnerId $ClaimId
        $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $journalPath
        if ($null -eq $journal -or -not (Test-Phase16ExactProperties -Value $journal -Required $v2Required) -or $journal.schema -cne 'amn2.phase16.readonly-preflight-transaction.v2' -or
            $journal.started_at -cne $migrationStartedAt) { throw 'transaction_invalid' }
    }
    if ($null -ne $journal.terminal_path -and -not (Test-Phase16ExactTerminalJournalBinding -Journal $journal -StateRoot $StateRoot -ClaimId $ClaimId -ExpectedOutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath)) { throw 'transaction_invalid' }
    Remove-Phase16TransactionTemps -TransactionPath $journalPath -ClaimId $ClaimId
    if ($null -ne $journal.terminal_path) {
        $terminalPath = [IO.Path]::GetFullPath($journal.terminal_path)
        $terminalIsCurrent = $terminalPath -ceq [IO.Path]::GetFullPath($journal.outcome_path)
        $terminalIsRecovery = $terminalPath -ceq [IO.Path]::GetFullPath($recoveryOutcomePath)
        $stagedExists = Test-Path -LiteralPath $journal.staged_path -PathType Leaf
        $staged = if ($stagedExists) { ConvertFrom-Phase16CanonicalJsonFile -Path $journal.staged_path } else { $null }
        if ($stagedExists -and $null -eq $staged) { throw 'transaction_invalid' }
        $stagedDigest = if ($null -ne $staged) { Get-Phase16CanonicalJsonSha256 -Value $staged } else { '' }
        $stagedValid = $null -ne $staged -and $stagedDigest -ceq $journal.terminal_outcome_sha256 -and (Test-Phase16ExactPublishedTerminalOutcome -Document $staged -Journal $journal)
        $publishedExists = Test-Path -LiteralPath $terminalPath -PathType Leaf
        $published = if ($publishedExists) { ConvertFrom-Phase16CanonicalJsonFile -Path $terminalPath } else { $null }
        if ($publishedExists -and $null -eq $published) { throw 'transaction_invalid' }
        $publishedDigest = if ($null -ne $published) { Get-Phase16CanonicalJsonSha256 -Value $published } else { '' }
        $publishedValid = $null -ne $published -and $publishedDigest -ceq $journal.terminal_outcome_sha256 -and (Test-Phase16ExactPublishedTerminalOutcome -Document $published -Journal $journal)
        $lifecycleReserved = $null -ne $reservedLifecycle -and (Test-Phase16ExactProperties -Value $reservedLifecycle -Required @('claim_id','reason_code','reserved_at','status')) -and
            $reservedLifecycle.claim_id -is [string] -and $reservedLifecycle.claim_id -ceq $ClaimId -and $reservedLifecycle.reason_code -is [string] -and $reservedLifecycle.reason_code -ceq 'not_applicable' -and
            $reservedLifecycle.reserved_at -is [string] -and $reservedLifecycle.reserved_at -ceq $journal.reserved_at -and $reservedLifecycle.status -is [string] -and $reservedLifecycle.status -ceq 'reserved'
        $lifecycleTerminal = $null -ne $reservedLifecycle -and (Test-Phase16ExactProperties -Value $reservedLifecycle -Required @('claim_id','ended_at','reason_code','status')) -and
            $reservedLifecycle.claim_id -is [string] -and $reservedLifecycle.claim_id -ceq $ClaimId -and $reservedLifecycle.ended_at -is [string] -and $reservedLifecycle.ended_at -ceq $journal.terminal_ended_at -and
            $reservedLifecycle.reason_code -is [string] -and $reservedLifecycle.reason_code -ceq $journal.terminal_reason_code -and $reservedLifecycle.status -is [string] -and $reservedLifecycle.status -ceq $journal.terminal_status
        $outcomeOwned = Test-Phase16OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId

        if ($publishedValid) {
            if ($journal.phase -cne 'finalizing' -or -not $lifecycleTerminal -or $stagedExists) { throw 'transaction_invalid' }
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes'))
            Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            [IO.File]::Delete($journalPath)
            return [pscustomobject]@{ Recovered = $true; OutcomePath = $terminalPath }
        }

        if ($terminalIsCurrent -and $stagedValid -and $outcomeOwned) {
            if ($journal.phase -cnotin @('owned','transport_attempted','ssh_started','outcome_staged','finalizing')) { throw 'transaction_invalid' }
            if (($journal.phase -cin @('owned','transport_attempted','ssh_started') -and -not $lifecycleReserved) -or
                ($journal.phase -ceq 'outcome_staged' -and -not ($lifecycleReserved -or $lifecycleTerminal)) -or
                ($journal.phase -ceq 'finalizing' -and -not $lifecycleTerminal)) { throw 'transaction_invalid' }
            if ($journal.phase -cin @('owned','transport_attempted','ssh_started')) {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
                [void](Set-Phase16TransactionPhase -TransactionPath $journalPath -ClaimId $ClaimId -Phase 'outcome_staged' -Lock $Lock)
                $journal.phase = 'outcome_staged'
            }
            if ($lifecycleReserved) {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
                [void](Set-Phase16ClaimTerminal -LifecyclePath $lifecyclePath -ClaimId $ClaimId -Status $journal.terminal_status -EndedAt $journal.terminal_ended_at -ReasonCode $journal.terminal_reason_code)
            }
            if ($journal.phase -cne 'finalizing') {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
                [void](Set-Phase16TransactionPhase -TransactionPath $journalPath -ClaimId $ClaimId -Phase 'finalizing' -Lock $Lock)
                $journal.phase = 'finalizing'
            }
            $backupPath = $journal.outcome_path + '.phase16-' + $ClaimId + '.recovery-backup-' + [Guid]::NewGuid().ToString('N')
            try {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes')); [void](Assert-Phase16TrustedOutcomeParent -StateRoot $StateRoot -OutcomePath $journal.outcome_path -AuthorizedSid $AuthorizedSid)
                if (-not (Test-Phase16OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId)) { throw 'transaction_invalid' }
                [IO.File]::Replace($journal.staged_path, $journal.outcome_path, $backupPath, $true)
            } finally {
                if (Test-Path -LiteralPath $backupPath -PathType Leaf) { [IO.File]::Delete($backupPath) }
            }
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes'))
            Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            [IO.File]::Delete($journalPath)
            return [pscustomobject]@{ Recovered = $true; OutcomePath = [IO.Path]::GetFullPath($journal.outcome_path) }
        }

        if ($terminalIsCurrent -and $journal.phase -ceq 'finalizing' -and -not $stagedExists -and $outcomeOwned) {
            $expectedCurrent = New-Phase16FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 $journal.manifest_sha256 -CollectorSha256 $journal.collector_sha256 -ExpectedHost $journal.expected_host -StartedAt $journal.started_at -EndedAt $journal.terminal_ended_at -SshUsed $journal.ssh_used
            $expectedCurrentValid = $journal.terminal_status -ceq 'failed' -and $journal.terminal_reason_code -ceq 'transport_failed' -and (Get-Phase16CanonicalJsonSha256 -Value $expectedCurrent) -ceq $journal.terminal_outcome_sha256
            if (-not $expectedCurrentValid -or -not ($lifecycleReserved -or $lifecycleTerminal)) { throw 'transaction_invalid' }
            if ($lifecycleReserved) {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
                [void](Set-Phase16ClaimTerminal -LifecyclePath $lifecyclePath -ClaimId $ClaimId -Status 'failed' -EndedAt $journal.terminal_ended_at -ReasonCode 'transport_failed')
            }
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes'))
            [void](Assert-Phase16TrustedOutcomeParent -StateRoot $StateRoot -OutcomePath $journal.outcome_path -AuthorizedSid $AuthorizedSid)
            if (-not (Test-Phase16OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId)) { throw 'transaction_invalid' }
            Write-Phase16AtomicJson -Path $journal.outcome_path -Value $expectedCurrent -OwnerId $ClaimId
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes'))
            Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            [IO.File]::Delete($journalPath)
            return [pscustomobject]@{ Recovered = $true; OutcomePath = [IO.Path]::GetFullPath($journal.outcome_path) }
        }

        if ($terminalIsRecovery -and $journal.phase -ceq 'finalizing' -and -not $stagedExists) {
            $expectedRecovery = New-Phase16FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 $journal.manifest_sha256 -CollectorSha256 $journal.collector_sha256 -ExpectedHost $journal.expected_host -StartedAt $journal.started_at -EndedAt $journal.terminal_ended_at -SshUsed $journal.ssh_used
            $expectedRecoveryValid = $journal.terminal_status -ceq 'failed' -and $journal.terminal_reason_code -ceq 'transport_failed' -and (Get-Phase16CanonicalJsonSha256 -Value $expectedRecovery) -ceq $journal.terminal_outcome_sha256
            if (-not $expectedRecoveryValid -or -not ($lifecycleReserved -or $lifecycleTerminal)) { throw 'transaction_invalid' }
            if ($lifecycleReserved) {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes'))
                Write-Phase16AtomicJson -Path $lifecyclePath -Value ([ordered]@{ claim_id = $ClaimId; ended_at = $journal.terminal_ended_at; reason_code = 'transport_failed'; status = 'failed' }) -OwnerId $ClaimId
            }
            if (-not $publishedExists) {
                [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes'))
                Write-Phase16AtomicJson -Path $recoveryOutcomePath -Value $expectedRecovery -OwnerId $ClaimId
            } elseif (-not $publishedValid) { throw 'transaction_invalid' }
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes'))
            Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            [IO.File]::Delete($journalPath)
            return [pscustomobject]@{ Recovered = $true; OutcomePath = [IO.Path]::GetFullPath($recoveryOutcomePath) }
        }

        if ($terminalIsCurrent -and -not $stagedExists -and $outcomeOwned -and $lifecycleReserved -and $journal.phase -cin @('owned','transport_attempted','ssh_started')) {
            $journal.terminal_ended_at = $null
            $journal.terminal_outcome_sha256 = $null
            $journal.terminal_path = $null
            $journal.terminal_reason_code = $null
            $journal.terminal_status = $null
            if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcomes')) }
            Write-Phase16AtomicJson -Path $journalPath -Value $journal -OwnerId $ClaimId
        } else { throw 'transaction_invalid' }
    }
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
    Remove-Phase16OwnedStateResidues -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
    $sshUsed = if ($phaseValid) { [bool]$journal.ssh_used } else { $true }
    $failure = New-Phase16FailureOutcome -ReasonCode 'transport_failed' -ManifestSha256 $journal.manifest_sha256 -CollectorSha256 $journal.collector_sha256 -ExpectedHost $journal.expected_host -StartedAt $journal.started_at -EndedAt $EndedAt -SshUsed $sshUsed
    if (Test-Phase16OutcomeOwnership -ReservationPath $journal.outcome_path -ClaimId $ClaimId) {
        $publishedPath = [IO.Path]::GetFullPath($journal.outcome_path)
    } else {
        if (-not (Test-Path -LiteralPath $recoveryRoot)) {
            if ($hasExpectedBindings) { throw 'state_root_invalid' }
            [void][IO.Directory]::CreateDirectory($recoveryRoot)
        }
        if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
        $recoveryItem = Get-Item -LiteralPath $recoveryRoot -Force
        if (($recoveryItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'transaction_invalid' }
        $publishedPath = $recoveryOutcomePath
    }
    $journal.phase = 'finalizing'
    $journal.terminal_ended_at = $EndedAt
    $journal.terminal_outcome_sha256 = Get-Phase16CanonicalJsonSha256 -Value $failure
    $journal.terminal_path = $publishedPath
    $journal.terminal_reason_code = 'transport_failed'
    $journal.terminal_status = 'failed'
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
    Write-Phase16AtomicJson -Path $journalPath -Value $journal -OwnerId $ClaimId
    $terminal = [ordered]@{ claim_id = $ClaimId; ended_at = $EndedAt; reason_code = 'transport_failed'; status = 'failed' }
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
    Write-Phase16AtomicJson -Path $lifecyclePath -Value $terminal -OwnerId $ClaimId
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
    Write-Phase16AtomicJson -Path $publishedPath -Value $failure -OwnerId $ClaimId
    if ($hasExpectedBindings) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $StateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','recovery-outcomes','outcomes')) }
    if (Test-Path -LiteralPath $journal.staged_path -PathType Leaf) { [IO.File]::Delete($journal.staged_path) }
    Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $lifecyclePath -OutcomePath $journal.outcome_path -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
    [IO.File]::Delete($journalPath)
    if (Test-Path -LiteralPath $journalPath) { throw 'transaction_reconciliation_failed' }
    return [pscustomobject]@{ Recovered = $true; OutcomePath = $publishedPath }
    } finally {
        if ($ownsOutcomeLock) { $OutcomeLock.Stream.Dispose() }
    }
    } finally {
        if ($ownsNamespaceLock) { $NamespaceLock.Stream.Dispose() }
    }
}

function Set-Phase16ClaimTerminal {
    param(
        [Parameter(Mandatory)][string]$LifecyclePath,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][ValidateSet('completed','failed')][string]$Status,
        [Parameter(Mandatory)][string]$EndedAt,
        [Parameter(Mandatory)][string]$ReasonCode
    )
    if (-not (Test-Path -LiteralPath $LifecyclePath -PathType Leaf) -or -not (Test-Phase16UtcTimestamp -Value $EndedAt)) { throw 'claim_lifecycle_invalid' }
    if (($Status -ceq 'completed' -and $ReasonCode -cne 'not_applicable') -or ($Status -ceq 'failed' -and $ReasonCode -cnotin $script:Phase16FailureReasons)) { throw 'claim_lifecycle_invalid' }
    $current = ConvertFrom-Phase16CanonicalJsonFile -Path $LifecyclePath
    if ($null -eq $current -or $current.claim_id -cne $ClaimId -or $current.status -cnotin @('reserved','completed','failed')) { throw 'claim_lifecycle_invalid' }
    if ($Status -ceq 'completed' -and $current.status -cne 'reserved') { throw 'claim_lifecycle_invalid' }
    $temporaryPath = $LifecyclePath + '.phase16-' + $ClaimId + '.terminal-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $LifecyclePath + '.phase16-' + $ClaimId + '.backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase16CreateNewJson -Path $temporaryPath -Value ([ordered]@{ claim_id = $ClaimId; ended_at = $EndedAt; reason_code = $ReasonCode; status = $Status }) -OwnerId $ClaimId
        [IO.File]::Replace($temporaryPath, $LifecyclePath, $backupPath, $true)
    } finally {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { Remove-Item -LiteralPath $temporaryPath -Force }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) { Remove-Item -LiteralPath $backupPath -Force }
    }
    return $LifecyclePath
}

function Publish-Phase16TerminalOutcome {
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
        [string]$ManifestSha256,
        [string]$CollectorSha256,
        [string]$ExpectedHost,
        [string]$ReservedAt,
        [string]$StateRoot,
        [string]$AuthorizedSid,
        [object]$Lock,
        [object]$OutcomeLock,
        [object]$NamespaceLock
    )
    $ownsNamespaceLock = $false
    $transactionStateRoot = $null
    if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) {
        $transactionStateRoot = Split-Path -Parent (Split-Path -Parent ([IO.Path]::GetFullPath($TransactionPath)))
        if ([string]::IsNullOrWhiteSpace($StateRoot) -or [IO.Path]::GetFullPath($StateRoot) -cne [IO.Path]::GetFullPath($transactionStateRoot) -or [string]::IsNullOrWhiteSpace($AuthorizedSid)) { throw 'transaction_invalid' }
        if (-not (Test-Phase16ClaimLock -Lock $Lock -StateRoot $transactionStateRoot -ClaimId $ClaimId)) { throw 'claim_lock_invalid' }
        if (-not (Test-Phase16OutcomeLock -Lock $OutcomeLock -StateRoot $transactionStateRoot -OutcomePath $OutcomePath -ClaimId $ClaimId)) { throw 'outcome_lock_invalid' }
        if ($null -eq $NamespaceLock) { $NamespaceLock = Enter-Phase16OutcomesNamespaceLock -StateRoot $transactionStateRoot; $ownsNamespaceLock = $true }
        elseif (-not (Test-Phase16OutcomesNamespaceLock -Lock $NamespaceLock -StateRoot $transactionStateRoot)) { throw 'outcome_namespace_invalid' }
    }
    try {
    if ([IO.Path]::GetFullPath($ReservationPath) -cne [IO.Path]::GetFullPath($OutcomePath) -or -not (Test-Phase16OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
    if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) {
        $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $TransactionPath
        $pendingPath = [IO.Path]::GetFullPath($OutcomePath) + '.phase16-' + $ClaimId + '.staged'
        $isExactPublishableJournal = {
            param([object]$Candidate)
            if ($Status -ceq 'failed' -and $ReasonCode -ceq 'claim_invalid' -and (Test-Phase16ExactNonterminalTransactionJournal -Journal $Candidate -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ReservedAt $ReservedAt -ExpectedPhase 'owned' -ExpectedSshUsed $false)) { return $true }
            if ($Status -ceq 'failed' -and $ReasonCode -ceq 'transport_failed' -and (Test-Phase16ExactNonterminalTransactionJournal -Journal $Candidate -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ReservedAt $ReservedAt -ExpectedPhase 'transport_attempted' -ExpectedSshUsed $true)) { return $true }
            return Test-Phase16ExactNonterminalTransactionJournal -Journal $Candidate -TransactionPath $TransactionPath -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ReservedAt $ReservedAt -ExpectedPhase 'ssh_started' -ExpectedSshUsed $true
        }
        if (-not (& $isExactPublishableJournal $journal)) {
            try { $journal.staged_path = $pendingPath } catch { throw 'transaction_invalid' }
            if (-not (& $isExactPublishableJournal $journal)) { throw 'transaction_invalid' }
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes'))
            Write-Phase16AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
            $journal = ConvertFrom-Phase16CanonicalJsonFile -Path $TransactionPath
            if (-not (& $isExactPublishableJournal $journal)) { throw 'transaction_invalid' }
        }
        if ($Outcome.started_at -isnot [string] -or $Outcome.started_at -cne $journal.started_at -or -not (Test-Phase16UtcTimestamp -Value $Outcome.started_at)) { throw 'transaction_invalid' }
        $journal.terminal_ended_at = $EndedAt
        $journal.terminal_outcome_sha256 = Get-Phase16CanonicalJsonSha256 -Value $Outcome
        $journal.terminal_path = [IO.Path]::GetFullPath($OutcomePath)
        $journal.terminal_reason_code = $ReasonCode
        $journal.terminal_status = $Status
        [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes'))
        Write-Phase16AtomicJson -Path $TransactionPath -Value $journal -OwnerId $ClaimId
    } else {
        $pendingPath = $OutcomePath + '.phase16-' + $ClaimId + '.pending-' + [Guid]::NewGuid().ToString('N')
    }
    $backupPath = $OutcomePath + '.phase16-' + $ClaimId + '.reservation-backup-' + [Guid]::NewGuid().ToString('N')
    try {
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes')); [void](Assert-Phase16TrustedOutcomeParent -StateRoot $transactionStateRoot -OutcomePath $OutcomePath -AuthorizedSid $AuthorizedSid) }
        Write-Phase16CreateNewJson -Path $pendingPath -Value $Outcome -OwnerId $ClaimId
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Set-Phase16TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'outcome_staged' -Lock $Lock) }
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes')); [void](Assert-Phase16TrustedOutcomeParent -StateRoot $transactionStateRoot -OutcomePath $OutcomePath -AuthorizedSid $AuthorizedSid) }
        [void](Set-Phase16ClaimTerminal -LifecyclePath $LifecyclePath -ClaimId $ClaimId -Status $Status -EndedAt $EndedAt -ReasonCode $ReasonCode)
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Set-Phase16TransactionPhase -TransactionPath $TransactionPath -ClaimId $ClaimId -Phase 'finalizing' -Lock $Lock) }
        if (-not (Test-Phase16OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) { [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes')); [void](Assert-Phase16TrustedOutcomeParent -StateRoot $transactionStateRoot -OutcomePath $OutcomePath -AuthorizedSid $AuthorizedSid) }
        [IO.File]::Replace($pendingPath, $OutcomePath, $backupPath, $true)
        if (-not [string]::IsNullOrWhiteSpace($TransactionPath)) {
            [void](Assert-Phase16TrustedManagedStateChain -StateRoot $transactionStateRoot -AuthorizedSid $AuthorizedSid -RequiredChildren @('claims','transactions','outcome-locks','outcomes'))
            $recoveryOutcomePath = Get-Phase16LifecyclePath -LifecycleRoot (Join-Path $transactionStateRoot 'recovery-outcomes') -ClaimId $ClaimId
            Remove-Phase16OwnedStateResidues -LifecyclePath $LifecyclePath -OutcomePath $OutcomePath -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            Assert-Phase16OwnedStateResiduesAbsent -LifecyclePath $LifecyclePath -OutcomePath $OutcomePath -RecoveryOutcomePath $recoveryOutcomePath -ClaimId $ClaimId
            [IO.File]::Delete($TransactionPath)
            if (Test-Path -LiteralPath $TransactionPath) { throw 'transaction_finalize_failed' }
        }
    } finally {
        if (Test-Path -LiteralPath $pendingPath -PathType Leaf) { Remove-Item -LiteralPath $pendingPath -Force }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) { Remove-Item -LiteralPath $backupPath -Force }
    }
    } finally {
        if ($ownsNamespaceLock) { $NamespaceLock.Stream.Dispose() }
    }
}

function New-Phase16FailureOutcome {
    param([string]$ReasonCode, [string]$ManifestSha256, [string]$CollectorSha256, [string]$ExpectedHost, [string]$StartedAt, [string]$EndedAt, [bool]$SshUsed)
    if ($ReasonCode -cnotin $script:Phase16FailureReasons) { throw 'failure_reason_invalid' }
    return [ordered]@{
        collector_sha256 = $CollectorSha256
        decision = 'stop'
        ended_at = $EndedAt
        expected_host = $ExpectedHost
        manifest_sha256 = $ManifestSha256
        package_id = $script:Phase16PackageId
        reason_code = $ReasonCode
        safety = [ordered]@{ live_mutation = $false; raw_output_persisted = $false; remote_file_written = $false; ssh_used = $SshUsed }
        schema = $script:Phase16FailureSchema
        started_at = $StartedAt
        transport_disposition = $(if ($SshUsed) { 'read_only_failed' } else { 'not_run' })
    }
}

function Invoke-Phase16RunnerMain {
    if (-not $FutureAuthorization -or [string]::IsNullOrWhiteSpace($FutureClaimPath)) { throw 'future_claim_required' }
    if ([string]::IsNullOrWhiteSpace($PackageRoot) -or [string]::IsNullOrWhiteSpace($OutcomePath) -or -not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost)) { throw 'runner_arguments_invalid' }
    try { $OutcomePath = [IO.Path]::GetFullPath($OutcomePath) } catch { throw 'runner_arguments_invalid' }
    $startedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $manifestPath = Join-Path $PackageRoot 'manifest.json'
    $collectorPath = Join-Path $PackageRoot 'tooling\scripts\vps\phase16_spain_readonly_preflight_remote.sh'
    $manifestArtifact = Read-Phase16ManifestArtifact -Path $manifestPath
    $manifest = $manifestArtifact.Value
    if ($null -eq $manifest -or $manifest.package_id -cne $script:Phase16PackageId) { throw 'package_identity_invalid' }
    $manifestSha256 = $manifestArtifact.Sha256
    $collectorArtifact = Read-Phase16CollectorArtifact -Path $collectorPath
    $collectorSha256 = $collectorArtifact.Sha256
    $entry = @($manifest.entries | Where-Object { $_.path -ceq 'tooling/scripts/vps/phase16_spain_readonly_preflight_remote.sh' })
    if ($entry.Count -ne 1 -or $entry[0].sha256 -cne $collectorSha256) { throw 'collector_checksum_invalid' }
    [void](Assert-Phase16SpainTrustBundle -ExpectedHost $ExpectedHost)
    $claim = Read-Phase16FutureClaim -ClaimPath $FutureClaimPath
    if ($null -eq $claim -or -not (Test-Phase16ClaimIdentity -Claim $claim -ExpectedPackageId $script:Phase16PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost)) { throw 'claim_invalid' }
    $preProvisionNow = Get-Phase16AuthorizationInstant
    $preProvisionAt = $preProvisionNow.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    if (-not (Test-Phase16FutureClaim -Claim $claim -ExpectedPackageId $script:Phase16PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -At $preProvisionAt)) { throw 'claim_invalid' }
    $stateRoot = Initialize-Phase16ProductionStateRoot
    $authorizedSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $OutcomePath = Assert-Phase16TrustedOutcomeParent -StateRoot $stateRoot -OutcomePath $OutcomePath -AuthorizedSid $authorizedSid
    $namespaceLock = Enter-Phase16OutcomesNamespaceLock -StateRoot $stateRoot
    $claimLock = $null
    $transaction = $null
    try {
        $claimLock = Enter-Phase16ClaimLock -StateRoot $stateRoot -ClaimId $claim.claim_id
        $reconciled = Reconcile-Phase16Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $startedAt -Lock $claimLock -NamespaceLock $namespaceLock -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -AuthorizedSid $authorizedSid
        if ($reconciled.Recovered) { throw 'claim_replay' }
        $lifecyclePath = Get-Phase16LifecyclePath -LifecycleRoot (Join-Path $stateRoot 'claims') -ClaimId $claim.claim_id
        if (Test-Path -LiteralPath $lifecyclePath) { throw 'claim_replay' }
        $reservationNow = Get-Phase16AuthorizationInstant
        $reservationAt = $reservationNow.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        if (-not (Test-Phase16FutureClaim -Claim $claim -ExpectedPackageId $script:Phase16PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -At $reservationAt)) { throw 'claim_invalid' }
        $transaction = Start-Phase16Transaction -StateRoot $stateRoot -OutcomePath $OutcomePath -ClaimId $claim.claim_id -StartedAt $startedAt -ReservedAt $reservationAt -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -AuthorizedSid $authorizedSid -Lock $claimLock
        $sshUsed = $false
        $failureReason = 'transport_failed'
        $transportStarted = $false
        try {
            $rawDocument = Invoke-Phase16OneSshTransport -ExpectedHost $ExpectedHost -CollectorBytes $collectorArtifact.Bytes -Claim $claim -ClaimId $claim.claim_id -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedOutcomePath $OutcomePath -ReservedAt $reservationAt -Started ([ref]$transportStarted) -TransactionPath $transaction.JournalPath -Lock $claimLock
            $sshUsed = $transportStarted
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            $document = ConvertFrom-Phase16CanonicalJsonText -Text $rawDocument
            if ($null -eq $document) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            if (-not (Test-Phase16CollectorDocument -Document $document -ExpectedHost $ExpectedHost -ExpectedClaimId $claim.claim_id -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -StartedAt $startedAt -EndedAt $endedAt)) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            $evidence = ConvertTo-Phase16Evidence -Document $document -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt
            Publish-Phase16TerminalOutcome -LifecyclePath $transaction.LifecyclePath -ReservationPath $transaction.ReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'completed' -EndedAt $endedAt -ReasonCode 'not_applicable' -Outcome $evidence -TransactionPath $transaction.JournalPath -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ReservedAt $reservationAt -StateRoot $stateRoot -AuthorizedSid $authorizedSid -Lock $claimLock -OutcomeLock $transaction.OutcomeLock -NamespaceLock $namespaceLock
        } catch {
            if (-not $transportStarted -and $_.Exception.Message -ceq 'claim_invalid') { $failureReason = 'claim_invalid' }
            $sshUsed = $sshUsed -or $transportStarted -or (Test-Phase16TransactionRequiresConservativeSshUsed -TransactionPath $transaction.JournalPath -ClaimId $claim.claim_id -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ReservedAt $reservationAt -Lock $claimLock)
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            try {
                if (Test-Phase16OutcomeOwnership -ReservationPath $transaction.ReservationPath -ClaimId $claim.claim_id) {
                    $failure = New-Phase16FailureOutcome -ReasonCode $failureReason -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt -SshUsed $sshUsed
                    Publish-Phase16TerminalOutcome -LifecyclePath $transaction.LifecyclePath -ReservationPath $transaction.ReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'failed' -EndedAt $endedAt -ReasonCode $failureReason -Outcome $failure -TransactionPath $transaction.JournalPath -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ReservedAt $reservationAt -StateRoot $stateRoot -AuthorizedSid $authorizedSid -Lock $claimLock -OutcomeLock $transaction.OutcomeLock -NamespaceLock $namespaceLock
                } elseif (Test-Path -LiteralPath $transaction.JournalPath -PathType Leaf) {
                    [void](Reconcile-Phase16Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $endedAt -Lock $claimLock -OutcomeLock $transaction.OutcomeLock -NamespaceLock $namespaceLock -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ExpectedReservedAt $reservationAt -AuthorizedSid $authorizedSid)
                }
            } catch {
                if (Test-Path -LiteralPath $transaction.JournalPath -PathType Leaf) {
                    [void](Reconcile-Phase16Transaction -StateRoot $stateRoot -ClaimId $claim.claim_id -EndedAt $endedAt -Lock $claimLock -OutcomeLock $transaction.OutcomeLock -NamespaceLock $namespaceLock -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -ExpectedOutcomePath $OutcomePath -ExpectedReservedAt $reservationAt -AuthorizedSid $authorizedSid)
                }
            }
            throw
        }
    } finally {
        if ($null -ne $transaction -and $null -ne $transaction.OutcomeLock) { $transaction.OutcomeLock.Stream.Dispose() }
        if ($null -ne $claimLock) { $claimLock.Stream.Dispose() }
        $namespaceLock.Stream.Dispose()
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-Phase16RunnerMain
        exit 0
    } catch {
        [Console]::Error.WriteLine('AMN2_PHASE16_PREFLIGHT_RUNNER_STOP')
        exit 64
    }
}
