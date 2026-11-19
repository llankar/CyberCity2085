# Corporate command network — tactical rules

## Read, commit, disrupt

Corp Strike and Three Sevens now share a compact coordination rule: a living
commander links nearby soldiers of the same doctrine within four tiles (128
world units), with a clear sight line. Suppression, stun or panic disables the
commander's links. Different factions cannot borrow each other's leadership.
The closest eligible commander wins; multiple commanders do not stack support.

At phase reservation, linked soldiers commit to the leader's target. Grunts
advertise **FOCUS**; a heavy with a clear ranged shot advertises **SUPPRESS**.
An objective-focused leader can instead coordinate a **BREACH**. The two
corporate doctrines retain their distinct specialist-hunt versus objective
priorities. Reinforcements get orders, but existing soldiers do not silently
relink to a new leader in the middle of the player's phase.

The HUD adds `[LINK]` and a line to a visible commander. A hidden commander
does not have its position disclosed by that line. Doctrine text in the
briefing explains the link, suppression cost and counterplay.

Killing or incapacitating the leader, pushing it out of range, or cutting the
sight line interrupts dependent orders with `command_lost`. This happens in
the HUD reconciliation and again during real AI execution, so a leader killed
by overwatch cannot coordinate soldiers activating later in the phase. The
soldier falls back to its own doctrine with an explicit interruption marker
and log entry. Existing target-loss/status/objective/blockage rules still apply.

## Suppression and accuracy

A heavy's suppressive shot costs **two AP**, including on a miss. It resolves
one ordinary ranged attack through the shared resolver; a hit also applies the
existing suppression status to a surviving target. Suppression consumes the
target's next phase AP under the existing status rules. It does not stack
multiple copies. After repositioning leaves only one AP, the heavy can fire
normally but cannot add suppression. Leaving the reserved shot's range is a
visible `target_repositioned` interruption rather than a free suppressive chase.

This trades the heavy's second shot for control. It is not yet proof that every
encounter composition is balanced; multi-heavy encounter budgets and repeated
suppression still need the Slice 5 composition simulations.

The existing commander accuracy support is now checked at each attack, with the
same range/faction/sight/status gates. It grants at most +1 AGI and restores the
exact original stat in a `finally` block, including values already capped at 99.
The previous phase-wide mutation could persist after a leader died and could
reduce a capped stat on restoration. Generic/noncorporate leaders retain local
accuracy support for their own doctrine but do not gain corporate shared orders.

## Verification

`tests/test_corporate_command_network.py` covers follower-first ordering, shared
targets, AP cost on hits/misses, status consumption, four ways to sever a link,
mixed-faction isolation, non-stacking/capped stats, exception restoration and
commander death during actual engine/overwatch activation. The HUD regression
checks that hidden commander positions remain concealed. Tests use pure engine
turns or stubbed drawing; no desktop control is needed.

Full regression result: **645 passed, 8 subtests passed**. Focused
command-network/HUD/reservation result: 30 passed.

Strategic template-stage alternates, the other faction doctrines and composition
QA remain separate open work. This is the corporate combined-arms slice, not a
claim that the entire tactical retrofit is complete.
