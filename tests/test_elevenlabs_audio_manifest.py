import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "audio" / "elevenlabs_manifest.json"


def test_downloaded_pilot_remains_outside_production_until_audition():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    attempt = data["latest_connector_attempt"]
    files = attempt["technical_qa"]["files"]

    assert attempt["downloaded"] is True
    assert attempt["auditory_validation_performed"] is False
    assert attempt["download_directory"].startswith("E:/CyberCity2085-builds/")
    assert len(files) == data["audio_files_downloaded"] == 5
    assert all(item["status"] != "ready" for item in files)
    assert all(len(item["sha256"]) == 64 for item in files)
    assert all(item["generation_id"] in attempt["started_generation_ids"] for item in files)
    assert not any((ROOT / "assets").rglob("*YlVWzsQ29QfVjlLdDoQH*"))


def test_near_inaudible_impact_is_rejected_not_normalized_into_production():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data["latest_connector_attempt"]["technical_qa"]["files"]
    impact = next(item for item in files if item["generation_id"] == "xv8Gzq2sccJdkTGrTECr")

    assert impact["family"] == "impact_metal"
    assert impact["peak_dbfs"] == -40.7
    assert impact["status"] == "technical_reject_near_inaudible"


def test_pilot_is_license_blocked_until_generation_plan_is_proven():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    review = data["latest_connector_attempt"]["license_review"]

    assert review["status"] == "blocked_plan_at_generation_unverified"
    assert review["jurisdiction"] == "EEA"
    assert review["terms_url"] == "https://elevenlabs.io/terms-of-use-eu"
    assert "Do not integrate or distribute" in review["release_rule"]
