# Robot and Novatek precision windups

TAC-ENEMY-04 uses the existing `corp_samurai_robot`, `corp_37_robot` and
`novatek_hybrid` rosters for its machine/hybrid precision doctrine. There is no
new faction, campaign routing rule, asset set or tactical controller. Human
corporate troops and power armor keep their previous behavior.

Only elites and commanders prepare precision shots. At player-phase start, a
specialist reserves its target and position when more than one cell away, within
weapon range and in clear sight. Corporate followers first inherit their leader's
target, then reserve a lock when eligible. Heavy robots keep two-AP suppression;
precision does not replace their combined-arms role.

The `LOCK` HUD marker shows the target, two-AP commitment, 30% critical chance and
the counterplay: move the target or cut sight. A different wounded target does not
silently attract the reserved shot. Moving even one step breaks the lock, including
movement that stays inside weapon range. Range loss, loss of a target or linked
commander, and loss of the second AP also spoil the windup. These checks run both
when reconciling the HUD and immediately before activation, so earlier enemy
actions/overwatch can invalidate a lock.

Spoiling aim costs one AP after activation reset. The order becomes `HUNT`, its
marker clears, and remaining AP can fund one ordinary action. Repeated HUD redraws
cannot apply the penalty repeatedly or rearm the lock. Reopening sight does not
restore precision during that phase. Suppression, stun and panic use the existing
full activation interruption instead. A successful attempt, including a miss,
sets a two-activation cooldown before the specialist can mark again.

An intact lock uses the shared attack resolver with:

- Two AP for one shot, including a miss.
- +2 attack value after existing stance/state adjustments, improving hit odds and
  adding two base damage before defensive and critical modifiers.
- 30% critical probability on a successful hit, replacing the normal 12%.
- Normal weapon range, directional cover, defense, LOS, command support and damage
  rules. No armor penetration, automatic hit or Starver infection.

The battle log records the shot or miss and its two-AP cost. The pure engine and
legacy battle-view adapter consume the same reservations and action results.
The global attack context is also used for numerical preview and direct resolver
tests, rather than duplicating an enemy-only damage formula.

Engine tests cover the three real roster themes, target motion, LOS reopening,
AP loss, suppression, misses, exact critical threshold, cover, target loss,
mid-phase commander loss, unchanged heavy suppression, cooldown and exclusions.
The HUD test checks the real reserved marker and its interrupted replacement
without opening a desktop window. Encounter-level balance and visual playthrough
remain separate release gates; these tests do not establish an optimal balance.
