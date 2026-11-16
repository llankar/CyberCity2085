# Paid objective actions and terrain-aware assaults

The reference Arcade objective lifecycle now treats interaction as an action:

- A successful interaction costs **one AP**, reported in `ObjectiveResult` and
  the objective prompt/message. Failed, remote, contested or repeated attempts
  cost nothing and record no contribution.
- Progress is limited to one interaction **per squad per tactical turn**. Changing
  the active agent cannot bypass the download/rescue/extraction pacing.
- Only a living allied operative with an available AP may advance an objective
  during the player phase. Explicit actor arguments cannot bypass team/phase
  validation in `CombatEngine.interact_with_objective`.
- Defense, containment and assassination are passive victory conditions. Pressing
  E cannot mark them complete. Defense needs its hold interval, containment needs
  enemies neutralized without a breach, and assassination needs the assigned
  target eliminated.
- Once a breach marks an objective failed, moving the enemy away cannot undo the
  defeat. This preserves terminal outcomes across repeated lifecycle checks.

The low-level position/progress helper in `mission_objectives` remains a geometry
primitive. Runtime callers must use the engine lifecycle for authorization, AP,
once-per-turn limits, contesting and contributions. The Arcade E-key path does so
and already advances the selected unit when its AP are exhausted.

## Enemy pressure

Objective-minded doctrines can reserve `BREACH` toward active interactive goals
as well as defense/containment when no immediate attack takes priority. Raiders
and corporate samurai retain their combat-focused priorities. Mutant projection,
corporate links, precision and Starver approach rules still apply normally.

Reserved objective movement now uses the existing bounded cardinal A* utility.
Every proposed step obeys occupancy, impassable cover and the supplied terrain
predicate. It consumes ordinary movement AP/stride and triggers overwatch; there
is no teleport, free objective movement or terrain carving. An enemy reaching the
contest/breach zone stops there instead of walking away before the phase result
can detect its pressure. A completely blocked approach interrupts explicitly.

The route search considers at most five legal approach cells, each with the
existing bounded search. This avoids an unbounded planner on large maps; a more
distant route can remain undiscovered within that limit and is not claimed as
guaranteed reachability. Actual map-specific campaign validation stays open.

## Verification

Real-engine regressions cover action costs and rejections, squad-wide pacing,
passive-goal protection, durable failure, paid wall detours and all eight tactical
objective families. The simulation harness also supports `objective` and
`objective_counterplay` policies. Both pursue objective markers and contesting
enemies; the latter also dodges marked precision/toxin threats. Assassination
prioritizes its designated target. Other combat rules use the shared engine.

```
python -m tools.simulate_encounters --scenario objectives --output runtime/objective_qa.json
python -m pytest -q tests/test_objective_action_economy.py tests/test_objective_lifecycle.py
```

See [the objective baseline](../qa/objective_baseline.md). These are synthetic
arene tests, not a substitute for authored-map/campaign or visual playthroughs.
