# Engine evaluation: Godot combat spike

Status: **spike completed, no migration decision taken**.

## Scope evaluated

The experiment lives in `experiments/godot_combat_spike/` and is intentionally outside the Arcade runtime. It reproduces only one tiny tactical mission:

- an 8x6 grid;
- 2 agents (`agent_echo`, `agent_vesper`);
- 2 enemies (`enemy_raider_a`, `enemy_raider_b`);
- cardinal movement, adjacent attack, and end-turn handoff;
- JSON export/import fields compatible with the current combat concepts: `mission_id`, `units`, `hp`, `ap`, `turn`, `turn_number`, and `result`.

## Comparison with current Arcade implementation

| Criterion | Godot spike observation | Arcade/current game observation | Early read |
| --- | --- | --- | --- |
| Iteration speed | A small scene can be opened and edited visually, but team setup would need Godot installed and conventions for exported state. | Existing Python tests and Arcade code are already wired into the repo workflow. | Arcade remains faster for rules changes today; Godot may become faster for visual scene iteration later. |
| Readability | Godot scene/script split is readable for the small grid, but rules in GDScript duplicate Python combat concepts. | `game/combat/` already separates pure state transitions from rendering. | Current Python rules are more readable for production combat until a formal bridge exists. |
| Testability | JSON contract can be checked from Python, but full Godot behavior needs Godot CLI or scene tests. | Pure combat engine tests run with the normal Python suite. | Arcade/Python is stronger for automated tactical-rule tests right now. |
| Asset integration | Godot would likely improve placement, animation, and scene composition once asset import rules are defined. | Current assets are PNG-oriented and already consumed by Arcade screens. | Godot has potential upside, but migration cost is not justified by this tiny spike alone. |
| Migration cost | Requires maintaining or translating combat state, input, HUD, camera, and save boundaries. | Production code already contains combat, UI, campaign fallout, and debrief integration. | High. Do not migrate without a staged adapter plan and explicit decision. |

## Decision

Do **not branch** this spike into the main game yet. The experiment is useful as a reference for visual/scene iteration, but it currently duplicates combat rules and lacks the automated coverage depth of the Python combat engine.

## Follow-up options

1. Keep the spike archived as an evaluation artifact.
2. If Godot remains attractive, run a second spike focused only on asset/camera/HUD feel, not combat rules.
3. Decide on a one-way JSON replay/export adapter before any production integration.
