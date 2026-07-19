[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("prepare-key", "write-binding", "verify-pin", "print-public-key")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [string]$ArtifactRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Import-Module (Join-Path $PSHOME "Modules\Microsoft.PowerShell.Security") -ErrorAction Stop

$DefaultRelativeRoot = "private-artifacts/post-release/spain-migration"
$SshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$SshKeygenExe = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"
$IcaclsExe = "C:\Windows\System32\icacls.exe"

if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$' -or $RunId.Contains("..")) {
    throw "RunId has an invalid format."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DefaultArtifactRoot = Join-Path $RepoRoot ($DefaultRelativeRoot.Replace("/", [IO.Path]::DirectorySeparatorChar))
$AllowLocalOverrides = $env:AMN2_SPAIN_TEST_ALLOW_LOCAL_OVERRIDES -eq "1"
$UsesTestArtifactRoot = [bool]$ArtifactRoot
if ($ArtifactRoot) {
    if (-not $AllowLocalOverrides) {
        throw "ArtifactRoot override is reserved for isolated local tests."
    }
    $ArtifactRoot = [IO.Path]::GetFullPath($ArtifactRoot)
    $SystemTempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not ($ArtifactRoot.TrimEnd('\') + '\').StartsWith($SystemTempRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "ArtifactRoot override must remain inside the system temporary directory."
    }
} else {
    $ArtifactRoot = $DefaultArtifactRoot
}

if ($AllowLocalOverrides -and $UsesTestArtifactRoot -and $env:AMN2_SPAIN_TEST_SSH_KEYGEN_EXE) {
    $SshKeygenExe = [IO.Path]::GetFullPath($env:AMN2_SPAIN_TEST_SSH_KEYGEN_EXE)
}

$RunDirectory = Join-Path $ArtifactRoot $RunId
$KeyPath = Join-Path $RunDirectory "id_ed25519_spain"
$PublicKeyPath = "$KeyPath.pub"
$KnownHostsPath = Join-Path $RunDirectory "known_hosts_spain"
$BindingPath = Join-Path $RunDirectory "target.env"

# Task 8 consumes this exact fail-closed option contract. This onboarding script
# deliberately never invokes ssh.exe.
$HardenedSshArguments = @(
    "-F", "none",
    "-o", "BatchMode=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "UserKnownHostsFile=$KnownHostsPath",
    "-i", $KeyPath
)

function Assert-LocalExecutable([string]$Path, [string]$Label) {
    if (-not [IO.Path]::IsPathRooted($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label executable is unavailable at its required absolute path."
    }
}

function Protect-PrivatePath([string]$Path) {
    Assert-LocalExecutable $IcaclsExe "ACL"
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $Arguments = @($Path, "/inheritance:r", "/grant:r", "${Identity}:F")
    & $IcaclsExe @Arguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "ACL hardening failed."
    }
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Acl = Get-Acl -LiteralPath $Path
    $Acl.SetAccessRuleProtection($true, $false)
    foreach ($ExistingRule in @($Acl.Access)) {
        $Acl.RemoveAccessRuleSpecific($ExistingRule)
    }
    if (Test-Path -LiteralPath $Path -PathType Container) {
        $Inheritance = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
    } else {
        $Inheritance = [Security.AccessControl.InheritanceFlags]::None
    }
    $Rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $CurrentSid,
        [Security.AccessControl.FileSystemRights]::FullControl,
        $Inheritance,
        [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Allow
    )
    $Acl.SetAccessRule($Rule)
    Set-Acl -LiteralPath $Path -AclObject $Acl
    Assert-PrivatePath $Path
}

function Assert-PrivatePath([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required private artifact is missing."
    }
    $CurrentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $VerifiedAcl = Get-Acl -LiteralPath $Path
    $VerifiedRules = @($VerifiedAcl.Access)
    if (-not $VerifiedAcl.AreAccessRulesProtected -or $VerifiedRules.Count -ne 1 -or
        $VerifiedRules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value -cne $CurrentSid.Value -or
        $VerifiedRules[0].AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
        (($VerifiedRules[0].FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne [Security.AccessControl.FileSystemRights]::FullControl)) {
        throw "ACL verification did not prove current-user-only access."
    }
}

function Assert-DedicatedKeyPair {
    Assert-LocalExecutable $SshKeygenExe "OpenSSH key generator"
    $DerivedLines = @(& $SshKeygenExe -y -f $KeyPath 2>$null)
    if ($LASTEXITCODE -ne 0 -or $DerivedLines.Count -ne 1) {
        throw "Dedicated Spain private key is invalid."
    }
    $DerivedMatch = [regex]::Match($DerivedLines[0].Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})$')
    $PublicText = Get-Content -LiteralPath $PublicKeyPath -Raw
    $PublicMatch = [regex]::Match($PublicText.Trim(), '^ssh-ed25519 ([A-Za-z0-9+/]+={0,2})(?: [^\r\n]+)?$')
    if (-not $DerivedMatch.Success -or -not $PublicMatch.Success -or $DerivedMatch.Groups[1].Value -cne $PublicMatch.Groups[1].Value) {
        throw "Dedicated Spain key files are not a matching Ed25519 pair."
    }
}

function Initialize-RunDirectory {
    [IO.Directory]::CreateDirectory($RunDirectory) | Out-Null
    Protect-PrivatePath $RunDirectory
}

function Read-PrivateValue([string]$EnvironmentName, [string]$Prompt) {
    $Value = [Environment]::GetEnvironmentVariable($EnvironmentName)
    if ($null -ne $Value -and $Value.Length -gt 0) {
        return $Value
    }
    $SecureValue = Read-Host -Prompt $Prompt -AsSecureString
    $Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureValue)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer)
    }
}

function Assert-TargetHost([string]$Value) {
    if ($Value -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9.:-]{0,252}[A-Za-z0-9])?$' -or $Value.Contains("..")) {
        throw "Target host has an invalid format."
    }
}

function Assert-TargetUser([string]$Value) {
    if ($Value -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
        throw "Target user has an invalid format."
    }
}

function Assert-Fingerprint([string]$Value) {
    if ($Value -notmatch '^SHA256:[A-Za-z0-9+/]{43}$') {
        throw "Host-key fingerprint has an invalid format."
    }
}

function Read-Binding {
    if (-not (Test-Path -LiteralPath $BindingPath -PathType Leaf)) {
        throw "Private target binding is missing."
    }
    $Lines = @(Get-Content -LiteralPath $BindingPath)
    $ExpectedNames = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($Lines.Count -ne $ExpectedNames.Count) {
        throw "Private target binding must contain exactly four lines."
    }
    $Binding = @{}
    for ($Index = 0; $Index -lt $ExpectedNames.Count; $Index++) {
        $Prefix = "$($ExpectedNames[$Index])="
        if (-not $Lines[$Index].StartsWith($Prefix)) {
            throw "Private target binding has an invalid schema."
        }
        $Binding[$ExpectedNames[$Index]] = $Lines[$Index].Substring($Prefix.Length)
    }
    Assert-TargetHost $Binding["TARGET_HOST"]
    Assert-TargetUser $Binding["TARGET_USER"]
    Assert-Fingerprint $Binding["EXPECTED_HOST_KEY_SHA256"]
    if ($Binding["SSH_KEY_PATH"] -cne $KeyPath) {
        throw "Private target binding is not bound to the dedicated Spain key."
    }
    return $Binding
}

switch ($Mode) {
    "prepare-key" {
        Initialize-RunDirectory
        if ((Test-Path -LiteralPath $KeyPath) -or (Test-Path -LiteralPath $PublicKeyPath)) {
            throw "Dedicated Spain key already exists."
        }
        Assert-LocalExecutable $SshKeygenExe "OpenSSH key generator"
        & $SshKeygenExe -t ed25519 -f $KeyPath -C "AMN2 Spain dedicated operator key" -N ""
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $KeyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $PublicKeyPath -PathType Leaf)) {
            throw "Dedicated Spain key generation failed."
        }
        Protect-PrivatePath $KeyPath
        Protect-PrivatePath $PublicKeyPath
        Assert-DedicatedKeyPair
        Assert-PrivatePath $RunDirectory
        Assert-PrivatePath $KeyPath
        Assert-PrivatePath $PublicKeyPath
        Write-Output "Dedicated Spain key prepared locally."
    }
    "write-binding" {
        $TargetHost = Read-PrivateValue "AMN2_SPAIN_TARGET_HOST" "Spain target host"
        $TargetUser = Read-PrivateValue "AMN2_SPAIN_TARGET_USER" "Spain target user"
        $ExpectedFingerprint = Read-PrivateValue "AMN2_SPAIN_EXPECTED_HOST_KEY_SHA256" "Expected host-key SHA-256 fingerprint"
        Assert-TargetHost $TargetHost
        Assert-TargetUser $TargetUser
        Assert-Fingerprint $ExpectedFingerprint
        Initialize-RunDirectory
        if (-not (Test-Path -LiteralPath $KeyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $PublicKeyPath -PathType Leaf)) {
            throw "Dedicated Spain key pair must be prepared before binding."
        }
        if ((Test-Path -LiteralPath $BindingPath) -or (Test-Path -LiteralPath $KnownHostsPath)) {
            throw "Existing binding or verified pin must not be overwritten."
        }
        Protect-PrivatePath $KeyPath
        Protect-PrivatePath $PublicKeyPath
        Assert-DedicatedKeyPair
        $Lines = @(
            "TARGET_HOST=$TargetHost",
            "TARGET_USER=$TargetUser",
            "SSH_KEY_PATH=$KeyPath",
            "EXPECTED_HOST_KEY_SHA256=$ExpectedFingerprint"
        )
        $Utf8WithoutBom = New-Object Text.UTF8Encoding($false)
        [IO.File]::WriteAllLines($BindingPath, $Lines, $Utf8WithoutBom)
        Protect-PrivatePath $BindingPath
        Assert-PrivatePath $RunDirectory
        Assert-PrivatePath $KeyPath
        Assert-PrivatePath $PublicKeyPath
        Assert-PrivatePath $BindingPath
        Write-Output "Private target binding written locally."
    }
    "verify-pin" {
        if (Test-Path -LiteralPath $KnownHostsPath) {
            throw "Verified Spain host pin already exists."
        }
        if (-not (Test-Path -LiteralPath $KeyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $PublicKeyPath -PathType Leaf)) {
            throw "Dedicated Spain key pair is incomplete."
        }
        Assert-PrivatePath $RunDirectory
        Assert-PrivatePath $BindingPath
        Assert-PrivatePath $KeyPath
        Assert-PrivatePath $PublicKeyPath
        Assert-DedicatedKeyPair
        $Binding = Read-Binding
        $HostKeyLine = Read-PrivateValue "AMN2_SPAIN_HOST_KEY_LINE" "Out-of-band host public key line"
        if ($HostKeyLine -match '[\r\n]' -or $HostKeyLine -notmatch '^(ssh-ed25519|ecdsa-sha2-nistp256|rsa-sha2-(?:256|512)) ([A-Za-z0-9+/]+={0,2})$') {
            throw "Host public key line has an invalid format."
        }
        $CandidatePath = Join-Path $RunDirectory "known_hosts_spain.candidate"
        try {
            Set-Content -LiteralPath $CandidatePath -Value "$($Binding['TARGET_HOST']) $HostKeyLine" -Encoding ASCII
            Protect-PrivatePath $CandidatePath
            Assert-LocalExecutable $SshKeygenExe "OpenSSH key generator"
            $FingerprintOutput = & $SshKeygenExe -lf $CandidatePath 2>$null
            if ($LASTEXITCODE -ne 0) {
                throw "Local host-key fingerprint calculation failed."
            }
            $Observed = [regex]::Match(($FingerprintOutput -join " "), 'SHA256:[A-Za-z0-9+/]{43}').Value
            if (-not $Observed -or $Observed -cne $Binding["EXPECTED_HOST_KEY_SHA256"]) {
                throw "Host-key fingerprint does not match the independently recorded pin."
            }
            [IO.File]::Move($CandidatePath, $KnownHostsPath)
            Protect-PrivatePath $KnownHostsPath
            Assert-PrivatePath $RunDirectory
            Assert-PrivatePath $BindingPath
            Assert-PrivatePath $KeyPath
            Assert-PrivatePath $PublicKeyPath
            Assert-PrivatePath $KnownHostsPath
            Write-Output "Independent host-key pin verified locally."
        } finally {
            if (Test-Path -LiteralPath $CandidatePath) {
                Remove-Item -LiteralPath $CandidatePath -Force
            }
        }
    }
    "print-public-key" {
        if (-not (Test-Path -LiteralPath $PublicKeyPath -PathType Leaf)) {
            throw "Dedicated Spain public key is missing."
        }
        Assert-PrivatePath $RunDirectory
        Assert-PrivatePath $KeyPath
        Assert-PrivatePath $PublicKeyPath
        Assert-DedicatedKeyPair
        Get-Content -LiteralPath $PublicKeyPath -Raw
    }
}
