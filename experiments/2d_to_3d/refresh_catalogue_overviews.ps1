param([ValidateRange(1,122)][int]$Limit = 122)

$ErrorActionPreference = 'Stop'
$jobs = @'
import json
from catalogue_test_assets import GODOT, catalogue_environment

entries = json.loads((GODOT / "preproduction_catalog.json").read_text())
jobs = {}
for entry in entries:
    model = catalogue_environment(entry["map"])
    image = model.with_name("godot_overview.png")
    if model.is_file() and (not image.is_file() or image.stat().st_mtime < model.stat().st_mtime):
        jobs.setdefault(str(image), {"model": str(model), "image": str(image), "scene": entry["scene"]})
print(json.dumps(list(jobs.values())))
'@

Push-Location $PSScriptRoot
try {
    $jobJson = $jobs | python -
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $pending = $jobJson | ConvertFrom-Json
    foreach ($job in ($pending | Select-Object -First $Limit)) {
        $ErrorActionPreference = 'Continue'
        & powershell.exe -NoProfile -File ./run_godot.ps1 -Scene $job.scene -QuitAfter 120 2>&1
        $ErrorActionPreference = 'Stop'
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $capture = Get-Item -LiteralPath $job.image
        $model = Get-Item -LiteralPath $job.model
        if ($capture.LastWriteTimeUtc -lt $model.LastWriteTimeUtc) {
            throw "Godot did not refresh the overview for $($job.scene)"
        }
        Write-Output "OVERVIEW_REFRESHED $($job.scene)"
    }
} finally {
    Pop-Location
}
