extends Control

const PANEL := Color(0.02, 0.05, 0.08, 0.94)
const NEON := Color(0.1, 0.95, 0.72, 1.0)
const TEXT := Color(0.84, 0.95, 0.92, 1.0)
const WARN := Color(1.0, 0.72, 0.22, 1.0)

var handoff: Dictionary = {}
var handoff_path := "runtime/godot_combat/mission_handoff.json"
var status_line := "Waiting for CyberCity handoff."

func _ready() -> void:
    _read_args()
    _load_handoff()
    queue_redraw()

func _read_args() -> void:
    var args := OS.get_cmdline_user_args()
    for index in range(args.size()):
        if args[index] == "--handoff" and index + 1 < args.size():
            handoff_path = args[index + 1]

func _load_handoff() -> void:
    if not FileAccess.file_exists(handoff_path):
        status_line = "No handoff JSON found at %s" % handoff_path
        return
    var text := FileAccess.get_file_as_string(handoff_path)
    var parsed = JSON.parse_string(text)
    if typeof(parsed) != TYPE_DICTIONARY:
        status_line = "Handoff JSON is unreadable."
        return
    handoff = parsed
    status_line = "Godot combat UI loaded %s" % handoff_path

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, size), Color(0.005, 0.015, 0.025, 1.0), true)
    _draw_panel(Rect2(42, 36, size.x - 84, size.y - 72))
    var mission: Dictionary = handoff.get("mission", {}) as Dictionary
    var campaign: Dictionary = handoff.get("campaign", {}) as Dictionary
    var map_data: Dictionary = handoff.get("map", {}) as Dictionary
    _draw_text("CYBERCITY 2085 // GODOT COMBAT UI", Vector2(72, 82), 26, NEON)
    _draw_text(str(mission.get("title", "TACTICAL INSERTION")).to_upper(), Vector2(72, 126), 34, TEXT)
    _draw_text("%s • Risk %s • %s" % [mission.get("target_faction", "Unknown faction"), mission.get("risk_level", "?"), map_data.get("label", "unmapped site")], Vector2(74, 166), 18, WARN)
    _draw_text(str(mission.get("objective_text", "Complete the objective.")), Vector2(74, 208), 20, TEXT)
    _draw_text("Campaign shell: %s / %s" % [campaign.get("corp_name", "AEGIS"), campaign.get("city_name", "Neo-Chrome City")], Vector2(74, 246), 16, TEXT)
    _draw_squad(Vector2(74, 308))
    _draw_actions(Vector2(size.x - 410, 308))
    _draw_text(status_line, Vector2(74, size.y - 74), 15, NEON)

func _draw_panel(rect: Rect2) -> void:
    draw_rect(rect, PANEL, true)
    draw_rect(rect, NEON, false, 2.0)

func _draw_squad(origin: Vector2) -> void:
    _draw_text("DEPLOYED AGENTS", origin, 20, NEON)
    var squad: Array = handoff.get("squad", [])
    if squad.is_empty():
        _draw_text("No selected agents in handoff.", origin + Vector2(0, 38), 16, WARN)
        return
    for index in range(min(squad.size(), 6)):
        var agent: Dictionary = squad[index]
        var y := origin.y + 42 + index * 48
        _draw_text("%s  [%s]  HP %s/%s  Stress %s" % [agent.get("name", "Agent"), agent.get("role", "unit"), agent.get("hp", 0), agent.get("max_hp", 0), agent.get("stress", 0)], Vector2(origin.x, y), 17, TEXT)

func _draw_actions(origin: Vector2) -> void:
    _draw_text("TACTICAL DECK", origin, 20, NEON)
    var actions: Array = handoff.get("combat_ui", {}).get("primary_actions", [])
    for index in range(actions.size()):
        var rect := Rect2(origin.x, origin.y + 36 + index * 42, 290, 30)
        draw_rect(rect, Color(0.03, 0.14, 0.12, 0.86), true)
        draw_rect(rect, NEON, false, 1.0)
        _draw_text(str(actions[index]).to_upper(), rect.position + Vector2(12, 21), 15, TEXT)

func _draw_text(text: String, pos: Vector2, font_size: int, color: Color) -> void:
    draw_string(ThemeDB.fallback_font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)
