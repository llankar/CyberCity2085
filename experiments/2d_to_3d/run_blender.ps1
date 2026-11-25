param(
    [Parameter(Mandatory=$true)][string]$Script,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$ScriptArguments
)
$ErrorActionPreference = 'Stop'
$labRoot = 'E:\CyberCity2085-3d-lab'
$scriptRoot = [System.IO.Path]::GetFullPath($PSScriptRoot) + [System.IO.Path]::DirectorySeparatorChar
$scriptPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $Script))
if (-not $scriptPath.StartsWith($scriptRoot,[System.StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw 'Choose a checked-in experiment script under this directory.'
}
foreach ($folder in @('tmp','cache\python','blender-user\config','blender-user\scripts','blender-user\extensions')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $labRoot $folder) | Out-Null
}
$env:TEMP = Join-Path $labRoot 'tmp'
$env:TMP = $env:TEMP
$env:XDG_CACHE_HOME = Join-Path $labRoot 'cache'
$env:PYTHONPYCACHEPREFIX = Join-Path $labRoot 'cache\python'
$env:BLENDER_USER_CONFIG = Join-Path $labRoot 'blender-user\config'
$env:BLENDER_USER_SCRIPTS = Join-Path $labRoot 'blender-user\scripts'
$env:BLENDER_USER_EXTENSIONS = Join-Path $labRoot 'blender-user\extensions'
$ErrorActionPreference = 'Continue'
& (Join-Path $labRoot 'tools\blender-4.5.17-windows-x64\blender.exe') --background --disable-autoexec --python-exit-code 1 --python $scriptPath -- @ScriptArguments
exit $LASTEXITCODE
