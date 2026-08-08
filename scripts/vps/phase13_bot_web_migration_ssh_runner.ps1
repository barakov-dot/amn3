Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:MaximumTimeoutMilliseconds = 60000
$script:MaximumOutputBytes = 1048576
$script:MaximumInputBytes = 1048576
$script:RoleTrustRoots = @{
    "usa" = "C:\ProgramData\AMN2\trust\usa"
    "spain" = "C:\ProgramData\AMN2\trust\spain"
}
$script:SecretClasses = @(
    "telegram_bot_token",
    "app_secret_key",
    "web_password_hash",
    "web_session_secret"
)

function Get-Phase13RoleTransportContract {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("usa", "spain")]
        [string]$Role
    )
    $TrustRoot = [string]$script:RoleTrustRoots[$Role]
    if (-not [System.IO.Path]::IsPathRooted($TrustRoot)) {
        throw "fixed trust root invalid"
    }
    return [pscustomobject]@{
        Role = $Role
        TrustRoot = $TrustRoot
        BindingPath = Join-Path $TrustRoot "target.env"
        KeyPath = Join-Path $TrustRoot "id_ed25519"
        KnownHostsPath = Join-Path $TrustRoot "known_hosts"
    }
}

function ConvertTo-Phase13ProcessArgument {
    param([Parameter(Mandatory = $true)][string]$Value)
    return '"' + $Value.Replace('\', '\').Replace('"', '\"') + '"'
}

function New-Phase13EphemeralHmacKey {
    $Key = New-Object byte[] 32
    $Generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $Generator.GetBytes($Key)
    } finally {
        $Generator.Dispose()
    }
    return $Key
}

function Invoke-Phase13BoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][byte[]]$InputBytes,
        [int]$TimeoutMilliseconds = 60000,
        [int]$MaximumOutputBytes = 1048576
    )
    if ($TimeoutMilliseconds -lt 1 -or $TimeoutMilliseconds -gt $script:MaximumTimeoutMilliseconds -or
        $MaximumOutputBytes -lt 1 -or $MaximumOutputBytes -gt $script:MaximumOutputBytes -or
        $InputBytes.Length -gt $script:MaximumInputBytes) {
        throw "bounded process contract invalid"
    }
    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $Executable
    $StartInfo.Arguments = (($Arguments | ForEach-Object { ConvertTo-Phase13ProcessArgument -Value $_ }) -join " ")
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardInput = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $StartInfo.StandardErrorEncoding = New-Object System.Text.UTF8Encoding($false)
    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $StartInfo
    $PreviousConsoleInputEncoding = [Console]::InputEncoding
    $Reason = "process_failure"
    $Document = $null
    $ExitCode = -1
    $OutputMemory = New-Object System.IO.MemoryStream
    try {
        [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
        [void]$Process.Start()
        $OutputStream = $Process.StandardOutput.BaseStream
        $ErrorStream = $Process.StandardError.BaseStream
        $OutputBuffer = New-Object byte[] 4096
        $ErrorBuffer = New-Object byte[] 4096
        $OutputTask = $OutputStream.ReadAsync($OutputBuffer, 0, $OutputBuffer.Length)
        $ErrorTask = $ErrorStream.ReadAsync($ErrorBuffer, 0, $ErrorBuffer.Length)
        $OutputDone = $false
        $ErrorDone = $false
        $TotalBytes = 0
        $Timer = [System.Diagnostics.Stopwatch]::StartNew()
        $InputStream = $Process.StandardInput.BaseStream
        if ($InputBytes.Length -gt 0) {
            $InputStream.Write($InputBytes, 0, $InputBytes.Length)
            $InputStream.Flush()
        }
        $InputStream.Close()

        while ($true) {
            if (-not $OutputDone -and $OutputTask.IsCompleted) {
                $Read = $OutputTask.GetAwaiter().GetResult()
                if ($Read -eq 0) {
                    $OutputDone = $true
                } else {
                    $TotalBytes += $Read
                    if ($TotalBytes -gt $MaximumOutputBytes) {
                        $Reason = "output_oversized"
                        break
                    }
                    $OutputMemory.Write($OutputBuffer, 0, $Read)
                    $OutputTask = $OutputStream.ReadAsync($OutputBuffer, 0, $OutputBuffer.Length)
                }
            }
            if (-not $ErrorDone -and $ErrorTask.IsCompleted) {
                $Read = $ErrorTask.GetAwaiter().GetResult()
                if ($Read -eq 0) {
                    $ErrorDone = $true
                } else {
                    $TotalBytes += $Read
                    if ($TotalBytes -gt $MaximumOutputBytes) {
                        $Reason = "output_oversized"
                        break
                    }
                    $ErrorTask = $ErrorStream.ReadAsync($ErrorBuffer, 0, $ErrorBuffer.Length)
                }
            }
            if ($OutputDone -and $ErrorDone -and $Process.HasExited) {
                break
            }
            if ($Timer.ElapsedMilliseconds -ge $TimeoutMilliseconds) {
                $Reason = "timeout"
                break
            }
            Start-Sleep -Milliseconds 5
        }
        $Timer.Stop()
        if ($Reason -in @("timeout", "output_oversized")) {
            try { $Process.Kill() } catch { }
            [void]$Process.WaitForExit(5000)
        } else {
            $Process.WaitForExit()
            $ExitCode = $Process.ExitCode
            if ($ExitCode -ne 0) {
                $Reason = "process_failure"
            } else {
                $Decoder = New-Object System.Text.UTF8Encoding($false, $true)
                $Document = $Decoder.GetString($OutputMemory.ToArray())
                $Reason = "success"
            }
        }
    } catch {
        $Reason = "process_failure"
        $Document = $null
        $ExitCode = -1
        try {
            $null = $Process.Id
            if ($Process.WaitForExit(1000)) {
                $ExitCode = $Process.ExitCode
            }
        } catch {
        }
    } finally {
        [Console]::InputEncoding = $PreviousConsoleInputEncoding
        if (-not $Process.HasExited) {
            try { $Process.Kill() } catch { }
        }
        $Process.Dispose()
        $OutputMemory.Dispose()
    }
    return [pscustomobject]@{
        Reason = $Reason
        Document = $Document
        ExitCode = $ExitCode
    }
}

function ConvertTo-Phase13CanonicalAudit {
    param(
        [Parameter(Mandatory = $true)]$Audit,
        [Parameter(Mandatory = $true)][ValidateSet("usa-source", "spain-target")][string]$ExpectedRole
    )
    if ($Audit.schema -ne "amn2.phase13.bot-web-audit.v1" -or
        $Audit.role -ne $ExpectedRole -or
        [string]$Audit.checked_at -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$') {
        throw "audit identity invalid"
    }
    if (
        [string]$Audit.database.schema_sha256 -notmatch '^[0-9a-f]{64}$' -or
        [string]$Audit.database.counts_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $Audit.database.foreign_key_violations -lt 0 -or
        $Audit.database.table_count -lt 0) {
        throw "audit database invalid"
    }
    if (
        $Audit.safety_receipt.mutation_attempted -ne $false -or
        $Audit.safety_receipt.raw_output_persisted -ne $false -or
        $Audit.safety_receipt.secret_bearing_data_persisted -ne $false) {
        throw "audit safety invalid"
    }
    foreach ($BooleanValue in @(
        $Audit.services.web_active,
        $Audit.services.bot_active,
        $Audit.services.web_loopback_only,
        $Audit.database.integrity_ok,
        $Audit.environment.telegram_bot_token_present,
        $Audit.environment.app_secret_present,
        $Audit.environment.web_password_hash_present,
        $Audit.environment.session_secret_present,
        $Audit.required_artifacts.database_readable,
        $Audit.required_artifacts.environment_reference_proof_available
    )) {
        if ($BooleanValue -isnot [bool]) {
            throw "audit boolean invalid"
        }
    }
    return [ordered]@{
        schema = "amn2.phase13.bot-web-audit.v1"
        role = $ExpectedRole
        checked_at = [string]$Audit.checked_at
        services = [ordered]@{
            web_active = [bool]$Audit.services.web_active
            bot_active = [bool]$Audit.services.bot_active
            web_loopback_only = [bool]$Audit.services.web_loopback_only
        }
        database = [ordered]@{
            integrity_ok = [bool]$Audit.database.integrity_ok
            foreign_key_violations = [int]$Audit.database.foreign_key_violations
            table_count = [int]$Audit.database.table_count
            schema_sha256 = [string]$Audit.database.schema_sha256
            counts_sha256 = [string]$Audit.database.counts_sha256
        }
        environment = [ordered]@{
            telegram_bot_token_present = [bool]$Audit.environment.telegram_bot_token_present
            app_secret_present = [bool]$Audit.environment.app_secret_present
            web_password_hash_present = [bool]$Audit.environment.web_password_hash_present
            session_secret_present = [bool]$Audit.environment.session_secret_present
        }
        required_artifacts = [ordered]@{
            database_readable = [bool]$Audit.required_artifacts.database_readable
            environment_reference_proof_available = [bool]$Audit.required_artifacts.environment_reference_proof_available
        }
        safety_receipt = [ordered]@{
            mutation_attempted = $false
            raw_output_persisted = $false
            secret_bearing_data_persisted = $false
        }
    }
}

function ConvertTo-Phase13SanitizedAuditPair {
    param(
        [Parameter(Mandatory = $true)]$UsaDocument,
        [Parameter(Mandatory = $true)]$SpainDocument
    )
    if ($UsaDocument.schema -ne "amn2.phase13.bot-web-collector.v1" -or
        $SpainDocument.schema -ne "amn2.phase13.bot-web-collector.v1" -or
        $UsaDocument.role -ne "usa" -or $SpainDocument.role -ne "spain") {
        throw "collector envelope invalid"
    }
    $Equality = [ordered]@{}
    foreach ($SecretClass in $script:SecretClasses) {
        $UsaDigest = [string]$UsaDocument.secret_reference_hmac.$SecretClass
        $SpainDigest = [string]$SpainDocument.secret_reference_hmac.$SecretClass
        if ($UsaDigest -notmatch '^[0-9a-f]{64}$' -or $SpainDigest -notmatch '^[0-9a-f]{64}$') {
            throw "ephemeral proof invalid"
        }
        $Equality[$SecretClass] = [System.StringComparer]::Ordinal.Equals($UsaDigest, $SpainDigest)
    }
    try {
        $UsaAudit = ConvertTo-Phase13CanonicalAudit -Audit $UsaDocument.audit -ExpectedRole "usa-source"
    } catch {
        $Category = switch -CaseSensitive ([string]$_.Exception.Message) {
            "audit identity invalid" { "identity" }
            "audit database invalid" { "database" }
            "audit safety invalid" { "safety" }
            "audit boolean invalid" { "boolean" }
            default { "internal" }
        }
        throw "usa audit $Category invalid"
    }
    try {
        $SpainAudit = ConvertTo-Phase13CanonicalAudit -Audit $SpainDocument.audit -ExpectedRole "spain-target"
    } catch {
        $Category = switch -CaseSensitive ([string]$_.Exception.Message) {
            "audit identity invalid" { "identity" }
            "audit database invalid" { "database" }
            "audit safety invalid" { "safety" }
            "audit boolean invalid" { "boolean" }
            default { "internal" }
        }
        throw "spain audit $Category invalid"
    }
    $Result = [ordered]@{
        schema = "amn2.phase13.bot-web-audit-pair.v1"
        audits = @($UsaAudit, $SpainAudit)
        secret_reference_equal = $Equality
        stable_fingerprints_persisted = $false
        safety_receipt = [ordered]@{
            ssh_processes = 2
            raw_stdout_persisted = $false
            raw_stderr_persisted = $false
            raw_secret_emitted = $false
        }
    }
    return ($Result | ConvertTo-Json -Depth 16 -Compress)
}

function Invoke-Phase13LocalFakeAuditPair {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string]$HarnessPath,
        [Parameter(Mandatory = $true)][string]$CounterPath
    )
    $Key = New-Phase13EphemeralHmacKey
    try {
        $KeyLine = [Convert]::ToBase64String($Key) + "`n"
        $InputBytes = [System.Text.Encoding]::ASCII.GetBytes($KeyLine)
        $Documents = @{}
        foreach ($Role in @("usa", "spain")) {
            $TransportContract = Get-Phase13RoleTransportContract -Role $Role
            $Transport = Invoke-Phase13BoundedProcess -Executable $Executable -Arguments @($HarnessPath, $CounterPath, $TransportContract.Role) -InputBytes $InputBytes -TimeoutMilliseconds 60000 -MaximumOutputBytes 1048576
            if ($Transport.Reason -ne "success") {
                throw "local fake transport failed: $($Transport.Reason):$($Transport.ExitCode)"
            }
            $Documents[$Role] = $Transport.Document | ConvertFrom-Json
        }
        return ConvertTo-Phase13SanitizedAuditPair -UsaDocument $Documents["usa"] -SpainDocument $Documents["spain"]
    } finally {
        [Array]::Clear($Key, 0, $Key.Length)
    }
}

function Get-Phase13Sha256Hex {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)
    $Hasher = [System.Security.Cryptography.SHA256]::Create()
    try {
        return -join ($Hasher.ComputeHash($Bytes) | ForEach-Object { $_.ToString("x2") })
    } finally {
        $Hasher.Dispose()
    }
}

function Test-Phase13ExactPropertySet {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string[]]$Expected,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($null -eq $Value) {
        throw $Message
    }
    $Actual = @($Value.PSObject.Properties.Name | Sort-Object)
    $Required = @($Expected | Sort-Object)
    if (($Actual -join "`n") -cne ($Required -join "`n")) {
        throw $Message
    }
}

function Test-Phase13CutoverBinding {
    param(
        [Parameter(Mandatory = $true)][byte[]]$ManifestBytes,
        [Parameter(Mandatory = $true)][byte[]]$CutoverBytes,
        [Parameter(Mandatory = $true)][byte[]]$RunnerBytes,
        [Parameter(Mandatory = $true)][DateTimeOffset]$NowUtc
    )
    if ($ManifestBytes.Length -lt 2 -or $CutoverBytes.Length -lt 1 -or $RunnerBytes.Length -lt 1) {
        throw "cutover binding bytes invalid"
    }
    try {
        $Decoder = New-Object System.Text.UTF8Encoding($false, $true)
        $Manifest = $Decoder.GetString($ManifestBytes) | ConvertFrom-Json
    } catch {
        throw "cutover manifest invalid"
    }
    Test-Phase13ExactPropertySet -Value $Manifest -Expected @(
        "approval_mode", "artifacts", "created_at", "expires_at",
        "live_mutation_authorized", "outcome_id", "schema", "trust_bundles",
        "web_data_apply_authorized"
    ) -Message "cutover manifest keys invalid"
    if ($Manifest.schema -cne "amn2.phase13.bot-web-cutover-manifest.v1" -or
        $Manifest.approval_mode -cne "bot_cutover" -or
        $Manifest.live_mutation_authorized -ne $false -or
        $Manifest.web_data_apply_authorized -ne $false -or
        [string]$Manifest.outcome_id -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$') {
        throw "cutover manifest contract invalid"
    }
    try {
        $CreatedAt = [DateTimeOffset]::Parse(
            [string]$Manifest.created_at,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::AssumeUniversal
        ).ToUniversalTime()
        $ExpiresAt = [DateTimeOffset]::Parse(
            [string]$Manifest.expires_at,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::AssumeUniversal
        ).ToUniversalTime()
    } catch {
        throw "cutover manifest time invalid"
    }
    if ($ExpiresAt -le $NowUtc.ToUniversalTime()) {
        throw "cutover manifest expired"
    }
    if ($CreatedAt -gt $ExpiresAt) {
        throw "cutover manifest time invalid"
    }

    Test-Phase13ExactPropertySet -Value $Manifest.artifacts -Expected @(
        "cutover_remote", "ssh_runner"
    ) -Message "cutover artifact set invalid"
    $ExpectedArtifacts = @{
        "cutover_remote" = $CutoverBytes
        "ssh_runner" = $RunnerBytes
    }
    foreach ($Name in @("cutover_remote", "ssh_runner")) {
        $Binding = $Manifest.artifacts.$Name
        Test-Phase13ExactPropertySet -Value $Binding -Expected @(
            "sha256", "size"
        ) -Message "cutover artifact binding invalid"
        $Bytes = [byte[]]$ExpectedArtifacts[$Name]
        if ([string]$Binding.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            [long]$Binding.size -ne $Bytes.Length -or
            [string]$Binding.sha256 -cne (Get-Phase13Sha256Hex -Bytes $Bytes)) {
            throw "cutover artifact checksum invalid"
        }
    }

    Test-Phase13ExactPropertySet -Value $Manifest.trust_bundles -Expected @(
        "usa", "spain"
    ) -Message "cutover trust bundle set invalid"
    foreach ($Role in @("usa", "spain")) {
        $Trust = $Manifest.trust_bundles.$Role
        Test-Phase13ExactPropertySet -Value $Trust -Expected @(
            "role", "trust_root"
        ) -Message "cutover trust bundle invalid"
        if ([string]$Trust.role -cne $Role -or
            [string]$Trust.trust_root -cne [string]$script:RoleTrustRoots[$Role]) {
            throw "cutover trust bundle invalid"
        }
    }

    return [pscustomobject]@{
        Schema = "amn2.phase13.bot-web-cutover-binding.v1"
        OutcomeId = [string]$Manifest.outcome_id
        ManifestSha256 = Get-Phase13Sha256Hex -Bytes $ManifestBytes
        CutoverSha256 = Get-Phase13Sha256Hex -Bytes $CutoverBytes
        RunnerSha256 = Get-Phase13Sha256Hex -Bytes $RunnerBytes
        ExpiresAt = $ExpiresAt.ToString("o")
        TrustRoles = @("usa", "spain")
    }
}

function New-Phase13LocalFakeCutoverClaim {
    param(
        [Parameter(Mandatory = $true)][string]$FakeRoot,
        [Parameter(Mandatory = $true)]$Binding
    )
    Test-Phase13ExactPropertySet -Value $Binding -Expected @(
        "Schema", "OutcomeId", "ManifestSha256", "CutoverSha256",
        "RunnerSha256", "ExpiresAt", "TrustRoles"
    ) -Message "cutover binding invalid"
    if ($Binding.Schema -cne "amn2.phase13.bot-web-cutover-binding.v1" -or
        [string]$Binding.OutcomeId -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$' -or
        [string]$Binding.ManifestSha256 -cnotmatch '^[0-9a-f]{64}$' -or
        [string]$Binding.CutoverSha256 -cnotmatch '^[0-9a-f]{64}$' -or
        [string]$Binding.RunnerSha256 -cnotmatch '^[0-9a-f]{64}$' -or
        (@($Binding.TrustRoles) -join ",") -cne "usa,spain") {
        throw "cutover binding invalid"
    }
    try {
        $BindingExpiresAt = [DateTimeOffset]::Parse(
            [string]$Binding.ExpiresAt,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::AssumeUniversal
        ).ToUniversalTime()
    } catch {
        throw "cutover binding invalid"
    }
    if ($BindingExpiresAt -le [DateTimeOffset]::UtcNow) {
        throw "cutover binding expired"
    }
    if (-not [IO.Path]::IsPathRooted($FakeRoot)) {
        throw "local fake root invalid"
    }
    $ResolvedRoot = [IO.Path]::GetFullPath($FakeRoot)
    $RootItem = Get-Item -LiteralPath $ResolvedRoot -Force -ErrorAction Stop
    if (-not $RootItem.PSIsContainer -or ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "local fake root invalid"
    }
    $SentinelPath = Join-Path $ResolvedRoot ".amn2-phase13-local-fake-harness"
    $SentinelItem = Get-Item -LiteralPath $SentinelPath -Force -ErrorAction Stop
    if ($SentinelItem.PSIsContainer -or
        ($SentinelItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        [IO.File]::ReadAllText($SentinelPath, (New-Object Text.UTF8Encoding($false, $true))) -cne "task8-local-only`n") {
        throw "local fake root invalid"
    }
    $OutcomeRoot = Join-Path $ResolvedRoot "outcomes"
    if ([IO.Directory]::Exists($OutcomeRoot)) {
        $OutcomeItem = Get-Item -LiteralPath $OutcomeRoot -Force -ErrorAction Stop
        if (-not $OutcomeItem.PSIsContainer -or
            ($OutcomeItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "local fake root invalid"
        }
    } else {
        [void][IO.Directory]::CreateDirectory($OutcomeRoot)
    }
    $ClaimPath = Join-Path $OutcomeRoot ("{0}.claim.json" -f $Binding.OutcomeId)
    if ([IO.File]::Exists($ClaimPath)) {
        throw "outcome claim replay"
    }
    $Claim = [ordered]@{
        cutover_sha256 = [string]$Binding.CutoverSha256
        expires_at = [string]$Binding.ExpiresAt
        manifest_sha256 = [string]$Binding.ManifestSha256
        outcome_id = [string]$Binding.OutcomeId
        runner_sha256 = [string]$Binding.RunnerSha256
        schema = "amn2.phase13.bot-web-cutover-claim.v1"
    }
    $ClaimBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(
        (($Claim | ConvertTo-Json -Depth 4 -Compress) + "`n")
    )
    try {
        $Stream = New-Object IO.FileStream(
            $ClaimPath,
            [IO.FileMode]::CreateNew,
            [IO.FileAccess]::Write,
            [IO.FileShare]::None
        )
        try {
            $Stream.Write($ClaimBytes, 0, $ClaimBytes.Length)
            $Stream.Flush($true)
        } finally {
            $Stream.Dispose()
        }
    } catch [IO.IOException] {
        if ([IO.File]::Exists($ClaimPath)) {
            throw "outcome claim replay"
        }
        throw "outcome claim write failed"
    }
    return $ClaimPath
}

function Get-Phase13AuditArtifactContract {
    return [ordered]@{
        audit_evidence_schema = "audit-evidence.schema.json"
        audit_package = "audit-package.py"
        audit_tooling_manifest_schema = "audit-tooling-manifest.schema.json"
        db_schema = "db-schema.py"
        failure_evidence_schema = "failure-evidence.schema.json"
        merge = "merge.py"
        migration_contract = "migration-contract.py"
        migration_manifest_schema = "migration-manifest.schema.json"
        migration_package = "migration-package.py"
        migration_plan_schema = "migration-plan.schema.json"
        readonly_collector = "readonly-collector.py"
        remote_cutover = "remote-cutover.sh"
        remote_stage = "remote-stage.sh"
        ssh_runner = "ssh-runner.ps1"
    }
}

function Get-Phase13AuditExactApprovalPhrase {
    param([Parameter(Mandatory = $true)]$Binding)
    $Prefix = [Text.Encoding]::UTF8.GetString(
        [Convert]::FromBase64String(
            "0KPQotCS0JXQoNCW0JTQkNCuINCe0JTQmNCdIFRXTy1IT1NUIFJFQUQtT05MWSBVU0EvU1BBSU4gQk9UL1dFQiBBVURJVA=="
        )
    )
    return @(
        "$Prefix OUTCOME_$($Binding.OutcomeId)",
        "MANIFEST_SHA_$($Binding.ManifestSha256)",
        "RUNNER_SHA_$($Binding.RunnerSha256)",
        "COLLECTOR_SHA_$($Binding.CollectorSha256)",
        "AUDIT_SCHEMA_SHA_$($Binding.AuditSchemaSha256)",
        "ROOT_BASE_$($Binding.RootHead)",
        "AMN2_HEAD_$($Binding.Amn2Head)",
        "EXPIRES_AT_$($Binding.ExpiresAt)",
        "MAX_ATTEMPTS_1",
        "NO_BACKUP_NO_DATA_TRANSFER_NO_DEPLOY_NO_DB_APPLY_NO_BOT_CUTOVER_NO_USA_RELEASE_NO_MUTATION"
    ) -join " "
}

function Read-Phase13AuditStrictJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$MaximumBytes = 1048576
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or
        ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        $Item.Length -lt 2 -or $Item.Length -gt $MaximumBytes) {
        throw "audit tooling manifest is unsafe"
    }
    $Bytes = [IO.File]::ReadAllBytes($Item.FullName)
    if ($Bytes[$Bytes.Length - 1] -ne 10 -or @($Bytes | Where-Object { $_ -eq 13 }).Count -ne 0) {
        throw "audit tooling manifest is not canonical"
    }
    try {
        $Text = (New-Object Text.UTF8Encoding($false, $true)).GetString($Bytes)
        $Value = $Text | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "audit tooling manifest is invalid"
    }
    return [pscustomobject]@{ Bytes = $Bytes; Value = $Value }
}

function Test-Phase13AuditToolingBinding {
    param(
        [Parameter(Mandatory = $true)][string]$PackageRoot,
        [Parameter(Mandatory = $true)][string]$ExactApprovalPhrase,
        [DateTimeOffset]$NowUtc = [DateTimeOffset]::UtcNow
    )
    if (-not [IO.Path]::IsPathRooted($PackageRoot)) {
        throw "audit tooling root is unsafe"
    }
    $RootItem = Get-Item -LiteralPath $PackageRoot -Force -ErrorAction Stop
    if (-not $RootItem.PSIsContainer -or
        ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "audit tooling root is unsafe"
    }
    $Root = $RootItem.FullName
    $ArtifactContract = Get-Phase13AuditArtifactContract
    $ExpectedFiles = @($ArtifactContract.Values) + @("manifest.json")
    $ActualItems = @(Get-ChildItem -LiteralPath $Root -Force)
    if ($ActualItems.Count -ne $ExpectedFiles.Count -or
        (@($ActualItems.Name | Sort-Object) -join "`n") -cne (@($ExpectedFiles | Sort-Object) -join "`n")) {
        throw "audit tooling artifact set is invalid"
    }
    foreach ($Item in $ActualItems) {
        if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "audit tooling artifact is unsafe"
        }
    }
    $ManifestDocument = Read-Phase13AuditStrictJson -Path (Join-Path $Root "manifest.json")
    $Manifest = $ManifestDocument.Value
    Test-Phase13ExactPropertySet -Value $Manifest -Expected @(
        "amn2_head", "artifacts", "created_at", "expires_at", "max_attempts",
        "outcome_id", "roles", "root_head", "safety", "schema", "trust_bundles"
    ) -Message "audit tooling manifest keys are invalid"
    if ($Manifest.schema -cne "amn2.phase13.bot-web-audit-tooling-manifest.v1" -or
        $Manifest.root_head -cne "408298982ce820b6a73c4f6721ce71e85e9c93e6" -or
        $Manifest.amn2_head -cne "910539eaa8051cb1b59131d38b9fa27b9392744d" -or
        [int]$Manifest.max_attempts -ne 1 -or
        [string]$Manifest.outcome_id -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$') {
        throw "audit tooling manifest contract is invalid"
    }
    Test-Phase13ExactPropertySet -Value $Manifest.roles -Expected @("source", "target") -Message "audit tooling role binding is invalid"
    if ($Manifest.roles.source -cne "usa-source" -or $Manifest.roles.target -cne "spain-target") {
        throw "audit tooling role binding is invalid"
    }
    Test-Phase13ExactPropertySet -Value $Manifest.safety -Expected @(
        "backup_allowed", "bot_cutover_allowed", "data_transfer_allowed",
        "db_apply_allowed", "live_mutation_authorized", "package_build_allowed",
        "remote_write_allowed", "usa_release_allowed"
    ) -Message "audit tooling safety contract is invalid"
    foreach ($Name in $Manifest.safety.PSObject.Properties.Name) {
        if ($Manifest.safety.$Name -ne $false) {
            throw "audit tooling safety contract is invalid"
        }
    }
    try {
        $CreatedAt = [DateTimeOffset]::Parse([string]$Manifest.created_at).ToUniversalTime()
        $ExpiresAt = [DateTimeOffset]::Parse([string]$Manifest.expires_at).ToUniversalTime()
    } catch {
        throw "audit tooling manifest time is invalid"
    }
    if ($CreatedAt -ge $ExpiresAt) {
        throw "audit tooling manifest time is invalid"
    }
    $Now = $NowUtc.ToUniversalTime()
    if ($Now -lt $CreatedAt) {
        throw "audit tooling manifest not yet valid"
    }
    if ($Now -ge $ExpiresAt) {
        throw "audit tooling manifest expired"
    }
    Test-Phase13ExactPropertySet -Value $Manifest.artifacts -Expected @($ArtifactContract.Keys) -Message "audit tooling artifact binding is invalid"
    $ArtifactHashes = @{}
    foreach ($ArtifactId in $ArtifactContract.Keys) {
        $ExpectedFilename = [string]$ArtifactContract[$ArtifactId]
        $ArtifactBinding = $Manifest.artifacts.$ArtifactId
        Test-Phase13ExactPropertySet -Value $ArtifactBinding -Expected @("filename", "sha256", "size") -Message "audit tooling artifact binding is invalid"
        if ([string]$ArtifactBinding.filename -cne $ExpectedFilename -or
            [string]$ArtifactBinding.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            [long]$ArtifactBinding.size -lt 1 -or [long]$ArtifactBinding.size -gt 4194304) {
            throw "audit tooling artifact binding is invalid"
        }
        $ArtifactPath = Join-Path $Root $ExpectedFilename
        $ArtifactItem = Get-Item -LiteralPath $ArtifactPath -Force -ErrorAction Stop
        if ($ArtifactItem.PSIsContainer -or
            ($ArtifactItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            $ArtifactItem.Length -ne [long]$ArtifactBinding.size) {
            throw "audit tooling artifact checksum mismatch"
        }
        $ObservedHash = Get-Phase13Sha256Hex -Bytes ([IO.File]::ReadAllBytes($ArtifactPath))
        if ($ObservedHash -cne [string]$ArtifactBinding.sha256) {
            throw "audit tooling artifact checksum mismatch"
        }
        $ArtifactHashes[$ArtifactId] = $ObservedHash
    }
    Test-Phase13ExactPropertySet -Value $Manifest.trust_bundles -Expected @("usa", "spain") -Message "audit tooling trust binding is invalid"
    $ExpectedTrust = @{
        usa = @{ BindingId = "phase13-bot-web-runner-fixed-usa-v1"; Role = "usa-source" }
        spain = @{ BindingId = "phase13-bot-web-runner-fixed-spain-v1"; Role = "spain-target" }
    }
    foreach ($Role in @("usa", "spain")) {
        $Trust = $Manifest.trust_bundles.$Role
        Test-Phase13ExactPropertySet -Value $Trust -Expected @("binding_id", "overridable", "role", "runner_sha256") -Message "audit tooling trust binding is invalid"
        if ($Trust.binding_id -cne $ExpectedTrust[$Role].BindingId -or
            $Trust.role -cne $ExpectedTrust[$Role].Role -or
            $Trust.overridable -ne $false -or
            $Trust.runner_sha256 -cne $ArtifactHashes["ssh_runner"]) {
            throw "audit tooling trust binding is invalid"
        }
    }
    $Binding = [pscustomobject]@{
        Amn2Head = [string]$Manifest.amn2_head
        AuditSchemaSha256 = [string]$ArtifactHashes["audit_evidence_schema"]
        CollectorBytes = [IO.File]::ReadAllBytes((Join-Path $Root $ArtifactContract["readonly_collector"]))
        CollectorSha256 = [string]$ArtifactHashes["readonly_collector"]
        ExpiresAt = [string]$Manifest.expires_at
        ManifestSha256 = Get-Phase13Sha256Hex -Bytes $ManifestDocument.Bytes
        OutcomeId = [string]$Manifest.outcome_id
        PackageRoot = $Root
        RootHead = [string]$Manifest.root_head
        RunnerSha256 = [string]$ArtifactHashes["ssh_runner"]
    }
    if ($ExactApprovalPhrase -cne (Get-Phase13AuditExactApprovalPhrase -Binding $Binding)) {
        throw "exact approval mismatch"
    }
    return $Binding
}

function ConvertTo-Phase13AuditCanonicalJsonBytes {
    param([Parameter(Mandatory = $true)]$Value)
    return (New-Object Text.UTF8Encoding($false)).GetBytes(
        (($Value | ConvertTo-Json -Depth 24 -Compress) + "`n")
    )
}

function Write-Phase13AuditCreateNewJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $Bytes = ConvertTo-Phase13AuditCanonicalJsonBytes -Value $Value
    try {
        $Stream = New-Object IO.FileStream(
            $Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None
        )
        try {
            $Stream.Write($Bytes, 0, $Bytes.Length)
            $Stream.Flush($true)
        } finally {
            $Stream.Dispose()
        }
    } catch [IO.IOException] {
        throw "sanitized outcome write failed"
    } finally {
        [Array]::Clear($Bytes, 0, $Bytes.Length)
    }
}

function New-Phase13AuditOutcomeClaim {
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
        throw "audit tooling manifest expired"
    }
    $ClaimPath = Join-Path $RootItem.FullName ("{0}.claim.json" -f $Binding.OutcomeId)
    if ([IO.File]::Exists($ClaimPath)) {
        throw "outcome claim replay"
    }
    $Claim = [ordered]@{
        collector_sha256 = [string]$Binding.CollectorSha256
        expires_at = [string]$Binding.ExpiresAt
        manifest_sha256 = [string]$Binding.ManifestSha256
        outcome_id = [string]$Binding.OutcomeId
        runner_sha256 = [string]$Binding.RunnerSha256
        schema = "amn2.phase13.bot-web-audit-claim.v1"
    }
    try {
        Write-Phase13AuditCreateNewJson -Path $ClaimPath -Value $Claim
    } catch {
        if ([IO.File]::Exists($ClaimPath)) {
            throw "outcome claim replay"
        }
        throw "outcome claim write failed"
    }
    return $ClaimPath
}

function New-Phase13AuditTransportEnvelope {
    param(
        [Parameter(Mandatory = $true)][byte[]]$CollectorBytes,
        [Parameter(Mandatory = $true)][string]$CollectorSha256,
        [Parameter(Mandatory = $true)][byte[]]$EphemeralHmacKey
    )
    $Envelope = [ordered]@{
        collector_b64 = [Convert]::ToBase64String($CollectorBytes)
        collector_sha256 = $CollectorSha256
        ephemeral_hmac_key_b64 = [Convert]::ToBase64String($EphemeralHmacKey)
    }
    $Bytes = ConvertTo-Phase13AuditCanonicalJsonBytes -Value $Envelope
    if ($Bytes.Length -gt $script:MaximumInputBytes) {
        [Array]::Clear($Bytes, 0, $Bytes.Length)
        throw "bounded audit input oversized"
    }
    return $Bytes
}

function New-Phase13AuditSshArguments {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("usa", "spain")][string]$Role,
        [Parameter(Mandatory = $true)]$RoleBinding
    )
    if ([string]$RoleBinding.TargetHost -cnotmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or
        [string]$RoleBinding.TargetUser -cnotmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "fixed target binding invalid"
    }
    $Bootstrap = 'import base64,hashlib,io,json,sys;e=json.load(sys.stdin);s=base64.b64decode(e["collector_b64"],validate=True);hashlib.sha256(s).hexdigest()==e["collector_sha256"] or sys.exit(70);k=e["ephemeral_hmac_key_b64"];sys.argv=["collector","--role",sys.argv[1]];sys.stdin=io.TextIOWrapper(io.BytesIO((k+"\n").encode("ascii")),encoding="ascii");exec(compile(s,"<collector>","exec"),{"__name__":"__main__"})'
    $RemoteCommand = "python3 -c '$Bootstrap' $Role"
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

function Write-Phase13AuditFailureOutcome {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][DateTimeOffset]$NowUtc,
        [Parameter(Mandatory = $true)][ValidateSet("audit_incomplete", "schema_validation_failed")][string]$ReasonCode
    )
    $Path = Join-Path $OutcomeRoot ("{0}.failure.json" -f $Binding.OutcomeId)
    $Failure = [ordered]@{
        checked_at = $NowUtc.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        decision = "stop"
        outcome_id = [string]$Binding.OutcomeId
        reason_code = $ReasonCode
        safety_receipt = [ordered]@{
            mutation_attempted = $false
            raw_output_persisted = $false
            secret_bearing_data_persisted = $false
        }
        schema = "amn2.phase13.bot-web-migration-failure.v1"
        stage = "audit"
    }
    Write-Phase13AuditCreateNewJson -Path $Path -Value $Failure
    return $Path
}

function Write-Phase13AuditSuccessOutcome {
    param(
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][DateTimeOffset]$NowUtc,
        [Parameter(Mandatory = $true)]$Evidence
    )
    $Path = Join-Path $OutcomeRoot ("{0}.success.json" -f $Binding.OutcomeId)
    $Success = [ordered]@{
        checked_at = $NowUtc.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        decision = "passed"
        evidence = $Evidence
        manifest_sha256 = [string]$Binding.ManifestSha256
        outcome_id = [string]$Binding.OutcomeId
        safety_receipt = [ordered]@{
            backup_created = $false
            data_transferred = $false
            db_applied = $false
            live_mutation_attempted = $false
            service_action_attempted = $false
        }
        schema = "amn2.phase13.bot-web-audit-outcome.v1"
    }
    Write-Phase13AuditCreateNewJson -Path $Path -Value $Success
    return $Path
}

function Invoke-Phase13ProductionAuditCore {
    param(
        [Parameter(Mandatory = $true)]$Binding,
        [Parameter(Mandatory = $true)][string]$OutcomeRoot,
        [Parameter(Mandatory = $true)][string]$SshExecutable,
        [string[]]$SshPrefixArguments = @(),
        [Parameter(Mandatory = $true)]$RoleBindings,
        [DateTimeOffset]$NowUtc = [DateTimeOffset]::UtcNow
    )
    $null = New-Phase13AuditOutcomeClaim -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc
    $Key = New-Phase13EphemeralHmacKey
    $EnvelopeBytes = $null
    try {
        $EnvelopeBytes = New-Phase13AuditTransportEnvelope -CollectorBytes $Binding.CollectorBytes -CollectorSha256 $Binding.CollectorSha256 -EphemeralHmacKey $Key
        $Documents = @{}
        $TransportFailed = $false
        foreach ($Role in @("usa", "spain")) {
            $Arguments = @($SshPrefixArguments) + @(New-Phase13AuditSshArguments -Role $Role -RoleBinding $RoleBindings[$Role])
            $Transport = Invoke-Phase13BoundedProcess -Executable $SshExecutable -Arguments $Arguments -InputBytes $EnvelopeBytes -TimeoutMilliseconds 60000 -MaximumOutputBytes 1048576
            if ($Transport.Reason -cne "success") {
                $TransportFailed = $true
                continue
            }
            try {
                $Documents[$Role] = $Transport.Document | ConvertFrom-Json -ErrorAction Stop
            } catch {
                $TransportFailed = $true
            }
        }
        if ($TransportFailed -or $Documents.Count -ne 2) {
            $FailurePath = Write-Phase13AuditFailureOutcome -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc -ReasonCode "audit_incomplete"
            return [pscustomobject]@{ OutcomePath = $FailurePath; Status = "failure" }
        }
        try {
            $SanitizedJson = ConvertTo-Phase13SanitizedAuditPair -UsaDocument $Documents["usa"] -SpainDocument $Documents["spain"]
            $Sanitized = $SanitizedJson | ConvertFrom-Json -ErrorAction Stop
        } catch {
            $FailurePath = Write-Phase13AuditFailureOutcome -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc -ReasonCode "schema_validation_failed"
            return [pscustomobject]@{ OutcomePath = $FailurePath; Status = "failure" }
        }
        $SuccessPath = Write-Phase13AuditSuccessOutcome -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc -Evidence $Sanitized
        return [pscustomobject]@{ OutcomePath = $SuccessPath; Status = "success" }
    } catch {
        try {
            $FailurePath = Write-Phase13AuditFailureOutcome -OutcomeRoot $OutcomeRoot -Binding $Binding -NowUtc $NowUtc -ReasonCode "audit_incomplete"
            return [pscustomobject]@{ OutcomePath = $FailurePath; Status = "failure" }
        } catch {
            throw "sanitized outcome write failed"
        }
    } finally {
        if ($null -ne $EnvelopeBytes) { [Array]::Clear($EnvelopeBytes, 0, $EnvelopeBytes.Length) }
        [Array]::Clear($Key, 0, $Key.Length)
    }
}

function ConvertTo-Phase13PublicAuditReceipt {
    param(
        [Parameter(Mandatory = $true)]$CoreResult,
        [Parameter(Mandatory = $true)][string]$OutcomeId
    )
    if ([string]$CoreResult.Status -cnotin @("success", "failure") -or
        $OutcomeId -cnotmatch '^[a-z0-9][a-z0-9-]{2,63}$') {
        throw "production audit result invalid"
    }
    return [ordered]@{
        decision = if ($CoreResult.Status -ceq "success") { "passed" } else { "stop" }
        outcome_id = $OutcomeId
        status = [string]$CoreResult.Status
    }
}

function Assert-Phase13AuditPrivatePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "private trust path unsafe"
    }
    $Acl = Get-Acl -LiteralPath $Item.FullName
    $OwnerSid = $Acl.Owner
    try { $OwnerSid = ([Security.Principal.NTAccount]$Acl.Owner).Translate([Security.Principal.SecurityIdentifier]).Value } catch { }
    if ($OwnerSid -cne $ExpectedOwnerSid -or -not $Acl.AreAccessRulesProtected) {
        throw "private trust path ACL invalid"
    }
    foreach ($Rule in $Acl.Access) {
        $RuleSid = $Rule.IdentityReference.Value
        try { $RuleSid = $Rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value } catch { }
        if ($Rule.IsInherited -or
            ($Rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and $RuleSid -cne $ExpectedOwnerSid)) {
            throw "private trust path ACL invalid"
        }
    }
}

function Protect-Phase13AuditOutcomeRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$OwnerSid
    )
    [void][IO.Directory]::CreateDirectory($Path)
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "private outcome root unsafe"
    }
    $Owner = New-Object Security.Principal.SecurityIdentifier($OwnerSid)
    $Acl = Get-Acl -LiteralPath $Item.FullName
    $Acl.SetOwner($Owner)
    $Acl.SetAccessRuleProtection($true, $false)
    foreach ($Rule in @($Acl.Access)) { [void]$Acl.RemoveAccessRuleAll($Rule) }
    $InheritanceFlags =
        [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
        [Security.AccessControl.InheritanceFlags]::ObjectInherit
    $Rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $Owner, [Security.AccessControl.FileSystemRights]::FullControl,
        $InheritanceFlags,
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )
    [void]$Acl.AddAccessRule($Rule)
    Set-Acl -LiteralPath $Item.FullName -AclObject $Acl
    Assert-Phase13AuditPrivatePath -Path $Item.FullName -ExpectedOwnerSid $OwnerSid
}

function Read-Phase13AuditFixedRoleBinding {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("usa", "spain")][string]$Role,
        [Parameter(Mandatory = $true)][string]$ExpectedOwnerSid,
        [Parameter(Mandatory = $true)][string]$SshKeygenExecutable
    )
    $Contract = Get-Phase13RoleTransportContract -Role $Role
    foreach ($Path in @($Contract.TrustRoot, $Contract.BindingPath, $Contract.KeyPath, $Contract.KnownHostsPath)) {
        Assert-Phase13AuditPrivatePath -Path $Path -ExpectedOwnerSid $ExpectedOwnerSid
    }
    $Lines = @(Get-Content -LiteralPath $Contract.BindingPath)
    $Names = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($Lines.Count -ne $Names.Count) { throw "private target binding invalid" }
    $Values = @{}
    for ($Index = 0; $Index -lt $Names.Count; $Index++) {
        $Prefix = "$($Names[$Index])="
        if (-not $Lines[$Index].StartsWith($Prefix, [StringComparison]::Ordinal)) {
            throw "private target binding invalid"
        }
        $Values[$Names[$Index]] = $Lines[$Index].Substring($Prefix.Length)
    }
    if ($Values["TARGET_HOST"] -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or
        $Values["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$' -or
        $Values["SSH_KEY_PATH"] -cne $Contract.KeyPath -or
        $Values["EXPECTED_HOST_KEY_SHA256"] -notmatch '^SHA256:[A-Za-z0-9+/]{43}$') {
        throw "private target binding invalid"
    }
    $HostLines = @(Get-Content -LiteralPath $Contract.KnownHostsPath)
    if ($HostLines.Count -ne 1 -or
        $HostLines[0] -notmatch '^([^ ]+) (ssh-ed25519|ecdsa-sha2-nistp256|rsa-sha2-(?:256|512)) ([A-Za-z0-9+/]+={0,2})$' -or
        $Matches[1] -cne $Values["TARGET_HOST"]) {
        throw "private host pin invalid"
    }
    $FingerprintOutput = @(& $SshKeygenExecutable -lf $Contract.KnownHostsPath 2>$null)
    $Observed = [regex]::Match(($FingerprintOutput -join " "), 'SHA256:[A-Za-z0-9+/]{43}').Value
    if ($LASTEXITCODE -ne 0 -or $Observed -cne $Values["EXPECTED_HOST_KEY_SHA256"]) {
        throw "private host pin invalid"
    }
    return [pscustomobject]@{
        KeyPath = $Contract.KeyPath
        KnownHostsPath = $Contract.KnownHostsPath
        TargetHost = $Values["TARGET_HOST"]
        TargetUser = $Values["TARGET_USER"]
    }
}

function Invoke-Phase13ProductionAudit {
    param(
        [string]$PackageRoot,
        [string]$ExactApprovalPhrase
    )
    if ([string]::IsNullOrEmpty($PackageRoot) -or [string]::IsNullOrEmpty($ExactApprovalPhrase)) {
        throw "production audit arguments required"
    }
    try {
        $Binding = Test-Phase13AuditToolingBinding -PackageRoot $PackageRoot -ExactApprovalPhrase $ExactApprovalPhrase
        $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $SshExecutable = "C:\Windows\System32\OpenSSH\ssh.exe"
        $SshKeygenExecutable = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"
        foreach ($Executable in @($SshExecutable, $SshKeygenExecutable)) {
            $Item = Get-Item -LiteralPath $Executable -Force -ErrorAction Stop
            if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "fixed transport executable invalid"
            }
        }
        $RoleBindings = @{
            usa = Read-Phase13AuditFixedRoleBinding -Role "usa" -ExpectedOwnerSid $CurrentSid -SshKeygenExecutable $SshKeygenExecutable
            spain = Read-Phase13AuditFixedRoleBinding -Role "spain" -ExpectedOwnerSid $CurrentSid -SshKeygenExecutable $SshKeygenExecutable
        }
        $OutcomeRoot = "C:\ProgramData\AMN2\private\phase13-bot-web-audit\outcomes"
        Protect-Phase13AuditOutcomeRoot -Path $OutcomeRoot -OwnerSid $CurrentSid
        $CoreResult = Invoke-Phase13ProductionAuditCore -Binding $Binding -OutcomeRoot $OutcomeRoot -SshExecutable $SshExecutable -RoleBindings $RoleBindings
        return ConvertTo-Phase13PublicAuditReceipt -CoreResult $CoreResult -OutcomeId $Binding.OutcomeId
    } catch {
        throw "production audit failed closed"
    }
}
