param([string]$Output='E:/CyberCity2085-3d-lab/generated/phase2/combat169/encounter.avi')
$ErrorActionPreference='Stop'
if (-not ([IO.Path]::GetFullPath($Output).StartsWith('E:\CyberCity2085-3d-lab\'))) { throw 'Keep experimental captures on E:' }
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$env:TEMP='E:\CyberCity2085-3d-lab\tmp';$env:TMP=$env:TEMP
$engine='C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$ErrorActionPreference='Continue'
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $Output --fixed-fps 30 --quit-after 2000 res://combat169.tscn
exit $LASTEXITCODE
