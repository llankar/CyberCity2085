"""Small strategic event system for management-phase threats.

Events are deliberately compact: templates describe the narrative pressure,
active events track calendar expiry, and choices apply a few mechanical levers
already owned by ``GameState``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

ENEMY_CORPORATION_ATTACK = "enemy corporation attack"
MUTANT_INVASION = "mutant invasion"
STARVERS_OUTBREAK = "Starvers outbreak"
SOCIAL_UNREST = "social unrest"
CORPORATE_POLITICS = "corporate politics"
CITY_POLITICS = "city politics"

EVENT_CATEGORIES = (
    ENEMY_CORPORATION_ATTACK,
    MUTANT_INVASION,
    STARVERS_OUTBREAK,
    SOCIAL_UNREST,
    CORPORATE_POLITICS,
    CITY_POLITICS,
)


@dataclass(frozen=True)
class EventChoice:
    """One player response option and its compact mechanical effects."""

    key: str
    label: str
    effects: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    relation_impact: str = "low"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "effects": dict(self.effects),
            "summary": self.summary,
            "relation_impact": self.relation_impact,
        }

    @classmethod
    def from_dict(cls, data: dict | "EventChoice") -> "EventChoice":
        if isinstance(data, cls):
            return data
        return cls(
            key=str(data.get("key", "respond")),
            label=str(data.get("label", "Respond")),
            effects=dict(data.get("effects", {})),
            summary=str(data.get("summary", "")),
            relation_impact=_normalize_relation_impact(
                str(data.get("relation_impact", "low"))
            ),
        )


def _normalize_relation_impact(value: str) -> str:
    level = str(value).strip().lower()
    if level not in {"low", "medium", "high"}:
        return "low"
    return level


@dataclass(frozen=True)
class EventTemplate:
    """Reusable event seed that can become an active command-deck crisis."""

    title: str
    category: str
    description: str
    severity: int
    choices: list[EventChoice]
    consequences: dict[str, Any] = field(default_factory=dict)
    relation_impact: str = "low"
    expiration_days: int = 3
    weight: int = 1

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "severity": max(1, int(self.severity)),
            "choices": [choice.to_dict() for choice in self.choices],
            "consequences": dict(self.consequences),
            "relation_impact": self.relation_impact,
            "expiration_days": max(1, int(self.expiration_days)),
            "weight": max(1, int(self.weight)),
        }

    @classmethod
    def from_dict(cls, data: dict | "EventTemplate") -> "EventTemplate":
        if isinstance(data, cls):
            return data
        return cls(
            title=str(data.get("title", "Unmarked Event")),
            category=str(data.get("category", SOCIAL_UNREST)),
            description=str(
                data.get("description", "A pressure spike reaches command.")
            ),
            severity=max(1, int(data.get("severity", 1))),
            choices=[
                EventChoice.from_dict(choice) for choice in data.get("choices", [])
            ],
            consequences=dict(data.get("consequences", {})),
            relation_impact=_normalize_relation_impact(
                str(data.get("relation_impact", "low"))
            ),
            expiration_days=max(1, int(data.get("expiration_days", 3))),
            weight=max(1, int(data.get("weight", 1))),
        )


@dataclass
class ActiveEvent:
    """Calendar-bound unresolved event visible to the command deck."""

    id: str
    template: EventTemplate
    created_day: int
    expires_day: int

    @property
    def title(self) -> str:
        return self.template.title

    @property
    def category(self) -> str:
        return self.template.category

    @property
    def severity(self) -> int:
        return self.template.severity

    @property
    def choices(self) -> list[EventChoice]:
        return self.template.choices

    @property
    def description(self) -> str:
        """Compatibility accessor for UI code that renders template text directly."""
        return self.template.description

    def days_remaining(self, current_day: int) -> int:
        return max(0, self.expires_day - int(current_day) + 1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "template": self.template.to_dict(),
            "created_day": int(self.created_day),
            "expires_day": int(self.expires_day),
        }

    @classmethod
    def from_dict(cls, data: dict | "ActiveEvent") -> "ActiveEvent":
        if isinstance(data, cls):
            return data
        return cls(
            id=str(data.get("id", "event-0")),
            template=EventTemplate.from_dict(data.get("template", {})),
            created_day=int(data.get("created_day", 1)),
            expires_day=int(data.get("expires_day", 1)),
        )


def create_event_templates() -> list[EventTemplate]:
    """Return the first small threat deck for CyberCity 2085."""
    return [
        EventTemplate(
            title="Aegis Shadow Buyout",
            category=ENEMY_CORPORATION_ATTACK,
            description="A rival board cell starts buying informants around Forward Base Kilo.",
            severity=3,
            expiration_days=3,
            weight=3,
            choices=[
                EventChoice(
                    "pay",
                    "Pay counter-intel",
                    {"funds": -30, "faction_pressure": -8},
                    "Spend funds to cool the hostile corporate net.",
                ),
                EventChoice(
                    "burn",
                    "Burn their cutouts",
                    {
                        "agent_stress": 5,
                        "faction_pressure": 6,
                        "mission_availability": -1,
                    },
                    "Agents move fast, but one operation route goes dark.",
                ),
            ],
            consequences={"faction_pressure": 5, "city_stability": -2},
        ),
        EventTemplate(
            title="Mutant Tunnel Surge",
            category=MUTANT_INVASION,
            description="Heat blooms under the transit grid as mutant packs breach service tunnels.",
            severity=4,
            expiration_days=2,
            weight=2,
            choices=[
                EventChoice(
                    "deploy",
                    "Deploy garrisons",
                    {"funds": -20, "city_stability": 5, "agent_stress": 3},
                    "Hold the line with tired patrol teams.",
                ),
                EventChoice(
                    "seal",
                    "Seal the lower decks",
                    {"city_unrest": 6, "city_stability": 2},
                    "Containment saves lives but strands residents.",
                ),
            ],
            consequences={"city_unrest": 8, "city_stability": -5},
        ),
        EventTemplate(
            title="Starvers Fever Line",
            category=STARVERS_OUTBREAK,
            description="Clinic relays report hunger-cult fever spreading through stacked shelters.",
            severity=4,
            expiration_days=3,
            weight=2,
            choices=[
                EventChoice(
                    "relief",
                    "Fund relief drones",
                    {"funds": -25, "city_unrest": -7, "city_stability": 3},
                    "Visible aid wins a fragile calm.",
                ),
                EventChoice(
                    "quarantine",
                    "Hard quarantine",
                    {"agent_stress": 4, "city_unrest": 4, "mission_availability": -1},
                    "Security saves the perimeter and closes a mission window.",
                ),
            ],
            consequences={"city_unrest": 7, "faction_pressure": 3},
        ),
        EventTemplate(
            title="Neon Market Riot",
            category=SOCIAL_UNREST,
            description="Rent strikes and pirate broadcasts turn a market deck into a flashpoint.",
            severity=2,
            expiration_days=2,
            weight=4,
            choices=[
                EventChoice(
                    "listen",
                    "Send negotiators",
                    {"funds": -10, "city_unrest": -5, "city_stability": 2},
                    "A cheap concession buys trust.",
                ),
                EventChoice(
                    "sweep",
                    "Authorize sweep",
                    {"city_unrest": 5, "faction_pressure": -4},
                    "Order returns with cameras watching.",
                ),
            ],
            consequences={"city_unrest": 5, "city_stability": -3},
        ),
        EventTemplate(
            title="Board Knife Vote",
            category=CORPORATE_POLITICS,
            description="Aegis directors demand proof the Warrens project deserves more funding.",
            severity=3,
            expiration_days=4,
            weight=3,
            choices=[
                EventChoice(
                    "lobby",
                    "Lobby the board",
                    {"funds": -20, "faction_pressure": -5},
                    "Political cover dampens the attack.",
                ),
                EventChoice(
                    "profit",
                    "Promise faster returns",
                    {"funds": 15, "agent_stress": 4, "city_stability": -2},
                    "The budget improves and the floor feels colder.",
                ),
            ],
            consequences={"funds": -15, "faction_pressure": 5},
        ),
        EventTemplate(
            title="Council Leverage Demand",
            category=CITY_POLITICS,
            description="Municipal brokers ask Aegis to back their ward boss before permits freeze.",
            severity=2,
            expiration_days=3,
            weight=3,
            choices=[
                EventChoice(
                    "back",
                    "Back the ward boss",
                    {"funds": -15, "city_stability": 3, "faction_pressure": 3},
                    "Permits stay open, but factions notice.",
                ),
                EventChoice(
                    "refuse",
                    "Refuse the demand",
                    {"city_stability": -4, "mission_availability": -1},
                    "Command stays clean while one city route closes.",
                ),
            ],
            consequences={"city_stability": -4, "city_unrest": 3},
        ),
    ]


def city_pressure_score(game_state) -> int:
    """Score district pressure from stability, unrest, and media heat."""
    district = game_state.district
    return max(0, (100 - district.stability) + district.unrest + district.media_heat)


def faction_pressure_score(game_state) -> int:
    """Score the loudest faction threat against the player."""
    if not game_state.factions:
        return 0
    return max(
        faction.hostility_to_player + faction.influence // 2
        for faction in game_state.factions
    )


def strategic_event_chance(game_state) -> float:
    """Return daily event chance from pressure spikes above normal slice tension."""
    city_overload = max(0, city_pressure_score(game_state) - 130) / 300
    faction_overload = max(0, faction_pressure_score(game_state) - 95) / 400
    if city_overload <= 0 and faction_overload <= 0:
        return 0.0
    return min(0.65, 0.05 + city_overload + faction_overload)


def weighted_event_templates(game_state) -> list[tuple[EventTemplate, int]]:
    """Build pressure-aware template weights without duplicating active categories."""
    active_categories = {event.category for event in game_state.active_events}
    city_pressure = city_pressure_score(game_state)
    faction_pressure = faction_pressure_score(game_state)
    weighted: list[tuple[EventTemplate, int]] = []
    for template in create_event_templates():
        if template.category in active_categories:
            continue
        weight = template.weight
        if template.category in {
            SOCIAL_UNREST,
            MUTANT_INVASION,
            STARVERS_OUTBREAK,
            CITY_POLITICS,
        }:
            weight += city_pressure // 35
        if template.category in {
            ENEMY_CORPORATION_ATTACK,
            CORPORATE_POLITICS,
            CITY_POLITICS,
        }:
            weight += faction_pressure // 35
        weighted.append((template, max(1, weight)))
    return weighted


def roll_random_event(
    game_state, rng: random.Random | None = None
) -> ActiveEvent | None:
    """Possibly create one unresolved event for the current campaign day."""
    rng = rng or random
    if rng.random() > strategic_event_chance(game_state):
        return None
    weighted = weighted_event_templates(game_state)
    if not weighted:
        return None
    templates, weights = zip(*weighted)
    template = rng.choices(templates, weights=weights, k=1)[0]
    event_number = getattr(game_state, "next_event_id", 1)
    game_state.next_event_id = event_number + 1
    active_event = ActiveEvent(
        id=f"event-{event_number}",
        template=template,
        created_day=game_state.calendar.current_day,
        expires_day=game_state.calendar.current_day + template.expiration_days - 1,
    )
    game_state.active_events.append(active_event)
    game_state.add_event(
        f"Strategic event: {template.title} ({template.category}, severity {template.severity})."
    )
    return active_event


def expire_events(game_state) -> list[ActiveEvent]:
    """Expire unresolved events and apply their unattended consequences."""
    expired: list[ActiveEvent] = []
    remaining: list[ActiveEvent] = []
    for active_event in game_state.active_events:
        if game_state.calendar.current_day > active_event.expires_day:
            expired.append(active_event)
            apply_event_effects(game_state, active_event.template.consequences)
            game_state.add_event(
                f"Expired event: {active_event.title} fallout hits command."
            )
        else:
            remaining.append(active_event)
    game_state.active_events = remaining
    return expired


def apply_event_choice(game_state, event_id: str, choice_key: str) -> bool:
    """Resolve an active event by applying a selected response choice."""
    for active_event in list(game_state.active_events):
        if active_event.id != event_id:
            continue
        for choice in active_event.choices:
            if choice.key != choice_key:
                continue
            apply_event_effects(game_state, choice.effects)
            from ..relationships.impact_tracker import record_relation_impact

            if choice.relation_impact == "high":
                record_relation_impact(
                    game_state,
                    source=f"event:{active_event.id}:{choice.key}",
                    level=choice.relation_impact,
                    context=active_event.title,
                )
            game_state.active_events.remove(active_event)
            game_state.add_event(
                f"Event response: {active_event.title} -> {choice.label}."
            )
            return True
    return False


def apply_event_effects(game_state, effects: dict[str, Any]) -> None:
    """Apply the small set of strategic levers events are allowed to touch."""
    funds = int(effects.get("funds", 0))
    if funds > 0:
        game_state.add_funds(funds, "event_choice", "Strategic event windfall.")
    elif funds < 0:
        game_state.spend_funds(abs(funds), "event_choice", "Strategic event response.")

    agent_stress = int(effects.get("agent_stress", 0))
    if agent_stress:
        for character in game_state.characters:
            character.stress = max(0, min(100, character.stress + agent_stress))

    district = game_state.district
    if "city_stability" in effects:
        district.stability += int(effects["city_stability"])
    if "city_unrest" in effects:
        district.unrest += int(effects["city_unrest"])
    if "media_heat" in effects:
        district.media_heat += int(effects["media_heat"])
    district.clamp_pressure()

    faction_pressure = int(effects.get("faction_pressure", 0))
    if faction_pressure and game_state.factions:
        faction_name = effects.get("faction")
        faction = game_state.get_faction(faction_name) if faction_name else None
        if faction is None:
            faction = max(
                game_state.factions, key=lambda item: item.hostility_to_player
            )
        faction.hostility_to_player += faction_pressure
        faction.clamp_pressure()

    mission_delta = int(effects.get("mission_availability", 0))
    if mission_delta < 0:
        _lock_first_available_mission(game_state)
    elif mission_delta > 0:
        del game_state.unavailable_mission_ids[:mission_delta]


def _lock_first_available_mission(game_state) -> None:
    """Mark one mission unavailable without removing the template from saves."""
    unavailable = set(game_state.unavailable_mission_ids)
    for mission in game_state.mission_templates:
        if mission.id not in unavailable:
            game_state.unavailable_mission_ids.append(mission.id)
            return
