# Clinic boundary validation — 2026-11-15

Scope: both identical clinic map entries × elimination/eight objective families,
four rifle agents, six enemies, level 4/risk 5, seed 0, original 60-turn cap.
Clinic 03 uses mutants and clinic 08 uses Starvers, matching the baseline matrix.

| Measurement | Victories | Defeats | Turn limits |
| --- | ---: | ---: | ---: |
| Before manual boundary correction, 18 cases | 4 | 2 | 12 |
| After boundary correction, same 18 inputs | 14 | 4 | 0 |
| Replay of the older 27 limited cases | 9 | 0 | 18 |

Every post-correction clinic case terminates. Elimination completes on turn 16
for clinic 03 and 11 for clinic 08. Source/current-survey hashes, exact map/
objective/seed coverage, unchanged caps and geometry compliance were checked.
Derived evidence is in [`clinic_boundary_summary.json`](clinic_boundary_summary.json).

The broader 18-case check matters: a limited-only replay excludes previously
completed scenarios and cannot detect their later regressions. Do not combine
the 27-case subset and other historical results into a current full-matrix total.

## Interpretation and regressions

Removing exterior padding changes which connected interior component the
existing placement helper uses. Unit and objective cells are recomputed. The
outcome delta is therefore a map-data/placement correction, **not** an isolated
enemy-strength improvement. All 34 preexisting obstacle records are unchanged.

Defense now fails during turn 1 in both clinic cases; containment fails on turns
2/1. Initial placement safety checks pass, so these are not pre-failed starts.
The compact encounters become much more immediate. Investigate hold-zone
spacing, roles/control and player policy before claiming balance or changing AP.
Fewer limits alone do not establish that every mission is well designed.

The full suite passes **756 tests and eight subtests**. The 28 focused clinic/
survey/placement tests pass, including the actual headless Godot wall loader.
All 122 stored surveys still reproduce their authored sources; both clinic
duplicates have matching obstacle lists. No desktop control was used.

## Completed full-matrix baseline

A complete pass finished after the clinic correction and before defense-opening
spacing changed:

`python -m tools.simulate_encounters --scenario authored --seeds 1 --output runtime/authored_after_clinic_bounds.json`

The 1,098 cases produced **957 victories, 121 defeats and 20 turn limits**, with
no geometry errors. Exact map/objective/seed coverage and each survey hash were
checked; see [derived results](post_clinic_full_summary.json). Defense accounted
for 118 victories and four defeats; containment for 20 victories and 102 defeats.
This is a pre-spacing baseline, not a full run of the later defense changes.
Other map boundaries,
encounter pacing, mixed/support teams, campaign and visual release gates remain
open. The earlier Windows archive has not been rebuilt.
