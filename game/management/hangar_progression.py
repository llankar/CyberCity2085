"""Persistent Hangar capacity progression and its fixed campaign prices."""

from dataclasses import dataclass


HANGAR_LEVELS = (
    (1, "Standard Hangar", 5, 0),
    (2, "Expanded Quarters", 6, 20_000),
    (3, "Tactical Hangar", 7, 60_000),
    (4, "Operations Base", 8, 180_000),
)


@dataclass
class HangarProgression:
    level: int = 1

    def __post_init__(self) -> None:
        self.level = min(4, max(1, int(self.level)))

    @property
    def name(self) -> str:
        return HANGAR_LEVELS[self.level - 1][1]

    @property
    def squad_capacity(self) -> int:
        return HANGAR_LEVELS[self.level - 1][2]

    @property
    def is_max_level(self) -> bool:
        return self.level == len(HANGAR_LEVELS)

    @property
    def next_upgrade(self) -> tuple[int, str, int, int] | None:
        return None if self.is_max_level else HANGAR_LEVELS[self.level]

    @property
    def next_cost(self) -> int | None:
        upgrade = self.next_upgrade
        return None if upgrade is None else upgrade[3]

    def to_dict(self) -> dict:
        return {"level": self.level}

    @classmethod
    def from_dict(cls, data: dict | None, roster_size: int = 0) -> "HangarProgression":
        if data:
            return cls(data.get("level", 1))
        # Legacy saves keep every operative. Their Hangar is migrated to the
        # lowest legitimate level able to contain that already-owned roster.
        migrated_level = min(4, max(1, roster_size - 4))
        return cls(migrated_level)
