$ErrorActionPreference = 'Stop'
$labRoot = 'E:/CyberCity2085-3d-lab'
$env:TEMP = Join-Path $labRoot 'tmp'
$env:TMP = $env:TEMP
$env:PYTHONPYCACHEPREFIX = Join-Path $labRoot 'cache/python'
$maps = @(
    'city_exterior_billboard_avenue',
    'cybercity_street_15_billboard_avenue',
    'cybercity_street_16_billboard_avenue'
)
foreach ($map in $maps) {
    $output = Join-Path $labRoot "generated/phase2/billboard_avenues/$map"
    python (Join-Path $PSScriptRoot 'prepare_floor248.py') --map $map --output $output
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& (Join-Path $PSScriptRoot 'run_blender.ps1') -Script blender/billboard_avenues.py
exit $LASTEXITCODE
