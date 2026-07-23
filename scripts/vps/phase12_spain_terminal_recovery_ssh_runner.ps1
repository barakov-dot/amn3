[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "400A46C60CEE775303FCEEC2BDD297D5373D721F0C6F9BACF5449D68700126A5"
$expectedExecutorBytes = 144591
$expectedNonce = "e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd"
$expectedTransactionSha = "c58ed7ec5ea40f47c7c65c4a6d4691667160f2444764679a285a9ee47bec8788"
$expectedCapsuleSha = "fe7e203b3a772811489371c90cab88e0247882882938045fd85d80709f6b63cc"
$expectedDockerTreeSha = "2328da44bf2bdf6fd831a1aa27b50df5bce8649fbbef015808a01ccd389a1cf4"
$expectedDockerTreeEntries = 916
$expectedDockerTreeBytes = 41902300
$expectedBlockRdev = 64770
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$artifactRoot = Join-Path $repoRoot "private-artifacts\phase12-spain-terminal-recovery-v2-20260723"
$executorPath = Join-Path $artifactRoot "executor-k.pyz"
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$scpExe = "C:\Windows\System32\OpenSSH\scp.exe"

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($Value)))).Replace("-", "") } finally { $hasher.Dispose() }
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
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $info
    if (-not $process.Start()) { throw "SSH process did not start." }
    try {
        $stdout = [IO.MemoryStream]::new(); $stderr = [IO.MemoryStream]::new()
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $process.StandardInput.BaseStream.Write($InputBytes, 0, $InputBytes.Length)
        $process.StandardInput.BaseStream.Flush(); $process.StandardInput.Close()
        try {
            $process.WaitForExit(); [Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
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

foreach ($path in @($executorPath, $sshExe, $scpExe)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required local artifact is unavailable." }
}
if ((Get-Item -LiteralPath $executorPath).Length -ne $expectedExecutorBytes -or (Get-FileHash -LiteralPath $executorPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedExecutorSha) { throw "Executor checksum/size mismatch." }

$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"; $keyPath = Join-Path $privateRoot "id_ed25519_spain"; $knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }
$runnerApproval = "APPROVE PHASE12 SPAIN TERMINAL RECOVERY RECEIPT RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha DOCKER TREE SHA256 $expectedDockerTreeSha ENTRIES $expectedDockerTreeEntries BYTES $expectedDockerTreeBytes RECORDED BLOCK RDEV $expectedBlockRdev SINGLE FILESYSTEM NO NESTED MOUNTS VERIFY RECORDED REMOVAL ONLY NO ADDITIONAL AMN2 MUTATION PRESERVE TERMINAL LEDGER NO AMN2 START NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact terminal recovery approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath)
$sshBase = @($transportOptions + @("-p", "22")); $scpBase = @($transportOptions + @("-P", "22")); $target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteHash = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum /root/amn2-spain-phase12-executor.pyz"))) ([byte[]]@())
$remoteText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteHash.Stdout)
if ($remoteHash.ExitCode -ne 0 -or $remoteText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  /root/amn2-spain-phase12-executor\.pyz$") {
    & $scpExe @scpBase $executorPath "${target}:/root/amn2-spain-phase12-terminal-recovery-executor.pyz"
    if ($LASTEXITCODE -ne 0) { throw "Approved terminal recovery executor upload failed." }
    $uploadedHash = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum /root/amn2-spain-phase12-terminal-recovery-executor.pyz"))) ([byte[]]@())
    $uploadedText = (New-Object Text.UTF8Encoding($false,$true)).GetString($uploadedHash.Stdout)
    if ($uploadedHash.ExitCode -ne 0 -or $uploadedText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  /root/amn2-spain-phase12-terminal-recovery-executor\.pyz$") { throw "Remote terminal recovery executor checksum mismatch." }
    $activation = Invoke-ExactSsh (@($sshBase + @($target, "mv -f /root/amn2-spain-phase12-terminal-recovery-executor.pyz /root/amn2-spain-phase12-executor.pyz"))) ([byte[]]@())
    if ($activation.ExitCode -ne 0) { throw "Remote terminal recovery executor activation failed." }
}
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{ approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; capsule_sha256=$expectedCapsuleSha; docker_tree_entry_count=$expectedDockerTreeEntries; docker_tree_sha256=$expectedDockerTreeSha; docker_tree_total_bytes=$expectedDockerTreeBytes; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now + 300); mutation_authorized=$true; nonce=$expectedNonce; schema="amn2.spain-terminal-recovery-intent.v1"; transaction_sha256=$expectedTransactionSha }
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress) + "`n")
$result = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B /root/amn2-spain-phase12-executor.pyz terminal-recovery-receipt-bound"))) $intentBytes
if ($result.ExitCode -ne 0) {
    $safeRemoteError = (New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stderr).Trim()
    if (-not [string]::IsNullOrWhiteSpace($safeRemoteError)) { [Console]::Error.WriteLine($safeRemoteError) }
    throw "Terminal recovery receipt failed; recorded removal was not safely verified."
}
[Console]::WriteLine((New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stdout))
