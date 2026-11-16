# Blocked-objective replay — 2026-11-15

The 27 previously limited cases were replayed with unchanged maps, mission
parameters, seeds, policies and original 60-turn caps. Result: **27 turn limits,
zero geometry-check failures**. Exact case coverage, old/current fingerprints and
cap preservation were verified. Derived evidence is in
[`blocked_objective_summary.json`](blocked_objective_summary.json).

Command:
`python -m tools.simulate_encounters --retest-limits runtime/reachable_choices_retest.json --output runtime/blocked_objective_retest.json`

This scoped repair does not create another completed mission in the replay. Its
evidence is a corrected decision rule and reduced stagnation, not a claimed
win-rate improvement. The complete suite passes **748 tests and eight subtests**;
14 focused objective/order/assault regressions also pass.

## Research-lab rescue

Before the repair, the player policy could not route to the next civilian marker
and ignored an available hostile shot. The final trace had objective progress 1
and six surviving enemies, with a longest unchanged-round streak of 13.

After the repair, progress remains 1, but only two enemies survive and the longest
unchanged-round streak is zero. Combat/movement now occurs, while mission pacing
and route length still prevent completion before turn 60. This is evidence that
the policy no longer simply waits at the inaccessible marker; it is not proof of
good pacing or a human-playable resolution in every situation.

Across all 27 cases, 26 have no unchanged streak longer than three rounds; the
remaining case (ruined-clinic extraction) has a streak of six, increased from
zero in the prior replay. Changed combat choices alter RNG and subsequent state,
so individual trajectories need review rather than a blanket improvement claim.

## Additional map-fidelity finding

Inspection of the actual `wasteland_inner_08_ruined_clinic.png` file shows a dark
margin outside the drawn interior floor. The current manual-derived profile
allows `(160, 0)` at 1280×720; a stalled clinic trace placed an agent there. The
bottom-row image sample is dark RGB `(15,14,13)`, and the image inspection—not
brightness alone—suggests this margin should receive an explicit playable-area
review. The 03/08 clinic variants have identical image hashes.

This is **not automatically fixed by blocking dark pixels**. A manual boundary
review must preserve visible floor, real entrances and intended exterior space.
No wall source or compiled geometry was edited in this iteration. Existing
geometry assertions only prove compliance with the stored survey, not that the
survey perfectly represents playable floor in the artwork. Reopen that fidelity
check before interpreting long perimeter routes solely as AI failures.

## Remaining gates

Prioritize playable-area boundaries and route/pacing review for the clinic/lab
maps, propagate reviewed identical-art changes consistently, then rerun placement
and real battles. Full current-source matrix, mixed/support/understrength squads,
campaign and graphical/visual validation remain open. The earlier Windows archive
is unchanged. [Rules](../gameplay/blocked_objective_choices.md) distinguish the
production enemy repair from the QA-player correction. No desktop control was used.
