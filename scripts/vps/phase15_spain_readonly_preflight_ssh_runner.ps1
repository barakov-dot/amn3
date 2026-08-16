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

function Get-Phase15FileSha256 {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function ConvertFrom-Phase15JsonFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        $bytes = [IO.File]::ReadAllBytes($Path)
        $strictUtf8 = [Text.UTF8Encoding]::new($false, $true)
        $text = $strictUtf8.GetString($bytes)
        return $text | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Test-Phase15FutureClaim {
    param(
        [Parameter(Mandatory)][string]$ClaimPath,
        [Parameter(Mandatory)][string]$ExpectedPackageId,
        [Parameter(Mandatory)][string]$ExpectedManifestSha256,
        [Parameter(Mandatory)][string]$ExpectedCollectorSha256,
        [Parameter(Mandatory)][string]$ExpectedHost
    )
    if ($ExpectedPackageId -cne $script:Phase15PackageId) { return $false }
    if ($ExpectedManifestSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
    if ($ExpectedCollectorSha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
    if ([string]::IsNullOrWhiteSpace($ExpectedHost)) { return $false }
    if (Test-Path -LiteralPath ($ClaimPath + '.consumed') -PathType Leaf) { return $false }
    $claim = ConvertFrom-Phase15JsonFile -Path $ClaimPath
    if ($null -eq $claim) { return $false }
    $names = @($claim.PSObject.Properties.Name | Sort-Object)
    $required = @('claim_id','collector_sha256','consumed_at','expected_host','expires_at','future_gate','issued_at','manifest_sha256','package_id','schema','status')
    if (($names -join '|') -cne ($required -join '|')) { return $false }
    if ($claim.schema -cne $script:Phase15ClaimSchema) { return $false }
    if ($claim.package_id -cne $ExpectedPackageId -or $claim.manifest_sha256 -cne $ExpectedManifestSha256) { return $false }
    if ($claim.collector_sha256 -cne $ExpectedCollectorSha256 -or $claim.expected_host -cne $ExpectedHost) { return $false }
    if ($claim.future_gate -cne 'PREFLIGHT' -or $claim.status -cne 'issued' -or $null -ne $claim.consumed_at) { return $false }
    try {
        $issued = [DateTimeOffset]::ParseExact($claim.issued_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture)
        $expires = [DateTimeOffset]::ParseExact($claim.expires_at, 'yyyy-MM-ddTHH:mm:ssZ', [Globalization.CultureInfo]::InvariantCulture)
    } catch { return $false }
    if ($issued -ge $expires -or [DateTimeOffset]::UtcNow -ge $expires) { return $false }
    return $true
}

function Test-Phase15CollectorDocument {
    param(
        [Parameter(Mandatory)][object]$Document,
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$ExpectedClaimId
    )
    $names = @($Document.PSObject.Properties.Name | Sort-Object)
    $required = @('blocking_reasons','claim_id','decision','host_identity','observed_at','observations','package_id','safety','schema')
    if (($names -join '|') -cne ($required -join '|')) { return $false }
    if ($Document.schema -cne $script:Phase15CollectorSchema -or $Document.package_id -cne $script:Phase15PackageId) { return $false }
    if ($Document.host_identity -cne $ExpectedHost -or $Document.claim_id -cne $ExpectedClaimId) { return $false }
    if ($Document.decision -notin @('pass','stop')) { return $false }
    if ($Document.safety.live_mutation -ne $false -or $Document.safety.remote_file_written -ne $false -or $Document.safety.raw_output_persisted -ne $false) { return $false }
    foreach ($item in @($Document.observations)) {
        if ($item.observation_sha256 -cnotmatch '^[0-9a-f]{64}$') { return $false }
        if ($item.state -notin @('absent','free','pass','present','stop','unknown')) { return $false }
    }
    return $true
}

function Invoke-Phase15OneSshTransport {
    param(
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][byte[]]$CollectorBytes,
        [Parameter(Mandatory)][string]$ClaimId
    )
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'C:\Windows\System32\OpenSSH\ssh.exe'
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    foreach ($argument in @('-T','-F','none','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',$ExpectedHost,'bash -s')) {
        [void]$start.ArgumentList.Add($argument)
    }
    $start.Environment['AMN2_PHASE15_CLAIM_ID'] = $ClaimId
    $start.Environment['AMN2_PHASE15_EXPECTED_HOST'] = $ExpectedHost
    $start.Environment['AMN2_PHASE15_PACKAGE_ID'] = $script:Phase15PackageId
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    if (-not $process.Start()) { throw 'transport_failed' }
    try {
        $process.StandardInput.BaseStream.Write($CollectorBytes, 0, $CollectorBytes.Length)
        $process.StandardInput.Close()
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(30000)) {
            $process.Kill()
            throw 'transport_failed'
        }
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        [void]$stderrTask.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0 -or [Text.Encoding]::UTF8.GetByteCount($stdout) -ge 65536) { throw 'transport_failed' }
        return $stdout
    } finally {
        $process.Dispose()
    }
}

function Write-Phase15CreateNewJson {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][object]$Value)
    $json = $Value | ConvertTo-Json -Depth 12 -Compress
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + "`n")
    $stream = [IO.FileStream]::new($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Invoke-Phase15RunnerMain {
    if (-not $FutureAuthorization -or [string]::IsNullOrWhiteSpace($FutureClaimPath)) { throw 'future_claim_required' }
    if ([string]::IsNullOrWhiteSpace($PackageRoot) -or [string]::IsNullOrWhiteSpace($ExpectedHost) -or [string]::IsNullOrWhiteSpace($OutcomePath)) { throw 'runner_arguments_invalid' }
    $manifestPath = Join-Path $PackageRoot 'manifest.json'
    $collectorPath = Join-Path $PackageRoot 'tooling\scripts\vps\phase15_spain_readonly_preflight_remote.sh'
    $manifest = ConvertFrom-Phase15JsonFile -Path $manifestPath
    if ($null -eq $manifest -or $manifest.package_id -cne $script:Phase15PackageId) { throw 'package_identity_invalid' }
    $manifestSha256 = Get-Phase15FileSha256 -Path $manifestPath
    $collectorSha256 = Get-Phase15FileSha256 -Path $collectorPath
    $entry = @($manifest.entries | Where-Object { $_.path -ceq 'tooling/scripts/vps/phase15_spain_readonly_preflight_remote.sh' })
    if ($entry.Count -ne 1 -or $entry[0].sha256 -cne $collectorSha256) { throw 'collector_checksum_invalid' }
    if (-not (Test-Phase15FutureClaim -ClaimPath $FutureClaimPath -ExpectedPackageId $script:Phase15PackageId -ExpectedManifestSha256 $manifestSha256 -ExpectedCollectorSha256 $collectorSha256 -ExpectedHost $ExpectedHost)) { throw 'claim_invalid' }
    $claim = ConvertFrom-Phase15JsonFile -Path $FutureClaimPath
    $startedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $collectorBytes = [IO.File]::ReadAllBytes($collectorPath)
    $rawDocument = Invoke-Phase15OneSshTransport -ExpectedHost $ExpectedHost -CollectorBytes $collectorBytes -ClaimId $claim.claim_id
    try { $document = $rawDocument | ConvertFrom-Json } catch { throw 'collector_schema_invalid' }
    if (-not (Test-Phase15CollectorDocument -Document $document -ExpectedHost $ExpectedHost -ExpectedClaimId $claim.claim_id)) { throw 'collector_schema_invalid' }
    $endedAt = [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
    $evidence = [ordered]@{
        collector_sha256 = $collectorSha256
        decision = $document.decision
        ended_at = $endedAt
        expected_host = $ExpectedHost
        manifest_sha256 = $manifestSha256
        observations = @($document.observations)
        package_id = $script:Phase15PackageId
        safety = [ordered]@{ live_mutation = $false; raw_output_persisted = $false; remote_file_written = $false; ssh_used = $true }
        schema = $script:Phase15EvidenceSchema
        started_at = $startedAt
        stop_reasons = @($document.blocking_reasons)
        transport_disposition = 'read_only_completed'
    }
    Write-Phase15CreateNewJson -Path $OutcomePath -Value $evidence
    Write-Phase15CreateNewJson -Path ($FutureClaimPath + '.consumed') -Value ([ordered]@{ claim_id = $claim.claim_id; consumed_at = $endedAt; status = 'consumed' })
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
