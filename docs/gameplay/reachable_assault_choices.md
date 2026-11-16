# Reachable assault markers and QA target choices

This iteration separates two different problems instead of treating every
limited simulation as a broken combat engine.

## QA policy correction

In the stalled extraction/clinic traces, the automated player kept selecting the
geometrically nearest enemy even when no approach to it existed. A farther enemy
had a legal route. The QA policy now tries its ordered candidates until it finds
a reachable approach instead of guarding forever at the first sealed target.
Assassination still prioritizes the designated target when reachable. Shooting,
movement, damage, costs and mission progress still go through the real engine.

This changes **the developer's automated player**, not player-facing controls or
enemy behavior. It does not prove that human players were trapped. No extra AP,
teleport, wall edits, objective relocation or relaxed turn cap was introduced.

## Production Starver correction

A free adjacent tile is not necessarily reachable: the prey itself can occupy a
doorway separating its two sides. Pack reservation previously chose a free tile
by geometric distance without verifying a route. It could advertise an unreachable
`SWARM` marker while a different adjacent tile was reachable.

Reservations now validate candidate routes against live occupancy, terrain and
impassable cover before claiming a distinct destination. The search uses actual
terrain dimensions and the existing bounded cardinal planner. The selected tile
is stable until the existing movement/prey/status disruption rules invalidate it.
If no candidate route exists, the enemy retains its ordinary approach priority
instead of promising an impossible destination. Execution rechecks legality and
still pays ordinary movement/stride costs and triggers overwatch.

This is reachability validation, not a coordinated multi-agent traffic scheduler.
Other units can move after reservation, so a legal approach can still be disrupted.
Bounds/profile propagation now reaches order reserve/reconcile/interrupt calls,
keeping the pure engine and view adapter on the same dimensions.

## Verification

Three focused regressions cover a sealed nearest QA target, a free but unreachable
Starver destination with a reachable alternative, and a case with no legal assault
square. The real enemy phase executes the advertised route with the normal bonus
stride/AP budget. Existing pack, reservation, movement, wide-map and replay tests
remain green. The full suite passes **745 tests and eight subtests**.

The [31-case replay](../qa/reachable_choices_retest.md) preserves the previous
parameters and caps. Its improvements combine both changes above and cannot be
attributed solely to stronger enemy intelligence. No desktop control was used.
