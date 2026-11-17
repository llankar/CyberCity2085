# Combat Visual 2.1

## Presentation changes

The source wall surveys describe UV silhouettes, not building heights or architectural footprints. The old renderer extruded these silhouettes into tall slabs and stretched roof strips down their sides. The replacement faithfully re-layers the original painted silhouettes at their original UV coordinates; it does not fabricate 3D architecture. Foreground cutouts fade when they intersect a living unit's visible body. The background artwork and source surveys remain unchanged.

The isometric projection now respects each source image's pixel aspect ratio. Tactical cells, collisions, LOS and movement costs still use the original 40×28 grid. Forward/inverse picking is checked for every cell on all 122 maps.

Humanoid visible height is now 70% of tile width, retaining the existing 10% presentation multiplier. This is **52% larger than the initial 46% iteration**, following the user's screenshot feedback. Transparent sprite margins no longer count as body height. Sprite proportions and opaque sole anchoring are preserved; animation poses use idle height as their stable reference.

The opening camera frames the living squad with a viewport-scaled 200px tile target. Mouse-wheel close zoom permits a further 1.65×, capped by the existing engine limit. Home reframes the squad. Zoom keeps the world point under the cursor stable.

Local light pools sample bright saturated areas of the actual map, with cached radial textures. Rain/dust/interior atmosphere, objectives, cover hints, movement routes and active HUD portrait accents remain presentation-only. Quality 0 disables the added layers. Legacy visuals and quality settings remain available.

## Real-renderer evidence

Captured using Godot 4.6.3 OpenGL Compatibility, Mesa llvmpipe, at 1280×720, 1920×1080 and 2560×1440 across urban, industrial, interior and wasteland maps. Full captures can be reproduced with:

```
DISPLAY=:103 godot --path godot/combat_missions_ui --rendering-method gl_compatibility --audio-driver Dummy --script tests/capture_combat_21.gd
```

- [Urban, opening framing, 720p](images/combat-21/urban-720.png)
- [Enlarged agent, close zoom, 1080p](images/combat-21/urban-close-1080.png)
- [Industrial, 1080p](images/combat-21/industrial-1080.png)
- [Interior, 1440p](images/combat-21/interior-1440.png)
- [Wasteland, 1080p](images/combat-21/wasteland-1080.png)

The capture driver also asserts exact cell picking, cursor-anchored zoom and unchanged combat data after camera operations. Existing native interaction regressions cover movement/AP, attack actions, target cards, quality changes and result export. `tests/test_combat_visual_21.py` compares all 122 maps against the legacy tactical board, including collision/LOS sets, paths, reachable cells, every cell's inverse projection and every surveyed cutout's UV alignment. `tests/test_map_8k.py` verifies the source artwork/survey integrity contracts.

Validation on November 17, 2026: 7 core/catalogue tests passed, 2 native GPU readability/target-card tests passed, and 2 source-map integrity tests passed (11 total). Native captures cover all four environments at 1280×720, 1920×1080 and 2560×1440, plus close framing at each size. The final visible-body multiplier increased from the first 2.1 preview's 0.46 to 0.70 (about 52% taller), retaining the existing 1.10 presentation multiplier. No map PNG or wall survey was modified.


## Combat feedback and interior vehicles

Out-of-range shots now report the actual distance and weapon range before checking line of sight. The target card uses the same priority. In-range blocked shots say an obstacle obstructs line of sight, rather than assuming every opaque surveyed cell is a wall. No shot validation conditions or AP/damage rules changed.

Interior maps (the catalogue's `inner`, `interior` and `tunnel` filenames) no longer generate arrival vehicles, decorative enemy vehicles or enemy vehicle combat units. Exterior encounters retain their vehicles; power armor remains deployable indoors. The classification is shared with the interior weather presentation. This affects newly created combats, without rewriting campaign saves or source maps.

`combat_feedback_regression.gd` exercises the real mission scene: out-of-range plus blocked LOS, in-range blocked LOS, matching target-card feedback, unchanged AP/HP after rejected shots, every interior map's generated vehicles, exterior decorative vehicles and interior power-armor support.
