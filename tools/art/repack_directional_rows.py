"""Repack a two-row directional sheet into two contained 8x1 rows.

The command is deliberately conservative: it writes nothing unless each source
row contains exactly eight substantial silhouettes at an alpha threshold.
"""

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

from import_artist_variants import clean_alpha


ALPHA_THRESHOLDS = (16, 32, 64, 96, 128, 160, 192, 220, 240, 250)


def _occupied_runs(alpha: Image.Image, threshold: int, min_width: int) -> list[tuple[int, int]]:
    occupied = [any(alpha.getpixel((x, y)) >= threshold for y in range(alpha.height)) for x in range(alpha.width)]
    runs: list[tuple[int, int]] = []
    start = None
    for x, present in enumerate(occupied + [False]):
        if present and start is None:
            start = x
        elif not present and start is not None:
            if x - start >= min_width:
                runs.append((start, x))
            start = None
    return runs


def find_eight_runs(row: Image.Image, min_width: int = 20) -> tuple[list[tuple[int, int]], int]:
    alpha = row.getchannel("A")
    diagnostics = []
    for threshold in ALPHA_THRESHOLDS:
        runs = _occupied_runs(alpha, threshold, min_width)
        diagnostics.append(f"alpha>={threshold}: {len(runs)}")
        if len(runs) == 8:
            return runs, threshold
    raise ValueError("expected exactly 8 substantial silhouettes (" + ", ".join(diagnostics) + ")")


def _eight_component_sprites(row: Image.Image, threshold: int = 16) -> list[Image.Image]:
    alpha = row.getchannel("A")
    pixels = alpha.load()
    seen = set()
    components = []
    for y in range(alpha.height):
        for x in range(alpha.width):
            if (x, y) in seen or pixels[x, y] < threshold:
                continue
            queue = deque([(x, y)])
            seen.add((x, y))
            points = []
            while queue:
                px, py = queue.popleft()
                points.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if (
                        0 <= nx < alpha.width
                        and 0 <= ny < alpha.height
                        and (nx, ny) not in seen
                        and pixels[nx, ny] >= threshold
                    ):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            if len(points) >= 64:
                components.append(points)
    if len(components) != 8:
        raise ValueError(f"expected exactly 8 substantial 2D components, found {len(components)}")

    sprites = []
    for points in sorted(components, key=lambda item: sum(x for x, _y in item) / len(item)):
        mask = Image.new("L", row.size)
        target = mask.load()
        for x, y in points:
            target[x, y] = 255
        mask = mask.filter(ImageFilter.MaxFilter(5))
        sprite = row.copy()
        sprite.putalpha(ImageChops.multiply(alpha, mask))
        sprites.append(sprite.crop(sprite.getchannel("A").getbbox()))
    return sprites


def repack_row(
    row: Image.Image,
    min_width: int = 20,
    padding: int = 32,
    margin: int = 16,
    clean_small_components: bool = False,
) -> Image.Image:
    row = row.convert("RGBA")
    try:
        runs, _threshold = find_eight_runs(row, min_width=min_width)
    except ValueError as run_error:
        try:
            sprites = _eight_component_sprites(row)
        except ValueError as component_error:
            raise ValueError(f"{run_error}; {component_error}") from component_error
    else:
        boundaries = [0]
        boundaries.extend((runs[index][1] + runs[index + 1][0]) // 2 for index in range(7))
        boundaries.append(row.width)
        sprites = []
        for index in range(8):
            partition = row.crop((boundaries[index], 0, boundaries[index + 1], row.height))
            bounds = partition.getchannel("A").getbbox()
            if bounds is None:
                raise ValueError(f"silhouette {index} has no source alpha")
            sprites.append(partition.crop(bounds))

    if clean_small_components:
        sprites = [clean_alpha(sprite) for sprite in sprites]
        sprites = [sprite.crop(sprite.getchannel("A").getbbox()) for sprite in sprites]

    cell_width = max(sprite.width for sprite in sprites) + padding
    height = max(sprite.height for sprite in sprites) + 2 * margin
    result = Image.new("RGBA", (8 * cell_width, height))
    for index, sprite in enumerate(sprites):
        x = index * cell_width + (cell_width - sprite.width) // 2
        y = height - margin - sprite.height
        result.alpha_composite(sprite, (x, y))
    return result


def repack_two_rows(source: Image.Image, **kwargs) -> tuple[Image.Image, Image.Image]:
    source = source.convert("RGBA")
    middle = source.height // 2
    alpha = source.getchannel("A")
    separator_rows = range(max(0, middle - 1), min(source.height, middle + 2))
    separator_ink = sum(
        alpha.getpixel((x, y)) >= 192 for y in separator_rows for x in range(source.width)
    )
    if separator_ink > source.width * len(separator_rows) * 0.01:
        raise ValueError("two-row source has opaque ink across its middle separator")
    return (
        repack_row(source.crop((0, 0, source.width, middle)), **kwargs),
        repack_row(source.crop((0, middle, source.width, source.height)), **kwargs),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--lead", type=Path, required=True)
    parser.add_argument("--follow", type=Path, required=True)
    parser.add_argument("--min-width", type=int, default=20)
    parser.add_argument(
        "--clean-small-components",
        action="store_true",
        help="remove reviewed detached specks smaller than 2%% of the main opaque body",
    )
    args = parser.parse_args()
    with Image.open(args.source) as source:
        lead, follow = repack_two_rows(
            source,
            min_width=args.min_width,
            clean_small_components=args.clean_small_components,
        )
    args.lead.parent.mkdir(parents=True, exist_ok=True)
    args.follow.parent.mkdir(parents=True, exist_ok=True)
    lead.save(args.lead)
    follow.save(args.follow)


if __name__ == "__main__":
    main()
