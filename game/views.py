import arcade
import os
import random

from .character import Character
from .stats import PlayerStats, EnemyStats
from .gamestate import GameState
from .unit import Unit

def create_character(name: str, role: str) -> Character:
    stats = PlayerStats()
    if role == "samurai":
        stats.str += 5
    elif role == "sniper":
        stats.agi += 5
    elif role == "psi":
        stats.psi += 5
    stats.recalculate_hp()
    return Character(name=name, role=role, stats=stats)

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
        self.recruiting = False
        self.selected_role = None
        self.allocating = None

    def on_draw(self):
        self.clear()
        arcade.draw_text(self.text, 20, self.window.height - 40, arcade.color.WHITE, 20)
        y = self.window.height - 80
        for char in game_state.characters:
            s = char.stats
            info = f"{char.name} ({char.role}) Lv{s.level} HP{s.hp}/{s.max_hp} STR{s.str} AGI{s.agi} PSI{s.psi} DEF{s.defense} CON{s.con} CHA{s.cha} XP{s.xp}"
            arcade.draw_text(info, 20, y, arcade.color.WHITE, 14)
            if char.pending_points > 0:
                arcade.draw_text(
                    f"  Allocate {char.pending_points} pts: 1=PSI 2=STR 3=AGI 4=CON 5=CHA",
                    40,
                    y - 15,
                    arcade.color.AQUA,
                    12,
                )
                y -= 15
            y -= 20
        if self.recruiting:
            arcade.draw_text(
                "Select role: 1 Samurai, 2 Sniper, 3 Psi", 20, y, arcade.color.YELLOW, 14
            )
            y -= 20
        arcade.draw_text(
            "Press N to recruit, B for Battle", 20, 20, arcade.color.AQUA, 14
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.B:
            battle_view = BattleView()
            battle_view.setup()
            self.window.show_view(battle_view)
        elif key == arcade.key.N:
            if game_state.budget_pool >= 5:
                self.recruiting = True
                self.selected_role = None
                game_state.budget_pool -= 5
            else:
                pass
        elif self.recruiting:
            if key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
                idx = len(game_state.characters) + 1
                role_map = {arcade.key.KEY_1: "samurai", arcade.key.KEY_2: "sniper", arcade.key.KEY_3: "psi"}
                role = role_map.get(key, "samurai")
                game_state.characters.append(create_character(f"Agent {idx}", role))
                self.recruiting = False
        else:
            # Allocate stat points if any
            for char in game_state.characters:
                if char.pending_points > 0:
                    if key == arcade.key.KEY_1:
                        char.stats.psi += 1
                    elif key == arcade.key.KEY_2:
                        char.stats.str += 1
                    elif key == arcade.key.KEY_3:
                        char.stats.agi += 1
                    elif key == arcade.key.KEY_4:
                        char.stats.con += 1
                    elif key == arcade.key.KEY_5:
                        char.stats.cha += 1
                    else:
                        break
                    char.pending_points -= 1
                    char.stats.recalculate_hp()
                    break


class BattleView(arcade.View):
    def setup(self):
        self.available_maps = [
            f for f in os.listdir("assets/maps") if f.lower().endswith(".jpeg")
        ]
        self.map_index = None
        self.background = None
        self.camera = arcade.Camera2D()
        self.player_units = [
            Unit(
                position=(64 + i * 64, 64),
                stats=char.stats,
                health=char.stats.hp,
                character=char,
            )
            for i, char in enumerate(game_state.characters)
        ]
        avg_level = (
            sum(c.stats.level for c in game_state.characters) / len(game_state.characters)
            if game_state.characters else 1
        )
        enemy_count = random.randint(1, 3)
        self.initial_enemy_count = enemy_count
        self.enemy_units = []
        for i in range(enemy_count):
            level = random.randint(1, int(avg_level))
            estats = EnemyStats(level=level, defense=level, psi=level, str=level, agi=level)
            unit = Unit(position=(224 + i * 64, 224), stats=estats, health=estats.hp)
            self.enemy_units.append(unit)
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

        self.turn_number = 1
        self.turn = "player"
        self.active_index = 0
        self.message = ""
        self.attack_timer = 0.0
        self.attack_line = None
        # Target selection state
        self.selecting_target = False
        self.target_candidates = []
        self.selected_target_idx = 0
        self.pending_attack = None
        self.start_player_turn()

    def start_player_turn(self):
        for unit in self.player_units:
            unit.reset_actions()
        if self.turn == "enemy":
            self.turn_number += 1
        self.turn = "player"
        self.active_index = 0

    def start_enemy_turn(self):
        for enemy in self.enemy_units:
            enemy.reset_actions()
        self.turn = "enemy"
        self.run_enemy_ai()
        if not self.player_units:
            self.end_battle(False)
            return
        elif not self.enemy_units:
            self.end_battle(True)
            return
        else:
            self.start_player_turn()

    def end_battle(self, victory: bool) -> None:
        """Finish the battle and return to the RPG view."""
        defeated = self.initial_enemy_count if victory else 0
        if victory:
            game_state.x += 50 * defeated
        for unit in list(self.player_units):
            if unit.character:
                unit.character.stats.hp = unit.health
                if victory:
                    unit.character.gain_xp(50 * defeated)
                if unit.health <= 0 and unit.character in game_state.characters:
                    game_state.characters.remove(unit.character)
        rpg_view = RPGView()
        rpg_view.setup()
        self.window.show_view(rpg_view)
        
    def run_enemy_ai(self):
        for enemy in list(self.enemy_units):
            target = self.player_units[0] if self.player_units else None
            if not target:
                break
            while enemy.action_points > 0 and target.health > 0:
                damage = enemy.attack(target)
                if damage > 0:
                    self.message = f"Enemy hits {target.character.name} for {damage}"
                    self.start_attack_animation(enemy, target)
                    if target.health <= 0:
                        if target.sprite:
                            target.sprite.kill()
                        idx = self.player_units.index(target)
                        self.player_units.remove(target)
                        if idx <= self.active_index and self.active_index > 0:
                            self.active_index -= 1
                        if not self.player_units:
                            break
                        break
                else:
                    dx = (
                        32 if target.position[0] > enemy.position[0] else -32 if target.position[0] < enemy.position[0] else 0
                    )
                    dy = (
                        32 if target.position[1] > enemy.position[1] else -32 if target.position[1] < enemy.position[1] else 0
                    )
                    if dx or dy:
                        enemy.move(dx, dy)
            if enemy.health <= 0:
                if enemy.sprite:
                    enemy.sprite.kill()
                self.enemy_units.remove(enemy)
            if not self.player_units:
                break
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
        if self.selecting_target and self.target_candidates:
            target = self.target_candidates[self.selected_target_idx]
            if target.sprite:
                arcade.draw_rectangle_outline(
                    target.sprite.center_x,
                    target.sprite.center_y,
                    target.sprite.width + 10,
                    target.sprite.height + 10,
                    arcade.color.YELLOW,
                    2,
                )
        if self.attack_line:
            x1, y1, x2, y2 = self.attack_line
            arcade.draw_line(x1, y1, x2, y2, arcade.color.YELLOW, 2)
        current_hp = (
            self.player_units[self.active_index].health if self.player_units else 0
        )
        status = (
            f"Turn {self.turn_number} - {self.turn.capitalize()}  Player HP: {current_hp}"
        )
        arcade.draw_text(status, 20, self.window.height - 20, arcade.color.AQUA, 14)
        if self.message:
            arcade.draw_text(self.message, 20, self.window.height - 40, arcade.color.YELLOW, 16)
        if self.turn == "ended":
            if not self.enemy_units:
                msg = "Victory!"
            else:
                msg = "Defeat..."
            arcade.draw_text(msg, 20, 40, arcade.color.YELLOW, 20)
        else:
            if self.selecting_target:
                arcade.draw_text(
                    "Select target with Left/Right, Enter to confirm, Esc to cancel",
                    20,
                    20,
                    arcade.color.AQUA,
                    14,
                )
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

        player = self.player_units[self.active_index]

        # Handle target selection mode
        if self.selecting_target:
            if key in (arcade.key.LEFT, arcade.key.A):
                self.selected_target_idx = (self.selected_target_idx - 1) % len(self.target_candidates)
            elif key in (arcade.key.RIGHT, arcade.key.D):
                self.selected_target_idx = (self.selected_target_idx + 1) % len(self.target_candidates)
            elif key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.SPACE, arcade.key.F, arcade.key.P):
                target = self.target_candidates[self.selected_target_idx]
                if self.pending_attack == "melee":
                    damage = player.melee_attack(target)
                elif self.pending_attack == "shoot":
                    damage = player.shoot(target)
                else:
                    damage = player.psi_attack(target)
                if damage > 0:
                    atk_name = {
                        "melee": "slashes",
                        "shoot": "shoots",
                        "psi": "psy hits",
                    }[self.pending_attack]
                    self.message = f"{player.character.name} {atk_name} for {damage}"
                    self.start_attack_animation(player, target)
                    if target.health <= 0:
                        if target.sprite:
                            target.sprite.kill()
                        if target in self.enemy_units:
                            self.enemy_units.remove(target)
                        if not self.enemy_units:
                            self.end_battle(True)
                            self.selecting_target = False
                            self.target_candidates = []
                            self.pending_attack = None
                            return
                self.selecting_target = False
                self.target_candidates = []
                self.pending_attack = None
                self.check_active_player()
            elif key == arcade.key.ESCAPE:
                self.selecting_target = False
                self.target_candidates = []
                self.pending_attack = None
            return

        # Normal input handling when not selecting target
        if key == arcade.key.UP:
            player.move(0, 32)
        elif key == arcade.key.DOWN:
            player.move(0, -32)
        elif key == arcade.key.LEFT:
            player.move(-32, 0)
        elif key == arcade.key.RIGHT:
            player.move(32, 0)
        elif key == arcade.key.SPACE:
            self.target_candidates = [e for e in self.enemy_units if player.distance_to(e) <= 32]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "melee"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.F:
            self.target_candidates = [e for e in self.enemy_units if player.distance_to(e) <= 10 * 32]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "shoot"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.P:
            self.target_candidates = [e for e in self.enemy_units if player.distance_to(e) <= 10 * 32]
            if self.target_candidates:
                self.selecting_target = True
                self.selected_target_idx = 0
                self.pending_attack = "psi"
            else:
                self.message = "No enemy in range"
        elif key == arcade.key.D:
            player.defend()
        elif key == arcade.key.V:
            player.psi_defend()
        elif key == arcade.key.ESCAPE:
            corp_view = CorpView()
            corp_view.setup()
            self.window.show_view(corp_view)

        self.check_active_player()

    def check_active_player(self):
        while (
            self.active_index < len(self.player_units)
            and (
                self.player_units[self.active_index].action_points <= 0
                or self.player_units[self.active_index].health <= 0
            )
        ):
            self.active_index += 1
        if self.active_index >= len(self.player_units):
            self.start_enemy_turn()

    def start_attack_animation(self, attacker: Unit, target: Unit):
        self.attack_line = (
            attacker.position[0],
            attacker.position[1],
            target.position[0],
            target.position[1],
        )
        self.attack_timer = 0.3

    def on_update(self, delta_time: float):
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.attack_line = None
