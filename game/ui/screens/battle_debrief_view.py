"""Post-battle report: shared squad cards, consequences and full paginated dossiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import arcade

if TYPE_CHECKING:
    from game.consequences import Consequence
    from game.gamestate import GameState
    from game.narrative.debrief import DebriefReport
    from game.mission_templates import MissionComplication
    from game.mission_templates import MissionTemplate


@dataclass
class AgentDebriefStat:
    """Per-agent performance snapshot collected during battle."""

    name: str
    role: str
    portrait_path: str | None
    damage_dealt: int = 0
    damage_taken: int = 0
    actions_used: int = 0
    kills: int = 0
    kia: bool = False
    stress_delta: int = 0
    xp_gained: int = 0
    injuries: list[str] = field(default_factory=list)
    hp_remaining: int | None = None
    max_hp_at_extraction: int | None = None


def _consequence_text(consequence: "Consequence") -> str:
    text = str(getattr(consequence, "narrative_text", "") or "").strip()
    if text:
        return text
    effects = getattr(consequence, "mechanical_effects", {}) or {}
    return _effect_summary(consequence) if effects else "No explicit consequence text."


def _effect_summary(consequence: "Consequence") -> str:
    effects = getattr(consequence, "mechanical_effects", {}) or {}
    if not effects:
        return f"severity {getattr(consequence, 'severity', 1)}"
    parts = []
    for key, value in effects.items():
        if isinstance(value, (int, float)):
            parts.append(f"{key} {value:+}")
        else:
            parts.append(f"{key} {value}")
    return ", ".join(parts)


def _applied_consequences(
    mission: "MissionTemplate | None",
    victory: bool,
    triggered_complication: "MissionComplication | None",
) -> list["Consequence"]:
    if mission is None:
        return []
    consequences = list(
        mission.success_consequences if victory else mission.failure_consequences
    )
    if triggered_complication is not None:
        consequences.append(triggered_complication.consequence)
    return consequences


def build_battle_debrief_summary(
    game_state: "GameState",
    victory: bool,
    mission: "MissionTemplate | None",
    agent_stats: list[AgentDebriefStat],
    triggered_complication: "MissionComplication | None" = None,
) -> dict[str, object]:
    """Build a render-independent post-battle report for UI and regression tests."""
    consequences = _applied_consequences(mission, victory, triggered_complication)
    debrief_raw = getattr(game_state, "latest_mission_debrief", {}) or {}
    narrative_lines: list[str] = []
    tactical_moments: list[str] = []
    if isinstance(debrief_raw, dict):
        tactical_moments = [
            moment["text"]
            for moment in debrief_raw.get("tactical_moments", [])
            if isinstance(moment, dict) and isinstance(moment.get("text"), str) and moment["text"].strip()
        ]
        for line_dict in debrief_raw.get("lines", []):
            if isinstance(line_dict, dict) and line_dict.get("text"):
                narrative_lines.append(str(line_dict["text"]))
        for key in ("decision_key", "risk_taken", "heroic_action"):
            if debrief_raw.get(key):
                narrative_lines.append(str(debrief_raw[key]))
        for award in debrief_raw.get("reputation_awards", []):
            if not isinstance(award, dict):
                continue
            agent = str(award.get("agent_name", "Unknown"))
            tag = str(award.get("tag", "reputation"))
            nickname = str(award.get("nickname", ""))
            reason = str(award.get("reason", "standout mission event"))
            label = f" '{nickname}'" if nickname else ""
            narrative_lines.append(
                f"Reputation: {agent}{label} earned {tag} ({reason})."
            )
    narrative_lines.extend(
        _consequence_text(consequence) for consequence in consequences
    )

    agent_rows = []
    for stat in agent_stats:
        character = next(
            (
                candidate
                for candidate in getattr(game_state, "characters", [])
                if candidate.name == stat.name
            ),
            None,
        )
        status = "ACTIVE"
        if stat.kia:
            status = "KIA"
        elif character and character.recovery_turns > 0:
            status = "RECOVERY"
        elif stat.hp_remaining == 0:
            status = "DOWNED"
        agent_rows.append(
            {
                "name": stat.name,
                "role": stat.role,
                "nickname": getattr(character, "nickname", "") if character else "",
                "reputation": (
                    list(getattr(character, "reputation", [])) if character else []
                ),
                "kills": stat.kills,
                "damage_dealt": stat.damage_dealt,
                "damage_taken": stat.damage_taken,
                "stress_delta": stat.stress_delta,
                "injuries": list(stat.injuries),
                "xp_gained": stat.xp_gained,
                "status": status,
                "hp_remaining":stat.hp_remaining,
                "max_hp_at_extraction":stat.max_hp_at_extraction,
            }
        )

    external=debrief_raw.get("external_combat",{}) if isinstance(debrief_raw,dict) else {}
    rewards=debrief_raw.get("campaign_rewards") if isinstance(debrief_raw,dict) else None
    reward_lines=([f"{key.title()}: {value:+}" for key,value in rewards["resources"].items()]+
                  [f"Net funds: {rewards['net_funds_change']:+}",f"Duration: {getattr(mission,'duration_days',0)}d"]
                  if isinstance(rewards,dict) else None)
    objective_text=("Objective completed" if external.get("objective_completed") is True else
                    "Objective not completed" if external.get("objective_completed") is False else "Objective completion not reported")
    return {
        "objective_result": objective_text if external else (
            "All objectives completed" if victory else "Mission objectives failed"
        ),
        "outcome": external.get("outcome", "victory" if victory else "defeat"),
        "rewards": reward_lines if reward_lines is not None else [
            f"Credits: +{getattr(mission, 'fund_reward', 0) if victory and mission else 0}",
            f"Duration: {getattr(mission, 'duration_days', 0) if mission else 0}d",
        ],
        "agent_rows": agent_rows,
        "triggered_complications": (
            [triggered_complication.trigger_text]
            if triggered_complication is not None
            else []
        ),
        "faction_changes": [
            f"{consequence.affected_faction}: {_effect_summary(consequence)}"
            for consequence in consequences
            if getattr(consequence, "affected_faction", None)
        ],
        "district_changes": [
            f"{consequence.affected_district}: {_effect_summary(consequence)}"
            for consequence in consequences
            if getattr(consequence, "affected_district", None)
        ],
        "narrative_consequences": narrative_lines[:10],
        "tactical_moments": tactical_moments,
        "continue_action": "ManagementView",
    }


def _tag_names(tags: object) -> list[str]:
    if not tags:
        return []
    names = []
    for tag in tags:
        names.append(str(getattr(tag, "name", tag)))
    return names


def build_consequence_summary_lines(
    game_state: "GameState",
    victory: bool,
    mission: "MissionTemplate | None",
    agent_stats: list[AgentDebriefStat],
    triggered_complication: "MissionComplication | None" = None,
) -> list[str]:
    """Build compact post-resolution state changes for the debrief panel."""
    import re
    from game.campaign.intel_fragments import get_fragment

    def display_name(identifier):
        return re.sub(r"_d\d+_s\d+$", "", str(identifier)).replace("_", " ").title()

    def section(title, items):
        if items:
            if lines:
                lines.append("")
            lines.extend([title, *items])

    lines = []
    summary = build_battle_debrief_summary(game_state, victory, mission, agent_stats, triggered_complication)
    section("MISSION PAYOUT", summary["rewards"])
    district = getattr(game_state, "district", None)
    if district is not None:
        section("DISTRICT STATUS", [
            f"Stability {district.stability}  ·  Unrest {district.unrest}",
            f"Media attention {district.media_heat}",
        ])
    faction = game_state.get_faction(mission.target_faction) if mission is not None else None
    if faction is not None:
        section(faction.name.upper(), [
            f"Hostility {faction.hostility_to_player}  ·  Influence {faction.influence}",
            f"Public legitimacy {faction.public_legitimacy}",
        ])

    consequences = _applied_consequences(mission, victory, triggered_complication)
    effects = dict.fromkeys(display_name(tag) for consequence in consequences
                            for tag in _tag_names(consequence.tags))
    section("NEW DEVELOPMENTS", list(effects))
    section("COMPLICATIONS", summary["triggered_complications"])
    deployed = {stat.name for stat in agent_stats}
    scars = []
    for character in game_state.characters:
        if character.name in deployed:
            for scar in character.temporary_scars:
                label = scar.get("title") or scar.get("name") or scar.get("label")
                scars.append(f"{character.name} — {label or display_name(scar.get('type', 'scar'))}")
    section("OPERATIVE SCARS", scars)
    titles = {entry.id: entry.title for entry in game_state.mission_templates}
    section("UNAVAILABLE MISSIONS", [
        titles.get(mid, display_name(mid)) for mid in sorted(game_state.unavailable_mission_ids)
    ])
    campaign = getattr(game_state, "campaign", None)
    if campaign is not None:
        intel = [get_fragment(fid) for fid in campaign.discovered_intel[-3:]]
        section("RECENT INTELLIGENCE", [fragment.title for fragment in intel if fragment])
        world = campaign.world
        section("CAMPAIGN PROGRESS", [
            f"Act {campaign.current_act}  ·  {campaign.act_progress}/{campaign.missions_required} missions",
            f"Hungry Tide {world.hungry_tide_progress}%",
            f"New York — {display_name(world.new_york_status)}",
        ])
    return lines


class BattleDebriefView(arcade.View):
    """Full-screen post-battle debrief shown after end_battle resolves."""

    def __init__(
        self,
        game_state: "GameState",
        victory: bool,
        mission: "MissionTemplate | None",
        agent_stats: list[AgentDebriefStat],
        triggered_complication: "MissionComplication | None" = None,
    ) -> None:
        super().__init__()
        self.game_state = game_state
        self.victory = victory
        self.mission = mission
        self.agent_stats = agent_stats
        self.triggered_complication = triggered_complication
        self._continue_rect: tuple[int, int, int, int] | None = None
        self._portrait_cache: dict[str, arcade.Texture | None] = {}

    def on_show_view(self) -> None:
        arcade.set_background_color((4, 10, 18))
        self._load_portraits()
        from game.audio import SoundManager
        from game.ui.screens.settings_screen import SettingsState

        sm = SoundManager.get()
        sm.ensure_loaded()
        from game.ui.screens.settings_screen import load_settings as _ls

        sm.configure_from_settings(_ls())
        sm.play_music("music_debrief", loop=True)

    def _load_portraits(self) -> None:
        for stat in self.agent_stats:
            if stat.portrait_path and stat.portrait_path not in self._portrait_cache:
                try:
                    self._portrait_cache[stat.portrait_path] = arcade.load_texture(
                        stat.portrait_path
                    )
                except Exception:
                    self._portrait_cache[stat.portrait_path] = None

    def on_update(self, dt):
        self._elapsed = getattr(self, "_elapsed", 0.0) + dt
        if hasattr(self, "_visual_deck"):
            self._visual_deck.update(dt)

    def on_draw(self):
        self.clear()
        if not hasattr(self, "_visual_deck"):
            from game.ui.components.utilities.reports import ReportDeck

            self._visual_deck = ReportDeck()
        self._elapsed = getattr(self, "_elapsed", 0.0)
        self._visual_deck.debrief(self)

    def on_mouse_motion(self, x, y, dx, dy):
        if hasattr(self, "_visual_deck"):
            self._visual_deck.motion(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if hasattr(self, "_visual_deck"):
            for name, (_, _, rect) in self._visual_deck.capacities.items():
                if rect.contains(x, y):
                    self._visual_deck.turn_page(name, -1 if scroll_y > 0 else 1)
                    break

    def on_key_press(self, key, modifiers) -> None:
        if hasattr(self, "_visual_deck") and key in (
            arcade.key.TAB,
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.SPACE,
        ):
            result = self._visual_deck.keyboard(key)
            if result:
                if (
                    result is not True
                    and not self._visual_deck.activate(result)
                    and result.action == "continue"
                ):
                    self._go_to_management()
                return
        if key in (
            arcade.key.RETURN,
            arcade.key.ENTER,
            arcade.key.ESCAPE,
            arcade.key.SPACE,
        ):
            self._go_to_management()

    def on_mouse_press(self, x, y, button, modifiers):
        for hit in getattr(self, "_hits", []):
            if hit.contains(x, y):
                if not self._visual_deck.activate(hit) and hit.action == "continue":
                    self._go_to_management()
                return

    def _go_to_management(self) -> None:
        callback = getattr(self, "after_debrief", None)
        if callback is not None:
            self.after_debrief = None
            if callback():return
        if self.game_state.campaign.ending is not None:
            from game.ui.screens.campaign_ending_view import CampaignEndingView

            self.window.show_view(CampaignEndingView(self.game_state))
            return
        from game.ui.screens.management_screen import ManagementView

        mgmt = ManagementView(self.game_state)
        mgmt.setup()
        mgmt.active_tab = "squad"
        self.window.show_view(mgmt)
