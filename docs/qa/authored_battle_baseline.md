# Authored-map combat validation — 2026-11-15

This report now describes the **archived Windows candidate**, not the latest
worktree. See [the newer scoped replay](multigoal_retest.md) for subsequent
multi-goal routing changes. The complete newer-source matrix has not been rerun.

The candidate-source pass has **completed**. Execution/coverage checks pass;
33 turn-limited battles keep the encounter-balance release gate open.

```
python -m tools.simulate_encounters --scenario authored --seeds 1 --output runtime/authored_battles.json
```

It covers 122 playable maps × elimination/eight objective families: 1,098 battles,
with four rifle agents, six enemies, level 4/risk 5, seed 0 and a 60-turn cap.
Runtime output records explicit victory/defeat/turn-limit/error outcomes and a
combat-source fingerprint. Geometry checks use the production manual terrain,
connected placement, cover/hazards and engine phases. No desktop control is used.

The exact map/objective/seed set was checked against the production catalog:
122 maps, nine objective variants per map, 1,098 distinct rows, zero missing or
duplicate cases, and zero error outcomes. All rows used manual terrain and
passed living-unit geometry checks. The recorded combat-source fingerprint
matches the candidate's combat sources. Derived counts and every limited case are stored in
[`authored_battle_summary.json`](authored_battle_summary.json); the complete raw
report is also included with the Windows candidate archive.

| Objective | Victories / 122 | Defeats | 60-turn limits |
| --- | ---: | ---: | ---: |
| Elimination | 106 | 9 | 7 |
| Extraction | 118 | 0 | 4 |
| Data theft | 118 | 0 | 4 |
| Sabotage | 118 | 0 | 4 |
| Recon scan | 114 | 2 | 6 |
| Civilian rescue | 114 | 3 | 5 |
| Defend | 120 | 2 | 0 |
| Containment | 24 | 98 | 0 |
| Assassination | 115 | 4 | 3 |
| **Total** | **947** | **118** | **33** |

706 victories occurred while enemies remained alive. The four-rifle squad and
one level/risk/seed sample do not prove campaign balance. In particular, the
containment policy needs control-oriented squads and real player tactics before
changing damage or breach timing.

## Remaining limited cases

| Map | Limited objectives |
| --- | ---: |
| wasteland_inner_02_collapsed_tunnel.png | 7 |
| wasteland_inner_03_ruined_clinic.png | 6 |
| wasteland_inner_07_collapsed_tunnel.png | 6 |
| wasteland_inner_08_ruined_clinic.png | 5 |
| cybercity_inner_03_research_lab.png | 3 |
| city_industrial_power_substation.png | 2 |
| city_interior_safehouse.png | 2 |
| city_industrial_data_vault.png | 1 |
| wasteland_city_06_ruined_downtown.png | 1 |

Inspect live occupancy, target alternatives, traffic and the simple QA player's
choices in these cases. Do not relabel limits as wins or remove difficult maps
from the matrix. Deferred reorientation reduces an inaccessible-target loop but
does not establish a universal solution to occupied bottlenecks.

## Completed evidence so far

- Before the shared-route repair, the 122-map elimination pass produced 106
  victories, two defeats and 14 turn limits. No geometry assertion failed.
- A subsequent pass with shared approaches, cover progression and the improved
  player approach policy produced 106 victories, ten defeats and six limits.
  That measurement preceded the latest deferred target reorientation. It is an
  intermediate result, not a current-source completion claim.
- Unit-level regressions prove legal paid detours for all seven doctrine families,
  impassable cover without a terrain callback, cardinal cover movement, guarding
  instead of undoing cover movement, and announced next-phase retargeting after
  an inaccessible approach. Two map-based tests run actual engine phases.
- The full regression suite after the latest gameplay repair passes **732 tests
  and eight subtests**.

These comparisons include both engine changes and QA-player corrections; they
cannot isolate a win-rate effect caused by enemy intelligence alone. More
defeats can mean enemies reached combat, rather than an unexplained regression.

## Diagnosed issues and limits

The prior intermediate limits included a blocked-target problem. In the research
lab case, several Raiders could approach one surviving agent but repeatedly
selected another with no legal approach. The current repair defers a reachable
alternative until the next advertised player phase, preserving counterplay rather
than making an unannounced same-phase shot. Corporate command cohesion still
applies; this is not a full implementation of all strategic template stages.

The QA player also previously selected just one candidate approach tile. Trying
multiple candidates removes an avoidable driver limitation. It still lacks human
traffic management, mixed roles, support assets and fog-limited decision-making.

The process, exact coverage, source match, errors and limited rows have now been
inspected. TAC-ENEMY-05 remains partial because encounter/campaign balance and
playable visual validation are unfinished. The Windows candidate itself builds
and passes its window-free executable smoke; that does not close these gates.
