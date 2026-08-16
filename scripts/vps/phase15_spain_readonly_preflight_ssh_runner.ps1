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

function Get-Phase15FileSha256 {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
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
        $bytes = [IO.File]::ReadAllBytes($Path)
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

function Test-Phase15FutureClaim {
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
    $now = [DateTimeOffset]::UtcNow
    if ($issued -ge $expires -or $now -lt $issued -or $now -ge $expires) { return $false }
    return $true
}

function Test-Phase15CollectorDocument {
    param(
        [Parameter(Mandatory)][object]$Document,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedClaimId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256
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
        if ($ExpectedClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $Document.observed_at)) { return $false }
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

function New-Phase15SshArguments {
    param([Parameter(Mandatory)][string]$ExpectedHost, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ManifestSha256, [Parameter(Mandatory)][string]$CollectorSha256)
    if (-not (Test-Phase15ExpectedHost -ExpectedHost $ExpectedHost) -or $ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or $ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or $CollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'transport_envelope_invalid' }
    $remote = "bash -s -- '$($script:Phase15PackageId)' '$ManifestSha256' '$CollectorSha256' '$ClaimId' '$ExpectedHost'"
    return @('-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1','--',$ExpectedHost,$remote)
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

function Invoke-Phase15OneSshTransport {
    param(
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][byte[]]$CollectorBytes,
        [Parameter(Mandatory)][string]$ClaimId,
        [Parameter(Mandatory)][string]$ManifestSha256,
        [Parameter(Mandatory)][string]$CollectorSha256
    )
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'C:\Windows\System32\OpenSSH\ssh.exe'
    $start.Arguments = ((New-Phase15SshArguments -ExpectedHost $ExpectedHost -ClaimId $ClaimId -ManifestSha256 $ManifestSha256 -CollectorSha256 $CollectorSha256) | ForEach-Object { ConvertTo-Phase15WindowsArgument -Argument $_ }) -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    if (-not $process.Start()) { throw 'transport_failed' }
    $stdout = [IO.MemoryStream]::new()
    $stderr = [IO.MemoryStream]::new()
    try {
        $process.StandardInput.BaseStream.Write($CollectorBytes, 0, $CollectorBytes.Length)
        $process.StandardInput.Close()
        $stdoutBytes = [byte[]]::new(4096)
        $stderrBytes = [byte[]]::new(4096)
        $stdoutTask = $process.StandardOutput.BaseStream.ReadAsync($stdoutBytes, 0, $stdoutBytes.Length)
        $stderrTask = $process.StandardError.BaseStream.ReadAsync($stderrBytes, 0, $stderrBytes.Length)
        $stdoutDone = $false
        $stderrDone = $false
        $deadline = [DateTimeOffset]::UtcNow.AddSeconds(30)
        while (-not ($process.HasExited -and $stdoutDone -and $stderrDone)) {
            if ([DateTimeOffset]::UtcNow -ge $deadline) { $process.Kill(); throw 'transport_failed' }
            if (-not $stdoutDone -and $stdoutTask.IsCompleted) {
                $count = $stdoutTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stdoutDone = $true } else {
                    if (Add-Phase15BoundedBytes -Buffer $stdout -Bytes $stdoutBytes -Count $count -MaximumBytes 65536) { $process.Kill(); throw 'transport_failed' }
                    $stdoutTask = $process.StandardOutput.BaseStream.ReadAsync($stdoutBytes, 0, $stdoutBytes.Length)
                }
            }
            if (-not $stderrDone -and $stderrTask.IsCompleted) {
                $count = $stderrTask.GetAwaiter().GetResult()
                if ($count -eq 0) { $stderrDone = $true } else {
                    if (Add-Phase15BoundedBytes -Buffer $stderr -Bytes $stderrBytes -Count $count -MaximumBytes 65536) { $process.Kill(); throw 'transport_failed' }
                    $stderrTask = $process.StandardError.BaseStream.ReadAsync($stderrBytes, 0, $stderrBytes.Length)
                }
            }
            Start-Sleep -Milliseconds 10
        }
        if ($process.ExitCode -ne 0) { throw 'transport_failed' }
        return [Text.UTF8Encoding]::new($false, $true).GetString($stdout.ToArray())
    } finally {
        $stdout.Dispose()
        $stderr.Dispose()
        $process.Dispose()
    }
}

function Write-Phase15CreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value)
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase15CanonicalJsonText -Value $Value) + "`n")
    $stream = [IO.FileStream]::new($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Get-Phase15LifecyclePath {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or [string]::IsNullOrWhiteSpace($LifecycleRoot)) { throw 'claim_lifecycle_invalid' }
    $root = [IO.Path]::GetFullPath($LifecycleRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $path = [IO.Path]::GetFullPath([IO.Path]::Combine($root, $ClaimId + '.json'))
    if ([IO.Path]::GetDirectoryName($path).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $root) { throw 'claim_lifecycle_invalid' }
    return $path
}

function Get-Phase15ProductionStateRoot {
    return $script:Phase15ProductionStateRoot
}

function Reserve-Phase15Claim {
    param([Parameter(Mandatory)][string]$LifecycleRoot, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $ReservedAt)) { throw 'claim_invalid' }
    if (-not (Test-Path -LiteralPath $LifecycleRoot -PathType Container)) { throw 'claim_lifecycle_invalid' }
    $rootItem = Get-Item -LiteralPath $LifecycleRoot -Force
    if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    $lifecyclePath = Get-Phase15LifecyclePath -LifecycleRoot $LifecycleRoot -ClaimId $ClaimId
    Write-Phase15CreateNewJson -Path $lifecyclePath -Value ([ordered]@{ claim_id = $ClaimId; reason_code = 'not_applicable'; reserved_at = $ReservedAt; status = 'reserved' })
    return $lifecyclePath
}

function Reserve-Phase15OutcomeSlot {
    param([Parameter(Mandatory)][string]$OutcomePath, [Parameter(Mandatory)][string]$ClaimId, [Parameter(Mandatory)][string]$ReservedAt)
    if ($ClaimId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,127}$' -or -not (Test-Phase15UtcTimestamp -Value $ReservedAt)) { throw 'outcome_reservation_invalid' }
    $fullPath = [IO.Path]::GetFullPath($OutcomePath)
    $parent = [IO.Path]::GetDirectoryName($fullPath)
    if ([string]::IsNullOrWhiteSpace($parent) -or -not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'outcome_reservation_invalid' }
    Write-Phase15CreateNewJson -Path $fullPath -Value ([ordered]@{ claim_id = $ClaimId; reserved_at = $ReservedAt; status = 'reserved' })
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
    if ($null -eq $current -or $current.claim_id -cne $ClaimId -or $current.status -notin @('reserved','completed')) { throw 'claim_lifecycle_invalid' }
    if ($Status -ceq 'completed' -and $current.status -cne 'reserved') { throw 'claim_lifecycle_invalid' }
    $temporaryPath = $LifecyclePath + '.terminal-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $LifecyclePath + '.backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase15CreateNewJson -Path $temporaryPath -Value ([ordered]@{ claim_id = $ClaimId; ended_at = $EndedAt; reason_code = $ReasonCode; status = $Status })
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
        [Parameter(Mandatory)][object]$Outcome
    )
    if ([IO.Path]::GetFullPath($ReservationPath) -cne [IO.Path]::GetFullPath($OutcomePath) -or -not (Test-Phase15OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
    $pendingPath = $OutcomePath + '.pending-' + [Guid]::NewGuid().ToString('N')
    $backupPath = $OutcomePath + '.reservation-backup-' + [Guid]::NewGuid().ToString('N')
    try {
        Write-Phase15CreateNewJson -Path $pendingPath -Value $Outcome
        [void](Set-Phase15ClaimTerminal -LifecyclePath $LifecyclePath -ClaimId $ClaimId -Status $Status -EndedAt $EndedAt -ReasonCode $ReasonCode)
        if (-not (Test-Phase15OutcomeOwnership -ReservationPath $ReservationPath -ClaimId $ClaimId)) { throw 'outcome_reservation_invalid' }
        [IO.File]::Replace($pendingPath, $OutcomePath, $backupPath, $true)
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
    $manifestPath = Join-Path $PackageRoot 'manifest.json'
    $collectorPath = Join-Path $PackageRoot 'tooling\scripts\vps\phase15_spain_readonly_preflight_remote.sh'
    $manifest = ConvertFrom-Phase15CanonicalJsonFile -Path $manifestPath
    if ($null -eq $manifest -or $manifest.package_id -cne $script:Phase15PackageId) { throw 'package_identity_invalid' }
    $manifestSha256 = Get-Phase15FileSha256 -Path $manifestPath
    $collectorSha256 = Get-Phase15FileSha256 -Path $collectorPath
    $entry = @($manifest.entries | Where-Object { $_.path -ceq 'tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh' })
    if ($entry.Count -ne 1 -or $entry[0].sha256 -cne $collectorSha256) { throw 'collector_checksum_invalid' }
    $claim = Read-Phase15FutureClaim -ClaimPath $FutureClaimPath
    if ($null -eq $claim -or -not (Test-Phase15FutureClaim -Claim $claim -ExpectedPackageId $script:Phase15PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost)) { throw 'claim_invalid' }
    $startedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $stateRoot = Get-Phase15ProductionStateRoot
    if (-not (Test-Path -LiteralPath $stateRoot)) { [void][IO.Directory]::CreateDirectory($stateRoot) }
    $stateRootItem = Get-Item -LiteralPath $stateRoot -Force
    if (($stateRootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'claim_lifecycle_invalid' }
    $lifecycleRoot = Join-Path $stateRoot 'claims'
    if (-not (Test-Path -LiteralPath $lifecycleRoot)) { [void][IO.Directory]::CreateDirectory($lifecycleRoot) }
    $outcomeReservationPath = Reserve-Phase15OutcomeSlot -OutcomePath $OutcomePath -ClaimId $claim.claim_id -ReservedAt $startedAt
    $lifecyclePath = $null
    try {
        $lifecyclePath = Reserve-Phase15Claim -LifecycleRoot $lifecycleRoot -ClaimId $claim.claim_id -ReservedAt $startedAt
        $sshUsed = $false
        $failureReason = 'transport_failed'
        try {
            $collectorBytes = [IO.File]::ReadAllBytes($collectorPath)
            $sshUsed = $true
            $rawDocument = Invoke-Phase15OneSshTransport -ExpectedHost $ExpectedHost -CollectorBytes $collectorBytes -ClaimId $claim.claim_id -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256
            $document = ConvertFrom-Phase15CanonicalJsonText -Text $rawDocument
            if ($null -eq $document) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            if (-not (Test-Phase15CollectorDocument -Document $document -ExpectedHost $ExpectedHost -ExpectedClaimId $claim.claim_id -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256)) { $failureReason = 'schema_invalid'; throw 'collector_schema_invalid' }
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            $evidence = ConvertTo-Phase15Evidence -Document $document -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt
            Publish-Phase15TerminalOutcome -LifecyclePath $lifecyclePath -ReservationPath $outcomeReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'completed' -EndedAt $endedAt -ReasonCode 'not_applicable' -Outcome $evidence
        } catch {
            $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
            if (Test-Phase15OutcomeOwnership -ReservationPath $outcomeReservationPath -ClaimId $claim.claim_id) {
                $failure = New-Phase15FailureOutcome -ReasonCode $failureReason -ManifestSha256 $manifestSha256 -CollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost -StartedAt $startedAt -EndedAt $endedAt -SshUsed $sshUsed
                Publish-Phase15TerminalOutcome -LifecyclePath $lifecyclePath -ReservationPath $outcomeReservationPath -OutcomePath $OutcomePath -ClaimId $claim.claim_id -Status 'failed' -EndedAt $endedAt -ReasonCode $failureReason -Outcome $failure
            }
            throw
        }
    } finally {
        Release-Phase15OutcomeSlot -ReservationPath $outcomeReservationPath -ClaimId $claim.claim_id
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
