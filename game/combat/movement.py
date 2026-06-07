"""Shared tactical movement rules for combat deployment, player input, and AI."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import Literal, Protocol

from game.unit import Unit

CELL_SIZE = 32
MovementMode = Literal["fluid", "tactical_grid"]


class WalkabilityProfile(Protocol):
    """Minimal terrain contract used by combat movement."""

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether the cell at pixel/grid position ``(x, y)`` can be entered."""


def _living_units(units: Iterable[Unit] | None) -> Iterable[Unit]:
    if units is None:
        return ()
    return (unit for unit in units if getattr(unit, "health", 0) > 0)


def _is_occupied(
    x: int,
    y: int,
    allied_units: Iterable[Unit] | None,
    enemy_units: Iterable[Unit] | None,
    *,
    exclude: Unit | None = None,
) -> bool:
    """Return whether any living unit except ``exclude`` occupies a destination."""
    for unit in [*_living_units(allied_units), *_living_units(enemy_units)]:
        if unit is exclude:
            continue
        if getattr(unit, "position", None) == (x, y):
            return True
    return False


def can_enter_cell(
    x: int,
    y: int,
    *,
    terrain_profile: WalkabilityProfile | None = None,
    allied_units: Iterable[Unit] | None = None,
    enemy_units: Iterable[Unit] | None = None,
    exclude: Unit | None = None,
    movement_mode: MovementMode = "tactical_grid",
) -> bool:
    """Return whether the shared combat movement rule allows entering a cell.

    ``fluid`` keeps the looser legacy feel by allowing units to pass through
    occupied cells while still honoring terrain masks. ``tactical_grid`` blocks
    both terrain and living unit occupancy.
    """
    if (
        terrain_profile is not None
        and hasattr(terrain_profile, "is_walkable")
        and not terrain_profile.is_walkable(x, y)
    ):
        return False
    if movement_mode == "tactical_grid" and _is_occupied(
        x, y, allied_units, enemy_units, exclude=exclude
    ):
        return False
    return True


def reachable_cells(
    start: tuple[int, int],
    movement_budget: int,
    *,
    width: int,
    height: int,
    cell_size: int = CELL_SIZE,
    terrain_profile: WalkabilityProfile | None = None,
    allied_units: Iterable[Unit] | None = None,
    enemy_units: Iterable[Unit] | None = None,
    exclude: Unit | None = None,
    movement_mode: MovementMode = "tactical_grid",
) -> set[tuple[int, int]]:
    """Return cells reachable from ``start`` within a cardinal-step budget."""
    if movement_budget < 0:
        return set()

    reachable: set[tuple[int, int]] = {start}
    seen: set[tuple[int, int]] = {start}
    queue = deque([(start[0], start[1], 0)])

    while queue:
        x, y, steps = queue.popleft()
        if steps >= movement_budget:
            continue
        for next_x, next_y in (
            (x + cell_size, y),
            (x - cell_size, y),
            (x, y + cell_size),
            (x, y - cell_size),
        ):
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue
            if (next_x, next_y) in seen:
                continue
            if not can_enter_cell(
                next_x,
                next_y,
                terrain_profile=terrain_profile,
                allied_units=allied_units,
                enemy_units=enemy_units,
                exclude=exclude,
                movement_mode=movement_mode,
            ):
                continue
            seen.add((next_x, next_y))
            reachable.add((next_x, next_y))
            queue.append((next_x, next_y, steps + 1))
    return reachable


def path_to_cell(
    start: tuple[int, int],
    goal: tuple[int, int],
    movement_budget: int,
    *,
    width: int,
    height: int,
    cell_size: int = CELL_SIZE,
    terrain_profile: WalkabilityProfile | None = None,
    allied_units: Iterable[Unit] | None = None,
    enemy_units: Iterable[Unit] | None = None,
    exclude: Unit | None = None,
    movement_mode: MovementMode = "tactical_grid",
) -> list[tuple[int, int]] | None:
    """Return the shortest cardinal path from ``start`` to ``goal``, if reachable."""
    if start == goal:
        return [start]
    if movement_budget < 0:
        return None

    seen: set[tuple[int, int]] = {start}
    previous: dict[tuple[int, int], tuple[int, int]] = {}
    queue = deque([(start[0], start[1], 0)])

    while queue:
        x, y, steps = queue.popleft()
        if steps >= movement_budget:
            continue
        for next_x, next_y in (
            (x + cell_size, y),
            (x - cell_size, y),
            (x, y + cell_size),
            (x, y - cell_size),
        ):
            cell = (next_x, next_y)
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue
            if cell in seen:
                continue
            if not can_enter_cell(
                next_x,
                next_y,
                terrain_profile=terrain_profile,
                allied_units=allied_units,
                enemy_units=enemy_units,
                exclude=exclude,
                movement_mode=movement_mode,
            ):
                continue
            previous[cell] = (x, y)
            if cell == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(previous[path[-1]])
                path.reverse()
                return path
            seen.add(cell)
            queue.append((next_x, next_y, steps + 1))
    return None
