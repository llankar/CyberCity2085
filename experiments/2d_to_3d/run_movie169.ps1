param([string]$Output='E:/CyberCity2085-3d-lab/generated/phase2/combat169/encounter.avi',[switch]$Architectural)
$ErrorActionPreference='Stop'
if ($Architectural -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/combat170/encounter.avi' }
if (-not ([IO.Path]::GetFullPath($Output).StartsWith('E:\CyberCity2085-3d-lab\'))) { throw 'Keep experimental captures on E:' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$env:TEMP='E:\CyberCity2085-3d-lab\tmp';$env:TMP=$env:TEMP
$engine='C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$ErrorActionPreference='Continue'
$sceneArguments=@()
if ($Architectural) { $sceneArguments=@('--','--architecture170') }
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $Output --fixed-fps 30 --quit-after 2000 res://combat169.tscn @sceneArguments
exit $LASTEXITCODE
