"""UI readability defaults for text scale and panel transparency."""

import unittest

from game.ui import palette
from game.ui.theme.typography import typography


class UIReadabilityThemeTest(unittest.TestCase):
    def test_text_tokens_prioritize_readability(self):
        self.assertGreaterEqual(typography.screen_title, 24)
        self.assertGreaterEqual(typography.panel_title, 15)
        self.assertGreaterEqual(typography.body_secondary, 13)
        self.assertGreaterEqual(typography.meta, 11)

    def test_panel_alpha_values_keep_backdrop_more_visible(self):
        self.assertLessEqual(palette.PANEL_FILL[3], 140)
        self.assertLessEqual(palette.PANEL_FILL_DARK[3], 180)
        self.assertLessEqual(palette.EXPANDED_ROOM_FILL[3], 180)


if __name__ == "__main__":
    unittest.main()
