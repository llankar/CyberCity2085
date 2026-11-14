"""Contracts for the scoped tactical-combat retrofit plan."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tactical_target_covers_rules_ai_objectives_roles_and_feedback() -> None:
    plan = (ROOT / "docs" / "tactical_combat_retrofit.md").read_text(encoding="utf-8")

    for requirement in (
        "AttackContext",
        "objectives",
        "Enemy intent",
        "signature mechanic",
        "persistent outcomes",
        "Arcade",
    ):
        assert requirement.lower() in plan.lower()


def test_first_tactical_slice_respects_five_task_limit() -> None:
    plan = (ROOT / "docs" / "tactical_combat_retrofit.md").read_text(encoding="utf-8")
    first_slice = plan.split("## First implementation slice", 1)[1].split(
        "## Second implementation slice", 1
    )[0]
    tasks = [line for line in first_slice.splitlines() if line[:3] in {"1. ", "2. ", "3. ", "4. ", "5. "}]

    assert len(tasks) == 5


def test_tactical_backlog_has_one_active_slice_and_final_release_gate() -> None:
    backlog = (ROOT / "docs" / "tactical_backlog.md").read_text(encoding="utf-8")

    assert backlog.count("(active)") == 1
    assert "TAC-RULE-01" in backlog
    assert "TAC-RC-05" in backlog
    assert "Godot" not in backlog or "parallel" not in backlog.lower()
