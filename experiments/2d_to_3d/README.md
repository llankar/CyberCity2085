# Experimental 2D to 3D pipeline

This directory contains only lightweight, reproducible tooling. AI weights,
downloads, caches, temporary files, generated meshes, textures and Blender
sources live under `E:\CyberCity2085-3d-lab` and are intentionally not tracked.

The experiment does not modify the CyberCity 2085 runtime or replace any game
asset. See `docs/experiments/2d_to_3d_pipeline.md` for status, licensing and
reproduction instructions.

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

For calibrated pixel-size review, run `prepare_sprite_review.py`, then launch
comparison.tscn with `-- --realtime --sprite-review` (add `--overview` for the
overview zoom). This renders a 1920x1080 viewport and verifies the projected
1.718m reference against the existing alley's default combat formula: 62.208px
close / 20.736px overview. It displays actual atlas idle frames alongside meshes.
The robot reference uses the selected normal-robot multiplier 1.65; the 3D robot
keeps its physical 2.4m height. Production sprite shaders/outlines and mission
presentation overrides are not included; this is a scale comparison, not an
identical reproduction of the production renderer.

The dense authored human is preserved. `export_authored_glb.py -- FOLDER
--realtime` produces a separate simplified GLB; `--pose-clip` adds only a fitting
test, not a gameplay action. Geometry and deformations need artistic review.

