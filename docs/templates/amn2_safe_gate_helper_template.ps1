param(
  [string]$TargetIp = "89.185.80.166",
  [switch]$DryRun,
  [switch]$RunLive
)

$ErrorActionPreference = "Stop"

function Write-SafeLine {
  param([AllowEmptyString()][string]$Line)
  Write-Host $Line
}

function Get-SafeProbeUrls {
  param([Parameter(Mandatory=$true)][string]$TargetIp)

  return @(
    "http://${TargetIp}:3030/login",
    "http://${TargetIp}:3040/api/servers",
    "http://${TargetIp}:80/",
    "https://${TargetIp}:443/"
  )
}

function Assert-SafeProbeUrlShape {
  param([Parameter(Mandatory=$true)][string[]]$Urls)

  foreach ($url in $Urls) {
    if ($url -match '^https?:///' -and $url -notmatch '^https?://[^/]+/') {
      throw "Malformed probe URL: $url"
    }
    if ($url -notmatch '^https?://[^/:]+:\d+/') {
      throw "Probe URL is missing host or port: $url"
    }
  }
}

Write-SafeLine "AMN2 safe gate helper template"
Write-SafeLine "encoding_rule=ascii_prompts_or_utf8_with_bom"
Write-SafeLine "url_interpolation_rule=use_braced_TargetIp_colon_PORT"
Write-SafeLine "live_vps_ssh_performed=false"
Write-SafeLine "public_exposure_performed=false"
Write-SafeLine "config_delivery_performed=false"
Write-SafeLine "telegram_live_send_performed=false"
Write-SafeLine "secret_values_printed=false"

$ProbeUrls = Get-SafeProbeUrls -TargetIp $TargetIp
Assert-SafeProbeUrlShape -Urls $ProbeUrls

Write-SafeLine ""
Write-SafeLine "[dry] probe URL inspection"
foreach ($url in $ProbeUrls) {
  Write-SafeLine "probe_url=$url"
}
Write-SafeLine "probe_url_shape_status=passed"

if ($DryRun -or -not $RunLive) {
  Write-SafeLine "network_probe_performed=false"
  Write-SafeLine "live_body_present=false"
  Write-SafeLine "template_status=dry_inspection_only"
  exit 0
}

throw "This template has no live gate body. Create a gate-specific helper with explicit allowed scope."
