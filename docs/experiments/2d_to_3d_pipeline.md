# CyberCity 2085 — experimental 2D to 3D pipeline

Status on 2026-11-24: **IN_PROGRESS — technical proof obtained, artistic
acceptance not reached**.

This experiment is isolated from the current game runtime. No existing asset,
map, combat rule or validated animation is replaced. Large and generated data
lives exclusively in `E:\CyberCity2085-3d-lab`.

## Coherent authored human source (batch143)

Preferred current game-source study145 keeps the author's actual Godot GLB
deformation instead of re-exporting the high-level Rigify source. It removes
unused joint branches while retaining all weighted ancestors.706->262skin joints,
all four source clips unchanged, exact0.0m native difference in6,830,032vertex
comparisons at88source key/midpoint times. This separate PASS does not repair or
supersede the original Blender Rigify fidelity FAIL recorded below.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python experiments/2d_to_3d/prune_dead_joints.py
& experiments/2d_to_3d/run_godot.ps1 -Scene res://amjviz_pruning_check.tscn
& experiments/2d_to_3d/run_blender.ps1 -Script blender/import_amjviz_game145.py
& experiments/2d_to_3d/run_godot.ps1 -QuitAfter 180 -SceneArguments @(
 '--amjviz-pruned-study','--robot-action-bundle','--source-opacity-study',
 '--vtol-motion-study','--vtol-finish-study','--tactical','--facades-study',
 '--sprite-review','--self-test',
 '--capture=E:/CyberCity2085-3d-lab/generated/phase2/amjviz_pruned145/tactical.png')
```

Require AMJVIZ_PRUNED_NATIVE_EQUIVALENCE_PASS, matching current source/output
hashes in native_equivalence.json and the usual stage positive markers. Output
human.glb is28.2MB; human.blend is an editable262linear-bone game source with all
26file images packed and four original actions. These remain private Royalty Free
assets on E:, not files to push/distribute publicly as a raw model/scene pack.
Shoot/melee/death and final Rook identity are still TODO. No current FPS/VRAM
benchmark or new atlas is implied by this model reduction.

Runtime bake144 is a rejected/unverified candidate, not the reviewed source143.
It reduces706to160bones and keeps original authored image payloads, but the strict
92pose native deformation check FAILS. Preserve that failure rather than selecting
it as the scene default. Reproduce targeted diagnostics on E::

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_amjviz_rig144.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/export_amjviz_runtime144.py
python experiments/2d_to_3d/prepare_amjviz_runtime144.py
& experiments/2d_to_3d/run_godot.ps1 -Scene res://amjviz_runtime_check.tscn
```

The raw export is unshifted_export.glb; prepared human.glb retains pose accessor
bytes while shifting each clip's time origin and restoring exact author Godot
compressed images/materials. Re-running preparation reads the explicit raw file,
not a previously processed candidate. Both scripts accept --all-bones-diagnostic
to use the separate amjviz_full144 folder (not a source-fidelity fix).
Blender export script --reset-reference and/or --linear-diagnostic are read-only
reference measurements, exiting before export. Pass matching flags to the native
checker: these alternate references are diagnostic, not permission to accept an
altered source. Combined flags have a separate reset_linear result. Final native
gate failures return1. Positive process exit alone never proves a pose check.
Source requires resetting transforms between clips; substantial residual errors
remain even after doing so. B-Bone curves explain only part. Next investigate
actual bone head/tail transforms, interpolation and inherited affine transforms
before building segmented/corrective deformation. A direct segment split needs
up to9vertex influences; blindly truncating to8can discard5.1%of weight.

The incompatible Diesel neck patch is a rejected diagnostic. The new first-human
source study uses the complete AmJViZ CyberPunk Rigged character, retaining its
actual integrated anatomy, clothing, PBR textures and original Rigify animation.
It is not yet final Rook and does not contain shoot/melee/death clips.

Source and license:
https://www.blendkit.com/asset-gallery-detail/ebd01e7e-ebd8-4c74-88f0-6c0e3ccc0806/
https://www.blendkit.com/docs/licenses/licensing-faq/
Royalty Free, not CC0: private source files and raw scenes must not be pushed or
redistributed as an asset pack. Games require assets not directly/easily
extractable; rendering to sprites is another explicitly supported output route.

Reproduce without desktop automation:

```powershell
& experiments/2d_to_3d/acquire_amjviz_source.ps1 -IncludeBlenderSource
$env:PYTHONDONTWRITEBYTECODE='1'
python experiments/2d_to_3d/inspect_amjviz_source.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/inspect_amjviz_blend143.py
& experiments/2d_to_3d/run_godot.ps1 -QuitAfter 180 -SceneArguments @(
 '--amjviz-study','--robot-action-bundle','--source-opacity-study',
 '--vtol-motion-study','--vtol-finish-study','--tactical','--facades-study',
 '--sprite-review','--self-test',
 '--capture=E:/CyberCity2085-3d-lab/generated/phase2/rook_anatomy143/amjviz_tactical.png')
```

Native smoke must print AMJVIZ_SOURCE_DISPATCH_OK, COMPARISON_INPUT_TEST_OK and
COMPARISON_CAPTURE 0 without unexpected assertions. Combining --amjviz-study with
--generated-atlas-review must reject: the old atlas is a different human. Source
hashes/inventory/credits live on E: and in the experimental progress register.
No current-source314pose or sustained-performance proof yet. Next work is genuine
Rigify deformation baking/optimization and complete combat animation integration,
then neutral art/contact review and only then new atlases/cohort expansion.

## Authored armor body-action study (batch106)

New first-human alternative117: `acquire_diesel_candidate.py` follows the author's
normal zero-price direct-download flow for one reviewed GLB. Rejects server errors,
quarantine and oversized/non-GLB payloads; does not bypass gates or purchase.
`run_blender.ps1 -Script blender/prepare_diesel_candidate.py` packs an editable
source-preserving candidate on E:. It is a source T-pose, not invented animation.

Sustained review-stage measurement117: comparison `--benchmark-output=<E:phase2
path.json>` records a five-second native drawn-frame interval, source GLB hashes,
UTC bounds, flags and actual viewport/window. Run `sample_gpu_memory.ps1` concurrently
with configurable SampleCount/IntervalMilliseconds; defaults remain24/400ms.
`verify_benchmark_window.py` checks current117scene hashes and rejects absent live
GPU overlap or inconsistent clocks/frame counts. GPU measurements are global,
never exclusive process attribution or a guaranteed peak. Artistic acceptance
and actual production combat performance remain separate.

Rigid environment116: after `prepare_tactical_inputs.py`, run
`run_blender.ps1 -Script blender/build_tactical_facades.py`. This generates
E:tactical_facades01/facades.blend and facades.glb from the original627cell map
footprint. Direct batched mesh buffers keep seven render meshes; no mass per-cube
Blender operators. `facade_check.tscn` verifies actual native GLB ray coverage
and roof height over all1120source cell centres, independent of report counts.
Comparison accepts optional `--facades-study` alongside the existing tactical,
contact, robot/VTOL and sprite-review flags. Original gray-volume mode remains
available without the flag. The floor is still the original image reference,
materials use constant PBR factors, and ornament clearance/art remain separate
from the body-cell coverage check. No production collision/LOS/navigation change.

Contact review115: use preview `main.tscn` with existing neutral/model options
and `--contact-review=E:/CyberCity2085-3d-lab/generated/phase2/scanned_armor_contact01/contact_review01`.
This captures four actual camera axes at17Shoot times and hashes the loaded model.
`review_contact_captures.py` validates complete distinct coverage/current SHA
and assembles four sheets, preserving originals. `blender/audit_scanned_contacts.py`
measures evaluated selected hand vertices against actual weapon triangles and
reports limited closed-part ray parity, not general collision freedom.
The fitter now uses bounded planar index IK (95/75degree rig-design bounds) and
front trigger-edge target; a simple capped CCD attempt was rejected for10mm error.
These bounds do not prove full finger anatomy, skin contact or professional art.

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
# Batch118: complete-outfit scanned-head diagnostic

Batch124 material study: run_blender.ps1 `-Script blender/rook_material_study.py`.
No new asset download. Uses actual game Rook portrait as direction; bakes existing
source colors through Blender, retains source mesh/UV and PBR normal/rough maps.
Native checker/comparison both accept --rook-material-study. First-head quality
is still unaccepted. preview main.tscn optional --geometry-normals-only is a
diagnostic; it does not alter any asset. review_cyborg_normals.py creates a separate
E:rook_normals01 diagnostic with unchanged positions; inspected result did not
resolve the head defects and must not be treated as an accepted fix.

Batch123 full first-character action study: run_blender.ps1 with
`blender/retarget_cyborg_actions.py` after batch121. Existing licensed Quaternius
UAL files on E: are required; no new download. Output cyborg_actions01 contains
all six actual clips plus freshly sampled source references. Native checker
`res://cyborg_ready_check.tscn` takes --actions-study; require the positive
CYBORG_ACTIONS_NATIVE_GEOMETRY_PASS marker and hash-matched native_actions_validation.json.
The floor envelope probes quarter-keys in Blender; native comparison samples
half-keys for melee/death. Neither is a continuous physics/contact proof.
Comparison accepts --cyborg-actions-study and --melee-preview/--death-preview.
SourceRun's small sole penetration and first-character art remain open.

Batch122 atlas: existing render_rocketbox_atlas.py now accepts
`--cyborg-fire-study --action=PistolFireStudy --samples=10` through run_blender.ps1
ScriptArguments. Verify using `python experiments/2d_to_3d/verify_rocketbox_atlas.py
--cyborg-fire-study`. Native `res://atlas_review.tscn` with
`--atlas-dir=E:/CyberCity2085-3d-lab/generated/phase2/cyborg_fire01/atlas`
`--manifest=PistolFireStudy_atlas.json --self-test --frame=4` reviews actual peak.
Capture must remain inside that atlas folder. Default robot/old human four-sample
behavior remains available. All PNG/JSON/credits remain on E:; no production
atlas overwrite, facing-map or artistic acceptance is implied.

Batch121 firing: run_blender.ps1 `-Script blender/build_cyborg_fire.py` after
batch120. Run native checker `res://cyborg_ready_check.tscn -- --fire-study`
through run_godot.ps1 SceneArguments. Require CYBORG_FIRE_NATIVE_GEOMETRY_PASS
and fresh hash-matched native_fire_validation.json, including measured20mm slide
travel and peak-fire-to-ready reset. New scene flag --cyborg-fire-study aliases
Shoot to PistolFireStudy; --shoot-preview freezes its actual recoil peak.
No trigger-finger, full-contact or final art approval is implied.

Batch120 equipped candidate: use run_blender.ps1 with
`blender/inspect_cyborg_combat_anatomy.py`, `blender/build_cyborg_ready_pose.py`,
then `blender/assemble_cyborg_gloved_pistol.py`. All outputs remain on E:.
Native gate `res://cyborg_ready_check.tscn` compares actual deformed mesh bounds
against freshly generated native_reference.json; require positive
CYBORG_READY_NATIVE_GEOMETRY_PASS and hash-matched native_ready_validation.json.
Comparison scene --cyborg-pistol-study selects this study and dispatches its ready
clip as Idle; Shoot stays unavailable. Body walk/run retained. The selected real
CC BY-SA3 hand geometry changes the derivative's redistribution notice from the
upstream CC0-only body. No new source files are downloaded by these DCC scripts.

Batch119 alternative: run `python experiments/2d_to_3d/acquire_grab3d_cyborg.py`
once for the reviewed public CC0/AI-assisted source. Then use run_blender.ps1
with `blender/prepare_grab3d_cyborg.py` and `blender/optimize_grab3d_cyborg.py`.
Native gate: run_godot.ps1 `-Scene res://cyborg_lod_check.tscn -QuitAfter 180`;
require CYBORG_LOD_NATIVE_POSES_PASS and fresh native_pose_retention.json.
Comparison scene accepts --grab3d-cyborg-lod, --robot-action-bundle,
--vtol-motion-study, --tactical, --facades-study, --sprite-review, --self-test.
Use --capture=E:/CyberCity2085-3d-lab/generated/phase2/grab3d_cyborg_lod01/tactical_scene.png.
This source only has walk/run; no simulated combat actions. Keep source24fps
and normalize NLA strip origin when re-exporting; changing FPS speeds up motion.

Run `run_blender.ps1 -Script blender/inspect_diesel_anatomy.py`, then
`blender/assemble_diesel_scanned_head.py` and `blender/verify_diesel_head_fit.py`
through the same wrapper. Existing acquired Diesel and Nathan sources are
required on E:. Output is `generated/phase2/diesel_scanned_head01` on E: only.
Godot main.tscn accepts `--model=<that folder>/human.glb --neutral
--view=front|side|back --capture=<that folder>/neutral_<view>.png`.
This candidate preserves real source geometry and licenses but fails the current
Rook artistic target. Do not infer animation or final art acceptance from the
source-retention assertion check. No new animation clips are present.

## First equipped actor: full-cadence atlas experiment (batch130)

The current independent source is E:/CyberCity2085-3d-lab/generated/phase2/
rook_run129/human.blend, not the older Diesel/MPFB or first Fire-only studies.
It combines the acquired body/hair, MIT head, BY-SA3 glove, CC0 pistol and actual
licensed motion; keep the complete CREDITS.txt with all derived outputs.
This source remains a prototype, not final Rook art or a production replacement.

From the repository in PowerShell:

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/render_rocketbox_atlas.py -ScriptArguments @('--rook-run-study')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/map_robot_atlas_facings.py -ScriptArguments @('--rook-run-study')
python experiments/2d_to_3d/verify_rocketbox_atlas.py --rook-run-study
```

This renders five actions at native24fps in eight views into the source folder's
atlas subdirectory: Ready48,Walk24,Fire19,Melee25,Death59frames/view,1400samples
total. Loop endpoints are not duplicated; nonloops retain their final pose and
Fire includes recoil at sourceframe8. RGBA frames are192x192; projected reference
height remains62.208px. Largest sheet1536x11328. PNGs are derived from actual mesh
renders, not pasted 2D art. The facing map is measured from actual Head/headfront
rest landmarks and camera projections using the existing facing_y_scale2 sectors.
No production scene, sprite, animation or rule is changed.

For each clip replace the manifest/action arguments below, using lower-case
action identifiers. The native test writes hash-bound evidence in the atlas
folder; --combat-scale displays at1.0 instead of the review enlargement1.5.

```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://atlas_review.tscn -QuitAfter 150 -SceneArguments @('--atlas-dir=E:/CyberCity2085-3d-lab/generated/phase2/rook_run129/atlas','--manifest=DeathStudy_atlas.json','--action=deathstudy','--combat-scale','--production-order','--self-test','--frame=58','--capture=E:/CyberCity2085-3d-lab/generated/phase2/rook_run129/atlas/native_DeathStudy.png')
```

After native checks for CombatReadyStudy,walk,PistolFireStudy,MeleeStudy,DeathStudy:

```powershell
python experiments/2d_to_3d/verify_rocketbox_atlas.py --rook-run-study --native-proof
```

The final verifier checks every source/sheet crop, alpha borders, sample times,
24fps, source Blender hash, attribution file hash, facing permutation, recoil
peak and the five current native manifest/PNG hashes. It proves the technical
atlas alternative on the first actor. It does not approve contact, hairline,
anatomical fidelity, material quality or use in the production game.

## Synchronized tactical comparison (batch131)

Use the actual scene with the current generated atlas overlay:

```powershell
& experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1800 -SceneArguments @('--generated-atlas-review','--robot-action-bundle','--vtol-motion-study','--tactical','--facades-study','--sprite-review','--self-test','--compare-action=PistolFireStudy','--compare-time=0.3333333333333333','--capture=E:/CyberCity2085-3d-lab/generated/phase2/rook_run129/atlas/synchronized_fire131.png')
```

Without compare-action/time, the existing1..5human controls drive the actual
AnimationPlayer. The helper reads its clock; generated24fps and original sprite
cadence remain distinct. Original Samurai has no shoot animation, so the original
picture is hidden and its missing clip labelled during Fire. Unsupported generated
Run is also hidden. No substitute action or normalized playback speed is invented.
The overlay is a comparison reference, not a sixth physical actor or Raider model.

The default comparison camera is snapped to one atlas view at elevation0.6;
eight-view facing is quantized during orbit. Other elevations/perspective cannot
be represented by these images and hide the overlays explicitly. Zoom recomputes
their scale/foot anchors from actual camera projection, including close62.208px
and overview20.736px. The existing production sprite rim/ground-shadow shader is
still not reproduced; do not infer identical lighting/materials from this review.

The native self-test covers120camera/action/time cases, original cadence, three
real AnimationPlayer.advance cases, missing actions, fixed-elevation restrictions
and close/overview scaling. Hash-bound proof and frozen-state JSON remain in the
E: atlas folder. Native screenshots are reviewed separately from those assertions.

## Portrait-driven undercut candidate (batch133)

`blender/trim_rook_undercut.py` derives rook_undercut133 from rook_run129 on E:.
It clips the genuine source quiff at the nape/temples, fits only a narrow root
band to the actual scalp and explicitly binds remaining/cut vertices to Head.
All non-hair geometry/UV hashes are asserted unchanged. Original portrait
agent_male_14.png is a reference only; it is not pasted into the model.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/trim_rook_undercut.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_actor_reference.py -ScriptArguments @('--folder','rook_undercut133','--dense-run')
& experiments/2d_to_3d/run_godot.ps1 -Scene res://cyborg_ready_check.tscn -QuitAfter 1200 -SceneArguments @('--undercut-study')
& experiments/2d_to_3d/run_godot.ps1 -Scene res://comparison.tscn -QuitAfter 1500 -SceneArguments @('--undercut-study','--robot-action-bundle','--vtol-motion-study','--tactical','--facades-study','--sprite-review','--self-test','--capture=E:/CyberCity2085-3d-lab/generated/phase2/rook_undercut133/tactical.png')
```

The129atlas still depicts the older hair. Combining --generated-atlas-review
with --undercut-study is deliberately rejected until matching atlas generation
is performed. Native314pose bounds are technical evidence; haircut likeness and
whole-character final art remain separate from that test.

### Lossless robot packaging study134

`compact_glb.py` repacks aligned embedded bufferViews and shares byte-identical
payloads. It preserves indices, geometry, animation, UVs, materials and image
bytes; unknown binary extensions are rejected. Source Blender remains in
security_bundle01. The derivative and notices live only on E:security_compact134.
This reduces disk/download size20.2%, not proven VRAM or draw-call cost.

```powershell
python experiments/2d_to_3d/compact_glb.py E:/CyberCity2085-3d-lab/generated/phase2/security_bundle01/robot_actions.glb E:/CyberCity2085-3d-lab/generated/phase2/security_compact134/robot_actions.glb
python experiments/2d_to_3d/verify_compact_robot.py
```

Verifier requires ten prior native captures: source/compact each for
Idle,Walk,Melee,Hit,Death at fraction0.5 using main.tscn --neutral --view=front.
Files are source_CLIP.png/log and compact_CLIP.png/log in security_compact134.
All five pairs decode to identical pixels. Full comparison scene can opt in with
--robot-action-bundle --compact-robot-study; default source stays unchanged.

### Vehicle fitted-panel/PBR study135

Original paint maps (not downloaded/licensed third-party textures) and eight
fitted aft hull plates are separate from the unchanged48mesh articulated source.
PNG maps, packed editableBLEND, embedded GLB and notices live on E:vtol_finish135.
Final vehicle art, landing-bay clearance and performance remain unaccepted.

```powershell
python experiments/2d_to_3d/vehicle_paint.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/finish_vtol_panels.py
& experiments/2d_to_3d/run_godot.ps1 -Scene res://vehicle_action_check.tscn -QuitAfter 600 -SceneArguments @('--vtol-finish-study')
```

Comparison scene opt-in: --vtol-motion-study --vtol-finish-study with existing
tactical/facades flags. For whole-vehicle neutral review, main.tscn accepts
--model=E:/CyberCity2085-3d-lab/generated/phase2/vtol_finish135/vtol_actions.glb
--neutral --focus-height=1 --ortho-size=12. The default portrait-sized camera
is unsuitable for this8m vehicle. Actual native_motion_check.json is GLB-hash
bound; rerun it after every export, even when generated paint maps are identical.

### Read-only robot alpha audit136

```powershell
python experiments/2d_to_3d/audit_robot_alpha.py
```

Outputs E:security_alpha136/alpha_audit.json plus first-material UV footprint
and sourceRGBA diagnostic images. It reads actual basecolor TEXCOORD_1 and
interleaved vertex/index buffers. Wrapped UV or transformed texture inputs are
rejected rather than silently mapped incorrectly.41/124conservative triangle
footprints contain nonopaque texels; only3expanded two-texel margins are opaque.
No entire basecolor image is opaque. This is not exact native GPU raster/mipmap
coverage, not proof of visible holes and not permission to strip all BLEND modes.
No derivative GLB is written. Next material change must inspect authored source
alpha and actual native filtered edges, preserving legitimate translucency.

### Source-proven robot opacity137

Source tracing resolves118constant-one adapter-alpha objects,4documented opaque
visor approximations and2dynamic lettering decals. This is stronger evidence
than footprint rasterization alone. The137derivative restores122opaque modes
and retains both decalsBLEND. It changes rendering intentionally; binary geometry,
UVs,weights,animation and original image data are unchanged. Source BLEND remains
untouched and editable derivative disconnects only those122alpha inputs.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_robot_source_alpha.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/restore_robot_source_opacity.py
python experiments/2d_to_3d/verify_robot_opacity.py
python experiments/2d_to_3d/verify_benchmark_window.py --folder security_opaque137 --batch 137
```

Native verifier requires prior main.tscn captures for five clips (Idle,Walk,Melee,
Hit,Death), --neutral --view=front --clip-fraction=0.5. Save CLIP.png/log under
E:security_opaque137. It compares SHA-bound source GLBs and actual compact134
baseline images. Comparison scene opts in with --robot-action-bundle
--source-opacity-study; current vehicle uses --vtol-motion-study
--vtol-finish-study. Add --benchmark-output=E:/CyberCity2085-3d-lab/generated/phase2/security_opaque137/benchmark137.json
and concurrent sample_gpu_memory.ps1 outputgpu137.json to reproduce current
five-second timestamp-correlated measurement. Current303.878fps/global2600..2693
MiB observations are neither an optimization gain nor production acceptance.

### Actual single-neck geometry candidate138

Neutral clay confirmed that pointed Melee neck artifacts survive removal of skin
textures. Removing the retained body skin layer in a separate diagnostic removes
the points but exposes a lower gap. Candidate138 removes those196faces and extends
the existing MIT head's lower neck into the collar (45mm max), preserving photoUVs,
weights and upper facial anatomy. No primitive neck or replacement clothes.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/diagnose_rook_neck.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_single_rook_neck.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/validate_single_rook_neck.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_actor_reference.py -ScriptArguments @('--folder','rook_single_neck138','--dense-run')
& experiments/2d_to_3d/run_godot.ps1 -Scene res://cyborg_ready_check.tscn -QuitAfter 1200 -SceneArguments @('--single-neck-study')
```

Actual mesh invariants and314native poses pass.175orphan vertices must be removed:
otherwise Blender bounds include unreferenced geometry omitted by glTF and Death
fails by14mm. Do not weaken the500micrometer gate to accommodate that failure.
For native head views use main.tscn, model E:rook_single_neck138/human.glb,
--neutral --view=front|side|back --focus-height=1.6 --ortho-size=.6,
CombatReadyStudy at0 or MeleeStudy at0.5. Death uses side/ortho2.5 for whole-body
review. Current screenshots reside in that candidate folder. Optional comparison
flag --single-neck-study inherits the133hair/129Run chain and rejects old129atlas
mixing. No matching138atlas or final human artistic acceptance exists yet.

### Skin material audit and controlled calibration139

The actual source head normal image is already present and pixel-identical to
the original2048TGA; Blender uses Non-Color/tangent normal wiring. No missing
source PBR map was discovered. Native no-normal and raw-texture controls isolate
the temple blotch to normal-map shading, not mip generation. Explicit tangents
False/True yield pixel-identical native controls, so tangent export is not a fix.
[glTF tangent guidance](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#meshes-overview)
describes tangent construction but does not identify this asset's source handedness.
No green-channel flip is justified by that document alone.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_rook_skin.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/export_rook_tangents.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/study_rook_skin_normal.py
& experiments/2d_to_3d/run_godot.ps1 -Scene res://cyborg_ready_check.tscn -QuitAfter 1200 -SceneArguments @('--skin-normal-study')
```

Separate candidate E:rook_normal_strength139 keeps the original image at normal
intensity0.35. This is artistic calibration, not a normal convention/import fix.
The GLB binary is unchanged; only sm004_head.normalTexture.scale differs. Editable
BLEND applies the same intensity. Native scene opt-in --skin-normal-study verifies
the actual imported enabled normal texture,2048dimensions and.35scale, saving
native_skin_material.json. It inherits the138neck and forbids129atlas mixing.
314native poses pass, but face likeness and modern-quality geometry/clothing
remain unaccepted. Do not confuse reduced normal contrast with a new detailed mesh.

### Genuine tactical equipment integration140

Existing Microsoft Rocketbox MIT components6135/5978 provide actual modeled
fabric pouches and original textured UVs. Four isolated source components can be
reviewed in E:rook_equipment140 before fitting; full source notice is retained.
The current candidate adds two meshes/550faces to the first actor, not another
character or a gameplay item system. Source body/face/hair/weapon geometry stays
unchanged. E:rook_pouches140 contains full editableBLEND/GLB/CREDITS and reports.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/review_rook_pouches.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_rook_pouches.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/check_rook_pouch_contacts.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_actor_reference.py -ScriptArguments @('--folder','rook_pouches140','--dense-run')
& experiments/2d_to_3d/run_godot.ps1 -Scene res://cyborg_ready_check.tscn -QuitAfter 1200 -SceneArguments @('--pouch-study')
```

RigidSpine/Hips trials failed actual triangle-contact checks and are preserved
as rejected studies. Final binding transfers actual torso weights via existing
surface_weights; eight-slot export retains six real influences without reducing
the99percent retention guard. Full weight mass retained on these vertices.
Contact audit samples18poses:36body comparisons and18pouch/pouch comparisons,
zero noncoplanar crossings. Coplanar,containment,other-prop and unsampled contacts
remain unverified.314native bounds confirm15meshes/25bones/6clips within500micrometers.
Neither test is full artistic acceptance. Current native ready/Melee/Death and
tactical screenshots are in the candidate directory. Scene opt-in --pouch-study
inherits139skin/138neck, preserves source notices and forbids129atlas mixing.
No140atlas or second human is generated before first-character art is convincing.

### Authored jacket adaptation141 — diagnostic, not accepted

The existing Diesel CC0 jacket is real separate garment geometry with source skin
weights. Per-bone uniform scaling caused3x circumference on differing spine
segments. Axial fitting plus a shared torso landmark map preserves circumference
independently. No closest-body projection or primitive garment was introduced.
Overlay and replacement are separate derivatives, original actor140is preserved.

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/inspect_diesel_garments.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_diesel_rook_jacket.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_diesel_rook_jacket.py -ScriptArguments @('--replace-old-cloth')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/inspect_replacement_remnants.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_diesel_rook_jacket.py -ScriptArguments @('--replace-old-cloth','--clean-remnants')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_actor_reference.py -ScriptArguments @('--folder','rook_diesel_replacement141','--dense-run')
& experiments/2d_to_3d/run_godot.ps1 -Scene res://cyborg_ready_check.tscn -QuitAfter 1200 -SceneArguments @('--authored-jacket-study')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/check_rook_pouch_contacts.py -ScriptArguments @('--folder','rook_diesel_replacement141','--include-jacket')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/check_diesel_source_contacts.py
```

Follow the untrimmed/selection/clean order: remnant face IDs are guarded by ordered
renderable face positions, independent of unreferenced vertex numbering. Four
inspected fragments remove7faces after15827old cloth and290additional collar
faces.20unreferenced vertices must also be removed; otherwise Blender-vs-GLB bounds
fail by64mm. Final314native poses pass within unchanged500micrometers. Exact final
GLB reproduction was verified. This proves technical roundtrip, not artist quality.

Native profile/back reveal an open posterior neck connection: coverage FAIL.
18pose contact results are geometric crossing-pair counts, not visual acceptance;
the original source itself has480pairs in one rest pose. Neither shader changes
nor a raised collar should conceal this missing anatomy. Current141BLEND/GLB,
failed trials and native screenshots remain on E: for inspection. Scene opt-in
--authored-jacket-study is diagnostic; no141atlas or production replacement exists.
Next repair must inspect licensed head/neck boundary topology and visible layering.

### Current authored game-rig combat study146

Current150 neutral motion review151: preview main.tscn with150GLB, --clip=Hard stand,
--neutral, --ortho-size=2.4 and
--motion-review=E:/CyberCity2085-3d-lab/generated/phase2/amjviz_wardrobe150/motion_review151.
Produces120actual poses across five clips/four views/six fractions, preserving a
completed manifest rather than overwriting it. Assemble/verify source hashes with
`python experiments/2d_to_3d/review_contact_captures.py --motion151`.
Five sheets require real visual inspection; command success is not art acceptance.

Blender sparse first-human atlas pilot:
`& experiments/2d_to_3d/run_blender.ps1 -Script blender/render_rocketbox_atlas.py -ScriptArguments @('--wardrobe150-pilot','--samples=4')`.
Outputs150/atlas_pilot151,160real renders and five canonical action manifests.
No previous129atlas/source is reused. Individual actions can be selected using
--action=ShootStudy, Hard stand, Walk (1_24), MeleeStudy or DeathStudy in the array.
Actual orbit projection measures source-forward/facings and foot anchor.
Native atlas_review.tscn accepts --atlas-dir=E:/.../atlas_pilot151,
--manifest=ShootStudy_atlas.json, --action=shoot, --combat-scale,
--production-order, --self-test and --capture=E:/.../atlas_pilot151/shoot_native.png.
Repeat for idle/walk/melee/death using the corresponding source-named manifests.
`python experiments/2d_to_3d/verify_rocketbox_atlas.py --wardrobe150-pilot --native-proof`
checks current source/CREDITS, PNG packing/margins/time calibration and all five
real native proof hashes. Sparse pilot is not a native24fps/final-art claim.

Rook wardrobe150 derivative:
`& experiments/2d_to_3d/run_blender.ps1 -Script blender/adapt_amjviz_wardrobe150.py`.
Requires149editable combat source. Removes only the real modular Neck guard's
364faces, retaining authored inner jacket collar and anatomy. Green/low-metal PBR
variation is stored in Blender nodes and compiled GLB factors; original textures,
UVs, pockets/folds and source geometry outside the guard remain. Source licenses
retained; private outputs amjviz_wardrobe150/human_actions.BLEND/GLB on E:.
Use --wardrobe150-study with measure_amjviz_actions146.py, native action checker
and tactical stage in place of --support-study. Preview model path is150GLB above.
First integration parse failure/name collision is corrected; require positive
COMPARISON_INPUT_TEST_OK and capture0, not mere process launch/exit.
This is not a full animation-contact/likeness acceptance or a production update.

Support-hand149 uses the original FK controls and existing analytical IK helper;
it preserves upper/lower-arm lengths, not a stretched wrist translation.
`& experiments/2d_to_3d/run_blender.ps1 -Script blender/audit_amjviz_grip149.py`
records posed landmarks. `fit_amjviz_support149.py` (same wrapper) first creates
static shoot_support.BLEND/GLB. Static export gate: run_godot.ps1 with
`-Scene res://amjviz_pose_check.tscn -SceneArguments @('--support-study')`.
Optional --curl-study produces a separate unaccepted finger diagnostic only;
it cannot be combined with --animated. Do not call its landmark metric contact.
For full arm-corrected source use fit_amjviz_support149.py with
`-ScriptArguments @('--animated')`; original six other clips stay in148source.
Then measure_amjviz_actions146.py with `@('--support-study')` and the native
amjviz_actions_check.tscn with the same flag for fresh288pose references/checks.
Use --support-study instead of --amjviz-combat-study in the stage command below.
Private outputs: amjviz_grip149/human_actions.blend and human_actions.glb on E:.
Neutral close-up: preview main.tscn, --model=E:/.../shoot_support.glb, --neutral,
--view=side, --focus-height=1.45, --ortho-size=.65. Camera distance alone does not
zoom an orthographic camera. Source licenses and unchanged originals retained.

Real hair geometry148 diagnostic, separate from147texture budget:
`run_blender.ps1 -Script blender/audit_amjviz_hair148.py`, then
`run_blender.ps1 -Script blender/fit_amjviz_quiff148.py`. Both live under
experiments/2d_to_3d; use the full repository-relative wrapper path as below.
Requires existing146BLEND/GLB and isolated ActualCopperQuiff from133private source.
The fit removes only Hair2 material faces and verifies nonhair face/UV coordinates;
uses real scalp BVH for the lower hairline, existing head bone, source copper UV.
CC0 Grab3D quiff publisher's AI-assisted provenance is retained alongside the
AmJViZ royalty-free license. No old head/hand components are reused.
Fresh reference:
`& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_amjviz_actions146.py -ScriptArguments @('--hair-study')`.
Native check:
`& experiments/2d_to_3d/run_godot.ps1 -Scene res://amjviz_actions_check.tscn -SceneArguments @('--hair-study')`.
Use --hair-study instead of --amjviz-combat-study for the tactical command below;
do not mix --texture-budget-study. Preview148file is amjviz_hair148/human.glb.
The fit remains an unaccepted Rook art diagnostic, not a final character cohort.

Texture-only optional147: `python experiments/2d_to_3d/texture_budget.py --maximum 1024`
uses current146GLB and writes private amjviz_budget147_1024 on E:, never overwrites
146. Requires Pillow and NumPy. It retains exact accessor payloads, material slots,
UVs, rig and clips; resamples color in linear light, packed data directly and
renormalizes normals. Role conflicts fail explicitly. Native checker147:
`& experiments/2d_to_3d/run_godot.ps1 -Scene res://amjviz_actions_check.tscn -SceneArguments @('--texture-budget-study')`.
For stage comparison replace --amjviz-combat-study with --texture-budget-study in
the command below. Keep tactical/facades/sprite-review flags: without them this is
a two-actor720p preview, not the five-subject combat-scale measurement.
Current147 is a GLB texture-budget derivative;146 editable BLEND remains the
full-resolution source. No separate147BLEND or new atlas has been exported.

The141 anatomy experiments above are rejected diagnostics, not the current human.
Current146 uses the real licensed AmJViZ character, original PBR and pruned262-bone
game rig145. No production replacement. Keep licensed source files and all output
under E:/CyberCity2085-3d-lab; do not redistribute the royalty-free source pack.
From the repository root in PowerShell, with145 human.blend and licensed UAL and
FireWarden sources present, execute in this order:

```powershell
& experiments/2d_to_3d/run_blender.ps1 -Script blender/bake_amjviz_combat146.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/ground_amjviz_locomotion146.py
& experiments/2d_to_3d/run_blender.ps1 -Script blender/fit_amjviz_pistol146.py -ScriptArguments @('--animated','--index-pad-fit')
& experiments/2d_to_3d/run_blender.ps1 -Script blender/measure_amjviz_actions146.py
& experiments/2d_to_3d/run_godot.ps1 -Scene res://amjviz_actions_check.tscn
& experiments/2d_to_3d/run_godot.ps1 -SceneArguments @('--amjviz-combat-study','--robot-action-bundle','--source-opacity-study','--vtol-motion-study','--vtol-finish-study','--tactical','--facades-study','--sprite-review','--self-test')
```

The source FK controller solver uses limb IK_FK=1 and evaluated rest-axis corrected
world poses, not direct rotation of constrained deform bones. New actions bake at
120Hz. Original locomotion bone curves are retained; upward-only root correction
prevents authored boot penetration. Export must keep constant object animation
tracks; otherwise Death root displacement leaks into Idle despite valid per-clip
bounds. Native checker tests all seven clips at48Hz source-key/midpoint cadence
(288poses), the floor, settled death height and death-to-idle reset. Require the
positive AMJVIZ_COMBAT_NATIVE_EXPORT_PASS marker and current hashes in
generated/phase2/amjviz_actions146/native_actions.json, not exit0 alone.

Independent preview: main.tscn with --model=E:/CyberCity2085-3d-lab/generated/phase2/amjviz_actions146/human_actions.glb,
--clip=ShootStudy (or MeleeStudy/DeathStudy), --clip-fraction=.5, --neutral,
--view=front/side/back and --capture=E:/.../capture.png. Gun meshes appear only
during ShootStudy, matching the tactical demonstration. No drop/holster mechanic
is implied. The fitted index landmark is not a grasp/contact solver.

Native numerical acceptance is not original nonlinear Rigify fidelity or artistic
acceptance. No new atlas exists. Current five-second benchmark evidence is
amjviz_actions146/benchmark146.json, gpu146.json and verified_benchmark146.json;
run verify_benchmark_window.py --folder amjviz_actions146 --batch146 (use
`--batch 146` as two CLI tokens). It checks current asset hashes, rendered1920x1080
target and live-Godot timestamp overlap. See the progress register for measured
values and limits; global GPU memory must not be called exclusive actor VRAM.
Rook likeness, final cloth/hand contacts and complete neutral multi-view action
review remain open. Do not expand humanoid production or regenerate old atlases.

