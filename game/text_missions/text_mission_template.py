"""Data structures for narrative text missions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillCheck:
    """A skill check attached to a mission choice."""

    skill: str       # key from ALLOWED_SKILL_KEYS
    difficulty: int  # target total: easy≈6, medium≈8, hard≈10, punishing≈12
    label: str       # "Pick the lock" / "Persuade the guard"


@dataclass(frozen=True)
class SceneChoice:
    """One option the player can take in a mission scene."""

    id: str
    label: str              # short text on the button (≤30 chars)
    skill_check: SkillCheck
    success_scene: str      # scene id on success
    failure_scene: str      # scene id on failure
    great_scene: str = ""   # scene id on great success ("" → use success_scene)
    partial_scene: str = "" # scene id on partial failure ("" → use failure_scene)


@dataclass(frozen=True)
class MissionScene:
    """One narrative beat in a text mission."""

    id: str
    text: str                         # atmospheric story text
    choices: tuple[SceneChoice, ...] = ()
    outcome: str = "none"             # "success" | "partial" | "failure" | "none"
    fund_delta: int = 0               # funds gained (may be negative)
    stress_delta: int = 0             # stress applied to every deployed agent


@dataclass
class TextMissionTemplate:
    """A narrative text mission driven by background art and skill checks."""

    id: str
    title: str
    district_type: str    # "city" or "wasteland"
    background_key: str   # filename stem, e.g. "city_01_neon_alley"
    description: str      # one-line briefing for the world map card
    opening_scene_id: str
    scenes: dict[str, MissionScene]
    fund_reward: int
    risk_level: int       # 1–5
    required_skills: list[str] = field(default_factory=list)
    duration_days: int = 1

    def background_path(self) -> str:
        return f"assets/missions/backgrounds/{self.district_type}/{self.background_key}.jpg"
