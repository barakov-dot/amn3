# Requires PowerShell 7 / modern .NET. Loading this file only defines functions.
# No endpoint, network adapter, configuration reader or live entrypoint exists.
# A future caller must separately authorize any process it asks to execute.

function Test-Phase16MeasurementNumber {
    param($Value)
    if ($null -eq $Value -or $Value -is [bool]) { return $false }
    if ($Value -isnot [byte] -and $Value -isnot [int] -and $Value -isnot [long] -and
        $Value -isnot [double] -and $Value -isnot [single] -and $Value -isnot [decimal]) { return $false }
    return [double]::IsFinite([double]$Value)
}

function Get-Phase16RttSummary {
    param($Samples = @(), $ProbePathValidated = $false)
    if ($ProbePathValidated -isnot [bool] -or @($Samples).Count -gt 10000) { throw 'invalid_samples' }
    $values = [Collections.Generic.List[double]]::new()
    $timeouts = 0; $errors = 0; $canceled = 0; $sequence = 0
    foreach ($row in @($Samples)) {
        $sequence++
        if ($null -eq $row) { throw 'invalid_samples' }
        $names = @($row.PSObject.Properties.Name)
        if ($names.Count -ne 3 -or 'sequence' -notin $names -or 'status' -notin $names -or
            'rtt_ms' -notin $names) { throw 'invalid_samples' }
        if (-not (Test-Phase16MeasurementNumber $row.sequence) -or $row.sequence -ne $sequence -or
            $row.status -isnot [string] -or $row.status -cnotin @('success','timeout','send_error','canceled')) {
            throw 'invalid_samples'
        }
        if ($row.status -ceq 'success') {
            if (-not (Test-Phase16MeasurementNumber $row.rtt_ms) -or $row.rtt_ms -lt 0 -or
                $row.rtt_ms -gt 900000) { throw 'invalid_samples' }
            $values.Add([double]$row.rtt_ms)
        } else {
            if ($null -ne $row.rtt_ms) { throw 'invalid_samples' }
            switch -CaseSensitive ($row.status) {
                'timeout' { $timeouts++ }
                'send_error' { $errors++ }
                'canceled' { $canceled++ }
            }
        }
    }
    $median = $null; $p95 = $null; $jitter = $null; $loss = $null
    if ($values.Count -gt 0) {
        $sorted = @($values | Sort-Object)
        $middle = [int][Math]::Floor($sorted.Count / 2)
        $median = if ($sorted.Count % 2) { $sorted[$middle] } else { ($sorted[$middle - 1] + $sorted[$middle]) / 2 }
        $p95 = $sorted[[int][Math]::Ceiling(0.95 * $sorted.Count) - 1]
    }
    if ($values.Count -gt 1) {
        $sum = 0.0
        for ($i = 1; $i -lt $values.Count; $i++) { $sum += [Math]::Abs($values[$i] - $values[$i - 1]) }
        $jitter = $sum / ($values.Count - 1)
    }
    $sent = $values.Count + $timeouts
    if ($ProbePathValidated -and $sent -gt 0 -and $errors -eq 0 -and $canceled -eq 0) {
        $loss = 100.0 * $timeouts / $sent
    }
    $ready = $ProbePathValidated -and $values.Count -ge 100 -and $errors -eq 0 -and $canceled -eq 0
    return [ordered]@{
        schema = 'amn2.phase16.rtt-summary.v1'
        readiness = $(if ($ready) { 'MEASURED' } else { 'INCOMPLETE' })
        sample_count = $sequence; success_count = $values.Count; sent_count = $sent
        timeout_count = $timeouts; send_error_count = $errors; canceled_count = $canceled
        median_ms = $median; p95_ms = $p95; jitter_ms = $jitter; loss_percent = $loss
    }
}

function Get-Phase16ThroughputSummary {
    # Caller supplies validated payload counts and whole-series elapsed time.
    # A completed local process alone does not establish HTTP/TLS success.
    param($BodyBytes, $ExpectedBytes, $ElapsedMs, $TransferCompleted = $false)
    foreach ($number in @($BodyBytes, $ExpectedBytes, $ElapsedMs)) {
        if (-not (Test-Phase16MeasurementNumber $number)) { throw 'invalid_transfer' }
    }
    if ($TransferCompleted -isnot [bool] -or $BodyBytes -lt 0 -or $ExpectedBytes -le 0 -or
        $BodyBytes -gt 67108864 -or $ExpectedBytes -gt 67108864 -or
        [Math]::Floor($BodyBytes) -ne $BodyBytes -or [Math]::Floor($ExpectedBytes) -ne $ExpectedBytes -or
        $ElapsedMs -le 0 -or $ElapsedMs -gt 900000) { throw 'invalid_transfer' }
    $ready = $TransferCompleted -and $BodyBytes -eq $ExpectedBytes
    $mbps = $null
    if ($ready) {
        $mbps = ([double]$BodyBytes * 8) / $ElapsedMs / 1000
        if (-not [double]::IsFinite($mbps)) { throw 'invalid_transfer' }
    }
    return [ordered]@{
        schema = 'amn2.phase16.throughput-summary.v1'
        readiness = $(if ($ready) { 'MEASURED' } else { 'INCOMPLETE' })
        payload_bytes = $BodyBytes; duration_ms = $ElapsedMs; mbps = $mbps
    }
}

function Invoke-Phase16BoundedProcess {
    # Counts raw pipe bytes, NOT wire bytes, HTTP status or successful throughput.
    # Work stops before the overall deadline to reserve time for process cleanup.
    # No shell expansion; raw stdout/stderr/arguments never enter the result.
    # stdin_bytes is null when an interrupted write may have transferred a prefix.
    # process_exited describes the direct child, not proof that detached descendants
    # were reaped. Future live adapters must not spawn detached descendants.
    param($FilePath, $ArgumentList = @(), $InputBytes = [byte[]]@(),
          $MaxInputBytes = 0, $MaxOutputBytes = 65536, $TimeoutMs = 5000,
          $CleanupReserveMs = 500)
    $result = [ordered]@{
        schema = 'amn2.phase16.bounded-process.v1'; status = 'invalid_request'
        process_id = $null; process_exited = $false; exit_code = $null
        stdin_bytes = 0L; stdout_bytes = 0L; stderr_bytes = 0L
        elapsed_ms = 0L; deadline_exceeded = $false; raw_output_retained = $false
    }
    foreach ($limit in @($MaxInputBytes, $MaxOutputBytes, $TimeoutMs, $CleanupReserveMs)) {
        if (-not (Test-Phase16MeasurementNumber $limit) -or [Math]::Floor($limit) -ne $limit) { return $result }
    }
    if ($FilePath -isnot [string] -or -not [IO.Path]::IsPathFullyQualified($FilePath) -or
        $InputBytes -isnot [byte[]] -or $MaxInputBytes -lt 0 -or $MaxInputBytes -gt 16777216 -or
        $InputBytes.Length -gt $MaxInputBytes -or $MaxOutputBytes -lt 0 -or $MaxOutputBytes -gt 67108864 -or
        $TimeoutMs -gt 900000 -or $CleanupReserveMs -lt 100 -or $CleanupReserveMs -gt 5000 -or
        $TimeoutMs -le $CleanupReserveMs -or @($ArgumentList).Count -gt 128) { return $result }
    foreach ($argument in @($ArgumentList)) {
        if ($argument -isnot [string] -or $argument.Length -gt 32768 -or $argument.Contains([char]0)) { return $result }
    }
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $process = [Diagnostics.Process]::new()
    $started = $false
    try {
        $info = [Diagnostics.ProcessStartInfo]::new()
        $info.FileName = $FilePath
        $info.UseShellExecute = $false; $info.CreateNoWindow = $true
        $info.RedirectStandardInput = $true; $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
        foreach ($argument in @($ArgumentList)) { $info.ArgumentList.Add($argument) }
        $process.StartInfo = $info
        try { $started = $process.Start() } catch { $result.status = 'start_failed'; return $result }
        if (-not $started) { $result.status = 'start_failed'; return $result }
        $result.process_id = $process.Id
        $result.status = 'timeout'
        $outBuffer = [byte[]]::new(4096); $errBuffer = [byte[]]::new(4096)
        $outTask = $process.StandardOutput.BaseStream.ReadAsync($outBuffer, 0, [int][Math]::Min(4096, $MaxOutputBytes + 1))
        $errTask = $process.StandardError.BaseStream.ReadAsync($errBuffer, 0, 4096)
        if ($InputBytes.Length -gt 0) { $result.stdin_bytes = $null }
        $writeTask = $process.StandardInput.BaseStream.WriteAsync($InputBytes, 0, $InputBytes.Length)
        $outDone = $false; $errDone = $false; $inputDone = $false
        $workDeadline = $TimeoutMs - $CleanupReserveMs
        while ($clock.ElapsedMilliseconds -lt $workDeadline) {
            if (-not $inputDone -and $writeTask.IsCompleted) {
                $null = $writeTask.GetAwaiter().GetResult()
                $result.stdin_bytes = $InputBytes.Length
                $process.StandardInput.Close(); $inputDone = $true
            }
            if (-not $outDone -and $outTask.IsCompleted) {
                $count = $outTask.GetAwaiter().GetResult()
                $result.stdout_bytes += $count
                if ($result.stdout_bytes -gt $MaxOutputBytes) { $result.status = 'output_limit'; break }
                if ($count -eq 0) { $outDone = $true } else {
                    $next = [int][Math]::Min(4096, $MaxOutputBytes - $result.stdout_bytes + 1)
                    $outTask = $process.StandardOutput.BaseStream.ReadAsync($outBuffer, 0, $next)
                }
            }
            if (-not $errDone -and $errTask.IsCompleted) {
                $count = $errTask.GetAwaiter().GetResult()
                $result.stderr_bytes += $count
                if ($result.stderr_bytes -gt 65536) { $result.status = 'stderr_limit'; break }
                if ($count -eq 0) { $errDone = $true } else {
                    $next = [int][Math]::Min(4096, 65536 - $result.stderr_bytes + 1)
                    $errTask = $process.StandardError.BaseStream.ReadAsync($errBuffer, 0, $next)
                }
            }
            if ($process.HasExited -and $outDone -and $errDone -and $inputDone) {
                $result.status = if ($process.ExitCode -eq 0) { 'completed' } else { 'nonzero_exit' }
                break
            }
            [Threading.Thread]::Sleep(5)
        }
    } catch {
        $result.status = 'io_error'
    } finally {
        if ($started) {
            try {
                if (-not $process.HasExited) { $process.Kill($true) }
                $remaining = [int][Math]::Max(0, $TimeoutMs - $clock.ElapsedMilliseconds)
                $result.process_exited = $process.WaitForExit($remaining)
                if ($result.process_exited) { $result.exit_code = $process.ExitCode }
                else { $result.status = 'cleanup_unconfirmed' }
            } catch { $result.status = 'cleanup_unconfirmed' }
        }
        $process.Dispose()
        $clock.Stop()
        $result.elapsed_ms = $clock.ElapsedMilliseconds
        $result.deadline_exceeded = $clock.ElapsedMilliseconds -gt $TimeoutMs
        if ($result.deadline_exceeded -and $result.status -eq 'completed') { $result.status = 'timeout' }
    }
    return $result
}
