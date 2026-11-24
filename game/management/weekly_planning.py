"""Weekly command forecast and one consequential directive per week."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .spec_ops_assets import maintenance_cost_for_assets
from .economy import WEEKLY_DIRECTIVE_COSTS

if TYPE_CHECKING:
    from game.gamestate import GameState


@dataclass(frozen=True)
class WeeklyDirective:
    id: str
    title: str
    cost: int
    promise: str
    consequence: str


@dataclass(frozen=True)
class ManagementForecast:
    week: int
    days_to_income: int
    projected_income: int
    asset_upkeep: int
    ready_agents: int
    total_agents: int
    district_pressure: int
    threat_level: str
    urgent_event: str
    urgent_event_days: int | None
    directive_locked: bool
    selected_directive: str

    @property
    def projected_net(self) -> int:
        return self.projected_income - self.asset_upkeep


DIRECTIVES: tuple[WeeklyDirective, ...] = (
    WeeklyDirective(
        id="civil_defense",
        title="FORTIFY THE WARRENS",
        cost=WEEKLY_DIRECTIVE_COSTS["civil_defense"],
        promise="Stability +8, unrest -6, security +5.",
        consequence="Visible patrols raise media heat +2.",
    ),
    WeeklyDirective(
        id="crew_recovery",
        title="BRING THEM HOME",
        cost=WEEKLY_DIRECTIVE_COSTS["crew_recovery"],
        promise="All agents recover 15 stress and 1 recovery day.",
        consequence="The city receives no direct protection this week.",
    ),
    WeeklyDirective(
        id="black_intel",
        title="OWN THE NIGHT",
        cost=WEEKLY_DIRECTIVE_COSTS["black_intel"],
        promise="Gain 4 intel, 2 influence, black ops +5.",
        consequence="Covert activity raises media heat +8.",
    ),
)
DIRECTIVES_BY_ID = {directive.id: directive for directive in DIRECTIVES}


def build_management_forecast(game_state: "GameState") -> ManagementForecast:
    """Build a read-only forecast from current management state."""

    calendar = game_state.calendar
    district = game_state.district
    pressure = max(0, min(100, (100 - district.stability + district.unrest + district.media_heat) // 3))
    threat_level = "critical" if pressure >= 70 else "high" if pressure >= 50 else "guarded" if pressure >= 30 else "stable"
    ready_agents = sum(
        1
        for agent in game_state.characters
        if agent.stats.hp > 0 and agent.recovery_turns <= 0 and agent.stress < 85
    )

    urgent_event = "No unresolved crisis"
    urgent_days: int | None = None
    if game_state.active_events:
        active = min(
            game_state.active_events,
            key=lambda event: max(0, int(event.expires_day) - calendar.current_day),
        )
        urgent_days = max(0, int(active.expires_day) - calendar.current_day)
        urgent_event = str(active.title)

    return ManagementForecast(
        week=calendar.current_week,
        days_to_income=max(0, calendar.next_week_start_day - calendar.current_day),
        projected_income=(
            game_state.projected_weekly_income
            + game_state.compute_budget() * calendar.days_per_week
        ),
        asset_upkeep=maintenance_cost_for_assets(game_state.spec_ops_assets),
        ready_agents=ready_agents,
        total_agents=len(game_state.characters),
        district_pressure=pressure,
        threat_level=threat_level,
        urgent_event=urgent_event,
        urgent_event_days=urgent_days,
        directive_locked=game_state.weekly_directive_week == calendar.current_week,
        selected_directive=game_state.weekly_directive_id,
    )


def apply_weekly_directive(game_state: "GameState", directive_id: str) -> tuple[bool, str]:
    """Apply one weekly directive atomically and return player-facing feedback."""

    directive = DIRECTIVES_BY_ID.get(directive_id)
    if directive is None:
        return False, "Unknown weekly directive."
    week = game_state.calendar.current_week
    if game_state.weekly_directive_week == week:
        chosen = DIRECTIVES_BY_ID.get(game_state.weekly_directive_id)
        return False, f"Week {week} directive already set: {chosen.title if chosen else game_state.weekly_directive_id}."
    if not game_state.spend_funds(directive.cost, "weekly_directive", directive.title):
        return False, f"{directive.title} requires ₦{directive.cost:,}."

    district = game_state.district
    if directive.id == "civil_defense":
        district.stability += 8
        district.unrest -= 6
        district.media_heat += 2
        game_state.corp_budget["security"] = game_state.corp_budget.get("security", 0) + 5
    elif directive.id == "crew_recovery":
        for agent in game_state.characters:
            agent.stress = max(0, agent.stress - 15)
            agent.recovery_turns = max(0, agent.recovery_turns - 1)
    elif directive.id == "black_intel":
        game_state.strategic_resources["intel"] = game_state.strategic_resources.get("intel", 0) + 4
        game_state.strategic_resources["influence"] = game_state.strategic_resources.get("influence", 0) + 2
        game_state.corp_budget["black_ops"] = game_state.corp_budget.get("black_ops", 0) + 5
        district.media_heat += 8
    district.clamp_pressure()

    game_state.weekly_directive_week = week
    game_state.weekly_directive_id = directive.id
    message = f"Week {week} directive: {directive.title}. {directive.promise}"
    game_state.add_event(message)
    return True, message
