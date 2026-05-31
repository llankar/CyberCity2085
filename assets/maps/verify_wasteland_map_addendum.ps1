$ErrorActionPreference = 'Stop'

$required = @(
  'wasteland_city_11_ruined_transit_plaza.png',
  'wasteland_city_12_cratered_waterfront.png',
  'wasteland_outdoor_11_convoy_crossing.png',
  'wasteland_outdoor_12_salt_flat_ambush.png',
  'wasteland_inner_11_emergency_medbay.png'
)

$missing = @()

foreach ($name in $required) {
  $path = Join-Path $PSScriptRoot $name
  if (-not (Test-Path -LiteralPath $path)) {
    $missing += $name
    continue
  }

  $item = Get-Item -LiteralPath $path
  if ($item.Length -le 0) {
    $missing += $name
  }
}

if ($missing.Count -gt 0) {
  Write-Error ("Missing or empty files:`n" + ($missing -join "`n"))
}

Write-Host "Verified $($required.Count) wasteland addendum assets."
