# CyberCity 2085 — experimental 2D to 3D pipeline

Status on 2026-11-24: **IN_PROGRESS — technical proof obtained, artistic
acceptance not reached**.

This experiment is isolated from the current game runtime. No existing asset,
map, combat rule or validated animation is replaced. Large and generated data
lives exclusively in `E:\CyberCity2085-3d-lab`.

## Mechanical forward walk study (batch91)

Run `run_blender.ps1 -Script blender/rig_charge_robot_idle.py -ScriptArguments
@('--walk')` from the experiment directory. It writes security_walk01 on E:;
without the flag it retains the existing Idle producer. Foot IK uses authored
mechanical controls, not human animation retargeting. Variable-length cable
arrays are fixed to their neutral segment counts in the derivative and bending
cables receive actual sampled surface corrections. Full source foot vertices
must remain stable during each stance interval and travel across the full clip.

Verify using `run_godot.ps1 -Scene res://surface_motion_check.tscn -QuitAfter 900
-SceneArguments @('--folder=E:/CyberCity2085-3d-lab/generated/phase2/security_walk01',
'--model-file=robot_walk.glb')`. Require fresh native_surface_check.json and the
positive EINAR_NATIVE_SURFACE_GATE_OK marker; name is historical shared tooling.
Review main.tscn with --model pointing to that GLB, --neutral, --clip=Walk and
--clip-fraction=.8. It is a forward nonloop study; world translation is currently
baked per mechanical joint. Do not add it to gameplay or force seamless looping.
Artistic acceptance, arm swing and full robot action coverage remain TODO.

## Mechanical strike and tactical review (batch92)

`run_blender.ps1 -Script blender/rig_charge_robot_idle.py -ScriptArguments
@('--melee')` produces security_melee01 on E: with one actual authored mechanical
left-hand strike/recovery clip. Target phases live in robot_strike.py; the source
wrist is explicitly oriented with the reach. This is not a complete combat action
or a fist/contact solver. Source hand displacement and all-source return are
asserted during export, then surface_motion_check.tscn verifies native deformation
against surface_reference.json as for Walk (model-file=robot_melee.glb).

`run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 3000 -SceneArguments
@('--rocketbox-motion-study','--robot-melee-study','--tactical','--sprite-review',
'--self-test','--capture=E:/CyberCity2085-3d-lab/generated/phase2/security_melee01/tactical_close.png')`
checks actual articulated reach/recovery, five human clips, selection and camera.
Use --robot-walk-study for the nonloop forward clip; --robot-idle-study retains
the prior source Idle. These flags are mutually exclusive. Forward native foot
displacement and hold-at-end are asserted rather than looping world motion.
Add --overview for20.736px human reference; default close reference62.208px.
Animations can be selected by keys; capture studies pause their requested pose.

## Authored garment PBR study (batch93)

Run `python acquire_jacket_leather.py` for ONE pinned2K CC0 Leather037 archive.
All downloads/caches/generated resources remain E:. Size/hash/redirect limits
are checked; extraction whitelists three maps, never extractall. A cached archive
and its maps must still match their reviewed hashes. `blender/audit_trebejo_jacket.py`
inventories true garment connectivity on an in-memory copy only.

`run_blender.ps1 -Script blender/retexture_trebejo_leather.py` bakes a source-seam
normal variant; add `-ScriptArguments @('--fresh-normal')` for recalculated smooth
normals/new leather normal. Outputs trebejo_leather01/02 respectively, original
garment remains unchanged. Existing bake helper now has opt-in preserve_source_uv;
old callers keep smart projection. New garment copies authored UVs for its bake.

`python verify_garment_retexture.py trebejo_leather02` verifies every original
position/UV triangle corner exactly, cyclic winding/multiplicity, embedded images,
unit normals and original attribution. Also run for trebejo_leather01. Native
`run_godot.ps1 -Scene res://trebejo_jacket_check.tscn -QuitAfter 600 -SceneArguments
@('--fresh-normal')` checks2K PBR material/geometry (.7m,18,400tris); --leather checks
variant01, no flag checks original1K source. Require fresh JSON/positive marker.
Use main.tscn --neutral --view=front/side/back with model path for actual renders.
These are standalone garments; no fitted/skinned character or art PASS implied.

## First shared-rig garment fitting study (batch94)

Run `run_blender.ps1 -Script blender/inspect_wardrobe_fit.py` for actual existing
rest landmarks, then `-Script blender/fit_authored_wardrobe.py` to generate
wardrobe_fit01/human.blend/.glb. It reuses the existing80-bone/five-action character,
fits the authored garment and transfers source triangle skin weights with
wardrobe_skinning.py. Original files remain unchanged. Source upper uniform is
alpha-hidden under the replacement; not a solved clothing/collision system.

`run_godot.ps1 -Scene res://rocketbox_motion_check.tscn -QuitAfter 3000
-SceneArguments @('--wardrobe-study')` verifies45sampled surfaces and complete
Death->Idle cloth reset. `-Script blender/check_wardrobe_intersections.py` runs
the separate Blender opaque-surface BVH diagnostic; its positive script execution
does NOT imply no collision. Current10,569overlap pairs require hip/pants correction.
Partial-alpha hair and continuous/self collisions are outside that audit.

Comparison scene --wardrobe-study loads this first human study; use --tactical
--sprite-review --self-test and a source robot flag for the calibrated stage.
Do not call this accepted Rook art or generate the Raider from it yet.

## Environment verified

- GPU: NVIDIA GeForce RTX 5070 Ti, 16,303 MiB, driver 621.24.
- WSL2: Ubuntu 24.04.
- GPU compute: PyTorch 2.11.0 + CUDA 12.8, compute capability 12.0; a real
  2048×2048 CUDA matrix multiplication passed.
- Blender: official portable Blender 4.5.17 LTS under
  `E:\CyberCity2085-3d-lab\tools`; archive SHA-256
  `282B9BFC14065D6341C0D70D83992F80BDE09D99E0099BFF260C94BBEC93803D`
  matched Blender's published checksum. Headless `bpy` check passed.
- Godot: 4.7.2 stable; experimental GLB load check passed headlessly.
- ComfyUI: existing installations detected at `E:\comfyui\ComfyUI` and
  `E:\comfyui2\ComfyUI`; no Image-to-3D node was found during the audit.

## Compatibility and licensing decision

| Candidate | Local compatibility | License finding | Decision |
| --- | --- | --- | --- |
| TripoSR | About 6 GB VRAM, Linux/WSL, single image | MIT covers code and pretrained model | Selected for the first proof |
| TRELLIS | Linux, **at least 16 GB VRAM**; this GPU is exactly at the published minimum | Models and most code MIT, submodules have their own licenses | Deferred until the lightweight path is measured |
| TripoSG | Linux image-to-mesh path | Root is MIT, but bundled FlashVDM/Hunyuan license explicitly excludes use in the EU | Rejected for this French workstation pending legal clarification |

TripoSR is single-view. It cannot truthfully be described as exploiting the
available multidirectional character sheets. A separate multi-view candidate
must therefore pass license and 16 GB compatibility checks before Rook or the
Raider is accepted.

## Source manifest

The experiment copies, without modifying, these real project resources:

- crate: `assets/units/mission_objective_city_09_safe_deposit_crate_512.png`
- industrial machine: `assets/units/mission_objective_wasteland_04_scrap_generator_512.png`
- robot: `assets/units/robot_combat_512.png`
- Rook: `assets/ui/portraits/agent_male_14.png`
- Raider Grunt: `assets/units/enemy_raider_grunt_512.png`
- vehicle: `assets/units/vehicle_aerial_military_04_vtol_stealth_dropship_512.png`

## First measured result: crate

- TripoSR input: 512 px project illustration.
- Raw result: 139,894 vertices, 175,876 faces, non-watertight mesh, UV texture
  1024×1024.
- Peak host RSS: 4,145,420 KiB on the successful textured run.
- A separate cached 128-resolution, non-textured inference measured 1,429 MiB
  idle and 3,808 MiB peak total GPU use through `nvidia-smi`, a 2,379 MiB
  delta. This is evidence for that exact mode only, not a claim about peak
  texture-baking usage.
- Timings after weights were cached: model initialization 17.8 s, preprocessing
  2.3 s, inference 24.9 s, mesh extraction 3.3 s, texture baking 39.4 s. OBJ
  serialization on the Windows-mounted `E:` volume was unusually slow (226.6 s).
- Blender result: 20,000 faces, normalized to 1 metre, Eevee preview, 2.50 MB
  `.blend`, 2.15 MB `.glb`.
- Godot: external GLB loaded by `GLTFDocument` in the independent experiment;
  headless exit code 0.
- Visual assessment: recognizable hard-surface volume and usable baked colour,
  but soft edges, surface noise and imperfect source orientation. **NOT
  ARTISTICALLY ACCEPTED**.

## Six-object prototype result

All six requested sources now have real Blender and GLB files. Every GLB loaded
through the independent Godot 4.7.2 scene with exit code 0.

| Asset | Raw faces | Optimized faces | GLB bytes | Visual decision |
| --- | ---: | ---: | ---: | --- |
| Crate | 175,876 | 20,000 | 2,155,040 | recognizable, soft/noisy; reject for final art |
| Industrial machine | 249,824 | 19,996 | 2,589,964 | severe surface noise; reject |
| Robot | 157,298 | 34,999 | 2,872,904 | collapsed anatomy; reject |
| Rook | 141,060 | 29,999 | 2,428,112 | portrait reconstructed as a bust/blob; not riggable |
| Raider Grunt | 64,020 | 29,999 | 2,262,444 | collapsed lateral form; not riggable |
| Vehicle | 86,980 | 30,000 | 2,418,656 | recognizable silhouette, melted details; reject |

The five-object batch took 18 minutes 36 seconds with 4,142,528 KiB peak host
RSS. Warm neural inference took 0.36–0.39 seconds per later image, while OBJ
serialization took 81–324 seconds per object. This confirms that the current
text OBJ stage on the mounted E: volume is the main throughput bottleneck.

The humanoid rigging test stops at its mandatory anatomy gate: neither generated
humanoid has a complete separable body or plausible joints. Adding a skeleton,
weights and five animations would create misleading placeholder data, not a
valid rigging test. `HUMANOID-RIG-01` is therefore **BLOCKED** until a licensed
multi-view reconstruction produces acceptable anatomy.

## 3D-to-sprite alternative

`experiments/2d_to_3d/blender/render_atlas.py` renders eight transparent
isometric directions from one Blender source and assembles them into a single
horizontal PNG atlas. The crate proof generated eight 256×256 frames and one
2048×256 atlas successfully. Static orientation rendering is verified; animated
atlas rendering remains blocked by the absence of an acceptable rigged model.

## Reproduction

The current external lab layout is:

```text
E:\CyberCity2085-3d-lab\
  cache\ downloads\ models\ outputs\ repos\ sources\ tmp\ tools\ venvs\ wheels\
```

TripoSR commit tested: `107cefdc244c39106fa830359024f6a2f1c78871`.
The upstream texture baker requires the small compatibility patch stored in
`experiments/2d_to_3d/patches`. `torchmcubes` is built CPU-only because WSL has
the CUDA runtime but not the full `nvcc` toolkit; neural inference remains on
the GPU. This adds a few seconds to mesh extraction and avoids a large toolkit
installation.

Blender processing example:

```powershell
& E:\CyberCity2085-3d-lab\tools\blender-4.5.17-windows-x64\blender.exe `
  --background --factory-startup `
  --python experiments\2d_to_3d\blender\process_mesh.py -- `
  --input E:\CyberCity2085-3d-lab\outputs\triposr\crate\0\mesh.obj `
  --output-dir E:\CyberCity2085-3d-lab\outputs\blender\crate `
  --name crate --target-faces 20000 --size-m 1.0
```

## Open acceptance work

- Find and verify a genuinely multi-view solution for humanoids.
- Retopologize an accepted humanoid before rigging; AI topology is not suitable
  for deformation as-is.
- Rig and skin one humanoid, then verify idle, walk, shoot, melee and death.
- Extend the verified eight-direction static atlas renderer to action/frame
  strips once a valid rig exists.
- Measure GPU peak VRAM during inference, Godot frame cost and shadow/material
  behavior in a visible isometric comparison.
- Review generated assets and their source rights before any distribution.

No larger migration should be proposed until those items pass visual review.

## Primary references

- Blender downloads and LTS releases: https://www.blender.org/download/ and
  https://www.blender.org/releases/4-5/
- TripoSR official repository and MIT statement:
  https://github.com/VAST-AI-Research/TripoSR
- TRELLIS requirements and licensing notes:
  https://github.com/microsoft/TRELLIS/blob/main/README.md
- TripoSG official repository and root license:
  https://github.com/VAST-AI-Research/TripoSG and
  https://github.com/VAST-AI-Research/TripoSG/blob/main/LICENSE
- TripoSG bundled FlashVDM/Hunyuan license containing the EU territorial
  exclusion: https://github.com/VAST-AI-Research/TripoSG/blob/main/triposg/LICENSE
- PyTorch CUDA installation matrix: https://pytorch.org/get-started/locally/


## Batch95: original-resolution professional scan study

Acquisition is bounded to four provenance-pinned Nathan files, with fresh official
author/license validation and cache hashes. No bulk library installation.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python experiments/2d_to_3d/acquire_nathan_candidate.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/inspect_nathan_candidate.py
python experiments/2d_to_3d/verify_nathan_candidate.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 3000 -SceneArguments @('--nathan-study','--robot-melee-study','--tactical','--sprite-review','--self-test')
```

The native source/export comparison must hold identical authored Walk poses; default
source standing and stopped export T-bind pose are different. Real8K JPEG bytes
are preserved. Native sampled skin errors and pixel differences are observations,
not a substitute for eye/material/outfit/identity artistic review. Only original
Walk exists on Nathan; no inferred human combat action set.

run_godot.ps1 now configures a lab-only userdata junction to physical E storage,
including shader cache/logs. Existing lab folder migration requires no live Godot,
exact source/target containment and every file hash verified before replacement.
No production userdata or driver-global shader cache changes. GPU sampler records
GPU-wide memory with live PIDs; it does not claim exclusive model allocation.

## Batch96: measured rest-pose wardrobe fitting

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_nathan_anatomy.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_nathan_wardrobe.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://surface_motion_check.tscn -QuitAfter 300 -SceneArguments @('--folder=E:/CyberCity2085-3d-lab/generated/phase2/nathan_wardrobe01','--model-file=human.glb')
```

Actual garment comes from existing licensed wardrobe study. Similarity transforms
align measured A/T bone segments, then weights transfer from professional scan's
actual surface. Skin/export verification passes but shoulder fit remains visibly
FAIL: local normal clearance pushes distort cloth. Do not accept or generalize it.
The source has separate eye surfaces and face joints; no nude modular anatomy or
missing detailed PBR maps assumed.

## Batch97: bounded cloth fitting alternatives (art FAIL)

`fit_nathan_wardrobe.py --smooth-fit` retains original authored geometry and smooths
only clearance displacement, output nathan_wardrobe02. `--landmark-fit` interpolates
measured old/new joint positions with depth anchors, output03. Both variants loaded
in Godot and front captures inspected; shoulders remain inadequate. Do not promote
either or infer deformation acceptance from previously checked01. Tests cover
mathematical invariants and failures, not clothing artistry.
