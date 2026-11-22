"""Place an encounter on authored terrain without erasing any obstacles."""

from collections import deque
from dataclasses import dataclass

MAX_OPENING_MOVES = 3  # Two AP plus the Starver movement-only stride.
CONTAINMENT_HALF_WIDTH = 96


def containment_breach_cells(region, breach_y, center_x, half_width=CONTAINMENT_HALF_WIDTH):
    """Cells whose centres form the marker-local containment breach."""
    local = {cell for cell in region
             if cell[1] <= breach_y and abs(cell[0] - center_x) <= half_width}
    return local or {cell for cell in region if cell[1] <= breach_y}


def defense_approach_distances(region, objectives):
    """Best-case movement distance to any cell that would breach the defense."""
    goals = {cell for cell in region
             if any(max(abs(cell[0]-x), abs(cell[1]-y)) <= 32 for x, y in objectives)}
    return approach_distances(region, goals)


def approach_distances(region, goals):
    """Shortest cardinal path to any breach cell, ignoring units that may move."""
    field, queue = {cell: 0 for cell in goals}, deque(goals)
    while queue:
        x, y = queue.popleft()
        for cell in ((x+32, y), (x-32, y), (x, y+32), (x, y-32)):
            if cell in region and cell not in field:
                field[cell] = field[x, y] + 1
                queue.append(cell)
    return field


@dataclass(frozen=True)
class EncounterPlacement:
    allies: tuple
    enemies: tuple
    objectives: tuple
    deployment_cells: frozenset
    breach_y: int | None


def connected_regions(profile):
    remaining = set(profile.walkable_cells)
    regions = []
    step = profile.cell_size
    while remaining:
        origin = min(remaining)
        remaining.remove(origin)
        region, queue = {origin}, deque([origin])
        while queue:
            x, y = queue.popleft()
            for cell in ((x+step, y), (x-step, y), (x, y+step), (x, y-step)):
                if cell in remaining:
                    remaining.remove(cell)
                    region.add(cell)
                    queue.append(cell)
        regions.append(frozenset(region))
    return sorted(regions, key=lambda region: (-len(region), min(region)))


def fit_encounter(profile, allies, enemies, objectives=(), *, objective_kind="eliminate", breach_y=None):
    regions = connected_regions(profile)
    if not regions:
        raise ValueError("Authored map has no walkable encounter region")
    region = regions[0]
    bottom = {cell for cell in region if cell[1] <= 112}
    if len(bottom) < max(1, len(allies)):
        top = min(y for x, y in region) + 96
        bottom = {cell for cell in region if cell[1] <= top}
    if len(bottom) < len(allies):
        raise ValueError("Authored map has insufficient deployment space")
    if objective_kind == "containment":
        original_line = max(breach_y or 0, max(y for x, y in bottom)+profile.cell_size)
        center_x = objectives[0][0] if objectives else sum(x for x, _ in bottom) // max(1, len(bottom))
        field = approach_distances(region, containment_breach_cells(region, original_line, center_x))
        capacity = len(enemies)+len(objectives)
        if sum(field.get(cell, 0) > MAX_OPENING_MOVES for cell in region-bottom) < capacity:
            # Try shallower allied bands only when the original frontier leaves
            # no response phase. Keep the first (largest) band that fits both sides.
            for top in sorted({y for x, y in bottom}, reverse=True):
                band = {cell for cell in bottom if cell[1] <= top}
                line = top+profile.cell_size
                if len(band) < len(allies):
                    continue
                distance = approach_distances(region, containment_breach_cells(region, line, center_x))
                if sum(distance.get(cell, 0) > MAX_OPENING_MOVES for cell in region-band) >= capacity:
                    bottom, breach_y = band, line
                    break
    occupied = set()

    def place(desired, candidates):
        free = set(candidates) - occupied
        if not free:
            raise ValueError("Authored map has insufficient legal encounter cells")
        cell = min(free, key=lambda cell: ((cell[0]-desired[0])**2+(cell[1]-desired[1])**2, cell))
        occupied.add(cell)
        return cell

    allied_positions = tuple(place(cell, bottom) for cell in allies)
    objective_positions = tuple(place(cell, region) for cell in objectives)
    enemy_region = set(region) - bottom
    if objective_kind == "defend":
        distance = defense_approach_distances(region, objective_positions)
        enemy_region = {cell for cell in enemy_region if distance.get(cell, 0) > MAX_OPENING_MOVES}
    if objective_kind == "containment":
        breach_y = max(breach_y or 0, max(y for x, y in bottom) + profile.cell_size)
        enemy_region = {cell for cell in enemy_region if cell[1] > breach_y}
        center_x = objective_positions[0][0] if objective_positions else sum(x for x, _ in bottom) // max(1, len(bottom))
        distances = approach_distances(region, containment_breach_cells(region, breach_y, center_x))
        # Prefer a full response activation, preserving authored headcount on
        # shallow corridors where four steps cannot physically fit.
        ranked = sorted((distances.get(cell, 0) for cell in enemy_region-occupied), reverse=True)
        if enemies and len(ranked) >= len(enemies):
            minimum = min(MAX_OPENING_MOVES+1, ranked[len(enemies)-1])
            enemy_region = {cell for cell in enemy_region if distances.get(cell, 0) >= minimum}
    enemy_positions = tuple(place(cell, enemy_region) for cell in enemies)
    return EncounterPlacement(allied_positions, enemy_positions, objective_positions, frozenset(bottom), breach_y)
