"""Blend the existing factory floor repairs inside their replacement mask."""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

phase = Path("E:/CyberCity2085-3d-lab/generated/phase2")
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", default="factory278", choices=("factory278","factory329"))
args = parser.parse_args()
source = Path(__file__).resolve().parents[2] / "assets/maps/city_industrial_factory_floor.png"
base = np.asarray(Image.open(source).convert("RGB"))
floor = np.asarray(Image.open(phase / args.input / "floor.png").convert("RGB"))
mask = np.asarray(Image.open(phase / args.input / "replacement_mask.png").convert("L")) > 0
assert base.shape == floor.shape and base.shape[:2] == mask.shape
blend = np.clip(cv2.distanceTransform(mask.astype("uint8"), cv2.DIST_L2, 5)
                / max(3, base.shape[1]*.002), 0, 1)[..., None]
result = np.rint(base*(1-blend)+floor*blend).astype("uint8")
assert np.array_equal(result[~mask], base[~mask])
output = phase / ("factory328" if args.input == "factory278" else args.input)
output.mkdir(exist_ok=True)
Image.fromarray(result).save(output / "floor.png")
