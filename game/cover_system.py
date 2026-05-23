"""CyberCity 2085 — Tactical Cover System.

Manages low/high cover nodes on the battle map, flanking detection,
and the defense bonuses they confer — XCOM-style.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.unit import Unit

CELL = 32

# Cover type → defense bonus
_COVER_BONUS: dict[str, int] = {
    "low":  1,   # half cover (+1 def)
    "high": 2,   # full cover (+2 def)
}

# Visual colours (RGBA) exposed so the HUD can draw them
COVER_LOW_COL  = (255, 220, 60,  60)   # yellow-ish
COVER_HIGH_COL = (80,  220, 255, 80)   # cyan-ish


@dataclass
class CoverNode:
    """A single grid tile that offers cover."""
    grid_x: int              # tile column
    grid_y: int              # tile row
    cover_type: str = "low"  # "low" | "high"
    passable: bool = True    # True if units can stand on this tile

    @property
    def world_x(self) -> int:
        return self.grid_x * CELL

    @property
    def world_y(self) -> int:
        return self.grid_y * CELL


def generate_cover_nodes(
    map_index: int | None,
    map_width: int = 1280,
    map_height: int = 720,
    seed_offset: int = 0,
) -> list[CoverNode]:
    """Procedurally generate cover nodes for the given map index.

    The pattern is deterministic per map_index so the layout doesn't
    change between turns.
    """
    rng = random.Random((map_index or 0) + seed_offset)
    cols = map_width  // CELL
    rows = map_height // CELL

    nodes: list[CoverNode] = []

    # --- Row-based cover barriers (like walls of containers / cars)
    num_rows = rng.randint(3, 6)
    for _ in range(num_rows):
        row = rng.randint(3, rows - 5)
        start_col = rng.randint(1, cols // 3)
        length = rng.randint(3, 7)
        ctype = rng.choice(["low", "low", "high"])
        for c in range(start_col, start_col + length):
            if 0 < c < cols:
                nodes.append(CoverNode(c, row, ctype))

    # --- Scattered individual pieces
    num_scatter = rng.randint(4, 10)
    occupied = {(n.grid_x, n.grid_y) for n in nodes}
    for _ in range(num_scatter):
        for _attempt in range(20):
            col = rng.randint(1, cols - 2)
            row = rng.randint(2, rows - 3)
            if (col, row) not in occupied:
                ctype = rng.choice(["low", "low", "high"])
                nodes.append(CoverNode(col, row, ctype))
                occupied.add((col, row))
                break

    return nodes


def node_at(gx: int, gy: int, nodes: list[CoverNode]) -> CoverNode | None:
    for n in nodes:
        if n.grid_x == gx and n.grid_y == gy:
            return n
    return None


def unit_in_cover(unit: "Unit", nodes: list[CoverNode]) -> CoverNode | None:
    """Return the CoverNode a unit is standing on/adjacent to, if any."""
    gx = unit.position[0] // CELL
    gy = unit.position[1] // CELL
    # Standing on the node
    n = node_at(gx, gy, nodes)
    if n:
        return n
    # Adjacent to a node (unit is behind it from enemy direction)
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        n = node_at(gx + dx, gy + dy, nodes)
        if n:
            return n
    return None


def cover_defense_bonus(unit: "Unit", nodes: list[CoverNode]) -> int:
    """Return the defense bonus the unit gains from nearby cover."""
    n = unit_in_cover(unit, nodes)
    if n is None:
        return 0
    return _COVER_BONUS.get(n.cover_type, 0)


def is_flanking(attacker: "Unit", defender: "Unit", nodes: list[CoverNode]) -> bool:
    """Return True when the attacker is flanking the defender.

    A unit is flanked when the attacker approaches from the *opposite* side
    of the cover node the defender is hiding behind, negating all cover bonuses.
    """
    n = unit_in_cover(defender, nodes)
    if n is None:
        return False  # No cover → not a flanking question

    # Vector from cover to defender
    dgx = defender.position[0] // CELL
    dgy = defender.position[1] // CELL
    agx = attacker.position[0] // CELL
    agy = attacker.position[1] // CELL

    # Cover is between defender and attacker when cover node is between them
    # Simplified: if attacker is on same side as cover node relative to defender → flanking
    cx, cy = n.grid_x, n.grid_y
    # Cover protects if it's between attacker and defender
    def between(a, b, c):
        lo, hi = min(a, b), max(a, b)
        return lo <= c <= hi

    if between(dgx, agx, cx) and between(dgy, agy, cy):
        return False  # Cover is shielding the defender
    return True       # Attacker came from unprotected flank


def flanking_bonus(attacker: "Unit", defender: "Unit", nodes: list[CoverNode]) -> int:
    """Return a hit-chance bonus for flanking (+20 to percent chance)."""
    return 20 if is_flanking(attacker, defender, nodes) else 0
