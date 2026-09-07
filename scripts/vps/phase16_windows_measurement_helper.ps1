# Requires PowerShell 7 / modern .NET. Loading this file only defines functions.
# No default endpoint, configuration reader or automatic live entrypoint exists.
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
          $CleanupReserveMs = 500, $CurlMetadata = $false)
    $result = [ordered]@{
        schema = 'amn2.phase16.bounded-process.v1'; status = 'invalid_request'
        process_id = $null; process_exited = $false; exit_code = $null
        stdin_bytes = 0L; stdout_bytes = 0L; stderr_bytes = 0L
        elapsed_ms = 0L; deadline_exceeded = $false; raw_output_retained = $false
    }
    if ($CurlMetadata -isnot [bool]) { return $result }
    if ($CurlMetadata) { $result.http_metadata = $null }
    foreach ($limit in @($MaxInputBytes, $MaxOutputBytes, $TimeoutMs, $CleanupReserveMs)) {
        if (-not (Test-Phase16MeasurementNumber $limit) -or [Math]::Floor($limit) -ne $limit) { return $result }
    }
    if ($FilePath -isnot [string] -or -not [IO.Path]::IsPathFullyQualified($FilePath) -or
        $InputBytes -isnot [byte[]] -or $MaxInputBytes -lt 0 -or $MaxInputBytes -gt 16777216 -or
        $InputBytes.Length -gt $MaxInputBytes -or $MaxOutputBytes -lt 0 -or $MaxOutputBytes -gt 67108864 -or
        $TimeoutMs -gt 900000 -or $CleanupReserveMs -lt 100 -or $CleanupReserveMs -gt 5000 -or
        $TimeoutMs -le $CleanupReserveMs -or @($ArgumentList).Count -gt 128) { return $result }
    if ($CurlMetadata -and $MaxOutputBytes -gt 4096) { return $result }
    foreach ($argument in @($ArgumentList)) {
        if ($argument -isnot [string] -or $argument.Length -gt 32768 -or $argument.Contains([char]0)) { return $result }
    }
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $process = [Diagnostics.Process]::new()
    $started = $false
    # At most 4 KiB retained transiently, never exported as text.
    $metadataText = [Text.StringBuilder]::new()
    try {
        $info = [Diagnostics.ProcessStartInfo]::new()
        $info.FileName = $FilePath
        $info.UseShellExecute = $false; $info.CreateNoWindow = $true
        $info.RedirectStandardInput = $true; $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
        # Opt-in curl mode must not inherit a request to persist TLS secrets.
        if ($CurlMetadata) { $null = $info.Environment.Remove('SSLKEYLOGFILE') }
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
                if ($CurlMetadata -and $count -gt 0) {
                    $null = $metadataText.Append([Text.Encoding]::ASCII.GetString($outBuffer, 0, $count))
                }
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
    if ($CurlMetadata -and $result.status -eq 'completed') {
        # Exact positional schema; no JSON, arbitrary keys, URLs or error text.
        $pattern = '\Ap16v1\t([0-9]{3})\t([0-9]{1,9})\t([0-9]{1,9})\t([0-9]{1,3}\.[0-9]{6})\t([0-9]{1,9})\t([0-9]{1,3})\t([01])\r?\n\z'
        $match = [regex]::Match($metadataText.ToString(), $pattern)
        if (-not $match.Success) { $result.status = 'metadata_invalid' }
        else {
            $result.http_metadata = [ordered]@{
                response_code = [int]$match.Groups[1].Value
                size_download = [long]$match.Groups[2].Value
                size_upload = [long]$match.Groups[3].Value
                time_total = [double]::Parse($match.Groups[4].Value, [Globalization.CultureInfo]::InvariantCulture)
                ssl_verify_result = [int]$match.Groups[5].Value
                num_redirects = [int]$match.Groups[6].Value
                proxy_used = [int]$match.Groups[7].Value
            }
        }
    }
    $null = $metadataText.Clear()
    return $result
}

function New-Phase16HttpRequest {
    # Pure internal request plan, NOT an evidence/export object (contains URL/body).
    # Caller must pin an approved curl >=8.16 (out-null); no auto-discovery/download.
    param($Endpoint, $Direction, $ExpectedBytes, $InputBytes = [byte[]]@(),
          $ResponseMaxBytes = 65536, $TimeoutMs = 5000)
    foreach ($value in @($ExpectedBytes, $ResponseMaxBytes, $TimeoutMs)) {
        if (-not (Test-Phase16MeasurementNumber $value) -or [Math]::Floor($value) -ne $value) {
            throw 'invalid_http_request'
        }
    }
    if ($Direction -cnotin @('download','upload') -or $InputBytes -isnot [byte[]] -or
        $ExpectedBytes -le 0 -or $ResponseMaxBytes -lt 1 -or $ResponseMaxBytes -gt 65536 -or
        $TimeoutMs -lt 1000 -or $TimeoutMs -gt 60000) { throw 'invalid_http_request' }
    if (($Direction -ceq 'download' -and ($ExpectedBytes -gt 8388608 -or $InputBytes.Length -ne 0)) -or
        ($Direction -ceq 'upload' -and ($ExpectedBytes -gt 2097152 -or $InputBytes.Length -ne $ExpectedBytes))) {
        throw 'invalid_http_request'
    }
    $uri = $null
    if ($Endpoint -isnot [string] -or $Endpoint.Length -gt 2048 -or $Endpoint -match '[\x00-\x20\\]' -or
        -not [Uri]::TryCreate($Endpoint, [UriKind]::Absolute, [ref]$uri) -or
        $uri.Scheme -cne 'https' -or $uri.UserInfo -ne '' -or $uri.Fragment -ne '' -or $uri.Host -eq '') {
        throw 'invalid_http_request'
    }
    $seconds = (($TimeoutMs - 500) / 1000.0).ToString('0.###', [Globalization.CultureInfo]::InvariantCulture)
    $cap = if ($Direction -ceq 'download') { $ExpectedBytes } else { $ResponseMaxBytes }
    $format = "p16v1`t%{response_code}`t%{size_download}`t%{size_upload}`t%{time_total}`t%{ssl_verify_result}`t%{num_redirects}`t%{proxy_used}`n"
    $arguments = @('-q','--silent','--show-error','--globoff',
        '--proto','=https','--proto-redir','=https','--proxy','','--noproxy','*',
        '--retry','0','--max-redirs','0','--max-time',$seconds,'--connect-timeout',$seconds,
        '--max-filesize',([string]$cap),'--out-null','--write-out',$format,
        '--header','Accept-Encoding: identity','--header','Cache-Control: no-cache')
    if ($Direction -ceq 'upload') {
        $arguments += @('--request','POST','--header','Content-Type: application/octet-stream',
                        '--header','Expect:','--data-binary','@-')
    } else { $arguments += @('--request','GET') }
    $arguments += @('--url',$Endpoint)
    return @{ arguments = $arguments; input_bytes = $InputBytes; timeout_ms = $TimeoutMs }
}

function Get-Phase16HttpSummary {
    # Accepts only normalized process evidence from the fixed curl invocation.
    # Does not establish server persistence, content identity, VPN routing or PASS.
    param($ProcessResult, $Direction, $ExpectedBytes, $ResponseMaxBytes = 65536)
    $result = [ordered]@{
        schema = 'amn2.phase16.http-summary.v1'; status = 'incomplete'; readiness = 'INCOMPLETE'
        payload_bytes = $null; duration_ms = $null; mbps = $null
        response_code = $null; download_bytes = $null; upload_bytes = $null
        curl_duration_ms = $null; ssl_verify_result = $null
    }
    if ($null -eq $ProcessResult -or $Direction -cnotin @('download','upload') -or
        -not (Test-Phase16MeasurementNumber $ExpectedBytes) -or $ExpectedBytes -le 0 -or
        [Math]::Floor($ExpectedBytes) -ne $ExpectedBytes -or
        -not (Test-Phase16MeasurementNumber $ResponseMaxBytes) -or $ResponseMaxBytes -lt 1 -or
        $ResponseMaxBytes -gt 65536 -or [Math]::Floor($ResponseMaxBytes) -ne $ResponseMaxBytes -or
        ($Direction -ceq 'download' -and $ExpectedBytes -gt 8388608) -or
        ($Direction -ceq 'upload' -and $ExpectedBytes -gt 2097152)) { return $result }
    $p = $ProcessResult
    if ($p.status -cne 'completed' -or $p.process_exited -isnot [bool] -or -not $p.process_exited -or
        $p.deadline_exceeded -isnot [bool] -or $p.deadline_exceeded -or
        -not (Test-Phase16MeasurementNumber $p.exit_code) -or $p.exit_code -ne 0 -or
        -not (Test-Phase16MeasurementNumber $p.elapsed_ms) -or $p.elapsed_ms -le 0 -or
        $p.elapsed_ms -gt 60000 -or $null -eq $p.http_metadata) { return $result }
    $m = $p.http_metadata
    foreach ($field in @('response_code','size_download','size_upload','time_total',
                        'ssl_verify_result','num_redirects','proxy_used')) {
        if (-not (Test-Phase16MeasurementNumber $m[$field])) { return $result }
        if ($m[$field] -lt 0 -or ($field -ne 'time_total' -and [Math]::Floor($m[$field]) -ne $m[$field])) {
            return $result
        }
    }
    # Preserve validated numeric failure evidence without publishing throughput.
    $result.response_code = $m.response_code; $result.download_bytes = $m.size_download
    $result.upload_bytes = $m.size_upload; $result.curl_duration_ms = $m.time_total * 1000
    $result.ssl_verify_result = $m.ssl_verify_result
    # Only the expected HTTP 200 contract; redirects/204/206 are not full objects.
    if ($m.response_code -ne 200 -or $m.ssl_verify_result -ne 0 -or $m.num_redirects -ne 0 -or
        $m.proxy_used -ne 0 -or $m.time_total -le 0 -or $m.time_total * 1000 -gt $p.elapsed_ms -or
        -not (Test-Phase16MeasurementNumber $p.stdin_bytes)) { return $result }
    if ($Direction -ceq 'download') {
        if ($m.size_download -ne $ExpectedBytes -or $m.size_upload -ne 0 -or $p.stdin_bytes -ne 0) { return $result }
    } else {
        if ($m.size_upload -ne $ExpectedBytes -or $p.stdin_bytes -ne $ExpectedBytes -or
            $m.size_download -gt $ResponseMaxBytes) { return $result }
    }
    $transfer = Get-Phase16ThroughputSummary -BodyBytes $ExpectedBytes -ExpectedBytes $ExpectedBytes `
                    -ElapsedMs $p.elapsed_ms -TransferCompleted $true
    $result.status = 'measured'; $result.readiness = $transfer.readiness
    $result.payload_bytes = $ExpectedBytes; $result.duration_ms = $p.elapsed_ms; $result.mbps = $transfer.mbps
    $result.response_code = $m.response_code; $result.download_bytes = $m.size_download
    $result.upload_bytes = $m.size_upload; $result.curl_duration_ms = $m.time_total * 1000
    return $result
}

function Invoke-Phase16HttpMeasurement {
    # One explicit transfer only. NOT a live approval gate or 900s/series runner.
    # Future live use requires exact endpoint, binary checksum/version and approval.
    # No profiles, files or defaults; HTTPS certificate verification remains enabled.
    param($CurlPath, $Endpoint, $Direction, $ExpectedBytes, $InputBytes = [byte[]]@(),
          $ResponseMaxBytes = 65536, $TimeoutMs = 5000)
    $empty = Get-Phase16HttpSummary
    try {
        if ($CurlPath -isnot [string] -or -not [IO.Path]::IsPathFullyQualified($CurlPath)) {
            throw 'invalid_http_request'
        }
        $request = New-Phase16HttpRequest -Endpoint $Endpoint -Direction $Direction -ExpectedBytes $ExpectedBytes `
                       -InputBytes $InputBytes -ResponseMaxBytes $ResponseMaxBytes -TimeoutMs $TimeoutMs
    } catch { $empty.status = 'invalid_request'; return $empty }
    $p = Invoke-Phase16BoundedProcess -FilePath $CurlPath -ArgumentList $request.arguments `
             -InputBytes $request.input_bytes -MaxInputBytes $request.input_bytes.Length `
             -MaxOutputBytes 4096 -TimeoutMs $request.timeout_ms -CleanupReserveMs 500 -CurlMetadata $true
    $result = Get-Phase16HttpSummary -ProcessResult $p -Direction $Direction `
                  -ExpectedBytes $ExpectedBytes -ResponseMaxBytes $ResponseMaxBytes
    # Keep failure classification but never raw error contents or arbitrary statuses.
    if ($p.status -cin @('invalid_request','start_failed','nonzero_exit','timeout','output_limit',
                         'stderr_limit','io_error','cleanup_unconfirmed','metadata_invalid')) { $result.status = $p.status }
    return $result
}
