param([string]$Output='E:/CyberCity2085-3d-lab/generated/phase2/combat169/encounter.avi',[switch]$Architectural,[switch]$Refined,[switch]$MedicalContact,[switch]$CityDetails,[switch]$NeuralTrial,[switch]$SmoothedTrial,[switch]$VehicleFinish,[switch]$ImpactFinish,[switch]$WreckFinish,[switch]$FallFinish,[switch]$Presentation,[switch]$DistrictFinish,[switch]$FacadeAssemblies,[switch]$VisibleBays)
$ErrorActionPreference='Stop'
if ($Architectural -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/combat170/encounter.avi' }
if ($Refined -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/combat171/encounter.avi' }
if ($MedicalContact -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/contact173_final/encounter.avi' }
if ($CityDetails -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/city174/encounter.avi' }
if ($NeuralTrial -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/neural176/encounter.avi' }
if ($SmoothedTrial -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/neural177/encounter.avi' }
if ($VehicleFinish -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/vehicle178/encounter.avi' }
if ($ImpactFinish -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/impact179/encounter.avi' }
if ($WreckFinish -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/wreck180/encounter.avi' }
if ($FallFinish -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/fall181/encounter.avi' }
if ($Presentation -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/presentation182/encounter.avi' }
if ($DistrictFinish -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/district183/encounter.avi' }
if ($FacadeAssemblies -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/assemblies184/encounter.avi' }
if ($VisibleBays -and -not $PSBoundParameters.ContainsKey('Output')) { $Output='E:/CyberCity2085-3d-lab/generated/phase2/visible185/encounter.avi' }
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
if ($NeuralTrial) { $sceneArguments=@('--','--refined-stage','--city-details');$scene='res://neural176.tscn' }
if ($SmoothedTrial) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177');$scene='res://neural176.tscn' }
if ($VehicleFinish) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178');$scene='res://neural176.tscn' }
if ($ImpactFinish) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179');$scene='res://neural176.tscn' }
if ($WreckFinish) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180');$scene='res://neural176.tscn' }
if ($FallFinish) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180','--fall181');$scene='res://neural176.tscn' }
if ($Presentation) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180','--fall181');$scene='res://presentation182.tscn' }
if ($DistrictFinish) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180','--fall181','--district183');$scene='res://presentation182.tscn' }
if ($FacadeAssemblies) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180','--fall181','--assemblies184');$scene='res://presentation182.tscn' }
if ($VisibleBays) { $sceneArguments=@('--','--refined-stage','--city-details','--weights177','--vtol178','--impact179','--wreck180','--fall181','--visible185');$scene='res://presentation182.tscn' }
& $engine --path (Join-Path $PSScriptRoot 'godot') --rendering-method gl_compatibility --resolution 1920x1080 --write-movie $Output --fixed-fps 30 --quit-after 2000 $scene @sceneArguments
exit $LASTEXITCODE
