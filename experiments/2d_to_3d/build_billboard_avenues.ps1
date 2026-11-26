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
foreach ($map in $Maps) {
    $output = Join-Path $labRoot "generated/phase2/billboard_avenues/$map"
    python (Join-Path $PSScriptRoot 'prepare_floor248.py') --map $map --output $output
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
& (Join-Path $PSScriptRoot 'run_blender.ps1') -Script blender/billboard_avenues.py -ScriptArguments $Maps
exit $LASTEXITCODE
