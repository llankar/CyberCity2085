# Combat Visual 2.2 — Lighting and tactical polish

This pass builds on 2.1. Source map PNGs, UV surveys, isometric axes, camera zoom/framing constants, character size/aspect/feet anchors and HUD command positions are unchanged. No combat rules, range, LOS, AI, movement budget or campaign data changed.

## Presentation

- `visual_lighting.gd` caches emissive samples from the actual map, and uses a shared soft texture for local pools. City/interior cyan, industrial amber and subdued wasteland profiles blend with source colors, so red/violet sources retain their hue. Pools pulse gently; high quality adds small broken floor reflections. These are stylized 2D lighting cues over the existing art, not reconstructed 3D surfaces.
- `unit_visual.gd` layers a contact core and soft penumbra beneath each unit. Every living enemy has a faint red foot ring; targeted enemies gain rotating arcs and subtly breathing brackets. The shader retains opaque, readable bodies and always-visible cyan/red contours, with a more directional rim. Static/animated frame geometry is unchanged.
- `visual_battlefield.gd` makes reachable diamonds quieter, moves small light beads along the true path and pulses the actual destination. The existing badge still derives PA from the real path length.
- `combat_visual_fx.gd` reuses the cached glow for brief muzzle/impact/explosion light, adds directional projectile impact sparks and rising healing crosses. Existing PSI trails, blast rings, smoke and particles remain. The 64-effect cap includes secondary smoke, and finished effects stop processing.
- `visual_hud.gd` retains command/portrait organization. It adds smooth hover emphasis and a dark footer surface, blocks accidental shots through footer gaps, fits text including the ellipsis, adapts long agent/title font sizes and keeps target cards on screen while minimizing overlaps with living silhouettes. Portrait artwork and its aspect-preserving crop remain unchanged.

## Quality and cost

Low quality omits environment pools, reflections, route beads, extra flash/spark effects and the layered penumbra; essential tactical markers remain. Medium uses up to six sampled lights and fewer particles. High uses up to twelve lights plus reflections. A bounded eight-texture sample cache avoids rescanning the same map on resize; soft-light texture and hover style resources are reused. Ambient/HUD redraws are limited to 20–30 Hz. The prior renderer (`--legacy-visuals`) and F9 HUD switch remain available.

## Verification

13 targeted Python/Godot tests passed:

```sh
DISPLAY=:103 python -m pytest -q \
  tests/test_unit_readability_runtime.py \
  tests/test_tactical_reference_runtime.py \
  tests/test_combat_visual_2.py \
  tests/test_combat_visual_21.py \
  tests/test_map_8k.py
```

Coverage includes 122-map geometry/picking/path/LOS equivalence and source integrity; real move/AP, attacks, healing/PSI, enemy turn and result export; opacity and permanent ally/enemy contours on the native GPU renderer; target-card click-through protection; unchanged unit dimensions across quality levels; bounded and expiring effects; cached lights/styles, HUD bounds and footer input protection. The added polish contract was rerun after the final text/layout changes.

Actual Godot 4.6.3/OpenGL captures were inspected on city, industrial, interior and wasteland maps at 1280×720, 1920×1080 and 2560×1440. Both movement and targeting/effects states were rendered, with six additional isolated effect captures. Low/medium quality and the previous renderer were also captured. Camera checks in the capture driver assert cell/UV agreement and cursor-anchored zoom after resizing/panning, without combat-data changes.

The captures use controlled QA encounters on the real maps and original collision geometry. Selected contacts are placed on valid open firing lanes; the detail capture simulates a player pan at the existing zoom. Effect showcase frames invoke the actual effect component at a controlled animation age; they do not claim to be an uncontrolled playthrough. Real action dispatch is independently exercised by the interaction regression.

Visual review corrected clipped ellipses/long compact names, weak hover contrast, target-card overlap and effects framed outside the screenshot. Compared with the 2.0 reference, the focus is local color, grounded silhouettes and clear red target identification while deliberately retaining the current painted scenery, character scale and HUD organization.

## Selected real captures

- [City, movement, 720p](images/combat-22/city-720.png)
- [Industrial, movement, 1080p](images/combat-22/industrial-1080.png)
- [Interior, targeting, 1440p](images/combat-22/interior-target-1440.png)
- [Wasteland, movement, 1440p](images/combat-22/wasteland-1440.png)
- [Industrial explosion](images/combat-22/explosion-1080.png)
- [Industrial PSI](images/combat-22/psi-1080.png)
- [Previous renderer, 720p](images/combat-22/legacy-720.png)

Reproduce the main capture set (30 PNGs):

```sh
DISPLAY=:103 godot --path godot/combat_missions_ui \
  --rendering-method gl_compatibility --audio-driver Dummy \
  --script tests/capture_combat_21.gd -- \
  --polish --effects-showcase --output /absolute/output/path
```

The reused capture driver additionally supports `--map`, `--size 1280x720`, `--quality 0|1|2`, and `--legacy-visuals --baseline` for focused checks.

Validation on November 17, 2026: 13 targeted tests passed across `test_combat_visual_2.py`, `test_tactical_reference_runtime.py`, `test_combat_visual_21.py`, `test_unit_readability_runtime.py` and `test_map_8k.py`. Final HUD/portrait/rim changes were rechecked with the 3 relevant native/polish tests (all passed). Real OpenGL captures completed without script/shader errors for the four environments, three resolutions, low/medium/high quality and the previous renderer. The action regression exercises actual movement, shots, melee, PSI, healing, enemy turns, quality/HUD switches and result export; the native effect gallery intentionally stages presentation-only bursts on real maps to inspect each effect separately.
