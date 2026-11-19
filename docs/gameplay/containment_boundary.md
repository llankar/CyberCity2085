# Visible containment boundary

The reference Arcade HUD now draws the containment breach frontier across the
current battlefield width. A red strip and downward chevrons identify the losing
side; the label asks the player to keep hostiles above the line. The marker's
instructions also explain that eliminating the hostiles completes containment.

The engine fails containment when a living enemy's centre has `y <= breach_y`.
Units move on a 32-pixel lattice. The displayed frontier therefore follows the
upper tile edge of the last failing row, including when the threshold is not
grid-aligned. It uses the fitted threshold rather than the prototype's original
value. The danger overlay disappears when the objective completes.

Captured rendering tests compare the actual full-width line against the real
failure predicate at widths 960, 1280 and 1920 and aligned/non-aligned thresholds.
No window or desktop takeover is needed. These verify rendering calls and rules,
not GPU appearance or human readability in a running game.

Validation: **32 focused tests and three subtests passed**; the full suite passed
**762 tests and eight subtests**. An additional combined HUD/objective/RPG-only
invocation failed because those legacy RPG tests inherited real Arcade base
classes before installing their window stubs. The complete suite uses the stub
collection order and passes; standalone RPG test isolation remains a test-harness
limitation, not evidence from a real game-window launch.

The original overlay pass changed visibility and instructions, not spawn placement, enemy AP,
breach direction or encounter balance. The earlier 122-case containment sample
had 102 defeats and 20 victories; corridor orientation and approach time remain
open issues. Godot has not received this Arcade overlay.

## Follow-up: path-based hostile placement

Authored containment placement now measures cardinal paths to every walkable
cell on the losing side. It prefers spawns at least four steps away, exceeding
the Starver's three-move activation. It retains the fitted line, original walls,
objective and full hostile headcount. When fewer than the required number of
cells meet four steps, it chooses the greatest minimum distance that fits the
whole group. It never grants immunity or changes enemy AP.

All 122 maps fit at three resolutions with six allies/eight enemies. Only
`city_exterior_elevated_freeway.png` cannot meet four steps in this sample:
two steps at 1280x720, one at 960x640. Its horizontal corridor needs a separate
orientation/deployment redesign; the current fallback is explicitly constrained.

[The 122-battle retest](../qa/containment_opening_summary.json) verifies current
combat-code and survey hashes: 21 victories, 99 defeats, two 60-turn limits,
no geometry errors. Previously: 20 victories, 102 defeats, no limits. The freeway
still loses on turn 1. Power-substation and research-lab cases now reach the cap
instead of losing; longest unchanged-state streaks are one/zero turns, so these
results do not establish static deadlock, but they remain unresolved pacing
regressions. No balanced-containment claim is made.

Validation: 764 tests/eight subtests passed before adding two final fixtures;
all four containment tests then passed, including real Starver activation and
capacity-limited placement. No interactive window or desktop control was used.

## Follow-up: fit the frontier before accepting a shallow approach

If the original line cannot provide four-step approaches for the entire hostile
group, placement now tries successively shallower allied deployment bands. It
keeps the largest band that fits all allies, a line one row above that band,
and enough distant hostile cells plus space for objective markers. Typical maps
retain their original deployment and line. If no such band fits, the previously
documented greatest-feasible-distance fallback remains.

This addresses the freeway's shallow north/south span without rotating controls,
editing walls, removing enemies or changing AP. The existing HUD reads the
fitted line directly. Tests explicitly cover the freeway at both smaller
viewports, full authored placement, objective separation and real activation.

The prior two limited cases were inspected through real engine phase snapshots:
the power-substation's last hostile lost HP on turns 57–60 (ending at 26 HP),
while the research-lab survivor and an enemy traversed the long outer route on
turns 55–60. They were not static stalls in that sample. Longer routes and
mission pacing remain unresolved; no turn cap has been raised to disguise them.

Current validation: **767 tests and eight subtests passed**. The
[122-case frontier retest](../qa/containment_frontier_summary.json) retains
21 victories/99 defeats/two limits, with no geometry errors or first-turn
defeats. The freeway still loses under the rifle policy, now on turn 2. At
1280x720 its fitted line is 128 (minimum approach four steps), at 960x640 it is
96 (five steps), and at 1920x1000 the original 192 remains (five steps).
No overall balancing claim or updated Windows-build claim follows from this.
