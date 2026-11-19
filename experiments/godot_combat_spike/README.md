# Godot combat spike

Experimental Godot 4 project for evaluating tactical combat feel without migrating CyberCity2085.

## Scope

- Isolated from the Arcade runtime: no imports from `game/`, no routing from production screens.
- Minimal mission only: 8x6 grid, two named agents, two enemies, movement, adjacent attack, turn handoff.
- JSON import/export shape mirrors current combat concepts: `mission_id`, `units`, `hp`, `ap`, `turn`, `turn_number`, and `result`.

## Manual run

Open this folder as a Godot project and run `scenes/combat_spike.tscn`.

Controls:

- Arrow keys: move selected agent.
- Space: attack first living enemy if adjacent.
- Tab: switch agent.
- T: end turn.
- J: print exported JSON state.

Decision gate: this project must remain disconnected from the main game until `docs/gameplay/engine_evaluation.md` records a follow-up decision.
