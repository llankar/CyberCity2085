"""Map-backed terrain visibility and movement helpers."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat


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


def _cell_walkability_score(crop) -> float:
    """Score a terrain cell by brightness minus local texture.

    Bright, smooth cells are more likely to be open ground; textured cells
    usually belong to vehicles, walls, debris, or other movement blockers.
    """
    stats = ImageStat.Stat(crop)
    mean_luma = _luma(tuple(stats.mean))
    stddev = sum(stats.stddev) / max(1, len(stats.stddev))
    return mean_luma - stddev * 0.9


def _mask_sidecar_path(image_path: Path) -> Path:
    return image_path.with_suffix(".walkable.png")


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
    """Sample the image into walkable grid cells at the given terrain score threshold."""
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
            if _cell_walkability_score(crop) >= threshold:
                walkable.add((gx, gy))
    return walkable


def _sample_walkable_cells_from_mask(
    image,
    width: int,
    height: int,
    cell_size: int,
    threshold: int = 128,
) -> set[tuple[int, int]]:
    """Sample a binary walkability mask into grid cells."""
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
            mean = crop_stats.mean[0] if crop_stats.mean else 0
            if mean >= threshold:
                walkable.add((gx, gy))
    return walkable


def _prune_isolated_cells(
    walkable: set[tuple[int, int]],
    forced_walkable: tuple[tuple[int, int], ...],
    cell_size: int,
) -> set[tuple[int, int]]:
    """Keep walkable cells connected to the forced spawn anchors."""
    if not walkable:
        return set()
    if not forced_walkable:
        return walkable

    seeds = {
        (int(round(x / cell_size)) * cell_size, int(round(y / cell_size)) * cell_size)
        for x, y in forced_walkable
    }
    seeds &= walkable
    if not seeds:
        return walkable

    seen = set(seeds)
    queue = deque(seeds)
    while queue:
        x, y = queue.popleft()
        for nx, ny in (
            (x + cell_size, y),
            (x - cell_size, y),
            (x, y + cell_size),
            (x, y - cell_size),
        ):
            if (nx, ny) in walkable and (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def infer_terrain_profile(
    image_path: str,
    width: int,
    height: int,
    cell_size: int = 32,
    forced_walkable: tuple[tuple[int, int], ...] = (),
) -> TerrainProfile:
    """Infer a terrain profile from art when no explicit walkability mask exists."""
    path = Path(image_path)
    if not path.exists():
        return TerrainProfile(image_path, width, height, cell_size, frozenset(), 0)

    try:
        with Image.open(path) as source:
            image = source.convert("RGB").resize((width, height), Image.BICUBIC)
    except Exception:
        return TerrainProfile(image_path, width, height, cell_size, frozenset(), 0)

    image = image.filter(ImageFilter.GaussianBlur(radius=0.6))
    stats = ImageStat.Stat(image)
    mean_stddev = sum(stats.stddev) / max(1, len(stats.stddev))
    threshold = int(max(28, min(170, _luma(tuple(stats.mean)) - mean_stddev * 0.65 + 10)))

    total_cells = ((width // cell_size) + 1) * ((height // cell_size) + 1)
    min_walkable = max(12, total_cells // 10)
    walkable: set[tuple[int, int]] = set()
    for offset in (0, -6, -12, -18, -24):
        sample_threshold = max(18, threshold + offset)
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


def export_walkable_mask(
    image_path: str,
    output_path: str | None = None,
    *,
    width: int | None = None,
    height: int | None = None,
    cell_size: int = 32,
    forced_walkable: tuple[tuple[int, int], ...] = (),
) -> Path:
    """Write a binary walkability mask for a battle map image."""
    path = Path(image_path)
    if output_path is None:
        output_path = str(_mask_sidecar_path(path))
    out_path = Path(output_path)

    with Image.open(path) as source:
        src_w, src_h = source.size
        map_w = width or src_w
        map_h = height or src_h

    profile = infer_terrain_profile(
        str(path),
        map_w,
        map_h,
        cell_size=cell_size,
        forced_walkable=forced_walkable,
    )
    mask = Image.new("L", (map_w, map_h), 0)
    draw = ImageDraw.Draw(mask)
    for gx, gy in profile.walkable_cells:
        draw.rectangle((gx, gy, min(map_w, gx + cell_size), min(map_h, gy + cell_size)), fill=255)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mask.save(out_path)
    return out_path


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

    mask_path = _mask_sidecar_path(path)
    if mask_path.exists():
        try:
            with Image.open(mask_path) as source:
                mask = source.convert("L").resize((width, height), Image.NEAREST)
        except Exception:
            mask = None
        if mask is not None:
            walkable = _sample_walkable_cells_from_mask(mask, width, height, cell_size)
            walkable.update(_anchor_cells(list(forced_walkable), cell_size, width, height))
            walkable.update(_anchor_halo(list(forced_walkable), cell_size, width, height, radius=1))
            return TerrainProfile(
                image_path=image_path,
                width=width,
                height=height,
                cell_size=cell_size,
                walkable_cells=frozenset(walkable),
                threshold=255,
            )

    return infer_terrain_profile(
        image_path,
        width,
        height,
        cell_size=cell_size,
        forced_walkable=forced_walkable,
    )
