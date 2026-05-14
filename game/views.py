import arcade
import os

from .agent_aftermath import apply_mission_aftermath
from .agent_readiness import agents_at_breaking_risk, build_agent_readiness_lines
from .battle_outcomes import resolve_defeated_agent_outcome
from .character import Character, is_deployable
from .combat_system import (
    create_enemy_units,
    create_player_units,
    is_occupied as combat_is_occupied,
    run_enemy_ai as run_enemy_ai_system,
)
from .deployment import (
    sanitize_selected_agent_names,
    selected_deployable_agents,
    toggle_agent_selection,
)
from .dossier import build_agent_dossier_lines
from .ui import palette
from .ui.drawing import draw_line_group
from .ui.panels import draw_panel, draw_status_bar
from .ui.dashboard import (
    build_agent_aftermath_lines,
    build_command_status_line,
    build_district_status_lines,
    build_event_log_lines,
    build_faction_pressure_lines,
    build_recent_consequence_lines,
    build_resource_summary_line,
)
from .ui.mission_board import build_mission_board_lines, build_selected_mission_lines
from .gamestate import GameState
from .mission_objectives import create_battle_objective, interact_with_objective
from .mission_system import (
    ensure_mission_templates,
    launch_selected_mission as launch_mission_system,
    resolve_mission_outcome as resolve_mission_outcome_system,
    selected_mission as selected_mission_system,
)
from .mission_templates import MissionTemplate
from .recruitment import recruit_agent
from .ui import GameView
from .unit import Unit


class CorpView(GameView):
    CORP_UPGRADE_COSTS = {
        arcade.key.KEY_1: ("research", {"intel": 5}),
        arcade.key.KEY_2: ("security", {"credits": 10, "salvage": 2}),
        arcade.key.KEY_3: ("politics", {"influence": 3}),
        arcade.key.KEY_4: ("black_ops", {"credits": 5, "intel": 3}),
    }

    def setup(self):
        self.text = "Corporation Management"
        if self.game_state.budget_pool <= 0:
            self.game_state.budget_pool = self.game_state.compute_budget()

    def on_draw(self):
        self.clear()
        draw_status_bar(
            build_command_status_line(
                self.game_state.turn,
                self.game_state.base_name,
                self.game_state.strategic_resources,
                self.game_state.district,
            ),
            self.window.width,
            self.window.height,
        )

        y = self.window.height - 58
        draw_panel(14, y - 132, 360, 126, "Corp Allocation")
        arcade.draw_text(self.text.upper(), 28, y - 26, palette.HEADER, 18)
        arcade.draw_text(
            f"Auto Budget Pool: {self.game_state.budget_pool}",
            32,
            y - 52,
            palette.MUTED_TEXT,
            12,
        )
        arcade.draw_text(
            build_resource_summary_line(self.game_state.strategic_resources),
            32,
            y - 70,
            palette.RESOURCE,
            11,
        )
        budget_y = y - 94
        for k, v in self.game_state.corp_budget.items():
            arcade.draw_text(f"{k}: {v}", 34, budget_y, palette.TEXT, 12)
            budget_y -= 16

        right_x = 392
        draw_panel(
            right_x,
            y - 132,
            max(360, self.window.width - right_x - 18),
            126,
            "Upgrade Sinks",
        )
        upgrade_lines = [
            "1 Research: 5 intel",
            "2 Security: 10 credits + 2 salvage",
            "3 Politics: 3 influence",
            "4 Black Ops: 5 credits + 3 intel",
        ]
        line_y = y - 38
        for line in upgrade_lines:
            arcade.draw_text(line, right_x + 18, line_y, palette.ACCENT, 12)
            line_y -= 20

        y -= 158
        draw_panel(14, y - 104, self.window.width - 28, 104, "District Pulse")
        next_y = draw_line_group(
            "District Pulse",
            build_district_status_lines(self.game_state.district),
            30,
            y - 28,
            palette.TEXT,
        )
        draw_panel(14, next_y - 96, self.window.width - 28, 96, "Latest Fallout")
        draw_line_group(
            "Latest Fallout",
            build_recent_consequence_lines(self.game_state.recent_consequences),
            30,
            next_y - 28,
            palette.MUTED_TEXT,
        )

        arcade.draw_text(
            "1-4 spend resources, S save, L load", 20, 40, palette.ACCENT, 14
        )
        arcade.draw_text("Press C for City, R for RPG", 20, 20, palette.ACCENT, 14)

    def _buy_corp_upgrade(self, key: str, costs: dict[str, int]) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.corp_budget[key] += 10
            cost_text = ", ".join(
                f"-{amount} {resource}" for resource, amount in costs.items()
            )
            self.game_state.add_event(f"Corp upgrade authorized: {key} ({cost_text}).")
            return
        cost_text = ", ".join(
            f"{amount} {resource}" for resource, amount in costs.items()
        )
        self.game_state.add_event(f"Upgrade denied: {key} requires {cost_text}.")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.C:
            city_view = CityView(self.game_state)
            city_view.setup()
            self.window.show_view(city_view)
        elif key == arcade.key.R:
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key in self.CORP_UPGRADE_COSTS:
            budget_key, costs = self.CORP_UPGRADE_COSTS[key]
            self._buy_corp_upgrade(budget_key, costs)
        elif key == arcade.key.S:
            self.game_state.save("savegame.json")
        elif key == arcade.key.L:
            self.game_state = GameState.load("savegame.json")
        if self.game_state.budget_pool <= 0:
            self.game_state.advance_turn()


class CityView(GameView):
    CITY_UPGRADE_COSTS = {
        arcade.key.KEY_7: ("armaments", {"credits": 5, "salvage": 3}),
        arcade.key.KEY_8: ("garrisons", {"credits": 10, "influence": 2}),
        arcade.key.KEY_9: ("defense_zones", {"credits": 5, "salvage": 5}),
    }

    def setup(self):
        self.text = "City Management"

    def on_draw(self):
        self.clear()
        draw_status_bar(
            build_command_status_line(
                self.game_state.turn,
                self.game_state.base_name,
                self.game_state.strategic_resources,
                self.game_state.district,
            ),
            self.window.width,
            self.window.height,
        )

        y = self.window.height - 58
        draw_panel(14, y - 116, 360, 110, "City Grid")
        arcade.draw_text(self.text.upper(), 28, y - 26, palette.HEADER, 18)
        arcade.draw_text(
            build_resource_summary_line(self.game_state.strategic_resources),
            32,
            y - 52,
            palette.RESOURCE,
            11,
        )
        budget_y = y - 78
        for k, v in self.game_state.city_budget.items():
            arcade.draw_text(f"{k}: {v}", 34, budget_y, palette.TEXT, 12)
            budget_y -= 18

        right_x = 392
        draw_panel(
            right_x,
            y - 116,
            max(360, self.window.width - right_x - 18),
            110,
            "District Investments",
        )
        upgrade_lines = [
            "7 Armaments: 5 credits + 3 salvage",
            "8 Garrisons: 10 credits + 2 influence",
            "9 Defense Zones: 5 credits + 5 salvage",
        ]
        line_y = y - 38
        for line in upgrade_lines:
            arcade.draw_text(line, right_x + 18, line_y, palette.ACCENT, 12)
            line_y -= 22

        y -= 140
        draw_panel(14, y - 104, self.window.width - 28, 104, "District Pressure")
        y = draw_line_group(
            "District Pressure",
            build_district_status_lines(self.game_state.district),
            30,
            y - 28,
            palette.TEXT,
        )
        draw_panel(14, y - 104, self.window.width - 28, 104, "Faction Pressure")
        y = draw_line_group(
            "Faction Pressure",
            build_faction_pressure_lines(self.game_state.factions),
            30,
            y - 28,
            palette.MUTED_TEXT,
        )
        draw_panel(14, y - 116, self.window.width - 28, 116, "Operations Log")
        draw_line_group(
            "Operations Log",
            build_event_log_lines(self.game_state.event_log),
            30,
            y - 28,
            palette.MUTED_TEXT,
        )

        arcade.draw_text("7-9 spend resources", 20, 40, palette.ACCENT, 14)
        arcade.draw_text("Press R for RPG", 20, 20, palette.ACCENT, 14)

    def _buy_city_upgrade(self, key: str, costs: dict[str, int]) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.city_budget[key] += 10
            cost_text = ", ".join(
                f"-{amount} {resource}" for resource, amount in costs.items()
            )
            self.game_state.add_event(f"City investment routed: {key} ({cost_text}).")
            return
        cost_text = ", ".join(
            f"{amount} {resource}" for resource, amount in costs.items()
        )
        self.game_state.add_event(f"Investment denied: {key} requires {cost_text}.")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key in self.CITY_UPGRADE_COSTS:
            budget_key, costs = self.CITY_UPGRADE_COSTS[key]
            self._buy_city_upgrade(budget_key, costs)


class RPGView(GameView):
    def setup(self):
        self.text = "RPG Phase"
        self.recruiting = False
        self.selected_role = None
        self.allocating = None
        self.message = ""
        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self.deployment_cursor_index = 0
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        ensure_mission_templates(self.game_state)

    def selected_mission(self) -> MissionTemplate:
        return selected_mission_system(self.game_state)

    def has_deployable_agent(self) -> bool:
        return any(is_deployable(char) for char in self.game_state.characters)

    def selected_deployment(self) -> list[Character]:
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        return selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )

    def launch_selected_mission(self) -> None:
        if not self.has_deployable_agent():
            self.message = (
                "Recruit at least one deployable agent before launching an operation."
            )
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
            return

        selected_squad = self.selected_deployment()
        if not selected_squad:
            self.message = (
                "Select at least one deployable agent before launching an operation."
            )
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
            return

        selected_mission = self.selected_mission()
        agents_at_risk = agents_at_breaking_risk(selected_squad, selected_mission)
        confirmation_matches = (
            self.pending_breakdown_confirmation
            and self.pending_breakdown_mission_id == selected_mission.id
        )
        if agents_at_risk and not confirmation_matches:
            lead_agent = agents_at_risk[0]
            self.pending_breakdown_confirmation = True
            self.pending_breakdown_mission_id = selected_mission.id
            self.message = (
                f"{lead_agent.name} is at breakdown risk. "
                "Press B again to force deployment."
            )
            return

        if agents_at_risk:
            names = ", ".join(agent.name for agent in agents_at_risk)
            self.game_state.add_event(
                f"Command forced {names} into {selected_mission.title} "
                "despite breakdown risk."
            )

        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        mission = launch_mission_system(self.game_state)
        battle_view = BattleView(self.game_state)
        battle_view.setup(mission)
        self.window.show_view(battle_view)

    def on_draw(self):
        self.clear()
        arcade.draw_text(self.text, 20, self.window.height - 40, arcade.color.WHITE, 20)
        y = self.window.height - 80
        selected_names = set(self.game_state.selected_agent_names)
        for idx, char in enumerate(self.game_state.characters):
            info, dossier = build_agent_dossier_lines(char)
            if char.recovery_turns > 0:
                info = f"{info} | Recovery: {char.recovery_turns} turns"
            cursor = ">" if idx == self.deployment_cursor_index else " "
            selected = "[X]" if char.name in selected_names else "[ ]"
            availability = "" if is_deployable(char) else " | Unavailable"
            info = f"{cursor} {selected} {info}{availability}"
            arcade.draw_text(info, 20, y, arcade.color.WHITE, 14)
            arcade.draw_text(dossier, 40, y - 15, arcade.color.LIGHT_GRAY, 12)
            y -= 15
            if char.pending_points > 0:
                arcade.draw_text(
                    f"  Allocate {char.pending_points} pts: 1=PSI 2=STR 3=AGI 4=CON 5=CHA",
                    40,
                    y - 15,
                    arcade.color.AQUA,
                    12,
                )
                y -= 15
            y -= 20
        if self.recruiting:
            arcade.draw_text(
                "Select role: 1 Samurai, 2 Sniper, 3 Psi",
                20,
                y,
                arcade.color.YELLOW,
                14,
            )
            y -= 20
        else:
            mission_lines = build_mission_board_lines(
                self.game_state.mission_templates,
                self.game_state.selected_mission_index,
            )
            mission_board_height = 34 + len(mission_lines) * 16
            draw_panel(
                14,
                y - mission_board_height,
                self.window.width - 28,
                mission_board_height,
                "Mission Board",
            )
            y -= 28
            for line in mission_lines:
                arcade.draw_text(
                    line,
                    20,
                    y,
                    (
                        arcade.color.AQUA
                        if line.startswith(">")
                        else arcade.color.WHITE
                    ),
                    12,
                )
                y -= 16
            mission = self.selected_mission()
            y -= 8
            mission_detail_lines = build_selected_mission_lines(mission)
            detail_height = 34 + len(mission_detail_lines) * 15
            draw_panel(
                14,
                y - detail_height,
                self.window.width - 28,
                detail_height,
                "Selected Mission",
            )
            y -= 28
            for line in mission_detail_lines:
                arcade.draw_text(line, 30, y, arcade.color.LIGHT_GRAY, 11)
                y -= 15
            y -= 8
            y = draw_line_group(
                "Readiness Brief",
                build_agent_readiness_lines(self.game_state.characters, mission),
                20,
                y,
                arcade.color.LIGHT_GRAY,
            )
            draw_line_group(
                "Aftermath Report",
                build_agent_aftermath_lines(self.game_state.latest_agent_aftermath),
                20,
                y,
                arcade.color.LIGHT_GRAY,
            )
        if self.message:
            arcade.draw_text(self.message, 20, 42, arcade.color.YELLOW, 13)
        arcade.draw_text(
            "Press N recruit, 1-3 mission, A/D agent, Enter toggle, B launch",
            20,
            20,
            arcade.color.AQUA,
            14,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.B:
            self.launch_selected_mission()
        elif key in (arcade.key.A, arcade.key.D) and self.game_state.characters:
            step = -1 if key == arcade.key.A else 1
            self.deployment_cursor_index = (self.deployment_cursor_index + step) % len(
                self.game_state.characters
            )
            self.message = ""
        elif (
            key in (arcade.key.ENTER, arcade.key.RETURN) and self.game_state.characters
        ):
            (
                self.game_state.selected_agent_names,
                self.message,
            ) = toggle_agent_selection(
                self.game_state.characters,
                self.game_state.selected_agent_names,
                self.deployment_cursor_index,
            )
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
        elif key == arcade.key.N:
            if self.game_state.budget_pool >= 5:
                self.recruiting = True
                self.selected_role = None
                self.message = ""
                self.game_state.budget_pool -= 5
            else:
                pass
        elif self.recruiting:
            if key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
                role_map = {
                    arcade.key.KEY_1: "samurai",
                    arcade.key.KEY_2: "sniper",
                    arcade.key.KEY_3: "psi",
                }
                role = role_map.get(key, "samurai")
                recruit_agent(self.game_state.characters, role)
                self.deployment_cursor_index = len(self.game_state.characters) - 1
                self.recruiting = False
                self.message = ""
        elif key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3) and not any(
            char.pending_points > 0 for char in self.game_state.characters
        ):
            idx = key - arcade.key.KEY_1
            if idx < len(self.game_state.mission_templates):
                self.game_state.selected_mission_index = idx
                self.pending_breakdown_confirmation = False
                self.pending_breakdown_mission_id = None
        else:
            # Allocate stat points if any
            for char in self.game_state.characters:
                if char.pending_points > 0:
                    if key == arcade.key.KEY_1:
                        char.stats.psi += 1
                    elif key == arcade.key.KEY_2:
                        char.stats.str += 1
                    elif key == arcade.key.KEY_3:
                        char.stats.agi += 1
                    elif key == arcade.key.KEY_4:
                        char.stats.con += 1
                    elif key == arcade.key.KEY_5:
                        char.stats.cha += 1
                    else:
                        break
                    char.pending_points -= 1
                    char.stats.recalculate_hp()
                    break


class BattleView(GameView):
    def setup(self, mission: MissionTemplate | None = None):
        self.mission = mission or self.game_state.active_mission
        if self.mission is None and self.game_state.mission_templates:
            self.mission = MissionTemplate.from_dict(
                self.game_state.mission_templates[
                    self.game_state.selected_mission_index
                ].to_dict()
            )
            self.game_state.active_mission = self.mission
        self.available_maps = [
            f for f in os.listdir("assets/maps") if f.lower().endswith(".jpeg")
        ]
        self.map_index = None
        self.background = None
        self.camera = arcade.Camera2D()
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        selected_squad = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.player_units = create_player_units(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.defeated_player_units = []
        self.enemy_units, self.initial_enemy_count = create_enemy_units(
            self.mission, selected_squad
        )
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.battle_objective = create_battle_objective(self.mission)

        for unit in self.player_units:
            sprite = arcade.Sprite(
                "assets/player.png",
                center_x=unit.position[0],
                center_y=unit.position[1],
            )
            unit.sprite = sprite
            self.player_list.append(sprite)

        for enemy in self.enemy_units:
            sprite = arcade.Sprite(
                "assets/enemy.png",
                center_x=enemy.position[0],
                center_y=enemy.position[1],
            )
            enemy.sprite = sprite
            self.enemy_list.append(sprite)

        self.turn_number = 1
        self.turn = "player"
        self.active_index = 0
        self.message = self.mission.objective_text if self.mission else ""
        self.triggered_complication = None
        self.attack_timer = 0.0
        self.attack_line = None
        # Target selection state
        self.selecting_target = False
        self.target_candidates = []
        self.selected_target_idx = 0
        self.pending_attack = None
        self.start_player_turn()

    def is_occupied(self, x: int, y: int, *, exclude: Unit | None = None) -> bool:
        """Check if a map position is occupied by any living unit."""
        return combat_is_occupied(
            x, y, self.player_units, self.enemy_units, exclude=exclude
        )

    def start_player_turn(self):
        for unit in self.player_units:
            unit.reset_actions()
        if self.turn == "enemy":
            self.turn_number += 1
        self.turn = "player"
        self.active_index = 0

    def start_enemy_turn(self):
        for enemy in self.enemy_units:
            enemy.reset_actions()
        self.turn = "enemy"
        self.run_enemy_ai()
        if not self.player_units:
            self.end_battle(False)
            return
        elif not self.enemy_units:
            self.end_battle(True)
            return
        else:
            self.start_player_turn()

    def end_battle(self, victory: bool) -> None:
        """Finish the battle, apply mission fallout, and return to the RPG view."""
        remaining_enemies = len(getattr(self, "enemy_units", []))
        defeated = max(0, self.initial_enemy_count - remaining_enemies)
        if victory:
            defeated = self.initial_enemy_count
            self.game_state.x += 50 * defeated
        processed_character_ids = set()
        surviving_participants = []
        all_player_units = list(self.player_units) + list(self.defeated_player_units)
        for unit in all_player_units:
            if not unit.character or id(unit.character) in processed_character_ids:
                continue
            processed_character_ids.add(id(unit.character))
            if unit.health <= 0:
                self.resolve_defeated_player_unit(unit)
                continue
            unit.character.stats.hp = unit.health
            surviving_participants.append(unit.character)
            if victory:
                unit.character.gain_xp(50 * defeated)
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.game_state.award_mission_resources(self.mission, victory, defeated)
        self.resolve_mission_outcome(victory)
        aftermath_lines = apply_mission_aftermath(
            surviving_participants,
            self.mission,
            victory,
            self.triggered_complication,
        )
        self.game_state.latest_agent_aftermath = aftermath_lines[-4:]
        for line in aftermath_lines:
            self.game_state.add_event(line)
        rpg_view = RPGView(self.game_state)
        rpg_view.setup()
        self.window.show_view(rpg_view)

    def resolve_defeated_player_unit(self, unit: Unit) -> None:
        """Resolve a downed agent's vertical-slice post-battle outcome."""
        character = unit.character
        if not character:
            return
        resolve_defeated_agent_outcome(
            character,
            remove_character=self.remove_character_from_roster,
            record_event=self.game_state.add_event,
        )

    def remove_character_from_roster(self, character: Character) -> None:
        """Remove a character only when a battle outcome confirms death."""
        if character in self.game_state.characters:
            self.game_state.characters.remove(character)

    def resolve_mission_outcome(self, victory: bool) -> None:
        self.triggered_complication = resolve_mission_outcome_system(
            self.game_state, self.mission, victory, self.triggered_complication
        )

    def run_enemy_ai(self):
        def on_attack(enemy: Unit, target: Unit, damage: int) -> None:
            target_name = target.character.name if target.character else "agent"
            self.message = f"Enemy hits {target_name} for {damage}"
            self.start_attack_animation(enemy, target)

        def on_defeated(target: Unit) -> None:
            if target.sprite:
                target.sprite.kill()
            if self.active_index > 0:
                self.active_index = min(self.active_index - 1, len(self.player_units))

        run_enemy_ai_system(
            self.player_units,
            self.enemy_units,
            defeated_player_units=self.defeated_player_units,
            on_attack=on_attack,
            on_defeated=on_defeated,
        )

    def on_draw(self):
        self.clear()
        self.camera.use()
        if self.map_index is None:
            y = self.window.height - 40
            arcade.draw_text("Select battle map:", 20, y, arcade.color.WHITE, 20)
            y -= 40
            if not self.available_maps:
                arcade.draw_text(
                    "No maps found in assets/maps",
                    20,
                    y,
                    arcade.color.RED,
                    14,
                )
            else:
                for idx, name in enumerate(self.available_maps, start=1):
                    arcade.draw_text(f"{idx} - {name}", 20, y, arcade.color.AQUA, 14)
                    y -= 20
            return
        if self.background:
            # Build a rectangle: left, bottom, width, height
            full_rect = arcade.LBWH(0, 0, self.window.width, self.window.height)
            # Draw the texture into that rect
            arcade.draw_texture_rect(
                self.background,  # Texture
                full_rect,  # LBWH rect
                # └─── only two positional args! ───┘
                # You can also pass angle=..., alpha=... as keywords if desired
            )
        self.enemy_list.draw()
        self.player_list.draw()

        if self.battle_objective:
            ox, oy = self.battle_objective.position
            marker_color = (
                arcade.color.GREEN
                if self.battle_objective.completed
                else arcade.color.YELLOW
            )
            arcade.draw_lrbt_rectangle_filled(
                ox - 14,
                ox + 14,
                oy - 14,
                oy + 14,
                marker_color,
            )
            arcade.draw_rect_outline(
                arcade.LBWH(ox - 18, oy - 18, 36, 36),
                arcade.color.AQUA,
                border_width=2,
            )
            arcade.draw_text(
                self.battle_objective.label,
                ox - 28,
                oy + 24,
                arcade.color.WHITE,
                12,
            )

        # Draw enemy HP bars
        for enemy in self.enemy_units:
            if enemy.sprite and enemy.stats:
                bar_width = enemy.sprite.width
                left = enemy.sprite.center_x - bar_width / 2
                right = enemy.sprite.center_x + bar_width / 2
                top = enemy.sprite.center_y + enemy.sprite.height / 2 + 6
                bottom = top - 4
                arcade.draw_lrbt_rectangle_filled(
                    left,
                    right,
                    bottom,
                    top,
                    arcade.color.DARK_RED,
                )
                current = bar_width * enemy.health / enemy.stats.max_hp
                arcade.draw_lrbt_rectangle_filled(
                    left,
                    left + current,
                    bottom,
                    top,
                    arcade.color.GREEN,
                )
        if self.selecting_target and self.target_candidates:
            target = self.target_candidates[self.selected_target_idx]
            if target.sprite:
                cx = target.sprite.center_x
                cy = target.sprite.center_y
                width = target.sprite.width + 10
                height = target.sprite.height + 10
                full_rect = arcade.LBWH(cx - width / 2, cy - height / 2, width, height)
                arcade.draw_rect_outline(
                    full_rect,
                    arcade.color.YELLOW,
                    border_width=2,
                )
                # Display hit chance above target
                player = self.player_units[self.active_index]
                stat_name = {
                    "melee": "str",
                    "shoot": "agi",
                    "psi": "psi",
                }.get(self.pending_attack or "melee", "str")
                atk_val = getattr(player.stats, stat_name)
                defense = target.stats.defense if target.stats else 1
                chance = atk_val / (atk_val + defense) if atk_val > 0 else 0
                prob_text = f"{chance*100:.0f}%"
                arcade.draw_text(
                    prob_text,
                    cx - width / 2,
                    cy + height / 2 + 4,
                    arcade.color.YELLOW,
                    12,
                )
        if self.attack_line:
            x1, y1, x2, y2 = self.attack_line
            arcade.draw_line(x1, y1, x2, y2, arcade.color.YELLOW, 2)
        current_hp = (
            self.player_units[self.active_index].health if self.player_units else 0
        )
        status = f"Turn {self.turn_number} - {self.turn.capitalize()}  Player HP: {current_hp}"
        if self.mission:
            status = f"{self.mission.title} | {status}"
        arcade.draw_text(status, 20, self.window.height - 20, arcade.color.AQUA, 14)
        if self.mission:
            arcade.draw_text(
                self.mission.objective_text,
                20,
                self.window.height - 42,
                arcade.color.LIGHT_GRAY,
                12,
            )
        if self.battle_objective:
            arcade.draw_text(
                self.battle_objective.status_text,
                20,
                self.window.height - 62,
                arcade.color.AQUA,
                12,
            )
        if self.message:
            message_y = (
                self.window.height - 84
                if self.battle_objective
                else self.window.height - 62
            )
            arcade.draw_text(self.message, 20, message_y, arcade.color.YELLOW, 16)
        if self.turn == "ended":
            if not self.enemy_units:
                msg = "Victory!"
            else:
                msg = "Defeat..."
            arcade.draw_text(msg, 20, 40, arcade.color.YELLOW, 20)
        else:
            if self.selecting_target:
                arcade.draw_text(
                    "Select target with Left/Right, Enter to confirm, Esc to cancel",
                    20,
                    20,
                    arcade.color.AQUA,
                    14,
                )
            else:
                arcade.draw_text(
                    "Arrows move, E objective, Space melee, F shoot, P psi atk, V psi def, D defend, Esc exit",
                    20,
                    20,
                    arcade.color.AQUA,
                    14,
                )

    def on_key_press(self, key, modifiers):
        if self.map_index is None:
            if arcade.key.KEY_1 <= key <= arcade.key.KEY_9:
                idx = key - arcade.key.KEY_1
                if idx < len(self.available_maps):
                    self.map_index = idx
                    path = os.path.join("assets/maps", self.available_maps[idx])
                    self.background = arcade.load_texture(path)
            elif key == arcade.key.ESCAPE:
                corp_view = CorpView(self.game_state)
                corp_view.setup()
                self.window.show_view(corp_view)
            return

        if self.turn != "player" or not self.player_units:
            return

        player = self.player_units[self.active_index]

        # Handle target selection mode
        if self.selecting_target:
            if key in (arcade.key.LEFT, arcade.key.A):
                self.selected_target_idx = (self.selected_target_idx - 1) % len(
                    self.target_candidates
                )
            elif key in (arcade.key.RIGHT, arcade.key.D):
                self.selected_target_idx = (self.selected_target_idx + 1) % len(
                    self.target_candidates
                )
            elif key in (
                arcade.key.ENTER,
                arcade.key.RETURN,
                arcade.key.SPACE,
                arcade.key.F,
                arcade.key.P,
            ):
                target = self.target_candidates[self.selected_target_idx]
                if self.pending_attack == "melee":
                    damage = player.melee_attack(target)
                elif self.pending_attack == "shoot":
                    damage = player.shoot(target)
                else:
                    damage = player.psi_attack(target)
                if damage > 0:
                    atk_name = {
                        "melee": "slashes",
                        "shoot": "shoots",
                        "psi": "psy hits",
                    }[self.pending_attack]
                    self.message = f"{player.character.name} {atk_name} for {damage}"
                    self.start_attack_animation(player, target)
                    if target.health <= 0:
                        if target.sprite:
                            target.sprite.kill()
                        if target in self.enemy_units:
                            self.enemy_units.remove(target)
                        if not self.enemy_units:
                            self.end_battle(True)
                            self.selecting_target = False
                            self.target_candidates = []
                            self.pending_attack = None
                            return
                self.selecting_target = False
                self.target_candidates = []
                self.pending_attack = None
                self.check_active_player()
            elif key == arcade.key.ESCAPE:
                self.selecting_target = False
                self.target_candidates = []
                self.pending_attack = None
            return

        # Normal input handling when not selecting target
        if key == arcade.key.E:
            if not self.battle_objective:
                self.message = "No battlefield objective on this mission. Eliminate enemies to win."
            else:
                completed, message = interact_with_objective(
                    player.position, self.battle_objective
                )
                self.message = message
                if completed:
                    self.end_battle(True)
                    return
        elif key == arcade.key.UP:
            new_x, new_y = player.position[0], player.position[1] + 32
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(0, 32)
        elif key == arcade.key.DOWN:
            new_x, new_y = player.position[0], player.position[1] - 32
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(0, -32)
        elif key == arcade.key.LEFT:
            new_x, new_y = player.position[0] - 32, player.position[1]
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(-32, 0)
        elif key == arcade.key.RIGHT:
            new_x, new_y = player.position[0] + 32, player.position[1]
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(32, 0)
        elif key == arcade.key.SPACE:
            self.target_candidates = [
                e for e in self.enemy_units if player.distance_to(e) <= 32
            ]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "melee"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.F:
            self.target_candidates = [
                e for e in self.enemy_units if player.distance_to(e) <= 10 * 32
            ]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "shoot"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.P:
            self.target_candidates = [
                e for e in self.enemy_units if player.distance_to(e) <= 10 * 32
            ]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "psi"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.D:
            player.defend()
        elif key == arcade.key.V:
            player.psi_defend()
        elif key == arcade.key.ESCAPE:
            corp_view = CorpView(self.game_state)
            corp_view.setup()
            self.window.show_view(corp_view)

        self.check_active_player()

    def check_active_player(self):
        while self.active_index < len(self.player_units) and (
            self.player_units[self.active_index].action_points <= 0
            or self.player_units[self.active_index].health <= 0
        ):
            self.active_index += 1
        if self.active_index >= len(self.player_units):
            self.start_enemy_turn()

    def start_attack_animation(self, attacker: Unit, target: Unit):
        self.attack_line = (
            attacker.position[0],
            attacker.position[1],
            target.position[0],
            target.position[1],
        )
        self.attack_timer = 0.3

    def on_update(self, delta_time: float):
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.attack_line = None
