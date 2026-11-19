extends Node
## Global signal bus. Registered as autoload "CombatSignals" in project.godot.
## All cross-component communication flows through here so nodes stay decoupled.

# ── Input events (emitted by UnitToken / Battlefield, consumed by CombatRoot) ─
signal unit_clicked(unit_id: int, is_enemy: bool)
signal unit_hovered(unit_id: int, is_enemy: bool)
signal unit_unhovered()
signal cell_clicked(cell: Vector2i)
signal cell_hovered(cell: Vector2i)

# ── Player actions (emitted by HudController buttons, consumed by CombatRoot) ─
signal action_pressed(action: String)

# ── Game events (emitted by CombatRoot, consumed by Audio/FX/HUD) ─────────────
signal unit_moved(unit_id: int, is_enemy: bool, to_cell: Vector2i)
signal unit_attacked(attacker_id: int, attacker_enemy: bool,
                     target_id: int,   target_enemy: bool,
                     damage: int, hit: bool)
signal unit_died(unit_id: int, is_enemy: bool)
signal unit_hp_changed(unit_id: int, is_enemy: bool, new_hp: int, max_hp: int)
signal turn_changed(side: String, turn_number: int)
signal combat_ended(outcome: String, result: Dictionary)

# ── Audio / FX requests (consumed by AudioManager / EffectsLayer) ─────────────
signal audio_event(event_name: String)
signal fx_at(fx_type: String, world_pos: Vector2)
