# Tactical Combat Retrofit — Audit and 1.0 Target

Date: November 13, 2026

## Product target

Arcade combat remains the authoritative, finishable tactical path. The retrofit
must make every activation answer three readable questions: **what is at stake,
what changes if I act, and what will the enemy probably do next?** Depth comes
from interacting positioning, roles, objectives, and consequences—not from a
large catalogue of disconnected abilities.

The intended rhythm is:

> read threat → choose position → combine roles → commit action → see causality
> → absorb consequence → adapt

Reference games inform principles, not copied content:

- XCOM / Zero Company: commitment, cover, intent, squad interdependence.
- Command & Conquer: silhouettes and battlefield roles readable at a glance.
- Pathfinder / Baldur's Gate: builds and companions express identity through
  consequential abilities and persistent outcomes.

## Evidence-based audit

The focused tactical baseline is green: **65 tests plus 3 subtests** cover the
engine, actions, movement, preview, upgraded AI, objectives, HUD, controls,
debrief, and faction identities. The full release suite was green at 462 tests
plus 8 subtests before this retrofit began.

### What already works and should be preserved

| Domain | Current evidence | Keep |
| --- | --- | --- |
| Loop | briefing → deployment → battle → debrief → campaign fallout | Yes |
| Action economy | two AP, move, weapon/psi attack, aid, overwatch, defend, end turn | Yes, rebalance |
| Terrain | grid movement, occupancy, generated low/high cover, map walkability | Yes, unify rules |
| AI | target scoring, cover seeking, flank attempts, commander aura, objective pressure | Yes, share resolver |
| Objectives | eliminate, extract, sabotage, data theft, containment, rescue, recon, defend, assassination | Yes, deepen win rules |
| Readability | intent cards, previews, ranges, fog, timeline, status badges, log, popups, action aftermath | Yes, simplify hierarchy |
| Identity | faction tactical profiles and role-sensitive starter equipment | Yes, make mechanically distinct |
| Consequences | wounds, stress, XP, scars, debrief, faction/district fallout | Yes, expose causal chain |

### Release-critical gaps found

1. **Resolution is not yet a single source of truth.** Preview estimates attack
   values, while `Unit` resolves independently. Player attacks consume cover,
   but flanking does not negate it; line of fire is only a warning. Enemy and
   player attacks therefore do not yet share one inspectable tactical context.
2. **Action costs have edge-case inconsistencies.** `Unit._perform_attack`
   spends AP on a miss, then enemy AI spends another AP in its miss branch.
   Missiles resolve as ordinary fire and do not visibly consume capacity.
   First aid is self-only and does not clear bleeding despite status semantics.
3. **Objectives are varied in text more than in phase structure.** Several
   objective prototypes use interaction counters, while the engine's terminal
   check still understands only squad wipe or enemy wipe. BattleView carries
   compatibility logic that should move behind an objective evaluator.
4. **Roles lack signature tactical decisions.** Equipment gates actions, but
   samurai, sniper, psi, medic/support, robot, and asset roles need one compact
   signature each that combines with teammates rather than replacing core fire.
5. **Terrain is defensive metadata, not yet a battlefield language.** Cover is
   generated and displayed, but direction, flank exposure, line blocking,
   destructibility, hazards, and objective lanes are not consistently modeled.
6. **Status effects are functional but shallow.** Suppression, stun, panic,
   bleeding, burning, and contamination need durations/sources/counters that
   previews and debrief can explain.
7. **Enemy telegraphs describe likely intent but do not reserve a plan.** The
   AI can recompute during activation, so the displayed promise is informative
   rather than a rule the player can deliberately disrupt.
8. **`BattleView` remains overloaded.** The pure engine boundary exists, but
   some objective resolution, action feedback, and rules orchestration remain
   in the view. Extraction must stay incremental to avoid destabilizing 1.0.

## Tactical 1.0 definition of done

1. Preview and resolution consume the same attack context: range, cover facing,
   flank, line of sight, defense, status, hit, crit, damage, and AP/resource cost.
2. Every action has an explicit cost, target rule, counterplay, and inspectable
   result; no action silently aliases another action.
3. Every mission objective has explicit setup, progress, success, failure, and
   enemy-pressure rules in the pure engine.
4. At least four squad roles and four enemy doctrines create different tactical
   decisions through small signature mechanics.
5. Cover, hazards, blockers, deployment zones, and objective lanes are authored
   or deterministically generated as one battlefield plan.
6. Enemy intent is stable enough to plan against and reacts only to documented
   disruption conditions.
7. HUD hierarchy makes active unit, AP, objective, danger, target outcome, and
   causal feedback readable without consulting the combat log.
8. Wounds, stress, kills, objective contribution, relationships, and memorable
   moments survive into debrief and campaign state.
9. Pure tactical simulations, UI regressions, full release tests, packaged build,
   and playable keyboard/mouse validation all pass.

## Scope controls

- No engine migration and no parallel Godot rules implementation.
- No giant ability tree; one signature mechanic per role before adding another.
- No real-time layer, base destruction simulation, or procedural campaign rewrite.
- New rules enter `game/combat/` first; Arcade translates results into visuals.
- Each implementation slice contains at most five tasks and closes with tests,
  documentation, backlog status, and playable/headless validation.

## First implementation slice — truthful attacks

1. `TAC-RULE-01` Add one pure `AttackContext`/`AttackResolution` path shared by
   preview and execution, including cover, flank, range, hit, crit, and damage.
2. `TAC-RULE-02` Correct AP/resource semantics for misses, aid, overwatch, and
   missiles; make every cost visible in results.
3. `TAC-AI-01` Route enemy attacks through the same resolver and preserve
   inspectable decision reasons.
4. `TAC-UX-01` Present the shared context in target lock and aftermath feedback.
5. `TAC-VAL-01` Add deterministic balance/regression tests, update docs/backlog,
   and validate a packaged playable encounter.

### Slice 1 result — November 13, 2026

Implemented one authoritative `AttackContext` and `AttackResolution` path for
player attacks, enemy attacks, previews, and overwatch. It now exposes the exact
range, cover, flank, hit, crit, damage, AP, and limited-resource calculation.
Flanking removes cover in both preview and execution. Enemy misses spend one AP
instead of two. Missiles gain a distinct accuracy/damage profile and consume
capacity even when they miss. First aid can target an adjacent ally and clears
bleeding. The target-lock panel and action deck display the same calculation.

Five deterministic regressions cover context parity, cover/flank, miss costs,
missile capacity, and adjacent stabilization. The canonical suite passes 470
tests plus 8 subtests before packaging and playable validation.

## Second implementation slice — objective-driven missions

1. `TAC-OBJ-01` Route all terminal checks through one pure objective lifecycle.
2. `TAC-OBJ-02` Give extraction, sabotage, data theft, rescue, and recon explicit
   phases instead of treating their labels as flavor only.
3. `TAC-OBJ-03` Let doctrine-weighted enemies pressure and contest interactive
   markers, while defensive breaches remain explicit defeat conditions.
4. `TAC-OBJ-04` Record successful agent interactions and turn repeated decisive
   contributions into a persistent debrief reputation moment.
5. `TAC-OBJ-05` Validate scenario rules, the full regression suite, Windows
   packaging, and packaged startup.

### Slice 2 result — November 14, 2026

`game/combat/objectives.py` now owns objective progress, victory, and defeat.
Extraction secures a witness and then moves to exfil on a later turn; sabotage
opens a one-turn counterpush; downloads cannot be completed twice in one turn;
rescue and recon retain sequential sites. Wiping enemies no longer incorrectly
ends these missions. Enemies with objective pressure move toward interactive
markers and block interaction while contesting them. The HUD names the current
phase, and successful interactions are credited to agents; two decisive actions
can award the `objective_specialist` / `Keymaker` debrief reputation.

The canonical suite passes 476 tests plus 8 subtests. The Windows build and a
five-second packaged launch smoke test both pass. Slice 3, battlefield language,
is now active.
