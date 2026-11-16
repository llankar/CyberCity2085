# Selected mixed-team integration

The new fixture uses `create_player_units` with selected character names and
selected asset IDs, rather than synthetic generic allied units. It equips the
actual starter kits for samurai, sniper, psi and medic, alongside the starting
K-9 combat robot and Phantom support drone.

One test fits that six-unit team and six hostiles on all 122 authored maps at
1280x720. It checks legal, distinct cells and that terrain is never carved.
Another executes melee, rifle fire, psi and a robot missile against a surviving
target through the real combat engine, then allied treatment and drone overwatch.
AP and missile consumption are checked alongside successful resolution.

These tests prove selected-roster integration and shared action rules. The
production occupancy model still treats each unit as one tactical cell;
large-support physical footprints and visual sprite overlap are not certified.
Power-armor/pilot combinations, understrength balance, sustained mixed-team
battles and meaningful role/loadout tradeoffs remain open. The four-agent/two-
robot fixture is not evidence that every selected support configuration works.

No production combat source changed in this pass, so the live full authored
matrix retains its original source fingerprint. Tests do not open a window or
take desktop control. The R2 executable is unchanged by these test-only additions.

Validation: both new integration tests passed; the full suite passed **787 tests
and eight subtests**. The independent authored matrix remains a separate live
job; no partial map count is presented as its final result.
