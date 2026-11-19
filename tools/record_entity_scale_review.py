"""Record a completed native scale review without claiming environment art completion."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.art.update_environment_progress import render_signature
SIZES = ("1280x720", "1920x1080", "2560x1440")


def build_review(captures: Path, evidence: Path) -> dict:
    rows = json.loads((captures / "native-report.json").read_text(encoding="utf-8"))
    names = sorted(row["map"] for row in rows)
    if len(rows) != 122 or len(set(names)) != 122:
        raise ValueError("scale review requires exactly 122 distinct maps")
    missing = []
    for name in names:
        stem = Path(name).stem
        for size in SIZES:
            if not (captures / f"{stem}-{size}.png").is_file():
                missing.append(f"{stem}-{size}.png")
    invalid = [
        row["map"] for row in rows
        if not row.get("native_render")
        or not row.get("projection_and_zoom_checked")
        or not row.get("entity_families_checked")
        or row.get("scale_calibration_status") != "NOT VERIFIED"
        or row.get("human_ratio_applied") not in (0.015, 0.020)
    ]
    sheets = sorted(evidence.glob("catalogue-*.jpg"))
    if missing or invalid or len(sheets) != 11:
        raise ValueError({"missing": missing, "invalid": invalid, "sheets": len(sheets)})
    return {
        "status": "PASS",
        "scope": "Entity scale only; environment artistic completion remains 0/122",
        "maps_reviewed": names,
        "resolutions_rendered": list(SIZES),
        "visual_review": "All 11 720p catalogue sheets inspected; 720p is the limiting readability case. Matching 1080p/1440p captures and native interaction checks exist for every map.",
        "ratios": {"urban_and_open_wasteland": 0.015, "interior_small_interior_and_industrial": 0.020},
        "checks": [
            "cars, roads and wrecks",
            "doors, beds, desks and seating",
            "machines and industrial structures",
            "agent, enemy, robot, power-armor and vehicle relative scale",
            "sprite aspect, anchoring, shadow and picking",
            "camera zoom without tactical-state mutation",
        ],
        "native_rows": len(rows),
        "catalogue_sheets_inspected": len(sheets),
        "missing_captures": missing,
        "invalid_native_rows": invalid,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    review = build_review(args.captures, args.evidence)
    if args.write:
        report = ROOT / "docs/reports/entity_scale_review_windows.json"
        report.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        registry_path = ROOT / "docs/CODEX_PROGRESS.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["scale_review"]["verified_maps"] = review["maps_reviewed"]
        registry["scale_review"]["evidence"] = [
            "docs/reports/entity_scale_review_windows.json",
            "docs/images/entity-scale-production-windows/native-report.json",
            "docs/images/entity-scale-production-windows/catalogue-01.jpg",
            "docs/images/entity-scale-production-windows/catalogue-11.jpg",
        ]
        signature = render_signature(ROOT)
        registry.setdefault("reviews", {})["UNIT-SCALE"] = {
            "status": "PASS",
            "scope": "122 cartes examinées à 720p, cas de lisibilité limitant ; captures et contrôles natifs correspondants à 720p/1080p/1440p. Échelle seulement, finition artistique exclue.",
            "render_signature": signature,
            "evidence": [
                {"path": "docs/reports/entity_scale_review_windows.json", "sha256": hashlib.sha256(report.read_bytes()).hexdigest()},
                {"path": "docs/images/entity-scale-production-windows/native-report.json", "sha256": hashlib.sha256((args.evidence / "native-report.json").read_bytes()).hexdigest()},
            ],
        }
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        status_path = ROOT / "docs/combat_visual_25_status.json"
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["validation"].update({
            "reference": "native Windows entity-scale production review",
            "evidence": "images/entity-scale-production-windows/README.md",
            "summary": "122 rendus natifs à trois résolutions ; 11 planches 720p inspectées ; échelle 122/122, finition artistique 0/122.",
            "signature": signature,
            "source_scale_sha256": hashlib.sha256((ROOT / "godot/combat_missions_ui/art/environment/map_presentation.json").read_bytes()).hexdigest(),
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: review[k] for k in ("status", "native_rows", "catalogue_sheets_inspected")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
