param(
    [string]$OutputDirectory = "dist",
    [string]$GodotExecutable = $env:CYBERCITY_PACKAGE_GODOT,
    [string]$InnoCompiler,
    [string]$ScratchRoot,
    [switch]$SkipTests,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BuildOutput = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $OutputDirectory))
$WorkPath = Join-Path $ProjectRoot "build/windows-candidate"
if ($ScratchRoot) {
    $ScratchRoot = (Resolve-Path -LiteralPath $ScratchRoot).ProviderPath
    $RunRoot = Join-Path $ScratchRoot ("cybercity-build-" + [guid]::NewGuid().ToString("N"))
    $BuildOutput = [System.IO.Path]::GetFullPath((Join-Path $RunRoot $OutputDirectory))
    $WorkPath = Join-Path $RunRoot "build"
} else {
    $RunRoot = $ProjectRoot
}
if (-not $BuildOutput.StartsWith($RunRoot.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Build output must stay inside the selected build directory."
}

Set-Location -LiteralPath $ProjectRoot
if (-not $GodotExecutable -or -not (Test-Path -LiteralPath $GodotExecutable -PathType Leaf)) {
    throw "Pass -GodotExecutable with the standalone Windows Godot executable."
}
$env:CYBERCITY_PACKAGE_GODOT = (Resolve-Path -LiteralPath $GodotExecutable).Path
if ($ScratchRoot) {
    $TempPath = Join-Path $RunRoot "temp"
    New-Item -Path $TempPath -ItemType Directory -Force | Out-Null
    $env:TEMP = $TempPath
    $env:TMP = $TempPath
    $env:APPDATA = Join-Path $RunRoot "appdata"
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $RunRoot "cache"
}
if (-not $SkipTests) {
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed; build cancelled." }
}

# PyInstaller writes routine progress messages to stderr. Windows PowerShell 5
# promotes those messages to terminating errors while ErrorActionPreference is
# Stop, before its actual process exit code can be checked.
$PreviousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    python -m PyInstaller --noconfirm --clean --distpath "$BuildOutput" --workpath "$WorkPath" CyberCity2085.spec
    $PyInstallerExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $PreviousErrorActionPreference
}
if ($PyInstallerExitCode -ne 0) { throw "Windows packaging failed." }

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

if (-not $SkipInstaller) {
    if (-not $InnoCompiler) {
        $InnoCandidates = @(
            (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
            (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
            (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
        )
        $InnoCompiler = $InnoCandidates | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -First 1
    }
    if (-not $InnoCompiler -or -not (Test-Path -LiteralPath $InnoCompiler -PathType Leaf)) {
        throw "Inno Setup 6 is required to create the autonomous installer. Pass -InnoCompiler or use -SkipInstaller explicitly."
    }
    $InstallerOutput = Join-Path $BuildOutput "installer"
    New-Item -Path $InstallerOutput -ItemType Directory -Force | Out-Null
    $BuildVersion = (git rev-parse --short=8 HEAD).Trim()
    & $InnoCompiler "/DSourceDir=$(Join-Path $BuildOutput 'CyberCity2085')" "/DOutputDir=$InstallerOutput" "/DBuildVersion=$BuildVersion" (Join-Path $ProjectRoot "installer\CyberCity2085.iss")
    if ($LASTEXITCODE -ne 0) { throw "Windows installer compilation failed." }
    $Installer = Join-Path $InstallerOutput "CyberCity2085-Setup.exe"
    if (-not (Test-Path -LiteralPath $Installer -PathType Leaf)) { throw "Installer output is missing: $Installer" }
    Write-Host "Autonomous installer ready: $Installer"
}
