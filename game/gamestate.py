from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from .consequences import Consequence, create_opening_consequence
from .factions import Faction, create_vertical_slice_factions
from .management.calendar import StrategicCalendar
from .management.funds import (
    MISSION_FUND_CATEGORIES,
    CorporateFunds,
    calculate_mission_fund_reward,
    default_mission_fund_distribution,
)
from .mission_templates import MissionTemplate, create_mission_templates
from .operations import Operation, create_operation_templates
from .world import District, create_vertical_slice_district

if TYPE_CHECKING:
    from .character import Character


@dataclass
class GameState:
    """Holds the state of the current game."""

    # Corporation values accumulated over all turns
    corp_budget: dict = field(
        default_factory=lambda: {
            "research": 0,
            "security": 0,
            "politics": 0,
            "black_ops": 0,
        }
    )

    # Strategic resources extracted from tactical missions and spent on upgrades
    strategic_resources: dict = field(
        default_factory=lambda: {
            "credits": 0,
            "intel": 0,
            "salvage": 0,
            "influence": 0,
        }
    )

    # Post-mission cash allocations reserved for named command categories.
    mission_fund_allocations: dict = field(
        default_factory=lambda: {key: 0 for key in MISSION_FUND_CATEGORIES}
    )

    # Management data for the city phase
    city_budget: dict = field(
        default_factory=lambda: {
            "armaments": 0,
            "garrisons": 0,
            "defense_zones": 0,
        }
    )

    # List of recruited characters
    characters: List[Character] = field(default_factory=list)

    # First vertical-slice world model: one district, one base, and three factions
    base_name: str = "Aegis Forward Base Kilo"
    district: District = field(default_factory=create_vertical_slice_district)
    factions: list[Faction] = field(default_factory=create_vertical_slice_factions)
    active_operations: list[Operation] = field(
        default_factory=create_operation_templates
    )
    mission_templates: list[MissionTemplate] = field(
        default_factory=create_mission_templates
    )
    active_mission: MissionTemplate | None = None
    selected_mission_index: int = 0
    recent_consequences: list[Consequence] = field(
        default_factory=lambda: [create_opening_consequence()]
    )
    latest_agent_aftermath: list[str] = field(default_factory=list)
    selected_agent_names: list[str] = field(default_factory=list)
    event_log: list[str] = field(
        default_factory=lambda: [
            "Turn 1: Forward Base Kilo establishes overwatch in the Chrome Warrens."
        ]
    )

    # Experience points gained through battles
    x: int = 0

    # Turn management
    turn: int = 1
    calendar: StrategicCalendar = field(default_factory=StrategicCalendar)
    funds: CorporateFunds = field(default_factory=CorporateFunds)
    budget_pool: int = 0

    def __post_init__(self) -> None:
        if not self.budget_pool:
            self.budget_pool = self.compute_budget()
        if self.funds.available_funds <= 0 and not self.funds.transaction_history:
            self.funds.add_funds(
                self.budget_pool,
                "opening_budget",
                "Initial corporate operating funds.",
            )
        self.budget_pool = self.funds.available_funds

    # ------------------------------------------------------------------
    # Turn and budget management
    # ------------------------------------------------------------------
    def compute_budget(self) -> int:
        """Compute the budget for the next turn based on current corp values."""
        return 100 + sum(self.corp_budget.values()) // 10

    @property
    def available_funds(self) -> int:
        """Return corporate funds available for immediate spending."""
        return self.funds.available_funds

    def can_afford(self, amount: int) -> bool:
        """Return whether the corporate ledger can cover an expense."""
        return self.funds.can_afford(amount)

    def add_funds(self, amount: int, source: str, note: str = "") -> bool:
        """Add income to the corporate funds ledger and sync legacy budget UI."""
        added = self.funds.add_funds(amount, source, note)
        if added:
            self.budget_pool = self.funds.available_funds
        return added

    def spend_funds(self, amount: int, sink: str, note: str = "") -> bool:
        """Spend from the corporate funds ledger and sync legacy budget UI."""
        spent = self.funds.spend_funds(amount, sink, note)
        if spent:
            self.budget_pool = self.funds.available_funds
        return spent

    def allocate_corp_funds(self, key: str, amount: int) -> bool:
        """Attempt to allocate funds from the current corporate ledger."""
        if key in self.corp_budget and self.spend_funds(
            amount, f"corp_{key}", f"Allocated to {key}."
        ):
            self.corp_budget[key] += amount
            return True
        return False

    def award_mission_resources(
        self, mission: MissionTemplate | None, victory: bool, defeated: int
    ) -> dict:
        """Award compact strategic resources from mission risk and performance."""
        if not mission:
            return {}

        risk = max(1, int(getattr(mission, "risk_level", 1)))
        defeated = max(0, int(defeated))
        rewards = {key: 0 for key in self.strategic_resources}

        if victory:
            objective_type = getattr(mission, "objective_type", "eliminate")
            rewards["credits"] = 10 + risk * 5 + defeated * 2
            rewards["intel"] = max(1, risk // 2)
            rewards["salvage"] = max(1, defeated // 2)
            rewards["influence"] = 1 if risk >= 3 else 0

            if objective_type in {"data_theft", "extract"}:
                rewards["intel"] += 1
            if objective_type in {"sabotage", "eliminate"}:
                rewards["salvage"] += 1
            if objective_type == "extract":
                rewards["influence"] += 1
        elif defeated >= 2:
            rewards["salvage"] = 1

        rewards = {key: value for key, value in rewards.items() if value > 0}
        for key, value in rewards.items():
            self.strategic_resources[key] = self.strategic_resources.get(key, 0) + value

        if rewards:
            reward_text = ", ".join(f"+{value} {key}" for key, value in rewards.items())
            self.add_event(f"Extraction secured: {reward_text}.")
        else:
            self.add_event("Extraction failed: no strategic resources recovered.")
        return rewards

    def award_mission_funds(
        self, mission: MissionTemplate | None, victory: bool
    ) -> dict[str, int]:
        """Add mission cash to the ledger, then apply a small default split."""
        reward = calculate_mission_fund_reward(mission, victory)
        if reward <= 0:
            return {}

        mission_title = getattr(mission, "title", "mission")
        if not self.add_funds(
            reward,
            "mission_reward",
            f"{mission_title} success payout.",
        ):
            return {}

        distribution = default_mission_fund_distribution(reward)
        for category, amount in distribution.items():
            if amount <= 0:
                continue
            self.mission_fund_allocations[category] = (
                self.mission_fund_allocations.get(category, 0) + amount
            )
            if category != "corporate_reserves":
                self.spend_funds(
                    amount,
                    f"mission_{category}",
                    f"Post-mission allocation from {mission_title}.",
                )

        summary = ", ".join(
            f"{category.replace('_', ' ')} +{amount}"
            for category, amount in distribution.items()
            if amount > 0
        )
        self.add_event(f"Mission funds secured: +{reward}; allocation {summary}.")
        return {key: value for key, value in distribution.items() if value > 0}

    def spend_resource(self, resource_key: str, amount: int) -> bool:
        """Spend one strategic resource safely when enough stock is available."""
        if amount < 0:
            return False
        if self.strategic_resources.get(resource_key, 0) < amount:
            return False
        self.strategic_resources[resource_key] -= amount
        return True

    def can_spend_resources(self, costs: dict[str, int]) -> bool:
        """Return whether all strategic-resource costs are currently affordable."""
        return all(
            self.strategic_resources.get(resource_key, 0) >= amount
            for resource_key, amount in costs.items()
        )

    def spend_resources(self, costs: dict[str, int]) -> bool:
        """Atomically spend several strategic resources when all costs are affordable."""
        if not self.can_spend_resources(costs):
            return False
        for resource_key, amount in costs.items():
            self.strategic_resources[resource_key] -= amount
        return True

    def advance_one_day(self, reason: str = "manual") -> None:
        """Move the shared strategic clock one day and process daily systems."""
        recovered_agents = []
        for character in self.characters:
            if character.recovery_turns > 0:
                character.recovery_turns -= 1
                if character.recovery_turns == 0:
                    recovered_agents.append(character.name)

        self.calendar.advance_one_day()
        self.turn = self.calendar.current_day
        income = self.compute_budget()
        self.add_funds(
            income,
            "daily_income",
            f"{self.calendar.campaign_date_label} passive income for {self.base_name}.",
        )
        self.add_event(
            f"{self.calendar.campaign_date_label}: Day advanced ({reason}); "
            f"passive income +{income}."
        )
        if self.recent_consequences:
            self.add_event(
                f"{self.calendar.campaign_date_label}: Pending fallout reviewed "
                f"({len(self.recent_consequences)} active beats)."
            )
        if self.calendar.is_new_week:
            self.add_event(
                f"Week {self.calendar.current_week}: Strategic planning cycle opens."
            )
        for name in recovered_agents:
            self.add_event(
                f"{self.calendar.campaign_date_label}: {name} is deployable after recovery."
            )

    def advance_days(self, days: int, reason: str = "manual") -> None:
        """Advance multiple days while preserving daily income and recovery ticks."""
        if days < 0:
            raise ValueError("days must be non-negative")
        for _ in range(days):
            self.advance_one_day(reason)

    def advance_turn(self) -> None:
        """Backward-compatible wrapper for one strategic day."""
        self.advance_one_day("turn refresh")

    def add_event(self, text: str) -> None:
        """Append a compact event-log entry and retain only the latest beats."""
        self.event_log.append(text)
        self.event_log = self.event_log[-12:]

    def record_consequence(self, consequence: Consequence) -> None:
        """Store recent fallout and add it to the event log."""
        self.recent_consequences.append(consequence)
        self.recent_consequences = self.recent_consequences[-6:]
        if consequence.narrative_text:
            self.add_event(consequence.narrative_text)

    def apply_consequence(self, consequence: Consequence) -> None:
        """Apply district and faction effects from a mission consequence."""
        effects = consequence.mechanical_effects
        for key in ("stability", "unrest", "media_heat"):
            if key in effects and hasattr(self.district, key):
                setattr(self.district, key, getattr(self.district, key) + effects[key])
        self.district.clamp_pressure()

        if consequence.affected_faction:
            faction = self.get_faction(consequence.affected_faction)
            if faction:
                if "faction_hostility" in effects:
                    faction.hostility_to_player += effects["faction_hostility"]
                if "faction_influence" in effects:
                    faction.influence += effects["faction_influence"]
                if "faction_legitimacy" in effects:
                    faction.public_legitimacy += effects["faction_legitimacy"]
                for tag in consequence.tags:
                    if all(
                        existing.name != tag.name for existing in faction.active_tags
                    ):
                        faction.active_tags.append(tag)
                faction.clamp_pressure()

        for tag in consequence.tags:
            if all(existing.name != tag.name for existing in self.district.tags):
                self.district.tags.append(tag)
        self.record_consequence(consequence)

    def apply_active_mission_pressure(self) -> None:
        """Apply up-front district pressure from the selected active mission."""
        if not self.active_mission:
            return
        for key, amount in self.active_mission.district_pressure.items():
            if hasattr(self.district, key):
                setattr(self.district, key, getattr(self.district, key) + amount)
        self.district.clamp_pressure()
        self.add_event(
            f"Mission launched: {self.active_mission.title} against "
            f"{self.active_mission.target_faction}."
        )

    def get_faction(self, name: str) -> Faction | None:
        """Find a faction by name in the current world slice."""
        for faction in self.factions:
            if faction.name == name:
                return faction
        return None

    def adjust_corp_budget(self, key: str, amount: int) -> None:
        """Backward compatible wrapper around :py:meth:`allocate_corp_funds`."""
        self.allocate_corp_funds(key, amount)

    def adjust_city_budget(self, key: str, amount: int) -> None:
        if key in self.city_budget:
            self.city_budget[key] += amount

    def save(self, path: str):
        data = {
            "turn": self.turn,
            "calendar": self.calendar.to_dict(),
            "budget_pool": self.budget_pool,
            "funds": self.funds.to_dict(),
            "corp_budget": self.corp_budget,
            "city_budget": self.city_budget,
            "strategic_resources": self.strategic_resources,
            "mission_fund_allocations": self.mission_fund_allocations,
            "characters": [c.to_dict() for c in self.characters],
            "x": self.x,
            "base_name": self.base_name,
            "district": self.district.to_dict(),
            "factions": [faction.to_dict() for faction in self.factions],
            "active_operations": [
                operation.to_dict() for operation in self.active_operations
            ],
            "mission_templates": [
                mission.to_dict() for mission in self.mission_templates
            ],
            "active_mission": (
                self.active_mission.to_dict() if self.active_mission else None
            ),
            "selected_mission_index": self.selected_mission_index,
            "selected_agent_names": list(self.selected_agent_names),
            "recent_consequences": [
                consequence.to_dict() for consequence in self.recent_consequences
            ],
            "latest_agent_aftermath": list(self.latest_agent_aftermath),
            "event_log": list(self.event_log),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> "GameState":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gs = cls()
        gs.corp_budget.update(data.get("corp_budget", {}))
        gs.city_budget.update(data.get("city_budget", {}))
        gs.strategic_resources.update(data.get("strategic_resources", {}))
        gs.mission_fund_allocations.update(
            data.get("mission_fund_allocations", {})
        )
        gs.calendar = StrategicCalendar.from_dict(data.get("calendar"))
        gs.turn = data.get("turn", gs.calendar.current_day)
        if "calendar" not in data:
            gs.calendar.current_day = max(1, int(gs.turn))
            gs.calendar._last_week = gs.calendar.current_week
        if "funds" in data:
            gs.funds = CorporateFunds.from_dict(data["funds"])
            gs.budget_pool = gs.funds.available_funds
        else:
            gs.budget_pool = data.get("budget_pool", gs.compute_budget())
            gs.funds = CorporateFunds(current_funds=gs.budget_pool)
        gs.x = data.get("x", 0)
        gs.base_name = data.get("base_name", gs.base_name)
        gs.district = District.from_dict(data.get("district", gs.district.to_dict()))
        gs.factions = [
            Faction.from_dict(faction) for faction in data.get("factions", [])
        ] or create_vertical_slice_factions()
        gs.active_operations = [
            Operation.from_dict(operation)
            for operation in data.get("active_operations", [])
        ] or create_operation_templates(gs.district.name)
        gs.mission_templates = [
            MissionTemplate.from_dict(mission)
            for mission in data.get("mission_templates", [])
        ] or create_mission_templates(gs.district.name)
        active_mission_data = data.get("active_mission")
        gs.active_mission = (
            MissionTemplate.from_dict(active_mission_data)
            if active_mission_data
            else None
        )
        gs.selected_mission_index = data.get("selected_mission_index", 0)
        gs.selected_agent_names = list(data.get("selected_agent_names", []))
        gs.recent_consequences = [
            Consequence.from_dict(consequence)
            for consequence in data.get("recent_consequences", [])
        ] or [create_opening_consequence(gs.district.name)]
        gs.latest_agent_aftermath = list(data.get("latest_agent_aftermath", []))
        gs.event_log = list(data.get("event_log", gs.event_log))
        from .character import Character

        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        from .deployment import sanitize_selected_agent_names

        gs.selected_agent_names = sanitize_selected_agent_names(
            gs.characters, gs.selected_agent_names
        )
        return gs
