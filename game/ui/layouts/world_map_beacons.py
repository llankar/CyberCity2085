"""Deterministic placement of holograms and attached labels, independent of rendering."""

from dataclasses import dataclass
from math import cos, sin, tau
from itertools import chain


@dataclass(frozen=True)
class Rect:
    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def center(self):
        return ((self.left + self.right) / 2, (self.bottom + self.top) / 2)

    def intersects(self, other, pad=0):
        return (
            self.left < other.right + pad
            and self.right > other.left - pad
            and self.bottom < other.top + pad
            and self.top > other.bottom - pad
        )

    def contains(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def inside(self, other):
        return (
            self.left >= other.left
            and self.right <= other.right
            and self.bottom >= other.bottom
            and self.top <= other.top
        )


@dataclass(frozen=True)
class Beacon:
    key: str
    kind: str
    index: int
    category: str
    title: str
    site: str
    anchor: tuple[float, float]
    selected: bool = False


@dataclass(frozen=True)
class Placement:
    beacon: Beacon
    x: float
    y: float
    marker: Rect
    label: Rect
    scale: float


# Measured label/info rectangles in the original 1672x941 artwork. Do not paint
# over the baked city names, title, legends, compass or bottom information cards.
CITY_LABELS = (
    (0.050, 0.620, 0.123, 0.684),
    (0.006, 0.475, 0.098, 0.559),
    (0.006, 0.327, 0.154, 0.410),
    (0.351, 0.735, 0.420, 0.794),
    (0.478, 0.716, 0.549, 0.775),
    (0.300, 0.607, 0.377, 0.673),
    (0.550, 0.608, 0.633, 0.683),
    (0.294, 0.338, 0.384, 0.406),
    (0.466, 0.313, 0.536, 0.390),
    (0.544, 0.442, 0.634, 0.512),
    (0.705, 0.285, 0.822, 0.358),
    (0.768, 0.561, 0.846, 0.637),
    (0.897, 0.438, 0.986, 0.508),
    (0.773, 0.717, 0.867, 0.787),
)


def artwork_obstacles(image: Rect):
    def mapped(r):
        a, b, c, d = r
        return Rect(
            image.left + a * image.width,
            image.bottom + b * image.height,
            image.left + c * image.width,
            image.bottom + d * image.height,
        )

    return [mapped(r) for r in CITY_LABELS] + [
        mapped((0, 0.815, 1, 1)),
        mapped((0, 0, 1, 0.205)),
    ]


def _offsets(step, rings):
    yield 0, 0
    for ring in range(1, rings + 1):
        radius = step * ring
        count = max(12, ring * 8)
        for i in range(count):
            angle = tau * i / count
            yield cos(angle) * radius, sin(angle) * radius


def arrange_beacons(beacons, image: Rect, *, exclusions=(), scale=1.0):
    """Keep marker/cartouche pairs together; selected labels get priority.

    Search beyond the nearest city when crowded rather than painting overlapping
    cartouches. Placements are stable across animation frames and hover states.
    """
    obstacles = list(artwork_obstacles(image)) + list(exclusions)
    active = Rect(
        image.left + 8,
        image.bottom + 0.21 * image.height,
        image.right - 8,
        image.bottom + 0.813 * image.height,
    )
    rings = int((image.width + image.height) / (18 * scale)) + 2

    def marker_for(beacon):
        ax = image.left + beacon.anchor[0] * image.width
        ay = image.bottom + beacon.anchor[1] * image.height
        radius = (48 if beacon.selected else 29) * scale
        height = (114 if beacon.selected else 76) * scale
        for dx, dy in _offsets(18 * scale, rings):
            x, y = ax + dx, ay + dy
            marker = Rect(x - radius, y - 11 * scale, x + radius, y + height)
            if marker.inside(active) and not any(
                marker.intersects(o, 4 * scale) for o in obstacles
            ):
                obstacles.append(marker)
                return x, y, marker
        raise ValueError("No free beacon for " + beacon.key)

    def label_for(beacon, x, y, marker):
        h = (76 if beacon.selected else 40) * scale
        for width in (
            [min(244, image.width * 0.208 / scale)]
            if beacon.selected
            else [158, 142, 126]
        ):
            w = width * scale
            head = y + (77 if beacon.selected else 49) * scale
            candidates = [
                Rect(
                    marker.right + 8 * scale,
                    head - h * 0.5,
                    marker.right + 8 * scale + w,
                    head + h * 0.5,
                ),
                Rect(
                    marker.left - 8 * scale - w,
                    head - h * 0.5,
                    marker.left - 8 * scale,
                    head + h * 0.5,
                ),
                Rect(
                    x - w * 0.5,
                    marker.top + 8 * scale,
                    x + w * 0.5,
                    marker.top + 8 * scale + h,
                ),
                Rect(
                    x - w * 0.5,
                    marker.bottom - h - 8 * scale,
                    x + w * 0.5,
                    marker.bottom - 8 * scale,
                ),
            ]
            gap = 5 * scale
            xs = {active.left, active.right - w}
            ys = {active.bottom, active.top - h}
            for obstacle in obstacles:
                xs.update([obstacle.right + gap, obstacle.left - w - gap])
                ys.update([obstacle.top + gap, obstacle.bottom - h - gap])
            edge_positions = [
                Rect(l, b, l + w, b + h)
                for l in sorted(xs)
                for b in sorted(ys)
                if l >= active.left
                and l + w <= active.right
                and b >= active.bottom
                and b + h <= active.top
            ]

            def distance(rect):
                px = min(max(x, rect.left), rect.right)
                py = min(max(head, rect.bottom), rect.top)
                return (
                    (px - x) ** 2
                    + (py - head) ** 2
                    + 0.03 * ((rect.center[0] - x) ** 2 + (rect.center[1] - head) ** 2)
                    + (
                        (120 * scale) ** 2
                        if beacon.selected and rect.center[1] < head
                        else 0
                    )
                )

            edge_positions.sort(key=distance)
            choices = (
                sorted(candidates + edge_positions, key=distance)
                if beacon.selected
                else chain(candidates, edge_positions)
            )
            label = next(
                (
                    r
                    for r in choices
                    if r.inside(active)
                    and not any(r.intersects(o, 4 * scale) for o in obstacles)
                ),
                None,
            )
            if label:
                obstacles.append(label)
                return label
        raise ValueError("No free cartouche for " + beacon.key)

    result = []
    pending = []
    for beacon in sorted(beacons, key=lambda b: (not b.selected, b.key)):
        x, y, marker = marker_for(beacon)
        if beacon.selected:
            label = label_for(beacon, x, y, marker)
            result.append(Placement(beacon, x, y, marker, label, scale))
        else:
            pending.append((beacon, x, y, marker))
    for beacon, x, y, marker in pending:
        label = label_for(beacon, x, y, marker)
        result.append(Placement(beacon, x, y, marker, label, scale))
    return result


def briefing_link(start, end, obstacles, bounds: Rect, padding=1.5):
    """Shortest orthogonal HUD link through free space around labels and legends."""
    import heapq

    expanded = [
        Rect(r.left - padding, r.bottom - padding, r.right + padding, r.top + padding)
        for r in obstacles
    ]
    xs = {start[0], end[0], bounds.left, bounds.right}
    ys = {start[1], end[1], bounds.bottom, bounds.top}
    for r in expanded:
        xs.update([r.left, r.right])
        ys.update([r.bottom, r.top])
    xs = sorted(x for x in xs if bounds.left <= x <= bounds.right)
    ys = sorted(y for y in ys if bounds.bottom <= y <= bounds.top)
    origin = (xs.index(start[0]), ys.index(start[1]))
    goal = (xs.index(end[0]), ys.index(end[1]))

    def blocked(a, b):
        x, y = a
        u, v = b
        if abs(y - v) < 1e-6:
            return any(
                r.bottom + 1e-6 < y < r.top - 1e-6
                and max(x, u) > r.left + 1e-6
                and min(x, u) < r.right - 1e-6
                for r in expanded
            )
        return any(
            r.left + 1e-6 < x < r.right - 1e-6
            and max(y, v) > r.bottom + 1e-6
            and min(y, v) < r.top - 1e-6
            for r in expanded
        )

    queue = [(0, 0, origin)]
    costs = {origin: 0}
    previous = {}
    while queue:
        _, cost, node = heapq.heappop(queue)
        if node == goal:
            break
        if cost > costs[node]:
            continue
        x, y = node
        for neighbor in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            a, b = neighbor
            if not (0 <= a < len(xs) and 0 <= b < len(ys)):
                continue
            if blocked((xs[x], ys[y]), (xs[a], ys[b])):
                continue
            distance = abs(xs[a] - xs[x]) + abs(ys[b] - ys[y])
            total = cost + distance
            if total < costs.get(neighbor, float("inf")):
                costs[neighbor] = total
                previous[neighbor] = node
                estimate = abs(xs[a] - end[0]) + abs(ys[b] - end[1])
                heapq.heappush(queue, (total + estimate, total, neighbor))
    if goal not in costs:
        return []
    path = [goal]
    while path[-1] != origin:
        path.append(previous[path[-1]])
    points = [(xs[x], ys[y]) for x, y in reversed(path)]
    simplified = []
    for point in points:
        if len(simplified) > 1:
            a, b = simplified[-2:]
            if (
                abs(a[0] - b[0]) < 1e-6
                and abs(b[0] - point[0]) < 1e-6
                or abs(a[1] - b[1]) < 1e-6
                and abs(b[1] - point[1]) < 1e-6
            ):
                simplified[-1] = point
                continue
        simplified.append(point)
    return simplified
