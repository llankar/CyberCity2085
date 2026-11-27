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
    if not model.is_file():
        continue
    scene = GODOT / entry["scene"].removeprefix("res://")
    renderer = GODOT / "laboratory247.gd"
    newest_input = max(path.stat().st_mtime_ns for path in (model, scene, renderer))
    if not image.is_file() or image.stat().st_mtime_ns < newest_input:
        jobs.setdefault(str(image), {"image": str(image), "scene": entry["scene"]})
print(json.dumps(list(jobs.values())))
'@

Push-Location $PSScriptRoot
try {
    $jobJson = $jobs | python -
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $pending = $jobJson | ConvertFrom-Json
    foreach ($job in ($pending | Select-Object -First $Limit)) {
        $started = [DateTime]::UtcNow
        $ErrorActionPreference = 'Continue'
        & powershell.exe -NoProfile -File ./run_godot.ps1 -Scene $job.scene -QuitAfter 120 2>&1
        $ErrorActionPreference = 'Stop'
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $capture = Get-Item -LiteralPath $job.image
        if ($capture.LastWriteTimeUtc -lt $started) {
            throw "Godot did not refresh the overview for $($job.scene)"
        }
        Write-Output "OVERVIEW_REFRESHED $($job.scene)"
    }
} finally {
    Pop-Location
}
