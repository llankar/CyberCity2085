from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "background_manifest.json"
EXPECTED_SIZE = (1600, 1200)
EXPECTED_COUNTS = {
    "city": 30,
    "wasteland": 30,
}


def test_manifest_and_background_files() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    backgrounds = manifest["backgrounds"]

    counts = {category: 0 for category in EXPECTED_COUNTS}
    seen_ids: set[str] = set()

    for item in backgrounds:
        asset_id = item["id"]
        category = item["category"]
        path = ROOT / item["path"]

        assert asset_id not in seen_ids, asset_id
        seen_ids.add(asset_id)
        assert category in EXPECTED_COUNTS, asset_id
        counts[category] += 1
        assert path.exists(), item["path"]
        assert path.suffix.lower() == ".jpg", item["path"]

        with Image.open(path) as image:
            assert image.size == EXPECTED_SIZE, item["path"]
            assert image.format == "JPEG", item["path"]

    assert counts == EXPECTED_COUNTS
    assert len(backgrounds) == sum(EXPECTED_COUNTS.values())
