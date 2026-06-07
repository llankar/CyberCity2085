"""Shared combat movement rule tests."""

import unittest

from game.combat.movement import can_enter_cell, path_to_cell, reachable_cells
from game.combat_system import run_enemy_ai
from game.unit import Unit


class FakeTerrainProfile:
    def __init__(self, walkable: set[tuple[int, int]]):
        self.walkable = walkable

    def is_walkable(self, x: int, y: int) -> bool:
        return (x, y) in self.walkable


def _unit(x: int, y: int, *, hp: int = 10, ap: int = 1) -> Unit:
    unit = Unit(position=(x, y), health=hp)
    unit.action_points = ap
    return unit


class CombatMovementRuleTest(unittest.TestCase):
    def test_blocked_terrain_refuses_entry(self):
        terrain = FakeTerrainProfile({(0, 0)})

        self.assertFalse(
            can_enter_cell(32, 0, terrain_profile=terrain, movement_mode="tactical_grid")
        )

    def test_occupied_cell_refuses_entry_in_tactical_grid(self):
        mover = _unit(0, 0)
        blocker = _unit(32, 0)
        terrain = FakeTerrainProfile({(0, 0), (32, 0)})

        self.assertFalse(
            can_enter_cell(
                32,
                0,
                terrain_profile=terrain,
                allied_units=[mover, blocker],
                enemy_units=[],
                exclude=mover,
                movement_mode="tactical_grid",
            )
        )

    def test_walkable_empty_cell_allows_entry_and_path(self):
        mover = _unit(0, 0)
        terrain = FakeTerrainProfile({(0, 0), (32, 0), (64, 0), (32, 32)})

        self.assertTrue(
            can_enter_cell(
                32,
                0,
                terrain_profile=terrain,
                allied_units=[mover],
                enemy_units=[],
                exclude=mover,
                movement_mode="tactical_grid",
            )
        )
        self.assertEqual(
            path_to_cell(
                (0, 0),
                (64, 0),
                2,
                width=96,
                height=64,
                terrain_profile=terrain,
                allied_units=[mover],
                exclude=mover,
            ),
            [(0, 0), (32, 0), (64, 0)],
        )

    def test_reachable_cells_excludes_refused_destination(self):
        mover = _unit(0, 0)
        blocker = _unit(32, 0)
        terrain = FakeTerrainProfile({(0, 0), (32, 0), (0, 32)})

        cells = reachable_cells(
            (0, 0),
            1,
            width=96,
            height=64,
            terrain_profile=terrain,
            allied_units=[mover, blocker],
            enemy_units=[],
            exclude=mover,
            movement_mode="tactical_grid",
        )

        self.assertIn((0, 32), cells)
        self.assertNotIn((32, 0), cells)

    def test_enemy_ai_refuses_blocked_movement_step(self):
        player = _unit(0, 0, hp=100)
        enemy = _unit(64, 0, hp=50, ap=1)
        enemy.unit_type = "enemy"
        terrain = FakeTerrainProfile({(0, 0), (64, 0)})

        results = run_enemy_ai([player], [enemy], terrain_profile=terrain)

        self.assertEqual(enemy.position, (64, 0))
        self.assertTrue(results)
        self.assertFalse(any(result.moved for result in results))


if __name__ == "__main__":
    unittest.main()
