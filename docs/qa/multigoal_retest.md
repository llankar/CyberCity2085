# Multi-goal routing replay — 2026-11-15

Historical intermediate measurement. The [newer reachable-choice replay](reachable_choices_retest.md)
retests its 31 remaining limits after additional source/QA corrections.

The scoped current-source replay completed: **33 cases, two victories, 31 turn
limits, zero geometry errors**. All maps, factions, levels, counts, seeds,
policies, objectives and original 60-turn caps were preserved. The exact case set
and both source fingerprints were checked against the archived baseline.
Derived evidence is in [`multigoal_retest_summary.json`](multigoal_retest_summary.json).

Command:
`python -m tools.simulate_encounters --retest-limits runtime/authored_battles.json --output runtime/multigoal_limited_retest.json`

This is **not** a replacement 1,098-case matrix. Previously completed cases have
not all been rerun on the newer planner. The Windows candidate/archive still
contains its earlier 735-test snapshot; its hashes and historical reports remain
valid for that artifact, rather than describing the current worktree.

## Completed previously limited cases

| Map | Objective | Completion turn |
| --- | --- | ---: |
| city_industrial_data_vault.png | Elimination | 59 |
| wasteland_inner_02_collapsed_tunnel.png | Assassination | 53 |

The routing change chooses shortest legal endpoints rather than the first one
ranked by straight-line distance. No obstacle, spawn, objective or turn cap was
changed. Both completions remain long encounters and need pacing assessment.

## What the remaining limits mean

Among the 31 remaining limits, 27 had no more than three consecutive unchanged
end-of-round snapshots. Twelve had no unchanged completed round at all. This
rules out a blanket description of every limit as total inactivity, but **does
not prove useful progress**: long paths, repeated movement, misses and poor QA
decisions still need trajectory analysis.

| Map/objective | Longest unchanged streak |
| --- | ---: |
| wasteland_city_06_ruined_downtown.png / extraction | 36 |
| wasteland_inner_08_ruined_clinic.png / elimination | 29 |
| wasteland_inner_08_ruined_clinic.png / assassination | 29 |
| cybercity_inner_03_research_lab.png / civilian rescue | 13 |

The first three are priority stagnation cases. The fourth is a separate, shorter
stagnation signal. Inspect live occupancy, reachable targets and QA policy
decisions before changing authored terrain or mission rules. Full movement
traces are needed to distinguish traffic problems from an artificial player's
failure to reposition an available squad member.

## Regression evidence

The full suite passes **742 tests and eight subtests**. Seven focused planner/
replay tests also pass, including 200 seeded layouts checked against an independent
breadth-first shortest-path oracle, the reproduced five-versus-seven-step layout,
sealed nearby breach-line pockets, bounded work, unchanged-round diagnostics,
wide-map reorientation and original-case/cap preservation.

The shared planner uses actual endpoints and legal terrain, not a new combat
controller. [Rules and limits](../gameplay/multigoal_routing.md) are documented.
No desktop control was used. TAC-ENEMY-01 stage execution, TAC-ENEMY-05 balance,
mixed/support squads, campaign and graphical/playable release gates remain open.
