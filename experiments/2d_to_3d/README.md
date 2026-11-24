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

The dense authored human is preserved. `export_authored_glb.py -- FOLDER
--realtime` produces a separate simplified GLB; `--pose-clip` adds only a fitting
test, not a gameplay action. Geometry and deformations need artistic review.

