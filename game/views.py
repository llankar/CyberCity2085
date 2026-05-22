import arcade
import os

from .agent_aftermath import apply_mission_aftermath
from .agent_readiness import agents_at_breaking_risk, build_agent_readiness_lines
from .battle_outcomes import resolve_defeated_agent_outcome
from .narrative.debrief import build_mission_debrief_report
from .character import Character, is_deployable
from .management.equipment import EQUIPMENT_SLOTS, default_equipment_catalog
from .combat_actions import available_combat_actions
from .combat_system import (
    create_enemy_units,
    create_player_units,
    is_occupied as combat_is_occupied,
    run_enemy_ai as run_enemy_ai_system,
)
from .deployment import (
    sanitize_selected_agent_names,
    sanitize_selected_asset_ids,
    selected_deployable_agents,
    toggle_agent_selection,
    toggle_asset_selection,
)
from .ui import palette
from .ui.combat_action_bar import (
    combat_action_at_point,
    draw_combat_action_bar,
    layout_combat_action_buttons,
)
from .ui.panels import draw_graphical_command_surface
from .ui.room_interaction import (
    RoomAction,
    RoomUIState,
    action_at_point,
    actions_for_room,
    active_room_rect,
    close_button_rect,
    close_room,
    layout_action_buttons,
    open_room,
    room_at_point,
    roster_card_at_point,
    step_room_ui,
)
from .ui.portraits import portrait_path_for_character
from .gamestate import GameState
from .mission_objectives import create_battle_objective, interact_with_objective
from .mission_system import (
    ensure_mission_templates,
    launch_selected_mission as launch_mission_system,
    resolve_mission_outcome as resolve_mission_outcome_system,
    selected_mission as selected_mission_system,
)
from .mission_templates import MissionTemplate
from .persistence import SaveSystem
from .recruitment import recruit_agent
from .ui import GameView
from .ui.command_deck import build_corporate_finance_lines, build_event_panel_lines
from .ui.research_lab import build_research_lab_lines
from .ui.widgets.squad_morale_panel import build_squad_morale_panel_lines
from .ui.widgets.notification_center import NotificationCenter
from .ui.action_feedback import confirm_message, push_action
from .ui.management.action_requirements import (
    blocked_launch_reason,
    blocked_recruit_reason,
)
from .ui.navigation import (
    HelpOverlayState,
    build_help_lines,
    build_hint_banner,
    build_view_focus_model,
)
from .management.morale import aggregate_squad_morale
from .ui.onboarding.tutorial_overlay import overlay_state_for_screen
from .unit import Unit


def build_roster_cards(
    characters: list[Character],
    selected_names: list[str],
    cursor_index: int = 0,
    assets: list | None = None,
    selected_asset_ids: list[str] | None = None,
) -> list[dict]:
    """Build graphical agent-first roster cards plus compact asset support cards."""
    selected = set(selected_names)
    cards = []
    for index, character in enumerate(characters):
        stats = character.stats
        max_hp = max(1, stats.max_hp)
        cards.append(
            {
                "name": character.name,
                "role": character.role,
                "active": index == cursor_index,
                "selected": character.name in selected,
                "portrait_path": portrait_path_for_character(character),
                "hp_ratio": max(0, min(stats.hp / max_hp, 1)),
                "stress_ratio": max(0, min(character.stress / 100, 1)),
                "pending_points": character.pending_points,
                "recovery_turns": character.recovery_turns,
                "level": stats.level,
                "primary_weapon": (
                    character.loadout.primary_weapon.name
                    if character.loadout.primary_weapon
                    else "Unarmed"
                ),
                "armor": (
                    character.loadout.armor.name
                    if character.loadout.armor
                    else "No armor"
                ),
            }
        )
    selected_assets = set(selected_asset_ids or [])
    for asset in assets or []:
        integrity = max(0, min(asset.maintenance.integrity / 100, 1))
        cards.append(
            {
                "name": asset.name,
                "role": asset.display_role,
                "active": False,
                "selected": asset.id in selected_assets,
                "portrait_path": None,
                "hp_ratio": integrity,
                "stress_ratio": 0,
                "pending_points": 0,
                "recovery_turns": 0 if asset.is_deployable else 1,
                "level": 1,
                "primary_weapon": asset.hardpoints[0].name if asset.hardpoints else "Unarmed rig",
                "armor": f"Armor {asset.armor.defense_bonus} | Missiles {asset.missile_capacity}",
                "is_asset": True,
            }
        )
    return cards




def _help_lines_for_view(game_state: GameState, screen: str) -> list[str]:
    overlay = overlay_state_for_screen(game_state.tutorial_progress, screen)
    help_panel = overlay.get("help", {})
    objective = help_panel.get("objective", "No active objective.")
    controls = ", ".join(help_panel.get("controls", []))
    nxt = help_panel.get("next", "")
    return [f"Objective: {objective}", f"Controls: {controls}", f"Next: {nxt}"]


class CorpView(GameView):
    CORP_UPGRADE_COSTS = {
        arcade.key.KEY_1: ("research", {"intel": 5}),
        arcade.key.KEY_2: ("security", {"credits": 10, "salvage": 2}),
        arcade.key.KEY_3: ("politics", {"influence": 3}),
        arcade.key.KEY_4: ("black_ops", {"credits": 5, "intel": 3}),
    }
    CORP_UPGRADE_ACTIONS = {
        "research": {"intel": 5},
        "security": {"credits": 10, "salvage": 2},
        "politics": {"influence": 3},
        "black_ops": {"credits": 5, "intel": 3},
    }

    def setup(self):
        self.text = "Corporation Management"
        self.room_ui = RoomUIState("corp")
        self.notifications = NotificationCenter()
        self.focus_model = build_view_focus_model("corp", 1280, 720)
        self.help_overlay = HelpOverlayState()
        if self.game_state.available_funds <= 0:
            self.game_state.add_funds(
                self.game_state.compute_budget(),
                "corp_setup",
                "Emergency command-floor operating funds.",
            )

    def on_draw(self):
        self.clear()
        draw_graphical_command_surface(
            self.window.width,
            self.window.height,
            self.room_ui,
            self.game_state.strategic_resources,
            self._room_info_lines(),
            roster_cards=build_roster_cards(
                self.game_state.characters,
                self.game_state.selected_agent_names,
                assets=self.game_state.spec_ops_assets,
                selected_asset_ids=self.game_state.selected_asset_ids,
            ),
            available_funds=self.game_state.available_funds,
        )

    def _buy_corp_upgrade(self, key: str, costs: dict[str, int]) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.corp_budget[key] += 10
            cost_text = ", ".join(
                f"-{amount} {resource}" for resource, amount in costs.items()
            )
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", True, f"{key} ({cost_text})"))
            return
        cost_text = ", ".join(
            f"{amount} {resource}" for resource, amount in costs.items()
        )
        self.game_state.add_event(push_action(self.notifications, "budget_allocation", False, f"{key} requires {cost_text}"))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.H:
            self.help_overlay.toggle()
            return
        if key == arcade.key.M:
            self.game_state.ui_audio_feedback_enabled = (
                not self.game_state.ui_audio_feedback_enabled
            )
            status = (
                "enabled"
                if self.game_state.ui_audio_feedback_enabled
                else "disabled"
            )
            self.game_state.add_event(f"UI audio feedback {status}.")
            return
        if key == arcade.key.ESCAPE and self.room_ui.is_open:
            close_room(self.room_ui)
            return
        if key in (arcade.key.TAB,):
            step = -1 if modifiers & arcade.key.MOD_SHIFT else 1
            self._activate_focus(step)
            return
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            self._trigger_focus()
            return
        if key == arcade.key.C:
            city_view = CityView(self.game_state)
            city_view.setup()
            self.window.show_view(city_view)
        elif key == arcade.key.R:
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key == arcade.key.D:
            self.game_state.advance_one_day("manual command")
        elif key in self.CORP_UPGRADE_COSTS:
            budget_key, costs = self.CORP_UPGRADE_COSTS[key]
            self._buy_corp_upgrade(budget_key, costs)
        elif key == arcade.key.S:
            result = SaveSystem.save_game(self.game_state)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = SaveSystem.load_game()
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
        if self.game_state.available_funds <= 0:
            self.game_state.advance_turn()

    def on_mouse_press(self, x, y, button, modifiers):
        if self._handle_room_click(x, y):
            return

    def on_update(self, delta_time: float):
        step_room_ui(self.room_ui, delta_time)

    def _handle_room_click(self, x: int, y: int) -> bool:
        if self.room_ui.is_open:
            if close_button_rect(self.window.width, self.window.height).contains(x, y):
                close_room(self.room_ui)
                return True
            action = action_at_point(self.room_ui.action_buttons, x, y)
            if action is not None:
                self._perform_room_action(action.key)
                return True
            return True

        room = room_at_point(self.window.width, self.window.height, "corp", x, y)
        if room is None:
            return False
        open_room(self.room_ui, self.window.width, self.window.height, room.key)
        self.game_state.mark_tutorial_event("entered_room")
        self._sync_focus_actions()
        return True

    def _activate_focus(self, step: int) -> None:
        active = self.focus_model.move(step)
        if active and active.kind == "room":
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._sync_focus_actions()

    def _trigger_focus(self) -> None:
        active = self.focus_model.active()
        if active is None:
            return
        if active.kind == "room":
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._sync_focus_actions()
        elif active.kind == "action":
            self._perform_room_action(active.key)

    def _sync_focus_actions(self) -> None:
        self.focus_model.set_actions([button.action.key for button in self.room_ui.action_buttons])

    def _perform_room_action(self, action_key: str) -> None:
        if action_key == "city":
            city_view = CityView(self.game_state)
            city_view.setup()
            self.window.show_view(city_view)
            return
        if action_key == "advance_day":
            self.game_state.advance_one_day("manual command")
            return
        if action_key == "squad":
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
            return
        if action_key.startswith("start_research_"):
            index = int(action_key.rsplit("_", 1)[-1])
            completed = set(self.game_state.completed_research)
            active_ids = {
                active.project_id for active in self.game_state.active_research
            }
            available = self.game_state.research_tree.available_projects(
                completed, active_ids
            )
            if index < len(available):
                self.game_state.start_research(available[index].id)
            else:
                self.game_state.add_event(
                    "Research denied: no project in that lab slot."
                )
            return
        if action_key.startswith("recruit_"):
            role = action_key.removeprefix("recruit_")
            if self.game_state.spend_funds(
                5, "recruitment", f"Recruited {role} from Black Ops."
            ):
                agent = recruit_agent(self.game_state.characters, role)
                self.game_state.add_event(push_action(self.notifications, "recruitment", True, f"{agent.name} as {role}"))
            else:
                self.game_state.add_event(push_action(self.notifications, "recruitment", False, "budget pool below 5"))
            return
        if action_key.startswith("event_"):
            self._respond_to_first_event(action_key)
            return
        costs = self.CORP_UPGRADE_ACTIONS.get(action_key)
        if costs:
            self._buy_corp_upgrade(action_key, costs)

    def _respond_to_first_event(self, action_key: str) -> None:
        if not self.game_state.active_events:
            return
        choice_index = int(action_key.rsplit("_", 1)[-1])
        event = self.game_state.active_events[0]
        if 0 <= choice_index < len(event.choices):
            self.game_state.respond_to_event(event.id, event.choices[choice_index].key)

    def _room_info_lines(self) -> dict[str, list[str]]:
        resources = self.game_state.strategic_resources
        finance_lines = build_corporate_finance_lines(
            self.game_state.next_weekly_income_date,
            self.game_state.projected_weekly_income,
        )
        info = {
            "executive": [
                f"{self.game_state.calendar.campaign_date_label} | Day {self.game_state.calendar.current_day}",
                *build_event_panel_lines(
                    self.game_state.active_events, self.game_state.calendar.current_day
                )[:3],
                f"Turn {self.game_state.turn} | Funds {self.game_state.available_funds}",
                *finance_lines,
                f"Politics allocation {self.game_state.corp_budget['politics']}",
                f"Influence reserve {resources.get('influence', 0)}",
            ],
            "research": build_research_lab_lines(self.game_state),
            "security": [
                f"Security allocation {self.game_state.corp_budget['security']}",
                f"Credits {resources.get('credits', 0)} | Salvage {resources.get('salvage', 0)}",
                "Upgrade cost: 10 credits + 2 salvage",
            ],
            "black_ops": [
                f"Black ops allocation {self.game_state.corp_budget['black_ops']}",
                f"Credits {resources.get('credits', 0)} | Intel {resources.get('intel', 0)}",
                f"Roster {len(self.game_state.characters)} agents | Recruit cost 5 funds",
                "Fund cost: 5 credits + 3 intel",
            ],
            "media": [
                f"Media heat {self.game_state.district.media_heat}/100",
                f"District unrest {self.game_state.district.unrest}/100",
                "Public story control affects fallout pressure.",
            ],
            "logistics": [
                f"Credits {resources.get('credits', 0)} | Salvage {resources.get('salvage', 0)}",
                f"Daily income target {self.game_state.compute_budget()}",
                *finance_lines,
                "D / Advance day ticks income, events, recovery.",
            ],
            "server": [
                f"Intel reserve {resources.get('intel', 0)}",
                f"Tracked missions {len(self.game_state.mission_templates)}",
                "Data work supports research and operation discovery.",
            ],
            "hangar": [
                f"Base {self.game_state.base_name}",
                f"District {self.game_state.district.name}",
                "Transit links to city control and squad command.",
            ],
        }
        return self._with_contextual_hints(info)

    def _with_contextual_hints(self, info: dict[str, list[str]]) -> dict[str, list[str]]:
        for room_key, lines in info.items():
            hints = [build_hint_banner("corp", room_key)]
            if self.help_overlay.visible:
                hints.extend(
                    build_help_lines(
                        "corp",
                        room_key,
                        [button.action.label for button in self.room_ui.action_buttons],
                    )[:5]
                )
            info[room_key] = _help_lines_for_view(self.game_state, "corp") + hints + lines
        return info


class CityView(GameView):
    CITY_UPGRADE_COSTS = {
        arcade.key.KEY_7: ("armaments", {"credits": 5, "salvage": 3}),
        arcade.key.KEY_8: ("garrisons", {"credits": 10, "influence": 2}),
        arcade.key.KEY_9: ("defense_zones", {"credits": 5, "salvage": 5}),
    }
    CITY_UPGRADE_ACTIONS = {
        "armaments": {"credits": 5, "salvage": 3},
        "garrisons": {"credits": 10, "influence": 2},
        "defense_zones": {"credits": 5, "salvage": 5},
    }

    def setup(self):
        self.text = "City Management"
        self.room_ui = RoomUIState("city")
        self.notifications = NotificationCenter()
        self.focus_model = build_view_focus_model("city", 1280, 720)
        self.help_overlay = HelpOverlayState()

    def on_draw(self):
        self.clear()
        draw_graphical_command_surface(
            self.window.width,
            self.window.height,
            self.room_ui,
            self.game_state.strategic_resources,
            self._room_info_lines(),
            roster_cards=build_roster_cards(
                self.game_state.characters,
                self.game_state.selected_agent_names,
                assets=self.game_state.spec_ops_assets,
                selected_asset_ids=self.game_state.selected_asset_ids,
            ),
            available_funds=self.game_state.available_funds,
        )

    def _buy_city_upgrade(self, key: str, costs: dict[str, int]) -> None:
        if self.game_state.spend_resources(costs):
            self.game_state.city_budget[key] += 10
            cost_text = ", ".join(
                f"-{amount} {resource}" for resource, amount in costs.items()
            )
            self.game_state.add_event(push_action(self.notifications, "budget_allocation", True, f"{key} ({cost_text})"))
            return
        cost_text = ", ".join(
            f"{amount} {resource}" for resource, amount in costs.items()
        )
        self.game_state.add_event(push_action(self.notifications, "budget_allocation", False, f"{key} requires {cost_text}"))

    def on_key_press(self, key, modifiers):
        if key == arcade.key.H:
            self.help_overlay.toggle()
            return
        if key == arcade.key.M:
            self.game_state.ui_audio_feedback_enabled = (
                not self.game_state.ui_audio_feedback_enabled
            )
            status = (
                "enabled"
                if self.game_state.ui_audio_feedback_enabled
                else "disabled"
            )
            self.game_state.add_event(f"UI audio feedback {status}.")
            return
        if key == arcade.key.ESCAPE and self.room_ui.is_open:
            close_room(self.room_ui)
            return
        if key == arcade.key.R:
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key == arcade.key.D:
            self.game_state.advance_one_day("manual command")
        elif key in self.CITY_UPGRADE_COSTS:
            budget_key, costs = self.CITY_UPGRADE_COSTS[key]
            self._buy_city_upgrade(budget_key, costs)
        elif key == arcade.key.S:
            result = SaveSystem.save_game(self.game_state)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = SaveSystem.load_game()
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded

    def on_mouse_press(self, x, y, button, modifiers):
        if self._handle_room_click(x, y):
            return

    def on_update(self, delta_time: float):
        step_room_ui(self.room_ui, delta_time)

    def _handle_room_click(self, x: int, y: int) -> bool:
        if self.room_ui.is_open:
            if close_button_rect(self.window.width, self.window.height).contains(x, y):
                close_room(self.room_ui)
                return True
            action = action_at_point(self.room_ui.action_buttons, x, y)
            if action is not None:
                self._perform_room_action(action.key)
                return True
            return True

        room = room_at_point(self.window.width, self.window.height, "city", x, y)
        if room is None:
            return False
        open_room(self.room_ui, self.window.width, self.window.height, room.key)
        self.game_state.mark_tutorial_event("entered_room")
        return True

    def _perform_room_action(self, action_key: str) -> None:
        if action_key == "squad":
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
            return
        if action_key == "advance_day":
            self.game_state.advance_one_day("manual command")
            return
        if action_key.startswith("event_"):
            self._respond_to_first_event(action_key)
            return
        costs = self.CITY_UPGRADE_ACTIONS.get(action_key)
        if costs:
            self._buy_city_upgrade(action_key, costs)

    def _respond_to_first_event(self, action_key: str) -> None:
        if not self.game_state.active_events:
            return
        choice_index = int(action_key.rsplit("_", 1)[-1])
        event = self.game_state.active_events[0]
        if 0 <= choice_index < len(event.choices):
            self.game_state.respond_to_event(event.id, event.choices[choice_index].key)

    def _room_info_lines(self) -> dict[str, list[str]]:
        resources = self.game_state.strategic_resources
        district = self.game_state.district
        factions = sorted(
            self.game_state.factions,
            key=lambda faction: faction.hostility_to_player,
            reverse=True,
        )
        lead_faction = factions[0].name if factions else "no active faction"
        hostility = factions[0].hostility_to_player if factions else 0
        info = {
            "municipal": [
                f"{self.game_state.calendar.campaign_date_label} | Week {self.game_state.calendar.current_week}",
                f"District {district.name}",
                f"Control faction {district.control_faction}",
                f"Garrisons network {self.game_state.city_budget['garrisons']}",
            ],
            "district": [
                f"Stability {district.stability}/100",
                f"Unrest {district.unrest}/100",
                f"Media heat {district.media_heat}/100",
            ],
            "transit": [
                f"Armaments network {self.game_state.city_budget['armaments']}",
                f"Credits {resources.get('credits', 0)} | Salvage {resources.get('salvage', 0)}",
                "Transit upgrades improve response capacity.",
            ],
            "factions": [
                f"Highest pressure: {lead_faction}",
                f"Hostility {hostility}/100",
                f"Active factions {len(self.game_state.factions)}",
            ],
            "public": [
                f"Media heat {district.media_heat}/100",
                f"Influence reserve {resources.get('influence', 0)}",
                "Public pressure changes mission fallout.",
            ],
            "relief": [
                f"Armaments network {self.game_state.city_budget['armaments']}",
                f"Defense zones {self.game_state.city_budget['defense_zones']}",
                "Relief routing stabilizes the district after combat.",
            ],
            "records": [
                f"Recent events {len(self.game_state.event_log)}",
                *build_event_panel_lines(
                    self.game_state.active_events, self.game_state.calendar.current_day
                )[:4],
                "D / Advance day reviews pending fallout.",
                f"District tags {len(district.tags)}",
                "Records preserve consequences for later systems.",
            ],
            "skybridge": [
                f"Agents available {len(self.game_state.characters)}",
                f"Operations ready {len(self.game_state.mission_templates)}",
                "Skybridge connects city command to squad command.",
            ],
        }
        for room_key, lines in info.items():
            hints = [build_hint_banner("city", room_key)]
            if self.help_overlay.visible:
                hints.extend(
                    build_help_lines(
                        "city",
                        room_key,
                        [button.action.label for button in self.room_ui.action_buttons],
                    )[:5]
                )
            info[room_key] = _help_lines_for_view(self.game_state, "city") + hints + lines
        return info


class RPGView(GameView):
    def setup(self):
        self.text = "RPG Phase"
        self.room_ui = RoomUIState("squad")
        self.notifications = NotificationCenter()
        self.recruiting = False
        self.selected_role = None
        self.allocating = None
        self.message = ""
        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self.deployment_cursor_index = 0
        self.equipment_catalog = default_equipment_catalog()
        self.focus_model = build_view_focus_model("squad", 1280, 720)
        self.help_overlay = HelpOverlayState()
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        selected_agents = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.game_state.selected_asset_ids = sanitize_selected_asset_ids(
            self.game_state.spec_ops_assets, self.game_state.selected_asset_ids, selected_agents
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
        selected_agents = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.game_state.selected_asset_ids = sanitize_selected_asset_ids(
            self.game_state.spec_ops_assets, self.game_state.selected_asset_ids, selected_agents
        )
        return selected_agents

    def launch_selected_mission(self) -> None:
        selected_squad = self.selected_deployment()
        selected_mission = self.selected_mission()
        blocked = blocked_launch_reason(
            has_deployable_agent=self.has_deployable_agent(),
            selected_count=len(selected_squad),
            mission_unavailable=selected_mission.id in self.game_state.unavailable_mission_ids,
            mission_title=selected_mission.title,
        )
        if blocked is not None:
            self.message = blocked.to_ui_text()
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
            self.game_state.mark_tutorial_event("selected_agent")
            if len(self.game_state.selected_agent_names) >= 2:
                self.game_state.mark_tutorial_event("formed_squad")
            self.notifications.warning(self.message)
            self.game_state.add_event(self.message)
            return
        agents_at_risk = agents_at_breaking_risk(selected_squad, selected_mission)
        confirmation_matches = (
            self.pending_breakdown_confirmation
            and self.pending_breakdown_mission_id == selected_mission.id
        )
        if agents_at_risk and not confirmation_matches:
            lead_agent = agents_at_risk[0]
            self.pending_breakdown_confirmation = True
            self.pending_breakdown_mission_id = selected_mission.id
            self.message = confirm_message("mission_launch_risk") + f" Lead agent at risk: {lead_agent.name}."
            self.notifications.warning(self.message)
            return

        if agents_at_risk:
            names = ", ".join(agent.name for agent in agents_at_risk)
            self.game_state.add_event(push_action(self.notifications, "mission_launch", True, f"forced {names} into {selected_mission.title} despite breakdown risk"))

        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self.game_state.mark_tutorial_event("launched_mission")
        mission = launch_mission_system(self.game_state)
        battle_view = BattleView(self.game_state)
        battle_view.setup(mission)
        self.window.show_view(battle_view)

    def on_draw(self):
        self.clear()
        draw_graphical_command_surface(
            self.window.width,
            self.window.height,
            self.room_ui,
            self.game_state.strategic_resources,
            self._room_info_lines(),
            roster_cards=build_roster_cards(
                self.game_state.characters,
                self.game_state.selected_agent_names,
                self.deployment_cursor_index,
                self.game_state.spec_ops_assets,
                self.game_state.selected_asset_ids,
            ),
            available_funds=self.game_state.available_funds,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.H:
            self.help_overlay.toggle()
            return
        if key == arcade.key.M:
            self.game_state.ui_audio_feedback_enabled = (
                not self.game_state.ui_audio_feedback_enabled
            )
            status = (
                "enabled"
                if self.game_state.ui_audio_feedback_enabled
                else "disabled"
            )
            self.game_state.add_event(f"UI audio feedback {status}.")
            return
        if key in (arcade.key.TAB,):
            step = -1 if modifiers & arcade.key.MOD_SHIFT else 1
            self._activate_focus(step)
            return
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            self._trigger_focus()
            return
        if key == arcade.key.ESCAPE and self.room_ui.is_open:
            close_room(self.room_ui)
            return
        if key == arcade.key.B:
            self.launch_selected_mission()
        elif key == arcade.key.S:
            result = SaveSystem.save_game(self.game_state)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = SaveSystem.load_game()
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
                self.deployment_cursor_index = 0
                self._refresh_squad_room_actions()
        elif key in (arcade.key.A, arcade.key.D) and self.game_state.characters:
            step = -1 if key == arcade.key.A else 1
            self.deployment_cursor_index = (self.deployment_cursor_index + step) % len(
                self.game_state.characters
            )
            self.message = ""
        elif self.game_state.characters and key == arcade.key.SPACE:
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
        elif key == arcade.key.V:
            selected_agents = self.selected_deployment()
            (
                self.game_state.selected_asset_ids,
                self.message,
            ) = toggle_asset_selection(
                self.game_state.spec_ops_assets,
                self.game_state.selected_asset_ids,
                selected_agents,
            )
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
        elif key == arcade.key.N:
            if self.game_state.spend_funds(
                5, "recruitment", "Reserved funds for a new agent."
            ):
                self.recruiting = True
                self.selected_role = None
                self.message = ""
            else:
                blocked = blocked_recruit_reason(self.game_state.available_funds)
                if blocked:
                    self.message = blocked.to_ui_text()
                    self.notifications.warning(self.message)
                    self.game_state.add_event(self.message)
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

    def on_mouse_press(self, x, y, button, modifiers):
        if self._handle_room_click(x, y):
            return

    def on_update(self, delta_time: float):
        step_room_ui(self.room_ui, delta_time)

    def _handle_room_click(self, x: int, y: int) -> bool:
        if self.room_ui.is_open:
            if close_button_rect(self.window.width, self.window.height).contains(x, y):
                close_room(self.room_ui)
                return True
            card_index = self._roster_card_index_at(x, y)
            if card_index is not None:
                self._select_roster_card(card_index)
                return True
            action = action_at_point(self.room_ui.action_buttons, x, y)
            if action is not None:
                self._perform_room_action(action.key)
                return True
            return True

        room = room_at_point(self.window.width, self.window.height, "squad", x, y)
        if room is None:
            return False
        open_room(self.room_ui, self.window.width, self.window.height, room.key)
        if room.key == "ops":
            self.game_state.mark_tutorial_event("opened_mission_board")
        self._refresh_squad_room_actions()
        self._sync_focus_actions()
        return True

    def _roster_card_index_at(self, x: int, y: int) -> int | None:
        if self.room_ui.expansion < 0.48:
            return None
        active = active_room_rect(self.room_ui, self.window.width, self.window.height)
        if active is None:
            return None
        room, rect = active
        if room.key not in {
            "barracks",
            "medbay",
            "armory",
            "briefing",
            "dossier",
            "insertion",
        }:
            return None
        return roster_card_at_point(
            rect,
            self.room_ui.action_buttons,
            len(self.game_state.characters),
            x,
            y,
        )

    def _select_roster_card(self, card_index: int) -> None:
        if not 0 <= card_index < len(self.game_state.characters):
            return
        self.deployment_cursor_index = card_index
        self.message = ""
        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self._refresh_squad_room_actions()

    def _perform_room_action(self, action_key: str) -> None:
        if action_key.startswith("recruit_"):
            role = action_key.removeprefix("recruit_")
            if self.game_state.spend_funds(
                5, "recruitment", "Recruited from squad room."
            ):
                recruit_agent(self.game_state.characters, role)
                self.game_state.play_ui_audio_feedback("recruitment")
                self.deployment_cursor_index = len(self.game_state.characters) - 1
                self.message = ""
                self._refresh_squad_room_actions()
            return
        if action_key == "mission_prev" and self.game_state.mission_templates:
            self.game_state.selected_mission_index = (
                self.game_state.selected_mission_index - 1
            ) % len(self.game_state.mission_templates)
            self.game_state.play_ui_audio_feedback("selection")
            self.pending_breakdown_confirmation = False
            self._refresh_squad_room_actions()
            return
        if action_key == "mission_next" and self.game_state.mission_templates:
            self.game_state.selected_mission_index = (
                self.game_state.selected_mission_index + 1
            ) % len(self.game_state.mission_templates)
            self.game_state.play_ui_audio_feedback("selection")
            self.pending_breakdown_confirmation = False
            self._refresh_squad_room_actions()
            return
        if action_key == "agent_prev" and self.game_state.characters:
            self.deployment_cursor_index = (self.deployment_cursor_index - 1) % len(
                self.game_state.characters
            )
            self._refresh_squad_room_actions()
            return
        if action_key == "agent_next" and self.game_state.characters:
            self.deployment_cursor_index = (self.deployment_cursor_index + 1) % len(
                self.game_state.characters
            )
            self._refresh_squad_room_actions()
            return
        if action_key == "select_agent" and self.game_state.characters:
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
            self.game_state.mark_tutorial_event("selected_agent")
            if len(self.game_state.selected_agent_names) >= 2:
                self.game_state.mark_tutorial_event("formed_squad")
            self.game_state.play_ui_audio_feedback("toggle")
            self._refresh_squad_room_actions()
            return
        if action_key == "toggle_asset":
            selected_agents = self.selected_deployment()
            (
                self.game_state.selected_asset_ids,
                self.message,
            ) = toggle_asset_selection(
                self.game_state.spec_ops_assets,
                self.game_state.selected_asset_ids,
                selected_agents,
            )
            self.pending_breakdown_confirmation = False
            self.pending_breakdown_mission_id = None
            self.game_state.play_ui_audio_feedback("toggle")
            self._refresh_squad_room_actions()
            return
        if action_key.startswith("equip_"):
            self._equip_active_agent(action_key.removeprefix("equip_"))
            self._refresh_squad_room_actions()
            return
        if action_key.startswith("level_"):
            self._level_active_agent(action_key.removeprefix("level_"))
            self._refresh_squad_room_actions()
            return
        if action_key == "launch":
            self.launch_selected_mission()

    def _active_agent(self) -> Character | None:
        if not self.game_state.characters:
            return None
        self.deployment_cursor_index %= len(self.game_state.characters)
        return self.game_state.characters[self.deployment_cursor_index]

    def _refresh_squad_room_actions(self) -> None:
        room_key = self.room_ui.active_room_key
        if room_key is None:
            return
        actions = []
        if room_key in {"armory", "dossier"}:
            actions.extend(
                [
                    RoomAction("agent_prev", "left", "Prev agent"),
                    RoomAction("select_agent", "select", "Toggle squad"),
                    RoomAction("agent_next", "right", "Next agent"),
                ]
            )
            if room_key == "armory":
                actions.extend(
                    [
                        RoomAction("equip_primary_weapon", "armory", "Primary"),
                        RoomAction("equip_sidearm", "radar", "Sidearm"),
                        RoomAction("equip_armor", "shield", "Armor"),
                        RoomAction("equip_utility_item", "medical", "Utility"),
                        RoomAction("equip_psi_focus", "research", "Psi focus"),
                        RoomAction("equip_special_gear", "stealth", "Special"),
                    ]
                )
            active_agent = self._active_agent()
            if active_agent and active_agent.pending_points > 0:
                points = active_agent.pending_points
                actions.extend(
                    [
                        RoomAction("level_psi", "research", f"+PSI {points}"),
                        RoomAction("level_str", "armory", f"+STR {points}"),
                        RoomAction("level_agi", "radar", f"+AGI {points}"),
                        RoomAction("level_con", "shield", f"+CON {points}"),
                        RoomAction("level_cha", "influence", f"+CHA {points}"),
                    ]
                )
        elif room_key == "insertion":
            actions.extend(
                [
                    RoomAction("launch", "launch", "Launch mission"),
                    RoomAction("toggle_asset", "armory", "Toggle support"),
                ]
            )
        elif room_key == "ops":
            actions.extend(
                [
                    RoomAction("mission_prev", "left", "Prev mission"),
                    RoomAction("mission_next", "right", "Next mission"),
                    RoomAction("launch", "launch", "Launch mission"),
                ]
            )
        else:
            actions = actions_for_room("squad", room_key)
        self.room_ui.action_buttons = layout_action_buttons(
            self.window.width, self.window.height, actions
        )
        self._sync_focus_actions()

    def _activate_focus(self, step: int) -> None:
        self.focus_model.mission_count = len(self.game_state.mission_templates)
        active = self.focus_model.move(step)
        if active is None:
            return
        if active.kind == "room":
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._refresh_squad_room_actions()
        elif active.kind == "mission":
            self.game_state.selected_mission_index = int(active.key.rsplit("_", 1)[-1]) % max(1, len(self.game_state.mission_templates))
            self.pending_breakdown_confirmation = False

    def _trigger_focus(self) -> None:
        active = self.focus_model.active()
        if active is None:
            return
        if active.kind == "room":
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._refresh_squad_room_actions()
            return
        if active.kind == "action":
            self._perform_room_action(active.key)
            return
        if active.kind == "mission" and self.game_state.mission_templates:
            self.game_state.selected_mission_index = int(active.key.rsplit("_", 1)[-1]) % len(self.game_state.mission_templates)

    def _sync_focus_actions(self) -> None:
        self.focus_model.mission_count = len(self.game_state.mission_templates)
        self.focus_model.set_actions([button.action.key for button in self.room_ui.action_buttons])

    def _equip_active_agent(self, slot: str) -> None:
        """Cycle the active agent through the starter equipment catalog for a slot."""
        active_agent = self._active_agent()
        if not active_agent or slot not in EQUIPMENT_SLOTS:
            return
        options = self.equipment_catalog.get(slot, [])
        if not options:
            return
        current = active_agent.loadout.item_for_slot(slot)
        next_index = 0
        if current:
            for index, item in enumerate(options):
                if item.id == current.id:
                    next_index = (index + 1) % len(options)
                    break
        item = options[next_index]
        active_agent.loadout.equip(slot, item)
        self.message = f"{active_agent.name} equipped {item.name}."
        self.game_state.add_event(self.message)

    def _level_active_agent(self, stat_key: str) -> None:
        active_agent = self._active_agent()
        if not active_agent or active_agent.pending_points <= 0:
            return
        if stat_key not in {"psi", "str", "agi", "con", "cha"}:
            return
        setattr(active_agent.stats, stat_key, getattr(active_agent.stats, stat_key) + 1)
        active_agent.pending_points -= 1
        active_agent.stats.recalculate_hp()
        self.message = f"{active_agent.name} trained {stat_key.upper()} (+1)."
        self.game_state.add_event(self.message)

    def _room_info_lines(self) -> dict[str, list[str]]:
        mission = self.selected_mission()
        selected = self.selected_deployment()
        recovering = [
            character
            for character in self.game_state.characters
            if character.recovery_turns > 0
        ]
        active_agent = (
            self.game_state.characters[self.deployment_cursor_index]
            if self.game_state.characters
            else None
        )
        risk_count = len(agents_at_breaking_risk(selected, mission)) if selected else 0
        selected_asset_count = len(self.game_state.selected_asset_ids)
        ready_asset_count = sum(
            1 for asset in self.game_state.spec_ops_assets if asset.is_deployable
        )
        agent_line = (
            f"{active_agent.name} | Stress {active_agent.stress} | Loyalty {active_agent.loyalty}"
            if active_agent
            else "No agent selected"
        )
        previous_morale = getattr(self.game_state, "_last_squad_morale", None)
        morale_summary = aggregate_squad_morale(selected, previous_morale)
        self.game_state._last_squad_morale = morale_summary.global_morale
        morale_lines = [line.text for line in build_squad_morale_panel_lines(morale_summary)]

        info = {
            "barracks": [
                f"Roster {len(self.game_state.characters)} agents",
                f"Available funds {self.game_state.available_funds}",
                "Recruit cost: 5 funds",
            ] + morale_lines[:2],
            "ops": [
                mission.title,
                f"Risk {mission.risk_level} | Objective {mission.objective_type}",
                f"Target faction {mission.target_faction}",
            ],
            "intel": [
                mission.objective_text,
                f"District pressure entries {len(mission.district_pressure)}",
                f"Complications {len(mission.possible_complications)}",
            ],
            "medbay": [
                f"Recovering agents {len(recovering)}",
                agent_line,
                f"Selected squad {len(selected)} + {selected_asset_count} support",
            ] + morale_lines[:1],
            "armory": (
                [
                    f"Selected squad {len(selected)} + {selected_asset_count} support",
                    f"Deployable agents {sum(1 for char in self.game_state.characters if is_deployable(char))}",
                    f"Ready support assets {ready_asset_count}",
                    f"Upgrade points {getattr(active_agent, 'pending_points', 0) if active_agent else 0}",
                ]
                + (active_agent.loadout.summary_lines() if active_agent else [])
            ),
            "briefing": [
                mission.title,
                f"Breakdown risk agents {risk_count}",
                f"Selected squad {len(selected)} + {selected_asset_count} support",
            ],
            "dossier": (
                [
                    agent_line,
                    f"Upgrade points {getattr(active_agent, 'pending_points', 0) if active_agent else 0}",
                    f"Recovery turns {getattr(active_agent, 'recovery_turns', 0) if active_agent else 0}",
                ]
                + (active_agent.loadout.summary_lines()[:3] if active_agent else [])
            ),
            "insertion": [
                mission.title,
                f"Selected squad {len(selected)} + {selected_asset_count} support",
                "Launch moves agents and support assets to combat.",
            ],
        }
        for room_key, lines in info.items():
            hints = [build_hint_banner("squad", room_key)]
            if self.help_overlay.visible:
                hints.extend(
                    build_help_lines(
                        "squad",
                        room_key,
                        [button.action.label for button in self.room_ui.action_buttons],
                    )[:6]
                )
            info[room_key] = _help_lines_for_view(self.game_state, "squad") + hints + lines
        return info


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
        self.room_ui = RoomUIState("battle")
        self.background = None
        self.camera = arcade.Camera2D()
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        selected_squad = selected_deployable_agents(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.game_state.selected_asset_ids = sanitize_selected_asset_ids(
            self.game_state.spec_ops_assets, self.game_state.selected_asset_ids, selected_squad
        )
        self.player_units = create_player_units(
            self.game_state.characters,
            self.game_state.selected_agent_names,
            self.game_state.spec_ops_assets,
            self.game_state.selected_asset_ids,
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
        self.combat_action_buttons = []
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
        debrief_report = build_mission_debrief_report(
            surviving_participants, self.mission, victory, self.triggered_complication
        )
        self.game_state.latest_mission_debrief = debrief_report.to_dict()
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
            draw_graphical_command_surface(
                self.window.width,
                self.window.height,
                self.room_ui,
                self.game_state.strategic_resources,
                self._room_info_lines(),
                available_funds=self.game_state.available_funds,
            )
            return
        if self.background:
            # Build a rectangle: left, bottom, width, height
            full_rect = arcade.LBWH(0, 0, self.window.width, self.window.height)
            # Draw the texture into that rect
            arcade.draw_texture_rect(
                self.background,  # Texture
                full_rect,  # LBWH rect
                # Only two positional args are accepted here.
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
                player = self.player_units[self.active_index]
                stat_name = {
                    "melee": "str",
                    "shoot": "agi",
                    "psi": "psi",
                }.get(self.pending_attack or "melee", "str")
                atk_val = getattr(player.stats, stat_name)
                defense = target.stats.defense if target.stats else 1
                chance = atk_val / (atk_val + defense) if atk_val > 0 else 0
                chance_width = int(width * chance)
                arcade.draw_lrbt_rectangle_filled(
                    cx - width / 2,
                    cx - width / 2 + chance_width,
                    cy + height / 2 + 4,
                    cy + height / 2 + 9,
                    palette.WARNING,
                )
        if self.attack_line:
            x1, y1, x2, y2 = self.attack_line
            arcade.draw_line(x1, y1, x2, y2, palette.WARNING, 2)
        current_hp = (
            self.player_units[self.active_index].health if self.player_units else 0
        )
        arcade.draw_lrbt_rectangle_filled(
            14,
            self.window.width - 14,
            self.window.height - 92,
            self.window.height - 18,
            palette.PANEL_FILL_DARK,
        )
        max_hp = (
            self.player_units[self.active_index].stats.max_hp
            if self.player_units and self.player_units[self.active_index].stats
            else 1
        )
        hp_width = int(220 * max(0, current_hp) / max(1, max_hp))
        arcade.draw_lrbt_rectangle_filled(
            34, 254, self.window.height - 54, self.window.height - 42, palette.DANGER
        )
        arcade.draw_lrbt_rectangle_filled(
            34,
            34 + hp_width,
            self.window.height - 54,
            self.window.height - 42,
            palette.TACTICAL_GREEN,
        )
        for index in range(max(1, self.turn_number)):
            left = 284 + index * 18
            arcade.draw_lrbt_rectangle_filled(
                left,
                left + 10,
                self.window.height - 58,
                self.window.height - 38,
                palette.ACCENT if self.turn == "player" else palette.WARNING,
            )
        if self.turn == "player" and self.player_units:
            active_unit = self.player_units[self.active_index]
            unit_name = (
                active_unit.character.name
                if active_unit.character
                else active_unit.spec_ops_asset.name
                if active_unit.spec_ops_asset
                else active_unit.unit_type
            )
            self.combat_action_buttons = draw_combat_action_bar(
                self.window.width,
                self.window.height,
                available_combat_actions(active_unit),
                unit_name,
                active_unit.action_points,
                self.message,
            )
        else:
            self.combat_action_buttons = []
        if self.turn == "ended":
            color = palette.TACTICAL_GREEN if not self.enemy_units else palette.DANGER
            arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, 18, color)

    def _begin_target_action(self, player: Unit, attack_key: str) -> None:
        """Enter target selection for an available combat-bar attack."""
        if attack_key == "melee":
            range_cells = 1
            pending = "melee"
        elif attack_key == "fire":
            range_cells = max(1, player.attack_range)
            pending = "shoot"
        else:
            range_cells = 10
            pending = "psi"
        self.target_candidates = [
            enemy
            for enemy in self.enemy_units
            if player.distance_to(enemy) <= range_cells * 32
        ]
        if self.target_candidates:
            self.selecting_target = True
            self.selected_target_idx = 0
            self.pending_attack = pending
        else:
            self.message = "No enemy in range"

    def _perform_combat_action(self, action_key: str) -> bool:
        """Perform a clicked or keyed combat action for the active player unit."""
        if self.turn != "player" or not self.player_units:
            return False
        player = self.player_units[self.active_index]
        available = {action.key for action in available_combat_actions(player)}
        if action_key not in available:
            return False
        if action_key == "move":
            self.message = "Move with arrow keys."
            self.game_state.mark_tutorial_event("used_battle_controls")
            return True
        if action_key in {"fire", "melee", "psi"}:
            self._begin_target_action(player, action_key)
            self.game_state.mark_tutorial_event("used_battle_controls")
            return True
        if action_key == "first_aid":
            if player.action_points <= 0 or not player.stats:
                return True
            before = player.health
            player.health = min(player.stats.max_hp, player.health + 2)
            player.stats.hp = player.health
            player.action_points -= 1
            self.message = f"First aid restores {player.health - before} HP."
            self.check_active_player()
            return True
        if action_key == "missiles":
            self._begin_target_action(player, "fire")
            self.message = "Missile target lock acquired."
            return True
        if action_key == "defend":
            player.defend()
            self.check_active_player()
            return True
        if action_key == "end_turn":
            player.action_points = 0
            self.check_active_player()
            return True
        return False

    def on_key_press(self, key, modifiers):
        if self.map_index is None:
            if key == arcade.key.ESCAPE and self.room_ui.is_open:
                close_room(self.room_ui)
                return
            if arcade.key.KEY_1 <= key <= arcade.key.KEY_9:
                idx = key - arcade.key.KEY_1
                if idx < len(self.available_maps):
                    self.map_index = idx
                    path = os.path.join("assets/maps", self.available_maps[idx])
                    self.background = arcade.load_texture(path)
            elif key == arcade.key.S:
                result = SaveSystem.save_game(self.game_state)
                self.game_state.add_event(result.message)
            elif key == arcade.key.L:
                loaded, result = SaveSystem.load_game()
                self.game_state.add_event(result.message)
                if loaded is not None:
                    self.game_state = loaded
            elif key == arcade.key.ESCAPE:
                corp_view = CorpView(self.game_state)
                corp_view.setup()
                self.window.show_view(corp_view)
            return

        if key == arcade.key.S:
            result = SaveSystem.save_game(self.game_state)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
            return
        if key == arcade.key.L:
            loaded, result = SaveSystem.load_game()
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
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
                    attacker_name = (
                        player.character.name
                        if player.character
                        else player.spec_ops_asset.name
                        if player.spec_ops_asset
                        else player.unit_type
                    )
                    self.message = f"{attacker_name} {atk_name} for {damage}"
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
                self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.DOWN:
            new_x, new_y = player.position[0], player.position[1] - 32
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(0, -32)
                self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.LEFT:
            new_x, new_y = player.position[0] - 32, player.position[1]
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(-32, 0)
                self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.RIGHT:
            new_x, new_y = player.position[0] + 32, player.position[1]
            if not self.is_occupied(new_x, new_y, exclude=player):
                player.move(32, 0)
                self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.SPACE:
            self._perform_combat_action("melee")
        elif key == arcade.key.F:
            self._perform_combat_action("fire")
        elif key == arcade.key.P:
            self._perform_combat_action("psi")
        elif key == arcade.key.A:
            self._perform_combat_action("first_aid")
        elif key == arcade.key.M:
            self._perform_combat_action("missiles")
        elif key == arcade.key.ENTER or key == arcade.key.RETURN:
            self._perform_combat_action("end_turn")
        elif key == arcade.key.D:
            self._perform_combat_action("defend")
        elif key == arcade.key.V:
            player.psi_defend()
        elif key == arcade.key.ESCAPE:
            corp_view = CorpView(self.game_state)
            corp_view.setup()
            self.window.show_view(corp_view)

        self.check_active_player()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.map_index is None:
            if self._handle_map_room_click(x, y):
                return
            return
        if self.turn == "player" and self.player_units:
            active_unit = self.player_units[self.active_index]
            buttons = self.combat_action_buttons or layout_combat_action_buttons(
                self.window.width, available_combat_actions(active_unit)
            )
            action = combat_action_at_point(buttons, x, y)
            if action is not None:
                self._perform_combat_action(action.key)

    def _handle_map_room_click(self, x: int, y: int) -> bool:
        if self.room_ui.is_open:
            if close_button_rect(self.window.width, self.window.height).contains(x, y):
                close_room(self.room_ui)
                return True
            action = action_at_point(self.room_ui.action_buttons, x, y)
            if action is not None and action.key.startswith("map_"):
                idx = int(action.key.removeprefix("map_"))
                if idx < len(self.available_maps):
                    self.map_index = idx
                    path = os.path.join("assets/maps", self.available_maps[idx])
                    self.background = arcade.load_texture(path)
                return True
            return True

        room = room_at_point(self.window.width, self.window.height, "battle", x, y)
        if room is None:
            return False
        open_room(self.room_ui, self.window.width, self.window.height, room.key)
        icons = ("city", "radar", "armory", "shield", "research", "black_ops")
        map_actions = [
            RoomAction(f"map_{index}", icons[index % len(icons)], f"Zone {index + 1}")
            for index, _name in enumerate(self.available_maps[:9])
        ]
        self.room_ui.action_buttons = layout_action_buttons(
            self.window.width, self.window.height, map_actions
        )
        return True

    def _room_info_lines(self) -> dict[str, list[str]]:
        mission_title = self.mission.title if self.mission else "No active mission"
        base = {
            "drop": [
                mission_title,
                f"Available drop zones {len(self.available_maps)}",
                "Choose a map icon to start tactical insertion.",
            ],
            "garage": [
                f"Squad units {len(self.player_units)}",
                f"Enemy contacts {len(self.enemy_units)}",
                "Vehicle bay stages the insertion route.",
            ],
            "maps": [
                f"Available maps {len(self.available_maps)}",
                "Room icons select the drop zone.",
                "Esc closes this room back to the base map.",
            ],
            "comms": [
                mission_title,
                f"Objective marker {'online' if self.battle_objective else 'offline'}",
                "Comms maintains mission status during insertion.",
            ],
            "drone": [
                f"Enemy contacts {len(self.enemy_units)}",
                f"Initial contacts {self.initial_enemy_count}",
                "Drone relay previews tactical resistance.",
            ],
            "casualty": [
                f"Recovering roster losses {len(self.defeated_player_units)}",
                f"Squad units {len(self.player_units)}",
                "Casualty desk tracks battle fallout.",
            ],
            "sensors": [
                f"Mission risk {getattr(self.mission, 'risk_level', 0)}",
                f"Enemy contacts {len(self.enemy_units)}",
                "Sensor floor reviews the combat area.",
            ],
            "uplink": [
                self.game_state.district.name,
                f"Turn {self.game_state.turn}",
                "Uplink returns to corporate command after combat.",
            ],
        }
        help_lines = _help_lines_for_view(self.game_state, "battle")
        return {key: help_lines + value for key, value in base.items()}

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
        if self.map_index is None:
            step_room_ui(self.room_ui, delta_time)
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.attack_line = None
