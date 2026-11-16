"""Refresh image metadata after an aligned map restoration, without rescanning walls."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from PIL import Image


def refresh_geometry_metadata(geometry: dict, image_path: str | Path) -> dict:
    """Keep all survey data verbatim; update only the referenced image metadata."""
    image_path = Path(image_path)
    with Image.open(image_path) as image:
        size = list(image.size)
    result = deepcopy(geometry)
    result.update(image=image_path.name, image_size=size,
                  image_sha256=sha256(image_path.read_bytes()).hexdigest())
    return result
