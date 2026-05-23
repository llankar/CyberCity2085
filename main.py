"""CyberCity 2085 — game entry point."""

import warnings
# Suppress Arcade's per-frame draw_text performance warning — known, non-critical.
warnings.filterwarnings("ignore", category=UserWarning, module="arcade")

import arcade

from game.ui.screens.title_screen import TitleView


def main() -> None:
    window = arcade.Window(1920, 1000, "CyberCity 2085")
    window.show_view(TitleView())
    arcade.run()


if __name__ == "__main__":
    main()
