# Combat engine boundary

`game/combat/` is the tactical battle rules package for the readable, gradual extraction of non-Arcade combat logic from `BattleView`.

## `CombatState`

`game/combat/state.py` owns the battle data that can be tested without rendering:

- active mission and optional battlefield objective;
- allied and enemy `Unit` lists;
- current turn phase, turn number, and active allied unit index;
- combat logs;
- tactical flags for small objective/status hooks that should not become view state.

## `CombatEngine`

`game/combat/engine.py` owns pure state transitions:

- `start_player_turn()` resets allied AP/status effects, advances the turn counter after enemy phase, and appends turn logs;
- `start_enemy_turn()` resets enemy AP and runs the existing pure enemy AI callbacks without owning sound or animation;
- `perform_action()` resolves AP-based actions such as movement, defend, first aid, overwatch, direct attacks with a supplied target, and end turn;
- `end_battle_check()` reports victory or defeat when one side has no living units.

The engine may mutate `CombatState` and `Unit` objects. It must not import Arcade, play sounds, create sprites, switch views, or apply campaign-level mission aftermath.

## `BattleView`

`game/views.py::BattleView` remains the adapter around the pure engine. Its responsibilities are limited to:

- keyboard/mouse input and target-selection UX;
- Arcade sprite setup, drawing, camera, combat HUD, particles, popups, screen shake, and attack lines;
- sound effects and music;
- mission fallout/debrief navigation after `end_battle()`;
- temporary sync with legacy fields while the migration is incremental.

When adding new combat rules, prefer adding them to `CombatEngine` first and let `BattleView` translate the returned result into feedback, sound, and navigation.
