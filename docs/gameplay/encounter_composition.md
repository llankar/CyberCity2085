# Authored counts, bounded specialist budgets

`create_enemy_units` now uses one deterministic composition plan before rolling
individual enemy levels. Mission `starting_enemy_count` remains authoritative,
including scripted zero-enemy events. No enemies are added to compensate for a
weak squad or removed to disguise difficulty. Existing theme stat multipliers,
weapons, commander support and individual level rolls remain in use.

Composition points measure role promotions within a faction, not equivalent
combat power between factions. Costs are grunt 2, heavy 3, elite 4, commander 5.
For count N, average squad level L and mission risk R:

```
bonus = min(N, N//3 + (floor(L)-1)//3 + (clamp(R, 1, 10)-1)//3)
budget = 2*N + bonus
```

At least half the roster remains ordinary troops. Specialist slots are capped
at `min(N//2, ceil(N/3))`. Heavy promotion unlocks at average level 3, elite at 4,
and one commander at 7 when at least three enemies are present. A commander is
attempted first, followed by affordable faction preferences. Unspent budget is
allowed; it never forces another specialist past the cap.

Corporate formations favor heavy support before additional elites. Raiders and
Novatek favor elites. Mutants favor heavies, shifting toward elite control at
risk 7+. Starver packs allow only one promoted body, including their existing
high-level commander; their extra stride and stronger bite remain intact.
Commander/precision/cast abilities still follow the actual combat rules.

Generation preserves the original first eight fallback spawn coordinates, then
uses distinct grid cells in the same right-side region. It no longer wraps onto
occupied spawns when a mission requests more than eight enemies. Over-capacity
requests raise an explicit error rather than stacking units. These are fallback
positions: the battle adapter still resolves map-specific terrain and deployment.

Generation accepts an optional RNG, preserving the ordinary default while making
QA seeds reproducible. No new campaign field or save migration is required.

## Reproducing the baseline

```
python -m tools.simulate_encounters --output runtime/encounter_qa.json
python -m pytest -q tests/test_encounter_composition.py
```

The CLI uses six factions, three progression bands, seeds 0–2, two layouts and
two simple player policies: 216 real engine battles. The synthetic squad consists
of four identical rifle agents at the requested level. `focus` shoots vulnerable
reachable enemies; `counterplay` first steps out of announced precision/toxin
threats when legal. Both move using legal bounded routes when no shot exists.
No health/AP/damage is fabricated after resolution. Runs stop at victory, defeat
or 30 turns; `turn_limit` is reported honestly, never treated as victory.

Each JSON row records inputs, roles, outcome, turn count, HP lost, losses,
survivors, infections, announced actions, dodges and interruptions. The helper
restores the process random state, including on exceptions; it is a synchronous
developer tool, not a production autoplayer or thread-safe parallel simulator.

See [the measured baseline](../qa/encounter_baseline.md). The test matrix also
checks all eleven existing themes across levels, risks and counts up to 20;
real generation verifies 32 distinct spawns. Mission objectives, manual maps,
deployment assets, role-specialized squads, human decisions and campaign pacing
need separate balance/playthrough evidence.
