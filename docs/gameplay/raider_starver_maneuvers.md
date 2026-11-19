# Raider and Starver maneuvers

## Raiders: isolate, shoot, reposition

At phase reservation a Raider prefers an agent with no living squadmate within
three tiles (96 world units, using the game's distance rule). Wounded/threat
scoring ranks the isolated candidates; it does not replace the isolated target
mid-phase merely because another agent becomes wounded. `ISOLATE` names this
priority. When nobody is isolated, the order is `SKIRMISH`.

Moving a squadmate back within that radius triggers a visible `squad_regrouped`
interruption. The Raider can select another isolated target or fall back to
skirmishing. Successive regrouping events can interrupt successive targets;
the interruption deduplication does not freeze the first replacement target.

After a ranged shot, including a miss, the Raider spends a remaining AP on one
legal, safer cardinal step if available. Safety prefers distance from all living
agents, with a small cover preference, while remaining within weapon range.
This step triggers normal overwatch. It is not a dodge, teleport or extra AP.
If boxed in, the Raider may fire twice instead. Adjacent melee attacks do not
grant a free disengage. A kill still ends the current activation under the
existing executor rule; it does not grant bonus movement.

Counterplay: keep buddies near vulnerable agents, block exits, suppress the
Raider, or put the exit under overwatch. The safety scorer does not secretly
avoid the player's overwatch, so that trap works.

## Starvers: melee pressure through separate approaches

Generated Starvers now have one-tile melee range across grunt/heavy/elite/
commander subtypes. Previously the maximum of theme and subtype ranges gave
even a Starver grunt a three-tile ranged attack. The executor also refuses ranged
attacks for the Starver doctrine, protecting existing/misconfigured unit data.

Against a prey target outside melee reach, each pack member reserves a distinct
free cardinal approach adjacent to that target. The `SWARM` order draws a small
destination marker and approach line. Adjacent pack members simply strike.
Four adjacent slots are available; excess members retain ordinary pursuit rather
than stacking multiple units on one slot. Existing defend/containment objective
pressure remains available through the objective order.

Movement toward the approach uses bounded cardinal A* over the existing legality
callback, occupancy, terrain mode and impassable cover. It can take an initial
step away from the prey to detour around a wall. Every step costs the ordinary
one AP and can trigger overwatch; arrival does not grant an extra bite. Search
work is bounded by the board estimate, capped at 4096 visited cells.

Subsequent requested Starver tuning adds one movement-only bonus stride per
activation, stronger melee and rare incurable infection. This supersedes the
earlier strictly two-step movement budget; see [Starver infection rules](starver_infection.md).

Moving the prey triggers `prey_moved`; occupying the approach triggers
`approach_blocked`. Both release the old surround marker and announce an ordinary
`RUSH` pursuit. The pack can still chase with its normal AP budget. Moving one
agent therefore does not cancel every pack member's whole turn for free.

Counterplay: move the prey, screen a reserved approach, use a chokepoint, suppress
a pack member or overwatch its lane. No new damage multiplier or stacking swarm
debuff is added in this slice.

## Validation and remaining limits

`tests/test_pack_maneuvers.py` exercises actual engine turns, shot/step AP costs,
overwatch removal, repeated regrouping, distinct approaches, melee enforcement,
wall detours, screening, moving prey, generation across subtypes and bounded
unreachable-route search. The HUD test checks the reserved approach coordinates.
The general reservation tests now use a neutral generic faction so they continue
testing target stability separately from the Raider's new one-shot/exit tradeoff.

These are authored tactical decisions, not a claim of universal path optimality
or complete encounter balance. Mutant/hybrid control, budgeted composition and
the release-wide dominant-action simulations remain open. Tests use pure turns
and drawing stubs, with no desktop control.
