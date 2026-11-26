param([string]$Output='E:/CyberCity2085-3d-lab/generated/phase2/combat169/encounter.avi',[switch]$Architectural,[switch]$Refined,[switch]$MedicalContact,[switch]$CityDetails)
$ErrorActionPreference='Stop'
if ($Architectural -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/combat170/encounter.avi' }
if ($Refined -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/combat171/encounter.avi' }
if ($MedicalContact -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/contact173_final/encounter.avi' }
if ($CityDetails -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/city174/encounter.avi' }
if (-not ([IO.Path]::GetFullPath($Output).StartsWith('E:\CyberCity2085-3d-lab\'))) { throw 'Keep experimental captures on E:' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
& (Join-Path $PSScriptRoot 'configure_godot_cache.ps1')
$env:TEMP='E:\CyberCity2085-3d-lab\tmp';$env:TMP=$env:TEMP
$engine='C:\Users\llank\AppData\Local\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe\Godot_v4.7.2-stable_win64_console.exe'
$ErrorActionPreference='Continue'
$sceneArguments=@()
if ($Architectural) { $sceneArguments=@('--','--architecture170') }
if ($Refined) { $sceneArguments=@('--','--refined-stage') }
$scene='res://combat169.tscn'
if ($MedicalContact) { $sceneArguments=@('--','--refined-stage');$scene='res://contact173.tscn' }
if ($CityDetails) { $sceneArguments=@('--','--refined-stage','--city-details');$scene='res://contact173.tscn' }
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $Output --fixed-fps 30 --quit-after 2000 $scene @sceneArguments
exit $LASTEXITCODE
