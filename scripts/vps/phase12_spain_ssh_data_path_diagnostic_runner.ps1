[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$probeBytes = 16777216
$timeoutMilliseconds = 60000
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
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

function Invoke-BoundedSshProbe([string[]]$Arguments) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "Approved data-path diagnostic did not start." }
    $payload = [byte[]]::new($probeBytes)
    $input = [IO.MemoryStream]::new($payload, $false)
    $timedOut = $false
    try {
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        $deadline = [Diagnostics.Stopwatch]::StartNew()
        $copyTask = $input.CopyToAsync($process.StandardInput.BaseStream)
        if (-not $copyTask.Wait($timeoutMilliseconds)) {
            $timedOut = $true
            throw "Approved data-path diagnostic exceeded 60 seconds."
        }
        $copyTask.GetAwaiter().GetResult()
        $process.StandardInput.Close()
        $remaining = [Math]::Max(0, $timeoutMilliseconds - [int]$deadline.ElapsedMilliseconds)
        if (-not $process.WaitForExit([int]$remaining)) {
            $timedOut = $true
            throw "Approved data-path diagnostic exceeded 60 seconds."
        }
        [Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
        if ($process.ExitCode -ne 0) { throw "Approved data-path diagnostic failed." }
        return [pscustomobject]@{ ElapsedMilliseconds=[int]$deadline.ElapsedMilliseconds; Bytes=$probeBytes }
    } catch {
        if ($timedOut) { throw }
        throw "Approved data-path diagnostic failed."
    } finally {
        if (-not $process.HasExited) {
            try { $process.Kill($true) } catch { }
            $process.WaitForExit()
        }
        $input.Dispose()
        [Array]::Clear($payload, 0, $payload.Length)
        $process.Dispose()
    }
}

if (-not (Test-Path -LiteralPath $sshExe -PathType Leaf)) { throw "Required local SSH executable is unavailable." }
$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"
$keyPath = Join-Path $privateRoot "id_ed25519_spain"
$knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }
$runnerApproval = "APPROVE PHASE12 SPAIN SSH DATA PATH DIAGNOSTIC RUNNER SHA256 $expectedRunnerSha PROBE BYTES $probeBytes TIMEOUT SECONDS 60 EXACT PRIVATE TARGET DEDICATED ED25519 KEY INDEPENDENT HOST PIN STDIN ONLY DEV NULL NO REMOTE FILE WRITE NO INSTALL NO AMN2 START NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact data-path diagnostic approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "Compression=no", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath, "-p", "22")
$target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$probeArguments = @($transportOptions + @($target, "exec /bin/cat > /dev/null"))
$probeResults = @(Invoke-BoundedSshProbe $probeArguments)
$probeReceipts = @($probeResults | Where-Object {
    $null -ne $_.PSObject.Properties["Bytes"] -and
    $null -ne $_.PSObject.Properties["ElapsedMilliseconds"]
})
if ($probeReceipts.Count -ne 1) { throw "Approved data-path diagnostic result invalid." }
$result = $probeReceipts[0]
$bytesPerSecond = [Math]::Floor(($result.Bytes * 1000.0) / [Math]::Max(1, $result.ElapsedMilliseconds))
[Console]::WriteLine(([ordered]@{ schema="amn2.spain-ssh-data-path-diagnostic.v1"; result="passed"; probe_bytes=$result.Bytes; elapsed_milliseconds=$result.ElapsedMilliseconds; bytes_per_second=[int64]$bytesPerSecond; persistent_remote_write=$false; amn2_started=$false; foreign_service_mutation=$false } | ConvertTo-Json -Compress))
