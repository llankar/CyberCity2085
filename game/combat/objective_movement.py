"""Bounded objective approaches using the same legal-cell rules as movement."""

from .pack_maneuvers import bounded, neighbors, route_step_to_any


def objective_route_step(enemy, objective, can_enter, *, width=1280, height=720):
    if objective is None or objective.completed:
        return None
    if objective.kind == "containment" and objective.breach_y is not None:
        if enemy.position[1] <= objective.breach_y:
            return (0, 0)
        y = (objective.breach_y // 32) * 32
        goals = [(x, y) for x in range(0, width, 32)]
    else:
        goals = [objective.position, *neighbors(objective.position)]
        if enemy.position in goals:
            return (0, 0)
    goals = sorted((cell for cell in goals if bounded(cell, width, height) and can_enter(*cell)),
                   key=lambda cell: (abs(cell[0]-enemy.position[0])+abs(cell[1]-enemy.position[1]), cell))
    return route_step_to_any(enemy.position, goals, can_enter, width=width, height=height)
