"""Enhanced Post-Battle Debrief Screen (Phase 2-A03).

Two-panel layout:
  Left  — Per-agent performance (damage dealt/taken, kills, AP used)
  Right — Objectives outcome, rewards, stress changes, narrative lines

Replaces the thin single-line end-screen with a structured after-action report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import arcade

from game.ui import palette
from game.ui.panels import draw_panel

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
    consequences = list(mission.success_consequences if victory else mission.failure_consequences)
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
    if isinstance(debrief_raw, dict):
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
    narrative_lines.extend(_consequence_text(consequence) for consequence in consequences)

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
        agent_rows.append(
            {
                "name": stat.name,
                "role": stat.role,
                "nickname": getattr(character, "nickname", "") if character else "",
                "reputation": list(getattr(character, "reputation", [])) if character else [],
                "kills": stat.kills,
                "damage_dealt": stat.damage_dealt,
                "damage_taken": stat.damage_taken,
                "stress_delta": stat.stress_delta,
                "injuries": list(stat.injuries),
                "xp_gained": stat.xp_gained,
                "status": "KIA" if stat.kia else "ACTIVE",
            }
        )

    return {
        "objective_result": "All objectives completed" if victory else "Mission objectives failed",
        "outcome": "victory" if victory else "defeat",
        "rewards": [
            f"Credits: +{getattr(mission, 'fund_reward', 0) if victory and mission else 0}",
            f"Duration: {getattr(mission, 'duration_days', 0) if mission else 0}d",
        ],
        "agent_rows": agent_rows,
        "triggered_complications": (
            [triggered_complication.trigger_text] if triggered_complication is not None else []
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
    consequences = _applied_consequences(mission, victory, triggered_complication)
    district = getattr(game_state, "district", None)
    lines: list[str] = []
    if district is not None:
        lines.append(
            "City pressure: "
            f"stability {getattr(district, 'stability', '?')}, "
            f"unrest {getattr(district, 'unrest', '?')}, "
            f"media heat {getattr(district, 'media_heat', '?')}"
        )

    faction = None
    if mission is not None and hasattr(game_state, "get_faction"):
        faction = game_state.get_faction(mission.target_faction)
    if faction is not None:
        lines.append(
            f"Faction {faction.name}: hostility {faction.hostility_to_player}, "
            f"influence {faction.influence}, legitimacy {faction.public_legitimacy}"
        )

    gained_tags: list[str] = []
    for consequence in consequences:
        gained_tags.extend(_tag_names(getattr(consequence, "tags", [])))
    if not gained_tags and district is not None:
        gained_tags = _tag_names(getattr(district, "tags", []))[-3:]
    lines.append(f"Tags gained: {', '.join(gained_tags) if gained_tags else 'none'}")

    scars: list[str] = []
    for character in getattr(game_state, "characters", []) or []:
        for scar in getattr(character, "temporary_scars", []) or []:
            label = (
                scar.get("title")
                or scar.get("name")
                or scar.get("label")
                or scar.get("type")
                or "scar"
            )
            scars.append(f"{character.name}: {label}")
    lines.append(f"Agent scars: {', '.join(scars[:3]) if scars else 'none'}")

    summary = build_battle_debrief_summary(
        game_state,
        victory,
        mission,
        agent_stats,
        triggered_complication,
    )
    rewards = ", ".join(str(line) for line in summary["rewards"])
    lines.append(f"Rewards: {rewards}")

    unavailable = list(getattr(game_state, "unavailable_mission_ids", []) or [])
    lines.append(
        "Unavailable missions: "
        + (", ".join(str(mid) for mid in unavailable[:3]) if unavailable else "none")
    )

    campaign = getattr(game_state, "campaign", None)
    discovered = list(getattr(campaign, "discovered_intel", []) or []) if campaign else []
    lines.append(
        "Intel unlocks: "
        + (", ".join(str(fid) for fid in discovered[-3:]) if discovered else "none")
    )
    if campaign is not None:
        world = getattr(campaign, "world", None)
        lines.append(
            f"Campaign: act {campaign.current_act} progress {campaign.act_progress}/{campaign.missions_required}; "
            f"Hungry Tide {getattr(world, 'hungry_tide_progress', 0)}%; "
            f"New York {getattr(world, 'new_york_status', 'unknown')}"
        )

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
                    self._portrait_cache[stat.portrait_path] = arcade.load_texture(stat.portrait_path)
                except Exception:
                    self._portrait_cache[stat.portrait_path] = None

    def on_draw(self) -> None:
        self.clear()
        w, h = self.window.width, self.window.height
        self._draw_header(w, h)
        self._draw_left_panel(w, h)
        self._draw_right_panel(w, h)
        self._draw_footer(w, h)

    def _draw_header(self, w: int, h: int) -> None:
        hh = 54
        outcome_col = palette.TACTICAL_GREEN if self.victory else palette.DANGER
        outcome_label = "MISSION COMPLETE" if self.victory else "MISSION FAILED"
        arcade.draw_lrbt_rectangle_filled(0, w, h - hh, h, (0, 0, 0, 220))
        arcade.draw_line(0, h - hh, w, h - hh, outcome_col, 3)
        arcade.draw_line(0, h, 20, h - 20, outcome_col, 2)
        arcade.draw_text(
            "AFTER-ACTION REPORT",
            20, h - hh // 2,
            palette.MUTED_TEXT, font_size=11, bold=True,
            anchor_y="center",
        )
        arcade.draw_text(
            outcome_label,
            w // 2, h - hh // 2,
            outcome_col, font_size=18, bold=True,
            anchor_x="center", anchor_y="center",
        )
        title = self.mission.title.upper() if self.mission else "UNKNOWN MISSION"
        arcade.draw_text(
            title,
            w - 20, h - hh // 2,
            palette.MUTED_TEXT, font_size=10,
            anchor_x="right", anchor_y="center",
        )

    def _draw_left_panel(self, w: int, h: int) -> None:
        panel_l = 20
        panel_b = 80
        panel_w = w // 2 - 30
        panel_h = h - 150

        draw_panel(panel_l, panel_b, panel_w, panel_h, "SQUAD PERFORMANCE")

        # Column headers
        col_y = panel_b + panel_h - 46
        headers = [("AGENT", 14), ("DEALT", 160), ("TAKEN", 210), ("KILLS", 260), ("XP", 305), ("STATUS", 340)]
        for label, ox in headers:
            arcade.draw_text(label, panel_l + ox, col_y, palette.MUTED_TEXT, font_size=9, bold=True)
        arcade.draw_line(panel_l + 14, col_y - 8, panel_l + panel_w - 14, col_y - 8, palette.PANEL_BORDER_MUTED, 1)

        row_y = col_y - 24
        row_h = 52

        for stat in self.agent_stats[:6]:
            if row_y - row_h < panel_b + 8:
                break
            bg_col = (40, 10, 10, 160) if stat.kia else (12, 24, 36, 160)
            arcade.draw_lrbt_rectangle_filled(panel_l + 14, panel_l + panel_w - 14, row_y - row_h, row_y, bg_col)

            # Portrait thumbnail
            portrait = self._portrait_cache.get(stat.portrait_path or "")
            if portrait:
                arcade.draw_texture_rect(portrait, arcade.LBWH(panel_l + 16, row_y - row_h + 4, 40, 44))
            else:
                arcade.draw_lrbt_rectangle_filled(panel_l + 16, panel_l + 56, row_y - row_h + 4, row_y - 4,
                                                  palette.ACTION_BUTTON_FILL)

            name_col = palette.DANGER if stat.kia else palette.TEXT
            arcade.draw_text(stat.name[:12], panel_l + 62, row_y - 14, name_col, font_size=10, bold=True)
            arcade.draw_text(stat.role.upper()[:8], panel_l + 62, row_y - 28, palette.MUTED_TEXT, font_size=8)

            arcade.draw_text(str(stat.damage_dealt),  panel_l + 160, row_y - 20, palette.WARNING, font_size=11, bold=True, anchor_x="center")
            arcade.draw_text(str(stat.damage_taken),  panel_l + 210, row_y - 20, palette.DANGER,  font_size=11, bold=True, anchor_x="center")
            arcade.draw_text(str(stat.kills),         panel_l + 260, row_y - 20, palette.TACTICAL_GREEN, font_size=11, bold=True, anchor_x="center")
            arcade.draw_text(str(stat.xp_gained),  panel_l + 305, row_y - 20, palette.ACCENT,  font_size=11, bold=True, anchor_x="center")

            if stat.kia:
                arcade.draw_text("KIA", panel_l + 350, row_y - 20, palette.DANGER, font_size=10, bold=True)
            else:
                stress_s = f"+{stat.stress_delta}%" if stat.stress_delta > 0 else f"{stat.stress_delta}%"
                stress_col = palette.DANGER if stat.stress_delta > 10 else palette.WARNING if stat.stress_delta > 0 else palette.TACTICAL_GREEN
                arcade.draw_text(stress_s, panel_l + 350, row_y - 20, stress_col, font_size=9)
                if stat.injuries:
                    arcade.draw_text(str(stat.injuries[0])[:24], panel_l + 350, row_y - 34, palette.DANGER, font_size=8)

            row_y -= row_h + 4

    def _draw_right_panel(self, w: int, h: int) -> None:
        panel_l = w // 2 + 10
        panel_b = 80
        panel_w = w // 2 - 30
        panel_h = h - 150

        draw_panel(panel_l, panel_b, panel_w, panel_h, "MISSION OUTCOME")

        y = panel_b + panel_h - 50
        summary = build_battle_debrief_summary(
            self.game_state,
            self.victory,
            self.mission,
            self.agent_stats,
            self.triggered_complication,
        )

        # Objective result
        outcome_col = palette.TACTICAL_GREEN if self.victory else palette.DANGER
        arcade.draw_text("OBJECTIVES", panel_l + 14, y, outcome_col, font_size=10, bold=True)
        y -= 18
        arcade.draw_text(
            str(summary["objective_result"]),
            panel_l + 14, y, outcome_col, font_size=10,
        )
        y -= 30

        # Rewards
        if self.mission:
            arcade.draw_text("REWARDS", panel_l + 14, y, palette.RESOURCE, font_size=10, bold=True)
            y -= 18
            for line in summary["rewards"]:
                arcade.draw_text(line, panel_l + 14, y, palette.TEXT, font_size=9)
                y -= 15
            y -= 10

        consequence_summary = build_consequence_summary_lines(
            self.game_state,
            self.victory,
            self.mission,
            self.agent_stats,
            self.triggered_complication,
        )
        if consequence_summary:
            arcade.draw_text("CONSEQUENCE SUMMARY", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
            y -= 18
            for line in consequence_summary[:5]:
                arcade.draw_text(str(line)[:72], panel_l + 14, y, palette.MUTED_TEXT, font_size=8)
                y -= 13
            y -= 6

        triggered = list(summary["triggered_complications"])
        if triggered:
            arcade.draw_text("TRIGGERED COMPLICATIONS", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
            y -= 18
            for line in triggered[:2]:
                arcade.draw_text(str(line)[:68], panel_l + 14, y, palette.WARNING, font_size=9)
                y -= 15
            y -= 6

        campaign_lines = list(summary["faction_changes"])[:2] + list(summary["district_changes"])[:2]
        if campaign_lines:
            arcade.draw_text("FACTION / DISTRICT CHANGES", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
            y -= 18
            for line in campaign_lines[:4]:
                arcade.draw_text(str(line)[:68], panel_l + 14, y, palette.MUTED_TEXT, font_size=9)
                y -= 15
            y -= 6

        # Narrative debrief lines
        debrief_raw = getattr(self.game_state, "latest_mission_debrief", None)
        if debrief_raw and isinstance(debrief_raw, dict):
            arcade.draw_text("DEBRIEF", panel_l + 14, y, palette.ACCENT, font_size=10, bold=True)
            y -= 18
            # Full narrative lines (tone-coloured sentences from DebriefReport.lines)
            _tone_colors = {
                "tense":   palette.WARNING,
                "loss":    palette.DANGER,
                "relief":  palette.TACTICAL_GREEN,
                "heroic":  (255, 215, 60),
                "neutral": palette.TEXT,
            }
            for line_dict in debrief_raw.get("lines", [])[:5]:
                if not isinstance(line_dict, dict):
                    continue
                text = str(line_dict.get("text", ""))
                tone = str(line_dict.get("tone", "neutral"))
                col = _tone_colors.get(tone, palette.TEXT)
                # Truncate + wrap tight in panel
                arcade.draw_text(
                    f"  {text[:68]}",
                    panel_l + 14, y,
                    col, font_size=9,
                    width=panel_w - 28, multiline=False,
                )
                y -= 15
            # Fallback: single-field strings
            for key, label in [("decision_key", "Decision"), ("risk_taken", "Risk"), ("heroic_action", "Heroics")]:
                text = debrief_raw.get(key, "")
                if text:
                    arcade.draw_text(f"{label}: {str(text)[:55]}", panel_l + 14, y,
                                     palette.MUTED_TEXT, font_size=9)
                    y -= 14
            y -= 8

        consequence_lines = list(summary["narrative_consequences"])
        if consequence_lines:
            arcade.draw_text("NARRATIVE CONSEQUENCES", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
            y -= 18
            for line in consequence_lines[:3]:
                arcade.draw_text(str(line)[:72], panel_l + 14, y, palette.MUTED_TEXT, font_size=9)
                y -= 15
            y -= 6

        # RPG links (stress/progression)
        if debrief_raw and isinstance(debrief_raw, dict):
            rpg = debrief_raw.get("rpg_links", "")
            if rpg:
                arcade.draw_text("CONSEQUENCES", panel_l + 14, y, palette.WARNING, font_size=10, bold=True)
                y -= 18
                rpg_lines = rpg if isinstance(rpg, list) else [rpg]
                for line in rpg_lines[:2]:
                    arcade.draw_text(
                        str(line)[:72],
                        panel_l + 14, y,
                        palette.MUTED_TEXT, font_size=9,
                        width=panel_w - 28, multiline=True,
                    )
                    y -= 15
                y -= 8

        # Aftermath lines from game_state
        aftermath = getattr(self.game_state, "latest_agent_aftermath", [])
        if aftermath:
            arcade.draw_text("AGENT STATUS", panel_l + 14, y, palette.ACCENT, font_size=10, bold=True)
            y -= 18
            for line in aftermath[:4]:
                arcade.draw_text(str(line)[:66], panel_l + 14, y, palette.TEXT, font_size=9)
                y -= 15

    def _draw_footer(self, w: int, h: int) -> None:
        fh = 68
        arcade.draw_lrbt_rectangle_filled(0, w, 0, fh, (0, 0, 0, 200))
        arcade.draw_line(0, fh, w, fh, palette.PANEL_BORDER, 2)

        bw, bh = 220, 44
        bx = (w - bw) // 2
        by = (fh - bh) // 2
        col = palette.TACTICAL_GREEN if self.victory else palette.WARNING
        arcade.draw_lrbt_rectangle_filled(bx, bx + bw, by, by + bh, (16, 40, 24, 230))
        arcade.draw_line(bx, by + bh, bx + bw, by + bh, col, 2)
        arcade.draw_text(
            "CONTINUE  [Enter]",
            bx + bw // 2, by + bh // 2,
            col, font_size=13, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self._continue_rect = (bx, by, bx + bw, by + bh)

    def on_key_press(self, key, modifiers) -> None:
        if key in (arcade.key.RETURN, arcade.key.ENTER, arcade.key.ESCAPE, arcade.key.SPACE):
            self._go_to_management()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        if self._continue_rect:
            l, b, r, t = self._continue_rect
            if l <= x <= r and b <= y <= t:
                self._go_to_management()

    def _go_to_management(self) -> None:
        from game.ui.screens.management_screen import ManagementView
        mgmt = ManagementView(self.game_state)
        mgmt.setup()
        mgmt.active_tab = "squad"
        self.window.show_view(mgmt)
