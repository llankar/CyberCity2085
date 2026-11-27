param(
    [string[]]$Maps = @(
        'city_exterior_billboard_avenue',
        'cybercity_street_15_billboard_avenue',
        'cybercity_street_16_billboard_avenue'
    )
)
$ErrorActionPreference = 'Stop'
$labRoot = 'E:/CyberCity2085-3d-lab'
$env:TEMP = Join-Path $labRoot 'tmp'
$env:TMP = $env:TEMP
$env:PYTHONPYCACHEPREFIX = Join-Path $labRoot 'cache/python'
$sharedTerrain = @{
    'cybercity_street_10_waterfront_docks' = 'cybercity_street_09_waterfront_docks'
    'cybercity_street_14_flood_prone_avenue' = 'cybercity_street_13_flood_prone_avenue'
}
$Maps = @($Maps | ForEach-Object {
    if ($sharedTerrain.ContainsKey($_)) { $sharedTerrain[$_] } else { $_ }
} | Select-Object -Unique)
foreach ($map in $Maps) {
    $output = Join-Path $labRoot "generated/phase2/billboard_avenues/$map"
    $floorOptions = @()
    if ($map.EndsWith('freight_yard') -or $map.StartsWith('wasteland_')) { $floorOptions += '--include-side-walls' }
    python (Join-Path $PSScriptRoot 'prepare_floor248.py') --map $map --output $output @floorOptions
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($map -in @('city_exterior_rooftop_access','city_rooftop_skybridge_spine',
                  'city_exterior_waterfront_docks','cybercity_street_04_waterfront_docks',
                  'cybercity_street_09_waterfront_docks','cybercity_street_13_flood_prone_avenue')) {
        python (Join-Path $PSScriptRoot 'rooftop_terrain.py') $map
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}
& (Join-Path $PSScriptRoot 'run_blender.ps1') -Script blender/billboard_avenues.py -ScriptArguments $Maps
exit $LASTEXITCODE
