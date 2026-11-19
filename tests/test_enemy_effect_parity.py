"""Status rules must run in the engine, once, independently of visual callbacks."""

from unittest.mock import Mock, patch

import pytest

from game.combat_system import _check_overwatch, _resolve_enemy_attack
from game.stats import EnemyStats, PlayerStats
from game.unit import Unit
from game.views import BattleView


def visual_callbacks():
    view = BattleView.__new__(BattleView)
    view.combat_log_messages = []
    view._snd = Mock()
    for name in ("_add_damage_popup","_add_status_popup","_spawn_muzzle_flash","_spawn_particles",
                 "_flash_unit","_add_screen_shake","start_attack_animation"):
        setattr(view,name,Mock())
    return view._enemy_ai_callbacks()


@pytest.mark.parametrize("with_visuals", [False,True])
def test_heavy_melee_stuns_once_with_or_without_visuals(with_visuals):
    enemy = Unit(position=(0,0),health=100,stats=EnemyStats(str=4,max_hp=100),
                 unit_type="enemy",enemy_subtype="heavy")
    target = Unit(position=(32,0),health=100,stats=PlayerStats(hp=100,max_hp=100))
    with patch("game.combat.attack_resolution.random.random",return_value=0), \
            patch.object(target,"apply_status",wraps=target.apply_status) as status:
        result = _resolve_enemy_attack(enemy,target,"melee",[enemy],[])
        if with_visuals:
            visual_callbacks()["on_attack"](enemy,target,result.damage)
        assert result.damage > 0 and target.has_status("stunned")
        status.assert_called_once_with("stunned")


@pytest.mark.parametrize("with_visuals", [False,True])
def test_overwatch_suppresses_once_with_or_without_visuals(with_visuals):
    watcher = Unit(position=(0,0),health=100,stats=PlayerStats(str=4,hp=100,max_hp=100),attack_range=4)
    watcher.on_overwatch = True
    watcher.attack_range = 4
    watcher.stats.agi = 4
    enemy = Unit(position=(64,0),health=100,stats=EnemyStats(hp=100,max_hp=100),unit_type="enemy")
    callback = visual_callbacks()["on_overwatch_shot"] if with_visuals else None
    with patch("game.combat.attack_resolution.random.random",return_value=0), \
            patch.object(enemy,"apply_status",wraps=enemy.apply_status) as status:
        assert not _check_overwatch(enemy,[watcher],[enemy],callback,None,[])
        assert enemy.has_status("suppressed") and not watcher.on_overwatch
        status.assert_called_once_with("suppressed")


def test_missed_heavy_melee_and_overwatch_apply_no_control_status():
    enemy = Unit(position=(0,0),health=20,stats=EnemyStats(),unit_type="enemy",enemy_subtype="heavy")
    target = Unit(position=(32,0),health=20,stats=PlayerStats())
    with patch("game.combat.attack_resolution.random.random",return_value=1):
        result = _resolve_enemy_attack(enemy,target,"melee",[enemy],[])
        assert result.damage == 0 and not target.has_status("stunned")
        target.on_overwatch = True
        target.attack_range = 4
        assert not _check_overwatch(enemy,[target],[enemy],None,None,[])
        assert not enemy.has_status("suppressed") and not target.on_overwatch
