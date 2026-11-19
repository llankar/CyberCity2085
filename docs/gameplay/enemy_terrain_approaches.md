# Shared legal enemy approaches and real-map combat QA

All enemy doctrines now use the same bounded cardinal approach search previously
used by Starvers. Ordinary enemies could previously choose only a direct step
toward their target; a wall requiring an initial step sideways or away could keep
them idle indefinitely. The shared helper tries legal cells adjacent to the
reserved target, retaining a Starver's distinct reserved approach where present.
It does not change targets, carve terrain, teleport or grant AP.

Impassable cover is checked even when a caller provides no terrain profile.
Cover-seeking also moves one cardinal cell per AP, rather than buying a diagonal
two-cell displacement. Every executed step still triggers ordinary overwatch.
The legal-cell callback reads live occupancy; only the immutable blocked-cover
coordinate lookup is precomputed for the AI pass to avoid repeated linear scans.
Searches retain their bounded visit limit; this is not a universal reachability
guarantee through occupied bottlenecks.

If an approach is blocked and another living target has a legal approach, the
battle-owned order book remembers that alternative for the next player phase.
The current activation still holds; it cannot redirect an unannounced shot.
The next reservation announces the new target before execution. Death of the
alternative cancels the suggestion, and corporate command links still apply.
This is a small executable reorientation rule, not completion of every strategic
template stage/alternate in TAC-ENEMY-01.

## Cover progression

The pure engine now refreshes cover bonuses when reserving/reconciling intents
and starting the player phase. This removes reliance on Arcade's per-frame
refresh for target selection and movement priorities. Numerical attacks continue
using directional cover in the shared resolver.

After an enemy uses its first AP to reach cover, it can shoot with the next AP
when a shot is possible. Otherwise it spends that AP guarding if actually at
cover, instead of undoing its movement toward the target. At the next reservation,
the refreshed cover state lets it resume an approach. This fixes a repeated
move-to-cover/move-back loop without creating a permanent defensive stance.

## Authored-map simulations

```
python -m tools.simulate_encounters --scenario authored --seeds 1 --output runtime/authored_battles.json
```

The authored scenario uses every playable catalog entry, including exact-art
duplicates as separate map entries. It runs elimination plus all eight objective
families at level 4/risk 5, with six generated enemies, four rifle agents, seed 0
and an objective/counterplay policy: **1,098 battles**, each capped at 60 turns.
City entries cycle corporate samurai, Three Sevens robots and Novatek; wasteland
entries cycle Starver, mutant and Raider. It is not every faction on every map.

The loader, connected placement, real manual terrain, map-pool hazard seed,
cover generation, objectives and real engine phases are used. Assassination picks
the highest-ranked enemy as in BattleView. The driver checks living-unit geometry
after resolved player movement/actions and enemy phases. Overlapping units or an
authored-obstacle entry produce an explicit error and a failing CLI exit code.
Reports include each map, objective, outcome, turn count, losses, survivor count,
contributions, interruptions and the combat-source fingerprint captured at start.

`--objective eliminate` restricts the authored pass for a smaller comparison run.
The player policy now tries multiple legal approach cells instead of giving up
when its single geometrically nearest candidate cannot be reached. It remains a
simple omniscient QA policy rather than a production player AI or human benchmark.

The earlier synthetic baselines are historical: their player approach policy and
cover-cache behavior preceded this repair. Running their commands on current
sources generates a new measurement, not necessarily their old numerical totals.
See [authored-map findings](../qa/authored_battle_baseline.md) for current evidence.

The same four-rifle squad cannot establish balance for mixed roles, support
assets, understrength teams, fog-limited decisions, reinforcements or campaign
aftermath. These and visual/playable Windows release gates remain open.
