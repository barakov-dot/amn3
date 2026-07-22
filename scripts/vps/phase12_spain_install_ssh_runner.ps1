[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sourceRevision = "55dc243b8e6c6bdb57f8301b56326e4cd4072d19"
$expectedPackageSha = "EA633C4B41A2FF86369485564BDF8E6F0B7AB7E3D74CA1D019B2F9879AF414E3"
$expectedPackageBytes = 139929600
$expectedManifestSha = "1762D40FD59F7B6952278BAE2E998BE370845D9BBAAA4C14772D0CACF9460C33"
$expectedPlanSha = "8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43"
$expectedExecutorSha = "676B2BFF9A25EBCBEE524816D4B3A461260789D8EF270D0AD93F90848C2B49E6"
$expectedExecutorBytes = 139019
$expectedCollectorSha = "70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A"
$run009EvidenceSha = "8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8"
$fingerprintArraySha = "E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5"
$expectedMachineSha = "3C3233534FD3B69280AAAD4E977A08E30409729D684B816E73C01DDBA24397F5"
$expectedBootSha = "099155E2A5578144C715124A1B9B4D8F5D572134C8F72FD98B75D5DE0EB54556"
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$artifactRoot = Join-Path $repoRoot "private-artifacts\phase12-spain-install-boundary-final-20260722"
$packagePath = Join-Path $artifactRoot "amn2-spain-phase12-install-a.tar"
$executorPath = Join-Path $artifactRoot "amn2-spain-phase12-executor-a.pyz"
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$scpExe = "C:\Windows\System32\OpenSSH\scp.exe"

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($Value)))).Replace("-", "")
    } finally { $hasher.Dispose() }
}

function ConvertTo-Hex([byte[]]$Bytes) {
    return ([BitConverter]::ToString($Bytes)).Replace("-", "")
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-ExactSsh([string[]]$Arguments, [byte[]]$InputBytes) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $info.UseShellExecute = $false
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "SSH process did not start." }
    try {
        $process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length)
        $process.StandardInput.BaseStream.Flush()
        $process.StandardInput.Close()
        $stdout = [IO.MemoryStream]::new(); $stderr = [IO.MemoryStream]::new()
        try {
            $process.StandardOutput.BaseStream.CopyTo($stdout)
            $process.StandardError.BaseStream.CopyTo($stderr)
            $process.WaitForExit()
            return [pscustomobject]@{ ExitCode=$process.ExitCode; Stdout=$stdout.ToArray(); Stderr=$stderr.ToArray() }
        } finally { $stdout.Dispose(); $stderr.Dispose() }
    } finally { $process.Dispose() }
}

function Read-PrivateBinding([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Private target binding unavailable." }
    $values = @{}
    foreach ($line in @(Get-Content -LiteralPath $Path)) {
        if ($line -notmatch '^([A-Z0-9_]+)=([^\r\n]+)$') { throw "Private target binding format invalid." }
        if ($values.ContainsKey($Matches[1])) { throw "Private target binding duplicate key." }
        $values[$Matches[1]] = $Matches[2]
    }
    $expected = @("TARGET_HOST", "TARGET_USER", "SSH_KEY_PATH", "EXPECTED_HOST_KEY_SHA256")
    if ($values.Count -ne $expected.Count -or @($expected | Where-Object { -not $values.ContainsKey($_) }).Count -ne 0) { throw "Private target binding key set invalid." }
    if ($values["TARGET_HOST"] -notmatch '^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$' -or $values["TARGET_HOST"].Contains("..")) { throw "Private target host invalid." }
    if ($values["TARGET_USER"] -notmatch '^[a-z_][a-z0-9_-]{0,31}$') { throw "Private target user invalid." }
    if ($values["EXPECTED_HOST_KEY_SHA256"] -notmatch '^SHA256:[A-Za-z0-9+/=]+$') { throw "Private host pin invalid." }
    return $values
}

foreach ($path in @($packagePath, $executorPath, $sshExe, $scpExe)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required local artifact is unavailable." }
}
if ((Get-Item -LiteralPath $packagePath).Length -ne $expectedPackageBytes -or (Get-FileHash -LiteralPath $packagePath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedPackageSha) { throw "Package checksum/size mismatch." }
if ((Get-Item -LiteralPath $executorPath).Length -ne $expectedExecutorBytes -or (Get-FileHash -LiteralPath $executorPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedExecutorSha) { throw "Executor checksum/size mismatch." }

$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"
$keyPath = Join-Path $privateRoot "id_ed25519_spain"
$knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }
$runnerApproval = "APPROVE PHASE12 SPAIN CHECKSUM BOUND INSTALL RUNNER SHA256 $expectedRunnerSha PACKAGE SHA256 $expectedPackageSha PACKAGE BYTES $expectedPackageBytes MANIFEST SHA256 $expectedManifestSha RESOURCE PLAN SHA256 $expectedPlanSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes COLLECTOR SHA256 $expectedCollectorSha SOURCE $sourceRevision RUN009 EVIDENCE SHA256 $run009EvidenceSha FINGERPRINT ARRAY SHA256 $fingerprintArraySha DYNAMIC FOREIGN EQUALITY PERSISTENT REQUIRED VOLATILE RECORDED EXACT PRIVATE TARGET DEDICATED ED25519 KEY INDEPENDENT HOST PIN STDIN ONLY UPLOAD PACKAGE EXECUTOR REMOTE HASH VERIFY INSTALL BOUND AUTOMATIC ROLLBACK NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact install approval mismatch." }

$sshBase = @("-F", "none", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath, "-p", "22")
$target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
& $scpExe @sshBase $packagePath $executorPath "${target}:/root/"
if ($LASTEXITCODE -ne 0) { throw "Approved artifact upload failed." }
$hashResult = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum /root/amn2-spain-phase12-install-a.tar /root/amn2-spain-phase12-executor-a.pyz"))) ([byte[]]@())
if ($hashResult.ExitCode -ne 0) { throw "Remote artifact hash command failed." }
$hashText = (New-Object Text.UTF8Encoding($false,$true)).GetString($hashResult.Stdout)
if ($hashText -notmatch "(?im)^$($expectedPackageSha.ToLowerInvariant())  /root/amn2-spain-phase12-install-a\.tar$" -or $hashText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  /root/amn2-spain-phase12-executor-a\.pyz$") { throw "Remote artifact checksum mismatch." }
& $sshExe @sshBase $target "mv -f /root/amn2-spain-phase12-install-a.tar /root/amn2-spain-phase12-install.tar && mv -f /root/amn2-spain-phase12-executor-a.pyz /root/amn2-spain-phase12-executor.pyz"
if ($LASTEXITCODE -ne 0) { throw "Remote artifact activation failed." }
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$nonceBytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($nonceBytes)
$nonce = (ConvertTo-Hex $nonceBytes).ToLowerInvariant()
[Array]::Clear($nonceBytes, 0, $nonceBytes.Length)
$intent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; collector_sha256=$expectedCollectorSha.ToLowerInvariant(); endpoint_host=$binding['TARGET_HOST']; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expected_boot_id_sha256=$expectedBootSha.ToLowerInvariant(); expected_host_identity_sha256=$expectedMachineSha.ToLowerInvariant(); expires_at_epoch=($now + 300); fingerprint_array_sha256=$fingerprintArraySha.ToLowerInvariant(); mutation_authorized=$true; nonce=$nonce; package_archive_sha256=$expectedPackageSha.ToLowerInvariant(); package_archive_size=$expectedPackageBytes; package_manifest_sha256=$expectedManifestSha.ToLowerInvariant(); resource_plan_sha256=$expectedPlanSha.ToLowerInvariant(); run009_evidence_sha256=$run009EvidenceSha.ToLowerInvariant(); schema="amn2.spain-install-boundary-intent.v1" }
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$installResult = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B /root/amn2-spain-phase12-executor.pyz install-bound"))) $intentBytes
if ($installResult.ExitCode -ne 0) { throw "Install-bound failed; remote executor is responsible for automatic rollback." }
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($installResult.Stdout))
