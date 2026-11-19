# Enemy control effects belong to the engine

The incoming-phase audit found two existing combat effects implemented only by
Arcade visual callbacks: heavy melee stun and player-overwatch suppression.
Headless combat therefore omitted those effects, and another adapter could
produce different tactical outcomes.

The shared attack resolver for enemy AI now stuns a surviving target after a
damaging heavy melee hit. Shared overwatch resolution suppresses a surviving
enemy after a damaging shot. The Arcade callbacks only display the corresponding
feedback; they do not apply these statuses again. Misses, zero-damage attacks
and dead targets do not receive these control statuses.

Five tests cover actual resolution with/without the actual visual callbacks,
exactly one status application, and missed heavy melee/overwatch without control.
No visible window or desktop input is involved. This preserves the reference
Arcade rules while correcting headless behavior; older simulation matrices
predate this parity correction and do not validate the current balance.

Final regression before commit/push: **882 tests and eight subtests passed**.
The six previously tracked generated Python bytecode files are removed from Git
tracking, retained locally and covered by the existing ignore rules.

This focused change does not close the whole incoming-phase audit. Miss versus
zero-damage-hit presentation, casualty morale callbacks, consecutive attack
sequencing and full mission/campaign/controller/release validation remain open.
