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
- `end_battle_check()` delegates victory and defeat to the authoritative mission
  objective lifecycle instead of assuming every mission is elimination.

## Authoritative attacks

`game/combat/attack_resolution.py` owns both the calculation and execution of
attacks. `AttackContext` is immutable and contains range, cover, flank, hit,
crit, normal/critical damage, AP cost, missile cost, and line warning. The HUD
preview, player actions, enemy AI, and overwatch all consume this same context.

`AttackResolution` records whether the attempt was legal, hit, crit, damage,
defeat, consumed AP/resource, and a compact reason. Rendering may animate that
result but must not recompute combat odds or damage.

## Objective lifecycle

## Battlefield rules

`battlefield.py` supplies deterministic cover/hazard plans and the shared sight
trace. Adjacent cover protects its facing and permits peeking; intervening high
cover blocks attacks. Preview warns `LINE BLOCKED`, execution spends no AP on an
illegal shot, enemy ranged decisions respect the same trace, and obscured
overwatch retains its reaction. Low cover does not block sight. Allies on the
line produce a warning but never receive collateral damage from direct fire.

Fire applies 2 immediate HP damage plus burning, contamination applies 1 HP plus
contamination, and blackout removes 1 AP. Exposure occurs at the start of each
side's phase after AP reset; existing statuses tick separately. The HUD labels
the danger zones before commitment. Generated cover and zones reserve spawns
and objective anchors. A flood fill from deployment keeps sequential objective
markers reachable, relocating inaccessible art-derived anchors to the closest
connected cells. Inferred art profiles first receive weighted access lanes that
prefer existing open ground and connect the original mission anchors, preserving
approach distance. Newly opened cells have a visible cyan lane overlay. Authored
binary masks are never carved. A fixed objective card keeps phase instructions
readable even when the world marker lies under a HUD panel. The first packaged
visual check exposed the disconnected-spawn case; real-asset route tests and
production frames from an invisible native GL context now verify its correction.
Map-bound obstacles render as subtle contours to preserve background readability.
Art inference remains approximate on maps without authored masks.

### Objective interaction and evaluation

`game/combat/objectives.py` owns pure objective interaction and evaluation.
Each result exposes status, reason, message, phase, progress, and the acting
agent. The rules enforce one interaction beat per turn, multi-site progress,
sabotage counterpushes, assassination/defend/containment conditions, squad-wipe
failure, and marker contesting by living enemies.

`CombatEngine` records successful objective contributions in tactical flags so
the battle adapter can pass them into debrief reputation. Enemy AI may move
toward interactive markers when its doctrine has sufficient objective bias;
the view only renders the resulting phase and message.

The engine may mutate `CombatState` and `Unit` objects. It must not import Arcade, play sounds, create sprites, switch views, or apply campaign-level mission aftermath.

## `BattleView`

`game/views.py::BattleView` remains the adapter around the pure engine. Its responsibilities are limited to:

- keyboard/mouse input and target-selection UX;
- Arcade sprite setup, drawing, camera, combat HUD, particles, popups, screen shake, and attack lines;
- sound effects and music;
- mission fallout/debrief navigation after `end_battle()`;
- temporary sync with legacy fields while the migration is incremental.

When adding new combat rules, prefer adding them to `CombatEngine` first and let `BattleView` translate the returned result into feedback, sound, and navigation.
