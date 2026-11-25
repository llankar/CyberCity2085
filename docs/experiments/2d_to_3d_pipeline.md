# CyberCity 2085 — experimental 2D to 3D pipeline

Status on 2026-11-24: **IN_PROGRESS — technical proof obtained, artistic
acceptance not reached**.

This experiment is isolated from the current game runtime. No existing asset,
map, combat rule or validated animation is replaced. Large and generated data
lives exclusively in `E:\CyberCity2085-3d-lab`.

## Authored armor body-action study (batch106)

Contact study114: first run `run_blender.ps1 -Script blender/inspect_scanned_grip.py`
on the111 equipped source, then `run_blender.ps1 -Script blender/fit_scanned_contacts.py`.
The latter creates a new seven-clip candidate under E:scanned_armor_contact01;
analytic arm IK rejects unreachable targets, preserves lengths, and retracts
the weapon65mm so the offhand can reach. Index CCD is an explicit fit study,
not a joint-limit or collision solver. Run the existing pistol fitter with
`--contact-study`; it MUST retain the original wrist-local grip, because the
bent forearm no longer defines barrel aim. Native authored-motion check,
pistol combined/runtime checks and comparison stage accept `--contact-study`.
Source head/hair verifiers use the same flag. Preserve their scoped results;
native import fidelity does not prove anatomical/artistic acceptance.

Robot saved-file roundtrip study112: `run_blender.ps1 -Script
blender/roundtrip_robot_bundle.py` opens the actual packed security_bundle01
Blend and writes only E:security_roundtrip01. All six animated owners must have
the same five NLA tracks. Move the entire imported strip with frame_start_ui
to remove its one-frame offset; frame_start alone extends it. Restore exact
source mesh node names through source GLB mesh identities, without guessed
suffix stripping. Export at120Hz (common multiple of source24/30Hz) and compare
with `bundle_action_check.tscn --robot-bundle --saved-blend-roundtrip`.
Re-export may split seam vertices, so this opt-in gate compares sampled surface
points against full opposite clouds in both directions. Original index-based
bundle gate remains intact. Native thresholds stay .0001 for skin transforms
and .0005m for sampled surfaces. Failure evidence must remain explicit; saving
and loading a Blend does not establish faithful animation roundtripping.

Resolved by113: before export, re-sample quaternion F-curves using shortest-arc
SLERP at quarter source frames. Blender's component-linear interpolation would
otherwise differ from glTF spherical interpolation even with120Hz export. Static
CONSTANT tracks must be uniform; unsupported varying STEP is rejected. Source
Blend stays unchanged. Actual native five-clip gate now passes; see113 register
for hashed output, measured errors and exact scope. Artistic robot acceptance
remains separate from this reproducibility check.

Batch111 continuation: run `run_blender.ps1 -Script blender/build_scanned_shoot.py`
after the scanned head/hair studies, then
`run_blender.ps1 -Script blender/fit_unvanquished_pistol.py -ScriptArguments @('--scanned-shoot')`.
Generated files stay on E: under `scanned_armor_shoot01`. Body has seven clips;
the equipped derivative deliberately contains only Shoot. Never infer exporter
filtering from NLA mute alone. Validate `authored_motion_check.tscn` with
`--scanned-shoot-study`, then `rocketbox_pistol_check.tscn` with the same flag,
both without and with `--runtime-attachment`. The latter checks17 actual times
against source prop vertices under a nonzero actor placement. Independent stage:
`comparison.tscn --scanned-shoot-study --robot-action-bundle --vtol-motion-study
--tactical --self-test --sprite-review --shoot-preview`. Check positive markers
and fresh hashed JSON, not only process exit status. Source geometry verifiers
`verify_scanned_head.py --shoot-study` and `verify_maxwell_hair.py --shoot-study`
must preserve the original six actions and source surfaces. This is a firing
fit study, not accepted trigger/offhand contact or final Rook artwork.

Run `run_blender.ps1 -Script blender/bake_unvanquished_actions.py` only after105
source acquisition/conversion. It preserves source author export timing, bakes
evaluated constrained body poses to a separate shared game rig, retains source
actions in the packed Blender file and writes six clips on E: unvanquished_motion01.
No artificial Shoot/Melee/Cover/Heal/PSI. Facial constrained shear is approximated
by TRS: inspect the recorded matrix error separately from sampled skin error;
2mm sampled skin is a technical tolerance, never artistic acceptance.

Run `run_godot.ps1 -Scene res://authored_motion_check.tscn -QuitAfter300` (PowerShell
argument is `-QuitAfter 300`). Require fresh matching-SHA native_motion_check.json
and UNV_NATIVE_AUTHORED_MOTION_OK, not merely exit0. Native import must retain120fps;
30fps resampling failed the source surface gate. Durations and Death->Idle reset
are checked. Samples cover nine times per clip, not exhaustive collision proof.

Optional independent comparison flags: `--unvanquished-motion-study
--robot-action-bundle --vtol-motion-study --tactical --self-test --sprite-review`.
Human keys U/A/K expose source Run/Attack/Crouch; Attack is not advertised as a
finished armed Shoot. Original hand/torso game composition and grip remain open.
Preview uses existing main.tscn; positive/negativeZ camera labels are camera axes,
not anatomical orientation proof. No production runtime integration.

Saved Blender reproducibility: run `blender/roundtrip_authored_human.py` through
the Blender wrapper, then authored_motion_check.tscn with --saved-blend-roundtrip.
The actual saved Blend is reexported and hash-checked unchanged. Batch107 GLB is
byte-identical; durations, source skin samples and reset pass natively too.
This does not establish art acceptance or reproducibility of other source rigs.

`blender/audit_authored_facing.py` measures this posed eye/head forward, roughly
Godot-Z. Existing preview --view=back is camera-negativeZ and shows its face.
Use --neutral for white ambient/gray background instead of default cyan preview.
Generic camera-axis labels are not anatomical labels; no model rotation needed.

Authored weapon composition experiment108: pinned source character.cfg must exist
on E: (SHA recorded in progress). `bake_unvanquished_actions.py --weapon-study`
creates a separate one-clip unvanquished_weapon01; default six-clip output remains
byte-identical. `authored_motion_check.tscn --weapon-study` verifies composed Blender
skin export, not source engine parity. `blender/fit_unvanquished_pistol.py` binds
the actual existing CC0 pistol using finger landmarks, writes equipped Blend/GLB.
`rocketbox_pistol_check.tscn --unvanquished-study` checks all nine weapon parts at
nine times. Neutral closeup shows raised arm obscures face and unfinished contact:
artistic FAIL, not accepted armed gameplay. Full original source rig remains intact.

## Scanned head with authored armor (batch109)

Run `blender/audit_scanned_head_fit.py`, then `blender/assemble_scanned_head.py`
through the Blender wrapper. Input Nathan and authored action Blend files remain
unchanged. Head selection follows ALL neck descendants (including mouth), not a
name-substring list. Fit in REST bind space: both anatomies face Blender-Y; source
animation can turn root180degrees. Body/armor and six source actions are retained.
New assembly contribution BY-SA4; original SA3/BY4 notices remain in source/exports.
New facial expressions/blinks are not implemented by the neck/head rebind.

Run `python verify_scanned_head.py` from this directory, then native
`authored_motion_check.tscn --scanned-head-study`. Require fresh matching-SHA
source_preservation_check/native_motion_check JSON, complete head topology/UV/photo,
unchanged body tracks and actual native positive marker. Normal storage component
error is explicitly bounded, not claimed exact. Art/contact are separate.

Use comparison.tscn --scanned-head-study --robot-action-bundle --vtol-motion-study
--tactical --self-test --sprite-review for actual62.208px tactical review. Head is
Nathan, not accepted Rook; no Raider/general production. Neutral main.tscn views
back/side/front correspond to face/profile/back at the authored Idle0 pose.

Embedded Blender ignores Python cache environment variables unless opted into
system environment. The wrapper explicitly sets sys.pycache_prefix on E: instead;
`blender/check_python_cache.py` verifies an actual imported module cache on E:.
No desktop automation or production runtime changes.

## Authored Maxwell hair (batch110)

Run `python inspect_hair_archive.py` then `python acquire_maxwell_hair.py` from
this experiment directory. HTTP ranges pin publisher archive size/ETag and fetch
only reviewed members; standard ZIP CRC and recorded per-file SHA are checked.
Publisher source headers/pack metadata and CC-BY FAQ qualify the asset, preserving
the short-label vs version-basis distinction. All downloaded ranges/sources are E:.

Run `blender/fit_maxwell_hair.py` through the Blender wrapper. Uses real authored
765vertex hair on the existing scanned head, not generated primitive clumps. The
profile-calibrated fit and smooth normals are documented; source triangles/UV/map
remain intact. Native lit alpha MASK material exports directly without patching.
Run `python verify_maxwell_hair.py`, `python verify_scanned_head.py --hair-study`,
then authored_motion_check.tscn --scanned-hair-study. Require fresh matchingSHA
evidence; material/skin fidelity is not scalp-contact/art acceptance.

The comparison scene accepts --scanned-hair-study with existing robot/vehicle/
tactical/self-test/sprite-review flags. Neutral main.tscn views back/side/front
at Idle0 correspond to anatomical face/profile/back. First floating-fit PNGs are
kept separately; current identity, wardrobe and firing pose remain unfinished.

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

## Batch98: authored mechanical Hit study

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/rig_charge_robot_idle.py -ScriptArguments @('--hit')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://surface_motion_check.tscn -QuitAfter 500 -SceneArguments @('--folder=E:/CyberCity2085-3d-lab/generated/phase2/security_hit01','--model-file=robot_hit.glb','--mechanical-hit-check')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 800 -SceneArguments @('--nathan-study','--robot-hit-study','--tactical','--sprite-review','--self-test')
```

Require both MECHANICAL_HIT_NATIVE_OK and EINAR_NATIVE_SURFACE_GATE_OK, no script
assertion, fresh native JSON tied to GLB hash. Process exit0 alone is insufficient.
Actual full native heel/toe geometry must remain planted, head recoil>5cm and all
checked geometry recover<.1mm. This .8s articulated study is separate from gameplay
damage/destruction or final robot art. Independent lab keyboard6 selects real Hit
only when present; it does not alias absent human actions.

## Batch99: articulated mechanical shutdown

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/rig_charge_robot_idle.py -ScriptArguments @('--shutdown')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://surface_motion_check.tscn -QuitAfter 800 -SceneArguments @('--folder=E:/CyberCity2085-3d-lab/generated/phase2/security_death01','--model-file=robot_death.glb','--mechanical-shutdown-check')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1000 -SceneArguments @('--nathan-study','--robot-shutdown-study','--tactical','--sprite-review','--self-test')
```

Require fresh matched GLB hash evidence and positive MECHANICAL_SHUTDOWN_NATIVE_OK
plus surface gate, no assertion. Source cage first buckles through actual rig/IK,
then falls to a measured flat-floor contact; no original resources modified. Cable
Array merging changes at compressed poses: derivative disables proximity merge,
preserves neutral corner correspondence onto underlying rings and sampled morphs.
Prefix inspection script reproduces the cause. Death is a flat-ground mechanical
shutdown study, not inter-part collision/debris/gameplay acceptance. All5robot clips
currently separate studies; unified skeletal animation bundle remains next.

## Batch100: one real five-action robot model

```powershell
python experiments/2d_to_3d/bundle_robot_actions.py
python experiments/2d_to_3d/verify_einar_action_bundle.py --robot-bundle
./experiments/2d_to_3d/run_blender.ps1 -Script blender/import_einar_action_bundle.py -ScriptArguments @('--robot-bundle')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://bundle_action_check.tscn -QuitAfter 2000 -SceneArguments @('--robot-bundle')
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1500 -SceneArguments @('--nathan-study','--robot-action-bundle','--tactical','--sprite-review','--self-test')
```

Outputs security_bundle01/robot_actions.glb and packed editable Blend; require fresh
verification/native_bundle_check/source hashes and ROBOT_NATIVE_ACTION_BUNDLE_OK.
Reuses existing Einar bundler/verifier/importer with opt-in robot configuration;
default Einar regeneration was verified byte-identical. Explicit sparse expansion
validates glTF override indices and views before copying; strict reader unchanged.
All union corrective weights are driven/reset in every clip. Same native model
supports Idle/Walk/Melee/Hit/Death; missing Shoot is not synthesized. Foot contacts
and flat-floor shutdown scope remain as recorded; no final robot art acceptance.
Blender re-export and robot atlas generation remain open.

## Batch101: eight-view atlas from the same mechanical model

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/inspect_robot_action_timing.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/render_rocketbox_atlas.py -ScriptArguments @('--robot-bundle')
python experiments/2d_to_3d/verify_rocketbox_atlas.py --robot-bundle
./experiments/2d_to_3d/run_godot.ps1 -Scene res://atlas_review.tscn -QuitAfter 300 -SceneArguments @('--atlas-dir=E:/CyberCity2085-3d-lab/generated/phase2/security_bundle01/atlas','--manifest=Walk_atlas.json','--action=walk','--self-test')
```

Five sheets /160transparent frames, actual imported scene strips start1 rather
than0. Source duration and all rig/morph strip ranges must agree. Signed root travel
is measured from actual source foot endpoints before compensating in atlas space;
Walk remains nonloop. --action=Walk can rerender a bounded single action; unsupported
action names fail rather than silently doing nothing. Source model hashes retained.
Render calibration uses the current professional-human study height, so physical
1.95m robot is64.895px against62.208px human. Orbit views/final art remain unaccepted
until facing and artistic review; do not replace production sprites.

## Batch102: measured robot atlas facing sectors

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/map_robot_atlas_facings.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://atlas_review.tscn -QuitAfter 300 -SceneArguments @('--atlas-dir=E:/CyberCity2085-3d-lab/generated/phase2/security_bundle01/atlas','--manifest=Walk_atlas.json','--action=walk','--production-order','--self-test')
```

Postprocess after a new atlas render: measures matching camera projections with
actual Walk source forward, retains all PNG pixels and enriches five manifests.
Uses existing screen sectors/facing_y_scale2. Source Blend and PNG SHA256 evidence
is external on E. Mathematical/native facing PASS does not establish final robot
identity, materials or full artistic animation acceptance.

## Batch103: actual VTOL moving components

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/animate_vtol.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://vehicle_action_check.tscn -QuitAfter 300
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1200 -SceneArguments @('--nathan-study','--robot-action-bundle','--vtol-motion-study','--tactical','--sprite-review','--self-test')
```

Outputs vtol_motion01, original vtol01 unchanged.48meshes/six pivots/three real
clips, keys7/8/9 in lab only. Explicit constant transform tracks are mandatory for
object animation resets; default glTF optimization omitted neutral gear channels
and was rejected by source/native geometry checks. Require fresh matched-hash
native_motion_check and VTOL_NATIVE_ARTICULATION_OK, not process exit0 alone.
Large standalone preview can use --camera-distance=14 --ortho-size=11. Gear stow
has no authored bays/collision acceptance; rotor speed is slowed mechanical
inspection. No production vehicle or flight/gameplay changes.

## Batch104: source-faithful eye material diagnosis

```powershell
./experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_nathan_eyes.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/refine_nathan_eye_material.py
python experiments/2d_to_3d/verify_nathan_eye_material.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://surface_motion_check.tscn -QuitAfter 300 -SceneArguments @('--folder=E:/CyberCity2085-3d-lab/generated/phase2/nathan_eyes01','--model-file=human.glb')
./experiments/2d_to_3d/run_godot.ps1 -RenderingMethod forward_plus -Scene res://eye_material_check.tscn -QuitAfter 200
```

Uniform clearcoat extension is present in the GLB but native4.7.2 imports left its
feature disabled in both tested renderers. eye_material_check applies the explicit
lab-only uniform_clearcoat bridge then verifies properties; reports distinguish
native import from bridged result. Native preview needs --gltf-uniform-clearcoat
for that bridge; --nathan-eyes-study stage applies it only to this derivative.
Textured clearcoat variants are refused. Scalar roughness imported natively.
Actual source iris/sclera already detailed/blue-gray, no missing-eye texture claim.
Original textured geometry, skin and Walk bytes preserved; new eye material does
not establish accepted character quality. Same-lighting source/refined closeups on E.
References: https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_materials_clearcoat
and https://github.com/godotengine/godot/blob/4.7/modules/gltf/gltf_document.cpp .

## Batch105: authored tactical wardrobe source

```powershell
python experiments/2d_to_3d/acquire_unvanquished_human.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_unvanquished_human.py
./experiments/2d_to_3d/run_blender.ps1 -Script blender/convert_unvanquished_human.py
./experiments/2d_to_3d/run_godot.ps1 -Scene res://authored_armor_check.tscn -QuitAfter 300
./experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1400 -SceneArguments @('--unvanquished-study','--robot-action-bundle','--vtol-motion-study','--tactical','--sprite-review','--self-test')
```

Acquisition requires explicit shipped model/armor author/license rows, not global
project policy or upcoming model credits. Originals/primary legalcode/hash manifest
on E. Derivative is neutral authored21part armor/body with122bone source skin,
under CC BY-SA3.0. Legacy spec maps not yet physically converted; material/style
acceptance and source segmented/HandDelta animation assembly remain open. No
production changes or Nathan combination. Static qualification has no fake clips.
