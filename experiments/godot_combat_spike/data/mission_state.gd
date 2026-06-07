extends Resource
class_name SpikeMissionState

const GRID_WIDTH := 8
const GRID_HEIGHT := 6
const DEFAULT_MISSION_ID := "godot_combat_spike_01"

var mission_id: String = DEFAULT_MISSION_ID
var turn: String = "player"
var turn_number: int = 1
var result: String = "in_progress"
var units: Array[Dictionary] = []
var event_log: Array[String] = []

static func default_state() -> SpikeMissionState:
	var state := SpikeMissionState.new()
	state.units = [
		{"id": "agent_echo", "team": "agent", "role": "samurai", "hp": 11, "max_hp": 11, "ap": 2, "position": {"x": 1, "y": 2}},
		{"id": "agent_vesper", "team": "agent", "role": "sniper", "hp": 11, "max_hp": 11, "ap": 2, "position": {"x": 1, "y": 3}},
		{"id": "enemy_raider_a", "team": "enemy", "role": "grunt", "hp": 10, "max_hp": 10, "ap": 2, "position": {"x": 5, "y": 2}},
		{"id": "enemy_raider_b", "team": "enemy", "role": "grunt", "hp": 10, "max_hp": 10, "ap": 2, "position": {"x": 5, "y": 3}},
	]
	state.event_log = ["Spike mission loaded outside the Arcade runtime."]
	return state

static func from_json_text(json_text: String) -> SpikeMissionState:
	var parsed = JSON.parse_string(json_text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return SpikeMissionState.default_state()
	var state := SpikeMissionState.new()
	state.mission_id = str(parsed.get("mission_id", DEFAULT_MISSION_ID))
	state.turn = str(parsed.get("turn", "player"))
	state.turn_number = int(parsed.get("turn_number", 1))
	state.result = str(parsed.get("result", "in_progress"))
	state.units = parsed.get("units", [])
	state.event_log = parsed.get("event_log", [])
	return state

func to_dictionary() -> Dictionary:
	return {
		"mission_id": mission_id,
		"turn": turn,
		"turn_number": turn_number,
		"result": result,
		"units": units,
		"event_log": event_log,
	}

func to_json_text() -> String:
	return JSON.stringify(to_dictionary(), "  ")

func living_units(team: String) -> Array[Dictionary]:
	return units.filter(func(unit): return unit.get("team", "") == team and int(unit.get("hp", 0)) > 0)
