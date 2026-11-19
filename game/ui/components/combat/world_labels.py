"""Small deterministic layout for neighbouring world-marker captions."""


def place_caption(x, y, width, occupied, *, height=20, gap=6, bounds=None):
    """Find a nearby free rectangle without moving world marker positions."""
    from heapq import heappop, heappush
    origin_left = x-width/2
    if bounds is not None and (width > bounds[2]-bounds[0] or height > bounds[3]-bounds[1]):
        return None
    candidates = [(0, 0, origin_left, y)]
    visited = set()
    serial = 0
    while candidates:
        _, _, left, bottom = heappop(candidates)
        if bounds is not None:
            left = max(bounds[0], min(left, bounds[2]-width))
            bottom = max(bounds[1], min(bottom, bounds[3]-height))
        if (left, bottom) in visited:
            continue
        visited.add((left, bottom))
        right = left+width
        collisions = [box for box in occupied
                      if left < box[2]+gap and right > box[0]-gap
                      and bottom < box[3]+gap and bottom+height > box[1]-gap]
        if not collisions:
            box = (left, bottom, right, bottom+height)
            occupied.append(box)
            return box
        for box in collisions:
            for nx, ny in ((left, box[3]+gap), (box[2]+gap, bottom),
                           (box[0]-gap-width, bottom), (left, box[1]-gap-height)):
                serial += 1
                heappush(candidates, (abs(nx-origin_left)+abs(ny-y), serial, nx, ny))
    return None
