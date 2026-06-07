extends Control

const PANEL := Color(0.02, 0.05, 0.08, 0.94)
const NEON := Color(0.1, 0.95, 0.72, 1.0)
const TEXT := Color(0.84, 0.95, 0.92, 1.0)
const WARN := Color(1.0, 0.72, 0.22, 1.0)

var handoff: Dictionary = {}
var handoff_path := "runtime/godot_combat/mission_handoff.json"
var status_line := "Waiting for CyberCity handoff."
var battle_started: bool = false
var intro_elapsed: float = 0.0
var intro_autostart_delay: float = 0.35
var selected_action: String = ""
var combat_log: Array[String] = []
var action_rects: Dictionary = {}
var deploy_rect: Rect2 = Rect2()
var enemy_contacts: int = 0

func _ready() -> void:
    set_process(true)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _read_args()
    _load_handoff()
    _seed_combat_state()
    call_deferred("_start_combat", "AUTO-DEPLOY")
    queue_redraw()

func _process(delta: float) -> void:
    if battle_started:
        return
    intro_elapsed += delta
    if intro_elapsed >= intro_autostart_delay:
        _start_combat("AUTO-DEPLOY")

func _read_args() -> void:
    var args: PackedStringArray = OS.get_cmdline_user_args()
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
    print(status_line)

func _seed_combat_state() -> void:
    var mission: Dictionary = _mission_data()
    var contacts_value: Variant = mission.get("starting_enemy_count", 0)
    enemy_contacts = int(contacts_value)
    combat_log = []
    selected_action = ""
    battle_started = false
    intro_elapsed = 0.0
    action_rects = {}
    deploy_rect = Rect2()
    if enemy_contacts > 0:
        combat_log.append("Enemy contacts detected: %d." % enemy_contacts)
    combat_log.append("Press Enter or click DEPLOY to begin.")

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, size), Color(0.005, 0.015, 0.025, 1.0), true)
    _draw_panel(Rect2(42, 36, size.x - 84, size.y - 72))
    if battle_started:
        _draw_combat_scene()
    else:
        _draw_handoff_scene()
    _draw_text(status_line, Vector2(74, size.y - 74), 15, NEON)

func _draw_handoff_scene() -> void:
    var mission: Dictionary = _mission_data()
    var campaign: Dictionary = _campaign_data()
    var map_data: Dictionary = _map_data()
    _draw_text("CYBERCITY 2085 // GODOT COMBAT UI", Vector2(72, 82), 26, NEON)
    _draw_text(str(mission.get("title", "TACTICAL INSERTION")).to_upper(), Vector2(72, 126), 34, TEXT)
    _draw_text("%s • Risk %s • %s" % [mission.get("target_faction", "Unknown faction"), mission.get("risk_level", "?"), map_data.get("label", "unmapped site")], Vector2(74, 166), 18, WARN)
    _draw_text(str(mission.get("objective_text", "Complete the objective.")), Vector2(74, 208), 20, TEXT)
    _draw_text("Campaign shell: %s / %s" % [campaign.get("corp_name", "AEGIS"), campaign.get("city_name", "Neo-Chrome City")], Vector2(74, 246), 16, TEXT)
    _draw_squad(Vector2(74, 308))
    _draw_actions(Vector2(size.x - 410, 308), false)
    _draw_deploy_prompt()

func _draw_combat_scene() -> void:
    var mission: Dictionary = _mission_data()
    var campaign: Dictionary = _campaign_data()
    _draw_text("TACTICAL INSERTION ACTIVE", Vector2(72, 82), 26, NEON)
    _draw_text(str(mission.get("title", "TACTICAL INSERTION")).to_upper(), Vector2(72, 126), 34, TEXT)
    _draw_text("Objective live: %s" % str(mission.get("objective_text", "Complete the objective.")), Vector2(74, 166), 18, WARN)
    _draw_text("Campaign shell: %s / %s" % [campaign.get("corp_name", "AEGIS"), campaign.get("city_name", "Neo-Chrome City")], Vector2(74, 204), 16, TEXT)
    _draw_battlefield(Rect2(70, 242, size.x - 560, 330))
    _draw_squad(Vector2(74, 308))
    _draw_actions(Vector2(size.x - 410, 308), true)
    _draw_combat_log(Vector2(74, size.y - 210))

func _draw_panel(rect: Rect2) -> void:
    draw_rect(rect, PANEL, true)
    draw_rect(rect, NEON, false, 2.0)

func _draw_deploy_prompt() -> void:
    var rect := Rect2(72, size.y - 166, 260, 44)
    deploy_rect = rect
    draw_rect(rect, Color(0.04, 0.22, 0.17, 0.95), true)
    draw_rect(rect, NEON, false, 1.5)
    _draw_text("DEPLOY  [Enter]", rect.position + Vector2(16, 28), 16, TEXT)
    _draw_text("Click to begin combat.", Vector2(74, size.y - 116), 14, WARN)

func _draw_battlefield(rect: Rect2) -> void:
    draw_rect(rect, Color(0.03, 0.08, 0.1, 0.95), true)
    draw_rect(rect, NEON, false, 1.0)
    var cols: int = 10
    var rows: int = 5
    var cell_w: float = rect.size.x / float(cols)
    var cell_h: float = rect.size.y / float(rows)
    for x in range(cols + 1):
        var px: float = rect.position.x + float(x) * cell_w
        draw_line(Vector2(px, rect.position.y), Vector2(px, rect.position.y + rect.size.y), Color(0.12, 0.45, 0.38, 0.45), 1.0)
    for y in range(rows + 1):
        var py: float = rect.position.y + float(y) * cell_h
        draw_line(Vector2(rect.position.x, py), Vector2(rect.position.x + rect.size.x, py), Color(0.12, 0.45, 0.38, 0.45), 1.0)
    _draw_text("Tactical grid online", rect.position + Vector2(12, 26), 14, WARN)
    var contacts_to_draw: int = maxi(enemy_contacts, 0)
    for index in range(min(contacts_to_draw, 6)):
        var enemy_x: float = rect.position.x + rect.size.x - 90.0 - float(index % 3) * 24.0
        var enemy_y: float = rect.position.y + 70.0 + float(index / 3) * 40.0
        draw_rect(Rect2(enemy_x, enemy_y, 18, 18), Color(0.78, 0.18, 0.18, 0.95), true)
        draw_rect(Rect2(enemy_x, enemy_y, 18, 18), WARN, false, 1.0)

func _draw_combat_log(origin: Vector2) -> void:
    _draw_text("COMBAT LOG", origin, 16, NEON)
    var line_y: float = origin.y + 28.0
    for index in range(combat_log.size()):
        _draw_text(str(combat_log[index]), Vector2(origin.x, line_y), 14, TEXT)
        line_y += 24.0
        if index >= 4:
            break

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

func _draw_actions(origin: Vector2, active: bool) -> void:
    _draw_text("TACTICAL DECK", origin, 20, NEON)
    var combat_ui: Dictionary = _combat_ui_data()
    var actions: Array = combat_ui.get("primary_actions", [])
    action_rects = {}
    for index in range(actions.size()):
        var action_name: String = str(actions[index]).to_upper()
        var rect := Rect2(origin.x, origin.y + 36 + index * 42, 290, 30)
        action_rects[action_name] = rect
        var fill_col := Color(0.03, 0.14, 0.12, 0.86)
        var border_col := NEON
        if not active:
            fill_col = Color(0.03, 0.08, 0.08, 0.6)
            border_col = Color(0.25, 0.7, 0.62, 0.5)
        elif selected_action == action_name:
            fill_col = Color(0.06, 0.22, 0.16, 0.95)
            border_col = WARN
        draw_rect(rect, fill_col, true)
        draw_rect(rect, border_col, false, 1.0)
        _draw_text(action_name, rect.position + Vector2(12, 21), 15, TEXT)

func _draw_text(text: String, pos: Vector2, font_size: int, color: Color) -> void:
    draw_string(ThemeDB.fallback_font, pos, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)

func _gui_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        var key_event := event as InputEventKey
        if key_event.keycode == KEY_ESCAPE:
            get_tree().quit()
            accept_event()
            return
        if key_event.keycode == KEY_ENTER or key_event.keycode == KEY_KP_ENTER:
            if not battle_started:
                _start_combat("ENTER")
            else:
                _execute_action("MOVE")
            accept_event()
            return
        if key_event.keycode == KEY_SPACE and battle_started:
            _execute_action("FIRE")
            accept_event()
            return

    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        var mouse_event := event as InputEventMouseButton
        var point := mouse_event.position
        if not battle_started and deploy_rect.has_point(point):
            _start_combat("DEPLOY")
            accept_event()
            return
        for action_key in action_rects.keys():
            var rect: Rect2 = action_rects.get(action_key, Rect2()) as Rect2
            if rect.has_point(point):
                if not battle_started:
                    _start_combat(str(action_key))
                _execute_action(str(action_key))
                accept_event()
                return

func _start_combat(source: String) -> void:
    if battle_started:
        return
    battle_started = true
    status_line = "Combat live. Click an action or press Space / Enter."
    combat_log.append("%s: tactical insertion live." % source)
    print(status_line)
    queue_redraw()

func _execute_action(action_name: String) -> void:
    if not battle_started:
        _start_combat(action_name)
    selected_action = action_name
    var mission: Dictionary = _mission_data()
    var squad_name: String = _lead_agent_name()
    var line := ""
    match action_name:
        "MOVE":
            line = "%s advances toward the objective." % squad_name
        "MELEE":
            line = "%s clears a close-quarters lane." % squad_name
        "FIRE":
            if enemy_contacts > 0:
                enemy_contacts -= 1
            line = "%s fires. Enemy contacts now %d." % [squad_name, enemy_contacts]
        "PSI":
            line = "%s pulses the tactical feed." % squad_name
        "DEFEND":
            line = "%s takes a defensive stance." % squad_name
        "OVERWATCH":
            line = "%s covers the corridor." % squad_name
        _:
            line = "%s selects %s." % [squad_name, action_name]
    combat_log.append(line)
    if combat_log.size() > 6:
        combat_log.remove_at(0)
    if enemy_contacts <= 0 and int(mission.get("starting_enemy_count", 0)) > 0:
        status_line = "Extraction corridor clear. Objective complete."
    else:
        status_line = "Combat live. Click an action or press Space / Enter."
    print(line)
    queue_redraw()

func _lead_agent_name() -> String:
    var squad: Array = handoff.get("squad", [])
    if squad.is_empty():
        return "Agent"
    var first: Variant = squad[0]
    if typeof(first) != TYPE_DICTIONARY:
        return "Agent"
    var agent: Dictionary = first as Dictionary
    return str(agent.get("name", "Agent"))

func _mission_data() -> Dictionary:
    var raw: Variant = handoff.get("mission", {})
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}

func _campaign_data() -> Dictionary:
    var raw: Variant = handoff.get("campaign", {})
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}

func _map_data() -> Dictionary:
    var raw: Variant = handoff.get("map", {})
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}

func _combat_ui_data() -> Dictionary:
    var raw: Variant = handoff.get("combat_ui", {})
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}
