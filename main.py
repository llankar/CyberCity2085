"""CyberCity 2085 — game entry point."""

import arcade

from game.ui.screens.title_screen import TitleView


def main() -> None:
    window = arcade.Window(1920, 1000, "CyberCity 2085")
    window.show_view(TitleView())
    arcade.run()


if __name__ == "__main__":
    main()
