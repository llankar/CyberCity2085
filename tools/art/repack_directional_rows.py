"""Repack a two-row directional sheet into two contained 8x1 rows.

The command is deliberately conservative: it writes nothing unless each source
row contains exactly eight substantial silhouettes at an alpha threshold.
"""

import argparse
from pathlib import Path

from PIL import Image


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


def repack_row(row: Image.Image, min_width: int = 20, padding: int = 32, margin: int = 16) -> Image.Image:
    row = row.convert("RGBA")
    runs, _threshold = find_eight_runs(row, min_width=min_width)
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
    if source.height % 2:
        raise ValueError("two-row source height must be even")
    middle = source.height // 2
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
    args = parser.parse_args()
    with Image.open(args.source) as source:
        lead, follow = repack_two_rows(source, min_width=args.min_width)
    args.lead.parent.mkdir(parents=True, exist_ok=True)
    args.follow.parent.mkdir(parents=True, exist_ok=True)
    lead.save(args.lead)
    follow.save(args.follow)


if __name__ == "__main__":
    main()
