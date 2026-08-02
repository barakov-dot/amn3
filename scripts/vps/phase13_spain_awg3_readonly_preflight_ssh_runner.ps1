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
    Protect-Phase13PrivateDirectory -Path $OutcomeRoot -OwnerSid $OwnerSid
    $OutcomeDirectory = Join-Path $OutcomeRoot $OutcomeId
    if (Test-Path -LiteralPath $OutcomeDirectory) {
        throw "Outcome claim already exists."
    }
    [IO.Directory]::CreateDirectory($OutcomeDirectory) | Out-Null
    Protect-Phase13PrivateDirectory -Path $OutcomeDirectory -OwnerSid $OwnerSid
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

function ConvertTo-ProcessArgumentString {
    param([string[]]$Arguments)
    $Quoted = foreach ($Argument in $Arguments) {
        if ($Argument -notmatch '[\s"]') { $Argument }
        else { '"' + ($Argument -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"' }
    }
    return ($Quoted -join ' ')
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
    if (-not $Process.Start()) { throw "Transport process could not start." }
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
            StdoutBytes = $Stdout.ToArray()
            StderrBytes = $Stderr.ToArray()
            MaximumOutputBytes = $MaximumOutputBytes
        }
    } finally {
        $Process.Dispose()
        $Stdout.Dispose()
        $Stderr.Dispose()
    }
}

function ConvertFrom-BoundedCollectorEnvelope {
    param([Parameter(Mandatory = $true)]$Transport)
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
    $PythonCode = "sys=__import__('sys');Path=__import__('pathlib',fromlist=['Path']).Path;sys.path.insert(0,sys.argv[1]);c=__import__('phase13_awg3_preflight_contract');raw_m=Path(sys.argv[2]).read_bytes();m=c.load_json_object_strict(raw_m,label='manifest');c.validate_manifest(m,artifact_root=Path(sys.argv[3]));raw=sys.stdin.buffer.read();e=c.load_json_object_strict(raw,label='evidence');c.validate_success_evidence(e,manifest=m);sys.stdout.buffer.write(b'passed\n')"
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
        [Parameter(Mandatory = $true)][string]$ReasonCode
    )
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
        schema = "amn2.phase13.awg3-readonly-preflight-failure.v1"
        source_head = $script:SourceHead
        stage = $Stage
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
        [void](New-Phase13OutcomeClaim -OutcomeRoot $OutcomeRoot -OutcomeId $OutcomeId -OwnerSid $CurrentSid -ManifestSha256 $ManifestSha -RunnerSha256 $RunnerSha -CollectorSha256 $CollectorSha -TargetRole "spain-primary")
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

    # Production transport remains unreachable until the separately approved
    # one-SSH transport and sanitized observation binding are implemented.
    Write-RunnerFailureLine "trust_binding" "runtime_capability_unavailable"
    return 73
}

if ($MyInvocation.InvocationName -ne '.') {
    $ExitCode = Invoke-RunnerMain -Mode $Mode -OutcomeId $OutcomeId -Approval $Approval
    exit $ExitCode
}
