Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:MaximumTimeoutMilliseconds = 60000
$script:MaximumOutputBytes = 1048576
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
        $InputBytes.Length -gt 4096) {
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
        [string]$Audit.checked_at -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$' -or
        [string]$Audit.database.schema_sha256 -notmatch '^[0-9a-f]{64}$' -or
        [string]$Audit.database.counts_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $Audit.database.foreign_key_violations -lt 0 -or
        $Audit.database.table_count -lt 0 -or
        $Audit.safety_receipt.mutation_attempted -ne $false -or
        $Audit.safety_receipt.raw_output_persisted -ne $false -or
        $Audit.safety_receipt.secret_bearing_data_persisted -ne $false) {
        throw "audit projection invalid"
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
    $UsaAudit = ConvertTo-Phase13CanonicalAudit -Audit $UsaDocument.audit -ExpectedRole "usa-source"
    $SpainAudit = ConvertTo-Phase13CanonicalAudit -Audit $SpainDocument.audit -ExpectedRole "spain-target"
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
