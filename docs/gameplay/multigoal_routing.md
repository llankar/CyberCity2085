# Shortest legal approaches and limited-case replay

Approaches now use one bounded A* search toward a **set** of legal endpoints.
Previously, the helper sorted adjacent target cells by straight-line grid distance
and attempted them one at a time. A geometrically near cell could require a longer
walk around walls than another legal endpoint. A small reproduced layout required
seven steps with that policy despite a valid five-step approach.

`route_step_to_any` minimizes route length to any supplied endpoint. The existing
single-goal helper delegates to it, while shared unit approaches and objective
assaults provide their legal endpoint sets. Reserved Starver destinations still
provide exactly one endpoint; the planner does not change their promised tile.
Containment considers all legal cells on its breach line rather than only the
five geometrically nearest candidates.

Only one cardinal step is executed at a time. Ordinary AP/stride, occupancy,
overwatch and terrain rules are unchanged. No wall, objective, spawn or turn cap
was edited to improve the measurements. Searches retain a bounded visit budget;
exhaustion returns no step rather than inventing a route. Reorientation checks
now use actual terrain dimensions instead of a fixed 1280×720 fallback, with a
regression covering units beyond X=1280.

## Verification

An independent breadth-first oracle checks 200 seeded 8×8 obstacle layouts:
the returned step must reduce true shortest distance by one, or return none when
no endpoint is reachable. The original five-versus-seven-step example is replayed
to arrival. Other tests cover a distant legal breach crossing, search budgets,
wide-map target reorientation and the existing real engine movement contracts.

QA rows now record `unchanged_rounds` and `longest_unchanged_rounds`. A snapshot
includes unit position/HP/status and objective position/progress/completion after
each completed round. These counters indicate unchanged **end-of-round state**,
not an absence of attempted actions: misses, guarding or a move/back sequence can
still count. A 60-turn limit alone does not prove an AI deadlock.

```
python -m tools.simulate_encounters --retest-limits runtime/authored_battles.json --output runtime/multigoal_limited_retest.json
```

Replay selects only previously limited authored cases and preserves their map,
theme, level, risk, count, seed, policy, objective and original turn cap. It does
not run an unrelated default matrix first. Reports record old/current combat
fingerprints and explicitly identify their limited scope. A driver regression
verifies this filtering and cap preservation.

The earlier Windows candidate remains a frozen 735-test snapshot. These newer
source changes do not silently update that archive. The full 1,098-case baseline
is historical until rerun on the new sources; a limited replay cannot replace it.
See [the scoped findings](../qa/multigoal_retest.md) for measured results and open work.
