"""Directional low/high cover rules for tactical combat."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.unit import Unit

CELL = 32
_COVER_BONUS = {"low": 1, "high": 2}
COVER_LOW_COL = (255, 220, 60, 60)
COVER_HIGH_COL = (80, 220, 255, 80)


@dataclass
class CoverNode:
    grid_x: int
    grid_y: int
    cover_type: str = "low"
    passable: bool = True

    @property
    def world_x(self) -> int:
        return self.grid_x * CELL

    @property
    def world_y(self) -> int:
        return self.grid_y * CELL


def generate_cover_nodes(map_index: int | None, map_width: int = 1280, map_height: int = 720, seed_offset: int = 0) -> list[CoverNode]:
    """Generate a stable compact cover layout for one map seed."""
    rng = random.Random((map_index or 0) + seed_offset)
    cols, rows = map_width // CELL, map_height // CELL
    nodes: list[CoverNode] = []
    for _ in range(rng.randint(3, 6)):
        row, start = rng.randint(3, rows - 5), rng.randint(1, cols // 3)
        cover_type = rng.choice(["low", "low", "high"])
        for col in range(start, start + rng.randint(3, 7)):
            if 0 < col < cols:
                nodes.append(CoverNode(col, row, cover_type))
    occupied = {(node.grid_x, node.grid_y) for node in nodes}
    for _ in range(rng.randint(4, 10)):
        for _attempt in range(20):
            cell = (rng.randint(1, cols - 2), rng.randint(2, rows - 3))
            if cell not in occupied:
                nodes.append(CoverNode(*cell, rng.choice(["low", "low", "high"])))
                occupied.add(cell)
                break
    return nodes


def node_at(gx: int, gy: int, nodes: list[CoverNode]) -> CoverNode | None:
    return next((node for node in nodes if (node.grid_x, node.grid_y) == (gx, gy)), None)


def unit_in_cover(unit: "Unit", nodes: list[CoverNode]) -> CoverNode | None:
    gx, gy = unit.position[0] // CELL, unit.position[1] // CELL
    standing = node_at(gx, gy, nodes)
    if standing:
        return standing
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        adjacent = node_at(gx + dx, gy + dy, nodes)
        if adjacent:
            return adjacent
    return None


def cover_defense_bonus(unit: "Unit", nodes: list[CoverNode]) -> int:
    node = unit_in_cover(unit, nodes)
    return _COVER_BONUS.get(node.cover_type, 0) if node else 0


def directional_cover(attacker: "Unit", defender: "Unit", nodes: list[CoverNode]) -> tuple[CoverNode | None, int]:
    """Return adjacent cover only when its face points toward the attacker."""
    dgx, dgy = defender.position[0] // CELL, defender.position[1] // CELL
    agx, agy = attacker.position[0] // CELL, attacker.position[1] // CELL
    candidates: list[tuple[int, CoverNode]] = []
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        node = node_at(dgx + dx, dgy + dy, nodes)
        if node and (agx - dgx) * dx + (agy - dgy) * dy > 0:
            candidates.append((_COVER_BONUS.get(node.cover_type, 0), node))
    if not candidates:
        return None, 0
    bonus, node = max(candidates, key=lambda item: item[0])
    return node, bonus


def is_flanking(attacker: "Unit", defender: "Unit", nodes: list[CoverNode]) -> bool:
    if unit_in_cover(defender, nodes) is None:
        return False
    return directional_cover(attacker, defender, nodes)[1] == 0


def flanking_bonus(attacker: "Unit", defender: "Unit", nodes: list[CoverNode]) -> int:
    return 20 if is_flanking(attacker, defender, nodes) else 0
