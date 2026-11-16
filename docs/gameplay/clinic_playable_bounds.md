# Reviewed clinic playable bounds

The two identical clinic images, `wasteland_inner_03_ruined_clinic.png` and
`wasteland_inner_08_ruined_clinic.png`, allowed characters to walk along their
dark exterior padding. Direct image inspection and actual traces placed agents
on the bottom image edge, outside the drawn interior floor. Stored-wall
compliance alone had not caught this floor-fidelity error.

## Manual data correction

Four named `unplayable_margin` rectangles now describe the exterior of the
building on its existing 960×540 authoring canvas:

| Boundary | Rectangle |
| --- | --- |
| Top | (0,0)–(960,18) |
| Bottom | (0,507)–(960,540) |
| West | (0,18)–(23,507) |
| East | (946,18)–(960,507) |

These were reviewed against the artwork and the existing outer wall traces,
not inferred from brightness. The original 34 obstacle records are preserved
exactly; four bounds bring the compiled count to 38. Both exact-art variants
were updated and explicitly recompiled. No image, interior wall, door, prop,
weapon statistic or mission rule was edited.

Bounds block movement but have `blocks_sight=false`, so padding does not grant
fictional high cover. The existing schema/compiler and Arcade/Godot loaders
already support this distinction. The headless Godot test checks that the real
clinic corner becomes solid without becoming high cover. F8 debug visibility
remains unchanged.

## Placement and provenance

The connected-placement helper naturally recomputes units/objectives on the
remaining interior components. **Actual spawn/objective cells can change** even
though generation inputs are preserved. The resulting shorter battles therefore
cannot be attributed to improved AI alone, or described as fixed placements.
Preexisting disconnected rooms are not joined by carving new passages. Coarse
40×28 survey sampling and resolution-dependent connectivity remain limits.

Manual `TerrainProfile` values now carry the SHA-256 of the compiled survey used
when they were constructed. QA rows record this value. A cached old profile thus
retains its old survey provenance instead of being mislabeled by a later disk
edit. Restart/clear the existing terrain cache after authoring changes.

## Verification

The source/compiled equality and duplicate-art contracts pass for all 122 maps.
The existing 1,952-placement matrix remains green, and clinic checks also cover
1280×720, 960×640 and the normal 1920×1000 window size. Regressions verify blocked
padding even with forced anchors, preserved original objects, open central floor,
distinct legal placement and source-survey fingerprints.

Diagnostic overlay:
`python tools/review_map_walls.py assets/maps/wasteland_inner_03_ruined_clinic.png --output runtime/clinic_boundary_review.png`

The overlay was inspected without desktop control. This is a review of the
clinic family only, not proof that all other map perimeters are correct. The
[inventory](../manual_wall_inventory.md) now tracks that boundary audit separately.
See [measured results](../qa/clinic_boundary_retest.md).
