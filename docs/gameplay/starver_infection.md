# Fast, strong Starvers and incurable infection

Implemented in the reference Arcade combat engine and persistent campaign state.

## Combat rules

Starvers receive one bonus stride at activation reset, in addition to the usual
two AP. The first movement spends this stride before AP. They can therefore
move three ordinary steps, or reach melee with the stride and retain two attack
AP. This is a movement-only point, never a third attack. Suppressed, stunned or
panicked Starvers receive neither active AP nor a bonus stride. The stride resets
each activation and does not accumulate. Steps still obey walls, occupancy and
overwatch.

Their melee damage increases by 25% rounded up, with a minimum +2 damage. The
bonus is included in the shared attack context before defense modifiers and the
critical multiplier, so preview and resolution agree. Hit chance is unchanged.

## Rare infection

A damaging Starver melee hit against a surviving campaign agent rolls a separate
**0.5%** transmission chance (one in 200 qualifying hits). Misses, ranged hits,
non-Starver attacks, mechanical support assets and fatal bites do not transmit.
Critical hits use the same transmission chance, not a higher one. Repeat bites
cannot duplicate the infection or reset its timer.

Transmission immediately records a diagnosis in agent history and the tactical
log. The agent has **three strategic daily ticks** before irreversible conversion.
Mission travel/aftermath that advances the strategic calendar counts toward this
deadline. Ordinary combat turns do not. The dossier and roster show the remaining
days and label the infection incurable.

HP recovery, first aid, medical recovery and removal of ordinary combat statuses
do not clear the separate infection clock. There is no treatment action or cure
in this system. On expiry, the character's role becomes `starver`, the permanent
conversion flag is saved, the agent leaves the selected squad and can never be
deployed again. The dossier/history remains as a record of the former agent.
Converted characters do not participate as recovering human agents in recovery
dialogues. This does not automatically add a rematch encounter to later missions.

An agent already dead does not progress or resurrect through this system. The
conversion rule applies to living infected agents; healing an already converted
dossier does not make it deployable again.

## Persistence and verification

`Character` saves `starver_infection_days` and `starver_transformed`. Missing fields
in older saves default to uninfected, preserving compatibility. They are not
ordinary injury strings or temporary status effects, so routine cleanup cannot
accidentally cure them.

Tests exercise the exact probability boundary, actual bite damage, engine log,
non-transmitting attacks/assets/death, no timer reset, movement-only stride,
suppression, real campaign save/load, daily medical recovery, third-day conversion,
permanent deployment exclusion and roster countdown. No desktop control is used.

Full regression result: **665 passed, 8 subtests passed**.

Request verification (November 15, 2026): the current local implementation passes
all **28 focused tests** in `test_starver_infection.py`, `test_pack_maneuvers.py`
and `test_tactical_identity.py`, without opening a game window or controlling
the desktop. The full-suite result above belongs to the original implementation.

Reverified November 16, 2026 for the renewed Starver request: the same 28 focused
tests pass on the current local changes. No game window or desktop control was
used. These rules are already implemented locally; this verification does not
claim a fresh full-suite run or validation of a separately distributed build.
