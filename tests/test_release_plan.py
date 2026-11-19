from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_plan_has_a_verifiable_finish_line() -> None:
    plan = (ROOT / "docs" / "release_plan.md").read_text(encoding="utf-8")

    assert "## Definition of done for 1.0" in plan
    assert "Act V" in plan
    assert "explicit ending" in plan
    assert "headless full-campaign smoke" in plan
    assert "Godot remains an optional" in plan


def test_first_release_batch_tracks_completion_criteria() -> None:
    plan = (ROOT / "docs" / "release_plan.md").read_text(encoding="utf-8")
    batch = plan.split("## First implementation batch", 1)[1]
    task_lines = [line for line in batch.splitlines() if line.startswith(tuple(f"{i}. `RELEASE-" for i in range(1, 10)))]

    assert task_lines


def test_design_doctrine_connects_management_and_tactics() -> None:
    doctrine = (ROOT / "docs" / "gameplay" / "design_pillars.md").read_text(encoding="utf-8")

    assert "## Pillar 1 — Strategic management" in doctrine
    assert "## Pillar 2 — Tactical combat" in doctrine
    assert "forecast → commit → deploy → resolve → remember → adapt" in doctrine
    assert "XCOM" in doctrine
    assert "Baldur's Gate" in doctrine


def test_release_candidate_checklist_is_documented() -> None:
    backlog = (ROOT / "docs" / "backlog.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs" / "release_checklist.md").read_text(encoding="utf-8")

    assert "release_checklist.md" in backlog
    assert "## Automated gates" in checklist
    assert "## Known 1.0 limitations" in checklist
    assert "dist/CyberCity2085/CyberCity2085.exe" in checklist
