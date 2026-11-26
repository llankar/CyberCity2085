param([switch]$Rigid190,[switch]$Arm191)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$env:TEMP='E:\CyberCity2085-3d-lab\tmp';$env:TMP=$env:TEMP
$engine='C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$ErrorActionPreference='Continue'
$output='E:/CyberCity2085-3d-lab/generated/phase2/robot189/actions.avi';$sceneArguments=@()
if ($Rigid190) { $output='E:/CyberCity2085-3d-lab/generated/phase2/robot190/actions.avi';$sceneArguments=@('--','--rigid190') }
if ($Arm191) { $output='E:/CyberCity2085-3d-lab/generated/phase2/robot191/actions.avi';$sceneArguments=@('--','--arm191') }
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $output --fixed-fps 30 --quit-after 400 res://robot189.tscn @sceneArguments
exit $LASTEXITCODE
