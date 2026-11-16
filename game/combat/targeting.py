"""Pointer target selection independent of rendering and attack resolution."""


def target_index_at_point(targets, x, y, *, camera_offset=(0, 0), radius=24):
    world_x, world_y = x+camera_offset[0], y+camera_offset[1]
    candidates = []
    for index, target in enumerate(targets):
        if target.health <= 0 or not getattr(target, "visible", True):
            continue
        px, py = target.position
        distance = (px-world_x)**2+(py-world_y)**2
        if distance <= radius**2:
            candidates.append((distance, index))
    return min(candidates)[1] if candidates else None
