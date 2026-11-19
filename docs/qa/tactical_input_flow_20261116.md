# Real tactical input flow — November 16, 2026

Two integration tests now run the actual Arcade BattleView and CombatEngine in
isolated processes with explicitly hidden windows. They dispatch input methods
directly: no desktop input, window activation or visible application is used.
Audio is mocked and each fixture creates fresh agents; no player save is read or
written.

The flow enters deployment, dispatches Enter, places one enemy on nearby authored
walkable ground and enters fire targeting. Its HP is set to 100 so the test can
verify one nonfatal shot without invoking end-of-mission rewards.

Five checks run against real handlers and the real combat engine:

1. Escape cancels targeting without spending AP.
2. Clicking the rendered Fire button opens targeting without spending AP.
3. Right-click cancels and preserves both AP and journal preference.
4. The first target click only selects/previews: AP and enemy HP are unchanged.
5. The second target click resolves exactly one shot: AP goes from 2 to 1,
   enemy HP from 100 to 98, HP/stat state agrees, targeting closes and the shot
   appears in the combat log. Allied world positions remain unchanged.

Random rolls are forced to a hit and critical. This proves dispatch and command
integration, not hit-rate balance, damage tuning or a representative encounter.
Particles, popups, attack animations and aftermath are the actual view effects.

`tests/test_hidden_tactical_input.py` covers 960 x 640 with journal enabled and
1280 x 720 with it disabled. The former restores the journal; the latter restores
initiative. Both report ten bounded captions and zero omissions. The tests are
skipped on non-Windows systems without a display server; this Windows run did
execute both. The 45-second subprocess timeout limits a hung fixture.

Full regression: **864 tests and eight subtests passed** in 32.89 seconds.

Inspected real post-shot frames and JSON reports:

- `input_flow_20261116/fire_960.png` / `.json`
- `input_flow_20261116/fire_1280.png` / `.json`

Reproduce with `python -m tools.render_tactical_snapshot --output <path>
--deployment --begin-battle --targeting --exercise-fire --pan-x 64 --pan-y -32`.
Add `--width 960 --height 640` for the first; `--hide-log` for the second.
The command now writes a JSON sidecar alongside its image.

The images expose remaining feedback issues: a successful outgoing shot triggers
a broad green edge flash over the HUD, and critical popups can clip at the left
edge. Immediate post-shot images contain animation/shake; they do not prove
animation completion or frame pacing. These issues remain open, as do movement
confirmation under live input, enemy-turn/end-turn dispatch, casualty/debrief
transitions, continuous campaign playthrough, Godot parity and current Windows
distribution. This is a specific playable-input gate, not full release approval.
