"""Python authority for the isolated Godot tactical preview."""
from game.combat.engine import CombatEngine
from game.combat.movement import CELL_SIZE
from game.combat_actions import available_combat_actions


class TacticalPreview:
    """Translate presentation requests into existing combat engine operations."""

    def __init__(self, engine: CombatEngine) -> None:
        self.engine = engine
        state = engine.state
        self.units = {
            f"{side}:{index}": unit
            for side, team in (("ally", state.allied_units), ("enemy", state.enemy_units))
            for index, unit in enumerate(team)
        }
        self.unit_ids = {id(unit): key for key, unit in self.units.items()}

    def snapshot(self) -> dict:
        state = self.engine.state
        battle = self.engine.end_battle_check()
        return {
            "turn": state.turn,
            "round": state.turn_number,
            "outcome": battle.outcome,
            "units": [
                {
                    "id": key,
                    "name": unit.character.name if unit.character else "Raider",
                    "cell": [coordinate // CELL_SIZE for coordinate in unit.position],
                    "hp": unit.health,
                    "max_hp": unit.stats.max_hp if unit.stats else unit.health,
                    "ap": unit.action_points,
                    "defending": unit.is_defending,
                    "overwatch": unit.on_overwatch,
                    "actions": [action.key for action in available_combat_actions(unit)]
                    if key.startswith("ally:") and state.turn == "player" and unit.health > 0
                    else [],
                }
                for key, unit in self.units.items()
            ],
        }

    def action(self, key: str, actor_id: str, *, target_id: str | None = None,
               destination: list[int] | None = None) -> dict:
        if key == "end_turn":
            if self.engine.state.turn != "player" or self.engine.end_battle_check().ended:
                return {"success": False, "message": "Turn unavailable.", "state": self.snapshot()}
            events = []

            def attack_event(source, victim, damage, *, kind="attack"):
                events.append({
                    "kind": kind,
                    "actor": self.unit_ids[id(source)],
                    "target": self.unit_ids[id(victim)],
                    "from_cell": [coordinate // CELL_SIZE for coordinate in source.position],
                    "to_cell": [coordinate // CELL_SIZE for coordinate in victim.position],
                    "damage": damage,
                })

            def overwatch_event(source, victim, damage):
                attack_event(source, victim, damage, kind="overwatch")

            if not self.engine.start_enemy_turn(on_attack=attack_event, on_overwatch_shot=overwatch_event).ended:
                self.engine.start_player_turn()
            return {"success": True, "message": "Enemy phase resolved.",
                    "events": events, "state": self.snapshot()}
        actor = self.units.get(actor_id)
        target = self.units.get(target_id) if target_id is not None else None
        if actor is None or (target_id is not None and target is None):
            return {"success": False, "message": "Unknown unit.", "state": self.snapshot()}
        if self.engine.end_battle_check().ended:
            return {"success": False, "message": "Battle ended.", "state": self.snapshot()}
        delta = None
        if destination is not None:
            if (not isinstance(destination, list) or len(destination) != 2
                    or any(type(value) is not int for value in destination)):
                return {"success": False, "message": "Invalid destination.", "state": self.snapshot()}
            delta = tuple(cell*CELL_SIZE - position//CELL_SIZE*CELL_SIZE
                          for cell, position in zip(destination, actor.position))
        result = self.engine.perform_action(key, actor=actor, target=target, move_delta=delta)
        reply = {"success": result.success, "message": result.message, "state": self.snapshot()}
        if result.success and result.attack_resolution is not None:
            reply["attack"] = {"hit": result.attack_resolution.hit, "damage": result.damage}
        return reply
