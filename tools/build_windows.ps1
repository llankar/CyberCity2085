param(
    [string]$OutputDirectory = "dist"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BuildOutput = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $OutputDirectory))
if (-not $BuildOutput.StartsWith($ProjectRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Build output must stay inside the project workspace."
}

Set-Location -LiteralPath $ProjectRoot
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed; build cancelled." }
python -m PyInstaller --noconfirm --clean --distpath "$BuildOutput" --workpath "build/windows-candidate" CyberCity2085.spec
if ($LASTEXITCODE -ne 0) { throw "Windows packaging failed." }

$Executable = Join-Path $BuildOutput "CyberCity2085\CyberCity2085.exe"
$SmokeReport = Join-Path $BuildOutput "packaged-smoke.json"
$SmokeProcess = Start-Process -FilePath $Executable -ArgumentList @("--smoke-test", "--smoke-report", "`"$SmokeReport`"") -WindowStyle Hidden -PassThru
if (-not $SmokeProcess.WaitForExit(120000)) {
    $SmokeProcess.Kill()
    throw "Packaged headless smoke timed out."
}
if ($SmokeProcess.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $SmokeReport)) {
    throw "Packaged headless smoke failed; inspect $SmokeReport."
}
$Smoke = Get-Content -LiteralPath $SmokeReport -Raw | ConvertFrom-Json
if ($Smoke.status -ne "ok") { throw "Packaged headless smoke reported failure." }
Write-Host "Build and headless smoke ready: $Executable"
