"""Enforce that data-helper screen modules use semantic theme tokens, not raw
palette constants.  Full view classes (title_screen, management_screen) are
excluded because they contain Arcade draw calls that legitimately reference
palette values directly."""

from pathlib import Path

# Files that are full Arcade view classes (drawing code) — allowed to use palette.
_VIEW_FILES = {"title_screen.py", "management_screen.py", "battle_hud.py"}


def test_screens_use_theme_tokens_not_palette() -> None:
    for path in Path("game/ui/screens").glob("*.py"):
        if path.name in _VIEW_FILES:
            continue
        source = path.read_text(encoding="utf-8")
        assert "palette." not in source, f"{path} should use semantic theme tokens"
