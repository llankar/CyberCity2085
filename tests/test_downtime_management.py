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


def _treatment(key):
    return next(activity for activity in DOWNTIME_ACTIVITIES if activity.key == key)


def test_rest_heals_quarter_max_hp_without_resource_cost_or_overheal():
    gs = GameState(characters=[Character("Injured")])
    agent = gs.characters[0]
    agent.stats.hp = 1
    agent.recovery_turns = 3
    gs.strategic_resources["credits"] = 0
    day = gs.calendar.current_day
    apply_activity(gs, _treatment("rest"), [agent])
    assert agent.stats.hp == 4  # ceil(11 * .25) == 3.
    assert gs.strategic_resources["credits"] == 0 and gs.calendar.current_day == day + 1
    assert agent.recovery_turns == 2  # Only the existing daily recovery tick.
    agent.stats.hp = agent.stats.max_hp - 1
    apply_activity(gs, _treatment("rest"), [agent])
    assert agent.stats.hp == agent.stats.max_hp


def test_hospital_fully_heals_living_patient_for_declared_cost():
    gs = GameState(characters=[Character("Patient"), Character("Other")])
    patient, other = gs.characters
    patient.stats.hp = 1
    other.stats.hp = 1
    gs.strategic_resources["credits"] = 20
    apply_activity(gs, _treatment("hospital"), [patient])
    assert patient.stats.hp == patient.stats.max_hp and other.stats.hp == 1
    assert gs.strategic_resources["credits"] == 12


def test_treatments_do_not_revive_or_charge_for_invalid_or_full_patient():
    gs = GameState(characters=[Character("Patient")])
    patient = gs.characters[0]
    gs.strategic_resources["credits"] = 20
    day = gs.calendar.current_day
    patient.stats.hp = 0
    assert "living injured" in apply_activity(gs, _treatment("hospital"), [patient])
    patient.stats.hp = patient.stats.max_hp
    assert "living injured" in apply_activity(gs, _treatment("rest"), [patient])
    patient.stats.hp = 1
    patient.starver_transformed = True
    assert "living injured" in apply_activity(gs, _treatment("hospital"), [patient])
    assert gs.strategic_resources["credits"] == 20 and gs.calendar.current_day == day


def test_hospital_without_credits_preserves_hp_and_day():
    gs = GameState(characters=[Character("Patient")])
    patient = gs.characters[0]
    patient.stats.hp = 1
    gs.strategic_resources["credits"] = 7
    day = gs.calendar.current_day
    assert "Not enough credits" in apply_activity(gs, _treatment("hospital"), [patient])
    assert (
        patient.stats.hp == 1
        and gs.calendar.current_day == day
        and gs.strategic_resources["credits"] == 7
    )
