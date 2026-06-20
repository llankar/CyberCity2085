"""Campaign panel — drawn inside the Intel room of ManagementView.

Shows: current act title, world state indicators, discovered intel fragments,
and a pending act-advance overlay when acts transition.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import arcade

from game.ui import palette
from game.ui.panels import draw_panel

if TYPE_CHECKING:
    from game.gamestate import GameState


_WORLD_LABELS = {
    "warsaw_status": {
        "open":                  ("WARSAW", "Open", palette.TACTICAL_GREEN),
        "coup_underway":         ("WARSAW", "Coup Active", palette.WARNING),
        "three_sevens_controlled": ("WARSAW", "3-7s Controlled", palette.DANGER),
    },
    "new_york_status": {
        "normal": ("NEW YORK", "Normal", palette.TACTICAL_GREEN),
        "alert":  ("NEW YORK", "Alert", palette.WARNING),
        "siege":  ("NEW YORK", "UNDER SIEGE", palette.DANGER),
    },
    "pharmacorp_secret": {
        "hidden":  ("PHARMACORP", "Secret Hidden", palette.MUTED_TEXT),
        "rumored": ("PHARMACORP", "Rumored", palette.WARNING),
        "exposed": ("PHARMACORP", "EXPOSED", palette.DANGER),
    },
    "ai_factions_status": {
        "unknown":   ("AI FACTIONS", "Unknown", palette.MUTED_TEXT),
        "suspected": ("AI FACTIONS", "Suspected", palette.WARNING),
        "confirmed": ("AI FACTIONS", "CONFIRMED", palette.DANGER),
    },
    "perfs_status": {
        "unknown":    ("PERFS", "Unknown", palette.MUTED_TEXT),
        "sighted":    ("PERFS", "Sighted", palette.WARNING),
        "understood": ("PERFS", "Origin Known", palette.DANGER),
    },
    "new_delhi_status": {
        "forbidden":  ("NEW DELHI", "Forbidden Zone", palette.MUTED_TEXT),
        "infiltrated": ("NEW DELHI", "Infiltrated", palette.WARNING),
        "revealed":   ("NEW DELHI", "Revealed", palette.ACCENT),
    },
}

from game.campaign.acts import ACT_TITLES
from game.campaign.intel_fragments import fragments_for_act, get_fragment
from game.campaign.story_missions import STORY_MISSIONS


def _status_text(field_name: str, value: str) -> str:
    labels = _WORLD_LABELS.get(field_name, {})
    entry = labels.get(value)
    return entry[1] if entry else str(value).replace("_", " ").title()


def _major_known_threats(game_state: "GameState") -> list[str]:
    world = game_state.campaign.world
    threats: list[str] = []
    if world.hungry_tide_progress > 0:
        threats.append(f"Hungry Tide at {world.hungry_tide_progress}%")
    if world.new_york_status != "normal":
        threats.append(f"New York {_status_text('new_york_status', world.new_york_status)}")
    if world.warsaw_status != "open":
        threats.append(f"Warsaw {_status_text('warsaw_status', world.warsaw_status)}")
    if world.pharmacorp_secret != "hidden":
        threats.append(f"Pharmacorp {_status_text('pharmacorp_secret', world.pharmacorp_secret)}")
    if world.ai_factions_status != "unknown":
        threats.append(f"AI factions {_status_text('ai_factions_status', world.ai_factions_status)}")
    if world.perfs_status != "unknown":
        threats.append(f"PERFs {_status_text('perfs_status', world.perfs_status)}")
    return threats or ["No major known threats confirmed"]


def _unresolved_global_events(game_state: "GameState") -> list[str]:
    current_day = int(getattr(game_state.calendar, "current_day", 1))
    lines: list[str] = []
    for event in getattr(game_state, "active_events", []) or []:
        title = getattr(event, "title", "Unresolved event")
        severity = getattr(event, "severity", "?")
        if hasattr(event, "days_remaining"):
            remaining = event.days_remaining(current_day)
            lines.append(f"{title} (severity {severity}, {remaining}d left)")
        else:
            lines.append(f"{title} (severity {severity})")
    if not lines:
        seen = list(getattr(game_state.campaign, "act_triggers_seen", []) or [])
        lines = [f"Trigger seen: {trigger}" for trigger in seen[-3:]]
    return lines or ["No unresolved global events"]


def build_hungry_tide_summary(game_state: "GameState") -> dict[str, object]:
    """Summarize Starver/Hungry Tide pressure for the Intel room."""
    world = game_state.campaign.world
    progress = max(0, min(100, int(world.hungry_tide_progress)))
    if progress >= 80:
        threat_level = "critical"
        affected_regions = ["Badlands", "Atlantic corridor", "New York perimeter"]
        expected_new_york_impact = "siege imminent or active"
        consequence_if_ignored = "New York falls into open siege and Starver pressure spikes worldwide."
    elif progress >= 50:
        threat_level = "high"
        affected_regions = ["Badlands", "Atlantic corridor"]
        expected_new_york_impact = "major assault forming"
        consequence_if_ignored = "The Tide reaches New York with fewer warning windows and higher civilian losses."
    elif progress >= 20:
        threat_level = "rising"
        affected_regions = ["Badlands", "outer evacuation routes"]
        expected_new_york_impact = "early warning signs"
        consequence_if_ignored = "Recon gaps let the Tide accelerate without prepared containment."
    else:
        threat_level = "low"
        affected_regions = ["Badlands"]
        expected_new_york_impact = "no immediate impact"
        consequence_if_ignored = "Delayed response risks losing the first movement pattern."
    if world.new_york_status == "siege":
        expected_new_york_impact = "New York is under siege"
    elif world.new_york_status == "alert" and progress < 50:
        expected_new_york_impact = "New York is on alert"
    return {
        "progress": progress,
        "threat_level": threat_level,
        "affected_regions": affected_regions,
        "expected_new_york_impact": expected_new_york_impact,
        "consequence_if_ignored": consequence_if_ignored,
    }


def _mentions_three_sevens(text: str) -> bool:
    lowered = text.lower()
    return "three sevens" in lowered or "warsaw" in lowered or "37" in lowered


def build_three_sevens_presence_summary(game_state: "GameState") -> dict[str, object]:
    """Summarize Three Sevens antagonist pressure from existing campaign hooks."""
    campaign = game_state.campaign
    world = campaign.world
    story_hooks = [
        mission
        for mission in STORY_MISSIONS
        if (
            "three_sevens" in mission.tags
            or "warsaw" in mission.tags
            or _mentions_three_sevens(mission.title)
            or _mentions_three_sevens(mission.briefing)
        )
    ]
    visible_story = [mission.title for mission in story_hooks if mission.act <= campaign.current_act]
    discovered_intel = []
    for fragment_id in campaign.discovered_intel:
        fragment = get_fragment(fragment_id)
        text = " ".join(
            [
                fragment_id,
                getattr(fragment, "title", ""),
                getattr(fragment, "text", ""),
            ]
        )
        if _mentions_three_sevens(text):
            discovered_intel.append(getattr(fragment, "title", fragment_id))

    active_event_hooks = []
    for event in getattr(game_state, "active_events", []) or []:
        event_text = " ".join(
            [
                getattr(event, "title", ""),
                getattr(event, "description", ""),
                " ".join(getattr(choice, "summary", "") for choice in getattr(event, "choices", [])),
            ]
        )
        if _mentions_three_sevens(event_text):
            active_event_hooks.append(getattr(event, "title", "Three Sevens pressure"))

    enemy_themes = sorted(
        {
            mission.enemy_theme
            for mission in story_hooks
            if mission.act <= campaign.current_act
            and (
                mission.enemy_theme.startswith("corp_37")
                or mission.enemy_theme.startswith("corp_samurai")
            )
        }
    )
    propaganda = (
        "Recovered Three Sevens propaganda is in the intel archive."
        if "act1_three_sevens_banner" in campaign.discovered_intel
        else "Warsaw propaganda signatures are suspected but not fully archived."
    )
    warsaw_pressure = _status_text("warsaw_status", world.warsaw_status)
    late_escalation = (
        "Emergency authority decrees are active or imminent."
        if campaign.current_act >= 5
        else "Late-campaign escalation points toward emergency authority decrees."
    )
    return {
        "story_mission_hooks": visible_story,
        "intel_fragments": discovered_intel,
        "event_hooks": active_event_hooks,
        "special_enemy_themes": enemy_themes,
        "propaganda": propaganda,
        "warsaw_reference": f"Warsaw: {warsaw_pressure}",
        "late_campaign_escalation": late_escalation,
    }


def build_global_scenario_summary(game_state: "GameState") -> dict[str, object]:
    """Return Intel-room campaign facts without depending on Arcade rendering."""
    campaign = game_state.campaign
    world = campaign.world
    required = campaign.missions_required
    act_progress = min(campaign.act_progress, required)
    current_act_fragments = fragments_for_act(campaign.current_act)
    discovered_this_act = [
        fragment_id
        for fragment_id in campaign.discovered_intel
        if fragment_id.startswith(f"act{campaign.current_act}_")
    ]
    return {
        "current_act": campaign.current_act,
        "act_title": ACT_TITLES.get(campaign.current_act, f"Act {campaign.current_act}"),
        "act_progress": act_progress,
        "act_required": required,
        "hungry_tide_percentage": world.hungry_tide_progress,
        "new_york_status": world.new_york_status,
        "warsaw_status": world.warsaw_status,
        "discovered_intel_count": len(campaign.discovered_intel),
        "discovered_intel_this_act": len(discovered_this_act),
        "known_intel_this_act": len(current_act_fragments),
        "major_known_threats": _major_known_threats(game_state),
        "unresolved_global_events": _unresolved_global_events(game_state),
        "hungry_tide": build_hungry_tide_summary(game_state),
        "three_sevens": build_three_sevens_presence_summary(game_state),
    }


def draw_campaign_panel(
    game_state: "GameState",
    x: int,
    y: int,
    width: int,
    height: int,
    elapsed: float = 0.0,
) -> None:
    """Draw the Global Scenario campaign panel at the given screen position."""
    c = game_state.campaign
    summary = build_global_scenario_summary(game_state)
    draw_panel(x, y, width, height, "GLOBAL SCENARIO")

    cy = y + height - 44

    # ── Act header ────────────────────────────────────────────────────────────
    act_title = str(summary["act_title"])
    pulse = 0.85 + 0.15 * math.sin(elapsed * 1.8)
    act_col = (*palette.HEADER[:3], int(230 * pulse))
    arcade.draw_text(
        f"ACT {c.current_act}  —  {act_title.upper()}",
        x + width // 2, cy,
        act_col, font_size=12, bold=True,
        anchor_x="center", anchor_y="center",
    )
    cy -= 18

    # Progress bar for act advancement
    req = int(summary["act_required"])
    prog = int(summary["act_progress"])
    bar_w = width - 28
    bar_h = 6
    bx = x + 14
    arcade.draw_lrbt_rectangle_filled(bx, bx + bar_w, cy - bar_h, cy, palette.ACTION_BUTTON_FILL)
    if req > 0:
        fill_w = int(bar_w * prog / req)
        arcade.draw_lrbt_rectangle_filled(bx, bx + fill_w, cy - bar_h, cy, palette.TACTICAL_GREEN)
    arcade.draw_text(
        f"Story missions: {prog}/{req}",
        bx, cy - bar_h - 12,
        palette.MUTED_TEXT, font_size=8,
        anchor_y="top",
    )
    cy -= bar_h + 18

    arcade.draw_line(x + 8, cy, x + width - 8, cy, palette.PANEL_BORDER_MUTED, 1)
    cy -= 14

    # ── World status indicators ───────────────────────────────────────────────
    arcade.draw_text("WORLD STATUS", x + 14, cy, palette.MUTED_TEXT, font_size=9, bold=True)
    cy -= 14

    w = c.world
    status_fields = [
        ("warsaw_status",       w.warsaw_status),
        ("new_york_status",     w.new_york_status),
        ("hungry_tide_progress", None),   # special handling
        ("pharmacorp_secret",   w.pharmacorp_secret),
        ("ai_factions_status",  w.ai_factions_status),
        ("perfs_status",        w.perfs_status),
    ]

    for field_name, value in status_fields:
        if cy < y + 60:
            break
        if field_name == "hungry_tide_progress":
            tide = w.hungry_tide_progress
            tide_col = (
                palette.TACTICAL_GREEN if tide < 30
                else palette.WARNING if tide < 70
                else palette.DANGER
            )
            # Mini progress bar
            bar_tw = width - 28
            arcade.draw_text("HUNGRY TIDE", x + 14, cy, palette.MUTED_TEXT, font_size=8)
            bar_bx = x + 14 + 80
            arcade.draw_lrbt_rectangle_filled(bar_bx, bar_bx + bar_tw - 80, cy - 3, cy + 7,
                                              palette.ACTION_BUTTON_FILL)
            fill_tw = int((bar_tw - 80) * tide / 100)
            arcade.draw_lrbt_rectangle_filled(bar_bx, bar_bx + fill_tw, cy - 3, cy + 7, tide_col)
            arcade.draw_text(f"{tide}%", bar_bx + bar_tw - 80 + 4, cy, tide_col, font_size=8)
            cy -= 14
            continue

        labels = _WORLD_LABELS.get(field_name, {})
        entry = labels.get(value)
        if not entry:
            continue
        label, status_text, col = entry
        arcade.draw_text(f"{label}:", x + 14, cy, palette.MUTED_TEXT, font_size=8)
        arcade.draw_text(status_text, x + 94, cy, col, font_size=8, bold=True)
        cy -= 14

    arcade.draw_line(x + 8, cy, x + width - 8, cy, palette.PANEL_BORDER_MUTED, 1)
    cy -= 14

    # ── Latest intel fragments ────────────────────────────────────────────────
    tide_summary = dict(summary["hungry_tide"])
    arcade.draw_text("HUNGRY TIDE INTEL", x + 14, cy, palette.DANGER, font_size=9, bold=True)
    cy -= 14
    tide_lines = [
        f"Threat: {tide_summary['threat_level']} | Regions: {', '.join(tide_summary['affected_regions'])}",
        f"NY impact: {tide_summary['expected_new_york_impact']}",
        f"If ignored: {tide_summary['consequence_if_ignored']}",
    ]
    for line in tide_lines:
        if cy < y + 92:
            break
        arcade.draw_text(str(line)[:72], x + 14, cy, palette.MUTED_TEXT, font_size=8)
        cy -= 12

    three_sevens = dict(summary["three_sevens"])
    arcade.draw_text("THREE SEVENS PRESSURE", x + 14, cy, palette.WARNING, font_size=9, bold=True)
    cy -= 14
    story_hooks = list(three_sevens["story_mission_hooks"])
    enemy_themes = list(three_sevens["special_enemy_themes"])
    three_sevens_lines = [
        str(three_sevens["warsaw_reference"]),
        str(three_sevens["propaganda"]),
        f"Story hook: {story_hooks[-1] if story_hooks else 'none visible yet'}",
        f"Special enemies: {', '.join(enemy_themes) if enemy_themes else 'none revealed'}",
        str(three_sevens["late_campaign_escalation"]),
    ]
    for line in three_sevens_lines[:4]:
        if cy < y + 92:
            break
        arcade.draw_text(str(line)[:72], x + 14, cy, palette.MUTED_TEXT, font_size=8)
        cy -= 12

    arcade.draw_text("MAJOR KNOWN THREATS", x + 14, cy, palette.WARNING, font_size=9, bold=True)
    cy -= 14
    for threat in list(summary["major_known_threats"])[:3]:
        if cy < y + 72:
            break
        arcade.draw_text(f"- {str(threat)[:40]}", x + 14, cy, palette.TEXT, font_size=8)
        cy -= 12

    arcade.draw_text("UNRESOLVED GLOBAL EVENTS", x + 14, cy, palette.ACCENT, font_size=9, bold=True)
    cy -= 14
    for event_line in list(summary["unresolved_global_events"])[:2]:
        if cy < y + 46:
            break
        arcade.draw_text(f"- {str(event_line)[:42]}", x + 14, cy, palette.MUTED_TEXT, font_size=8)
        cy -= 12

    arcade.draw_line(x + 8, cy, x + width - 8, cy, palette.PANEL_BORDER_MUTED, 1)
    cy -= 14

    total = int(summary["discovered_intel_count"])
    act_total = int(summary["discovered_intel_this_act"])
    act_possible = int(summary["known_intel_this_act"])
    arcade.draw_text(
        f"INTEL  {total} total  ({act_total}/{act_possible} this act)",
        x + 14, cy,
        palette.ACCENT, font_size=9, bold=True,
    )
    cy -= 14

    from game.campaign.intel_fragments import get_fragment
    # Show last 4 discovered (most recent last = show from end)
    recent = list(reversed(c.discovered_intel))[:4]
    for fid in recent:
        if cy < y + 8:
            break
        frag = get_fragment(fid)
        title = frag.title if frag else fid
        is_new = c.discovered_intel[-1] == fid
        col = (255, 215, 60) if is_new else palette.TEXT
        prefix = "► " if is_new else "  "
        arcade.draw_text(
            f"{prefix}{title[:36]}",
            x + 14, cy,
            col, font_size=8,
        )
        cy -= 13


def draw_act_advance_overlay(
    width: int,
    height: int,
    act_number: int,
    act_title: str,
    elapsed: float,
    duration: float = 3.0,
) -> None:
    """Full-screen overlay announcing an act transition. Fades after *duration* seconds."""
    progress = min(1.0, elapsed / duration)
    fade = 1.0 - progress if progress > 0.6 else 1.0

    arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, int(200 * fade)))

    cx = width // 2
    cy = height // 2

    pulse = 0.8 + 0.2 * math.sin(elapsed * 3.0)
    gold = (255, 215, 60, int(240 * fade * pulse))

    arcade.draw_line(cx - 300, cy + 56, cx + 300, cy + 56, (*gold[:3], int(120 * fade)), 1)
    arcade.draw_line(cx - 300, cy - 56, cx + 300, cy - 56, (*gold[:3], int(120 * fade)), 1)

    arcade.draw_text(
        f"ACT {act_number}",
        cx, cy + 30,
        gold, font_size=36, bold=True,
        anchor_x="center", anchor_y="center",
    )
    arcade.draw_text(
        act_title.upper(),
        cx, cy - 14,
        (*palette.HEADER[:3], int(200 * fade)),
        font_size=18, bold=True,
        anchor_x="center", anchor_y="center",
    )
    arcade.draw_text(
        "The world changes.",
        cx, cy - 44,
        (*palette.MUTED_TEXT[:3], int(160 * fade)),
        font_size=10,
        anchor_x="center", anchor_y="center",
    )
