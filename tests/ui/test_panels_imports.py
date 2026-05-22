"""Static regression checks for panel module dependencies."""

from pathlib import Path


def test_panels_imports_pulse_helper() -> None:
    source = Path("game/ui/panels.py").read_text(encoding="utf-8")

    assert "from .theme.motion import pulse_from_elapsed" in source
