# Collapsed-tunnel exterior bounds

Actual phase traces placed agents at `(1088,0)`, `(1152,0)` and on the far-right
image edge while trying to approach objectives inside the collapsed tunnels.
Direct inspection of the original artwork confirmed these were exterior dark
margins. Stored-wall compliance had allowed this long route outside the floor.

Both exact-pixel duplicates, `wasteland_inner_02_collapsed_tunnel.png` and
`wasteland_inner_07_collapsed_tunnel.png`, now have six manual exterior masks on
the existing 960x540 authoring canvas:

| Margin | Rectangle |
| --- | --- |
| Top | (0,0)–(960,18) |
| Bottom | (0,501)–(960,540) |
| West | (0,18)–(15,501) |
| East | (938,18)–(960,501) |
| Northwest exterior | (0,18)–(115,140) |
| Northern notch | (406,18)–(507,50) |

All 23 existing walls/props remain unchanged, protected by a canonical compiled-
object hash. The total is now 29 records. Added masks block movement but not
sight, and cannot be carved by forced spawn anchors. Both surveys were explicitly
recompiled. No internal opening, weapon, enemy AP or turn cap was changed.
The diagnostic overlay was inspected from a saved image without desktop control.

The complete 18-case retest preserves the R2 map/objective/seed/role inputs and
60-turn cap: previously four victories/two defeats/12 limits; now 16 victories,
two defeats and no limits. All cases finish within 29 turns. Provenance and exact
coverage are verified in [derived evidence](../qa/tunnel_boundary_summary.json).
Connected placement recomputes team/objective positions after the bounds change;
this is not an isolated AI-strength comparison. Two containment defeats on turns
2/3 remain a pacing concern. Do not combine this subset with the old full matrix
to assert a new complete-current-source result.

Tests cover both maps at three viewport sizes, exterior/forced-anchor exclusion,
distinct connected encounter placement, unchanged original objects and duplicate
parity. The all-map source/compiled survey and real headless Godot loader checks
also pass. Other map perimeters remain separately reviewed/unreviewed in the
inventory; this correction does not certify them or update the R2 executable.

Validation: **27 focused tests passed**, including survey/placement and headless
Godot loading; the full suite passed **799 tests and eight subtests**. No desktop
takeover or visible game window was used.
