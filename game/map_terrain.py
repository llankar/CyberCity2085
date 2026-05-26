"""Map-backed terrain visibility and movement helpers."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat


@dataclass(frozen=True)
class TerrainProfile:
    """Simple per-map walkability profile sampled from a background PNG."""

    image_path: str
    width: int
    height: int
    cell_size: int
    walkable_cells: frozenset[tuple[int, int]]
    threshold: int

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether a grid position can be entered."""
        if x < 0 or y < 0 or x > self.width or y > self.height:
            return False
        gx = int(round(x / self.cell_size)) * self.cell_size
        gy = int(round(y / self.cell_size)) * self.cell_size
        return (gx, gy) in self.walkable_cells


def _luma(mean_rgb: tuple[float, float, float]) -> float:
    r, g, b = mean_rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _anchor_cells(points: list[tuple[int, int]], cell_size: int, width: int, height: int) -> set[tuple[int, int]]:
    anchors: set[tuple[int, int]] = set()
    for x, y in points:
        gx = int(round(x / cell_size)) * cell_size
        gy = int(round(y / cell_size)) * cell_size
        if 0 <= gx <= width and 0 <= gy <= height:
            anchors.add((gx, gy))
    return anchors


def _anchor_halo(
    points: list[tuple[int, int]],
    cell_size: int,
    width: int,
    height: int,
    radius: int = 1,
) -> set[tuple[int, int]]:
    """Expand forced walkable anchors so units are not boxed in by dark cells."""
    halo: set[tuple[int, int]] = set()
    for x, y in points:
        gx = int(round(x / cell_size)) * cell_size
        gy = int(round(y / cell_size)) * cell_size
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) > radius:
                    continue
                ax = gx + dx * cell_size
                ay = gy + dy * cell_size
                if 0 <= ax <= width and 0 <= ay <= height:
                    halo.add((ax, ay))
    return halo


def _sample_walkable_cells(
    image,
    width: int,
    height: int,
    cell_size: int,
    threshold: int,
) -> set[tuple[int, int]]:
    """Sample the image into walkable grid cells at the given brightness threshold."""
    walkable: set[tuple[int, int]] = set()
    half = max(6, cell_size // 2)
    for gx in range(0, width + 1, cell_size):
        for gy in range(0, height + 1, cell_size):
            left = max(0, gx - half)
            right = min(width, gx + half)
            bottom = max(0, gy - half)
            top = min(height, gy + half)
            if right <= left or top <= bottom:
                continue
            crop = image.crop((left, bottom, right, top))
            crop_stats = ImageStat.Stat(crop)
            if _luma(tuple(crop_stats.mean)) >= threshold:
                walkable.add((gx, gy))
    return walkable


@lru_cache(maxsize=96)
def build_terrain_profile(
    image_path: str,
    width: int,
    height: int,
    cell_size: int = 32,
    forced_walkable: tuple[tuple[int, int], ...] = (),
) -> TerrainProfile:
    """Build a cached walkability profile from a background image."""
    path = Path(image_path)
    if not path.exists():
        return TerrainProfile(image_path, width, height, cell_size, frozenset(), 0)

    try:
        with Image.open(path) as source:
            image = source.convert("RGB").resize((width, height), Image.BICUBIC)
    except Exception:
        return TerrainProfile(image_path, width, height, cell_size, frozenset(), 0)

    image = image.filter(ImageFilter.GaussianBlur(radius=1.0))
    stats = ImageStat.Stat(image)
    threshold = int(max(46, min(132, _luma(tuple(stats.mean)) * 0.82 + 8)))

    total_cells = ((width // cell_size) + 1) * ((height // cell_size) + 1)
    min_walkable = max(12, total_cells // 10)
    walkable: set[tuple[int, int]] = set()
    for offset in (0, -8, -16, -24):
        sample_threshold = max(34, threshold + offset)
        walkable = _sample_walkable_cells(image, width, height, cell_size, sample_threshold)
        if len(walkable) >= min_walkable:
            threshold = sample_threshold
            break

    walkable.update(_anchor_cells(list(forced_walkable), cell_size, width, height))
    walkable.update(_anchor_halo(list(forced_walkable), cell_size, width, height, radius=1))
    return TerrainProfile(
        image_path=image_path,
        width=width,
        height=height,
        cell_size=cell_size,
        walkable_cells=frozenset(walkable),
        threshold=threshold,
    )
