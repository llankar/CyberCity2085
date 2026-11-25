param(
    [string]$Scene = 'res://comparison.tscn',
    [int]$QuitAfter = 0,
    [ValidateSet('gl_compatibility','mobile','forward_plus')][string]$RenderingMethod,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$SceneArguments
)
$ErrorActionPreference = 'Stop'
$labRoot = 'E:\CyberCity2085-3d-lab'
New-Item -ItemType Directory -Force -Path (Join-Path $labRoot 'tmp') | Out-Null
$env:TEMP = Join-Path $labRoot 'tmp'
$env:TMP = $env:TEMP
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$engine = 'C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$arguments = @('--path',(Join-Path $PSScriptRoot 'godot'),'--log-file',(Join-Path $labRoot 'tmp\godot_runtime.log'))
if ($RenderingMethod) { $arguments += @('--rendering-method',$RenderingMethod) }
if ($QuitAfter -gt 0) { $arguments += @('--quit-after',"$QuitAfter") }
$arguments += @($Scene,'--')
$ErrorActionPreference = 'Continue'
& $engine @arguments @SceneArguments
exit $LASTEXITCODE
