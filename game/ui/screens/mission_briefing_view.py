"""Mission Briefing Screen — shown before BattleView launches.

Displays mission objectives, enemy intel, map thumbnail, squad roster,
and emotional impact hint. Player chooses DEPLOY or ABORT.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from game.agent_readiness import estimate_mission_stress, projected_stress
from game.battle_maps import select_battle_map_entry
from game.deployment import selected_deployable_agents
from game.narrative.mission_briefing_conventions import translate_legacy_briefing_text
from game.narrative.agent_memory import latest_tactical_memory
from game.narrative.temporary_scars import build_temporary_scar_summary

if TYPE_CHECKING:
    from game.character import Character
    from game.gamestate import GameState
    from game.management.spec_ops_assets import SpecOpsAsset
    from game.mission_templates import MissionTemplate


def _complication_label(complication: object) -> str:
    if isinstance(complication, str):
        return complication
    return (
        getattr(complication, "trigger_text", None)
        or getattr(complication, "name", None)
        or str(complication)
    )


def mission_tag_label(tag: object) -> str:
    """Turn tag objects and legacy dictionaries into compact player-facing text."""
    if isinstance(tag, dict):
        value = tag.get("name") or tag.get("key") or tag.get("label") or ""
    elif isinstance(tag, str):
        value = tag
    else:
        value = getattr(tag, "name", None) or getattr(tag, "key", None) or ""
    cleaned = str(value).strip().replace("_", " ")
    return cleaned.title() if cleaned else "Unknown"


def pressure_label(pressure: object) -> str:
    """Format pressure effects as player-facing consequences, not raw data."""
    if isinstance(pressure, dict):
        parts = [
            f"{str(key).replace('_', ' ').upper()} {int(value):+d}"
            for key, value in pressure.items()
            if isinstance(value, (int, float))
        ]
        return " | ".join(parts) if parts else "STABLE"
    return f"{pressure}/10"


def _emotional_impact_text(mission: "MissionTemplate") -> str:
    hint = getattr(mission, "emotional_impact_hint", None)
    if isinstance(hint, dict):
        return translate_legacy_briefing_text(
            hint.get("short_text")
            or hint.get("text")
            or "No unusual emotional impact forecast."
        )
    return "No unusual emotional impact forecast."


def selected_support_assets(game_state: "GameState") -> list["SpecOpsAsset"]:
    """Return selected deployable support assets in stable roster order."""
    selected_ids = set(getattr(game_state, "selected_asset_ids", []) or [])
    return [
        asset
        for asset in getattr(game_state, "spec_ops_assets", []) or []
        if asset.id in selected_ids
    ]


def expected_stress_band(agents: list["Character"], mission: "MissionTemplate") -> str:
    """Build the pre-battle projected stress band shown in the briefing."""
    baseline = estimate_mission_stress(mission)
    if not agents:
        return f"+{baseline} mission pressure; no squad selected"
    projected = [projected_stress(agent, mission) for agent in agents]
    return f"{min(projected)}-{max(projected)} projected stress; +{baseline} mission pressure"


def reward_preview(mission: "MissionTemplate", assets: list["SpecOpsAsset"]) -> str:
    """Summarize mission funds after selected support asset deployment costs."""
    mission_reward = int(getattr(mission, "fund_reward", 0))
    deploy_cost = sum(max(0, int(getattr(asset, "deploy_cost", 0))) for asset in assets)
    if deploy_cost <= 0:
        return f"Funds +{mission_reward}"
    return f"Funds +{mission_reward}; assets -{deploy_cost}; net {mission_reward - deploy_cost}"


def build_mission_briefing_facts(
    game_state: "GameState", mission: "MissionTemplate"
) -> dict[str, object]:
    """Collect the Wave 6 briefing fields without depending on Arcade rendering."""
    agents = selected_deployable_agents(
        getattr(game_state, "characters", []),
        getattr(game_state, "selected_agent_names", []),
    )
    assets = selected_support_assets(game_state)
    try:
        map_entry = select_battle_map_entry(mission)
        map_thumbnail = (
            str(map_entry.path)
            if map_entry is not None
            else "mission-matched tactical map"
        )
    except Exception:
        map_thumbnail = "mission-matched tactical map"
    signal_array = game_state.has_base_upgrade("signal_array")
    hostile_count = max(0, int(getattr(mission, "starting_enemy_count", 0)))
    return {
        "title": mission.title,
        "objective": mission.objective_text,
        "target_faction": mission.target_faction,
        "district": mission.district,
        "risk_level": mission.risk_level,
        "expected_stress_band": expected_stress_band(agents, mission),
        "emotional_impact": _emotional_impact_text(mission),
        "complications": [
            _complication_label(complication)
            for complication in getattr(mission, "possible_complications", [])
        ],
        "map_thumbnail": map_thumbnail,
        "squad_roster": [agent.name for agent in agents],
        "recent_tactical_memories": [
            f"{agent.name}: {memory}"
            for agent in agents
            if (memory := latest_tactical_memory(getattr(agent, "history", [])))
        ],
        "temporary_scar_summary": [
            f"{agent.name}: {line}"
            for agent in agents
            for line in build_temporary_scar_summary(agent)
            if line != "Temporary scars: none"
        ],
        "selected_support_assets": [asset.name for asset in assets],
        "reward_preview": reward_preview(mission, assets),
        "mission_intel_level": 1 if signal_array else 0,
        "hostile_estimate": (
            f"{hostile_count} hostiles // {mission.target_faction} doctrine"
            if signal_array else "Limited — install Strategic Signal Array"
        ),
        "actions": ["DEPLOY", "ABORT"],
    }


class MissionBriefingView(arcade.View):
    """Full-screen mission briefing shown between management and battle launch."""

    def __init__(self, game_state: "GameState", mission: "MissionTemplate") -> None:
        super().__init__()
        self.game_state = game_state
        self.mission = mission
        self._scene_art = None
        self._renderer = None
        self._elapsed = 0.0
        self._facts = build_mission_briefing_facts(game_state, mission)
        self._hits = []
        self._map_texture: arcade.Texture | None = None
        self._deploy_rect: tuple[int, int, int, int] | None = None
        self._abort_rect: tuple[int, int, int, int] | None = None

    def on_show_view(self) -> None:
        arcade.set_background_color((4, 10, 18))
        self._load_assets()
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import SettingsState

        sm = SoundManager.get()
        sm.ensure_loaded()
        from game.ui.screens.settings_screen import load_settings as _ls

        sm.configure_from_settings(_ls())
        sm.play_music("music_briefing", loop=True)

    def _load_assets(self) -> None:
        from game.ui.components.squad_mission import mission_art_path

        self._scene_art = mission_art_path(self.mission)
        self._facts = build_mission_briefing_facts(self.game_state, self.mission)
        self._map_texture = None
        # Match the briefing thumbnail to the mission's map environment.
        try:
            map_entry = select_battle_map_entry(self.mission)
            if map_entry is not None:
                self._map_texture = arcade.load_texture(map_entry.path)
        except Exception:
            pass

    def on_draw(self) -> None:
        self.clear()
        if self._renderer is None:
            from game.ui.components.mission_briefing import MissionBriefingRenderer

            self._renderer = MissionBriefingRenderer()
        self._renderer.draw(self, self.window.width, self.window.height)

    def on_update(self, delta_time):
        self._elapsed += delta_time
        if self._renderer is not None:
            self._renderer.update(delta_time)

    def on_key_press(self, key, modifiers) -> None:
        renderer = self._renderer
        if renderer and renderer.map_open:
            if key == arcade.key.ESCAPE:
                renderer.map_open = False
            return
        if key in (arcade.key.RETURN, arcade.key.ENTER):
            self._launch_battle()
        elif key == arcade.key.ESCAPE:
            self._abort()
        elif renderer and key in (arcade.key.PAGEDOWN, arcade.key.PAGEUP):
            renderer.scroll(renderer.focus, 1 if key == arcade.key.PAGEDOWN else -1)

    def on_mouse_motion(self, x, y, dx, dy):
        if self._renderer:
            self._renderer.motion(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._renderer and not self._renderer.map_open:
            self._renderer.motion(x, y)
            self._renderer.scroll(self._renderer.focus, -int(scroll_y))

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for hit in reversed(self._hits):
            if not hit.contains(x, y):
                continue
            if hit.action == "deploy":
                self._launch_battle()
            elif hit.action == "abort":
                self._abort()
            elif hit.action == "map":
                self._renderer.map_open = True
            elif hit.action == "close_map":
                self._renderer.map_open = False
            elif hit.action == "scroll":
                self._renderer.scroll(*hit.data)
            return

    def _launch_battle(self) -> None:
        from game.ui.screens.godot_combat_handoff_view import open_mission_combat

        open_mission_combat(self.window, self.game_state, self.mission)

    def _abort(self) -> None:
        from game.ui.screens.management_screen import ManagementView

        mgmt = ManagementView(self.game_state)
        mgmt.setup()
        mgmt.active_tab = "squad"
        self.window.show_view(mgmt)
