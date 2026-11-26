"""Assemble the selected local prototype without weights, caches or old takes."""
from pathlib import Path
import json
import re
import shutil

LAB = Path("E:/CyberCity2085-3d-lab")
REPO = Path(__file__).resolve().parents[2]
OUT = LAB / "deliveries/tactical_demo205"
PROJECT = OUT / "project"
assert OUT.resolve().is_relative_to(LAB.resolve())
PROJECT.mkdir(parents=True, exist_ok=True)
records = []


def copy(source, target):
    source, target = Path(source), Path(target)
    assert source.is_file(), source
    assert target.resolve().is_relative_to(OUT.resolve()), target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    records.append({"source": str(source), "file": str(target.relative_to(OUT)),
                    "bytes": target.stat().st_size})


def portable(text):
    return text.replace("E:/CyberCity2085-3d-lab/", "res://lab/").replace(
        "res://../../../assets/", "res://assets/")


# Preserve the existing scene implementations; only the delivered copies get
# portable resource roots and fixed selection options.
source = REPO / "experiments/2d_to_3d/godot"
pending, seen = ["contact204.tscn"], set()
while pending:
    name = pending.pop()
    if name in seen:
        continue
    seen.add(name)
    text = (source / name).read_text(encoding="utf8")
    pending += [p for p in re.findall(
        r"res://([\w./-]+\.(?:gd|tscn|gdshader))", text) if not p.startswith("../")]
    text = portable(text).replace("OS.get_cmdline_user_args()",
        'preload("res://delivery_options205.gd").arguments()')
    (PROJECT / name).write_text(text, encoding="utf8")

flags = ["--refined-stage", "--city-details", "--weights177", "--vtol178",
         "--impact179", "--wreck180", "--fall181", "--visible185",
         "--baked186", "--painted192", "--cannon193"]
(PROJECT / "delivery_options205.gd").write_text(
    'extends RefCounted\nstatic func arguments() -> PackedStringArray:\n'
    ' var result:=OS.get_cmdline_user_args()\n'
    ' for flag in ' + json.dumps(flags) + ':\n'
    '  if not flag in result:result.append(flag)\n return result\n', encoding="utf8")

models = {
    "sole_skin162": "human",
    "support167": "human",
    "rig177": "human",
    "robot193": "robot_actions",
    "showcase199": "environment",
    "vtol178": "vtol_actions",
    "crate_procedural": "crate_procedural",
    "generator01": "generator",
    "armored203": "armored_actions",
    "medic201": "medical_pack",
    "amjviz_wardrobe150": "human_actions",
    "firewarden_pistol01": "pistol",
}
phase = LAB / "generated/phase2"
for folder, stem in models.items():
    copy(phase / folder / (stem + ".glb"),
         PROJECT / "lab/generated/phase2" / folder / (stem + ".glb"))
    copy(phase / folder / (stem + ".blend"),
         OUT / "sources" / folder / (stem + ".blend"))

for file in ["modularity166/body_1.glb",
             "modularity166/body_0_helmet_restfixed.glb",
             "amjviz_modules153/p320.glb",
             "rocketbox_military03/motion01/pistol_fit01/fit_report.json",
             "amjviz_modules153/modules.json"]:
    copy(phase / file, PROJECT / "lab/generated/phase2" / file)
copy(phase / "modularity166/export_sources.blend",
     OUT / "sources/modularity166/export_sources.blend")
config = json.loads((phase / "amjviz_modules153/modules.json").read_text())
for asset in config["variants"].values():
    file = Path(asset["file"])
    copy(file, PROJECT / "lab" / file.relative_to(LAB))

def portable_metadata(value):
    if isinstance(value, dict):
        return {key: portable_metadata(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_metadata(item) for item in value]
    if isinstance(value, str):
        normalized = value.replace("\\", "/")
        if normalized.startswith("E:/CyberCity2085-3d-lab/"):
            return portable(normalized)
    return value


# Parse JSON before changing Windows paths: raw JSON may escape its slashes.
# Never change model bytes or metadata asset hashes.
for file in (PROJECT / "lab").rglob("*.json"):
    file.write_text(json.dumps(portable_metadata(json.loads(
        file.read_text(encoding="utf8"))), indent=2), encoding="utf8")

for file in PROJECT.glob("*.gd"):
    assert not re.search(r"[A-Z]:[\\/]", file.read_text(encoding="utf8")), file
runtime_config = json.loads((PROJECT / "lab/generated/phase2/amjviz_modules153/modules.json").read_text())
for asset in runtime_config["variants"].values():
    assert asset["file"].startswith("res://lab/"), asset
    assert (PROJECT / asset["file"][6:]).is_file(), asset

for file in (LAB / "sources/environment169/medical_box").rglob("*"):
    if file.is_file():
        copy(file, PROJECT / "lab" / file.relative_to(LAB))
for name in ["city_exterior_neon_market_alley.png",
             "city_exterior_neon_market_alley.walls.json"]:
    copy(LAB / "sources/tactical_map" / name,
         PROJECT / "lab/sources/tactical_map" / name)
audio = ["weapons/fire_pistol_01.wav", "weapons/fire_laser_cc0_01.wav",
         "movement/step_concrete_cc0_01.wav", "combat/impact_metal_cc0_01.wav",
         "combat/impact_organic_cc0_01.wav", "combat/melee_cc0_01.wav",
         "combat/explosion_small_cc0_01.wav", "technology/shield_cc0_01.wav"]
for file in audio:
    copy(REPO / "assets/audio/overhaul" / file,
         PROJECT / "assets/audio/overhaul" / file)

for folder in models:
    notice = phase / folder / "CREDITS.txt"
    if notice.exists():
        copy(notice, OUT / "notices" / folder / "CREDITS.txt")
copy(phase / "armored203/CREDITS.txt", OUT / "notices/armored203/CREDITS.txt")
for file in (phase / "contact204").iterdir():
    if file.suffix in [".png", ".json", ".gif", ".mp4"]:
        copy(file, OUT / "media" / file.name)
copy(phase / "armored203/comparison_native.png", OUT / "media/comparison_native.png")
for name in ["assemble_armored203.py", "medical_pack201.py", "roof_identity199.py",
             "correct_sole_skin162.py", "smooth_neural177.py",
             "rig_painted_robot189.py", "robot_gait.py", "robot_shutdown.py",
             "cannon_sockets193.py", "create_hardsurface_crate.py",
             "create_industrial_generator.py", "finish_vtol178.py"]:
    copy(REPO / "experiments/2d_to_3d/blender" / name, OUT / "source_scripts" / name)

engine = Path("C:/Users/llank/AppData/Local/Microsoft/WinGet/Packages/"
              "GodotEngine.GodotEngine_microsoft.Winget.Source_8wekyb3d8bbwe")
for name in ["Godot_v4.7.2-stable_win64.exe",
             "Godot_v4.7.2-stable_win64_console.exe"]:
    copy(engine / name, OUT / "tools" / name)

(PROJECT / "project.godot").write_text('''config_version=5
[application]
config/name="CyberCity 2085 - Experimental Tactical Demo"
run/main_scene="res://delivery205.tscn"
[display]
window/size/viewport_width=1920
window/size/viewport_height=1080
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
''')
(PROJECT / "delivery205.tscn").write_text('''[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://delivery205.gd" id="1"]
[node name="TacticalDemo" type="Node3D"]
script = ExtResource("1")
''')
(PROJECT / "delivery205.gd").write_text('''extends "res://contact204.gd"
var frame_seconds:Array[float]=[]
var ready_ms:=0
var summary_written:=false
func _ready() -> void:
 var start:=Time.get_ticks_msec()
 super._ready()
 ready_ms=Time.get_ticks_msec()-start
 delivery_folder=ProjectSettings.globalize_path("res://evidence/")
 DirAccess.make_dir_recursive_absolute(delivery_folder)
func _process(delta: float) -> void:
 if time_value>1 and delta>0:frame_seconds.append(delta)
 super._process(delta)
 if time_value>=30 and not summary_written:
  summary_written=true
  var total:=0.0
  for value in frame_seconds:total+=value
  FileAccess.open(delivery_folder+"native_summary.json",FileAccess.WRITE).store_string(JSON.stringify({"movie_mode":OS.has_feature("movie"),"sample_frames":frame_seconds.size(),"mean_fps":frame_seconds.size()/maxf(total,.001),"scene_ready_ms":ready_ms,"scope":"one native run on this machine; excludes first timeline second; no general hardware claim"}))
''')
(OUT / "Run.ps1").write_text(r'''param([switch]$Verify)
$ErrorActionPreference='Stop'
$bundle=$PSScriptRoot
foreach ($folder in @('cache','cache/tmp')) {
 New-Item -ItemType Directory -Force -Path (Join-Path $bundle $folder) | Out-Null
}
$env:TEMP=Join-Path $bundle 'cache/tmp';$env:TMP=$env:TEMP
$env:XDG_CACHE_HOME=Join-Path $bundle 'cache'
# Keep Godot's own shader/user cache on E: as well as TEMP.
$appData=[IO.Path]::GetFullPath([Environment]::GetFolderPath('ApplicationData'))
$projectName='CyberCity 2085 - Experimental Tactical Demo'
$source=[IO.Path]::GetFullPath((Join-Path $appData "Godot/app_userdata/$projectName"))
$target=[IO.Path]::GetFullPath((Join-Path $bundle 'cache/godot-userdata'))
if ([IO.Path]::GetPathRoot($bundle) -ne 'E:\' -or -not $source.StartsWith(($appData+'\'),[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($source) -ne $projectName -or -not $target.StartsWith(($bundle+'\cache\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected cache paths' }
$existing=Get-Item -LiteralPath $source -Force -ErrorAction SilentlyContinue
if ($existing -and -not $existing.LinkType) {
 $preserved=$target
 if (Test-Path -LiteralPath $preserved) { $preserved=Join-Path $bundle ('cache/userdata-preserved-'+[Guid]::NewGuid().ToString('N')) }
 $preserved=[IO.Path]::GetFullPath($preserved)
 if (-not $preserved.StartsWith(($bundle+'\cache\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected preservation target' }
 Move-Item -LiteralPath $source -Destination $preserved
 $existing=$null
}
New-Item -ItemType Directory -Force -Path $target | Out-Null
if (-not $existing) {
 New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($source)) | Out-Null
 New-Item -ItemType Junction -Path $source -Target $target | Out-Null
} elseif (-not ([IO.Path]::GetFullPath([string]$existing.Target[0])).StartsWith('E:\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Existing cache link is not on E:' }
$binary=if ($Verify) {'Godot_v4.7.2-stable_win64_console.exe'} else {'Godot_v4.7.2-stable_win64.exe'}
$ErrorActionPreference='Continue'
& (Join-Path $bundle "tools/$binary") --path (Join-Path $bundle 'project') --rendering-method gl_compatibility --resolution 1920x1080
exit $LASTEXITCODE
''')
(OUT / "Run.cmd").write_text('@echo off\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Run.ps1"\n')

(OUT / "README.txt").write_text("""CYBERCITY 2085 - DEMONSTRATION TACTIQUE EXPERIMENTALE
Double-cliquer sur Run.cmd. Attendre environ 35 secondes de chargement sur
la machine testee. La rencontre dure ensuite 30 secondes puis se ferme.
Relancer Run.cmd pour la revoir. Godot est inclus : aucune installation de
Python ou Godot n'est requise pour lancer ce dossier local.
La compatibilite sur un PC vierge n'a pas ete testee.
Il s'agit d'une rencontre mise en scene, pas de l'IA tactique de production.

project/: selected scene and its retained implementation dependencies.
sources/: editable packed Blender files, outside the Godot import tree.
project/lab/: actual runtime GLB models, embedded textures and source metadata.
media/: existing Full HD30 movie, GIF and clean captures.
source_scripts/: original authoring recipes; these still refer to the original
E: lab inputs and are not a bundled AI-generation environment. AI weights,
tool caches, intermediate takes and old experiments are deliberately excluded.
notices/: retained model notices. Nothing has been published.

Le lancement natif mesure environ 59,7 FPS ici, hors premiere seconde de
la sequence, sur RTX 5070 Ti. Ce n'est pas une mesure universelle.
Conserver le dossier sur E: pour y garder les ressources et caches.
Les recettes de source_scripts utilisent encore les entrees du laboratoire E:
d'origine. Les poids IA et l'environnement de generation ne sont pas inclus.

Restent ouverts : facades repetitives, visage duplique du soignant, qualite
globale des contacts et validation artistique. Aucun fichier de production
ni sauvegarde de campagne n'a ete modifie par la construction de ce dossier.
CHANTIER GLOBAL INCOMPLET.
""")
(OUT / "index.html").write_text('''<!doctype html><meta charset="utf-8">
<title>CyberCity 2085 - Tactical 3D prototype</title>
<style>body{max-width:1300px;margin:32px auto;background:#07141a;color:#e9f4f7;font:18px sans-serif}a{color:#39dce7}img,video{width:100%;height:auto}</style>
<h1>CyberCity 2085 - Tactical 3D prototype</h1>
<p>Run.cmd launches the selected local scene with the bundled engine.
This is a staged experimental encounter, not production AI.</p>
<video controls src="media/encounter_1080p30.mp4"></video>
<h2>Visible combat contacts</h2><img src="media/melee_sequence.png">
<h2>Cast at combat scale</h2><img src="media/comparison_native.png">
<p>Nominal 41/62px humans; sprite and model views differ.</p>
<h2>Models and sources</h2><ul>''' + "".join(
    f'<li>{folder}: <a href="sources/{folder}/{stem}.blend">Blender</a> / '
    f'<a href="project/lab/generated/phase2/{folder}/{stem}.glb">GLB</a></li>'
    for folder, stem in models.items()) + '''</ul>
<p>Local native run: about 59.7 FPS here; startup about 35 seconds.
No clean-PC or general hardware compatibility claim.</p>
<p>Remaining art: repeated architecture, main/medic face reuse and full-motion
contact quality. CHANTIER GLOBAL INCOMPLET.</p>''', encoding="utf8")
records = list({record["file"]: record for record in records}.values())
for record in records:
    record["bytes"] = (OUT / record["file"]).stat().st_size
(OUT / "manifest.json").write_text(json.dumps({
    "scope": "Selected local runtime and editable sources; no AI weights or campaign",
    "scripts": sorted(seen), "files": records,
    "bytes": sum(r["bytes"] for r in records)}, indent=2), encoding="utf8")
print("DELIVERY205_BUILT", OUT, "files", len(records),
      "bytes", sum(r["bytes"] for r in records))
