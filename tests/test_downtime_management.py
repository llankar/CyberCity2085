from game.character import Character
from game.gamestate import GameState
from game.management.downtime import DOWNTIME_ACTIVITIES, apply_activity


def test_downtime_consumes_day_resource_and_updates_agent_state():
    gs = GameState(characters=[Character(name="Nova")])
    gs.selected_agent_names = ["Nova"]
    gs.strategic_resources["credits"] = 20
    activity = DOWNTIME_ACTIVITIES[0]

    before_day = gs.calendar.current_day
    result = apply_activity(gs, activity, gs.characters)

    assert "Downtime" in result
    assert gs.calendar.current_day == before_day + 1
    assert gs.strategic_resources["credits"] == 12
    assert gs.characters[0].stress == 0
    assert gs.characters[0].loyalty == 10
    assert "grounded" in gs.characters[0].traits


def test_downtime_blocks_when_resource_missing():
    gs = GameState(characters=[Character(name="Iris")])
    gs.strategic_resources["influence"] = 0

    msg = apply_activity(gs, DOWNTIME_ACTIVITIES[2], gs.characters)

    assert "Not enough influence" in msg
