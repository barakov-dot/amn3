[CmdletBinding()]
param(
    [string]$StagePackageRoot,
    [string]$StageApproval,
    [string]$StageExpectedCurrentStateSha256,
    [string]$StageTransactionId,
    [string]$StageOutcomePath,
    [string]$StageExpectedHost = '138.124.181.246'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'phase16_spain_readonly_preflight_ssh_runner.ps1')

$script:Phase16ControlledStagePackageId = 'phase16-awg3-family-3-1-spain-pilot-20260824-013'
$script:Phase16ControlledStageRequestSchema = 'amn2.phase16.controlled-stage-request.v1'
$script:Phase16ControlledStageMaximumArchiveBytes = 268435456
$script:Phase16ControlledStageTimeoutMilliseconds = 300000

function Get-Phase16ControlledStageRollbackScope {
    return [ordered]@{
        application_ledger = '/var/lib/amn2-phase16/stage/application.json'
        application_release = "/opt/amn2-spain/releases/$($script:Phase16ControlledStagePackageId)"
        backup_policy = 'preserve_checksum_bound_sqlite_backup'
        coordinator_ledger = '/var/lib/amn2-phase16/stage/coordinator.json'
        package_root = '/var/lib/amn2-phase16/package'
        runtime_ledger = '/var/lib/amn2-phase16/stage/awg31-runtime.json'
        runtime_resources = @(
            '/etc/systemd/system/amn2-spain-awg3.service',
            '/var/lib/amn2-spain/awg3',
            'container:amn2-spain-awg3',
            'network:amn2sp3'
        )
        schema = 'amn2.phase16.controlled-stage-rollback-scope.v1'
    }
}

function Test-Phase16ControlledStageSafeRelativePath {
    param([Parameter(Mandatory)][string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path.Contains('\') -or $Path.Contains([char]0) -or $Path.StartsWith('/') -or $Path.Contains(':')) { return $false }
    $parts = @($Path.Split('/'))
    return $parts.Count -gt 1 -and @($parts | Where-Object { $_ -in @('', '.', '..') }).Count -eq 0
}

function Read-Phase16ControlledStagePackage {
    param([Parameter(Mandatory)][string]$Root)
    $rootItem = Get-Item -LiteralPath $Root -Force -ErrorAction Stop
    if (-not $rootItem.PSIsContainer -or ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'package_root_invalid' }
    $rootFull = $rootItem.FullName.TrimEnd('\')
    $manifestArtifact = Read-Phase16ManifestArtifact -Path (Join-Path $rootFull 'manifest.json')
    $manifest = $manifestArtifact.Value
    if ($manifest.package_id -cne $script:Phase16ControlledStagePackageId -or $manifest.package_identity_sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'package_identity_invalid' }
    $files = [Collections.Generic.List[object]]::new()
    $expected = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    [void]$expected.Add('manifest.json')
    $files.Add([pscustomobject]@{ Bytes = [byte[]]$manifestArtifact.Bytes; Path = 'manifest.json' })
    foreach ($entry in @($manifest.entries | Sort-Object -Property path)) {
        if (-not (Test-Phase16ExactProperties -Value $entry -Required @('gate','mode','path','role','rollback_role','secret_classification','sha256','size')) -or
            -not (Test-Phase16ControlledStageSafeRelativePath -Path ([string]$entry.path)) -or
            $entry.sha256 -cnotmatch '^[0-9a-f]{64}$' -or $entry.size -isnot [int64] -and $entry.size -isnot [int32] -or
            [int64]$entry.size -lt 0 -or [int64]$entry.size -gt 67108864 -or -not $expected.Add([string]$entry.path)) { throw 'manifest_entry_invalid' }
        $local = Join-Path $rootFull ([string]$entry.path).Replace('/', '\')
        $full = [IO.Path]::GetFullPath($local)
        if (-not $full.StartsWith($rootFull + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'manifest_entry_invalid' }
        $item = Get-Item -LiteralPath $full -Force -ErrorAction Stop
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -ne [int64]$entry.size) { throw 'package_entry_invalid' }
        $bytes = if ($item.Length -eq 0) { [byte[]]::new(0) } else { Read-Phase16BoundedFileBytes -Path $full -MaximumBytes ([int][Math]::Max(1, $item.Length)) }
        if ((Get-Phase16BytesSha256 -Bytes $bytes) -cne [string]$entry.sha256) { throw 'package_checksum_invalid' }
        $files.Add([pscustomobject]@{ Bytes = [byte[]]$bytes; Path = [string]$entry.path })
    }
    foreach ($directory in @(Get-ChildItem -LiteralPath $rootFull -Directory -Recurse -Force)) {
        if (($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'package_reparse_invalid' }
    }
    $actualFiles = @(Get-ChildItem -LiteralPath $rootFull -File -Recurse -Force)
    if ($actualFiles.Count -ne $expected.Count) { throw 'package_inventory_invalid' }
    foreach ($item in $actualFiles) {
        $relative = $item.FullName.Substring($rootFull.Length + 1).Replace('\', '/')
        if (-not $expected.Contains($relative)) { throw 'package_inventory_invalid' }
    }
    $coordinator = $files | Where-Object { $_.Path -ceq 'tooling/scripts/vps/phase16_controlled_stage_coordinator.py' }
    if (@($coordinator).Count -ne 1) { throw 'coordinator_missing' }
    return [pscustomobject]@{
        CoordinatorBytes = [byte[]]$coordinator.Bytes
        Files = $files
        Manifest = $manifest
        ManifestSha256 = $manifestArtifact.Sha256
    }
}

function New-Phase16ControlledStageArchive {
    param([Parameter(Mandatory)][Collections.Generic.List[object]]$Files)
    Add-Type -AssemblyName System.IO.Compression
    $memory = [IO.MemoryStream]::new()
    $archive = [IO.Compression.ZipArchive]::new($memory, [IO.Compression.ZipArchiveMode]::Create, $true)
    try {
        foreach ($file in @($Files | Sort-Object -Property Path)) {
            $entry = $archive.CreateEntry([string]$file.Path, [IO.Compression.CompressionLevel]::Optimal)
            $stream = $entry.Open()
            try { $stream.Write([byte[]]$file.Bytes, 0, ([byte[]]$file.Bytes).Length) } finally { $stream.Dispose() }
        }
    } finally {
        $archive.Dispose()
    }
    try {
        if ($memory.Length -lt 1 -or $memory.Length -gt $script:Phase16ControlledStageMaximumArchiveBytes) { throw 'archive_size_invalid' }
        return [byte[]]$memory.ToArray()
    } finally {
        $memory.Dispose()
    }
}

function New-Phase16ControlledStageSshArguments {
    param(
        [Parameter(Mandatory)][string]$ExpectedHost,
        [Parameter(Mandatory)][string]$CoordinatorSha256
    )
    if (-not (Test-Phase16ExpectedHost -ExpectedHost $ExpectedHost) -or $CoordinatorSha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'transport_envelope_invalid' }
    $contract = Get-Phase16SpainTrustContract
    $bootstrap = 'import hashlib,sys;s=sys.stdin.buffer;n=int(s.read(8),16);c=s.read(n);h=sys.argv[1];len(c)==n and hashlib.sha256(c).hexdigest()==h or sys.exit(65);exec(compile(c,"phase16_controlled_stage_coordinator.py","exec"),{"__name__":"__main__","PHASE16_EMBEDDED_SOURCE_SHA256":h})'
    $remote = '/usr/bin/python3 -I -B -c ''{0}'' ''{1}''' -f $bootstrap,$CoordinatorSha256
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

function Write-Phase16ControlledStageOutcome {
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][byte[]]$Bytes)
    $full = [IO.Path]::GetFullPath($Path)
    $parent = Split-Path -Parent $full
    if (-not (Test-Path -LiteralPath $parent -PathType Container) -or (Test-Path -LiteralPath $full)) { throw 'outcome_path_invalid' }
    $stream = [IO.FileStream]::new($full, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($Bytes, 0, $Bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}

function Invoke-Phase16ControlledStageRunnerMain {
    if ([string]::IsNullOrWhiteSpace($StagePackageRoot) -or [string]::IsNullOrWhiteSpace($StageApproval) -or
        $StageExpectedCurrentStateSha256 -cnotmatch '^[0-9a-f]{64}$' -or $StageTransactionId -cnotmatch '^[a-z0-9][a-z0-9._-]{0,79}$' -or
        [string]::IsNullOrWhiteSpace($StageOutcomePath) -or -not (Test-Phase16ExpectedHost -ExpectedHost $StageExpectedHost)) { throw 'stage_arguments_invalid' }
    Assert-Phase16SpainTrustBundle -ExpectedHost $StageExpectedHost
    $package = Read-Phase16ControlledStagePackage -Root $StagePackageRoot
    $rollbackSha256 = Get-Phase16CanonicalJsonSha256 -Value (Get-Phase16ControlledStageRollbackScope)
    $expectedApproval = "/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_$($script:Phase16ControlledStagePackageId) IDENTITY_$($package.Manifest.package_identity_sha256) MANIFEST_SHA256_$($package.ManifestSha256) STATE_$StageExpectedCurrentStateSha256 ROLLBACK_SCOPE_SHA256_$rollbackSha256 TRANSACTION_$StageTransactionId MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED"
    if ($StageApproval -cne $expectedApproval) { throw 'stage_approval_invalid' }
    $approvalBytes = [Text.Encoding]::ASCII.GetBytes($StageApproval)
    $request = [ordered]@{
        approval_sha256 = Get-Phase16BytesSha256 -Bytes $approvalBytes
        expected_current_state_sha256 = $StageExpectedCurrentStateSha256
        manifest_sha256 = $package.ManifestSha256
        package_id = $script:Phase16ControlledStagePackageId
        package_identity_sha256 = [string]$package.Manifest.package_identity_sha256
        rollback_scope_sha256 = $rollbackSha256
        schema = $script:Phase16ControlledStageRequestSchema
        transaction_id = $StageTransactionId
    }
    $archive = New-Phase16ControlledStageArchive -Files $package.Files
    $coordinatorSha256 = Get-Phase16BytesSha256 -Bytes $package.CoordinatorBytes
    $header = [ordered]@{
        approval = $StageApproval
        archive_sha256 = Get-Phase16BytesSha256 -Bytes $archive
        archive_size = [int64]$archive.Length
        coordinator_sha256 = $coordinatorSha256
        request = $request
    }
    $headerBytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Phase16CanonicalJsonText -Value $header) + "`n")
    $prefix = [Text.Encoding]::ASCII.GetBytes(('{0:x8}' -f $headerBytes.Length))
    $coordinatorPrefix = [Text.Encoding]::ASCII.GetBytes(('{0:x8}' -f $package.CoordinatorBytes.Length))
    $arguments = New-Phase16ControlledStageSshArguments -ExpectedHost $StageExpectedHost -CoordinatorSha256 $coordinatorSha256
    $start = New-Phase16SshProcessStartInfo -Arguments $arguments
    $start.RedirectStandardInput = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    try {
        if (-not $process.Start()) { throw 'transport_failed' }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        $stream = $process.StandardInput.BaseStream
        $stream.Write($coordinatorPrefix, 0, $coordinatorPrefix.Length)
        $stream.Write($package.CoordinatorBytes, 0, $package.CoordinatorBytes.Length)
        $stream.Write($prefix, 0, $prefix.Length)
        $stream.Write($headerBytes, 0, $headerBytes.Length)
        $stream.Write($archive, 0, $archive.Length)
        $stream.Flush()
        $process.StandardInput.Close()
        if (-not $process.WaitForExit($script:Phase16ControlledStageTimeoutMilliseconds)) { try { $process.Kill() } catch {}; throw 'transport_timeout' }
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        if (-not [string]::IsNullOrEmpty($stderr) -or [Text.Encoding]::UTF8.GetByteCount($stdout) -gt 8192) { throw 'transport_output_invalid' }
        $document = ConvertFrom-Phase16CanonicalJsonText -Text $stdout
        if ($null -eq $document -or $document.schema -cne 'amn2.phase16.controlled-stage-outcome.v1' -or $document.package_id -cne $script:Phase16ControlledStagePackageId -or
            $document.general_issuance_enabled -isnot [bool] -or $document.general_issuance_enabled -ne $false) { throw 'stage_outcome_invalid' }
        $outcomeBytes = [Text.UTF8Encoding]::new($false).GetBytes($stdout)
        Write-Phase16ControlledStageOutcome -Path $StageOutcomePath -Bytes $outcomeBytes
        if ($process.ExitCode -ne 0 -or $document.result -cne 'application_and_awg31_staged') { throw 'stage_failed' }
        [Console]::Out.Write($stdout)
    } finally {
        if (-not $process.HasExited) { try { $process.Kill() } catch {} }
        $process.Dispose()
        [Array]::Clear($archive, 0, $archive.Length)
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-Phase16ControlledStageRunnerMain
        exit 0
    } catch {
        [Console]::Error.WriteLine('AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP')
        exit 64
    }
}
