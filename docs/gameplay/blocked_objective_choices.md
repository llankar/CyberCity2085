# Clearing threats around a blocked objective

The research-lab rescue trace exposed a specific developer-policy failure. Its
next civilian marker was inaccessible, but the automated player kept trying only
that route and ignored a reachable hostile, including available shots. This was
not proof that the human player's controls prevented fighting.

The QA objective policy still advances the marker when a legal approach exists.
If no approach exists, it can take a legal shot, or approach another reachable
hostile, using ordinary engine actions and AP. It does not complete the marker
remotely, carve a passage, move the objective or raise the turn cap. This change
belongs to the simulation driver, not a new in-game player autopilot.

## Production enemy behavior

Objective-minded enemies can also have a blocked `BREACH` order with no unit
target. Previously the deferred-target logic only handled blocked orders already
aimed at an operative. Such an objective order could repeatedly hold despite an
available threat-clearance route.

Now an interrupted objective assault can nominate a reachable living operative
for the **next** player-phase reservation. The current activation still holds
and cannot make an unannounced alternate attack. The next order advertises its
target, using `HUNT` rather than immediately replacing it with the same blocked
objective priority. Normal attack/cast/command/pack rules still apply once that
new reservation is shown. The ordinary reservation policy runs again after the
phase; the mission objective is not permanently discarded.

If no reachable threat exists, no alternate is fabricated and the next normal
reservation can remain `BREACH`. The existing bounded search, terrain dimensions,
occupancy, cost and sight rules remain authoritative. No faction gains movement,
damage or extra AP through this change.

## Verification

Regressions exercise an unavailable QA objective with successful ordinary fire,
an actual blocked enemy assault that holds before advertising next-phase threat
clearance, and a blocked assault with no reachable alternative. The complete
suite passes **748 tests and eight subtests**.

The [scoped replay findings](../qa/blocked_objective_retest.md) preserve the prior
maps, mission inputs and caps. Outcome changes combine a production-enemy repair
and a QA-player correction; they do not isolate an enemy-strength coefficient.
No desktop control is used. Full matrix, mixed-squad balance, campaign and visual
release gates remain separate work.
