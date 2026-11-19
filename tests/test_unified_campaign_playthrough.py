"""The natural-play harness uses production campaign inputs, never result overrides."""
from pathlib import Path
import re
import pytest
from tools.check_unified_return import campaign_scenario

ROOT=Path(__file__).resolve().parents[1]


def test_scenario_uses_actual_generated_board_and_starter_equipment():
    state,mission=campaign_scenario()
    assert mission is state.mission_templates[state.selected_mission_index]
    assert len(state.characters)==5 and len(state.selected_agent_names)==5
    assert all(c.loadout.primary_weapon is not None for c in state.characters)
    assert all(c.stats.level==1 and c.stats.hp==c.stats.max_hp for c in state.characters)
    assert mission.id not in {'unified_victory','unified_defeat','unified_retreat'}


def test_missing_board_mission_is_an_explicit_error():
    with pytest.raises(ValueError,match='absent'):campaign_scenario('not-on-board')


def test_natural_driver_has_no_terminal_outcome_or_tactical_stat_override():
    for name in ['campaign_playthrough.gd','campaign_agent.gd','persistent_runtime_playthrough.gd']:
        source=(ROOT/'godot/combat_missions_ui/tests'/name).read_text()
        assert '_end_combat(' not in source and '_complete_mission(' not in source
        assert not re.search(r'\.(hp|ap|position|objective_completed|turn_number)\s*=',source)
