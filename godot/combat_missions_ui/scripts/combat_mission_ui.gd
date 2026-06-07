extends Control

const PANEL := Color(0.02, 0.05, 0.08, 0.94)
const NEON := Color(0.1, 0.95, 0.72, 1.0)
const TEXT := Color(0.84, 0.95, 0.92, 1.0)
const WARN := Color(1.0, 0.72, 0.22, 1.0)
const PLAYER_COL := Color(0.1, 0.95, 0.72, 1.0)
const ENEMY_COL := Color(1.0, 0.34, 0.30, 1.0)
const ROLE_SNIPER := Color(0.56, 0.88, 1.0, 1.0)
const ROLE_PSI := Color(0.76, 0.56, 1.0, 1.0)
const ROLE_SAMURAI := Color(0.28, 1.0, 0.74, 1.0)
const ACTIONS: Array[String] = ["MOVE", "MELEE", "FIRE", "PSI", "DEFEND", "OVERWATCH", "END TURN"]
const GRID_COLS := 12
const GRID_ROWS := 8

var handoff: Dictionary = {}
var handoff_path := "runtime/godot_combat/mission_handoff.json"
var status_line := "Waiting for CyberCity handoff."
var battle_started: bool = false
var intro_elapsed: float = 0.0
var intro_autostart_delay: float = 0.35
var elapsed_time: float = 0.0
var selected_action: String = ""
var pending_end_turn_confirmation: bool = false
var show_combat_log: bool = false
var turn_side: String = "player"
var turn_number: int = 1
var active_player_index: int = 0
var selected_target_index: int = 0
var enemy_turn_timer: float = 0.0
var enemy_turn_duration: float = 0.75
var combat_log: Array[String] = []
var action_rects: Dictionary = {}
var deploy_rect: Rect2 = Rect2()
var enemy_contacts: int = 0
var battlefield_rect: Rect2 = Rect2()
var objective_cell: Vector2i = Vector2i(6, 3)
var player_units: Array[Dictionary] = []
var enemy_units: Array[Dictionary] = []
var initiative_entries: Array[Dictionary] = []

func _ready() -> void:
    set_process(true)
    mouse_filter = Control.MOUSE_FILTER_STOP
    _read_args()
    _load_handoff()
    _seed_combat_state()
    call_deferred("_start_combat", "AUTO-DEPLOY")
    queue_redraw()

func _process(delta: float) -> void:
    if not battle_started:
        return
    elapsed_time += delta
    if turn_side == "enemy":
        enemy_turn_timer = max(0.0, enemy_turn_timer - delta)
        if enemy_turn_timer <= 0.0:
            _resolve_enemy_turn()

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
    player_units = _build_player_units()
    enemy_units = _build_enemy_units()
    enemy_contacts = enemy_units.size()
    objective_cell = Vector2i(6, 3)
    combat_log = []
    selected_action = "MOVE"
    pending_end_turn_confirmation = false
    show_combat_log = false
    turn_side = "player"
    turn_number = 1
    active_player_index = 0
    selected_target_index = 0
    enemy_turn_timer = 0.0
    elapsed_time = 0.0
    battle_started = false
    intro_elapsed = 0.0
    action_rects = {}
    deploy_rect = Rect2()
    initiative_entries = []
    _refresh_initiative()
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

func _draw_panel(rect: Rect2) -> void:
    draw_rect(rect, PANEL, true)
    draw_rect(rect, NEON, false, 2.0)

func _draw_combat_scene() -> void:
    _layout_combat_hud()
    _draw_combat_background()
    _draw_mission_header()
    _draw_top_chrome()
    _draw_battlefield()
    _draw_objective_marker()
    _draw_units()
    _draw_phase_banner()
    _draw_initiative_timeline()
    _draw_unit_status_panel()
    _draw_portrait_strip()
    _draw_action_bar()
    if show_combat_log:
        _draw_combat_log_panel()
    elif selected_action in ["FIRE", "MELEE", "PSI"]:
        _draw_target_lock_panel()
    _draw_text(status_line, Vector2(74, 268), 14, NEON)

func _layout_combat_hud() -> void:
    battlefield_rect = Rect2(70, 286, max(360, size.x - 480), max(180, size.y - 510))

func _draw_combat_background() -> void:
    draw_rect(Rect2(Vector2.ZERO, size), Color(0.005, 0.015, 0.025, 1.0), true)
    draw_rect(Rect2(42, 36, size.x - 84, size.y - 72), Color(0.01, 0.03, 0.05, 0.94), true)
    draw_rect(Rect2(42, 36, size.x - 84, size.y - 72), NEON, false, 2.0)

func _draw_mission_header() -> void:
    var mission: Dictionary = _mission_data()
    var campaign: Dictionary = _campaign_data()
    var map_data: Dictionary = _map_data()
    _draw_text("CYBERCITY 2085 // GODOT COMBAT UI", Vector2(72, 82), 26, NEON)
    _draw_text(str(mission.get("title", "TACTICAL INSERTION")).to_upper(), Vector2(72, 126), 34, TEXT)
    _draw_text("%s • Risk %s • %s" % [mission.get("target_faction", "Unknown faction"), mission.get("risk_level", "?"), map_data.get("label", "unmapped site")], Vector2(74, 166), 18, WARN)
    _draw_text(str(mission.get("objective_text", "Complete the objective.")), Vector2(74, 208), 20, TEXT)
    _draw_text("Campaign shell: %s / %s" % [campaign.get("corp_name", "AEGIS"), campaign.get("city_name", "Neo-Chrome City")], Vector2(74, 246), 16, TEXT)

func _draw_top_chrome() -> void:
    var mission: Dictionary = _mission_data()
    var player_count := 0
    for unit in player_units:
        if int(unit.get("hp", 0)) > 0:
            player_count += 1
    var enemy_count := 0
    for unit in enemy_units:
        if int(unit.get("hp", 0)) > 0:
            enemy_count += 1
    var bh := 38
    draw_rect(Rect2(0, size.y - bh, size.x, bh), Color(0, 0, 0, 0.78), true)
    draw_line(Vector2(0, size.y - bh), Vector2(size.x, size.y - bh), Color(0.18, 0.92, 0.72, 1.0), 2.0)
    _draw_text_centered(mission.get("title", "MISSION").to_upper(), Vector2(size.x * 0.5, size.y - bh + 19), 13, TEXT, 280.0)
    _draw_text("SQUAD %d" % player_count, Vector2(size.x * 0.5 - 280, size.y - bh + 19), 12, PLAYER_COL)
    _draw_text("ENEMIES %d" % enemy_count, Vector2(size.x * 0.5 + 170, size.y - bh + 19), 12, ENEMY_COL)
    _draw_text_centered("TURN %02d" % turn_number, Vector2(size.x - 72, size.y - bh + 19), 12, TEXT, 72.0)

func _draw_battlefield() -> void:
    draw_rect(battlefield_rect, Color(0.03, 0.08, 0.1, 0.95), true)
    draw_rect(battlefield_rect, NEON, false, 1.0)
    var cols: int = GRID_COLS
    var rows: int = GRID_ROWS
    var cell_w: float = battlefield_rect.size.x / float(cols)
    var cell_h: float = battlefield_rect.size.y / float(rows)
    for x in range(cols + 1):
        var px: float = battlefield_rect.position.x + float(x) * cell_w
        draw_line(Vector2(px, battlefield_rect.position.y), Vector2(px, battlefield_rect.position.y + battlefield_rect.size.y), Color(0.12, 0.45, 0.38, 0.45), 1.0)
    for y in range(rows + 1):
        var py: float = battlefield_rect.position.y + float(y) * cell_h
        draw_line(Vector2(battlefield_rect.position.x, py), Vector2(battlefield_rect.position.x + battlefield_rect.size.x, py), Color(0.12, 0.45, 0.38, 0.45), 1.0)
    _draw_text("TACTICAL GRID ONLINE", battlefield_rect.position + Vector2(12, 26), 14, WARN)

func _draw_objective_marker() -> void:
    var center := _cell_center(objective_cell)
    var pulse := 0.7 + 0.3 * sin(elapsed_time * 2.2)
    var col := PLAYER_COL
    var ring := 22.0 + 6.0 * pulse
    draw_arc(center, ring, 0.0, TAU, 48, col, 2.0)
    draw_rect(Rect2(center.x - 10, center.y - 10, 20, 20), Color(col.r, col.g, col.b, 0.24), true)
    draw_rect(Rect2(center.x - 12, center.y - 12, 24, 24), col, false, 2.0)
    _draw_text("OBJECTIVE", center + Vector2(-20, -28), 9, col)

func _draw_units() -> void:
    var cell_w: float = battlefield_rect.size.x / float(GRID_COLS)
    var cell_h: float = battlefield_rect.size.y / float(GRID_ROWS)
    if selected_action == "MOVE" and turn_side == "player":
        var active: Dictionary = _current_active_player()
        if not active.is_empty():
            var budget: int = max(1, int(active.get("ap", 2)))
            var origin: Vector2i = _cell_position(active)
            for dx in range(-budget, budget + 1):
                for dy in range(-budget, budget + 1):
                    if abs(dx) + abs(dy) > budget:
                        continue
                    var cell := Vector2i(origin.x + dx, origin.y + dy)
                    if cell.x < 0 or cell.y < 0 or cell.x >= GRID_COLS or cell.y >= GRID_ROWS:
                        continue
                    var rect := Rect2(
                        battlefield_rect.position.x + float(cell.x) * cell_w,
                        battlefield_rect.position.y + float(cell.y) * cell_h,
                        cell_w,
                        cell_h,
                    )
                    draw_rect(rect, Color(0.18, 0.82, 0.62, 0.16), true)

    for i in range(player_units.size()):
        var unit: Dictionary = player_units[i]
        _draw_unit_token(unit, false, i == active_player_index and turn_side == "player")
    for j in range(enemy_units.size()):
        var enemy: Dictionary = enemy_units[j]
        _draw_unit_token(enemy, true, false)

func _draw_unit_token(unit: Dictionary, is_enemy: bool, is_active: bool) -> void:
    if int(unit.get("hp", 0)) <= 0:
        return
    var center: Vector2 = _unit_center(unit)
    var role: String = str(unit.get("role", "agent")).to_lower()
    var role_col: Color = ROLE_SAMURAI
    if role == "sniper":
        role_col = ROLE_SNIPER
    elif role == "psi":
        role_col = ROLE_PSI
    var fill: Color = Color(0.08, 0.18, 0.24, 0.95) if not is_enemy else Color(0.22, 0.08, 0.08, 0.95)
    var border: Color = role_col if not is_enemy else ENEMY_COL
    var size: float = 28.0 if not is_enemy else 26.0
    draw_rect(Rect2(center.x - size * 0.5, center.y - size * 0.5, size, size), fill, true)
    draw_rect(Rect2(center.x - size * 0.5, center.y - size * 0.5, size, size), border, false, 2.0)
    if is_active:
        draw_arc(center, size * 0.7, 0.0, TAU, 64, PLAYER_COL, 2.0)
    elif selected_action in ["FIRE", "MELEE", "PSI"] and is_enemy and unit == _current_target():
        draw_arc(center, size * 0.75, 0.0, TAU, 64, WARN, 2.0)
    var name: String = str(unit.get("name", "Agent")).to_upper()
    _draw_text(name, Vector2(center.x, center.y - size * 0.9), 9, TEXT if not is_enemy else WARN)
    var hp: int = int(unit.get("hp", 0))
    var max_hp: int = max(1, int(unit.get("max_hp", 1)))
    var hp_frac: float = clamp(float(hp) / float(max_hp), 0.0, 1.0)
    var hp_col: Color = PLAYER_COL if hp_frac > 0.5 else (WARN if hp_frac > 0.25 else ENEMY_COL)
    var bar_w: float = 40.0
    draw_rect(Rect2(center.x - bar_w * 0.5, center.y + size * 0.65, bar_w, 5), Color(0.05, 0.11, 0.14, 0.9), true)
    draw_rect(Rect2(center.x - bar_w * 0.5, center.y + size * 0.65, bar_w * hp_frac, 5), hp_col, true)
    if int(unit.get("stress", 0)) >= 70:
        _draw_text("SUP", Vector2(center.x - 8, center.y - size * 1.05), 8, WARN)

func _draw_phase_banner() -> void:
    var label: String = "PLAYER TURN"
    var col: Color = PLAYER_COL
    if turn_side == "enemy":
        label = "ENEMY TURN"
        col = ENEMY_COL
    elif turn_side == "ended":
        label = "MISSION COMPLETE"
        col = TEXT
    var pill_w := 230.0
    var pill_h := 32.0
    var px := size.x - pill_w - 12.0
    var py := 72.0
    draw_rect(Rect2(px, py, pill_w, pill_h), Color(0, 0, 0, 0.75), true)
    draw_line(Vector2(px, py + pill_h), Vector2(px + pill_w, py + pill_h), col, 2.0)
    _draw_text_centered(label, Vector2(px + pill_w * 0.5, py + 18.0), 13, col, pill_w - 16.0)

func _draw_initiative_timeline() -> void:
    if initiative_entries.is_empty():
        return
    var panel_w: float = 320.0
    var panel_h: float = 34.0 + 30.0 * float(initiative_entries.size())
    var left: float = size.x - panel_w - 14.0
    var top: float = 118.0
    draw_rect(Rect2(left, top, panel_w, panel_h), Color(0, 0, 0, 0.75), true)
    draw_line(Vector2(left, top), Vector2(left + panel_w, top), NEON, 2.0)
    _draw_text("INITIATIVE", Vector2(left + 10, top + 16), 10, TEXT)
    for i in range(initiative_entries.size()):
        var entry: Dictionary = initiative_entries[i]
        var row_y: float = top + 34.0 + float(i) * 30.0
        if bool(entry.get("is_active", false)):
            draw_rect(Rect2(left + 8.0, row_y - 20.0, panel_w - 16.0, 26.0), Color(0.18, 0.82, 0.62, 0.18), true)
        var marker := "●" if bool(entry.get("is_active", false)) else "○"
        var color := ENEMY_COL if bool(entry.get("is_enemy", false)) else PLAYER_COL
        _draw_text(marker, Vector2(left + 14, row_y - 6.0), 11, color)
        _draw_text(str(entry.get("label", "UNIT")), Vector2(left + 34, row_y - 6.0), 10, TEXT)
        var threat := str(entry.get("threat", ""))
        if threat != "":
            _draw_text("THREAT", Vector2(left + panel_w - 66.0, row_y - 6.0), 8, WARN)

func _draw_unit_status_panel() -> void:
    var unit: Dictionary = _current_active_player()
    var pw: float = 320.0
    var ph: float = 90.0
    var px: float = 12.0
    var py: float = size.y - ph - 12.0
    var turn_col: Color = PLAYER_COL if turn_side == "player" else (ENEMY_COL if turn_side == "enemy" else TEXT)
    draw_rect(Rect2(px, py, pw, ph), Color(0, 0, 0, 0.8), true)
    draw_line(Vector2(px, py + ph), Vector2(px + pw, py + ph), turn_col, 2.0)
    if unit.is_empty():
        _draw_text("NO ACTIVE UNIT", Vector2(px + pw * 0.5, py + ph * 0.5), 12, TEXT)
        return
    var name := str(unit.get("name", "Agent")).to_upper()
    var role := str(unit.get("role", "agent")).to_upper()
    _draw_text(name, Vector2(px + 110, py + 16), 13, TEXT)
    _draw_text(role, Vector2(px + 110, py + 32), 10, turn_col)
    _draw_text("HP %d/%d" % [int(unit.get("hp", 0)), int(unit.get("max_hp", 1))], Vector2(px + 110, py + 50), 10, TEXT)
    _draw_text("AP %d" % int(unit.get("ap", 0)), Vector2(px + 110, py + 68), 10, TEXT)
    _draw_text("STRESS %d" % int(unit.get("stress", 0)), Vector2(px + 210, py + 68), 10, WARN if int(unit.get("stress", 0)) >= 70 else TEXT)
    draw_rect(Rect2(px + 10, py + 12, 82, 62), Color(0.06, 0.14, 0.18, 0.95), true)
    draw_rect(Rect2(px + 10, py + 12, 82, 62), turn_col, false, 2.0)
    _draw_text("UNIT", Vector2(px + 51, py + 43), 12, turn_col)

func _draw_portrait_strip() -> void:
    if player_units.is_empty():
        return
    var strip_y: float = size.y - 214.0
    var card_w: float = 70.0
    var card_h: float = 80.0
    var total_w: float = float(player_units.size()) * card_w + max(0.0, float(player_units.size() - 1) * 4.0)
    var start_x: float = (size.x - total_w) * 0.5
    draw_rect(Rect2(start_x - 8.0, strip_y, total_w + 16.0, card_h), Color(0, 0, 0, 0.75), true)
    draw_line(Vector2(start_x - 8.0, strip_y + card_h), Vector2(start_x + total_w + 8.0, strip_y + card_h), NEON, 2.0)
    for i in range(player_units.size()):
        var unit: Dictionary = player_units[i]
        var x: float = start_x + float(i) * (card_w + 4.0)
        var active: bool = i == active_player_index and turn_side == "player"
        var fill: Color = Color(0.12, 0.26, 0.34, 0.95) if active else Color(0.03, 0.08, 0.12, 0.85)
        var role: String = str(unit.get("role", "agent")).to_lower()
        var role_col: Color = ROLE_SAMURAI
        if role == "sniper":
            role_col = ROLE_SNIPER
        elif role == "psi":
            role_col = ROLE_PSI
        draw_rect(Rect2(x, strip_y + 2.0, card_w, card_h - 4.0), fill, true)
        draw_line(Vector2(x, strip_y + card_h - 2.0), Vector2(x + card_w, strip_y + card_h - 2.0), role_col if active else Color(0.23, 0.47, 0.56, 1.0), 2.0)
        if active:
            draw_arc(Vector2(x + card_w * 0.5, strip_y + card_h * 0.5), 33.0, 0.0, TAU, 48, role_col, 2.0)
        var hp_frac: float = clamp(float(int(unit.get("hp", 0))) / float(max(1, int(unit.get("max_hp", 1)))), 0.0, 1.0)
        draw_rect(Rect2(x + 4.0, strip_y + 18.0, 36.0, 36.0), Color(0.08, 0.16, 0.2, 0.95), true)
        draw_rect(Rect2(x + 4.0, strip_y + 18.0, 36.0, 36.0), role_col, false, 1.0)
        _draw_text(str(unit.get("name", "Agent")).substr(0, 6).to_upper(), Vector2(x + 42.0, strip_y + 30.0), 8, TEXT if active else TEXT)
        _draw_text(str(unit.get("role", "agent")).to_upper().substr(0, 6), Vector2(x + 42.0, strip_y + 44.0), 7, role_col)
        draw_rect(Rect2(x + 4.0, strip_y + 52.0, card_w - 8.0, 6.0), Color(0.05, 0.1, 0.12, 1.0), true)
        draw_rect(Rect2(x + 4.0, strip_y + 52.0, (card_w - 8.0) * hp_frac, 6.0), PLAYER_COL if hp_frac > 0.5 else (WARN if hp_frac > 0.25 else ENEMY_COL), true)
        for d in range(max(1, int(unit.get("ap", 0)) + 1)):
            var dot_x: float = x + 4.0 + float(d) * 12.0
            draw_rect(Rect2(dot_x, strip_y + 62.0, 8.0, 6.0), PLAYER_COL if d < int(unit.get("ap", 0)) else Color(0.08, 0.16, 0.2, 1.0), true)

func _draw_action_bar() -> void:
    var bar_bottom: float = size.y - 130.0
    var bar_width: float = min(size.x - 36.0, 880.0)
    var bar_height: float = 112.0
    var bar: Rect2 = Rect2((size.x - bar_width) * 0.5, bar_bottom, bar_width, bar_height)
    draw_rect(bar, Color(0, 0, 0, 0.82), true)
    draw_line(Vector2(bar.position.x, bar.position.y + bar.size.y), Vector2(bar.position.x + bar.size.x, bar.position.y + bar.size.y), NEON, 1.0)
    var active: Dictionary = _current_active_player()
    var unit_name: String = str(active.get("name", "UNIT")).to_upper() if not active.is_empty() else "UNIT"
    _draw_text("%s // AP %d" % [unit_name, int(active.get("ap", 0)) if not active.is_empty() else 0], Vector2(bar.position.x + 18.0, bar.position.y + 24.0), 11, WARN)
    _draw_text(status_line, Vector2(bar.position.x + 220.0, bar.position.y + 24.0), 10, TEXT)
    action_rects = {}
    var enabled_actions: Array[String] = ACTIONS.duplicate()
    var btn_w: float = min(96.0, max(66.0, (bar.size.x - 48.0) / float(max(1, enabled_actions.size()))))
    var total: float = float(enabled_actions.size()) * btn_w + float(max(0, enabled_actions.size() - 1)) * 10.0
    var bx: float = bar.position.x + max(20.0, (bar.size.x - total) * 0.5)
    var by: float = bar.position.y + 46.0
    for action in enabled_actions:
        var label := action
        if action == "END TURN" and pending_end_turn_confirmation:
            label = "CONFIRM"
        var rect := Rect2(bx, by, btn_w, 58.0)
        action_rects[action] = rect
        var active_action := selected_action == action
        var fill := Color(0.04, 0.14, 0.12, 0.92) if not active_action else Color(0.08, 0.26, 0.18, 0.96)
        var border := NEON if not active_action else WARN
        if turn_side != "player" or turn_side == "ended":
            fill = Color(0.04, 0.08, 0.1, 0.65)
            border = Color(0.3, 0.55, 0.5, 0.55)
        draw_rect(rect, fill, true)
        draw_line(Vector2(rect.position.x, rect.position.y + rect.size.y), Vector2(rect.position.x + rect.size.x, rect.position.y + rect.size.y), border, 2.0)
        _draw_text(label, Vector2(rect.position.x + rect.size.x * 0.5, rect.position.y + 20.0), 10, TEXT if active_action else TEXT)
        bx += btn_w + 10.0
    _draw_text("Enter: deploy/confirm   Tab: log   Mouse: act", Vector2(bar.position.x + bar.size.x - 12.0, bar.position.y + 24.0), 9, TEXT)

func _draw_target_lock_panel() -> void:
    var target := _current_target()
    if target.is_empty() or active_player_index < 0 or active_player_index >= player_units.size():
        return
    var pw := 270.0
    var ph := 80.0
    var px := size.x - pw - 14.0
    var py: float = battlefield_rect.position.y + battlefield_rect.size.y + 12.0
    draw_rect(Rect2(px, py, pw, ph), Color(0, 0, 0, 0.82), true)
    draw_line(Vector2(px, py + ph), Vector2(px + pw, py + ph), ENEMY_COL, 2.0)
    _draw_text("TARGET LOCK", Vector2(px + 10.0, py + 16.0), 10, ENEMY_COL)
    _draw_text(str(target.get("name", "TARGET")).to_upper(), Vector2(px + 10.0, py + 32.0), 13, TEXT)
    var atk: int = 12 + _active_player_unit_stat("ap") * 4
    var defense: int = int(target.get("defense", 8))
    var chance: float = clamp(float(60 + atk - defense * 2), 20.0, 95.0)
    _draw_text("HIT %d%%  DEF %d" % [int(chance), defense], Vector2(px + 10.0, py + 48.0), 10, WARN if chance < 50.0 else PLAYER_COL)
    _draw_text("HP %d/%d" % [int(target.get("hp", 0)), int(target.get("max_hp", 1))], Vector2(px + pw - 86.0, py + 66.0), 9, ENEMY_COL)
    var bw := pw - 20.0
    draw_rect(Rect2(px + 10.0, py + 60.0, bw, 6.0), Color(0.05, 0.1, 0.12, 1.0), true)
    draw_rect(Rect2(px + 10.0, py + 60.0, bw * clamp(float(int(target.get("hp", 0))) / float(max(1, int(target.get("max_hp", 1)))), 0.0, 1.0), 6.0), ENEMY_COL, true)

func _draw_combat_log_panel() -> void:
    var panel_w := 260.0
    var max_lines := 8
    var panel_h := float(max_lines) * 18.0 + 44.0
    var px := size.x - panel_w - 8.0
    var py := 394.0
    draw_rect(Rect2(px, py, panel_w, panel_h), Color(0.03, 0.08, 0.12, 0.9), true)
    draw_line(Vector2(px, py + panel_h), Vector2(px + panel_w, py + panel_h), NEON, 1.0)
    _draw_text("COMBAT LOG  [Tab]", Vector2(px + panel_w * 0.5, py + 14.0), 10, TEXT)
    var visible: Array[String] = combat_log.duplicate()
    visible.reverse()
    var line_y := py + panel_h - 44.0
    for i in range(min(max_lines, visible.size())):
        _draw_text(visible[i].substr(0, 34), Vector2(px + 8.0, line_y), 9, TEXT if i == 0 else Color(0.72, 0.82, 0.82, 1.0))
        line_y -= 18.0

func _build_player_units() -> Array[Dictionary]:
    var squad: Array = handoff.get("squad", [])
    var units: Array[Dictionary] = []
    if squad.is_empty():
        units.append({
            "name": "AGENT",
            "role": "samurai",
            "hp": 30,
            "max_hp": 30,
            "stress": 20,
            "ap": 2,
            "initiative": 18,
            "position": Vector2i(1, 1),
            "kind": "player",
            "status_effects": [],
        })
        return units
    for i in range(squad.size()):
        var raw: Variant = squad[i]
        if typeof(raw) != TYPE_DICTIONARY:
            continue
        var agent: Dictionary = raw as Dictionary
        var role := str(agent.get("role", "agent")).to_lower()
        var row := 1 + (i * 2)
        if row >= GRID_ROWS:
            var band_count: int = max(1, int(GRID_ROWS / 2))
            row = 1 + (i % band_count) * 2
        units.append({
            "name": str(agent.get("name", "Agent")),
            "role": role,
            "hp": int(agent.get("hp", 30)),
            "max_hp": max(1, int(agent.get("max_hp", agent.get("hp", 30)))),
            "stress": int(agent.get("stress", 0)),
            "ap": 2 if int(agent.get("stress", 0)) < 80 else 1,
            "initiative": 20 + int(agent.get("level", 1)) * 2 - i,
            "position": Vector2i(1, min(GRID_ROWS - 1, row)),
            "kind": "player",
            "status_effects": [],
        })
    return units

func _build_enemy_units() -> Array[Dictionary]:
    var mission: Dictionary = _mission_data()
    var contacts_value: Variant = mission.get("starting_enemy_count", 3)
    var count: int = max(1, min(6, int(contacts_value)))
    var enemy_theme: String = str(mission.get("enemy_theme", "generic")).to_lower()
    var subtypes := ["grunt", "grunt", "sniper", "elite", "commander", "grunt"]
    var units: Array[Dictionary] = []
    for i in range(count):
        var subtype: String = str(subtypes[min(i, subtypes.size() - 1)])
        var hp: int = 10 + (i * 2)
        if subtype == "elite":
            hp += 4
        elif subtype == "commander":
            hp += 8
        units.append({
            "name": "%s %02d" % [enemy_theme.replace("_", " ").to_upper(), i + 1],
            "role": "enemy",
            "hp": hp,
            "max_hp": hp,
            "stress": 0,
            "ap": 2,
            "initiative": 16 - i * 2,
            "position": Vector2i(GRID_COLS - 2 - (i % 2), 1 + (i % 4) * 2),
            "kind": "enemy",
            "enemy_subtype": subtype,
            "enemy_theme": enemy_theme,
            "status_effects": [],
            "defense": 7 + i,
        })
    return units

func _refresh_initiative() -> void:
    initiative_entries = []
    var ordered_players: Array[Dictionary] = []
    var active := _current_active_player()
    if not active.is_empty():
        ordered_players.append(active)
    for i in range(player_units.size()):
        var unit: Dictionary = player_units[i]
        if unit == active or int(unit.get("hp", 0)) <= 0:
            continue
        ordered_players.append(unit)
    ordered_players.sort_custom(Callable(self, "_compare_unit_initiative"))

    var ordered_enemies: Array[Dictionary] = []
    for enemy in enemy_units:
        if int(enemy.get("hp", 0)) > 0:
            ordered_enemies.append(enemy)
    ordered_enemies.sort_custom(Callable(self, "_compare_unit_initiative"))

    var projected: Array[Dictionary] = []
    projected.append_array(ordered_players)
    projected.append_array(ordered_enemies)
    for i in range(min(8, projected.size())):
        var unit: Dictionary = projected[i]
        var is_enemy := str(unit.get("kind", "player")) == "enemy"
        initiative_entries.append({
            "label": _unit_short_label(unit),
            "is_enemy": is_enemy,
            "is_active": i == 0,
            "threat": _enemy_threat(unit) if is_enemy else "",
        })

func _compare_unit_initiative(a: Dictionary, b: Dictionary) -> bool:
    return int(a.get("initiative", 0)) > int(b.get("initiative", 0))

func _unit_short_label(unit: Dictionary) -> String:
    if str(unit.get("kind", "player")) == "enemy":
        return str(unit.get("enemy_subtype", "grunt")).to_upper().substr(0, 9)
    return str(unit.get("name", "AGENT")).to_upper().split(" ")[0].substr(0, 9)

func _enemy_threat(unit: Dictionary) -> String:
    var subtype := str(unit.get("enemy_subtype", "grunt")).to_lower()
    if subtype in ["sniper", "elite", "commander"]:
        return "HIGH"
    return ""

func _current_active_player() -> Dictionary:
    if active_player_index < 0 or active_player_index >= player_units.size():
        return {}
    var raw: Variant = player_units[active_player_index]
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}

func _current_target() -> Dictionary:
    if enemy_units.is_empty():
        return {}
    if selected_target_index < 0 or selected_target_index >= enemy_units.size():
        selected_target_index = 0
    if int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
        for i in range(enemy_units.size()):
            if int(enemy_units[i].get("hp", 0)) > 0:
                selected_target_index = i
                break
    if int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
        return {}
    var raw: Variant = enemy_units[selected_target_index]
    if typeof(raw) == TYPE_DICTIONARY:
        return raw as Dictionary
    return {}

func _cell_position(unit: Dictionary) -> Vector2i:
    var raw: Variant = unit.get("position", Vector2i.ZERO)
    if typeof(raw) == TYPE_VECTOR2I:
        return raw as Vector2i
    return Vector2i.ZERO

func _cell_center(cell: Vector2i) -> Vector2:
    var cell_w := battlefield_rect.size.x / float(GRID_COLS)
    var cell_h := battlefield_rect.size.y / float(GRID_ROWS)
    return Vector2(
        battlefield_rect.position.x + float(cell.x) * cell_w + cell_w * 0.5,
        battlefield_rect.position.y + float(cell.y) * cell_h + cell_h * 0.5,
    )

func _unit_center(unit: Dictionary) -> Vector2:
    return _cell_center(_cell_position(unit))

func _cell_from_point(point: Vector2) -> Vector2i:
    if not battlefield_rect.has_point(point):
        return Vector2i(-1, -1)
    var cell_w := battlefield_rect.size.x / float(GRID_COLS)
    var cell_h := battlefield_rect.size.y / float(GRID_ROWS)
    var x := int((point.x - battlefield_rect.position.x) / cell_w)
    var y := int((point.y - battlefield_rect.position.y) / cell_h)
    return Vector2i(clamp(x, 0, GRID_COLS - 1), clamp(y, 0, GRID_ROWS - 1))

func _unit_at_point(point: Vector2, enemy_only: bool) -> int:
    var pool: Array = enemy_units if enemy_only else player_units
    for i in range(pool.size()):
        var unit: Dictionary = pool[i]
        if int(unit.get("hp", 0)) <= 0:
            continue
        var center := _unit_center(unit)
        var size := 26.0 if enemy_only else 28.0
        var rect := Rect2(center.x - size * 0.55, center.y - size * 0.55, size * 1.1, size * 1.1)
        if rect.has_point(point):
            return i
    return -1

func _draw_deploy_prompt() -> void:
    var rect := Rect2(72, size.y - 166, 260, 44)
    deploy_rect = rect
    draw_rect(rect, Color(0.04, 0.22, 0.17, 0.95), true)
    draw_rect(rect, NEON, false, 1.5)
    _draw_text("DEPLOY  [Enter]", rect.position + Vector2(16, 28), 16, TEXT)
    _draw_text("Click to begin combat.", Vector2(74, size.y - 116), 14, WARN)

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

func _draw_text_centered(text: String, pos: Vector2, font_size: int, color: Color, width: float = 320.0) -> void:
    draw_string(ThemeDB.fallback_font, pos, text, HORIZONTAL_ALIGNMENT_CENTER, width, font_size, color)

func _gui_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        var key_event := event as InputEventKey
        if key_event.keycode == KEY_ESCAPE:
            get_tree().quit()
            accept_event()
            return
        if key_event.keycode == KEY_TAB:
            show_combat_log = not show_combat_log
            queue_redraw()
            accept_event()
            return
        if key_event.keycode == KEY_ENTER or key_event.keycode == KEY_KP_ENTER:
            if not battle_started:
                _start_combat("ENTER")
            elif selected_action == "END TURN" and pending_end_turn_confirmation:
                _end_player_turn()
            elif selected_action == "END TURN":
                _execute_action("END TURN")
            elif selected_action in ["FIRE", "MELEE", "PSI"]:
                _resolve_selected_attack()
            accept_event()
            return
        if key_event.keycode == KEY_SPACE and battle_started and selected_action == "MOVE":
            _move_active_unit_to(_cell_center(_cell_position(_current_active_player())))
            accept_event()
            return

    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        var mouse_event := event as InputEventMouseButton
        var point := mouse_event.position
        if not battle_started:
            if deploy_rect.has_point(point):
                _start_combat("DEPLOY")
                accept_event()
            return
        for action_key in action_rects.keys():
            var rect: Rect2 = action_rects.get(action_key, Rect2()) as Rect2
            if rect.has_point(point):
                _execute_action(str(action_key))
                accept_event()
                return
        _handle_combat_field_click(point)
        accept_event()

func _start_combat(source: String) -> void:
    if battle_started:
        return
    battle_started = true
    status_line = "TACTICAL COMBAT UI READY"
    _log_event("%s: tactical insertion live." % source)
    print("TACTICAL COMBAT UI READY: grid / timeline / action bar / unit panel / log")
    queue_redraw()

func _execute_action(action_name: String) -> void:
    if not battle_started or turn_side != "player" or turn_side == "ended":
        return
    if action_name == "END TURN":
        if pending_end_turn_confirmation:
            _end_player_turn()
            return
        pending_end_turn_confirmation = true
        status_line = "Confirm end turn to hand control to enemies."
        _log_event("End turn confirmation armed.")
        queue_redraw()
        return
    selected_action = action_name
    pending_end_turn_confirmation = false
    status_line = "%s selected." % action_name
    _log_event("%s selected." % action_name)
    queue_redraw()

func _handle_combat_field_click(point: Vector2) -> void:
    if turn_side != "player" or turn_side == "ended" or not battle_started:
        return
    var cell := _cell_from_point(point)
    if cell.x < 0 or cell.y < 0:
        return
    if selected_action == "MOVE":
        _move_active_unit_to(cell)
        return
    if selected_action in ["FIRE", "MELEE", "PSI"]:
        var target_index := _unit_at_point(point, true)
        if target_index >= 0:
            selected_target_index = target_index
            _attack_enemy(target_index, selected_action)
            return
        if selected_action == "PSI":
            _log_event("Psi pulse stabilizes the squad feed.")
            status_line = "Psi pulse online."
            queue_redraw()
            return
        _resolve_selected_attack()
        return
    if selected_action in ["DEFEND", "OVERWATCH"]:
        _log_event("%s active." % selected_action)
        status_line = "%s active." % selected_action
        queue_redraw()

func _resolve_selected_attack() -> void:
    var target := _current_target()
    if target.is_empty():
        status_line = "No live target."
        _log_event("No live target available.")
        queue_redraw()
        return
    _attack_enemy(selected_target_index, selected_action)

func _move_active_unit_to(cell: Vector2i) -> void:
    var active := _current_active_player()
    if active.is_empty():
        return
    var index := active_player_index
    var unit := player_units[index] as Dictionary
    unit["position"] = cell
    player_units[index] = unit
    status_line = "%s moved to %d,%d" % [str(unit.get("name", "Agent")), cell.x, cell.y]
    _log_event("%s moved to %d,%d" % [str(unit.get("name", "Agent")), cell.x, cell.y])
    queue_redraw()

func _attack_enemy(target_index: int, action_name: String) -> void:
    if target_index < 0 or target_index >= enemy_units.size():
        return
    var target := enemy_units[target_index] as Dictionary
    if int(target.get("hp", 0)) <= 0:
        return
    var damage := 2
    if action_name == "FIRE":
        damage = 4
    elif action_name == "MELEE":
        damage = 3
    elif action_name == "PSI":
        damage = 2
    target["hp"] = max(0, int(target.get("hp", 0)) - damage)
    enemy_units[target_index] = target
    var attacker_name := str(_current_active_player().get("name", "Agent"))
    var line := "%s %s %s for %d." % [attacker_name, action_name.to_lower(), str(target.get("name", "enemy")), damage]
    _log_event(line)
    status_line = line
    if int(target.get("hp", 0)) <= 0:
        _log_event("%s neutralized." % str(target.get("name", "enemy")))
    _selected_target_validity()
    _refresh_initiative()
    if _enemy_alive_count() == 0:
        _complete_mission()
    queue_redraw()

func _end_player_turn() -> void:
    pending_end_turn_confirmation = false
    selected_action = "MOVE"
    turn_side = "enemy"
    enemy_turn_timer = enemy_turn_duration
    _log_event("Player ends turn.")
    status_line = "Enemy turn in progress."
    queue_redraw()

func _resolve_enemy_turn() -> void:
    if turn_side != "enemy":
        return
    var target_index := _next_alive_player_index(active_player_index)
    if target_index >= 0 and target_index < player_units.size():
        active_player_index = target_index
        var unit := player_units[target_index] as Dictionary
        unit["stress"] = min(100, int(unit.get("stress", 0)) + 6)
        unit["hp"] = max(1, int(unit.get("hp", 0)) - 1)
        player_units[target_index] = unit
        _log_event("Enemy pressure hits %s." % str(unit.get("name", "Agent")))
    turn_side = "player"
    turn_number += 1
    status_line = "Your turn."
    _refresh_initiative()
    queue_redraw()

func _complete_mission() -> void:
    turn_side = "ended"
    status_line = "Extraction corridor clear. Objective complete."
    _log_event("Mission complete.")
    _refresh_initiative()
    queue_redraw()

func _selected_target_validity() -> void:
    if enemy_units.is_empty():
        selected_target_index = 0
        return
    if selected_target_index < 0 or selected_target_index >= enemy_units.size():
        selected_target_index = 0
    if int(enemy_units[selected_target_index].get("hp", 0)) <= 0:
        for i in range(enemy_units.size()):
            if int(enemy_units[i].get("hp", 0)) > 0:
                selected_target_index = i
                return

func _enemy_alive_count() -> int:
    var count := 0
    for enemy in enemy_units:
        if int(enemy.get("hp", 0)) > 0:
            count += 1
    return count

func _alive_enemy_indices() -> Array[int]:
    var indices: Array[int] = []
    for i in range(enemy_units.size()):
        if int(enemy_units[i].get("hp", 0)) > 0:
            indices.append(i)
    return indices

func _next_alive_player_index(start_index: int) -> int:
    if player_units.is_empty():
        return -1
    var count := player_units.size()
    for offset in range(1, count + 1):
        var idx := (start_index + offset) % count
        if int(player_units[idx].get("hp", 0)) > 0:
            return idx
    return start_index

func _log_event(line: String) -> void:
    combat_log.append(line)
    if combat_log.size() > 10:
        combat_log.remove_at(0)

func _active_player_unit_stat(key: String) -> int:
    var unit := _current_active_player()
    if unit.is_empty():
        return 0
    return int(unit.get(key, 0))

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
