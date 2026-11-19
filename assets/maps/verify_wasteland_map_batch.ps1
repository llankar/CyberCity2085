$ErrorActionPreference = 'Stop'

$required = @(
  'wasteland_city_01_ruined_downtown.png',
  'wasteland_city_02_burned_market_block.png',
  'wasteland_city_03_collapsed_overpass.png',
  'wasteland_city_04_flooded_civic_square.png',
  'wasteland_city_05_scavenger_plaza.png',
  'wasteland_outdoor_01_dust_road_ambush.png',
  'wasteland_outdoor_02_ashfield_ruins.png',
  'wasteland_outdoor_03_wrecked_highway.png',
  'wasteland_outdoor_04_rusted_trainyard.png',
  'wasteland_outdoor_05_irradiated_basin.png',
  'wasteland_inner_01_abandoned_safehouse.png',
  'wasteland_inner_02_collapsed_tunnel.png',
  'wasteland_inner_03_ruined_clinic.png',
  'wasteland_inner_04_bunker_command_post.png',
  'wasteland_inner_05_looted_vault.png',
  'wasteland_inner_06_maintenance_depot.png',
  'wasteland_inner_07_apartment_shelter.png',
  'wasteland_inner_08_data_relay_room.png',
  'wasteland_inner_09_underground_market.png',
  'wasteland_inner_10_detention_block.png'
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

Write-Host "Verified $($required.Count) wasteland map assets."
