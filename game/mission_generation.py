from __future__ import annotations

import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState
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




def _build_emotional_impact_hint(mission: MissionTemplate) -> dict:
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
        text = "Risque de séquelles émotionnelles durables pour l'escouade."
    elif score >= 6:
        level = "high"
        text = "Mission susceptible de laisser une forte charge émotionnelle."
    elif score >= 4:
        level = "medium"
        text = "Tension humaine notable, prévoir du soutien post-mission."
    else:
        level = "low"
        text = "Impact humain contenu si l'exécution reste disciplinée."
    short_text = build_short_emotional_impact(level, text)
    risk_explanation = (
        f"Risque {mission.risk_level}/5, durée {mission.duration_days}j, "
        f"{len(mission.possible_complications)} complication(s) probable(s)."
    )
    return {
        "level": level,
        "text": text,
        "short_text": short_text,
        "emotional_impact_summary": short_text,
        "risk_explanation": risk_explanation,
        "expected_stress_band": level,
    }


def generate_mission_board(game_state: "GameState", board_size: int = 3) -> list[MissionTemplate]:
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
    slots = max(1, board_size)
    for slot in range(slots):
        base = templates[slot % len(templates)]
        mission = MissionTemplate.from_dict(base.to_dict())
        risk_delta = rng.choice([-1, 0, 1]) + pressure_mod
        mission.risk_level = max(1, mission.risk_level + risk_delta)
        mission.fund_reward = max(20, mission.fund_reward + mission.risk_level * 5)
        mission.starting_enemy_count = max(1, mission.starting_enemy_count + max(0, risk_delta))
        mission.id = f"{mission.id}_d{game_state.calendar.current_day}_s{slot}"
        mission.title = f"{mission.title} [Day {game_state.calendar.current_day}]"
        mission_tag_names = [tag.name for tag in mission.tags]
        mission.possible_complications.extend(
            select_complications(
                district_pressure=pressure_score,
                mission_tags=mission_tag_names,
                seed=_mission_seed(game_state) + slot,
            )
        )
        mission.possible_complications = mission.possible_complications[:2]
        mission.emotional_impact_hint = _build_emotional_impact_hint(mission)
        mission.emotional_impact_hint["normalized_tags"] = normalize_mission_tags(mission.tags)
        generated.append(mission)

    rng.shuffle(generated)
    return generated
