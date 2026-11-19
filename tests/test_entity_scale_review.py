import json
from pathlib import Path

import pytest

from tools.record_entity_scale_review import build_review


ROOT = Path(__file__).resolve().parents[1]


def test_archived_scale_review_covers_122_maps_and_three_resolutions():
    review = json.loads((ROOT / "docs/reports/entity_scale_review_windows.json").read_text(encoding="utf-8"))
    assert review["status"] == "PASS"
    assert len(review["maps_reviewed"]) == len(set(review["maps_reviewed"])) == 122
    assert review["resolutions_rendered"] == ["1280x720", "1920x1080", "2560x1440"]
    assert review["catalogue_sheets_inspected"] == 11
    assert not review["missing_captures"] and not review["invalid_native_rows"]
    assert "artistic completion remains 0/122" in review["scope"]


def test_review_refuses_missing_resolution(tmp_path):
    captures = tmp_path / "captures"
    evidence = tmp_path / "evidence"
    captures.mkdir(); evidence.mkdir()
    rows = [{"map": f"map_{i}.png", "native_render": True, "projection_and_zoom_checked": True,
             "entity_families_checked": True, "scale_calibration_status": "NOT VERIFIED",
             "human_ratio_applied": .015} for i in range(122)]
    (captures / "native-report.json").write_text(json.dumps(rows))
    for i in range(1, 12): (evidence / f"catalogue-{i:02d}.jpg").write_bytes(b"x")
    with pytest.raises(ValueError, match="missing"):
        build_review(captures, evidence)
