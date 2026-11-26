param([switch]$GameScale,[switch]$Equipped)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$env:TEMP='E:\CyberCity2085-3d-lab\tmp';$env:TMP=$env:TEMP
$output='E:/CyberCity2085-3d-lab/generated/phase2/rig175/actions.avi'
if ($GameScale) { $output='E:/CyberCity2085-3d-lab/generated/phase2/rig175/actions_game.avi' }
$sceneArguments=@()
if ($GameScale) { $sceneArguments=@('--','--game-scale') }
if ($Equipped) {
    $name=if ($GameScale) { 'actions_game.avi' } else { 'actions.avi' }
    $output=Join-Path 'E:/CyberCity2085-3d-lab/generated/phase2/rig176' $name
    if ($sceneArguments.Count -eq 0) { $sceneArguments=@('--') }
    $sceneArguments+=@('--equipped')
}
$engine='C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$ErrorActionPreference='Continue'
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $output --fixed-fps 30 --quit-after 400 res://unarmed175.tscn @sceneArguments
exit $LASTEXITCODE
