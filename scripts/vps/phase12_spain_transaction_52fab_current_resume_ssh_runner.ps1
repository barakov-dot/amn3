[CmdletBinding()]
param([string]$Approval = "")

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$expectedExecutorSha = "07FA623C7C919A0263C738FACBC816717102526B3A126CDEDAA03E70E6DF5060"
$expectedExecutorBytes = 151989
$expectedPriorExecutorSha = "88FE4633126E3BC5732A68EADD679BE2D30AD5D89A5B780F01FA45BB41CBE480"
$expectedPriorExecutorBytes = 151821
$expectedNonce = "52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246"
$expectedTransactionSha = "7beec673258de6b4b68206f8013ab8cc9c8d1fb488e38e39340baa1c571d6e1c"
$expectedCapsuleSha = "eb6b3ee6864504f724f7ac7d8839983bdec717c576871cadc7c98b95337cf088"
$expectedLedgerSha = "0ee87dfa762739457eafa5d6c8c81168f99da745b6ddd0f30bc60388f7e660c9"
$expectedCommittedSha = "7fb31fce8076058c691d2f9aaf486ff5a33dbae946f7b9772c981bcc2b0b08bc"
$expectedRemovedSha = "bc26afe7c2daff7d6b18053f6bb65c236deb0673454177366e745179d406b6f8"
$expectedPendingSha = "782ba67c96044bef0d3c7a7cc98b6e32cf7218ff9462ca8cc13551ed07b8c29a"
$expectedSystemdSha = "f1768eee265e2b6396dd300a8ba7e54a05f059c9a1b951adb97559dbff0e04e2"
$expectedRunIdentity = "sha256:c8b39711f9539bd0b73330eb8f2e09e66bd0495cf276688be81ef91806aeb07d"
$expectedEtcTree = [ordered]@{ entry_count=4; root_mode="0750"; total_bytes=2392; tree_sha256="cd94755306a8c864b29fec3b336565f470a5fc49fc7af26982cd18ecd9caf5a7" }
$expectedOptTree = [ordered]@{ entry_count=2903; root_mode="0755"; total_bytes=313921242; tree_sha256="0f2f2ade8f6876dfdd65ef495f7131555caab6be6361dca2d6811ca9f3d25119" }
$expectedVarTree = [ordered]@{ entry_count=1; root_mode="0750"; total_bytes=249856; tree_sha256="8f95e1f1f0ce9ba9c204b5143b5111ad350b2122996dbae6ec1dd543b527bc99" }
$expectedRunnerSha = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToUpperInvariant()
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$executorPath = Join-Path $repoRoot "private-artifacts\phase12-spain-current-terminal-resume-v3-52fab7-20260725\executor-a.pyz"
$sshExe = "C:\Windows\System32\OpenSSH\ssh.exe"
$uploadTimeoutMilliseconds = 60000

function Get-TextSha256([string]$Value) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($Value)))).Replace("-", "") }
    finally { $hasher.Dispose() }
}

function ConvertTo-WindowsCommandLineArgument([string]$Value) {
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + (($Value -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
}

function Invoke-ExactSsh([string[]]$Arguments, [byte[]]$InputBytes) {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $sshExe
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $info.UseShellExecute = $false; $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true; $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
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

function Invoke-BoundedSshUpload([string]$SourcePath, [string]$Destination) {
    if ($Destination -cne "/root/amn2-spain-phase12-current-resume-executor-a.pyz") { throw "Approved resume artifact destination invalid." }
    $info = [Diagnostics.ProcessStartInfo]::new(); $info.FileName = $sshExe
    $remoteCommand = 'destination=' + $Destination + '; umask 077; cat > "$destination"'
    $info.Arguments = ((@($sshBase + @($target, $remoteCommand)) | ForEach-Object { ConvertTo-WindowsCommandLineArgument $_ }) -join ' ')
    $info.UseShellExecute = $false; $info.CreateNoWindow = $true
    $info.RedirectStandardInput = $true; $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $info
    if (-not $process.Start()) { throw "Approved resume executor upload did not start." }
    $input = $null; $timedOut = $false
    try {
        $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
        $stderrTask = $process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        $input = [IO.File]::Open($SourcePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $copyTask = $input.CopyToAsync($process.StandardInput.BaseStream); $deadline = [Diagnostics.Stopwatch]::StartNew()
        if (-not $copyTask.Wait($uploadTimeoutMilliseconds)) { $timedOut = $true; throw "Approved resume executor upload exceeded 60 seconds." }
        [void]$copyTask.GetAwaiter().GetResult(); $process.StandardInput.Close()
        $remaining = [Math]::Max(0, $uploadTimeoutMilliseconds - [int]$deadline.ElapsedMilliseconds)
        if (-not $process.WaitForExit($remaining)) { $timedOut = $true; throw "Approved resume executor upload exceeded 60 seconds." }
        [void][Threading.Tasks.Task]::WaitAll(@($stdoutTask, $stderrTask))
        if ($process.ExitCode -ne 0) { throw "Approved resume executor upload failed." }
    } catch { if ($timedOut) { throw }; throw "Approved resume executor upload failed." }
    finally {
        if (-not $process.HasExited) { try { $process.Kill($true) } catch { }; $process.WaitForExit() }
        if ($null -ne $input) { $input.Dispose() }; $process.Dispose()
    }
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

foreach ($path in @($executorPath, $sshExe)) { if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required resume artifact unavailable." } }
if ((Get-Item -LiteralPath $executorPath).Length -ne $expectedExecutorBytes -or (Get-FileHash -LiteralPath $executorPath -Algorithm SHA256).Hash.ToUpperInvariant() -cne $expectedExecutorSha) { throw "Resume executor checksum/size mismatch." }
$privateRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) "AMN2\private-artifacts\post-release\spain-migration\spain-fresh-20260720-001"
$bindingPath = Join-Path $privateRoot "target.env"; $keyPath = Join-Path $privateRoot "id_ed25519_spain"; $knownHostsPath = Join-Path $privateRoot "known_hosts_spain"
$binding = Read-PrivateBinding $bindingPath
if ($binding["SSH_KEY_PATH"] -cne $keyPath -or -not (Test-Path -LiteralPath $keyPath -PathType Leaf) -or -not (Test-Path -LiteralPath $knownHostsPath -PathType Leaf)) { throw "Private SSH material unavailable." }

$runnerApproval = "APPROVE PHASE12 SPAIN TRANSACTION 52FAB7 CURRENT TERMINAL RECOVERY RESUME RUNNER SHA256 $expectedRunnerSha EXECUTOR SHA256 $expectedExecutorSha EXECUTOR BYTES $expectedExecutorBytes PRIOR EXECUTOR SHA256 $expectedPriorExecutorSha PRIOR EXECUTOR BYTES $expectedPriorExecutorBytes NONCE $expectedNonce TRANSACTION SHA256 $expectedTransactionSha CAPSULE SHA256 $expectedCapsuleSha LEDGER SHA256 $($expectedLedgerSha.ToUpperInvariant()) COMMITTED SET SHA256 $($expectedCommittedSha.ToUpperInvariant()) REMOVED SET SHA256 $($expectedRemovedSha.ToUpperInvariant()) PENDING SET SHA256 $($expectedPendingSha.ToUpperInvariant()) SYSTEMD SHA256 $($expectedSystemdSha.ToUpperInvariant()) OPT TREE SHA256 $($expectedOptTree.tree_sha256.ToUpperInvariant()) ENTRIES $($expectedOptTree.entry_count) BYTES $($expectedOptTree.total_bytes) ETC TREE SHA256 $($expectedEtcTree.tree_sha256.ToUpperInvariant()) ENTRIES $($expectedEtcTree.entry_count) BYTES $($expectedEtcTree.total_bytes) VAR TREE SHA256 $($expectedVarTree.tree_sha256.ToUpperInvariant()) ENTRIES $($expectedVarTree.entry_count) BYTES $($expectedVarTree.total_bytes) RUN IDENTITY $expectedRunIdentity REMOVE EXACT AUDITED AMN2 CONTOUR VERIFY FOREIGN EQUALITY NO INSTALL NO FOREIGN SERVICE MUTATION NO USA DATA MUTATION USA ROLLBACK CONTOUR"
if ($Approval -cne $runnerApproval) { Write-Output $runnerApproval; throw "Exact current terminal recovery resume approval mismatch." }

$transportOptions = @("-F", "none", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "IdentitiesOnly=yes", "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no", "-o", "GSSAPIAuthentication=no", "-o", "ForwardAgent=no", "-o", "ClearAllForwardings=yes", "-o", "RequestTTY=no", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=$knownHostsPath", "-i", $keyPath)
$sshBase = @($transportOptions + @("-p", "22")); $target = "$($binding['TARGET_USER'])@$($binding['TARGET_HOST'])"
$remoteExecutorPath = "/root/amn2-spain-phase12-executor.pyz"
$remoteState = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"))) ([byte[]]@())
$remoteText = (New-Object Text.UTF8Encoding($false,$true)).GetString($remoteState.Stdout)
$hasPrior = $remoteState.ExitCode -eq 0 -and $remoteText -match "(?im)^$($expectedPriorExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and $remoteText -match "(?m)^$expectedPriorExecutorBytes$"
$hasCurrent = $remoteState.ExitCode -eq 0 -and $remoteText -match "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -and $remoteText -match "(?m)^$expectedExecutorBytes$"
if (-not ($hasPrior -or $hasCurrent)) { throw "Remote executor checksum/size precondition mismatch." }
$transactionPath = "/var/lib/amn2-spain-phase12-audit/transaction-$expectedNonce.json"; $capsulePath = "/var/lib/amn2-spain-phase12-audit/recovery-capsule-$expectedNonce.json"; $ledgerPath = "/var/lib/amn2-spain-phase12-audit/mutation-ledger-$expectedNonce.json"
$bindingResult = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $transactionPath $capsulePath $ledgerPath && test ! -e /opt/amn2-spain-package && test ! -L /opt/amn2-spain-package"))) ([byte[]]@())
$bindingText = (New-Object Text.UTF8Encoding($false,$true)).GetString($bindingResult.Stdout)
if ($bindingResult.ExitCode -ne 0 -or $bindingText -notmatch "(?im)^$($expectedTransactionSha.ToLowerInvariant())  $([regex]::Escape($transactionPath))$" -or $bindingText -notmatch "(?im)^$($expectedCapsuleSha.ToLowerInvariant())  $([regex]::Escape($capsulePath))$" -or $bindingText -notmatch "(?im)^$($expectedLedgerSha.ToLowerInvariant())  $([regex]::Escape($ledgerPath))$") { throw "Resume transaction/capsule/ledger binding mismatch." }
if (-not $hasCurrent) {
    $stagingPath = "/root/amn2-spain-phase12-current-resume-executor-a.pyz"; Invoke-BoundedSshUpload $executorPath $stagingPath
    $uploaded = Invoke-ExactSsh (@($sshBase + @($target, "sha256sum $stagingPath && stat -c '%s' $stagingPath"))) ([byte[]]@()); $uploadedText = (New-Object Text.UTF8Encoding($false,$true)).GetString($uploaded.Stdout)
    if ($uploaded.ExitCode -ne 0 -or $uploadedText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($stagingPath))$" -or $uploadedText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote resume executor checksum mismatch." }
    $activated = Invoke-ExactSsh (@($sshBase + @($target, "mv -f $stagingPath $remoteExecutorPath && chmod 0644 $remoteExecutorPath && sha256sum $remoteExecutorPath && stat -c '%s' $remoteExecutorPath"))) ([byte[]]@()); $activatedText = (New-Object Text.UTF8Encoding($false,$true)).GetString($activated.Stdout)
    if ($activated.ExitCode -ne 0 -or $activatedText -notmatch "(?im)^$($expectedExecutorSha.ToLowerInvariant())  $([regex]::Escape($remoteExecutorPath))$" -or $activatedText -notmatch "(?m)^$expectedExecutorBytes$") { throw "Remote resume executor activation mismatch." }
}
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$intent = [ordered]@{
    approval_id=(Get-TextSha256 $Approval).ToLowerInvariant(); approved_at_epoch=$now; capsule_sha256=$expectedCapsuleSha; committed_objects_sha256=$expectedCommittedSha; executor_sha256=$expectedExecutorSha.ToLowerInvariant(); expires_at_epoch=($now+300); mutation_ledger_sha256=$expectedLedgerSha; nonce=$expectedNonce
    owned_tree_inventories=[ordered]@{ etc=$expectedEtcTree; opt=$expectedOptTree; var=$expectedVarTree }
    pending_objects_sha256=$expectedPendingSha; recovery_authorized=$true; removed_objects_sha256=$expectedRemovedSha; run_directory_identity=$expectedRunIdentity; schema="amn2.spain-current-terminal-recovery-resume-intent.v1"; systemd_sha256=$expectedSystemdSha; transaction_sha256=$expectedTransactionSha
}
$intentBytes = (New-Object Text.UTF8Encoding($false)).GetBytes(($intent | ConvertTo-Json -Compress -Depth 6) + "`n")
$result = Invoke-ExactSsh (@($sshBase + @($target, "/usr/bin/python3 -I -B $remoteExecutorPath current-terminal-recovery-resume-bound"))) $intentBytes
if ($result.ExitCode -ne 0) { $safe = (New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stderr).Trim(); $safeLine = @($safe -split '\r?\n')[0]; if ($safeLine -match '^[a-zA-Z0-9_ /-]{1,200}$') { [Console]::Error.WriteLine($safeLine) }; throw "Current terminal recovery resume failed; transaction remains fail-closed." }
$resultText = (New-Object Text.UTF8Encoding($false,$true)).GetString($result.Stdout).Trim()
try { $receipt = $resultText | ConvertFrom-Json -AsHashtable } catch { throw "Current terminal recovery resume receipt JSON invalid." }
if ($receipt["schema"] -cne "amn2.spain-current-terminal-recovery-resume-receipt.v1" -or $receipt["result"] -cne "passed" -or $receipt["nonce"] -cne $expectedNonce -or $receipt["transaction_sha256"] -cne $expectedTransactionSha -or $receipt["capsule_sha256"] -cne $expectedCapsuleSha -or $receipt["mutation_ledger_before_sha256"] -cne $expectedLedgerSha -or $receipt["mutation_ledger_after_sha256"] -notmatch '^[0-9a-f]{64}$' -or @($receipt["removed_owned_objects"]).Count -ne 29 -or @($receipt["pending_owned_objects"]).Count -ne 5 -or $receipt["foreign_service_persistent_equal"] -ne $true) { throw "Current terminal recovery resume receipt binding mismatch." }
[Console]::WriteLine($resultText)
