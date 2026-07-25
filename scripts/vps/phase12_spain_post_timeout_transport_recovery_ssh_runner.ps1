[CmdletBinding()]
param(
    [string]$Approval = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedPackageSha = "FF9E8FA4604C4E9F7A3EE139B1D7B96D53FA4693E4555808B7E1725BDBAD4974"
$expectedPackageBytes = 139970560
$expectedExecutorSha = "04B0F5142E7D7464C7CA6555E482A17F4C3D79D1F209A0E7327CD44144AD6978"
$expectedExecutorBytes = 146014
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$timeoutMilliseconds = 60000

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

function Invoke-BoundedSsh([string[]]$Arguments, [byte[]]$InputBytes) {
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
    if (-not $process.Start()) { throw "Post-timeout transport recovery did not start." }
    $stdout = [IO.MemoryStream]::new()
    $stderr = [IO.MemoryStream]::new()
    $timedOut = $false
    try {
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        $deadline = [Diagnostics.Stopwatch]::StartNew()
        $writeTask = $process.StandardInput.BaseStream.WriteAsync($InputBytes, 0, $InputBytes.Length)
        if (-not $writeTask.Wait($timeoutMilliseconds)) {
            $timedOut = $true
            throw "Post-timeout transport recovery exceeded 60 seconds."
        }
        [void]$writeTask.GetAwaiter().GetResult()
        $process.StandardInput.Close()
        $remaining = [Math]::Max(0, $timeoutMilliseconds - [int]$deadline.ElapsedMilliseconds)
        if (-not $process.WaitForExit([int]$remaining)) {
            $timedOut = $true
            throw "Post-timeout transport recovery exceeded 60 seconds."
        }
        [Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
        return [pscustomobject]@{ ExitCode=$process.ExitCode; Stdout=$stdout.ToArray(); Stderr=$stderr.ToArray() }
    } catch {
        if ($timedOut) { throw }
        throw "Post-timeout transport recovery failed before any staging deletion."
    } finally {
        if (-not $process.HasExited) {
            try { $process.Kill($true) } catch { }
            $process.WaitForExit()
        }
        $stdout.Dispose()
        $stderr.Dispose()
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

$runnerApproval = "AUTHORIZE AMN2 PHASE12 POST-TIMEOUT TRANSPORT RECOVERY IN GO MODE: VERIFY READ ONLY WHETHER /root/amn2-spain-phase12-install-a.tar OR /root/amn2-spain-phase12-executor-a.pyz ARE PARTIAL; VERIFY NO AMN2 INSTALL TRANSACTION AND NO AMN2 UNITS ACTIVE; IF AND ONLY IF PARTIAL STAGING FILES EXIST REMOVE ONLY THOSE TWO -a STAGING FILES; NO INSTALL NO FOREIGN SERVICE MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact post-timeout transport recovery authorization mismatch." }

$remoteProgram = @'
set -euo pipefail
package_path="/root/amn2-spain-phase12-install-a.tar"
executor_path="/root/amn2-spain-phase12-executor-a.pyz"
expected_package_sha="ff9e8fa4604c4e9f7a3ee139b1d7b96d53fa4693e4555808b7e1725bdbad4974"
expected_package_bytes="139970560"
expected_executor_sha="04b0f5142e7d7464c7ca6555e482a17f4c3d79d1f209a0e7327cd44144ad6978"
expected_executor_bytes="146014"

classify_staging_file() {
    local path="$1" expected_sha="$2" expected_bytes="$3" bytes sha
    if [ -L "$path" ]; then printf '%s' "unexpected"; return 0; fi
    if [ ! -e "$path" ]; then printf '%s' "absent"; return 0; fi
    if [ ! -f "$path" ]; then printf '%s' "unexpected"; return 0; fi
    bytes="$(stat -c %s -- "$path")"
    sha="$(sha256sum -- "$path" | awk '{print $1}')"
    if ! [[ "$bytes" =~ ^[0-9]+$ && "$sha" =~ ^[0-9a-f]{64}$ ]]; then return 78; fi
    if [ "$bytes" = "$expected_bytes" ] && [ "$sha" = "$expected_sha" ]; then
        printf '%s' "complete_current"
    elif [ "$bytes" -lt "$expected_bytes" ]; then
        printf '%s' "partial"
    else
        printf '%s' "unexpected"
    fi
}

# Historic audit ledgers are retained terminal evidence. An active transaction is
# represented only by active owned runtime state, not by preserved audit records.
active_install_transaction=false
for owned_path in /opt/amn2-spain-package /etc/amn2-spain /opt/amn2-spain /run/amn2-spain /var/lib/amn2-spain /var/lib/amn2-spain-docker; do
    if [ -e "$owned_path" ] || [ -L "$owned_path" ]; then active_install_transaction=true; fi
done

amn2_units_active=false
for unit_name in amn2-spain-web.service amn2-spain-bot.service amn2-spain-docker.service amn2-spain-network.service; do
    if systemctl is-active --quiet "$unit_name" 2>/dev/null; then amn2_units_active=true; fi
done

package_state="$(classify_staging_file "$package_path" "$expected_package_sha" "$expected_package_bytes")"
executor_state="$(classify_staging_file "$executor_path" "$expected_executor_sha" "$expected_executor_bytes")"
case "$package_state:$executor_state" in
    *unexpected*) exit 78 ;;
esac
if [ "$active_install_transaction" != false ] || [ "$amn2_units_active" != false ]; then exit 78; fi

action="none"
removed_count=0
if [ "$package_state" = "partial" ]; then
    rm -f -- "$package_path"
    [ ! -e "$package_path" ] && [ ! -L "$package_path" ] || exit 78
    removed_count=$((removed_count + 1))
fi
if [ "$executor_state" = "partial" ]; then
    rm -f -- "$executor_path"
    [ ! -e "$executor_path" ] && [ ! -L "$executor_path" ] || exit 78
    removed_count=$((removed_count + 1))
fi
if [ "$removed_count" -gt 0 ]; then action="removed_partial_staging"; fi
printf '{"schema":"amn2.spain-post-timeout-transport-recovery.v1","result":"passed","package_a":"%s","executor_a":"%s","active_install_transaction":false,"amn2_units_active":false,"action":"%s","removed_count":%s}\n' "$package_state" "$executor_state" "$action" "$removed_count"
'@
$remoteBytes = (New-Object Text.UTF8Encoding($false)).GetBytes($remoteProgram)
$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath, "-p", "22")
$target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$result = Invoke-BoundedSsh (@($transportOptions + @($target, "/bin/bash -s"))) $remoteBytes
if ($result.ExitCode -ne 0) { throw "Post-timeout transport recovery was rejected before staging deletion." }
$resultText = (New-Object Text.UTF8Encoding($false, $true)).GetString($result.Stdout).Trim()
try { $receipt = $resultText | ConvertFrom-Json } catch { throw "Post-timeout transport recovery receipt invalid." }
$allowedStates = @("absent", "partial", "complete_current")
$allowedActions = @("none", "removed_partial_staging")
if ($receipt.schema -cne "amn2.spain-post-timeout-transport-recovery.v1" -or $receipt.result -cne "passed" -or $allowedStates -notcontains $receipt.package_a -or $allowedStates -notcontains $receipt.executor_a -or $receipt.active_install_transaction -ne $false -or $receipt.amn2_units_active -ne $false -or $allowedActions -notcontains $receipt.action) { throw "Post-timeout transport recovery receipt invalid." }
$stagingStates = @($receipt.package_a, $receipt.executor_a)
$expectedRemovedCount = @($stagingStates | Where-Object { $_ -ceq "partial" }).Count
if ([int]$receipt.removed_count -ne $expectedRemovedCount -or (($expectedRemovedCount -gt 0) -ne ($receipt.action -ceq "removed_partial_staging"))) { throw "Post-timeout transport recovery receipt invalid." }
[Console]::WriteLine(([ordered]@{ schema=$receipt.schema; result=$receipt.result; package_a=$receipt.package_a; executor_a=$receipt.executor_a; active_install_transaction=$false; amn2_units_active=$false; action=$receipt.action; removed_count=[int]$receipt.removed_count; install_started=$false; foreign_service_mutation=$false } | ConvertTo-Json -Compress))
