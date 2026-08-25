[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$RemoteScriptPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$expectedHost = '138.124.181.246'
$expectedHostKeySha256 = 'SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU'
$trustRoot = Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)) 'AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001'
$keyPath = Join-Path $trustRoot 'id_ed25519_spain'
$knownHostsPath = Join-Path $trustRoot 'known_hosts_spain'
$sshPath = 'C:\Windows\System32\OpenSSH\ssh.exe'
$maximumScriptBytes = 65536
$maximumOutputChars = 65536

function ConvertTo-WindowsArgument {
    param([Parameter(Mandatory)][string]$Value)
    return '"' + $Value.Replace('"', '\"') + '"'
}

foreach ($path in @($sshPath, $keyPath, $knownHostsPath, $RemoteScriptPath)) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.Length -lt 1) {
        throw 'local_input_invalid'
    }
}

$knownHostsBytes = [IO.File]::ReadAllBytes($knownHostsPath)
try {
    if ($knownHostsBytes.Length -gt 4096 -or @($knownHostsBytes | Where-Object { $_ -gt 127 }).Count -ne 0) {
        throw 'trust_binding_invalid'
    }
    $knownHostsText = [Text.ASCIIEncoding]::new().GetString($knownHostsBytes)
    $match = [regex]::Match($knownHostsText, '^([^ \r\n]+) (ssh-ed25519) ([A-Za-z0-9+/]+={0,2})\r?\n$')
    if (-not $match.Success -or $match.Groups[1].Value -cne $expectedHost) {
        throw 'trust_binding_invalid'
    }
    $blob = [Convert]::FromBase64String($match.Groups[3].Value)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $digest = $algorithm.ComputeHash($blob) } finally { $algorithm.Dispose() }
    $fingerprint = 'SHA256:' + [Convert]::ToBase64String($digest).TrimEnd('=')
    if ($fingerprint -cne $expectedHostKeySha256) { throw 'trust_binding_invalid' }
} finally {
    [Array]::Clear($knownHostsBytes, 0, $knownHostsBytes.Length)
}

$remoteBytes = [IO.File]::ReadAllBytes($RemoteScriptPath)
try {
    if ($remoteBytes.Length -lt 1 -or $remoteBytes.Length -gt $maximumScriptBytes) { throw 'remote_script_invalid' }
    if ($remoteBytes.Length -ge 3 -and $remoteBytes[0] -eq 239 -and $remoteBytes[1] -eq 187 -and $remoteBytes[2] -eq 191) {
        throw 'remote_script_bom_invalid'
    }
    $hashAlgorithm = [Security.Cryptography.SHA256]::Create()
    try { $remoteSha256 = ([BitConverter]::ToString($hashAlgorithm.ComputeHash($remoteBytes))).Replace('-', '').ToLowerInvariant() } finally { $hashAlgorithm.Dispose() }

    $arguments = @(
        '-T','-F','none',
        '-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','IdentityAgent=none',
        '-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no','-o','GSSAPIAuthentication=no',
        '-o','ForwardAgent=no','-o','ClearAllForwardings=yes','-o','RequestTTY=no',
        '-o','StrictHostKeyChecking=yes','-o',"UserKnownHostsFile=$knownHostsPath",
        '-o','GlobalKnownHostsFile=NUL','-o','ConnectTimeout=10','-o','ConnectionAttempts=1',
        '-i',$keyPath,'--',"root@$expectedHost",'/usr/bin/python3 -I -B -'
    )
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $sshPath
    $start.Arguments = ($arguments | ForEach-Object { ConvertTo-WindowsArgument $_ }) -join ' '
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.EnvironmentVariables.Clear()
    $start.EnvironmentVariables['SYSTEMROOT'] = 'C:\Windows'
    $start.EnvironmentVariables['WINDIR'] = 'C:\Windows'
    $start.EnvironmentVariables['PATH'] = 'C:\Windows\System32\OpenSSH;C:\Windows\System32'
    $start.EnvironmentVariables['PROGRAMDATA'] = 'C:\ProgramData'
    $start.EnvironmentVariables['HOME'] = 'C:\ProgramData\AMN2\phase16\no-ambient-home'
    $start.EnvironmentVariables['USERPROFILE'] = 'C:\ProgramData\AMN2\phase16\no-ambient-profile'

    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    if (-not $process.Start()) { throw 'transport_start_failed' }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.BaseStream.Write($remoteBytes, 0, $remoteBytes.Length)
    $process.StandardInput.BaseStream.Flush()
    $process.StandardInput.Close()
    if (-not $process.WaitForExit(30000)) {
        try { $process.Kill() } catch { }
        throw 'transport_timeout'
    }
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    if ($stdout.Length -gt $maximumOutputChars -or $stderr.Length -gt 4096) { throw 'transport_output_too_large' }
    $stderrBytes = [Text.UTF8Encoding]::new($false).GetBytes($stderr)
    $stderrHasher = [Security.Cryptography.SHA256]::Create()
    try { $stderrSha256 = ([BitConverter]::ToString($stderrHasher.ComputeHash($stderrBytes))).Replace('-', '').ToLowerInvariant() } finally { $stderrHasher.Dispose() }
    $result = [ordered]@{
        exit_code = $process.ExitCode
        remote_script_sha256 = $remoteSha256
        stderr_length = $stderrBytes.Length
        stderr_sha256 = $stderrSha256
        stdout = $stdout
    }
    $result | ConvertTo-Json -Compress
    if ($process.ExitCode -ne 0 -or $stderrBytes.Length -ne 0) { exit 1 }
} finally {
    if ($null -ne $remoteBytes) { [Array]::Clear($remoteBytes, 0, $remoteBytes.Length) }
}
