import arcade
import os
import random

from .character import Character
from .gamestate import GameState
from .unit import Unit
from arcade.camera import Camera2D

game_state = GameState()


class CorpView(arcade.View):
    def setup(self):
        self.text = "Corporation Management"
        if game_state.budget_pool <= 0:
            game_state.budget_pool = game_state.compute_budget()

    def on_draw(self):
        self.clear()
        y = self.window.height - 40
        arcade.draw_text(self.text, 20, y, arcade.color.WHITE, 20)
        y -= 40
        arcade.draw_text(
            f"Turn {game_state.turn} - Budget: {game_state.budget_pool}",
            20,
            y,
            arcade.color.AQUA,
            14,
        )
        y -= 20
        for k, v in game_state.corp_budget.items():
            arcade.draw_text(f"{k}: {v}", 20, y, arcade.color.WHITE, 14)
            y -= 20
        arcade.draw_text(
            "1-4 to invest, S to save, L to load", 20, 40, arcade.color.AQUA, 14
        )
        arcade.draw_text("Press C for City, R for RPG", 20, 20, arcade.color.AQUA, 14)

    def on_key_press(self, key, modifiers):
        global game_state
        if key == arcade.key.C:
            city_view = CityView()
            city_view.setup()
            self.window.show_view(city_view)
        elif key == arcade.key.R:
            rpg_view = RPGView()
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key == arcade.key.KEY_1:
            game_state.allocate_corp_funds("research", 10)
        elif key == arcade.key.KEY_2:
            game_state.allocate_corp_funds("security", 10)
        elif key == arcade.key.KEY_3:
            game_state.allocate_corp_funds("politics", 10)
        elif key == arcade.key.KEY_4:
            game_state.allocate_corp_funds("black_ops", 10)
        elif key == arcade.key.S:
            game_state.save("savegame.json")
        elif key == arcade.key.L:
            game_state = GameState.load("savegame.json")
        if game_state.budget_pool <= 0:
            game_state.advance_turn()


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
        arcade.draw_text("7-9 to invest", 20, 40, arcade.color.AQUA, 14)
        arcade.draw_text("Press R for RPG", 20, 20, arcade.color.AQUA, 14)

    def on_key_press(self, key, modifiers):
        global game_state
        if key == arcade.key.R:
            rpg_view = RPGView()
            rpg_view.setup()
            self.window.show_view(rpg_view)
        elif key == arcade.key.KEY_7:
            game_state.adjust_city_budget("armaments", 10)
        elif key == arcade.key.KEY_8:
            game_state.adjust_city_budget("garrisons", 10)
        elif key == arcade.key.KEY_9:
            game_state.adjust_city_budget("defense_zones", 10)


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
            arcade.draw_text(
                f"{char.name} - Lvl {char.level} - SP {char.skill_points}",
                20,
                y,
                arcade.color.WHITE,
                14,
            )
            y -= 20
        arcade.draw_text(
            "Press N to recruit, B for Battle", 20, 20, arcade.color.AQUA, 14
        )

    def on_key_press(self, key, modifiers):
        global game_state
        if key == arcade.key.B:
            battle_view = BattleView()
            battle_view.setup()
            self.window.show_view(battle_view)
        elif key == arcade.key.N:
            idx = len(game_state.characters) + 1
            game_state.characters.append(Character(name=f"Agent {idx}"))


class BattleView(arcade.View):
    def setup(self):
        self.available_maps = [
            f for f in os.listdir("assets/maps") if f.lower().endswith(".jpeg")
        ]
        self.map_index = None
        self.background = None
        self.camera = arcade.Camera2D()
        self.player_units = [Unit(position=(64, 64))]
        # Random number of enemies between 1 and 3
        import random
        enemy_count = random.randint(1, 3)
        self.enemy_units = [
            Unit(position=(224 + i * 64, 224)) for i in range(enemy_count)
        ]
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        
        for unit in self.player_units:
            sprite = arcade.Sprite("assets/player.png", center_x=unit.position[0], center_y=unit.position[1])
            unit.sprite = sprite
            self.player_list.append(sprite)
            
        for enemy in self.enemy_units:
            sprite = arcade.Sprite(
                "assets/enemy.png", center_x=enemy.position[0], center_y=enemy.position[1]
            )
            enemy.sprite = sprite
            self.enemy_list.append(sprite)

        self.turn = "player"
        self.start_player_turn()

    def start_player_turn(self):
        for unit in self.player_units:
            unit.reset_actions()
        self.turn = "player"

    def start_enemy_turn(self):
        for enemy in self.enemy_units:
            enemy.reset_actions()
        self.turn = "enemy"
        self.run_enemy_ai()
        if not self.player_units or self.player_units[0].health <= 0:
            self.turn = "ended"
        elif not self.enemy_units:
            self.turn = "ended"
        else:
            self.start_player_turn()

    def run_enemy_ai(self):
        target = self.player_units[0]
        for enemy in list(self.enemy_units):
            while enemy.action_points > 0 and target.health > 0:
                if enemy.attack(target):
                    if target.health <= 0:
                        if target.sprite:
                            target.sprite.kill()
                        break
                else:
                    dx = 32 if target.position[0] > enemy.position[0] else -32 if target.position[0] < enemy.position[0] else 0
                    dy = 32 if target.position[1] > enemy.position[1] else -32 if target.position[1] < enemy.position[1] else 0
                    if dx or dy:
                        enemy.move(dx, dy)
            if enemy.health <= 0:
                if enemy.sprite:
                    enemy.sprite.kill()
                self.enemy_units.remove(enemy)

        
    def on_draw(self):
        self.clear()
        self.camera.use()
        if self.map_index is None:
            y = self.window.height - 40
            arcade.draw_text("Select battle map:", 20, y, arcade.color.WHITE, 20)
            y -= 40
            if not self.available_maps:
                arcade.draw_text(
                    "No maps found in assets/maps",
                    20,
                    y,
                    arcade.color.RED,
                    14,
                )
            else:
                for idx, name in enumerate(self.available_maps, start=1):
                    arcade.draw_text(
                        f"{idx} - {name}", 20, y, arcade.color.AQUA, 14
                    )
                    y -= 20
            return
        if self.background:
            # Build a rectangle: left, bottom, width, height
            full_rect = arcade.LBWH(
                0,
                0,
                self.window.width,
                self.window.height
            )
            # Draw the texture into that rect
            arcade.draw_texture_rect(
                self.background,  # Texture
                full_rect         # LBWH rect
                # └─── only two positional args! ───┘
                # You can also pass angle=..., alpha=... as keywords if desired
            )
        self.enemy_list.draw()
        self.player_list.draw()
        status = f"Turn: {self.turn.capitalize()}  Player HP: {self.player_units[0].health if self.player_units else 0}"
        arcade.draw_text(status, 20, self.window.height - 20, arcade.color.AQUA, 14)
        if self.turn == "ended":
            if not self.enemy_units:
                msg = "Victory!"
            else:
                msg = "Defeat..."
            arcade.draw_text(msg, 20, 40, arcade.color.YELLOW, 20)
        else:
            arcade.draw_text(
                "Arrows move, Space melee, F shoot, P psi atk, V psi def, D defend, Esc exit",
                20,
                20,
                arcade.color.AQUA,
                14,
            )

    def on_key_press(self, key, modifiers):
        if self.map_index is None:
            if arcade.key.KEY_1 <= key <= arcade.key.KEY_9:
                idx = key - arcade.key.KEY_1
                if idx < len(self.available_maps):
                    self.map_index = idx
                    path = os.path.join("assets/maps", self.available_maps[idx])
                    self.background = arcade.load_texture(path)
            elif key == arcade.key.ESCAPE:
                corp_view = CorpView()
                corp_view.setup()
                self.window.show_view(corp_view)
            return

        if self.turn != "player" or not self.player_units:
            return

        player = self.player_units[0]
        if key == arcade.key.UP:
            player.move(0, 32)
        elif key == arcade.key.DOWN:
            player.move(0, -32)
        elif key == arcade.key.LEFT:
            player.move(-32, 0)
        elif key == arcade.key.RIGHT:
            player.move(32, 0)
        elif key == arcade.key.SPACE:
            for enemy in list(self.enemy_units):
                if player.melee_attack(enemy):
                    if enemy.health <= 0:
                        if enemy.sprite:
                            enemy.sprite.kill()
                        self.enemy_units.remove(enemy)
                    break
        elif key == arcade.key.F:
            for enemy in list(self.enemy_units):
                if player.shoot(enemy):
                    if enemy.health <= 0:
                        if enemy.sprite:
                            enemy.sprite.kill()
                        self.enemy_units.remove(enemy)
                    break
        elif key == arcade.key.P:
            for enemy in list(self.enemy_units):
                if player.psi_attack(enemy):
                    if enemy.health <= 0:
                        if enemy.sprite:
                            enemy.sprite.kill()
                        self.enemy_units.remove(enemy)
                    break
        elif key == arcade.key.D:
            player.defend()
        elif key == arcade.key.V:
            player.psi_defend()
        elif key == arcade.key.ESCAPE:
            corp_view = CorpView()
            corp_view.setup()
            self.window.show_view(corp_view)

        if player.action_points <= 0:
            self.start_enemy_turn()
