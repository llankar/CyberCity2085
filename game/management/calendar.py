"""Strategic campaign calendar for management-phase pacing.

The calendar is intentionally small: it tracks day-scale campaign time so
mission fallout, passive funding, and agent recovery all move from one shared
clock instead of separate UI-only turns.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StrategicCalendar:
    """Track campaign day, week, month, and a readable date label."""

    current_day: int = 1
    days_per_week: int = 7
    days_per_month: int = 30
    era_label: str = "2085"
    _last_week: int = field(default=1, init=False, repr=False)

    def __post_init__(self) -> None:
        self.current_day = max(1, int(self.current_day))
        self.days_per_week = max(1, int(self.days_per_week))
        self.days_per_month = max(self.days_per_week, int(self.days_per_month))
        self._last_week = self.current_week

    @property
    def current_week(self) -> int:
        """Return the one-indexed campaign week for the current day."""
        return ((self.current_day - 1) // self.days_per_week) + 1

    @property
    def current_month(self) -> int:
        """Return the one-indexed campaign month for the current day."""
        return ((self.current_day - 1) // self.days_per_month) + 1

    @property
    def day_of_month(self) -> int:
        """Return the one-indexed day inside the current campaign month."""
        return ((self.current_day - 1) % self.days_per_month) + 1

    @property
    def campaign_date_label(self) -> str:
        """Return a compact in-world label for dashboards and logs."""
        return self.date_label_for_day(self.current_day)

    @property
    def next_week_start_day(self) -> int:
        """Return the campaign day that opens the next weekly cycle."""
        return self.current_week * self.days_per_week + 1

    def date_label_for_day(self, day: int) -> str:
        """Return the compact in-world label for an arbitrary campaign day."""
        day = max(1, int(day))
        month = ((day - 1) // self.days_per_month) + 1
        day_of_month = ((day - 1) % self.days_per_month) + 1
        return f"{self.era_label}.M{month:02d}.D{day_of_month:02d}"

    @property
    def is_new_week(self) -> bool:
        """Return whether the most recent advancement crossed into a new week."""
        return self.current_week != self._last_week

    def advance_days(self, days: int) -> None:
        """Advance the calendar by a positive number of days."""
        if days < 0:
            raise ValueError("days must be non-negative")
        if days == 0:
            self._last_week = self.current_week
            return
        self._last_week = self.current_week
        self.current_day += int(days)

    def advance_one_day(self) -> None:
        """Advance the calendar exactly one campaign day."""
        self.advance_days(1)

    def to_dict(self) -> dict:
        """Serialize the strategic calendar for save files."""
        return {
            "current_day": self.current_day,
            "days_per_week": self.days_per_week,
            "days_per_month": self.days_per_month,
            "era_label": self.era_label,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "StrategicCalendar":
        """Restore a calendar from save data, tolerating older save files."""
        data = data or {}
        return cls(
            current_day=int(data.get("current_day", 1)),
            days_per_week=int(data.get("days_per_week", 7)),
            days_per_month=int(data.get("days_per_month", 30)),
            era_label=str(data.get("era_label", "2085")),
        )
