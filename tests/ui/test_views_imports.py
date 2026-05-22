"""Static regression checks for view module imports."""

from pathlib import Path


def test_views_imports_save_system_result() -> None:
    source = Path("game/views.py").read_text(encoding="utf-8")

    assert "from .persistence import SaveSystem, SaveSystemResult" in source
