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
from .ui import palette
from .ui.panels import (
    draw_action_strip,
    draw_command_screen_frame,
    draw_deck_panel,
    draw_megacity_backdrop,
    draw_panel,
    draw_status_bar,
    draw_tactical_meter,
)
from .ui.dashboard import (
    build_agent_aftermath_lines,
    build_command_status_line,
    build_district_status_lines,
    build_event_log_lines,
    build_faction_pressure_lines,
    build_recent_consequence_lines,
    build_resource_summary_line,
)
from .ui.command_center import (
    build_action_strip,
    build_command_center_layout,
    build_command_title,
    panel_by_key,
)
from .ui.mission_board import build_mission_board_lines, build_selected_mission_lines
from .ui.command_deck import (
    build_agent_card_lines,
    build_command_deck_layout,
    build_ops_table_header,
    deck_panel_by_key,
)
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
        draw_command_screen_frame(
            build_command_title(
                "corp", self.game_state.base_name, self.game_state.district.name
            ),
            self.window.width,
            self.window.height,
        )
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

        panels = build_command_center_layout(
            self.window.width, self.window.height, "corp"
        )
        for panel in panels:
            draw_panel(panel.left, panel.bottom, panel.width, panel.height, panel.title)

        primary = panel_by_key(panels, "primary")
        arcade.draw_text(
            "BOARD DIRECTIVE",
            primary.left + 18,
            primary.bottom + primary.height - 58,
            palette.HEADER,
            16,
        )
        arcade.draw_text(
            f"Auto Budget Pool: {self.game_state.budget_pool}",
            primary.left + 18,
            primary.bottom + primary.height - 86,
            palette.MUTED_TEXT,
            12,
        )
        arcade.draw_text(
            build_resource_summary_line(self.game_state.strategic_resources),
            primary.left + 18,
            primary.bottom + primary.height - 108,
            palette.RESOURCE,
            11,
        )
        budget_y = primary.bottom + primary.height - 140
        for k, v in self.game_state.corp_budget.items():
            arcade.draw_text(
                f"{k.upper()} ALLOCATION   {v}",
                primary.left + 22,
                budget_y,
                palette.TEXT,
                12,
            )
            budget_y -= 24

        top_right = panel_by_key(panels, "top_right")
        upgrade_lines = [
            "1 RESEARCH LAB      5 intel",
            "2 SECURITY GRID     10 credits + 2 salvage",
            "3 POLITICAL FLOOR   3 influence",
            "4 BLACK OPS CELL    5 credits + 3 intel",
        ]
        line_y = top_right.bottom + top_right.height - 58
        for line in upgrade_lines:
            arcade.draw_text(line, top_right.left + 18, line_y, palette.ACCENT, 12)
            line_y -= 28

        bottom_right = panel_by_key(panels, "bottom_right")
        meter_x = bottom_right.left + 18
        meter_y = bottom_right.bottom + bottom_right.height - 70
        draw_tactical_meter(
            meter_x, meter_y, 180, "stability", self.game_state.district.stability
        )
        draw_tactical_meter(
            meter_x, meter_y - 28, 180, "unrest", self.game_state.district.unrest
        )
        draw_tactical_meter(
            meter_x,
            meter_y - 56,
            180,
            "media heat",
            self.game_state.district.media_heat,
        )
        y = meter_y - 90
        for line in build_recent_consequence_lines(self.game_state.recent_consequences):
            arcade.draw_text(line, bottom_right.left + 18, y, palette.MUTED_TEXT, 11)
            y -= 20

        draw_action_strip(
            build_action_strip(["1-4 spend", "S save", "L load", "C city", "R squad"]),
            self.window.width,
        )

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
        draw_command_screen_frame(
            build_command_title(
                "city", self.game_state.base_name, self.game_state.district.name
            ),
            self.window.width,
            self.window.height,
        )
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

        panels = build_command_center_layout(
            self.window.width, self.window.height, "city"
        )
        for panel in panels:
            draw_panel(panel.left, panel.bottom, panel.width, panel.height, panel.title)

        primary = panel_by_key(panels, "primary")
        arcade.draw_text(
            "CITY BUDGET ROUTER",
            primary.left + 18,
            primary.bottom + primary.height - 58,
            palette.HEADER,
            16,
        )
        arcade.draw_text(
            build_resource_summary_line(self.game_state.strategic_resources),
            primary.left + 18,
            primary.bottom + primary.height - 86,
            palette.RESOURCE,
            11,
        )
        budget_y = primary.bottom + primary.height - 122
        for k, v in self.game_state.city_budget.items():
            arcade.draw_text(
                f"{k.upper()} NETWORK   {v}",
                primary.left + 22,
                budget_y,
                palette.TEXT,
                12,
            )
            budget_y -= 26
        y = budget_y - 18
        for line in [
            "7 ARMAMENTS      5 credits + 3 salvage",
            "8 GARRISONS      10 credits + 2 influence",
            "9 DEFENSE ZONES  5 credits + 5 salvage",
        ]:
            arcade.draw_text(line, primary.left + 22, y, palette.ACCENT, 12)
            y -= 24

        top_right = panel_by_key(panels, "top_right")
        meter_x = top_right.left + 18
        meter_y = top_right.bottom + top_right.height - 66
        draw_tactical_meter(
            meter_x, meter_y, 220, "stability", self.game_state.district.stability
        )
        draw_tactical_meter(
            meter_x, meter_y - 30, 220, "unrest", self.game_state.district.unrest
        )
        draw_tactical_meter(
            meter_x,
            meter_y - 60,
            220,
            "media heat",
            self.game_state.district.media_heat,
        )
        y = meter_y - 96
        for line in build_district_status_lines(self.game_state.district):
            arcade.draw_text(line, top_right.left + 18, y, palette.TEXT, 11)
            y -= 20

        bottom_right = panel_by_key(panels, "bottom_right")
        y = bottom_right.bottom + bottom_right.height - 58
        for line in build_faction_pressure_lines(self.game_state.factions, limit=2):
            arcade.draw_text(line, bottom_right.left + 18, y, palette.MUTED_TEXT, 10)
            y -= 22
        y -= 12
        for line in build_event_log_lines(self.game_state.event_log, limit=4):
            arcade.draw_text(line, bottom_right.left + 18, y, palette.TEXT, 10)
            y -= 18

        draw_action_strip(
            build_action_strip(["7-9 invest", "R squad deck"]),
            self.window.width,
        )

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
        draw_command_screen_frame(
            "SQUAD COMMAND DECK // CITY INSERTION TABLE",
            self.window.width,
            self.window.height,
        )
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

        panels = build_command_deck_layout(self.window.width, self.window.height)
        for panel in panels:
            draw_deck_panel(panel)

        selected_names = set(self.game_state.selected_agent_names)
        squad_panel = deck_panel_by_key(panels, "squad")
        y = squad_panel.bottom + squad_panel.height - 46
        for line in build_agent_card_lines(
            self.game_state.characters, selected_names, self.deployment_cursor_index
        ):
            color = palette.ACCENT if line.startswith("▶") else palette.TEXT
            if "MEDBAY" in line:
                color = palette.WARNING
            if line.startswith("STAT UPGRADE"):
                color = palette.RESOURCE
            arcade.draw_text(line, squad_panel.left + 14, y, color, 11)
            y -= 16
            if y < squad_panel.bottom + 18:
                arcade.draw_text(
                    "... roster continues",
                    squad_panel.left + 14,
                    y,
                    palette.MUTED_TEXT,
                    10,
                )
                break

        mission = self.selected_mission()
        mission_panel = deck_panel_by_key(panels, "mission")
        arcade.draw_text(
            build_ops_table_header(mission, self.game_state.district.name),
            mission_panel.left + 14,
            mission_panel.bottom + mission_panel.height - 48,
            palette.RESOURCE,
            12,
        )

        if self.recruiting:
            arcade.draw_text(
                "RECRUIT SIGNAL: 1 Samurai, 2 Sniper, 3 Psi",
                mission_panel.left + 14,
                mission_panel.bottom + mission_panel.height - 76,
                palette.WARNING,
                13,
            )
        else:
            mission_lines = build_mission_board_lines(
                self.game_state.mission_templates,
                self.game_state.selected_mission_index,
            )
            y = mission_panel.bottom + mission_panel.height - 76
            for line in mission_lines:
                selected = line.startswith(">")
                if selected:
                    arcade.draw_lrbt_rectangle_filled(
                        mission_panel.left + 10,
                        mission_panel.left + mission_panel.width - 10,
                        y - 4,
                        y + 15,
                        palette.SELECTED_FILL,
                    )
                arcade.draw_text(
                    line.replace(">", "▶", 1),
                    mission_panel.left + 16,
                    y,
                    palette.ACCENT if selected else palette.TEXT,
                    11,
                )
                y -= 20

            detail_panel = deck_panel_by_key(panels, "details")
            y = detail_panel.bottom + detail_panel.height - 46
            for line in build_selected_mission_lines(mission):
                arcade.draw_text(
                    line, detail_panel.left + 14, y, palette.MUTED_TEXT, 10
                )
                y -= 15

            briefs_panel = deck_panel_by_key(panels, "briefs")
            y = briefs_panel.bottom + briefs_panel.height - 46
            arcade.draw_text(
                "READINESS BRIEF", briefs_panel.left + 14, y, palette.HEADER, 12
            )
            y -= 20
            for line in build_agent_readiness_lines(
                self.game_state.characters, mission
            ):
                arcade.draw_text(line, briefs_panel.left + 14, y, palette.TEXT, 10)
                y -= 16
            y -= 12
            arcade.draw_text(
                "AFTERMATH REPORT", briefs_panel.left + 14, y, palette.HEADER, 12
            )
            y -= 20
            for line in build_agent_aftermath_lines(
                self.game_state.latest_agent_aftermath
            ):
                arcade.draw_text(
                    line, briefs_panel.left + 14, y, palette.MUTED_TEXT, 10
                )
                y -= 16

        if self.message:
            arcade.draw_text(self.message, 20, 42, palette.WARNING, 13)
        draw_action_strip(
            build_action_strip(
                ["N recruit", "1-3 select op", "A/D agent", "Enter toggle", "B launch"]
            ),
            self.window.width,
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
            draw_command_screen_frame(
                "TACTICAL INSERTION // SELECT CITY COMBAT ZONE",
                self.window.width,
                self.window.height,
            )
            draw_panel(
                18,
                80,
                min(620, self.window.width - 36),
                self.window.height - 160,
                "Drop Zone Uplink",
            )
            y = self.window.height - 130
            arcade.draw_text("SELECT BATTLE MAP", 42, y, palette.HEADER, 20)
            y -= 40
            if not self.available_maps:
                arcade.draw_text(
                    "No maps found in assets/maps",
                    42,
                    y,
                    palette.DANGER,
                    14,
                )
            else:
                for idx, name in enumerate(self.available_maps, start=1):
                    arcade.draw_text(f"{idx}  ▸  {name}", 42, y, palette.ACCENT, 14)
                    y -= 24
            draw_action_strip(
                build_action_strip(["1-9 choose drop zone", "Esc return"]),
                self.window.width,
            )
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
                palette.TACTICAL_GREEN
                if self.battle_objective.completed
                else palette.WARNING
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
                palette.ACCENT,
                border_width=2,
            )
            arcade.draw_text(
                self.battle_objective.label,
                ox - 28,
                oy + 24,
                palette.TEXT,
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
                    palette.DANGER,
                )
                current = bar_width * enemy.health / enemy.stats.max_hp
                arcade.draw_lrbt_rectangle_filled(
                    left,
                    left + current,
                    bottom,
                    top,
                    palette.TACTICAL_GREEN,
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
                    palette.WARNING,
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
                    palette.WARNING,
                    12,
                )
        if self.attack_line:
            x1, y1, x2, y2 = self.attack_line
            arcade.draw_line(x1, y1, x2, y2, palette.WARNING, 2)
        current_hp = (
            self.player_units[self.active_index].health if self.player_units else 0
        )
        status = (
            f"TURN {self.turn_number} // {self.turn.upper()} // ACTIVE HP {current_hp}"
        )
        if self.mission:
            status = f"{self.mission.title.upper()} // {status}"
        draw_panel(
            14,
            self.window.height - 112,
            self.window.width - 28,
            98,
            "Tactical Combat HUD",
        )
        arcade.draw_text(status, 32, self.window.height - 48, palette.ACCENT, 14)
        if self.mission:
            arcade.draw_text(
                self.mission.objective_text,
                32,
                self.window.height - 70,
                palette.MUTED_TEXT,
                12,
            )
        if self.battle_objective:
            arcade.draw_text(
                self.battle_objective.status_text,
                32,
                self.window.height - 90,
                palette.RESOURCE,
                12,
            )
        if self.message:
            arcade.draw_text(
                self.message, 32, self.window.height - 132, palette.WARNING, 16
            )
        if self.turn == "ended":
            if not self.enemy_units:
                msg = "Victory!"
            else:
                msg = "Defeat..."
            arcade.draw_text(msg, 20, 40, palette.WARNING, 20)
        else:
            if self.selecting_target:
                draw_action_strip(
                    build_action_strip(
                        ["Left/Right target", "Enter confirm", "Esc cancel"]
                    ),
                    self.window.width,
                )
            else:
                draw_action_strip(
                    build_action_strip(
                        [
                            "Arrows move",
                            "E objective",
                            "Space melee",
                            "F shoot",
                            "P psi",
                            "V/D defend",
                            "Esc exit",
                        ]
                    ),
                    self.window.width,
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
