from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def cover_crop(image: Image.Image, target_ratio: float) -> Image.Image:
    width, height = image.size
    ratio = width / height
    if abs(ratio - target_ratio) < 0.001:
        return image

    if ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))

    new_height = int(width / target_ratio)
    top = (height - new_height) // 2
    return image.crop((0, top, width, top + new_height))


def normalize(src: Path, dest: Path, width: int, height: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = cover_crop(image, width / height)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(dest, "JPEG", quality=92, optimize=True, progressive=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument("dest", type=Path)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1200)
    args = parser.parse_args()
    normalize(args.src, args.dest, args.width, args.height)


if __name__ == "__main__":
    main()
