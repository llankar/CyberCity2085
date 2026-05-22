from __future__ import annotations

from dataclasses import dataclass

from game.consequences import Consequence
from game.mission_templates import MissionTemplate
from game.savage_fate import SavageTag, tag_from_library


@dataclass(frozen=True)
class EvacuationOutcome:
    """Compact result payload for extraction-first mission resolution."""

    succeeded: bool
    score: int
    summary: str
    extracted_agents: int
    alive_agents: int
    neutralized_enemies: int


def create_evacuation_template(district_name: str, pressure: int = 0) -> MissionTemplate:
    """Build one evacuation mission focused on saving squad members under pressure."""
    risk_level = 3 if pressure >= 60 else 2
    duration_days = 2 if pressure >= 70 else 1
    min_extracted = 2 if pressure >= 60 else 1
    tolerated_losses = 0 if pressure >= 60 else 1

    return MissionTemplate(
        id="evacuation",
        title="Evacuation: Last Lift Corridor",
        objective_text=(
            "Extract a minimum number of living agents before corridor lockdown. "
            "Neutralizations are optional; survival is mandatory."
        ),
        target_faction="Aegis Dynamics",
        district=district_name,
        district_pressure={"pressure": pressure, "unrest_weight": 2, "media_weight": 1},
        starting_enemy_count=3,
        objective_type="safe_extraction",
        risk_level=risk_level,
        fund_reward=55 + max(0, pressure // 10),
        duration_days=duration_days,
        tags=[
            tag_from_library("civilian_panic"),
            SavageTag(
                name="evacuation_pressure",
                description="Time pressure and fragile evac routes push squads into emotional triage.",
                intensity=2 if pressure >= 60 else 1,
                source="mission",
            ),
        ],
        success_consequences=[
            Consequence(
                affected_district=district_name,
                affected_faction="Evacuation Network",
                severity=1,
                narrative_text="Evac success: survivors spread trust through the district shelters.",
                mechanical_effects={"stability": 4, "unrest": -3},
            )
        ],
        failure_consequences=[
            Consequence(
                affected_district=district_name,
                affected_faction="Aegis Dynamics",
                severity=3,
                narrative_text="Evac failure: missing agents become symbols of abandonment.",
                mechanical_effects={"unrest": 7, "media_heat": 5, "stability": -4},
            )
        ],
    )


def evacuation_constraints(pressure: int) -> dict[str, int]:
    """Expose extraction/loss/pressure constraints for UI and evaluation."""
    return {
        "min_extracted_agents": 2 if pressure >= 60 else 1,
        "tolerated_losses": 0 if pressure >= 60 else 1,
        "pressure": max(0, pressure),
    }


def evaluate_evacuation_outcome(
    extracted_agents: int,
    alive_agents: int,
    neutralized_enemies: int,
    min_extracted_agents: int,
    tolerated_losses: int,
) -> EvacuationOutcome:
    """Score evacuation with survival-first weighting."""
    extracted = max(0, extracted_agents)
    alive = max(0, alive_agents)
    neutralized = max(0, neutralized_enemies)
    losses = max(0, alive - extracted)

    succeeded = extracted >= max(1, min_extracted_agents) and losses <= max(0, tolerated_losses)
    score = (extracted * 35) + (alive * 20) + (neutralized * 5) - (losses * 40)
    summary = "Evacuation success: survival corridor held." if succeeded else "Evacuation failed: extraction threshold missed."

    return EvacuationOutcome(
        succeeded=succeeded,
        score=score,
        summary=summary,
        extracted_agents=extracted,
        alive_agents=alive,
        neutralized_enemies=neutralized,
    )


def evacuation_briefing_fields(pressure: int) -> dict[str, str | int]:
    """Return UI briefing metadata centered on emotional stakes."""
    risk = "critical" if pressure >= 70 else "high" if pressure >= 45 else "elevated"
    reward = "Survivors secured and district trust gains." if pressure >= 45 else "Safe extraction with moderate public goodwill."
    impact = "High emotional attachment expected: squad survival and witness memory are foregrounded."
    return {"risk": risk, "reward": reward, "emotional_impact": impact, "pressure": pressure}
