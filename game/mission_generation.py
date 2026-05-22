from __future__ import annotations

import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState
from .mission_templates import MissionTemplate, create_mission_templates
from .missions.complications import select_complications
from .missions.evacuation import create_evacuation_template


def _mission_seed(game_state: "GameState") -> int:
    """Build a deterministic seed from campaign state for stable daily boards."""
    return (
        game_state.calendar.current_day * 97
        + game_state.district.unrest * 11
        + game_state.district.media_heat * 7
        + (100 - game_state.district.stability) * 5
    )


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
        generated.append(mission)

    rng.shuffle(generated)
    return generated

