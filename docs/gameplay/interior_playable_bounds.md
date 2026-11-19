# Safehouse and research-lab exterior bounds

Phase traces placed safehouse agents/enemies at `y=0` and the lab survivor at
`x=0`, while the source artwork shows these routes outside the buildings. Both
original images and saved diagnostic overlays were inspected without desktop
control. The correction adds only manual, non-opaque exterior masks; all 41
safehouse and 32 lab walls/props remain unchanged under golden-hash tests.

Rectangles use the existing 960x540 authoring canvas:

| Map | Exterior masks |
| --- | --- |
| `city_interior_safehouse.png` | top (0,0)-(960,23); bottom (0,522)-(960,540); west (0,23)-(24,522); east (943,23)-(960,522); northern notch (219,0)-(284,40) |
| `cybercity_inner_03_research_lab.png` | top (0,0)-(960,20); bottom (0,523)-(960,540); west (0,20)-(22,523); east (946,20)-(960,523); northern notch (234,20)-(309,40); northeast exterior (800,20)-(946,42) |

The compiled totals are 46/38. No interior opening, AP, weapon statistic or turn
cap changed. Connected placement recalculates legal team/objective positions;
outcome differences are therefore terrain/placement effects, not isolated AI
improvements. Forced anchors cannot cut through the new masks.

The full 18-case map/objective retest ends with **17 victories, one defeat and
no limits**; exact original inputs/caps and survey provenance were checked in
[the derived report](../qa/interior_boundary_summary.json). The separate replay
of all 22 formerly limited R2 cases now has **17 victories, one defeat and four
limits**, all on other maps. See [remaining cases](../qa/r2_limits_after_interior_summary.json).
This subset does not establish a new full 1,098-case result or rule out regressions
in previously successful encounters elsewhere. The lab containment defeat on
turn 3 still needs a pacing assessment.

Validation: **27 focused tests passed**, including all-map survey/placement and
headless Godot loading; **806 tests and eight subtests passed** in the full suite.
The new tests cover three viewport sizes, borders, forced anchors and preservation
of all original obstacles. Other perimeter reviews remain explicit in the
inventory. R2's distributed archive predates these data corrections.
