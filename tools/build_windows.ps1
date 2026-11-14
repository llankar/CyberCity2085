$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Set-Location -LiteralPath $ProjectRoot
python -m pytest tests -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed; build cancelled." }
python -m PyInstaller --noconfirm --clean CyberCity2085.spec
if ($LASTEXITCODE -ne 0) { throw "Windows packaging failed." }

Write-Host "Build ready: $ProjectRoot\dist\CyberCity2085\CyberCity2085.exe"
