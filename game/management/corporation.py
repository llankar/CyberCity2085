"""Small corporation finance rules for recurring management funding.

The model is intentionally narrow: the calendar decides *when* a new week
opens, and this module decides *how much* support the corporation receives.
"""

from __future__ import annotations

from dataclasses import dataclass

from .calendar import StrategicCalendar
from .funds import CorporateFunds


@dataclass
class CorporationFinance:
    """Recurring weekly funding profile for the player's corporation."""

    weekly_stipend: int = 75
    city_support_modifier: float = 0.10
    political_pressure_modifier: float = -0.05
    debt_upkeep: int = 15

    def projected_weekly_income(self) -> int:
        """Return the next net weekly payment after modifiers and upkeep."""
        modifier = 1 + self.city_support_modifier + self.political_pressure_modifier
        gross_income = round(self.weekly_stipend * modifier)
        return max(0, gross_income - self.debt_upkeep)

    def next_income_day(self, calendar: StrategicCalendar) -> int:
        """Return the campaign day when the next weekly payment will arrive."""
        return calendar.next_week_start_day

    def next_income_date_label(self, calendar: StrategicCalendar) -> str:
        """Return a readable date label for the next weekly payment."""
        return calendar.date_label_for_day(self.next_income_day(calendar))

    def apply_weekly_income(
        self,
        ledger: CorporateFunds,
        calendar: StrategicCalendar,
        source: str = "weekly_corporate_funding",
    ) -> int:
        """Add this week's corporation funding to the ledger and return it."""
        amount = self.projected_weekly_income()
        if amount <= 0:
            return 0
        ledger.add_funds(
            amount,
            source,
            f"Week {calendar.current_week} corporate funding cycle.",
        )
        return amount

    def to_dict(self) -> dict:
        """Serialize recurring finance settings for save files."""
        return {
            "weekly_stipend": self.weekly_stipend,
            "city_support_modifier": self.city_support_modifier,
            "political_pressure_modifier": self.political_pressure_modifier,
            "debt_upkeep": self.debt_upkeep,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "CorporationFinance":
        """Restore finance settings while tolerating older save files."""
        data = data or {}
        return cls(
            weekly_stipend=int(data.get("weekly_stipend", 75)),
            city_support_modifier=float(data.get("city_support_modifier", 0.10)),
            political_pressure_modifier=float(
                data.get("political_pressure_modifier", -0.05)
            ),
            debt_upkeep=int(data.get("debt_upkeep", 15)),
        )
