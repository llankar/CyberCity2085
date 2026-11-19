"""Actual BattleView visual timers advance in seconds, independent of frame count."""

from types import SimpleNamespace

import pytest

from game.views import BattleView


def effects_state():
    return SimpleNamespace(map_index=0,_battle_elapsed=0,attack_timer=0.3,attack_line=(0,0,32,0),
                           _flash_alpha=160.,_aftermath_timer=2.2,
                           damage_popups=[{"age":0.,"max_age":1.2}],
                           particles=[{"x":0.,"y":0.,"vx":60.,"vy":100.,"life":1.}],
                           _unit_flashes={1:{"timer":0.15}},
                           _death_rings=[{"radius":10.,"life":1.}],
                           _muzzle_flashes=[{"timer":0.08}],
                           _psi_waves=[{"radius":8.,"life":1.,"delay":0.08,"active":False}],
                           _shake_intensity=10.,_intro_active=False,cover_nodes=[])


@pytest.mark.parametrize("steps", [1,3,6,24,100])
def test_same_elapsed_time_gives_same_motion_fades_shake_and_delayed_wave(steps):
    state = effects_state()
    for _ in range(steps):
        BattleView.on_update(state,0.1/steps)
    assert state.attack_timer == pytest.approx(0.2)
    assert state._flash_alpha == pytest.approx(112)
    assert state.particles[0]["life"] == pytest.approx(0.58)
    assert state.particles[0]["x"] == pytest.approx(6)
    assert state.particles[0]["y"] == pytest.approx(8.5)
    assert state._shake_intensity == pytest.approx(10*0.72**6)
    assert state._psi_waves[0]["radius"] == pytest.approx(11.2)
    assert state._psi_waves[0]["life"] == pytest.approx(0.97)


@pytest.mark.parametrize("fps", [30,60,240,1000])
def test_complete_effect_lifecycle_clears_every_transient_at_all_frame_rates(fps):
    state = effects_state()
    for _ in range(int(2.5*fps)):
        BattleView.on_update(state,1/fps)
    assert state.attack_timer == 0 and state.attack_line is None
    assert state._flash_alpha == state._aftermath_timer == state._shake_intensity == 0
    assert not any((state.damage_popups,state.particles,state._unit_flashes,
                    state._death_rings,state._muzzle_flashes,state._psi_waves))
