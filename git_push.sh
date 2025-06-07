 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 572ba637dd373f6faca437db3d4eb5b15c655d33..c58fde8eb03db9daa5bdf147096125273609460a 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,15 @@
 # CyberCity2085
-Cybercity2085 python game
+
+Prototype project mixing corporation management, RPG progression and tactical battles built with [Arcade](https://api.arcade.academy/).
+
+Run with:
+```bash
+pip install -r requirements.txt
+python main.py
+```
+
+## Project structure
+- `assets/` – game art and other assets
+- `scenes/` – Tiled TMX maps
+- `game/` – core game modules
+- `main.py` – starts the game window and initial view
diff --git a/assets/empty.png b/assets/empty.png
new file mode 100644
index 0000000000000000000000000000000000000000..909c66db1740b7c1b41eb4db6c414a7ab5bb6a23
GIT binary patch
literal 68
zcmeAS@N?(olHy`uVBq!ia0vp^j3CUx0wlM}@Gt=>Zci7-kcwN$DG5Lh8v~O;;{|;n
Oi^0>?&t;ucLK6U5DhwL{

literal 0
HcmV?d00001

diff --git a/game/__init__.py b/game/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
diff --git a/game/building.py b/game/building.py
new file mode 100644
index 0000000000000000000000000000000000000000..200fe7bf24860285d2acf6da418a20dbab285f22
--- /dev/null
+++ b/game/building.py
@@ -0,0 +1,7 @@
+from dataclasses import dataclass
+
+
+@dataclass
+class Building:
+    name: str
+    level: int = 1
diff --git a/game/character.py b/game/character.py
new file mode 100644
index 0000000000000000000000000000000000000000..c69ad84ef0c98c3bdb140870bda4f283a421a994
--- /dev/null
+++ b/game/character.py
@@ -0,0 +1,30 @@
+from dataclasses import dataclass, field
+from typing import Dict
+
+
+@dataclass
+class Character:
+    name: str
+    level: int = 1
+    skill_points: int = 0
+    talents: Dict[str, int] = field(default_factory=dict)
+    equipment: Dict[str, str] = field(default_factory=dict)
+
+    def to_dict(self) -> dict:
+        return {
+            "name": self.name,
+            "level": self.level,
+            "skill_points": self.skill_points,
+            "talents": self.talents,
+            "equipment": self.equipment,
+        }
+
+    @classmethod
+    def from_dict(cls, data: dict) -> "Character":
+        return cls(
+            name=data.get("name", "Unnamed"),
+            level=data.get("level", 1),
+            skill_points=data.get("skill_points", 0),
+            talents=data.get("talents", {}),
+            equipment=data.get("equipment", {}),
+        )
diff --git a/game/gamestate.py b/game/gamestate.py
new file mode 100644
index 0000000000000000000000000000000000000000..600fd5c41592a969e23a23a59c8857be5787de7e
--- /dev/null
+++ b/game/gamestate.py
@@ -0,0 +1,39 @@
+import json
+from dataclasses import dataclass, field
+from typing import List
+
+
+@dataclass
+class GameState:
+    corp_budget: dict = field(default_factory=lambda: {
+        "research": 0,
+        "security": 0,
+        "politics": 0,
+        "black_ops": 0,
+    })
+    city_budget: dict = field(default_factory=lambda: {
+        "armaments": 0,
+        "garrisons": 0,
+        "defense_zones": 0,
+    })
+    characters: List["Character"] = field(default_factory=list)
+
+    def save(self, path: str):
+        data = {
+            "corp_budget": self.corp_budget,
+            "city_budget": self.city_budget,
+            "characters": [c.to_dict() for c in self.characters],
+        }
+        with open(path, "w", encoding="utf-8") as f:
+            json.dump(data, f, indent=2)
+
+    @classmethod
+    def load(cls, path: str) -> "GameState":
+        with open(path, "r", encoding="utf-8") as f:
+            data = json.load(f)
+        gs = cls()
+        gs.corp_budget.update(data.get("corp_budget", {}))
+        gs.city_budget.update(data.get("city_budget", {}))
+        from .character import Character
+        gs.characters = [Character.from_dict(c) for c in data.get("characters", [])]
+        return gs
diff --git a/game/unit.py b/game/unit.py
new file mode 100644
index 0000000000000000000000000000000000000000..270444546108a987180e635d3476cec145ec24b9
--- /dev/null
+++ b/game/unit.py
@@ -0,0 +1,13 @@
+from dataclasses import dataclass, field
+from typing import Tuple
+
+
+@dataclass
+class Unit:
+    position: Tuple[int, int]
+    action_points: int = 2
+
+    def move(self, dx: int, dy: int):
+        x, y = self.position
+        self.position = (x + dx, y + dy)
+        self.action_points -= 1
diff --git a/game/views.py b/game/views.py
new file mode 100644
index 0000000000000000000000000000000000000000..68b58dabad6d74b8692b8a07465098cf9558b4d3
--- /dev/null
+++ b/game/views.py
@@ -0,0 +1,104 @@
+import arcade
+from .gamestate import GameState
+from .character import Character
+from .unit import Unit
+
+
+game_state = GameState()
+
+
+class CorpView(arcade.View):
+    def setup(self):
+        self.text = "Corporation Management"
+
+    def on_draw(self):
+        arcade.start_render()
+        y = self.window.height - 40
+        arcade.draw_text(self.text, 20, y, arcade.color.WHITE, 20)
+        y -= 40
+        for k, v in game_state.corp_budget.items():
+            arcade.draw_text(f"{k}: {v}", 20, y, arcade.color.WHITE, 14)
+            y -= 20
+        arcade.draw_text("Press C for City, R for RPG", 20, 20, arcade.color.AQUA, 14)
+
+    def on_key_press(self, key, modifiers):
+        if key == arcade.key.C:
+            city_view = CityView()
+            city_view.setup()
+            self.window.show_view(city_view)
+        elif key == arcade.key.R:
+            rpg_view = RPGView()
+            rpg_view.setup()
+            self.window.show_view(rpg_view)
+
+
+class CityView(arcade.View):
+    def setup(self):
+        self.text = "City Management"
+
+    def on_draw(self):
+        arcade.start_render()
+        y = self.window.height - 40
+        arcade.draw_text(self.text, 20, y, arcade.color.WHITE, 20)
+        y -= 40
+        for k, v in game_state.city_budget.items():
+            arcade.draw_text(f"{k}: {v}", 20, y, arcade.color.WHITE, 14)
+            y -= 20
+        arcade.draw_text("Press R for RPG", 20, 20, arcade.color.AQUA, 14)
+
+    def on_key_press(self, key, modifiers):
+        if key == arcade.key.R:
+            rpg_view = RPGView()
+            rpg_view.setup()
+            self.window.show_view(rpg_view)
+
+
+class RPGView(arcade.View):
+    def setup(self):
+        if not game_state.characters:
+            game_state.characters.append(Character(name="Agent 1"))
+        self.text = "RPG Phase"
+
+    def on_draw(self):
+        arcade.start_render()
+        arcade.draw_text(self.text, 20, self.window.height - 40, arcade.color.WHITE, 20)
+        y = self.window.height - 80
+        for char in game_state.characters:
+            arcade.draw_text(f"{char.name} - Lvl {char.level} - SP {char.skill_points}", 20, y, arcade.color.WHITE, 14)
+            y -= 20
+        arcade.draw_text("Press B for Battle", 20, 20, arcade.color.AQUA, 14)
+
+    def on_key_press(self, key, modifiers):
+        if key == arcade.key.B:
+            battle_view = BattleView()
+            battle_view.setup()
+            self.window.show_view(battle_view)
+
+
+class BattleView(arcade.View):
+    def setup(self):
+        self.map = arcade.load_tilemap("scenes/test.tmx")
+        self.scene = arcade.Scene.from_tilemap(self.map)
+        self.camera = arcade.Camera(self.window.width, self.window.height)
+        self.unit = Unit(position=(64, 64))
+
+    def on_draw(self):
+        arcade.start_render()
+        self.camera.use()
+        self.scene.draw()
+        x, y = self.unit.position
+        arcade.draw_circle_filled(x, y, 10, arcade.color.RED)
+
+    def on_key_press(self, key, modifiers):
+        if key == arcade.key.UP:
+            self.unit.move(0, 32)
+        elif key == arcade.key.DOWN:
+            self.unit.move(0, -32)
+        elif key == arcade.key.LEFT:
+            self.unit.move(-32, 0)
+        elif key == arcade.key.RIGHT:
+            self.unit.move(32, 0)
+        elif key == arcade.key.ESCAPE:
+            corp_view = CorpView()
+            corp_view.setup()
+            self.window.show_view(corp_view)
diff --git a/main.py b/main.py
new file mode 100644
index 0000000000000000000000000000000000000000..a0a924a5191fcb88640d54cd3d65938436d9afa8
--- /dev/null
+++ b/main.py
@@ -0,0 +1,14 @@
+import arcade
+from game.views import CorpView
+
+
+def main():
+    window = arcade.Window(800, 600, "CyberCity 2085")
+    start_view = CorpView()
+    start_view.setup()
+    window.show_view(start_view)
+    arcade.run()
+
+
+if __name__ == "__main__":
+    main()
diff --git a/requirements.txt b/requirements.txt
new file mode 100644
index 0000000000000000000000000000000000000000..77078445b26ee278c4729b3bd0f201629d633b35
--- /dev/null
+++ b/requirements.txt
@@ -0,0 +1 @@
+arcade==2.6.17
diff --git a/scenes/test.tmx b/scenes/test.tmx
new file mode 100644
index 0000000000000000000000000000000000000000..627fd7deb8cc21090dd5c2e19d7eceee5d6e7702
--- /dev/null
+++ b/scenes/test.tmx
@@ -0,0 +1,20 @@
+<?xml version="1.0" encoding="UTF-8"?>
+<map version="1.4" tiledversion="1.4.2" orientation="orthogonal" renderorder="right-down" width="10" height="10" tilewidth="32" tileheight="32" infinite="0" nextlayerid="2" nextobjectid="1">
+ <tileset firstgid="1" name="base" tilewidth="32" tileheight="32" tilecount="1" columns="1">
+  <image source="../assets/empty.png" width="1" height="1"/>
+ </tileset>
+ <layer id="1" name="Tile Layer 1" width="10" height="10">
+  <data encoding="csv">
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0,
+0,0,0,0,0,0,0,0,0,0
+  </data>
+ </layer>
+</map>
 
EOF
)