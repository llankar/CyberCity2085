from pathlib import Path


def test_screens_use_theme_tokens_not_palette() -> None:
    for path in Path("game/ui/screens").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "palette." not in source, f"{path} should use semantic theme tokens"
