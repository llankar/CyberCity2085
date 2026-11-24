# Experimental 2D to 3D pipeline

This directory contains only lightweight, reproducible tooling. AI weights,
downloads, caches, temporary files, generated meshes, textures and Blender
sources live under `E:\CyberCity2085-3d-lab` and are intentionally not tracked.

The experiment does not modify the CyberCity 2085 runtime or replace any game
asset. See `docs/experiments/2d_to_3d_pipeline.md` for status, licensing and
reproduction instructions.

Current progress is authoritative in `docs/experiments/2d_to_3d_progress.md`.
Professional Charge source conversion studies are stored on E: only:
`security_pbr_robot01` (120/124 surfaces, unresolved glass), `einar_geometry01`
(static diagnostic human), `einar_jacket01` (authored fabric bake proof).
Run `verify_charge_robot_pbr.py E:/CyberCity2085-3d-lab/generated/phase2/security_pbr_robot01`
and `verify_charge_human_geometry.py` for real-file structural checks. These do
not prove artistic quality, rigging or animation acceptance. `audit_charge_human.py`
requires source/output paths after `--`; export/bake study scripts use explicit
external E: paths. Source Blender files are preserved, embedded source scripts
are disabled. All Charge derivatives require the recorded CC BY4 attribution.

Latest human material study: `bake_einar_dielectrics.py`, then
`bake_einar_mechanics.py` (optional `-- --resume` only for unresolved parts).
`verify_einar_dielectrics.py --mechanics` checks the combined export on E:.
`godot --path experiments/2d_to_3d/godot res://comparison.tscn -- --charge --tactical --self-test`
loads the five-subject scene with the new static sources. Add `--sprite-review`
and optionally `--overview` for measured current-game pixel-height comparison.
These sources have no action clips; the check verifies their absence explicitly.
`preview.gd --view=front|side|back` selects neutral orthographic inspection angles.

`audit_einar_hair.py` inventories the original film curves. `export_einar_hair.py`
creates a separate static strand-mesh study from the fresh original scene and
combines it with the converted game meshes on E:. `verify_einar_hair.py` checks
the actual GLB and head-space placement. Approximate hair palette, high strand
triangle count and aliasing remain unaccepted; this is not a final game hairstyle.

`rig_einar_game_study.py` bakes an independent game skeleton from actual authored
weights and mechanical transforms. Default output is the head-only diagnostic
`einar_rig01`; `-- --idle` outputs the relaxed Idle study `einar_idle01`.
`verify_einar_rig.py [--idle]` checks actual skin buffers, joints, weights and
clip scope. `godot --path experiments/2d_to_3d/godot res://skin_motion_check.tscn -- --idle`
checks native sampled deformation and loop endpoints. Add `--rigged-human` to
the `--charge` comparison to load/loop the new human Idle. These are experimental
animation studies; walking, weapon actions and full visual acceptance remain open.

`rig_einar_game_study.py -- --walk` adds an IK-foot in-place walk study.
`rigid_surface_fit.py` preserves authored rigid/surface-deformed attachments and
reports any nonrigid residual. `combine_einar_motion.py` packages Idle/Walk into
one external `einar_motion01/human_motion.glb` used by `--rigged-human`.
Run `verify_einar_rig.py --bundle`, then the native `skin_motion_check.tscn`
with `-- --bundle --idle` or `-- --bundle --walk`. Walk contact checks sample
both complete stance intervals with0.7m virtual root travel/cycle; actual map
locomotion is not implemented. `--walk-preview` on the comparison loops Walk.
Validated contacts and loop timing do not imply artistic or full action coverage.

## Independent comparison stage

Launch `godot --path experiments/2d_to_3d/godot res://comparison.tscn -- --realtime`.
Requires the external authored_tactical01 and george_tactical GLBs on E:.
TAB/click selects; C switches isometric/orbit mode; RMB drag orbits; wheel zooms.
Robot actions: 1 idle, 2 walk, 3 shoot, 4 death. Human action clips are absent and
reported as unavailable. `--self-test` exercises selection, clip dispatch and
camera mode; `--capture=E:/CyberCity2085-3d-lab/generated/phase2/name.png` saves
a native screenshot after warmup and 120 measured frames. This is a scale stage,
not yet the requested existing-map tactical scene.

`python experiments/2d_to_3d/prepare_tactical_inputs.py` copies the existing alley
image and wall metadata to E: and checks their hashes. Add `--tactical` to the
comparison launch after generating `vtol01` with `blender/create_vtol.py`.
This prototype loads a textured 2D map floor plus blocked-cell volumes, the two
actors, a hovering VTOL and a crate. It is not a finished 3D environment or an
exact production-zoom comparison. Original map/runtime files remain unchanged.

The tactical stage also requires `generator01`: run Blender with
`blender/create_industrial_generator.py -- E:/CyberCity2085-3d-lab/generated/phase2/generator01`.
Its BLEND keeps75 editable rigid parts; its GLB is a merged one-mesh/six-material
derivative. This geometric study lacks the reference's weathering/PBR texture detail.

For calibrated pixel-size review, run `prepare_sprite_review.py`, then launch
comparison.tscn with `-- --realtime --sprite-review` (add `--overview` for the
overview zoom). This renders a 1920x1080 viewport and verifies the projected
1.718m reference against the existing alley's default combat formula: 62.208px
close / 20.736px overview. It displays actual atlas idle frames alongside meshes.
The robot reference uses the selected normal-robot multiplier 1.65; the 3D robot
keeps its physical 2.4m height. Production sprite shaders/outlines and mission
presentation overrides are not included; this is a scale comparison, not an
identical reproduction of the production renderer.

## Animated 3D-to-2D proof

Run Blender in background with `blender/render_robot_walk_atlas.py --
E:/CyberCity2085-3d-lab/generated/phase2/robot_walk_atlas01`, then run
`python experiments/2d_to_3d/verify_robot_atlas.py E:/CyberCity2085-3d-lab/generated/phase2/robot_walk_atlas01`.
The preserved Quaternius George source produces a transparent 1024x512 atlas:
eight orbit views, four authored Walk samples per view. The verifier checks
all 32 frames, margins, distinct poses and exact packing (one-channel-unit
tolerance). Production direction mapping, frame density, anchor calibration
and artistic quality remain unverified; no production asset is replaced.

The renderer also accepts `--action=Idle`, `Shoot`, `HitRecieve_1` or `Death`.
Pass the action name as the verifier's second argument. One-shot clips include
their final pose; duplicate return-to-rest endpoints are valid and reported.
Death uses a wider frame to contain the fallen model; consistent cross-action
scale/anchors remain unfinished.

Launch `godot --path experiments/2d_to_3d/godot res://atlas_review.tscn -- --self-test`
for the default Walk atlas. For another action add `--action=Death
--atlas-dir=E:/CyberCity2085-3d-lab/generated/phase2/robot_atlas_Death`.
Space pauses; arrows select a raw orbit view. Native tests exercise all frame
indices, timed advance, pause, view changes and loop/non-loop end behavior.

Latest renders use a common 5m orthographic scale and camera target for every
action. `verify_robot_clip_alignment.py` checks five `robot_unified_ACTION`
folders for identical anchors/scale and projected facing mapping. Ground-origin
anchor is approximately `(0.5,0.65264)`; standing2.4m reference height0.40704UV.
The review's `--production-order` / M uses camera-projected -Y forward to order
E,SE,S,SW,W,NW,N,NE. The source-forward assumption still needs visual acceptance.
Previous differently framed experimental sheets remain preserved on E:.

## Charge source review

Official Einar and Security Bot ZIPs are retained on E: with provenance JSON,
hashes and their embedded CC BY4 ReadMe. See the asset selection register.
Run Blender with embedded scripts disabled and `blender/review_charge_asset.py
-- SOURCE.blend OUTPUT_FOLDER` for neutral front/profile/back review. The script
preserves bound subdivision topology and disables film procedural displacement
only in memory. These are source-asset reviews, not optimized Godot exports.
The first render attempt was stopped after14GB OS working set; lowering bound
subdivision then failed Surface Deform vertex counts. Preserve the author rig
and bake an evaluated derivative instead of editing its bound topology.

`blender/export_charge_geometry.py -- SECURITY_SOURCE.blend OUTPUT_FOLDER`
creates a separate evaluated static BLEND and a neutral-material GLB diagnostic.
`verify_charge_geometry.py OUTPUT_FOLDER` compares actual GLB mesh/triangle
coverage with the Blender report. The BLEND retains film materials for baking;
the GLB deliberately uses a simple lit material after a profiled recursive
shader-export bottleneck. This is not the final textured or animated robot.

`blender/bake_charge_piece.py -- OUTPUT_FOLDER` tests source Worn Surface group
Color/Roughness/Metallic plus tangent-normal baking on the shin shell. Four512px
PNG maps become three embedded glTF textures through standard PBR nodes.
`verify_charge_pbr_piece.py OUTPUT_FOLDER` checks map sizes, connections, embedded
images and exactly one exported mesh/scene. Explicit `use_active_scene=True`
prevents selected objects from other stored scenes leaking into the export.
Layered film shader fidelity and the complete robot still need review/conversion.

The dense authored human is preserved. `export_authored_glb.py -- FOLDER
--realtime` produces a separate simplified GLB; `--pose-clip` adds only a fitting
test, not a gameplay action. Geometry and deformations need artistic review.

