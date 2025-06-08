import arcade
from game.views import CorpView


def main():
    window = arcade.Window(1920, 1080, "CyberCity 2085")
    start_view = CorpView()
    start_view.setup()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
