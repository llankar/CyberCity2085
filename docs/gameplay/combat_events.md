# Combat events

Combat events are the render-independent layer for mid-battle complications. They
live in `game/combat/events.py`, are resolved by `CombatEngine`, and are consumed
by `BattleView` only after the engine has returned descriptive results.

## Format

A combat event has three small data objects:

- `CombatEventTrigger`: the pure condition for activation. Current events use a
  turn milestone (`turn_at_least`).
- `CombatEvent`: the mission-derived event definition (`key`, readable `name`,
  `effect`, and `trigger`).
- `CombatEventResult`: a render-agnostic instruction with a `kind`, `event_key`,
  optional `message`, and a `payload` dictionary.

Supported result kinds are deliberately narrow:

| Result kind | Meaning | Typical payload |
| --- | --- | --- |
| `spawn_enemy` | Ask the view to create a concrete enemy unit and sprite. | `position`, `unit_type`, `enemy_subtype`, `stats` |
| `visibility_changed` | Ask the view/HUD to change visibility rules for a duration. | `fog_radius`, `duration_turns` |
| `log_message` | Add event text to combat logs and banners. | `banner` |
| `screen_shake` | Request camera shake without owning camera state. | `intensity` |
| `sound_key` | Request a sound by key without importing audio code. | `key` |

## Current complication mapping

The current layer keeps the original compact scope of dynamic complications:

- `rapid_response` and `mod_rapid_response` trigger reinforcements on turn 3.
- `watcher_drone`, `mod_watcher_drone`, `counterintel_ping`, and
  `mod_counterintel_ping` trigger blackout on turn 2.

Each event key is stored in `CombatState.tactical_flags["triggered_combat_event_keys"]`
after it fires, so calling the resolver again cannot duplicate an already
triggered complication.

## Rendering boundary

`CombatEngine.resolve_combat_events()` only returns data. It does not create
`Unit` sprites, play sound, shake the screen, or patch HUD fog constants.
`BattleView` translates those results into Arcade sprites, particles, sound
manager calls, combat-log lines, flash banners, and temporary fog changes.
