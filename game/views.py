import arcade
import os
import types

if not hasattr(arcade, "View"):
    class _FallbackArcadeView:
        def __init__(self, *args, **kwargs):
            self.window = None

        def clear(self):
            pass

    arcade.View = _FallbackArcadeView

if not hasattr(arcade, "Camera2D"):
    arcade.Camera2D = lambda *args, **kwargs: None

if not hasattr(arcade, "LBWH"):
    arcade.LBWH = lambda left, bottom, width, height: (left, bottom, width, height)

if not hasattr(arcade, "load_texture"):
    arcade.load_texture = lambda *args, **kwargs: None

if not hasattr(arcade, "draw_texture_rect"):
    arcade.draw_texture_rect = lambda *args, **kwargs: None

if not hasattr(arcade, "draw_rect_outline"):
    arcade.draw_rect_outline = lambda *args, **kwargs: None

if not hasattr(arcade, "Sprite"):
    class _FallbackSprite:
        def __init__(self, *args, **kwargs):
            self.center_x = kwargs.get("center_x", 0)
            self.center_y = kwargs.get("center_y", 0)
            self.width = kwargs.get("width", 32)
            self.height = kwargs.get("height", 32)
            self.visible = True

        def kill(self):
            pass

    arcade.Sprite = _FallbackSprite

if not hasattr(arcade, "SpriteList"):
    class _FallbackSpriteList(list):
        def draw(self):
            pass

    arcade.SpriteList = _FallbackSpriteList

if not hasattr(arcade, "key"):
    arcade.key = types.SimpleNamespace(
        A=65,
        B=66,
        C=67,
        D=68,
        E=69,
        F=70,
        H=72,
        L=76,
        M=77,
        N=78,
        O=79,
        P=80,
        R=82,
        S=83,
        T=84,
        V=86,
        X=88,
        TAB=9,
        SPACE=32,
        ENTER=13,
        RETURN=13,
        ESCAPE=27,
        LEFT=1002,
        RIGHT=1003,
        UP=1004,
        DOWN=1005,
        MOD_SHIFT=1,
        MOD_CTRL=2,
        KEY_1=49,
        KEY_2=50,
        KEY_3=51,
        KEY_4=52,
        KEY_5=53,
        KEY_6=54,
        KEY_7=55,
        KEY_8=56,
        KEY_9=57,
        F1=3001,
        F2=3002,
        F3=3003,
        F4=3004,
        F5=3005,
        F6=3006,
    )

from .agent_aftermath import apply_mission_aftermath
from .agent_readiness import agents_at_breaking_risk
from .battle_outcomes import resolve_defeated_agent_outcome
from .combat_preview import estimate_attack_preview, line_of_fire_warning
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
    remove_agent_from_roster,
    sanitize_selected_agent_names,
    sanitize_selected_asset_ids,
    selected_deployable_agents,
    toggle_agent_selection,
    toggle_asset_selection,
)
from .audio import SoundManager
from .ui import palette
from .ui.combat_action_bar import (
    combat_action_at_point,
    draw_combat_action_bar,
    layout_combat_action_buttons,
)
from .ui.panels import draw_graphical_command_surface
from .progression import ATTRIBUTE_KEYS, option_a_projection, option_b_plan, option_b_projection
from .ui.room_interaction import (
    ROOM_ACTIONS,
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
from .enemy_themes import enemy_sprite_filename, normalize_enemy_theme
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
from .persistence import SaveSystem, SaveSystemResult
from .recruitment import recruit_agent
try:
    from .ui.base import GameView
except Exception:
    from .gamestate import GameState

    class GameView:
        """Fallback base for headless tests that stub out arcade.View."""

        def __init__(self, game_state: GameState | None = None):
            self.game_state = game_state or GameState()
            self.selected_save_slot = 1
            self.window = None

        def clear(self):
            pass
from .ui.command_deck import build_corporate_finance_lines, build_event_panel_lines
from .ui.research_lab import build_research_lab_lines
from .ui.screens.spec_ops_assets import (
    battle_unit_label_and_hint,
    build_asset_outcome_lines,
    build_mission_prep_asset_state_lines,
    build_spec_ops_acquisition_lines,
    build_spec_ops_assets_guide_lines,
)
from .ui.widgets.squad_morale_panel import build_squad_morale_panel_lines
from .ui.widgets.notification_center import NotificationCenter
from .ui.action_feedback import push_action
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
from .ui.guidance.next_action import compute_next_action
from .ui.onboarding.tutorial_overlay import overlay_state_for_screen
from .ui.controllers.mission_controller import (
    mission_index_from_focus_key,
    next_mission_index,
    previous_mission_index,
)
from .ui.controllers.room_actions_controller import (
    apply_asset_toggle,
    apply_agent_toggle,
    select_roster_card,
)
from .ui.controllers.focus_controller import (
    should_open_room_for_focus,
    should_select_mission_for_focus,
    should_trigger_action_for_focus,
)
from .unit import Unit
from .ui.components.combat.action_aftermath import build_action_aftermath_line
from .ui.components.combat.initiative_timeline import (
    build_initiative_timeline,
    draw_initiative_timeline,
)


def _arcade_key(name: str, default: int = 0) -> int:
    """Return an Arcade key code when available, or a harmless default in tests."""
    key_ns = getattr(arcade, "key", None)
    return getattr(key_ns, name, default) if key_ns is not None else default


# ── Sprite path resolver ─────────────────────────────────────────────────────

_UNIT_SPRITE_DIR = "assets/units"

_ROLE_SPRITES: dict[str, str] = {
    "samurai": "agent_samurai.png",
    "sniper":  "agent_sniper.png",
    "psi":     "agent_psi.png",
}

_ASSET_TYPE_SPRITES: dict[str, str] = {
    "combat_robot": "robot_combat.png",
    "robot":        "robot_combat.png",
    "support_robot":"robot_support.png",
    "drone":        "robot_support.png",
    "power_armor":  "power_armor.png",
    "heavy_armor":  "power_armor_heavy.png",
}

_ENEMY_SUBTYPE_SPRITES: dict[str, str] = {
    "grunt":     "enemy_grunt.png",
    "heavy":     "enemy_heavy.png",
    "elite":     "enemy_elite.png",
    "commander": "enemy_commander.png",
}


def _sprite_path_for_unit(unit: Unit) -> str:
    """Return the correct sprite path from assets/units/ for a given unit.

    Falls back to the legacy assets/player.png or assets/enemy.png when no
    typed sprite is available.
    """
    import os

    def _resolve(filename: str) -> str:
        path = os.path.join(_UNIT_SPRITE_DIR, filename)
        return path if os.path.exists(path) else None

    # ── Enemy units ──────────────────────────────────────────────────────────
    if unit.unit_type == "enemy":
        theme = normalize_enemy_theme(getattr(unit, "enemy_theme", "generic"))
        subtype = getattr(unit, "enemy_subtype", "grunt")
        themed_filename = enemy_sprite_filename(theme, subtype)
        path = _resolve(themed_filename)
        if path:
            return path
        filename = _ENEMY_SUBTYPE_SPRITES.get(subtype, "enemy_grunt.png")
        path = _resolve(filename)
        return path if path else "assets/enemy.png"

    # ── Support assets (robots / power armour) ───────────────────────────────
    if unit.spec_ops_asset is not None:
        atype = getattr(unit.spec_ops_asset, "asset_type", "").lower()
        filename = _ASSET_TYPE_SPRITES.get(atype)
        if filename:
            path = _resolve(filename)
            if path:
                return path

    # ── Agent roles ──────────────────────────────────────────────────────────
    if unit.character is not None:
        role = unit.character.role.lower()
        filename = _ROLE_SPRITES.get(role)
        if filename:
            path = _resolve(filename)
            if path:
                return path

    return "assets/player.png"


def _save_to_selected_slot(view: GameView) -> SaveSystemResult:
    return SaveSystem.save_game(view.game_state, SaveSystem.slot_path(view.selected_save_slot))


def _load_from_selected_slot(view: GameView) -> tuple[GameState | None, SaveSystemResult]:
    return SaveSystem.load_game(SaveSystem.slot_path(view.selected_save_slot))


def _cycle_save_slot(view: GameView, step: int) -> int:
    total = 5
    view.selected_save_slot = ((view.selected_save_slot - 1 + step) % total) + 1
    return view.selected_save_slot

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
                    "talent_points": character.talent_points,
                    "specialization_count": len(character.specializations),
                    "specializations": list(character.specializations),
                    "recovery_turns": character.recovery_turns,
                    "level": stats.level,
                "defense": stats.defense + character.loadout.total_stat_bonuses().get("defense", 0),
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
                    "talent_points": 0,
                    "specialization_count": 0,
                    "specializations": [],
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
        _arcade_key("KEY_1"): ("research", {"intel": 5}),
        _arcade_key("KEY_2"): ("security", {"credits": 10, "salvage": 2}),
        _arcade_key("KEY_3"): ("politics", {"influence": 3}),
        _arcade_key("KEY_4"): ("black_ops", {"credits": 5, "intel": 3}),
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
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = _load_from_selected_slot(self)
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
        if should_open_room_for_focus(active.kind):
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._sync_focus_actions()
        elif active.kind == "action":
            self._perform_room_action(active.key)

    def _sync_focus_actions(self) -> None:
        self.focus_model.set_actions([button.action.key for button in self.room_ui.action_buttons])

    def _perform_room_action(self, action_key: str) -> None:
        if action_key == "slot_prev":
            slot = _cycle_save_slot(self, -1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "slot_next":
            slot = _cycle_save_slot(self, 1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "save":
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
            return
        if action_key == "load":
            loaded, result = _load_from_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
            return
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
        if action_key == "next_step":
            self._follow_next_step("corp")
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

    def _follow_next_step(self, screen: str) -> None:
        guidance = compute_next_action(self.game_state, screen)
        if guidance.target_screen == "city":
            view = CityView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        if guidance.target_screen == "squad":
            view = RPGView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        open_room(self.room_ui, self.window.width, self.window.height, guidance.target_room)

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
            guidance = compute_next_action(self.game_state, "corp")
            info[room_key] = [f"Next Step: {guidance.text}"] + _help_lines_for_view(self.game_state, "corp") + hints + lines
        return info


class CityView(GameView):
    CITY_UPGRADE_COSTS = {
        _arcade_key("KEY_7"): ("armaments", {"credits": 5, "salvage": 3}),
        _arcade_key("KEY_8"): ("garrisons", {"credits": 10, "influence": 2}),
        _arcade_key("KEY_9"): ("defense_zones", {"credits": 5, "salvage": 5}),
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
        if key == arcade.key.C:
            corp_view = CorpView(self.game_state)
            corp_view.selected_save_slot = self.selected_save_slot
            corp_view.setup()
            self.window.show_view(corp_view)
        elif key == arcade.key.R:
            rpg_view = RPGView(self.game_state)
            rpg_view.selected_save_slot = self.selected_save_slot
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key == arcade.key.D:
            self.game_state.advance_one_day("manual command")
        elif key in self.CITY_UPGRADE_COSTS:
            budget_key, costs = self.CITY_UPGRADE_COSTS[key]
            self._buy_city_upgrade(budget_key, costs)
        elif key == arcade.key.S:
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = _load_from_selected_slot(self)
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
        if action_key == "slot_prev":
            slot = _cycle_save_slot(self, -1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "slot_next":
            slot = _cycle_save_slot(self, 1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "save":
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
            return
        if action_key == "load":
            loaded, result = _load_from_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
            return
        if action_key == "squad":
            rpg_view = RPGView(self.game_state)
            rpg_view.setup()
            self.window.show_view(rpg_view)
            return
        if action_key == "advance_day":
            self.game_state.advance_one_day("manual command")
            return
        if action_key == "next_step":
            self._follow_next_step("city")
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

    def _follow_next_step(self, screen: str) -> None:
        guidance = compute_next_action(self.game_state, screen)
        if guidance.target_screen == "corp":
            view = CorpView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        if guidance.target_screen == "squad":
            view = RPGView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        open_room(self.room_ui, self.window.width, self.window.height, guidance.target_room)

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
            guidance = compute_next_action(self.game_state, "city")
            info[room_key] = [f"Next Step: {guidance.text}"] + _help_lines_for_view(self.game_state, "city") + hints + lines
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
            self.message = f"{lead_agent.name} is at breakdown risk. Press B again to force deployment."
            self.notifications.warning(self.message)
            return

        if agents_at_risk:
            names = ", ".join(agent.name for agent in agents_at_risk)
            push_action(self.notifications, "mission_launch", True, f"forced {names} into {selected_mission.title} despite breakdown risk")
            self.game_state.add_event(f"Command forced {names} into {selected_mission.title} despite breakdown risk.")

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
            # ENTER toggles the current agent's squad selection (same as SPACE).
            if self.game_state.characters:
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
            return
        if key == arcade.key.ESCAPE and self.room_ui.is_open:
            close_room(self.room_ui)
            return
        if key == arcade.key.C:
            corp_view = CorpView(self.game_state)
            corp_view.selected_save_slot = self.selected_save_slot
            corp_view.setup()
            self.window.show_view(corp_view)
        elif key == arcade.key.X:
            city_view = CityView(self.game_state)
            city_view.selected_save_slot = self.selected_save_slot
            city_view.setup()
            self.window.show_view(city_view)
        elif key == arcade.key.B:
            self.launch_selected_mission()
        elif key == arcade.key.S:
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
        elif key == arcade.key.L:
            loaded, result = _load_from_selected_slot(self)
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
            state = apply_agent_toggle(
                self.game_state.selected_agent_names,
                self.game_state.selected_agent_names,
                self.game_state.selected_asset_ids,
            )
            self.pending_breakdown_confirmation = state.pending_breakdown_confirmation
            self.pending_breakdown_mission_id = state.pending_breakdown_mission_id
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
        result = select_roster_card(
            card_index,
            len(self.game_state.characters),
            self.game_state.selected_agent_names,
            self.game_state.selected_asset_ids,
        )
        if result is None:
            return
        self.deployment_cursor_index = result.cursor_index
        self.pending_breakdown_confirmation = result.pending_breakdown_confirmation
        self.pending_breakdown_mission_id = result.pending_breakdown_mission_id
        self.message = ""
        self._refresh_squad_room_actions()

    def _perform_room_action(self, action_key: str) -> None:
        if action_key == "slot_prev":
            slot = _cycle_save_slot(self, -1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "slot_next":
            slot = _cycle_save_slot(self, 1)
            self.game_state.add_event(f"Active save slot: {slot}.")
            return
        if action_key == "save":
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
            return
        if action_key == "load":
            loaded, result = _load_from_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
            return
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
        if action_key == "remove_agent":
            self._remove_active_agent_from_roster()
            return
        if action_key == "mission_prev" and self.game_state.mission_templates:
            self.game_state.selected_mission_index = previous_mission_index(
                self.game_state.selected_mission_index, len(self.game_state.mission_templates)
            )
            self.game_state.play_ui_audio_feedback("selection")
            self.pending_breakdown_confirmation = False
            self._refresh_squad_room_actions()
            return
        if action_key == "mission_next" and self.game_state.mission_templates:
            self.game_state.selected_mission_index = next_mission_index(
                self.game_state.selected_mission_index, len(self.game_state.mission_templates)
            )
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
            state = apply_asset_toggle(
                self.deployment_cursor_index,
                self.game_state.selected_agent_names,
                self.game_state.selected_asset_ids,
            )
            self.pending_breakdown_confirmation = state.pending_breakdown_confirmation
            self.pending_breakdown_mission_id = state.pending_breakdown_mission_id
            self.game_state.play_ui_audio_feedback("toggle")
            self._refresh_squad_room_actions()
            return
        if action_key == "next_step":
            self._follow_next_step("squad")
            return
        if action_key.startswith("equip_"):
            self._equip_active_agent(action_key.removeprefix("equip_"))
            self._refresh_squad_room_actions()
            return
        if action_key.startswith("level_"):
            self._level_active_agent(action_key.removeprefix("level_"))
            self._refresh_squad_room_actions()
            return
        if action_key.startswith("skillup_"):
            self._level_active_agent_skill(action_key.removeprefix("skillup_"))
            self._refresh_squad_room_actions()
            return
        if action_key == "launch":
            self.launch_selected_mission()

    def _remove_active_agent_from_roster(self) -> None:
        if not self.game_state.characters:
            return
        index = min(max(self.deployment_cursor_index, 0), len(self.game_state.characters) - 1)
        removed, sanitized_agents, sanitized_assets = remove_agent_from_roster(
            self.game_state.characters,
            self.game_state.spec_ops_assets,
            self.game_state.selected_agent_names,
            self.game_state.selected_asset_ids,
            index,
        )
        if removed is None:
            return
        self.game_state.selected_agent_names = sanitized_agents
        self.game_state.selected_asset_ids = sanitized_assets
        self.deployment_cursor_index = min(index, len(self.game_state.characters) - 1) if self.game_state.characters else 0
        self.pending_breakdown_confirmation = False
        self.pending_breakdown_mission_id = None
        self.message = f"{removed.name} removed from roster."
        self.game_state.add_event(push_action(self.notifications, "remove_agent", True, removed.name))
        self._refresh_squad_room_actions()

    def _active_agent(self) -> Character | None:
        if not self.game_state.characters:
            return None
        self.deployment_cursor_index %= len(self.game_state.characters)
        return self.game_state.characters[self.deployment_cursor_index]

    def _follow_next_step(self, screen: str) -> None:
        guidance = compute_next_action(self.game_state, screen)
        if guidance.target_screen == "corp":
            view = CorpView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        if guidance.target_screen == "city":
            view = CityView(self.game_state)
            view.setup()
            self.window.show_view(view)
            return
        open_room(self.room_ui, self.window.width, self.window.height, guidance.target_room)
        self._refresh_squad_room_actions()

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
                    RoomAction("remove_agent", "black_ops", "Remove agent"),
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
                option_b = option_b_projection(active_agent)
                option_b_hint = ", ".join(
                    f"{key[:3].upper()}+{delta}" for key, delta in option_b.skills_delta.items() if delta > 0
                ) or "No eligible skills"
                actions.extend(
                    [
                        RoomAction(
                            "skillup_auto",
                            "research",
                            f"B: +2 skills ({option_b_hint}) | Resolve {option_b.derived_delta.get('resolve', 0):+d} Aim {option_b.derived_delta.get('aim', 0):+d}",
                        ),
                    ]
                )
                for stat_key in ATTRIBUTE_KEYS:
                    proj = option_a_projection(active_agent, stat_key)
                    delta = proj.stats_delta.get(stat_key, 0)
                    if delta <= 0:
                        continue
                    actions.append(
                        RoomAction(
                            f"level_{stat_key}",
                            "research" if stat_key == "psi" else "armory" if stat_key == "str" else "radar" if stat_key == "agi" else "shield" if stat_key == "con" else "influence",
                            f"A: +1 {stat_key.upper()} | HP {proj.derived_delta.get('hp', 0):+d} Def {proj.derived_delta.get('defense', 0):+d} Res {proj.derived_delta.get('resolve', 0):+d}",
                        )
                    )
        elif room_key == "barracks":
            # Expose recruit actions directly at index 0 (no nav wrapper).
            actions = list(ROOM_ACTIONS.get("squad", {}).get("barracks", []))
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
        if should_open_room_for_focus(active.kind):
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._refresh_squad_room_actions()
        elif should_select_mission_for_focus(active.kind, len(self.game_state.mission_templates)):
            self.game_state.selected_mission_index = mission_index_from_focus_key(active.key, len(self.game_state.mission_templates))
            self.pending_breakdown_confirmation = False

    def _trigger_focus(self) -> None:
        active = self.focus_model.active()
        if active is None:
            return
        if should_open_room_for_focus(active.kind):
            open_room(self.room_ui, self.window.width, self.window.height, active.key)
            self._refresh_squad_room_actions()
            return
        if should_trigger_action_for_focus(active.kind):
            self._perform_room_action(active.key)
            return
        if should_select_mission_for_focus(active.kind, len(self.game_state.mission_templates)):
            self.game_state.selected_mission_index = mission_index_from_focus_key(active.key, len(self.game_state.mission_templates))

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
        if not active_agent or active_agent.pending_points <= 0 or stat_key not in ATTRIBUTE_KEYS:
            return
        projection = option_a_projection(active_agent, stat_key)
        delta = projection.stats_delta.get(stat_key, 0)
        if delta <= 0:
            self.message = f"{active_agent.name} {stat_key.upper()} is already capped."
            return
        setattr(active_agent.stats, stat_key, getattr(active_agent.stats, stat_key) + delta)
        active_agent.pending_points -= 1
        active_agent.stats.recalculate_hp()
        self.message = f"{active_agent.name} option A: {stat_key.upper()} +{delta}."
        self.game_state.add_event(self.message)

    def _level_active_agent_skill(self, action_key: str) -> None:
        active_agent = self._active_agent()
        if not active_agent or active_agent.pending_points <= 0 or action_key != "auto":
            return
        planned = option_b_plan(active_agent)
        if not planned:
            self.message = f"{active_agent.name} has no eligible skills to raise."
            return
        applied: list[str] = []
        for key, target in planned.items():
            current = int(active_agent.skills.get(key, 0))
            if target > current:
                active_agent.skills[key] = target
                applied.append(f"{key}+{target-current}")
        active_agent.pending_points -= 1
        self.message = f"{active_agent.name} option B: {', '.join(applied)}."
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
            ] + build_mission_prep_asset_state_lines(self.game_state)[1:],
            "spec_ops": (
                build_spec_ops_assets_guide_lines()
                + build_spec_ops_acquisition_lines(self.game_state)[1:]
                + build_asset_outcome_lines(self.game_state)[1:]
            ),
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
            guidance = compute_next_action(self.game_state, "squad")
            info[room_key] = [f"Next Step: {guidance.text}"] + _help_lines_for_view(self.game_state, "squad") + hints + lines
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
        self.available_maps = sorted(
            f for f in os.listdir("assets/maps")
            if f.lower().endswith((".jpeg", ".jpg", ".png"))
            and not f.startswith(".")
        )
        self.room_ui = RoomUIState("battle")
        # Auto-select a random map ? no manual selection screen needed
        import random as _rnd
        if self.available_maps:
            self.map_index = _rnd.randint(0, len(self.available_maps) - 1)
            self._load_battle_map(self.map_index)
        else:
            self.map_index = 0
            self.background = None
            self.map_path = None
            self.terrain_profile = None
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self._cam_pan_x = 0.0
        self._cam_pan_y = 0.0
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
                _sprite_path_for_unit(unit),
                center_x=unit.position[0],
                center_y=unit.position[1],
            )
            unit.sprite = sprite
            self.player_list.append(sprite)

        for enemy in self.enemy_units:
            sprite = arcade.Sprite(
                _sprite_path_for_unit(enemy),
                center_x=enemy.position[0],
                center_y=enemy.position[1],
            )
            enemy.sprite = sprite
            self.enemy_list.append(sprite)

        if getattr(self, "map_path", None):
            from game.map_terrain import build_terrain_profile

            forced = tuple(unit.position for unit in self.player_units + self.enemy_units)
            self.terrain_profile = build_terrain_profile(
                self.map_path,
                getattr(self.window, "width", 1280),
                getattr(self.window, "height", 720),
                forced_walkable=forced,
            )

        self.turn_number = 1
        self.turn = "player"
        self.active_index = 0
        self.message = self.mission.objective_text if self.mission else ""
        self.triggered_complication = None
        self.attack_timer = 0.0
        self.attack_line = None
        # Attack flash state (screen-edge colour flash)
        self._flash_alpha: int = 0
        self._flash_hit: bool  = True
        # Target selection state
        self.selecting_target = False
        self.target_candidates = []
        self.selected_target_idx = 0
        self.pending_attack = None
        self.selecting_overwatch_orientation = False
        self.overwatch_direction_index = 0
        self.overwatch_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.combat_action_buttons = []
        self.pending_end_turn_confirmation = False
        self.last_input_mode = "keyboard_mouse"
        self._aftermath_line = ""
        self._aftermath_timer = 0.0
        # Phase 1 polish features
        self.damage_popups: list[dict] = []
        self._paused = False
        self._pause_buttons: list = []
        self._show_combat_log = False
        self.combat_log_messages: list[str] = []
        # Phase 2-A02: pre-battle deployment phase
        self._deploying = True
        self._deploy_cursor = 0  # which player unit is being repositioned
        # Phase 4: VFX
        self.particles: list[dict] = []
        self._unit_flashes: dict[int, dict] = {}
        self._death_rings: list[dict] = []
        self._muzzle_flashes: list[dict] = []
        self._psi_waves: list[dict] = []
        self._shake_intensity: float = 0.0
        # Wave 5-B: spectacle
        self._intro_timer: float = 2.2
        self._intro_active: bool = True
        # Wave 5-C: mission objectives
        self._assassination_target: "Unit | None" = None
        self._defend_turns_needed: int = 0
        self._setup_special_objectives()
        # Phase 4: sound
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import SettingsState
        _snd = SoundManager.get()
        _snd.ensure_loaded()
        from game.ui.screens.settings_screen import load_settings as _load_settings
        _snd.configure_from_settings(_load_settings())
        _snd.play_music("music_battle", loop=True)
        # Cover nodes (generated once per map, used for defense bonuses + HUD)
        from game.cover_system import generate_cover_nodes
        self.cover_nodes = generate_cover_nodes(self.map_index, seed_offset=self.turn_number)
        self.start_player_turn()

    def _load_battle_map(self, index: int) -> None:
        """Load the active tactical map texture and terrain profile."""
        if not self.available_maps:
            self.map_index = 0
            self.background = None
            self.map_path = None
            self.terrain_profile = None
            return
        self.map_index = max(0, min(index, len(self.available_maps) - 1))
        self.map_path = os.path.join("assets/maps", self.available_maps[self.map_index])
        self.background = arcade.load_texture(self.map_path)
        from game.map_terrain import build_terrain_profile

        forced = tuple(unit.position for unit in getattr(self, "player_units", [])) + tuple(
            unit.position for unit in getattr(self, "enemy_units", [])
        )
        self.terrain_profile = build_terrain_profile(
            self.map_path,
            getattr(self.window, "width", 1280),
            getattr(self.window, "height", 720),
            forced_walkable=forced,
        )

    def can_move_to(self, x: int, y: int, *, exclude: Unit | None = None) -> bool:
        """Return True when (x, y) is on walkable terrain.

        Occupancy is intentionally not checked here (UI-51: player movement
        stays unrestricted so melee positioning remains fluid). Terrain
        obstacles from the walkability mask are still respected.
        """
        profile = getattr(self, "terrain_profile", None)
        if profile is not None and hasattr(profile, "is_walkable") and not profile.is_walkable(x, y):
            return False
        return True

    def is_occupied(self, x: int, y: int, *, exclude: Unit | None = None) -> bool:
        """Check if a map position is occupied by any living unit."""
        return combat_is_occupied(
            x, y, self.player_units, self.enemy_units, exclude=exclude
        )

    # ── In-battle complication keys that have active effects ──────────────────
    _COMPLICATION_EFFECTS: dict[str, str] = {
        "mod_rapid_response": "reinforcements",
        "rapid_response":     "reinforcements",
        "mod_watcher_drone":  "blackout",
        "watcher_drone":      "blackout",
        "mod_counterintel_ping": "blackout",
        "counterintel_ping":  "blackout",
    }

    def _check_complications(self, turn_number: int) -> None:
        """Trigger mid-battle complication effects keyed to turn milestones."""
        if not self.mission:
            return
        triggered = getattr(self, "_triggered_complication_keys", set())
        if not hasattr(self, "_triggered_complication_keys"):
            self._triggered_complication_keys: set[str] = set()
            triggered = self._triggered_complication_keys

        for comp in self.mission.possible_complications or []:
            key = comp.key
            effect = self._COMPLICATION_EFFECTS.get(key)
            if not effect or key in triggered:
                continue
            # Reinforcements fire on turn 3
            if effect == "reinforcements" and turn_number >= 3:
                triggered.add(key)
                self._spawn_reinforcements(comp.name)
            # Blackout fires on turn 2
            elif effect == "blackout" and turn_number >= 2:
                triggered.add(key)
                self._trigger_blackout(comp.name)

    def _spawn_reinforcements(self, comp_name: str) -> None:
        """Spawn 2 grunt reinforcements from a random map edge."""
        import random as _rnd
        from game.stats import EnemyStats
        w = getattr(self.window, "width", 1280)
        h = getattr(self.window, "height", 720)
        edges = [(32, _rnd.randint(64, h - 64)), (w - 32, _rnd.randint(64, h - 64))]
        spawned = 0
        for ex, ey in edges[:2]:
            if spawned >= 2:
                break
            stats = EnemyStats(hp=4, max_hp=4, agi=2, defense=1)
            new_enemy = Unit(
                position=(ex, ey),
                stats=stats,
                unit_type="grunt",
                enemy_subtype="grunt",
                health=4,
                action_points=2,
                attack_range=1,
            )
            try:
                sprite = arcade.Sprite(
                    "assets/enemy.png",
                    center_x=ex,
                    center_y=ey,
                )
                new_enemy.sprite = sprite
                self.enemy_list.append(sprite)
            except Exception:
                pass
            self.enemy_units.append(new_enemy)
            spawned += 1
        self._snd().play("sfx_reinforce")
        self._add_screen_shake(10)
        for eu in self.enemy_units[-spawned:]:
            self._spawn_particles(*eu.position, count=14, color=(255, 60, 40))
        self.message = f"COMPLICATION: {comp_name} — Reinforcements incoming!"
        self.combat_log_messages.append(f"⚠ REINFORCEMENTS: {comp_name}")
        self._aftermath_line = f"COMPLICATION: {comp_name}"
        self._aftermath_timer = 3.0

    def _trigger_blackout(self, comp_name: str) -> None:
        """Reduce fog-of-war sight radius for 2 turns."""
        # Patch the FOG sight radius constant in battle_hud temporarily
        try:
            import game.ui.screens.battle_hud as _hud
            if not hasattr(self, "_original_fog_radius"):
                self._original_fog_radius = getattr(_hud, "_FOG_SIGHT_RADIUS", 5)
                _hud._FOG_SIGHT_RADIUS = 3
                self._blackout_turns_left = 2
        except Exception:
            pass
        self.message = f"COMPLICATION: {comp_name} — Visibility reduced!"
        self.combat_log_messages.append(f"⚠ BLACKOUT: {comp_name}")
        self._aftermath_line = f"COMPLICATION: {comp_name}"
        self._aftermath_timer = 3.0

    def start_player_turn(self):
        for unit in self.player_units:
            msgs = unit.tick_status_effects()
            for msg in msgs:
                if "bleeding" in msg:
                    name = unit.character.name if unit.character else unit.unit_type
                    self.combat_log_messages.append(f"{name} is bleeding (-1 HP)")
                    self._snd().play("sfx_bleed", 0.7)
                    self._spawn_particles(*unit.position, count=5, color=(200, 40, 40))
            unit.reset_actions()
        if self.turn == "enemy":
            self.turn_number += 1
        self.turn = "player"
        self.active_index = 0
        self.combat_log_messages.append(f"── Turn {self.turn_number} ──")
        self._snd().play("sfx_turn_player")
        # Defend objective: check if hold turns are reached
        if self._defend_turns_needed > 0 and self.turn_number > self._defend_turns_needed:
            self.end_battle(True)
            return
        # Defend objective: check if enemy reached the objective position
        if self._defend_turns_needed > 0 and self.battle_objective:
            obj_pos = self.battle_objective.position
            for enemy in self.enemy_units:
                dx = abs(enemy.position[0] - obj_pos[0])
                dy = abs(enemy.position[1] - obj_pos[1])
                if dx <= 32 and dy <= 32:
                    self.message = "POSITION BREACHED — Mission failed!"
                    self.end_battle(False)
                    return
        # Tick blackout duration
        if hasattr(self, "_blackout_turns_left"):
            self._blackout_turns_left -= 1
            if self._blackout_turns_left <= 0:
                try:
                    import game.ui.screens.battle_hud as _hud
                    _hud._FOG_SIGHT_RADIUS = getattr(self, "_original_fog_radius", 5)
                    del self._blackout_turns_left
                    del self._original_fog_radius
                except Exception:
                    pass
        self._check_complications(self.turn_number)

    def start_enemy_turn(self):
        for enemy in self.enemy_units:
            enemy.reset_actions()
        self.turn = "enemy"
        self._snd().play("sfx_turn_enemy")
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
            unit.character._pre_battle_level = getattr(unit.character.stats, "level", 1)
            if victory:
                unit.character.gain_xp(50 * defeated)
        self.game_state.selected_agent_names = sanitize_selected_agent_names(
            self.game_state.characters, self.game_state.selected_agent_names
        )
        self.game_state.award_mission_resources(self.mission, victory, defeated)
        self.resolve_mission_outcome(victory)
        # Campaign: record story mission completion
        if self.mission and self.mission.id.startswith("sm_"):
            try:
                from game.campaign.engine import record_story_mission_complete
                if victory:
                    record_story_mission_complete(self.game_state, self.mission.id)
                    self.game_state.campaign.record_trigger(f"story_complete_{self.mission.id}")
            except Exception:
                pass
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
        outcomes = []
        for unit in all_player_units:
            if not unit.spec_ops_asset or not unit.stats:
                continue
            asset = unit.spec_ops_asset
            max_hp = max(1, unit.stats.max_hp)
            damage_pct = int(max(0, min(100, (max_hp - max(0, unit.health)) * 100 / max_hp)))
            asset.maintenance.integrity = max(0, asset.maintenance.integrity - damage_pct)
            asset.maintenance.cooldown_days = 1 if damage_pct >= 30 else 0
            outcomes.append(
                {
                    "id": asset.id,
                    "name": asset.name,
                    "damage": damage_pct,
                    "repair_cost": asset.maintenance.repair_cost,
                    "cooldown_days": asset.maintenance.cooldown_days,
                }
            )
        self.game_state.latest_spec_ops_outcomes = outcomes
        for line in aftermath_lines:
            self.game_state.add_event(line)

        # Sound: victory fanfare or defeat tone; stop battle music
        self._snd().stop_music()
        self._snd().play("sfx_victory" if victory else "sfx_defeat")
        if victory and hasattr(self, "_death_rings"):
            _wc = getattr(self.window, "width", 1280) // 2
            _hc = getattr(self.window, "height", 720) // 2
            self._spawn_death_ring(_wc, _hc, color=(60, 220, 120))
            self._add_screen_shake(6)

        # Collect promotion records (agents who levelled up)
        from game.ui.screens.agent_promotion_view import AgentPromotionView, PromotionRecord
        from game.ui.portraits import portrait_path_for_character as _ppfc
        promotions: list[PromotionRecord] = []
        for char in surviving_participants:
            old_lvl = getattr(char, "_pre_battle_level", char.stats.level)
            new_lvl = char.stats.level
            if new_lvl > old_lvl:
                try:
                    _ppath = _ppfc(char)
                except Exception:
                    _ppath = None
                promotions.append(PromotionRecord(
                    character=char,
                    old_level=old_lvl,
                    new_level=new_lvl,
                    portrait_path=_ppath,
                ))

        # Build per-agent debrief stats from tracked data
        from game.ui.screens.battle_debrief_view import AgentDebriefStat, BattleDebriefView
        from game.ui.portraits import portrait_path_for_character
        agent_stats: list[AgentDebriefStat] = []
        for unit in all_player_units:
            if not unit.character:
                continue
            try:
                portrait = portrait_path_for_character(unit.character)
            except Exception:
                portrait = None
            old_stress = getattr(unit.character, "_pre_battle_stress", unit.character.stress)
            agent_stats.append(AgentDebriefStat(
                name=unit.character.name,
                role=unit.character.role,
                portrait_path=portrait,
                damage_dealt=getattr(unit, "_damage_dealt", 0),
                damage_taken=getattr(unit, "_damage_taken", 0),
                actions_used=getattr(unit, "_actions_used", 0),
                kills=getattr(unit, "_kills", 0),
                kia=(unit.health <= 0),
                stress_delta=unit.character.stress - old_stress,
            ))

        debrief_view = BattleDebriefView(self.game_state, victory, self.mission, agent_stats)
        if promotions:
            self.window.show_view(AgentPromotionView(self.game_state, promotions, debrief_view))
        else:
            self.window.show_view(debrief_view)

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
            from game.unit import STATUS_STUNNED, STATUS_SUPPRESSED
            target_name = target.character.name if target.character else "agent"
            self.message = f"Enemy hits {target_name} for {damage}"
            self._add_damage_popup(target, damage)
            self.combat_log_messages.append(f"Enemy → {target_name}: {damage} dmg")
            # Sound + VFX
            self._snd().play("sfx_fire", 0.6)
            self._spawn_muzzle_flash(*enemy.position)
            if damage > 0:
                self._snd().play("sfx_hit", 0.8)
                self._spawn_particles(*target.position, count=10, color=(255, 80, 50))
                self._flash_unit(target, color=(255, 60, 60))
                self._add_screen_shake(8)
                # Heavy melee applies STUNNED
                if enemy.enemy_subtype == "heavy" and enemy.distance_to(target) <= 32:
                    target.apply_status(STATUS_STUNNED)
                    self._snd().play("sfx_stun", 0.9)
                    self._flash_unit(target, color=(160, 100, 255), duration=0.25)
                    self.combat_log_messages.append(f"{target_name} is stunned!")
            self.start_attack_animation(enemy, target)
            self._flash_hit   = False
            self._flash_alpha = 140

        def on_defeated(target: Unit) -> None:
            self._snd().play("sfx_death")
            self._spawn_death_ring(*target.position, color=(200, 60, 60))
            self._spawn_particles(*target.position, count=16, color=(220, 50, 30))
            self._add_screen_shake(10)
            if target.sprite:
                target.sprite.kill()
            if self.active_index > 0:
                self.active_index = min(self.active_index - 1, len(self.player_units))
            # Morale cascade: surviving players have 30% chance of SUPPRESSED
            import random as _mr
            from game.unit import STATUS_SUPPRESSED
            kia_name = target.character.name if target.character else "an agent"
            for ally in self.player_units:
                if ally is not target and ally.health > 0 and _mr.random() < 0.30:
                    ally.apply_status(STATUS_SUPPRESSED)
                    ally_name = ally.character.name if ally.character else "Agent"
                    self.combat_log_messages.append(f"{ally_name} shaken by {kia_name}'s fall")

        def on_overwatch_shot(watcher: Unit, enemy: Unit, damage: int) -> None:
            from game.unit import STATUS_SUPPRESSED
            watcher_name = watcher.character.name if watcher.character else "Agent"
            self._snd().play("sfx_fire", 0.75)
            self._spawn_muzzle_flash(*watcher.position)
            if damage > 0:
                self.message = f"OVERWATCH! {watcher_name} hits for {damage}"
                enemy.apply_status(STATUS_SUPPRESSED)
                self.combat_log_messages.append(f"Overwatch! Enemy suppressed.")
                self._spawn_particles(*enemy.position, count=8, color=(255, 200, 60))
                self._flash_unit(enemy, color=(255, 200, 60))
                self._add_screen_shake(4)
                self.start_attack_animation(watcher, enemy)
                self._flash_hit   = True
                self._flash_alpha = 200
            else:
                self.message = f"OVERWATCH! {watcher_name} misses"

        run_enemy_ai_system(
            self.player_units,
            self.enemy_units,
            defeated_player_units=self.defeated_player_units,
            on_attack=on_attack,
            on_defeated=on_defeated,
            on_overwatch_shot=on_overwatch_shot,
            can_enter=lambda x, y: self.can_move_to(x, y, exclude=None),
            cover_nodes=getattr(self, "cover_nodes", None),
        )

    def on_draw(self):
        from game.ui.screens.battle_hud import (
            draw_active_unit_ring,
            draw_attack_flash,
            draw_attack_range,
            draw_cover_nodes,
            draw_fog_of_war,
            draw_mission_status_bar,
            draw_movement_range,
            draw_objective_marker,
            draw_phase_banner,
            draw_resource_summary,
            draw_tactical_grid,
            draw_target_lock_panel,
            draw_overwatch_preview,
            draw_unit_labels,
            draw_unit_portrait_strip,
            draw_unit_status_panel,
            battle_shortcut_banner,
            draw_battle_shortcut_banner,
            draw_action_aftermath_line,
            update_enemy_visibility,
        )

        self.clear()

        w, h = self.window.width, self.window.height

        # ── World camera (panned + shake) ────────────────────────────────
        import random as _rr
        sx = _rr.uniform(-1, 1) * self._shake_intensity if self._shake_intensity > 0 else 0.0
        sy = _rr.uniform(-1, 1) * self._shake_intensity if self._shake_intensity > 0 else 0.0
        self.camera.position = arcade.Vec2(
            w / 2 + self._cam_pan_x + sx,
            h / 2 + self._cam_pan_y + sy,
        )
        self.camera.use()

        # ── Pre-battle drop-zone selection ──────────────────────────────
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

        # ── Background map ───────────────────────────────────────────────
        if self.background:
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, w, h))

        # ── Tactical grid ────────────────────────────────────────────────
        draw_tactical_grid(w, h)

        # ── Cover nodes ───────────────────────────────────────────────────
        cover_nodes = getattr(self, "cover_nodes", [])
        draw_cover_nodes(cover_nodes)

        # ── Movement range (player turn only) ───────────────────────────
        has_active = bool(self.player_units) and 0 <= self.active_index < len(self.player_units)
        active_unit = self.player_units[self.active_index] if has_active else None

        if self.turn == "player" and active_unit and not self.selecting_target:
            draw_movement_range(
                active_unit,
                w,
                h,
                can_enter=lambda x, y: self.can_move_to(x, y, exclude=active_unit),
            )

        if self.selecting_target and active_unit:
            draw_attack_range(active_unit, w, h, highlight=True)
        elif self.selecting_overwatch_orientation and active_unit:
            direction = self.overwatch_directions[self.overwatch_direction_index]
            draw_overwatch_preview(active_unit, direction, w, h)

        # ── Objective marker ─────────────────────────────────────────────
        elapsed = getattr(self, "_battle_elapsed", 0.0)
        draw_objective_marker(self.battle_objective, elapsed)

        # ── Fog of war — darken unseen tiles, hide invisible enemies ────
        update_enemy_visibility(self.player_units, self.enemy_units)
        for enemy in self.enemy_units:
            if enemy.sprite:
                enemy.sprite.visible = enemy.visible
        draw_fog_of_war(self.player_units, w, h)

        # ── Units ────────────────────────────────────────────────────────
        self.enemy_list.draw()
        self.player_list.draw()

        # ── Active unit selection ring ───────────────────────────────────
        if active_unit and self.turn == "player":
            draw_active_unit_ring(active_unit, elapsed)

        # ── Unit labels (HP bars + names) ────────────────────────────────
        draw_unit_labels(self.player_units, self.enemy_units, self.active_index)

        # ── Assassination target marker ──────────────────────────────────
        if self._assassination_target and self._assassination_target in self.enemy_units:
            from game.ui.screens.battle_hud import draw_assassination_marker
            draw_assassination_marker(self._assassination_target, elapsed)

        # ── Target selection overlay ──────────────────────────────────────
        if self.selecting_target and self.target_candidates:
            target = self.target_candidates[self.selected_target_idx]
            if target.sprite:
                cx = target.sprite.center_x
                cy = target.sprite.center_y
                tw  = target.sprite.width + 10
                th  = target.sprite.height + 10
                arcade.draw_rect_outline(
                    arcade.LBWH(cx - tw / 2, cy - th / 2, tw, th),
                    palette.WARNING, border_width=2,
                )
            draw_target_lock_panel(w, target, self.pending_attack or "melee", active_unit)

        # ── Attack animation ─────────────────────────────────────────────
        if self.attack_line:
            x1, y1, x2, y2 = self.attack_line
            arcade.draw_line(x1, y1, x2, y2, palette.WARNING, 3)
            # Bright flash at impact point
            arcade.draw_lrbt_rectangle_filled(x2 - 8, x2 + 8, y2 - 8, y2 + 8, (*palette.WARNING[:3], 180))

        # ── Advanced VFX (world space) ───────────────────────────────────
        from game.ui.screens.battle_hud import (
            draw_damage_popups,
            draw_particles,
            draw_hit_flashes,
            draw_death_rings,
            draw_muzzle_flashes,
            draw_psi_waves,
        )
        draw_muzzle_flashes(self._muzzle_flashes)
        draw_psi_waves(self._psi_waves)
        all_units = self.player_units + self.enemy_units
        draw_hit_flashes(all_units, self._unit_flashes)
        draw_particles(self.particles)
        draw_death_rings(self._death_rings)

        # ── Floating damage numbers (world space) ────────────────────────
        draw_damage_popups(self.damage_popups)

        # ── Switch to GUI camera (screen-fixed HUD) ──────────────────────
        self.gui_camera.use()

        # ── Deployment phase overlay (intercepts HUD) ────────────────────
        if self._deploying:
            from game.ui.screens.battle_hud import draw_deployment_overlay
            draw_deployment_overlay(w, h, self.player_units, self._deploy_cursor, elapsed)
            return

        # ── Mission status bar (top) ──────────────────────────────────────
        draw_mission_status_bar(
            w, h,
            self.mission.title if self.mission else "MISSION",
            len(self.player_units),
            len(self.enemy_units),
            self.turn_number,
        )
        draw_resource_summary(w, h, self.game_state.strategic_resources, self.game_state.available_funds)

        # ── Phase indicator (top-right) ──────────────────────────────────
        draw_phase_banner(w, h, self.turn, self.turn_number, elapsed)

        timeline = build_initiative_timeline(
            self.player_units,
            self.enemy_units,
            active_player_index=self.active_index,
            slots=8,
        )
        draw_initiative_timeline(w, h, timeline)

        # ── Unit status panel (bottom-left) ──────────────────────────────
        draw_unit_status_panel(w, h, active_unit, self.turn)
        draw_battle_shortcut_banner(
            w,
            h,
            battle_shortcut_banner(
                getattr(self, "last_input_mode", "keyboard_mouse"),
                self.selecting_target,
                getattr(self, "pending_end_turn_confirmation", False),
            ),
        )
        draw_action_aftermath_line(w, h, self._aftermath_line if self._aftermath_timer > 0 else "")

        # ── Combat action bar ─────────────────────────────────────────────
        if self.turn == "player" and active_unit:
            role_label, action_hint = battle_unit_label_and_hint(active_unit)
            unit_name = (
                active_unit.character.name if active_unit.character
                else active_unit.spec_ops_asset.name if active_unit.spec_ops_asset
                else active_unit.unit_type
            )
            preview = None
            warning = None
            if self.selecting_target and self.target_candidates:
                target = self.target_candidates[self.selected_target_idx]
                attack_kind = self.pending_attack or "shoot"
                preview = estimate_attack_preview(active_unit, target, attack_kind)
                warning = line_of_fire_warning(active_unit, target, self.player_units)
            self.combat_action_buttons = draw_combat_action_bar(
                w, h,
                available_combat_actions(active_unit),
                f"{unit_name} [{role_label}]",
                active_unit.action_points,
                f"{self.message}  {action_hint}",
                preview=preview,
                warning=warning,
            )
        else:
            self.combat_action_buttons = []

        # ── Portrait strip (all player units, bottom) ────────────────────
        draw_unit_portrait_strip(self.player_units, self.active_index, w, elapsed)

        # ── Screen-edge attack flash ─────────────────────────────────────
        draw_attack_flash(w, h, self._flash_hit, self._flash_alpha)

        # ── Ambient atmosphere (scanlines, neon glow, map-keyed fx) ─────
        from game.ui.screens.battle_hud import draw_ambient_overlay
        draw_ambient_overlay(w, h, elapsed, getattr(self, "map_path", "") or "", self.particles)

        # ── End-of-battle indicator ──────────────────────────────────────
        if self.turn == "ended":
            color = palette.TACTICAL_GREEN if not self.enemy_units else palette.DANGER
            arcade.draw_lrbt_rectangle_filled(0, w, 0, 18, color)
            arcade.draw_text(
                "MISSION COMPLETE" if not self.enemy_units else "MISSION FAILED",
                w // 2, 10, color, font_size=10, bold=True,
                anchor_x="center", anchor_y="center",
            )

        # ── Mission intro sequence (fade-in overlay) ────────────────────
        if self._intro_active:
            from game.ui.screens.battle_hud import draw_mission_intro
            _intro_progress = max(0.0, 1.0 - self._intro_timer / 2.2)
            _district = getattr(getattr(self.mission, "district", None), "__str__", lambda: "")() if self.mission else ""
            draw_mission_intro(w, h,
                               self.mission.title if self.mission else "TACTICAL INSERTION",
                               _district,
                               _intro_progress)

        # ── Combat log side panel (Tab toggle) ──────────────────────────
        if self._show_combat_log:
            from game.ui.screens.battle_hud import draw_combat_log_side_panel
            draw_combat_log_side_panel(w, h, self.combat_log_messages)

        # ── Pause overlay (Escape) ───────────────────────────────────────
        if self._paused:
            from game.ui.screens.battle_hud import draw_pause_overlay
            self._pause_buttons = draw_pause_overlay(w, h)

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
            if getattr(enemy, "visible", True)
            and player.distance_to(enemy) <= range_cells * 32
        ]
        if self.target_candidates:
            self.selecting_target = True
            self.selected_target_idx = 0
            self.pending_attack = pending
        else:
            self.message = "No visible enemy in range"

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
            self._set_action_aftermath(action_label="MOVE")
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
            healed = player.health - before
            self.message = f"First aid restores {healed} HP."
            if healed > 0:
                self._spawn_particles(*player.position, count=10, color=(60, 220, 120))
                self._flash_unit(player, color=(60, 220, 120))
            self._set_action_aftermath(
                action_label="SKILL",
                status_applied=f"+{player.health - before} HP",
            )
            self.check_active_player()
            return True
        if action_key == "missiles":
            self._begin_target_action(player, "fire")
            self.message = "Missile target lock acquired."
            return True
        if action_key == "overwatch":
            self.selecting_overwatch_orientation = True
            self.overwatch_direction_index = 0
            self.message = "Rotate overwatch cone with ←/→ then confirm (Entrée/O)."
            return True
        if action_key == "defend":
            player.defend()
            self.check_active_player()
            return True
        if action_key == "end_turn":
            if not self.pending_end_turn_confirmation:
                self.pending_end_turn_confirmation = True
                self.message = "Confirm end turn to lock irreversible actions."
                return True
            self.pending_end_turn_confirmation = False
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
                    self._load_battle_map(idx)
            elif key == arcade.key.S:
                result = _save_to_selected_slot(self)
                self.game_state.add_event(result.message)
            elif key == arcade.key.L:
                loaded, result = _load_from_selected_slot(self)
                self.game_state.add_event(result.message)
                if loaded is not None:
                    self.game_state = loaded
            elif key == arcade.key.ESCAPE:
                from game.ui.screens.management_screen import ManagementView
                mgmt = ManagementView(self.game_state)
                mgmt.setup()
                self.window.show_view(mgmt)
            return

        if key == arcade.key.S and not (modifiers & arcade.key.MOD_SHIFT):
            self.last_input_mode = "keyboard_mouse"
            result = _save_to_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "save", result.ok, result.message))
            return
        if key == arcade.key.L:
            loaded, result = _load_from_selected_slot(self)
            self.game_state.add_event(push_action(self.notifications, "load", result.ok, result.message))
            if loaded is not None:
                self.game_state = loaded
            return

        # ── Pause menu guard ─────────────────────────────────────────────
        if self._paused:
            if key == arcade.key.ESCAPE:
                self._paused = False
            return

        # ── Tab: toggle combat log side panel ────────────────────────────
        if key == arcade.key.TAB:
            self._show_combat_log = not self._show_combat_log
            return

        # ── Camera pan: Shift + arrows (works any turn) ──────────────────
        _PAN = 64  # 2 grid cells per step
        if modifiers & arcade.key.MOD_SHIFT:
            if key == arcade.key.LEFT:
                self._cam_pan_x -= _PAN
            elif key == arcade.key.RIGHT:
                self._cam_pan_x += _PAN
            elif key == arcade.key.UP:
                self._cam_pan_y += _PAN
            elif key == arcade.key.DOWN:
                self._cam_pan_y -= _PAN
            return

        # ── Home: re-center camera on active unit ────────────────────────
        if key == arcade.key.HOME:
            self._cam_pan_x = 0.0
            self._cam_pan_y = 0.0
            return

        # ── Deployment phase input ───────────────────────────────────────
        if self._deploying:
            self._handle_deployment_key(key)
            return

        if self.turn != "player" or not self.player_units:
            return

        self.last_input_mode = "keyboard_mouse"

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
                if not getattr(target, "visible", True):
                    self.message = "Target lost in fog."
                    self.selecting_target = False
                    self.target_candidates = []
                    self.pending_attack = None
                    return
                if self.pending_attack == "melee":
                    damage = player.melee_attack(target)
                elif self.pending_attack == "shoot":
                    damage = player.shoot(target)
                else:
                    damage = player.psi_attack(target)
                self._add_damage_popup(target, damage)
                atk_type = self.pending_attack or "shoot"
                # Sound
                _sfx_map = {"melee": "sfx_melee", "shoot": "sfx_fire", "psi": "sfx_psi"}
                self._snd().play(_sfx_map.get(atk_type, "sfx_fire"))
                # Muzzle flash at attacker
                self._spawn_muzzle_flash(*player.position)
                if damage > 0:
                    atk_name = {"melee": "slashes", "shoot": "shoots", "psi": "psy hits"}[atk_type]
                    attacker_name = (
                        player.character.name if player.character
                        else player.spec_ops_asset.name if player.spec_ops_asset
                        else player.unit_type
                    )
                    cover_note = " (through cover)" if target.in_cover_bonus > 0 else ""
                    self.message = f"{attacker_name} {atk_name} for {damage}{cover_note}"
                    self.combat_log_messages.append(f"{attacker_name} → {damage} dmg")
                    self.start_attack_animation(player, target)
                    self._flash_hit   = True
                    self._flash_alpha = 160
                    # VFX on target
                    _is_crit = getattr(player, "_last_crit", False)
                    self._snd().play("sfx_hit", 0.7)
                    _col = (90, 160, 255) if atk_type == "psi" else (255, 180, 60)
                    _count = 20 if _is_crit else 12
                    self._spawn_particles(*target.position, count=_count, color=_col)
                    self._flash_unit(target, color=(255, 255, 255) if _is_crit else _col[:3])
                    if atk_type == "psi":
                        self._spawn_psi_wave(*player.position)
                    _shake = (14 if _is_crit else 5) if atk_type == "melee" else (10 if _is_crit else 3)
                    self._add_screen_shake(_shake)
                    if _is_crit:
                        # "CRITICAL!" popup replaces the normal "-N" popup
                        self.damage_popups[-1]["text"] = f"CRITICAL! -{damage}"
                        self.damage_popups[-1]["color"] = (255, 60, 20)
                        self.damage_popups[-1]["max_age"] = 1.2
                        self._snd().play("sfx_hit", 1.0)
                else:
                    cover_note = " — cover blocked!" if target.in_cover_bonus > 0 else " — miss!"
                    self._flash_hit   = False
                    self._flash_alpha = 120
                    self.message = f"Attack missed{cover_note}"
                    self.combat_log_messages.append(f"Attack missed{cover_note}")
                    self._snd().play("sfx_miss")
                self._set_action_aftermath(
                    action_label=(self.pending_attack or "ACTION").upper(),
                    damage=damage,
                    status_applied="touché" if damage > 0 else "raté",
                    suppression_created=target.health <= 0,
                )

                # ── Remove killed enemy immediately (hit or pre-existing death) ──
                if target.health <= 0:
                    self._snd().play("sfx_death")
                    self._spawn_death_ring(*target.position, color=(255, 80, 60))
                    self._spawn_particles(*target.position, count=18, color=(255, 60, 40))
                    self._add_screen_shake(12)
                    # XP popup above the killer
                    _xp_gain = 50
                    self.damage_popups.append({
                        "x": player.position[0], "y": player.position[1] + 36,
                        "text": f"+{_xp_gain} XP",
                        "color": (255, 220, 50),
                        "age": 0.0, "max_age": 1.3,
                    })
                    if target.sprite:
                        target.sprite.kill()
                    if target in self.enemy_units:
                        self.enemy_units.remove(target)
                    # Assassination: instant win when the target dies
                    if self._assassination_target is target:
                        self.selecting_target = False
                        self.target_candidates = []
                        self.pending_attack = None
                        self.end_battle(True)
                        return
                    if not self.enemy_units:
                        self.selecting_target = False
                        self.target_candidates = []
                        self.pending_attack = None
                        self.end_battle(True)
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

        if self.selecting_overwatch_orientation:
            if key in (arcade.key.LEFT, arcade.key.A):
                self.overwatch_direction_index = (self.overwatch_direction_index - 1) % len(self.overwatch_directions)
                self.message = "Overwatch orientation changed."
                return
            if key in (arcade.key.RIGHT, arcade.key.D):
                self.overwatch_direction_index = (self.overwatch_direction_index + 1) % len(self.overwatch_directions)
                self.message = "Overwatch orientation changed."
                return
            if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.O):
                if player.set_overwatch():
                    player.overwatch_direction = self.overwatch_directions[self.overwatch_direction_index]
                    self.message = f"{getattr(player.character, 'name', 'Unit')} is on OVERWATCH."
                    self._snd().play("sfx_overwatch")
                    self.selecting_overwatch_orientation = False
                    self.check_active_player()
                return
            if key == arcade.key.ESCAPE:
                self.selecting_overwatch_orientation = False
                self.message = "Overwatch cancelled."
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
            player.move(0, 32)
            self._set_action_aftermath(action_label="MOVE")
            self._log_move(player)
            self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.DOWN:
            player.move(0, -32)
            self._set_action_aftermath(action_label="MOVE")
            self._log_move(player)
            self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.LEFT:
            player.move(-32, 0)
            self._set_action_aftermath(action_label="MOVE")
            self._log_move(player)
            self.game_state.mark_tutorial_event("used_battle_controls")
        elif key == arcade.key.RIGHT:
            player.move(32, 0)
            self._set_action_aftermath(action_label="MOVE")
            self._log_move(player)
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
        elif key == arcade.key.O:
            self._perform_combat_action("overwatch")
        elif key == arcade.key.ENTER or key == arcade.key.RETURN:
            self._perform_combat_action("end_turn")
        elif key == arcade.key.ESCAPE and self.pending_end_turn_confirmation:
            self.pending_end_turn_confirmation = False
            self.message = "End turn cancelled."
            return
        elif key == arcade.key.D:
            self._perform_combat_action("defend")
        elif key == arcade.key.V:
            player.psi_defend()
        elif key == arcade.key.ESCAPE:
            self._paused = True
            return

        self.check_active_player()

    # ── Phase 4: VFX helpers ──────────────────────────────────────────────────

    def _add_damage_popup(self, unit: "Unit", damage: int) -> None:
        """Spawn a floating damage number above the given unit."""
        text = f"-{damage}" if damage > 0 else "MISS"
        color = (255, 80, 60) if damage > 0 else (160, 160, 160)
        self.damage_popups.append({
            "x": unit.position[0],
            "y": unit.position[1] + 20,
            "text": text,
            "color": color,
            "age": 0.0,
            "max_age": 0.8,
        })

    def _add_screen_shake(self, intensity: float) -> None:
        """Add screen shake — capped so multiple hits don't compound excessively."""
        if not SoundManager.get().camera_shake:
            return
        self._shake_intensity = min(20.0, self._shake_intensity + intensity)

    def _spawn_particles(self, x: float, y: float, count: int = 12,
                         color: tuple = (255, 180, 60)) -> None:
        import random as _r
        import math as _m
        for _ in range(count):
            angle = _r.uniform(0, 2 * _m.pi)
            speed = _r.uniform(60, 220)
            self.particles.append({
                "x": x, "y": y,
                "vx": _m.cos(angle) * speed,
                "vy": _m.sin(angle) * speed,
                "color": color,
                "life": 1.0,
                "size": _r.uniform(2.0, 5.5),
            })

    def _flash_unit(self, unit: "Unit", color: tuple = (255, 255, 255),
                    duration: float = 0.15) -> None:
        self._unit_flashes[id(unit)] = {
            "timer": duration,
            "max_timer": duration,
            "color": color,
        }

    def _spawn_death_ring(self, x: float, y: float,
                          color: tuple = (255, 80, 60)) -> None:
        self._death_rings.append({
            "x": x, "y": y, "radius": 10.0, "life": 1.0, "color": color,
        })

    def _spawn_muzzle_flash(self, x: float, y: float) -> None:
        self._muzzle_flashes.append({"x": x, "y": y, "timer": 0.08, "max_timer": 0.08})

    def _spawn_psi_wave(self, x: float, y: float) -> None:
        for i in range(3):
            self._psi_waves.append({
                "x": x, "y": y, "radius": 8.0 + i * 14,
                "life": 1.0, "delay": i * 0.08, "active": (i == 0),
            })

    def _snd(self) -> "SoundManager":
        return SoundManager.get()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.map_index is None:
            if self._handle_map_room_click(x, y):
                return
            return

        # Pause menu button clicks
        if self._paused:
            from game.ui.screens.battle_hud import PAUSE_RESUME, PAUSE_SETTINGS, PAUSE_ABANDON
            for key, (left, bottom, right, top) in self._pause_buttons:
                if left <= x <= right and bottom <= y <= top:
                    if key == PAUSE_RESUME:
                        self._paused = False
                    elif key == PAUSE_SETTINGS:
                        self._paused = False
                        from game.ui.screens.settings_screen import SettingsView
                        self.window.show_view(SettingsView(self.game_state))
                    elif key == PAUSE_ABANDON:
                        self._paused = False
                        from game.ui.screens.management_screen import ManagementView
                        mgmt = ManagementView(self.game_state)
                        mgmt.setup()
                        mgmt.active_tab = "squad"
                        self.window.show_view(mgmt)
                    return
            return

        self.last_input_mode = "controller" if button in (1, 2, 4, 5, 6, 7) else "keyboard_mouse"
        if self.pending_end_turn_confirmation:
            self.pending_end_turn_confirmation = False
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
                    self._load_battle_map(idx)
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
        guidance = compute_next_action(self.game_state, "battle")
        help_lines = [f"Next Step: {guidance.text}"] + _help_lines_for_view(self.game_state, "battle")
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

    def _setup_special_objectives(self) -> None:
        """Flag an assassination target or set defend turn count from mission template."""
        obj_type = getattr(self.mission, "objective_type", "") if self.mission else ""
        if obj_type == "assassination" and self.enemy_units:
            # Pick the highest-subtype enemy as the target
            priority = {"commander": 4, "elite": 3, "heavy": 2, "grunt": 1}
            self._assassination_target = max(
                self.enemy_units,
                key=lambda u: priority.get(u.enemy_subtype, 0),
            )
        elif obj_type == "defend" and self.mission:
            self._defend_turns_needed = max(4, (self.mission.duration_days or 1) * 4)

    def _handle_deployment_key(self, key: int) -> None:
        """Process arrow/tab/enter input during the pre-battle deployment phase."""
        if key == arcade.key.TAB:
            self._deploy_cursor = (self._deploy_cursor + 1) % max(1, len(self.player_units))
            return
        if key in (arcade.key.ENTER, arcade.key.RETURN):
            self._deploying = False
            self.combat_log_messages.append("Squad deployed — battle begins!")
            self._snd().play("sfx_deploy")
            return
        if not self.player_units or self._deploy_cursor >= len(self.player_units):
            return
        unit = self.player_units[self._deploy_cursor]
        dx = dy = 0
        if key == arcade.key.LEFT:
            dx = -32
        elif key == arcade.key.RIGHT:
            dx = 32
        elif key == arcade.key.UP:
            dy = 32
        elif key == arcade.key.DOWN:
            dy = -32
        if dx or dy:
            _DEPLOY_ZONE_H = 128
            ww = getattr(self.window, "width", 1280)
            nx = max(16, min(ww - 16, unit.position[0] + dx))
            ny = max(16, min(_DEPLOY_ZONE_H - 16, unit.position[1] + dy))
            unit.position = (nx, ny)
            if unit.sprite:
                unit.sprite.center_x = nx
                unit.sprite.center_y = ny

    def _log_move(self, unit: "Unit") -> None:
        name = (
            unit.character.name if unit.character
            else unit.spec_ops_asset.name if unit.spec_ops_asset
            else unit.unit_type
        )
        self.combat_log_messages.append(f"{name} moved → {unit.position}")

    def _set_action_aftermath(
        self,
        *,
        action_label: str,
        damage: int = 0,
        status_applied: str | None = None,
        suppression_created: bool = False,
    ) -> None:
        self._aftermath_line = build_action_aftermath_line(
            action_label=action_label,
            damage=damage,
            status_applied=status_applied,
            suppression_created=suppression_created,
        )
        self._aftermath_timer = 2.2

    def on_update(self, delta_time: float):
        self._battle_elapsed = getattr(self, "_battle_elapsed", 0.0) + delta_time
        if self.map_index is None:
            step_room_ui(self.room_ui, delta_time)
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.attack_line = None
        # Fade attack flash
        if self._flash_alpha > 0:
            self._flash_alpha = max(0, self._flash_alpha - int(delta_time * 480))
        if self._aftermath_timer > 0:
            self._aftermath_timer = max(0.0, self._aftermath_timer - delta_time)
        # Tick floating damage numbers
        self.damage_popups = [
            {**p, "age": p["age"] + delta_time}
            for p in self.damage_popups
            if p["age"] + delta_time < p["max_age"]
        ]
        # Tick VFX
        import math as _m, random as _r
        for p in self.particles:
            p["x"] += p["vx"] * delta_time
            p["y"] += p["vy"] * delta_time
            p["vy"] -= 300 * delta_time
            p["life"] -= 0.055 + 0.015 * delta_time * 60
        self.particles = [p for p in self.particles if p["life"] > 0]
        for uid in list(self._unit_flashes):
            self._unit_flashes[uid]["timer"] -= delta_time
            if self._unit_flashes[uid]["timer"] <= 0:
                del self._unit_flashes[uid]
        for ring in self._death_rings:
            ring["radius"] += 130 * delta_time
            ring["life"] -= 1.3 * delta_time
        self._death_rings = [r for r in self._death_rings if r["life"] > 0]
        for mf in self._muzzle_flashes:
            mf["timer"] -= delta_time
        self._muzzle_flashes = [m for m in self._muzzle_flashes if m["timer"] > 0]
        for wave in self._psi_waves:
            if wave.get("delay", 0) > 0:
                wave["delay"] -= delta_time
                wave["active"] = wave["delay"] <= 0
            elif wave.get("active"):
                wave["radius"] += 160 * delta_time
                wave["life"] -= 1.5 * delta_time
        self._psi_waves = [w for w in self._psi_waves if w["life"] > 0]
        # Decay screen shake
        if self._shake_intensity > 0.4:
            self._shake_intensity *= 0.72
        else:
            self._shake_intensity = 0.0
        # Intro timer
        if self._intro_active:
            self._intro_timer -= delta_time
            if self._intro_timer <= 0:
                self._intro_active = False
        # ── Refresh cover bonuses for all living units ──────────────────
        cover_nodes = getattr(self, "cover_nodes", [])
        if cover_nodes:
            from game.cover_system import cover_defense_bonus
            for unit in self.player_units + self.enemy_units:
                unit.in_cover_bonus = cover_defense_bonus(unit, cover_nodes)
