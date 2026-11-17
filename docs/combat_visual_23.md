# Combat Visual 2.3 — Environmental depth

The 2.2 background and surveyed tactical board remain intact. A render-only model now builds elevated props above that same plane. Character dimensions, camera projection/zoom, HUD commands, collision/LOS cells and combat rules are unchanged.

## Strategy

The existing surveys contain texture-space outlines, not measured 3D buildings. `environment_depth.gd` adds conservative, human-relative cutaway elevations by obstacle identity, without adding those inferred dimensions to the tactical data:

- Tables/desks/benches have four separate legs and a thin raised tabletop.
- Chairs have legs, a seat, a back and arms; sofas have a padded base, raised back and arms. Small bevels soften furniture corners.
- Market canopies have posts and a roof split into two sloping planes.
- Walls, machines, containers and buildings have bounded volume and independently shaded visible side faces. Water surfaces and nonphysical boundaries stay flat.

Height is bounded to 0.90 full tactical-tile widths, compared with the unchanged humanoid visible height of 0.77 tile widths. These are deliberately limited tactical cutaways, not inferred full building stories.

Top surfaces keep their source-map UVs. Facades use separate cached, repeating metal, fabric or stone textures, with orientation-dependent shading and narrow cap lips. Roof/floor texture strips are never stretched down the sides. This avoids the earlier giant extrusions and elongated UVs.

## Ground separation and occlusion

Simply lifting the original art would leave a second copy painted underneath. For each elevated footprint, a cached, temporary floor patch completes the obscured region from its surrounding pixels using a small push/pull pyramid. It is composited only inside the original outline, underneath the raised prop. This is an approximation of the hidden floor, not newly surveyed artwork. It does not write to the original map or change any SHA-256 record.

Ground patches and cached soft projected shadows render in the battlefield ground pass, before tactical diamonds and routes. Props share the existing unit depth-sort layer. Occlusion tests use the actual elevated cap/side polygons, not only the old ground outline; foreground props fade for living units and route previews. Occlusion updates at 20 Hz during combat, so movement does not leave units hidden behind a stale wall. The map's actual collision and LOS remain exactly as surveyed.

## Controls, quality and performance

- **F10** toggles environmental depth immediately, retaining camera and combat state. Disabled depth restores the flat 2.2 prop presentation, including its existing lighting/HUD.
- **F9** still selects the previous HUD; `--legacy-visuals` still selects the earlier renderer.
- `--flat-environment` / `--environment-depth` explicitly override the persisted `graphics.environment_depth` preference.
- Low quality bypasses volume construction and floor completion. Medium/high restore the volume; high uses the fuller soft-shadow layers.
- Geometry, shadows, materials and completed floor patches are built/cached outside the draw loop. The source-image cache retains one map; the floor-patch cache retains at most two map texture IDs. Patch generation is capped at 192 pixels on its longest side; untouched visible floor and prop art still use the original map texture.

No new random-number draws are used by this presentation model. It does not alter encounter RNG, enemy stats, AP, range, damage, paths, objectives or saves.

## Real before/after captures

All PNGs below are actual Godot OpenGL renders. The central furniture comparison uses the same camera and combat state, and asserts that switching depth leaves them unchanged. The wider catalogue capture driver seeds/stages the same fixtures before and after, retaining real map walls and paths.

| Environment | Before | After |
| --- | --- | --- |
| Central sofas, chair and coffee table, 1080p | [Before](images/combat-23/furniture-before-1080.png) | [After](images/combat-23/furniture-after-1080.png) |
| Industrial, 720p | [Before](images/combat-23/industrial-before-720.png) | [After](images/combat-23/industrial-after-720.png) |
| Urban market, 720p | [Before](images/combat-23/urban-before-720.png) | [After](images/combat-23/urban-after-720.png) |
| Wasteland, 720p | [Before](images/combat-23/wasteland-before-720.png) | [After](images/combat-23/wasteland-after-720.png) |

[Laboratory targeting at 1440p](images/combat-23/lab-after-1440.png).

The first prototype exposed repeated floor tiles around lifted props. Replacing those tiles with local floor completion removed the repetition; a mask-weight regression prevents the white-fill error encountered while developing the completion pass. Furniture was then refined into distinct parts, and canopies into sloped roofs. Final captures cover safehouse interior, industrial floor, city market, laboratory and wasteland at 1280×720, 1920×1080 and 2560×1440, with both movement previews and enemy targeting.

## Validation and reproduction

`environment_depth_regression.gd` checks all 122 maps: bounded elevations, unchanged ground vertices, correct roof UV projection, independent facade materials, multipart tables, floor completion/cache behavior and cap/side occlusion. The existing catalogue and real action tests cover unchanged A*/AP/LOS, cell selection, movement, attacks, healing/PSI, enemy turns, HUD/quality switching and result export. Native pixel checks retain solid bodies and readable outlines.

`capture_environment_depth.gd` also exercises real F10 key events and low/medium/high quality changes, asserting unchanged combat state/camera and that low quality constructs no elevated props. Original source-map hashes and geometry/trace contracts are covered by `test_map_8k.py`.

```sh
DISPLAY=:103 python -m pytest -q \
  tests/test_combat_visual_2.py tests/test_tactical_reference_runtime.py \
  tests/test_combat_visual_21.py tests/test_unit_readability_runtime.py \
  tests/test_map_8k.py
```

Matched central-furniture capture and native toggle checks:

```sh
DISPLAY=:103 godot --path godot/combat_missions_ui \
  --rendering-method gl_compatibility --audio-driver Dummy \
  --script tests/capture_environment_depth.gd
```

Five-map, three-resolution capture set (repeat with `--flat-environment` for the before set):

```sh
DISPLAY=:103 godot --path godot/combat_missions_ui \
  --rendering-method gl_compatibility --audio-driver Dummy \
  --script tests/capture_combat_21.gd -- \
  --environment-depth --polish --depth-catalogue --output /absolute/output/path
```

Final validation on November 17, 2026: **15 targeted tests passed** (`test_combat_visual_2.py`, `test_tactical_reference_runtime.py`, `test_combat_visual_21.py`, `test_unit_readability_runtime.py`, `test_map_8k.py`). Native before/after capture runs completed on all five environments at all three resolutions without script/shader errors. The matched furniture comparison and native F10/quality test also passed. No source map, wall survey, trace, character-size constant or camera-projection/zoom code was modified.
