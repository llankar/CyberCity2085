import arcade
from .gamestate import GameState
from .character import Character
from .unit import Unit


game_state = GameState()


class CorpView(arcade.View):
    def setup(self):
        self.text = "Corporation Management"

    def on_draw(self):
        self.clear()
        y = self.window.height - 40
        arcade.draw_text(self.text, 20, y, arcade.color.WHITE, 20)
        y -= 40
        for k, v in game_state.corp_budget.items():
            arcade.draw_text(f"{k}: {v}", 20, y, arcade.color.WHITE, 14)
            y -= 20
        arcade.draw_text("Press C for City, R for RPG", 20, 20, arcade.color.AQUA, 14)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.C:
            city_view = CityView()
            city_view.setup()
            self.window.show_view(city_view)
        elif key == arcade.key.R:
            rpg_view = RPGView()
            rpg_view.setup()
            self.window.show_view(rpg_view)


class CityView(arcade.View):
    def setup(self):
        self.text = "City Management"

    def on_draw(self):
        self.clear()
        y = self.window.height - 40
        arcade.draw_text(self.text, 20, y, arcade.color.WHITE, 20)
        y -= 40
        for k, v in game_state.city_budget.items():
            arcade.draw_text(f"{k}: {v}", 20, y, arcade.color.WHITE, 14)
            y -= 20
        arcade.draw_text("Press R for RPG", 20, 20, arcade.color.AQUA, 14)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            rpg_view = RPGView()
            rpg_view.setup()
            self.window.show_view(rpg_view)


class RPGView(arcade.View):
    def setup(self):
        if not game_state.characters:
            game_state.characters.append(Character(name="Agent 1"))
        self.text = "RPG Phase"

    def on_draw(self):
        self.clear()
        arcade.draw_text(self.text, 20, self.window.height - 40, arcade.color.WHITE, 20)
        y = self.window.height - 80
        for char in game_state.characters:
            arcade.draw_text(f"{char.name} - Lvl {char.level} - SP {char.skill_points}", 20, y, arcade.color.WHITE, 14)
            y -= 20
        arcade.draw_text("Press B for Battle", 20, 20, arcade.color.AQUA, 14)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.B:
            battle_view = BattleView()
            battle_view.setup()
            self.window.show_view(battle_view)


class BattleView(arcade.View):
    def setup(self):
        self.map = arcade.load_tilemap("scenes/test.tmx")
        self.scene = arcade.Scene.from_tilemap(self.map)
        self.camera = arcade.Camera(self.window.width, self.window.height)
        self.unit = Unit(position=(64, 64))

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        x, y = self.unit.position
        arcade.draw_circle_filled(x, y, 10, arcade.color.RED)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.unit.move(0, 32)
        elif key == arcade.key.DOWN:
            self.unit.move(0, -32)
        elif key == arcade.key.LEFT:
            self.unit.move(-32, 0)
        elif key == arcade.key.RIGHT:
            self.unit.move(32, 0)
        elif key == arcade.key.ESCAPE:
            corp_view = CorpView()
            corp_view.setup()
            self.window.show_view(corp_view)
