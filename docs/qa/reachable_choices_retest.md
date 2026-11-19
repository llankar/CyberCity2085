# Reachable-choice replay — 2026-11-15

Historical intermediate result. The [blocked-objective replay](blocked_objective_retest.md)
subsequently retests its 27 remaining limits and records a map-floor fidelity concern.

Command:
`python -m tools.simulate_encounters --retest-limits runtime/multigoal_limited_retest.json --output runtime/reachable_choices_retest.json`

The 31 previously limited cases were replayed on the current combat sources:
**four victories, 27 turn limits, zero geometry errors**. The exact case set,
old/current source fingerprints, original parameters and unchanged 60-turn caps
were checked. Derived evidence is in
[`reachable_choices_summary.json`](reachable_choices_summary.json).

This is not a new full 1,098-case result. The previously completed cases were not
all rerun, so the combined historical/current totals must not be presented as a
single current-source matrix. The old Windows candidate remains its 735-test
snapshot; current sources pass 745 tests and eight subtests.

## Newly completed cases

| Map | Objective | Turn |
| --- | --- | ---: |
| city_industrial_power_substation.png | Recon scan | 43 |
| city_industrial_power_substation.png | Civilian rescue | 30 |
| wasteland_inner_08_ruined_clinic.png | Data theft | 60 |
| wasteland_inner_08_ruined_clinic.png | Sabotage | 60 |

The clinic completions remain long and occur exactly at the original cap. They
are genuine terminal results, not a raised limit or a relabeled incomplete run.

## Stagnation evidence

Of the 27 remaining limits, 26 have at most three consecutive unchanged
end-of-round states; 14 have none. The three earlier 36/29/29-round streaks no
longer occur in this replay. The research-lab civilian rescue still has a longest
unchanged streak of 13 rounds. These measurements do not establish that every
other case progresses usefully: repeated routes and costly movement can change
state without improving a tactical position.

The diagnostic traces proved a QA-player limitation: a nearer sealed enemy was
repeatedly preferred even though another was reachable. A separate production
fixture proved that a Starver could reserve a free square on the inaccessible
side of its prey. [Both fixes](../gameplay/reachable_assault_choices.md) now have
regressions. Since the engine and test policy both changed, the outcome delta is
not a controlled measurement of enemy AI strength alone.

## Remaining release work

Inspect research-lab congestion and long routes/mission pacing, then validate
mixed and understrength squads, support footprints, campaign consequences and
graphical playability. Rerun the complete matrix and rebuild Windows after the
next stabilization gate. TAC-ENEMY-01/TAC-ENEMY-05 and the overall goal stay open;
no arbitrary map simplification is used to close them. No desktop control was used.
