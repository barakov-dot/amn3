Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:ExpectedSshProcessCount = 3
$script:ProductionMaximumInputBytes = 2097152
$script:ProductionMaximumOutputBytes = 1048576
$script:ProductionTimeoutMilliseconds = 60000
$script:ProductionRootBaseHead = "1b55f7c83c3453829e24af5dd11facedb2188447"
$script:ProductionAmn2Head = "910539eaa8051cb1b59131d38b9fa27b9392744d"

$AuditRunnerPath = Join-Path $PSScriptRoot "audit-ssh-runner.ps1"
if (-not [IO.File]::Exists($AuditRunnerPath)) {
    $AuditRunnerPath = Join-Path $PSScriptRoot "phase13_bot_web_migration_ssh_runner.ps1"
}
if (-not [IO.File]::Exists($AuditRunnerPath)) {
    throw "bound audit runner unavailable"
}
. $AuditRunnerPath
$script:MaximumInputBytes = $script:ProductionMaximumInputBytes

function Get-Phase13ProductionStageFileContract {
    return @(
        "amn2-spain-bot.service",
        "audit-ssh-runner.ps1",
        "failure-evidence.schema.json",
        "manifest.json",
        "manifest.schema.json",
        "merge-preview.json",
        "merged-target.sqlite3.enc",
        "migration-plan.json",
        "production-stage-package.py",
        "production-stage-remote.py",
        "production-stage-runner.ps1",
        "readonly-collector.py",
        "recovery_crypto.py",
        "rollback-plan.json",
        "runtime.env.delta.enc",
        "source-audit.json",
        "source-full-backup.enc",
        "source-input-manifest.json",
        "source-merge-claim.json",
        "source-merge-receipt.json",
        "target-audit.json",
        "target-before-backup.enc"
    )
}

function Get-Phase13ProductionStageDirectArtifactContract {
    return [ordered]@{
        merge_preview = "merge-preview.json"
        merged_target_db = "merged-target.sqlite3.enc"
        rollback_plan = "rollback-plan.json"
        source_full_backup = "source-full-backup.enc"
        target_before_backup = "target-before-backup.enc"
    }
}

function Get-Phase13ProductionStageIndirectArtifactContract {
    return @(
        "amn2-spain-bot.service",
        "audit-ssh-runner.ps1",
        "failure-evidence.schema.json",
        "manifest.schema.json",
        "migration-plan.json",
        "production-stage-package.py",
        "production-stage-remote.py",
        "production-stage-runner.ps1",
        "readonly-collector.py",
        "recovery_crypto.py",
        "runtime.env.delta.enc",
        "source-audit.json",
        "source-input-manifest.json",
        "source-merge-claim.json",
        "source-merge-receipt.json",
        "target-audit.json"
    )
}

function Assert-Phase13ProductionStageRegularFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int64]$MaximumBytes = 67108864
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or
        ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $Item.Length -lt 1 -or $Item.Length -gt $MaximumBytes) {
        throw "package artifact unsafe"
    }
    return $Item
}

function Get-Phase13ProductionStageExactApprovalPhrase {
    param([Parameter(Mandatory = $true)]$Binding)
    $Prefix = [Text.Encoding]::UTF8.GetString(
        [Convert]::FromBase64String(
            "0KPQotCS0JXQoNCW0JTQkNCuINCe0JTQmNCdIENIRUNLU1VNLUJPVU5EIExJVkUgU1BBSU4gRElTQUJMRUQtU1RBR0Ug0JggV0VCL0RBVEEtQVBQTFk="
        )
    )
    return @(
        "$Prefix OUTCOME_$($Binding.OutcomeId)",
        "MANIFEST_SHA_$($Binding.ManifestSha256)",
        "RUNNER_SHA_$($Binding.RunnerSha256)",
        "REMOTE_SHA_$($Binding.RemoteSha256)",
        "COLLECTOR_SHA_$($Binding.CollectorSha256)",
        "TOOLING_HEAD_$($Binding.ToolingHead)",
        "EXPIRES_AT_$($Binding.ExpiresAt)",
        "MAX_ATTEMPTS_1",
        "THREE_SSH_NO_BOT_START_NO_USA_MUTATION_NO_AWG_MUTATION_NO_FOREIGN_MUTATION"
    ) -join " "
}

function Test-Phase13ProductionStagePackage {
    param(
        [Parameter(Mandatory = $true)][string]$PackageRoot,
        [Parameter(Mandatory = $true)][string]$ExactApprovalPhrase,
        [DateTimeOffset]$NowUtc = [DateTimeOffset]::UtcNow
    )
    if (-not [IO.Path]::IsPathRooted($PackageRoot)) {
        throw "package root invalid"
    }
    $RootItem = Get-Item -LiteralPath $PackageRoot -Force -ErrorAction Stop
    if (-not $RootItem.PSIsContainer -or
        ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "package root unsafe"
    }
    $Root = $RootItem.FullName
    $ExpectedFiles = @(Get-Phase13ProductionStageFileContract | Sort-Object)
    $ObservedItems = @(Get-ChildItem -LiteralPath $Root -Force)
    $ObservedFiles = @($ObservedItems | ForEach-Object { $_.Name } | Sort-Object)
    if ($ObservedItems.Count -ne $ExpectedFiles.Count -or
        @(Compare-Object -ReferenceObject $ExpectedFiles -DifferenceObject $ObservedFiles -CaseSensitive).Count -ne 0) {
        throw "package file set invalid"
    }
    foreach ($Name in $ExpectedFiles) {
        $null = Assert-Phase13ProductionStageRegularFile -Path (Join-Path $Root $Name)
    }

    $ManifestDocument = Read-Phase13AuditStrictJson -Path (Join-Path $Root "manifest.json")
    $Manifest = $ManifestDocument.Value
    Test-Phase13ExactPropertySet -Value $Manifest -Expected @(
        "artifacts", "created_at", "expires_at", "live_mutation_authorized",
        "outcome_id", "schema", "source_audit_sha256", "source_role",
        "target_audit_sha256", "target_role"
    ) -Message "manifest contract invalid"
    if ($Manifest.schema -cne "amn2.phase13.bot-web-migration-manifest.v1" -or
        $Manifest.outcome_id -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$' -or
        $Manifest.source_role -cne "usa-source" -or
        $Manifest.target_role -cne "spain-target" -or
        $Manifest.live_mutation_authorized -ne $false -or
        [string]$Manifest.source_audit_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        [string]$Manifest.target_audit_sha256 -cnotmatch '^[0-9a-f]{64}$') {
        throw "manifest contract invalid"
    }
    $ExpiresAt = if ($Manifest.expires_at -is [DateTime]) {
        [DateTimeOffset]$Manifest.expires_at
    } else {
        [DateTimeOffset]::Parse(
            [string]$Manifest.expires_at,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::AssumeUniversal
        )
    }
    $ExpiresAt = $ExpiresAt.ToUniversalTime()
    if ($NowUtc.ToUniversalTime() -ge $ExpiresAt) {
        throw "production stage manifest expired"
    }
    $ManifestSha256 = Get-Phase13Sha256Hex -Bytes $ManifestDocument.Bytes
    $Direct = Get-Phase13ProductionStageDirectArtifactContract
    Test-Phase13ExactPropertySet -Value $Manifest.artifacts -Expected @($Direct.Keys) -Message "direct artifact set invalid"
    foreach ($Key in $Direct.Keys) {
        $Name = [string]$Direct[$Key]
        $Value = $Manifest.artifacts.$Key
        Test-Phase13ExactPropertySet -Value $Value -Expected @("path", "sha256", "size") -Message "direct artifact binding invalid"
        $Path = Join-Path $Root $Name
        $Item = Assert-Phase13ProductionStageRegularFile -Path $Path
        if ($Value.path -cne $Name -or
            [int64]$Value.size -ne $Item.Length -or
            [string]$Value.sha256 -cne (Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes($Path)))) {
            throw "direct artifact binding invalid"
        }
    }

    $RollbackDocument = Read-Phase13AuditStrictJson -Path (Join-Path $Root "rollback-plan.json")
    $Rollback = $RollbackDocument.Value
    Test-Phase13ExactPropertySet -Value $Rollback -Expected @(
        "artifact_bindings", "expected", "heads", "max_attempts", "process_contract",
        "safety", "schema", "source", "trust_bundles"
    ) -Message "rollback plan invalid"
    if ($Rollback.schema -cne "amn2.phase13.bot-web-production-stage-plan.v1" -or
        $Rollback.max_attempts -ne 1) {
        throw "rollback plan invalid"
    }
    $Indirect = @(Get-Phase13ProductionStageIndirectArtifactContract)
    Test-Phase13ExactPropertySet -Value $Rollback.artifact_bindings -Expected $Indirect -Message "indirect artifact set invalid"
    foreach ($Name in $Indirect) {
        $Value = $Rollback.artifact_bindings.$Name
        Test-Phase13ExactPropertySet -Value $Value -Expected @("sha256", "size") -Message "indirect artifact binding invalid"
        $Path = Join-Path $Root $Name
        $Item = Assert-Phase13ProductionStageRegularFile -Path $Path
        if ([int64]$Value.size -ne $Item.Length -or
            [string]$Value.sha256 -cne (Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes($Path)))) {
            throw "indirect artifact binding invalid"
        }
    }
    Test-Phase13ExactPropertySet -Value $Rollback.heads -Expected @("amn2", "root_base", "tooling") -Message "head binding invalid"
    if ($Rollback.heads.root_base -cne $script:ProductionRootBaseHead -or
        $Rollback.heads.amn2 -cne $script:ProductionAmn2Head -or
        [string]$Rollback.heads.tooling -cnotmatch '^[0-9a-f]{40}$') {
        throw "head binding invalid"
    }
    Test-Phase13ExactPropertySet -Value $Rollback.process_contract -Expected @(
        "expected_ssh_processes", "remote_temp_package", "retries", "roles", (-join ([char[]](115,99,112)))
    ) -Message "process contract invalid"
    $CopyKey = -join ([char[]](115,99,112))
    if ($Rollback.process_contract.expected_ssh_processes -ne $script:ExpectedSshProcessCount -or
        $Rollback.process_contract.remote_temp_package -ne $false -or
        $Rollback.process_contract.retries -ne 0 -or
        $Rollback.process_contract.$CopyKey -ne $false -or
        (@($Rollback.process_contract.roles) -join '|') -cne 'usa-readonly|spain-readonly|spain-stage-apply') {
        throw "process contract invalid"
    }
    Test-Phase13ExactPropertySet -Value $Rollback.safety -Expected @(
        "awg_mutation_allowed", "bot_cutover_allowed", "foreign_service_mutation_allowed",
        "live_mutation_authorized", "spain_bot_start_allowed", "usa_mutation_allowed"
    ) -Message "safety contract invalid"
    foreach ($Property in $Rollback.safety.PSObject.Properties) {
        if ($Property.Value -ne $false) { throw "safety contract invalid" }
    }
    Test-Phase13ExactPropertySet -Value $Rollback.expected -Expected @(
        "awg2_foundation_sha256", "foreign_receipt_sha256", "foreign_stable_sha256",
        "merged_database_sha256", "spain_invariants_sha256",
        "target_before_database_sha256", "target_runtime_env_sha256"
    ) -Message "expected projection invalid"
    foreach ($Property in $Rollback.expected.PSObject.Properties) {
        if ([string]$Property.Value -cnotmatch '^[0-9a-f]{64}$') { throw "expected projection invalid" }
    }
    if ($Rollback.expected.awg2_foundation_sha256 -cne "0e5a5926821d88ae4a2515f9e95cd7c3f69db52100c1a1ec74e99fb794222281" -or
        $Rollback.expected.foreign_receipt_sha256 -cne "bc9065b3fa7cab40f5eefebbfd8093f2d62477e972777fe665e8d9f6028aa704" -or
        $Rollback.expected.foreign_stable_sha256 -cne "f5767f361a9441dd4b5361c07da164a3059e0d1347d5217594534797d367b7e8") {
        throw "accepted foundation binding invalid"
    }
    Test-Phase13ExactPropertySet -Value $Rollback.trust_bundles -Expected @("spain", "usa") -Message "trust contract invalid"
    foreach ($Role in @("spain", "usa")) {
        Test-Phase13ExactPropertySet -Value $Rollback.trust_bundles.$Role -Expected @("binding_id", "overridable") -Message "trust contract invalid"
        if ($Rollback.trust_bundles.$Role.overridable -ne $false) { throw "trust contract invalid" }
    }

    foreach ($SchemaContract in @(
        @("manifest.schema.json", "amn2.phase13.bot-web-migration-manifest.v1"),
        @("failure-evidence.schema.json", "amn2.phase13.bot-web-migration-failure.v1")
    )) {
        try {
            $Schema = [IO.File]::ReadAllText((Join-Path $Root $SchemaContract[0])) | ConvertFrom-Json -ErrorAction Stop
        } catch { throw "existing schema contract invalid" }
        if ($Schema.'$id' -cne $SchemaContract[1] -or $Schema.type -cne "object" -or $Schema.additionalProperties -ne $false) {
            throw "existing schema contract invalid"
        }
    }

    $Binding = [pscustomobject]@{
        CollectorBytes = [IO.File]::ReadAllBytes((Join-Path $Root "readonly-collector.py"))
        CollectorSha256 = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes((Join-Path $Root "readonly-collector.py")))
        ExpiresAt = $ExpiresAt.ToString("yyyy-MM-ddTHH:mm:ssZ", [Globalization.CultureInfo]::InvariantCulture)
        Expected = $Rollback.expected
        ManifestSha256 = $ManifestSha256
        OutcomeId = [string]$Manifest.outcome_id
        PackageRoot = $Root
        PackageBuilderSha256 = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes((Join-Path $Root "production-stage-package.py")))
        RemoteBytes = [IO.File]::ReadAllBytes((Join-Path $Root "production-stage-remote.py"))
        RemoteSha256 = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes((Join-Path $Root "production-stage-remote.py")))
        RunnerSha256 = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes((Join-Path $Root "production-stage-runner.ps1")))
        ToolingHead = [string]$Rollback.heads.tooling
    }
    if ($ExactApprovalPhrase -cne (Get-Phase13ProductionStageExactApprovalPhrase -Binding $Binding)) {
        throw "exact approval mismatch"
    }
    return $Binding
}

function New-Phase13ProductionStageOutcomeClaim {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][DateTimeOffset]$NowUtc
    )
    $RootItem = Get-Item -LiteralPath $OutcomeRoot -Force -ErrorAction Stop
    if (-not $RootItem.PSIsContainer -or
        ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "private outcome root unsafe"
    }
    if ($NowUtc.ToUniversalTime() -ge [DateTimeOffset]::Parse($Binding.ExpiresAt).ToUniversalTime()) {
        throw "production stage manifest expired"
    }
    $Path = Join-Path $RootItem.FullName ("{0}.claim.json" -f $Binding.OutcomeId)
    if ([IO.File]::Exists($Path)) { throw "outcome claim replay" }
    $Claim = [ordered]@{
        collector_sha256 = [string]$Binding.CollectorSha256
        expires_at = [string]$Binding.ExpiresAt
        manifest_sha256 = [string]$Binding.ManifestSha256
        max_attempts = 1
        outcome_id = [string]$Binding.OutcomeId
        remote_sha256 = [string]$Binding.RemoteSha256
        runner_sha256 = [string]$Binding.RunnerSha256
        schema = "amn2.phase13.bot-web-production-stage-claim.v1"
    }
    try {
        Write-Phase13AuditCreateNewJson -Path $Path -Value $Claim
    } catch {
        if ([IO.File]::Exists($Path)) { throw "outcome claim replay" }
        throw "outcome claim write failed"
    }
    return $Path
}

function Write-Phase13ProductionStageFailure {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][DateTimeOffset]$NowUtc,
        [Parameter(Mandatory = $true)][ValidateSet("audit", "stage", "rollback")][string]$Stage,
        [Parameter(Mandatory = $true)][ValidateSet("audit_incomplete", "checksum_mismatch", "schema_validation_failed", "rollback_required")][string]$ReasonCode,
        [Parameter(Mandatory = $true)][bool]$MutationAttempted
    )
    $Path = Join-Path $OutcomeRoot ("{0}.failure.json" -f $Binding.OutcomeId)
    $Failure = [ordered]@{
        checked_at = $NowUtc.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        decision = "stop"
        outcome_id = [string]$Binding.OutcomeId
        reason_code = $ReasonCode
        safety_receipt = [ordered]@{
            mutation_attempted = $MutationAttempted
            raw_output_persisted = $false
            secret_bearing_data_persisted = $false
        }
        schema = "amn2.phase13.bot-web-migration-failure.v1"
        stage = $Stage
    }
    Write-Phase13AuditCreateNewJson -Path $Path -Value $Failure
    return $Path
}

function Invoke-Phase13ProductionStageAuditTransport {
    param(
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][string]$SshExecutable,
        [string[]]$SshPrefixArguments = @(),
        [Parameter(Mandatory = $true)]$RoleBindings
    )
    $Key = New-Phase13EphemeralHmacKey
    $EnvelopeBytes = $null
    try {
        $EnvelopeBytes = New-Phase13AuditTransportEnvelope `
            -CollectorBytes $Binding.CollectorBytes `
            -CollectorSha256 $Binding.CollectorSha256 `
            -EphemeralHmacKey $Key
        $Documents = @{}
        $Failed = $false
        $FailureRole = "not_applicable"
        $FailureSubreason = "not_applicable"
        foreach ($Role in @("usa", "spain")) {
            $Arguments = @($SshPrefixArguments) + @(
                New-Phase13AuditSshArguments -Role $Role -RoleBinding $RoleBindings[$Role]
            )
            $Transport = Invoke-Phase13BoundedProcess `
                -Executable $SshExecutable `
                -Arguments $Arguments `
                -InputBytes $EnvelopeBytes `
                -TimeoutMilliseconds $script:ProductionTimeoutMilliseconds `
                -MaximumOutputBytes $script:ProductionMaximumOutputBytes
            if ($Transport.Reason -cne "success") {
                $Failed = $true
                if ($FailureRole -ceq "not_applicable") {
                    $FailureRole = $Role
                    $FailureSubreason = switch ([string]$Transport.Reason) {
                        "timeout" { "timeout" }
                        "output_oversized" { "output_oversized" }
                        default { "ssh_process_failed" }
                    }
                }
                continue
            }
            try {
                $Documents[$Role] = $Transport.Document | ConvertFrom-Json -ErrorAction Stop
            } catch {
                $Failed = $true
                if ($FailureRole -ceq "not_applicable") {
                    $FailureRole = $Role
                    $FailureSubreason = "frame_invalid"
                }
            }
        }
        if ($Failed -or $Documents.Count -ne 2) {
            return [pscustomobject]@{
                AuditBytes = $null
                FailureRole = $FailureRole
                FailureSubreason = $FailureSubreason
                ProcessCount = 2
                Success = $false
            }
        }
        try {
            $PairText = ConvertTo-Phase13SanitizedAuditPair `
                -UsaDocument $Documents["usa"] `
                -SpainDocument $Documents["spain"]
            $PairBytes = (New-Object Text.UTF8Encoding($false)).GetBytes($PairText + "`n")
        } catch {
            return [pscustomobject]@{
                AuditBytes = $null
                FailureRole = "not_applicable"
                FailureSubreason = "audit_pair_invalid"
                ProcessCount = 2
                Success = $false
            }
        }
        return [pscustomobject]@{
            AuditBytes = $PairBytes
            FailureRole = "not_applicable"
            FailureSubreason = "not_applicable"
            ProcessCount = 2
            Success = $true
        }
    } finally {
        if ($null -ne $EnvelopeBytes) { [Array]::Clear($EnvelopeBytes, 0, $EnvelopeBytes.Length) }
        [Array]::Clear($Key, 0, $Key.Length)
    }
}

function New-Phase13ProductionStageSshArguments {
    param([Parameter(Mandatory = $true)]$RoleBinding)
    if ([string]$RoleBinding.TargetHost -cnotmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or
        [string]$RoleBinding.TargetUser -cnotmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "fixed Spain binding invalid"
    }
    $Bootstrap = 'import base64,hashlib,json,sys;e=json.load(sys.stdin);s=base64.b64decode(e["remote_b64"],validate=True);hashlib.sha256(s).hexdigest()==e["remote_sha256"] or sys.exit(70);p=(json.dumps(e["payload"],ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode();n={"__name__":"phase13_bound_remote"};exec(compile(s,"<bound-remote>","exec"),n);sys.exit(n["main_bound_payload"](base64.b64encode(p).decode("ascii")))'
    $RemoteCommand = "python3 -c '$Bootstrap'"
    return @(
        "-T", "-F", "none",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "UserKnownHostsFile=$($RoleBinding.KnownHostsPath)",
        "-o", "ConnectTimeout=10",
        "-o", "ConnectionAttempts=1",
        "-o", "ServerAliveInterval=5",
        "-o", "ServerAliveCountMax=1",
        "-i", [string]$RoleBinding.KeyPath,
        "-p", "22",
        "$($RoleBinding.TargetUser)@$($RoleBinding.TargetHost)",
        $RemoteCommand
    )
}

function New-Phase13ProductionStageTransportEnvelope {
    param(
        [Parameter(Mandatory = $true)][byte[]]$PayloadBytes,
        [Parameter(Mandatory = $true)][byte[]]$RemoteBytes,
        [Parameter(Mandatory = $true)][string]$RemoteSha256
    )
    try {
        $Decoder = New-Object Text.UTF8Encoding($false, $true)
        $Payload = $Decoder.GetString($PayloadBytes) | ConvertFrom-Json -ErrorAction Stop
    } catch { throw "prepared payload invalid" }
    $Envelope = [ordered]@{
        payload = $Payload
        remote_b64 = [Convert]::ToBase64String($RemoteBytes)
        remote_sha256 = $RemoteSha256
        schema = "amn2.phase13.bot-web-production-stage-transport.v1"
    }
    $Bytes = ConvertTo-Phase13AuditCanonicalJsonBytes -Value $Envelope
    if ($Bytes.Length -gt $script:ProductionMaximumInputBytes) {
        [Array]::Clear($Bytes, 0, $Bytes.Length)
        throw "production stage input oversized"
    }
    return $Bytes
}

function Test-Phase13ProductionStageRemoteReceipt {
    param(
        [Parameter(Mandatory = $true)]$Receipt,
        [Parameter(Mandatory = $true)]$Binding
    )
    Test-Phase13ExactPropertySet -Value $Receipt -Expected @(
        "awg2_equal", "bot_active", "database_equal", "foreign_equal", "marker_present", "outcome",
        "outcome_id", "raw_output_persisted", "reason", "rolled_back", "schema",
        "stage", "web_active"
    ) -Message "remote receipt invalid"
    if ($Receipt.schema -cne "amn2.phase13.bot-web-production-stage-receipt.v1" -or
        $Receipt.outcome_id -cne $Binding.OutcomeId -or
        $Receipt.outcome -cnotin @("passed", "failed") -or
        $Receipt.stage -cnotin @(
            "package_verify", "preflight", "stage", "web_stop", "atomic_db_apply",
            "web_start", "post_apply_verify", "rollback"
        ) -or
        $Receipt.raw_output_persisted -ne $false -or
        $Receipt.bot_active -ne $false -or
        $Receipt.marker_present -ne $false) {
        throw "remote receipt invalid"
    }
    foreach ($Value in @(
        $Receipt.awg2_equal, $Receipt.bot_active, $Receipt.foreign_equal,
        $Receipt.database_equal, $Receipt.marker_present, $Receipt.raw_output_persisted,
        $Receipt.rolled_back, $Receipt.web_active
    )) {
        if ($Value -isnot [bool]) { throw "remote receipt invalid" }
    }
    if ($Receipt.outcome -ceq "passed" -and (
        $Receipt.stage -cne "post_apply_verify" -or $Receipt.reason -cne "none" -or
        $Receipt.web_active -ne $true -or $Receipt.database_equal -ne $true -or
        $Receipt.awg2_equal -ne $true -or
        $Receipt.foreign_equal -ne $true -or $Receipt.rolled_back -ne $false
    )) {
        throw "remote success receipt invalid"
    }
}

function Invoke-Phase13ProductionStageMutationTransport {
    param(
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][byte[]]$PayloadBytes,
        [Parameter(Mandatory = $true)][string]$SshExecutable,
        [string[]]$SshPrefixArguments = @(),
        [Parameter(Mandatory = $true)]$SpainRoleBinding
    )
    $TransportBytes = $null
    try {
        $TransportBytes = New-Phase13ProductionStageTransportEnvelope `
            -PayloadBytes $PayloadBytes `
            -RemoteBytes $Binding.RemoteBytes `
            -RemoteSha256 $Binding.RemoteSha256
        $Arguments = @($SshPrefixArguments) + @(
            New-Phase13ProductionStageSshArguments -RoleBinding $SpainRoleBinding
        )
        $Transport = Invoke-Phase13BoundedProcess `
            -Executable $SshExecutable `
            -Arguments $Arguments `
            -InputBytes $TransportBytes `
            -TimeoutMilliseconds $script:ProductionTimeoutMilliseconds `
            -MaximumOutputBytes $script:ProductionMaximumOutputBytes
        if ($Transport.Reason -cne "success") {
            return [pscustomobject]@{ Document = $null; ProcessCount = 1; Success = $false }
        }
        try {
            $Document = $Transport.Document | ConvertFrom-Json -ErrorAction Stop
            Test-Phase13ProductionStageRemoteReceipt -Receipt $Document -Binding $Binding
        } catch {
            return [pscustomobject]@{ Document = $null; ProcessCount = 1; Success = $false }
        }
        return [pscustomobject]@{
            Document = $Document
            ProcessCount = 1
            Success = ($Document.outcome -ceq "passed")
        }
    } finally {
        if ($null -ne $TransportBytes) { [Array]::Clear($TransportBytes, 0, $TransportBytes.Length) }
    }
}

function Get-Phase13ProductionStageFixedPython {
    $Local = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    if ([string]::IsNullOrWhiteSpace($Local)) { throw "fixed Python unavailable" }
    $Path = Join-Path $Local "Python\pythoncore-3.14-64\python.exe"
    $null = Assert-Phase13ProductionStageRegularFile -Path $Path -MaximumBytes 10485760
    return $Path
}

function Invoke-Phase13ProductionStagePayloadBuilder {
    param(
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][byte[]]$AuditBytes,
        [Parameter(Mandatory = $true)][string]$PythonExecutable
    )
    $Arguments = @(
        (Join-Path $Binding.PackageRoot "production-stage-package.py"),
        "payload",
        $Binding.PackageRoot
    )
    $Result = Invoke-Phase13BoundedProcess `
        -Executable $PythonExecutable `
        -Arguments $Arguments `
        -InputBytes $AuditBytes `
        -TimeoutMilliseconds $script:ProductionTimeoutMilliseconds `
        -MaximumOutputBytes $script:ProductionMaximumOutputBytes
    if ($Result.Reason -cne "success") { throw "payload preparation failed" }
    $Bytes = (New-Object Text.UTF8Encoding($false, $true)).GetBytes([string]$Result.Document)
    if ($Bytes.Length -lt 2 -or $Bytes.Length -gt 1048576) {
        [Array]::Clear($Bytes, 0, $Bytes.Length)
        throw "payload preparation failed"
    }
    return $Bytes
}

function Write-Phase13ProductionStageTerminalReceipt {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)]$Receipt
    )
    Test-Phase13ProductionStageRemoteReceipt -Receipt $Receipt -Binding $Binding
    $Suffix = if ($Receipt.outcome -ceq "passed") { "success" } else { "failure" }
    $Path = Join-Path $OutcomeRoot ("{0}.{1}.json" -f $Binding.OutcomeId, $Suffix)
    Write-Phase13AuditCreateNewJson -Path $Path -Value $Receipt
    return $Path
}

function Invoke-Phase13ProductionStageCore {
    param(
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][string]$PackageRoot,
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)][string]$SshExecutable,
        [string[]]$SshPrefixArguments = @(),
        [Parameter(Mandatory = $true)]$RoleBindings,
        [string]$PythonExecutable = "",
        [AllowNull()][byte[]]$PreparedPayloadBytes = $null,
        [DateTimeOffset]$NowUtc = [DateTimeOffset]::UtcNow
    )
    $null = New-Phase13ProductionStageOutcomeClaim -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc
    $Audit = Invoke-Phase13ProductionStageAuditTransport `
        -Binding $Binding `
        -SshExecutable $SshExecutable `
        -SshPrefixArguments $SshPrefixArguments `
        -RoleBindings $RoleBindings
    if (-not $Audit.Success) {
        $Path = Write-Phase13ProductionStageFailure `
            -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc `
            -Stage "audit" -ReasonCode "audit_incomplete" -MutationAttempted $false
        return [pscustomobject]@{
            FailureRole = [string]$Audit.FailureRole
            FailureSubreason = [string]$Audit.FailureSubreason
            OutcomePath = $Path
            ProcessCount = 2
            Status = "failure"
        }
    }
    $PayloadBytes = $null
    try {
        if ($null -ne $PreparedPayloadBytes) {
            $PayloadBytes = [byte[]]$PreparedPayloadBytes.Clone()
        } else {
            if ([string]::IsNullOrWhiteSpace($PythonExecutable)) { throw "fixed Python unavailable" }
            $PayloadBytes = Invoke-Phase13ProductionStagePayloadBuilder `
                -Binding $Binding -AuditBytes $Audit.AuditBytes -PythonExecutable $PythonExecutable
        }
    } catch {
        $Path = Write-Phase13ProductionStageFailure `
            -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc `
            -Stage "stage" -ReasonCode "checksum_mismatch" -MutationAttempted $false
        return [pscustomobject]@{
            FailureRole = "not_applicable"
            FailureSubreason = "not_applicable"
            OutcomePath = $Path
            ProcessCount = 2
            Status = "failure"
        }
    } finally {
        if ($null -ne $Audit.AuditBytes) { [Array]::Clear($Audit.AuditBytes, 0, $Audit.AuditBytes.Length) }
    }
    try {
        $Mutation = Invoke-Phase13ProductionStageMutationTransport `
            -Binding $Binding `
            -PayloadBytes $PayloadBytes `
            -SshExecutable $SshExecutable `
            -SshPrefixArguments $SshPrefixArguments `
            -SpainRoleBinding $RoleBindings["spain"]
        if ($null -eq $Mutation.Document) {
            $Path = Write-Phase13ProductionStageFailure `
                -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc `
                -Stage "rollback" -ReasonCode "rollback_required" -MutationAttempted $true
            return [pscustomobject]@{
                FailureRole = "not_applicable"
                FailureSubreason = "not_applicable"
                OutcomePath = $Path
                ProcessCount = 3
                Status = "failure"
            }
        }
        $Path = Write-Phase13ProductionStageTerminalReceipt `
            -OutcomeRoot $OutcomeRoot -Binding $Binding -Receipt $Mutation.Document
        $Status = if ($Mutation.Success) { "success" } else { "failure" }
        return [pscustomobject]@{
            FailureRole = "not_applicable"
            FailureSubreason = "not_applicable"
            OutcomePath = $Path
            ProcessCount = 3
            Status = $Status
        }
    } finally {
        if ($null -ne $PayloadBytes) { [Array]::Clear($PayloadBytes, 0, $PayloadBytes.Length) }
    }
}

function ConvertTo-Phase13ProductionStagePublicReceipt {
    param(
        [Parameter(Mandatory = $true)]$CoreResult,
        [Parameter(Mandatory = $true)][string]$OutcomeId
    )
    $Hash = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes($CoreResult.OutcomePath))
    $FailureRole = [string]$CoreResult.FailureRole
    $FailureSubreason = [string]$CoreResult.FailureSubreason
    if ($FailureRole -cnotin @("usa", "spain", "not_applicable") -or
        $FailureSubreason -cnotin @(
            "timeout", "output_oversized", "ssh_process_failed", "frame_invalid",
            "audit_pair_invalid", "not_applicable"
        )) {
        throw "production stage public receipt invalid"
    }
    return [pscustomobject]@{
        FailureRole = $FailureRole
        FailureSubreason = $FailureSubreason
        OutcomeId = $OutcomeId
        OutcomeSha256 = $Hash
        ProcessCount = [int]$CoreResult.ProcessCount
        Status = [string]$CoreResult.Status
    }
}

function Invoke-Phase13ProductionStageWebDataApply {
    param(
        [string]$PackageRoot,
        [string]$ExactApprovalPhrase
    )
    if ([string]::IsNullOrWhiteSpace($PackageRoot) -or
        [string]::IsNullOrWhiteSpace($ExactApprovalPhrase)) {
        throw "production stage arguments required"
    }
    try {
        $Binding = Test-Phase13ProductionStagePackage `
            -PackageRoot $PackageRoot `
            -ExactApprovalPhrase $ExactApprovalPhrase
        $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $SshExecutable = "C:\Windows\System32\OpenSSH\ssh.exe"
        $SshKeygenExecutable = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"
        foreach ($Executable in @($SshExecutable, $SshKeygenExecutable)) {
            $null = Assert-Phase13ProductionStageRegularFile -Path $Executable -MaximumBytes 10485760
        }
        $RoleBindings = @{
            usa = Read-Phase13AuditFixedRoleBinding -Role "usa" -ExpectedOwnerSid $CurrentSid -SshKeygenExecutable $SshKeygenExecutable
            spain = Read-Phase13AuditFixedRoleBinding -Role "spain" -ExpectedOwnerSid $CurrentSid -SshKeygenExecutable $SshKeygenExecutable
        }
        $OutcomeRoot = "C:\ProgramData\AMN2\private\phase13-bot-web-stage-apply\outcomes"
        Protect-Phase13AuditOutcomeRoot -Path $OutcomeRoot -OwnerSid $CurrentSid
        $PythonExecutable = Get-Phase13ProductionStageFixedPython
        $CoreResult = Invoke-Phase13ProductionStageCore `
            -Binding $Binding `
            -PackageRoot $Binding.PackageRoot `
            -OutcomeRoot $OutcomeRoot `
            -SshExecutable $SshExecutable `
            -RoleBindings $RoleBindings `
            -PythonExecutable $PythonExecutable
        return ConvertTo-Phase13ProductionStagePublicReceipt `
            -CoreResult $CoreResult `
            -OutcomeId $Binding.OutcomeId
    } catch {
        throw "production stage failed closed"
    }
}
