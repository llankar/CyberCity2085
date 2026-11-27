import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from game.combat import CombatEngine, CombatState
from game.combat.movement import CELL_SIZE
from game.stats import EnemyStats, PlayerStats
from game.unit import STATUS_BLEEDING, Unit
from tactical_preview import TacticalPreview
from tactical_mailbox import TacticalMailbox
from run_tactical_preview import CATALOG, SCENARIOS, battlefield_presentation, scenario_maps, scenario_preview, selected_map


class TacticalPreviewTest(unittest.TestCase):
    def test_lethal_attack_reports_victory_and_disables_actions(self):
        preview = scenario_preview("warehouse")
        ally, enemy = preview.units["ally:0"], preview.units["enemy:0"]
        ally.stats.agi = 10
        enemy.stats.hp = enemy.health = 1
        with patch("game.combat.attack_resolution.random.random", return_value=0.0):
            result = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertTrue(result["success"])
        self.assertEqual(result["state"]["outcome"], "victory")
        self.assertEqual(result["state"]["units"][0]["moves"], [])
        self.assertEqual(result["state"]["units"][0]["actions"], [])
        self.assertEqual(result["state"]["units"][0]["targeting"], {})
        self.assertFalse(preview.action("end_turn", "ally:0")["success"])

    def test_attack_replies_distinguish_hit_miss_and_rejection(self):
        preview = scenario_preview("warehouse")
        preview.units["ally:0"].stats.agi = 10
        with patch("game.combat.attack_resolution.random.random", return_value=.9999):
            missed = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertEqual(missed["attack"], {"hit": False, "damage": 0})
        with patch("game.combat.attack_resolution.random.random", return_value=0.0):
            hit = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertTrue(hit["attack"]["hit"])
        self.assertGreater(hit["attack"]["damage"], 0)
        rejected = preview.action("fire", "ally:0", target_id="ally:1")
        self.assertNotIn("attack", rejected)

    def test_oracle_has_independent_psi_ap_and_can_receive_adjacent_aid(self):
        preview = scenario_preview("metro")
        sniper, oracle = (preview.units[key] for key in ("ally:0", "ally:1"))
        self.assertTrue(preview.action("move", "ally:0", destination=[17, 13])["success"])
        oracle.health = oracle.stats.hp = 6
        self.assertTrue(preview.action("first_aid", "ally:0", target_id="ally:1")["success"])
        self.assertEqual(oracle.health, 8)
        self.assertEqual(oracle.action_points, 3)
        self.assertTrue(preview.action("psi", "ally:1", target_id="enemy:0")["success"])
        self.assertEqual(oracle.action_points, 2)
        self.assertEqual(sniper.action_points, 1)

    def test_equipped_support_actions_apply_existing_combat_rules(self):
        preview = scenario_preview("warehouse")
        ally = preview.units["ally:0"]
        ally.health = ally.stats.hp = 5
        ally.apply_status(STATUS_BLEEDING)
        result = preview.action("first_aid", "ally:0")
        self.assertTrue(result["success"], result)
        self.assertEqual(ally.health, 7)
        self.assertFalse(ally.has_status(STATUS_BLEEDING))
        self.assertTrue(preview.action("defend", "ally:0")["state"]["units"][0]["defending"])
        self.assertTrue(preview.action("overwatch", "ally:0")["state"]["units"][0]["overwatch"])
        self.assertEqual(ally.action_points, 0)

    def test_melee_uses_close_range(self):
        preview = scenario_preview("warehouse")
        ally = preview.units["ally:0"]
        enemy = preview.units["enemy:0"]
        self.assertFalse(preview.action("melee", "ally:0", target_id="enemy:0")["success"])
        self.assertEqual(ally.action_points, 3)
        enemy.position = (ally.position[0] + CELL_SIZE, ally.position[1])
        result = preview.action("melee", "ally:0", target_id="enemy:0")
        self.assertTrue(result["success"], result)
        self.assertEqual(ally.action_points, 2)

    def test_rooftop_canyons_block_movement_without_spending_ap(self):
        cases = (("rooftop", (19, 3), [18, 3]), ("skybridge", (15, 11), [16, 11]))
        for name, start, destination in cases:
            with self.subTest(map=name):
                preview = scenario_preview(name)
                ally = preview.units["ally:0"]
                origin = tuple(axis * CELL_SIZE for axis in start)
                terrain = preview.engine.terrain_profile
                self.assertIn(origin, terrain.walkable_cells)
                ally.position = origin
                result = preview.action("move", "ally:0", destination=destination)
                self.assertFalse(result["success"])
                self.assertEqual(ally.position, origin)
                self.assertEqual(ally.action_points, 3)

    def test_selector_accepts_only_configured_maps(self):
        lab_tmp = Path("E:/CyberCity2085-3d-lab/tmp")
        with tempfile.TemporaryDirectory(dir=lab_tmp if lab_tmp.is_dir() else None) as temp:
            directory = Path(temp)
            self.assertIsNone(selected_map(directory))
            request = directory / "map-selection.txt"
            request.write_text("metro", encoding="utf-8")
            self.assertEqual(selected_map(directory), "metro")
            request.write_text("../warehouse", encoding="utf-8")
            with self.assertRaises(ValueError):
                selected_map(directory)

    def test_enemy_hit_events_preserve_engine_damage_and_positions(self):
        preview = scenario_preview("warehouse")
        enemy = preview.units["enemy:0"]
        enemy.attack_range = 10
        allies = {key: unit for key, unit in preview.units.items() if key.startswith("ally:")}
        starting_hp = {key: unit.health for key, unit in allies.items()}
        with patch("game.combat.attack_resolution.random.random", return_value=.2):
            result = preview.action("end_turn", "ally:0")
        self.assertTrue(result["success"])
        events = result["events"]
        self.assertTrue(events)
        for key, unit in allies.items():
            self.assertEqual(sum(event["damage"] for event in events if event["target"] == key),
                             starting_hp[key] - unit.health)
        self.assertEqual(events[0]["actor"], "enemy:0")
        self.assertEqual(events[0]["to_cell"], [
            axis // CELL_SIZE for axis in allies[events[0]["target"]].position
        ])

    def test_warehouse_fire_spends_ap_and_surveyed_cover_blocks_fire(self):
        preview = scenario_preview("warehouse")
        ally = preview.units["ally:0"]
        enemy = preview.units["enemy:0"]
        position = enemy.position
        enemy.position = (7 * CELL_SIZE, 10 * CELL_SIZE)
        hint = preview.snapshot()["units"][0]["targeting"]["enemy:0"]["fire"]
        self.assertTrue(hint["line_blocked"])
        self.assertTrue(hint["in_range"])
        self.assertTrue(hint["can_pay"])
        rejected = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertFalse(rejected["success"])
        self.assertIn("line blocked", rejected["message"])
        self.assertEqual(ally.action_points, 3)
        enemy.position = position
        fired = preview.action("fire", "ally:0", target_id="enemy:0")
        self.assertTrue(fired["success"], fired)
        self.assertEqual(ally.action_points, 2)

    def test_all_catalogue_maps_have_a_playable_deployment(self):
        catalogue = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(scenario_maps()), len(catalogue))
        map_names = set()
        for key in scenario_maps():
            with self.subTest(map=key):
                presentation = battlefield_presentation(key)
                scene = CATALOG.parent / presentation["preview_scene"].removeprefix("res://")
                self.assertTrue(scene.is_file(), scene)
                preview = scenario_preview(key)
                terrain = preview.engine.terrain_profile
                map_names.add(Path(terrain.image_path).stem)
                geometry = json.loads(Path(terrain.image_path).with_suffix(".walls.json").read_text())
                width, height = geometry["grid"]
                authored_blocked = {tuple(cell) for wall in geometry["walls"] for cell in wall["cells"]}
                presented_blocked = {
                    (column, row) for column in range(width) for row in range(height)
                    if (column * CELL_SIZE, (height - 1 - row) * CELL_SIZE) not in terrain.walkable_cells
                }
                self.assertEqual(authored_blocked, presented_blocked)
                positions = {unit.position for unit in preview.units.values()}
                self.assertEqual(len(positions), 3)
                self.assertTrue(positions <= terrain.walkable_cells)
                ally = preview.units["ally:0"]
                targeting = preview.attack_previews(ally)["enemy:0"]["fire"]
                self.assertGreater(targeting["hit_percent"], 0)
                options = preview.move_options(ally)
                self.assertTrue(options, "Lead operative has no starting move")
                move = preview.action("move", "ally:0", destination=options[0])
                self.assertTrue(move["success"], move["message"])
                self.assertEqual(move["state"]["units"][0]["cell"], options[0])
                phase = preview.action("end_turn", "ally:0")
                self.assertTrue(phase["success"], phase["message"])
                self.assertIsNone(phase["state"]["outcome"])
                self.assertEqual((phase["state"]["turn"], phase["state"]["round"]), ("player", 2))
        self.assertEqual(map_names, {entry["map"] for entry in catalogue})

    def test_scenarios_use_original_geometry_and_advance_round(self):
        for name, (map_name, (x, y), _) in SCENARIOS.items():
            with self.subTest(map=name):
                presentation = battlefield_presentation(name)
                scene_path = CATALOG.parent / presentation["preview_scene"].removeprefix("res://")
                self.assertTrue(scene_path.is_file())
                preview = scenario_preview(name)
                terrain = preview.engine.terrain_profile
                self.assertEqual(terrain.source, "manual_wall_traces_v1")
                self.assertEqual(Path(terrain.image_path).stem, map_name)
                destination = [x + 1, y]
                moved = preview.action("move", "ally:0", destination=destination)
                self.assertTrue(moved["success"], moved)
                self.assertEqual(moved["state"]["units"][0]["cell"], destination)
                result = preview.action("end_turn", "ally:0")
                self.assertTrue(result["success"], result)
                self.assertEqual(result["state"]["turn"], "player")
                self.assertEqual(result["state"]["round"], 2)

    def test_engine_updates_position_ap_and_rejects_blocked_cell(self):
        ally = Unit(position=(64, 64), stats=PlayerStats(), health=10, action_points=3)
        enemy = Unit(position=(320, 64), stats=EnemyStats(level=1), health=10, unit_type="enemy")
        engine = CombatEngine(CombatState(None, [ally], [enemy]),
                              can_enter=lambda x, y: x != 128)
        preview = TacticalPreview(engine)
        from game.cover_system import CoverNode
        engine.cover_nodes = [CoverNode(3, 3, "high", passable=False)]
        self.assertEqual(preview.snapshot()["units"][0]["covered_moves"], [[3, 2], [2, 3]])
        self.assertEqual(ally.position, (64, 64))
        starting_moves = preview.snapshot()["units"][0]["moves"]
        self.assertIn([3, 2], starting_moves)
        self.assertNotIn([4, 2], starting_moves)
        result = preview.action("move", "ally:0", destination=[3, 2])
        self.assertTrue(result["success"], result)
        self.assertEqual(result["state"]["units"][0]["cell"], [3, 2])
        self.assertLess(ally.action_points, 3)
        self.assertNotIn([4, 2], result["state"]["units"][0]["moves"])
        self.assertIn([2, 2], result["state"]["units"][0]["moves"])
        rejected = preview.action("move", "ally:0", destination=[4, 2])
        self.assertFalse(rejected["success"], rejected)
        self.assertEqual(rejected["state"], result["state"])


    def test_mailbox_applies_each_command_once(self):
        ally = Unit(position=(64, 64), stats=PlayerStats(), health=10, action_points=3)
        enemy = Unit(position=(320, 64), stats=EnemyStats(level=1), health=10, unit_type="enemy")
        engine = CombatEngine(CombatState(None, [ally], [enemy]))
        lab_tmp = Path("E:/CyberCity2085-3d-lab/tmp")
        with tempfile.TemporaryDirectory(dir=lab_tmp if lab_tmp.is_dir() else None) as temp:
            directory = Path(temp)
            mailbox = TacticalMailbox(directory, TacticalPreview(engine))
            command = directory / "command-1.json"
            command.write_text('{"action":', encoding="utf-8")
            self.assertFalse(mailbox.poll())
            command.write_text(json.dumps({"action":"move","actor":"ally:0","destination":[3,2]}),
                               encoding="utf-8")
            self.assertTrue(mailbox.poll())
            response = json.loads((directory / "reply-1.json").read_text(encoding="utf-8"))
            original = json.loads((directory / "reply-0.json").read_text(encoding="utf-8"))
            self.assertEqual(original["state"]["units"][0]["cell"], [2, 2])
            self.assertEqual(response["sequence"], 1)
            self.assertTrue(response["success"])
            self.assertFalse(mailbox.poll())
            self.assertEqual(ally.position, (96,64))
