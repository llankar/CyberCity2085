"""Pure battlefield language: sight lines, hazards, and safe map plans."""

from __future__ import annotations

from dataclasses import dataclass, replace
from collections import deque
from heapq import heappop, heappush
import random

from game.cover_system import CELL, CoverNode, generate_cover_nodes
from game.unit import STATUS_BURNING, STATUS_CONTAMINATED


@dataclass(frozen=True)
class SightLine:
    clear: bool
    blocker: CoverNode | None = None


@dataclass(frozen=True)
class HazardZone:
    kind: str
    position: tuple[int, int]
    radius_cells: int = 1
    expires_after_turn: int | None = None

    def contains(self, position: tuple[int, int]) -> bool:
        dx, dy = position[0] - self.position[0], position[1] - self.position[1]
        return dx * dx + dy * dy <= (self.radius_cells * CELL) ** 2


@dataclass(frozen=True)
class HazardEffect:
    kind: str
    damage: int = 0
    ap_lost: int = 0
    status: str = ""


@dataclass(frozen=True)
class BattlefieldPlan:
    cover_nodes: tuple[CoverNode, ...]
    hazards: tuple[HazardZone, ...]


def connect_inferred_terrain(terrain_profile, anchors):
    """Add explicit tactical access lanes through uncertain art-derived cells.

    Binary authored masks remain authoritative. For inferred art, shortest
    weighted paths prefer existing ground and connect every mission anchor.
    Added cells are returned for a visible lane overlay in the battle adapter.
    """
    if terrain_profile is None or terrain_profile.threshold == 255 or not anchors:
        return terrain_profile, frozenset()
    step = terrain_profile.cell_size
    points = [
        (min(terrain_profile.width // step, max(0, round(x / step))) * step,
         min(terrain_profile.height // step, max(0, round(y / step))) * step)
        for x, y in anchors
    ]
    walkable = set(terrain_profile.walkable_cells)
    original = set(walkable)
    origin = points[0]
    walkable.add(origin)
    for target in points[1:]:
        frontier = [(0, origin)]
        costs = {origin: 0}
        previous = {}
        while frontier:
            cost, cell = heappop(frontier)
            if cost != costs[cell]:
                continue
            if cell == target:
                break
            x, y = cell
            for adjacent in ((x+step, y), (x-step, y), (x, y+step), (x, y-step)):
                nx, ny = adjacent
                if not (0 <= nx <= terrain_profile.width and 0 <= ny <= terrain_profile.height):
                    continue
                next_cost = cost + (1 if adjacent in walkable else 5)
                if next_cost < costs.get(adjacent, float("inf")):
                    costs[adjacent] = next_cost
                    previous[adjacent] = cell
                    heappush(frontier, (next_cost, adjacent))
        cursor = target
        while cursor != origin:
            walkable.add(cursor)
            cursor = previous[cursor]
    return replace(terrain_profile, walkable_cells=frozenset(walkable)), frozenset(walkable - original)


def reachable_objective_positions(
    positions: tuple[tuple[int, int], ...], deployment: tuple[int, int], terrain_profile
) -> tuple[tuple[int, int], ...]:
    """Keep every objective beat in the deployment's connected walkable region.

    Art-derived walkability can fragment a map. Relocate inaccessible markers to
    the closest reachable cell rather than declaring a false reachable anchor
    or carving invisible passages through the map.
    """
    if terrain_profile is None or not positions:
        return positions
    step = terrain_profile.cell_size
    origin = (round(deployment[0] / step) * step, round(deployment[1] / step) * step)
    if not terrain_profile.is_walkable(*origin):
        return positions
    reachable = {origin}
    queue = deque([origin])
    while queue:
        x, y = queue.popleft()
        for adjacent in ((x+step, y), (x-step, y), (x, y+step), (x, y-step)):
            if adjacent not in reachable and terrain_profile.is_walkable(*adjacent):
                reachable.add(adjacent)
                queue.append(adjacent)
    resolved = []
    for target in positions:
        candidates = reachable.difference(resolved) or reachable
        nearest = min(candidates, key=lambda cell: (
            (cell[0]-target[0])**2 + (cell[1]-target[1])**2, cell
        ))
        resolved.append(nearest)
    return tuple(resolved)


def trace_sight_line(start: tuple[int, int], end: tuple[int, int], cover_nodes: list[CoverNode] | None) -> SightLine:
    """High cover between units blocks direct attacks; low cover does not."""
    ax, ay = start
    bx, by = end
    vx, vy = bx - ax, by - ay
    length2 = vx * vx + vy * vy
    if not cover_nodes or not length2:
        return SightLine(True)
    for node in cover_nodes:
        if node.cover_type != "high":
            continue
        px, py = node.world_x, node.world_y
        # Adjacent cover is a defensive face: units can peek around it. Only
        # intervening structures farther from both endpoints block the shot.
        if min((px-ax)**2 + (py-ay)**2, (px-bx)**2 + (py-by)**2) <= CELL**2:
            continue
        dot = (px - ax) * vx + (py - ay) * vy
        if 0 < dot < length2:
            distance = abs((px - ax) * vy - (py - ay) * vx) / length2**0.5
            if distance <= CELL * 0.42:
                return SightLine(False, node)
    return SightLine(True)


def apply_hazard(unit, zone: HazardZone) -> HazardEffect:
    if not zone.contains(unit.position) or unit.health <= 0:
        return HazardEffect(zone.kind)
    if zone.kind == "fire":
        unit.health = max(0, unit.health - 2)
        if unit.stats:
            unit.stats.hp = unit.health
        unit.apply_status(STATUS_BURNING)
        return HazardEffect("fire", damage=2, status=STATUS_BURNING)
    if zone.kind == "contamination":
        unit.health = max(0, unit.health - 1)
        if unit.stats:
            unit.stats.hp = unit.health
        unit.apply_status(STATUS_CONTAMINATED)
        return HazardEffect("contamination", damage=1, status=STATUS_CONTAMINATED)
    if zone.kind == "sludge":
        lost = min(1, unit.action_points)
        unit.action_points -= lost
        unit.health = max(0, unit.health - 1)
        if unit.stats:
            unit.stats.hp = unit.health
        return HazardEffect("sludge", damage=1, ap_lost=lost)
    if zone.kind == "blackout":
        lost = min(1, unit.action_points)
        unit.action_points -= lost
        return HazardEffect("blackout", ap_lost=lost)
    return HazardEffect(zone.kind)


def build_battlefield_plan(
    *, map_index: int, width: int, height: int,
    reserved_positions: tuple[tuple[int, int], ...], terrain_profile=None,
    objective_kind: str = "eliminate",
) -> BattlefieldPlan:
    """Generate cover/hazards without occupying spawns or objective anchors."""
    reserved = {(round(x / CELL) * CELL, round(y / CELL) * CELL) for x, y in reserved_positions}
    if terrain_profile is not None:
        # Cover belongs to map geometry: expose the boundary of the blocked
        # regions in the background's walkability profile, never random walls
        # on otherwise open terrain. Access lanes remain open.
        step = terrain_profile.cell_size
        cover = tuple(
            CoverNode(x // CELL, y // CELL, "high", passable=False)
            for x in range(0, width + 1, step)
            for y in range(0, height + 1, step)
            if (x, y) not in reserved
            and not terrain_profile.is_walkable(x, y)
            and (terrain_profile.sight_blocked_cells is None or (x, y) in terrain_profile.sight_blocked_cells)
            and any(terrain_profile.is_walkable(nx, ny) for nx, ny in (
                (x+step, y), (x-step, y), (x, y+step), (x, y-step)
            ))
        )
    else:
        cover = tuple(
            node for node in generate_cover_nodes(map_index, width, height)
            if (node.world_x, node.world_y) not in reserved
        )
    rng = random.Random(map_index * 101 + len(reserved) * 17)
    kinds = ["blackout", "fire"] if objective_kind in {"civilian_rescue", "extract"} else ["fire", "contamination", "blackout"]
    candidates = [
        (x, y) for x in range(CELL * 4, width - CELL * 3, CELL)
        for y in range(CELL * 4, height - CELL * 3, CELL)
        if (x, y) not in reserved and (terrain_profile is None or terrain_profile.is_walkable(x, y))
        and all((x-rx)**2 + (y-ry)**2 > (CELL*2)**2 for rx, ry in reserved)
    ]
    rng.shuffle(candidates)
    hazards = tuple(HazardZone(kind, position) for kind, position in zip(kinds, candidates))
    return BattlefieldPlan(cover, hazards)
