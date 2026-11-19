# Enemy-plan counterplay audit — November 15, 2026

## Runtime reservation integration

`CombatEngine` now owns an `EnemyOrders` book per battle. At player-phase start,
it reserves each enemy's target and movement priority. The HUD draws those same
orders, and the real `run_enemy_ai` activation consumes them. The legacy
`BattleView.run_enemy_ai` adapter also passes the engine's orders. Reinforcements
receive orders when introduced; dead enemies' orders are removed.

Ordinary target-score changes do not retarget during the phase. Invalidations are
explicit: target lost, objective completed, suppression/stun/panic, newly blocked
direct fire, or blocked movement. The engine records the reason in the combat
log; the next HUD label gets an `!` interruption marker. Incapacitated or blocked
orders HOLD; invalid target/objective orders re-evaluate once. A new player phase
refreshes reservations. A target reservation is a priority, not a promise of an
attack at an impossible range: the AI can advance toward that target before
firing. Flank and cover-seeking steps now trigger overwatch as ordinary advances do.

The small runtime book deliberately does not use the module-global prototype
manager. The standalone strategic-template cooldown/alternate manager described
below remains a compatibility API, not the battle controller. Strategic alternate
plans and faction coordination still need executable integration; this pass
proves target/priority reservation, not completion of the whole enemy-plan slice.

## Audit before correction (historical)

The previous plan slice overstated integration. `CombatEngine.start_enemy_turn`
calls `combat_system.run_enemy_ai`; it does not own an `EnemyPlanManager`, reserve
the HUD's predicted target or dispatch disruption events into plan state. The
existing `update_plan_state` compatibility method returns strategic metadata,
not an executable activation. Stable, disruptible plans in actual battles remain
a release requirement, not a completed feature.

Before this pass, the public AI disruption adapter called an undefined function.
The manager looked up a template using a faction normalizer on a plan key, then
accessed a nonexistent enum `.key`. Its recovery tick did nothing. Existing tests
mostly verified registry presence and labels, so these failures were untested.

The corrected lifecycle now:

1. Looks up the selected template by its actual plan key.
2. Accepts only registered disruption conditions at their severity threshold.
3. Records an explicit caller-supplied turn and a retry deadline. Repeated
   interruptions extend the deadline instead of shortening an existing delay.
4. Activates a registered alternate at the deadline, or retries the current plan
   when the data references an unimplemented alternate. No new fallback content
   is invented. Counters reset so the plan can execute again.
5. Keeps cancelled/completed/aborted plans terminal. Diagnostic disruption keys
   are JSON-compatible names, suitable for later save/UI integration.

## Intent preview

Strategic template labels remain explanatory context. Immediate intent uses the
unit's attack range, target cover, faction doctrine and unfinished objective.
A corporate hunter can advertise a flank against cover or seeking cover outside
range; a completed defend objective does not attract a breach preview. Empty
target lists produce HOLD. One-shot squad iterables work for every enemy.

This remains a priority prediction, not a guaranteed shot or reserved activation:
LOS, path feasibility and target reservation still need the battle-owned planning
integration. The change does not claim those missing guarantees.

## Validation and next gate

```powershell
python -m pytest game/combat/test_enemy_plans.py game/combat/test_ai_decision.py tests/test_enemy_plan_lifecycle.py tests/test_tactical_identity.py tests/test_enemy_ai_upgrade.py tests/test_combat_engine.py tests/test_combat_preview.py -q
```

Result: 62 passed. Tests exercise threshold rejection, exact retry boundaries,
registered/missing alternates, repeated interruptions, terminal cancellation,
the public adapter, serialized diagnostics and intent regressions. Existing
Arcade engine/AI tests remain green. These checks require no desktop control.

Original integration gate: a manager scoped to each battle, intent reservation before
player decisions, execution using that reservation, explicit disruption dispatch,
and a turn-cycle simulation proving that the displayed plan survives until
execution or is visibly interrupted. Campaign saves and other battles must not
share the module-level compatibility manager.

## Runtime validation

`tests/test_enemy_reserved_orders.py` runs actual `CombatEngine` phase transitions
and the enemy executor, including a case using the real attack resolver. It proves
target stability despite a newly wounded alternative, explicit target loss,
one-phase suppression, blocked sight, objective-directed movement and blockage,
objective completion, battle isolation, reinforcements and phase refresh.

Current targeted result: 70 engine/AI/preview/lifecycle tests plus 7 selected
Arcade view/deployment/rendering regressions pass.

The broader UI run at that audit found five Windows launch failures in
`godot_ipc.start_ipc_server` (`os.mkfifo` unavailable). The subsequent
[portable launch repair](windows_combat_launch.md) resolved them; the full suite
now passes 634 tests and 8 subtests. No desktop automation was used.
