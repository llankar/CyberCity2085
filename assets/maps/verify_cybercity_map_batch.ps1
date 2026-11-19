$ErrorActionPreference = 'Stop'

$required = @(
  'cybercity_street_07_downtown_intersection.png',
  'cybercity_street_08_neon_market_alley.png',
  'cybercity_street_09_elevated_freeway.png',
  'cybercity_street_10_waterfront_docks.png',
  'cybercity_street_11_civic_plaza.png',
  'cybercity_street_12_transit_interchange.png',
  'cybercity_street_13_industrial_district.png',
  'cybercity_street_14_flood_prone_avenue.png',
  'cybercity_street_15_bridge_access.png',
  'cybercity_street_16_billboard_avenue.png',
  'cybercity_inner_06_blacksite_lab.png',
  'cybercity_inner_07_corporate_lobby.png',
  'cybercity_inner_08_police_records.png',
  'cybercity_inner_09_apartment_block.png',
  'cybercity_inner_10_penthouse_atrium.png',
  'cybercity_inner_11_cyber_cafe.png',
  'cybercity_inner_12_maintenance_tunnel.png',
  'cybercity_inner_13_warehouse_floor.png',
  'cybercity_inner_14_detention_block.png',
  'cybercity_inner_15_data_vault.png'
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

Write-Host "Verified $($required.Count) CyberCity map assets."
