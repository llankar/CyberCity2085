"""Mission board card line builder."""

from __future__ import annotations

from ....mission_templates import MissionTemplate
from ...accessibility.states import label_with_non_color_indicator


def build_mission_card_line(
    mission: MissionTemplate,
    *,
    index: int,
    selected: bool,
    objective_label: str,
    risk_label: str,
) -> str:
    """Build one compact mission row for list rendering."""
    state = "focus" if selected else "normal"
    prefix = ">" if selected else " "
    return (
        f"{label_with_non_color_indicator(f'{prefix}{index + 1}. {mission.title}', state)} | "
        f"{objective_label} | "
        f"Risk {mission.risk_level} ({risk_label}) | "
        f"Reward {mission.fund_reward} funds | "
        f"Duration: {mission.duration_days} day{'s' if mission.duration_days != 1 else ''} | "
        f"{mission.target_faction} | Enemies {mission.starting_enemy_count}"
    )
