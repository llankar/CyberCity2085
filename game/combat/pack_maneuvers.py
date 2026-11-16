"""Raider isolation, skirmish exits and bounded Starver approach routes."""

from heapq import heappop, heappush
from math import hypot

CELL = 32
BUDDY_DISTANCE = 3 * CELL


def buddy_distance(target, allies):
    return min((target.distance_to(other) for other in allies
                if other is not target and other.health > 0), default=float("inf"))


def isolated_target(enemy, allies, score):
    isolated = [unit for unit in allies if unit.health > 0 and buddy_distance(unit, allies) > BUDDY_DISTANCE]
    return max(isolated, key=lambda unit: score(enemy, unit), default=None)


def neighbors(position):
    x, y = position
    return [(x+CELL, y), (x-CELL, y), (x, y+CELL), (x, y-CELL)]


def bounded(cell, width=1280, height=720):
    return 0 <= cell[0] < width and 0 <= cell[1] < height


def route_step(start, goal, can_enter, *, width=1280, height=720, max_visits=1120):
    """One cardinal A* step; bounded work, no terrain mutation or teleporting."""
    return route_step_to_any(start, (goal,), can_enter, width=width, height=height, max_visits=max_visits)


def route_step_to_any(start, goals, can_enter, *, width=1280, height=720, max_visits=1120):
    """Shortest legal approach to a set of endpoints within one search budget."""
    goals = frozenset(goals)
    if not goals or start in goals:
        return None
    frontier = [(0, start)]
    cost, previous = {start: 0}, {}
    visits = 0
    closed = set()
    while frontier and visits < max_visits:
        _, current = heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        visits += 1
        if current in goals:
            while previous[current] != start:
                current = previous[current]
            return current[0]-start[0], current[1]-start[1]
        for cell in neighbors(current):
            if not bounded(cell, width, height) or not can_enter(*cell):
                continue
            candidate = cost[current] + 1
            if candidate >= cost.get(cell, float("inf")):
                continue
            cost[cell], previous[cell] = candidate, current
            heuristic = min(abs(cell[0]-goal[0])+abs(cell[1]-goal[1]) for goal in goals) / CELL
            heappush(frontier, (candidate+heuristic, cell))
    return None


def approach_step(enemy, target, can_enter, destination=None, *, width=1280, height=720):
    goals = [destination] if destination is not None else sorted(
        (cell for cell in neighbors(target.position) if bounded(cell, width, height) and can_enter(*cell)),
        key=lambda cell: abs(cell[0]-enemy.position[0])+abs(cell[1]-enemy.position[1]),
    )
    return route_step_to_any(enemy.position, goals, can_enter, width=width, height=height,
                             max_visits=min(4096, (width//CELL+1)*(height//CELL+1)))


starver_step = approach_step  # Compatibility name; all doctrines share legal approaches.


def skirmish_exit(enemy, target, allies, can_enter, cover_nodes, *, width=1280, height=720):
    threats = [unit for unit in allies if unit.health > 0]
    def safety(cell):
        distance = min((hypot(cell[0]-u.position[0], cell[1]-u.position[1]) for u in threats), default=0)
        cover = any(abs(cell[0]-node.world_x)+abs(cell[1]-node.world_y) <= CELL for node in cover_nodes or ())
        return distance + (CELL if cover else 0)
    candidates = [cell for cell in neighbors(enemy.position)
                  if bounded(cell, width, height) and can_enter(*cell)
                  and hypot(cell[0]-target.position[0], cell[1]-target.position[1]) <= enemy.attack_range*CELL
                  and safety(cell) > safety(enemy.position)]
    best = max(candidates, key=safety, default=None)
    return (best[0]-enemy.position[0], best[1]-enemy.position[1]) if best else None
