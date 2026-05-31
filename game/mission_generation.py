from __future__ import annotations

import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState
from .i18n import t
from .enemy_themes import mission_enemy_theme
from .mission_templates import MissionTemplate, create_mission_templates
from .missions.complications import select_complications
from .missions.evacuation import create_evacuation_template
from .narrative.mission_briefing_conventions import (
    build_short_emotional_impact,
    normalize_mission_tags,
)


def _mission_seed(game_state: "GameState") -> int:
    """Build a deterministic seed from campaign state for stable daily boards."""
    return (
        game_state.calendar.current_day * 97
        + game_state.district.unrest * 11
        + game_state.district.media_heat * 7
        + (100 - game_state.district.stability) * 5
    )




def _build_emotional_impact_hint(mission: MissionTemplate, language: str | None = None) -> dict:
    """Estimate emotional impact based on objective pressure, risk, duration, and complications."""
    objective_weight = {
        "safe_extraction": 2,
        "extract": 2,
        "data_with_detour": 2,
        "data_theft": 1,
        "sabotage_window": 1,
        "sabotage": 1,
        "eliminate": 0,
    }.get(mission.objective_type, 1)
    score = (
        mission.risk_level
        + max(0, mission.duration_days - 1)
        + len(mission.possible_complications)
        + objective_weight
    )
    if score >= 8:
        level = "critical"
        text = t("mission.impact.critical", language)
    elif score >= 6:
        level = "high"
        text = t("mission.impact.high", language)
    elif score >= 4:
        level = "medium"
        text = t("mission.impact.medium", language)
    else:
        level = "low"
        text = t("mission.impact.low", language)
    short_text = build_short_emotional_impact(level, text)
    risk_explanation = t(
        "mission.impact.risk_explanation",
        language,
        risk=mission.risk_level,
        duration=mission.duration_days,
        complications=len(mission.possible_complications),
    )
    return {
        "level": level,
        "text": text,
        "short_text": short_text,
        "emotional_impact_summary": short_text,
        "risk_explanation": risk_explanation,
        "expected_stress_band": level,
    }


def generate_mission_board(game_state: "GameState", board_size: int | None = None) -> list[MissionTemplate]:
    """Generate a small daily mission board based on district pressure."""
    templates = create_mission_templates(game_state.district.name)
    district_pressure = game_state.district.unrest + game_state.district.media_heat
    evac_probability = min(0.65, max(0.15, district_pressure / 140))
    if random.Random(_mission_seed(game_state) + 404).random() < evac_probability:
        templates.append(create_evacuation_template(game_state.district.name, district_pressure))
    if not templates:
        return []

    rng = random.Random(_mission_seed(game_state))
    pressure_score = game_state.district.unrest + game_state.district.media_heat
    pressure_mod = max(0, pressure_score - game_state.district.stability) // 20

    generated: list[MissionTemplate] = []
    slots = board_size if board_size is not None else random.Random(_mission_seed(game_state) + 313).randint(3, 6)
    slots = max(1, slots)
    for slot in range(slots):
        base = templates[slot % len(templates)]
        mission = MissionTemplate.from_dict(base.to_dict())
        risk_delta = rng.choice([-1, 0, 1]) + pressure_mod
        mission.risk_level = max(1, mission.risk_level + risk_delta)
        mission.fund_reward = max(20, mission.fund_reward + mission.risk_level * 5)
        mission.starting_enemy_count = max(1, mission.starting_enemy_count + max(0, risk_delta))
        mission.id = f"{mission.id}_d{game_state.calendar.current_day}_s{slot}"
        mission.title = f"{mission.title} {t('mission.board.day_suffix', game_state.ui_language, day=game_state.calendar.current_day)}"
        mission_tag_names = [tag.name for tag in mission.tags]
        mission.possible_complications.extend(
            select_complications(
                district_pressure=pressure_score,
                mission_tags=mission_tag_names,
                seed=_mission_seed(game_state) + slot,
            )
        )
        mission.possible_complications = mission.possible_complications[:2]
        mission.emotional_impact_hint = _build_emotional_impact_hint(mission, game_state.ui_language)
        mission.emotional_impact_hint["normalized_tags"] = normalize_mission_tags(mission.tags)
        mission.enemy_theme = mission_enemy_theme(mission)
        generated.append(mission)

    # ── Story mission injection ───────────────────────────────────────────────
    _inject_story_mission(game_state, generated)

    rng.shuffle(generated)
    return generated


def _inject_story_mission(
    game_state: "GameState",
    board: list[MissionTemplate],
) -> None:
    """Insert one story mission per act into the board if conditions are met."""
    try:
        from game.campaign.story_missions import story_missions_for_act
        from game.campaign.acts import ACT_TITLES
    except Exception:
        return

    c = game_state.campaign
    act_missions = story_missions_for_act(c.current_act)
    if not act_missions:
        return

    # Pick the first story mission whose id hasn't been completed yet
    completed_ids = set(c.act_triggers_seen)
    for sm in act_missions:
        completed_key = f"story_complete_{sm.id}"
        if completed_key in completed_ids:
            continue
        # Build a MissionTemplate from the StoryMissionTemplate
        from game.consequences import Consequence
        mt = MissionTemplate(
            id=sm.id,
            title=f"[STORY] {sm.title}",
            objective_text=sm.objective_text,
            target_faction="Three Sevens Corp",
            district=game_state.district.name,
            district_pressure={"unrest": game_state.district.unrest},
            starting_enemy_count=max(3, sm.risk_level // 2),
            enemy_theme=sm.enemy_theme,
            objective_type=sm.objective_type,
            risk_level=sm.risk_level,
            fund_reward=sm.fund_reward,
            duration_days=2,
            emotional_impact_hint={
                "level": "critical",
                "text": sm.briefing[:120],
                "short_text": sm.briefing[:60],
                "normalized_tags": sm.tags,
            },
        )
        mt.enemy_theme = mission_enemy_theme(mt)
        # Insert at front of board (replace last regular mission if board is full)
        if len(board) >= 3:
            board[-1] = mt
        else:
            board.insert(0, mt)
        return  # only one story mission at a time
