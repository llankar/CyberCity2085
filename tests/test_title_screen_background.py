"""Regression checks for the title-screen background asset."""

from pathlib import Path
import unittest


class TitleScreenBackgroundTest(unittest.TestCase):
    def test_title_screen_background_asset_exists(self) -> None:
        self.assertTrue(Path("assets/ui/title_background.png").exists())

    def test_title_screen_source_points_at_the_new_asset(self) -> None:
        source = Path("game/ui/screens/title_screen.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("_TITLE_BACKGROUND_ASSET", source)
        self.assertIn("title_background.png", source)


if __name__ == "__main__":
    unittest.main()
