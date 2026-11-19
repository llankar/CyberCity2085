extends Node
class_name AudioManager
## Listens to CombatSignals.audio_event and plays the matching WAV from
## res://audio/ (populated by godot_bridge.py on launch).
## Silently skips missing files so a fresh checkout still runs.

const SFX_MAP: Dictionary = {
	"move"        : "sfx_move.wav",
	"fire"        : "sfx_fire.wav",
	"melee"       : "sfx_melee.wav",
	"psi"         : "sfx_psi.wav",
	"hit"         : "sfx_hit.wav",
	"miss"        : "sfx_miss.wav",
	"death"       : "sfx_death.wav",
	"overwatch"   : "sfx_overwatch.wav",
	"defend"      : "sfx_act_advance.wav",
	"deploy"      : "sfx_deploy.wav",
	"ui_click"    : "sfx_ui_click.wav",
	"turn_player" : "sfx_turn_player.wav",
	"turn_enemy"  : "sfx_turn_enemy.wav",
	"victory"     : "sfx_victory.wav",
	"defeat"      : "sfx_defeat.wav",
	"reinforce"   : "sfx_reinforce.wav",
	"stun"        : "sfx_stun.wav",
	"bleed"       : "sfx_bleed.wav",
}

# Optional WAVs from assets/audio/overhaul, copied by godot_bridge.py.
# All are still unreviewed; the original event WAV remains the fallback.
const PREVIEW_SFX_MAP: Dictionary = {
    "fire": ["fire_assault_01.wav"],
    "fire_pistol": ["fire_pistol_01.wav"],
    "fire_laser": ["fire_laser_cc0_01.wav", "fire_laser_cc0_02.wav"],
    "hit": ["impact_metal_01.wav", "impact_metal_cc0_01.wav"],
    "hit_metal": ["impact_metal_01.wav", "impact_metal_cc0_01.wav", "impact_metal_cc0_02.wav"],
    "hit_glass": ["impact_glass_cc0_01.wav"],
    "hit_organic": ["impact_organic_cc0_01.wav"],
    "melee": ["melee_cc0_01.wav"],
    "explosion_small": ["explosion_small_cc0_01.wav"],
    "move": ["step_concrete_01.wav", "step_concrete_cc0_01.wav"],
    "move_concrete": ["step_concrete_01.wav", "step_concrete_cc0_01.wav", "step_concrete_cc0_02.wav", "step_concrete_cc0_03.wav"],
    "move_metal": ["step_metal_cc0_01.wav", "step_metal_cc0_02.wav", "step_metal_cc0_03.wav", "step_metal_cc0_04.wav", "step_metal_cc0_05.wav"],
    "move_robot": ["move_robot_cc0_01.wav"],
    "shield": ["shield_cc0_01.wav"],
    "terminal": ["terminal_cc0_01.wav"],
    "door_open": ["door_open_cc0_01.wav"],
    "ui_click": ["ui_click_01.wav", "ui_click_cc0_01.wav", "ui_click_cc0_02.wav"],
    "ui_confirm": ["ui_confirm_cc0_01.wav"],
    "ui_refuse": ["ui_refuse_cc0_01.wav"],
}
const CITY_AMBIENCE_WAV := "ambience_city_loop_candidate_01.wav"
const CC0_CITY_AMBIENCE_WAV := "ambience_city_cc0_01.wav"
const CC0_RAIN_AMBIENCE_WAV := "ambience_city_rain_cc0_01.wav"
const CCBY_LAB_AMBIENCE_WAV := "ambience_laboratory_ccby_01.wav"
const AMBIENCE_FILES: Dictionary = {
    "city": [CC0_CITY_AMBIENCE_WAV, CITY_AMBIENCE_WAV],
    "city_rain": [CC0_RAIN_AMBIENCE_WAV, CC0_CITY_AMBIENCE_WAV, CITY_AMBIENCE_WAV],
    "laboratory": [CCBY_LAB_AMBIENCE_WAV],
}
const CITY_INTRO_WAV := "ambience_city_short_candidate_02.wav"

var _sfx_players : Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer = null
var _ambience_player: AudioStreamPlayer = null
var _sfx_volume_linear: float = 0.8
var _next_sample_index: Dictionary = {}
var _active_ambience_filename: String = ""
var _streams     : Dictionary         = {}   # filename → AudioStream
var _pool_idx    : int                = 0
var _battle_music: String = "music_battle.wav"
var _current_track := ""
var _asset_root := ""
var _enabled: bool = true
var _music_owned: bool = true
const POOL_SIZE  := 6

func _ready() -> void:
	# SFX pool — allows overlapping sounds
	for _i in range(POOL_SIZE):
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_sfx_players.append(p)

	# Ambience owns a separate player; do not route long loops through the SFX pool.
	_ambience_player = AudioStreamPlayer.new()
	_ambience_player.bus = "SFX"
	_ambience_player.volume_linear = 0.08
	add_child(_ambience_player)

	# Music player
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music"
	_music_player.volume_db = -6.0
	add_child(_music_player)

	_preload_streams()

	CombatSignals.audio_event.connect(_on_audio_event)

func _preload_streams() -> void:
	for _fname: String in SFX_MAP.values():
		_load_stream(_fname)
	for preview_options in PREVIEW_SFX_MAP.values():
		for preview_file in preview_options:
			_load_stream(str(preview_file))
	for ambience_options in AMBIENCE_FILES.values():
		for ambience_file in ambience_options:
			_load_stream(str(ambience_file))
	_load_stream(CITY_INTRO_WAV)
	for mfile in ["music_battle.wav", "music_debrief.wav", "music_briefing.wav"]:
		_load_stream(mfile)

func _load_stream(filename: String) -> void:
	if _streams.has(filename):
		return
	var path := filename.replace("\\","/")
	if not path.is_absolute_path() and not path.begins_with("res://"):
		path = "res://audio/"+path
	if not FileAccess.file_exists(path): return
	if path.to_lower().ends_with(".mp3"):
		var mp3 := AudioStreamMP3.new()
		var bytes := FileAccess.get_file_as_bytes(path)
		if bytes.is_empty(): return
		mp3.data = bytes
		mp3.loop = true
		if mp3.get_length() > 0.0: _streams[filename] = mp3
	elif path.to_lower().ends_with(".wav"):
		# Read source files directly: a source checkout has no imported audio cache.
		var wav := AudioStreamWAV.load_from_file(path)
		if wav != null: _streams[filename] = wav

func _play_sfx(filename: String, volume_scale: float = 1.0) -> void:
	if not _enabled or not _streams.has(filename):
		return
	# Use an idle channel before stealing the oldest active channel.
	var player: AudioStreamPlayer = null
	for candidate in _sfx_players:
		if not candidate.playing:
			player = candidate
			break
	if player == null:
		player = _sfx_players[_pool_idx % POOL_SIZE]
		_pool_idx += 1
	player.volume_linear = clampf(_sfx_volume_linear * volume_scale, 0.0, 1.0)
	player.stream = _streams[filename] as AudioStream
	player.play()


func _play_event_sfx(event_name: String, fallback_filename: String) -> void:
	var options: Array = PREVIEW_SFX_MAP.get(event_name, [])
	var available: Array[String] = []
	for item in options:
		var filename := str(item)
		if _streams.has(filename):
			available.append(filename)
	if available.is_empty():
		_play_sfx(fallback_filename)
		return
	# Cycle through known-real WAVs, no instant repetition when 2+ exist.
	var next_index: int = int(_next_sample_index.get(event_name, 0)) % available.size()
	_next_sample_index[event_name] = next_index + 1
	_play_sfx(available[next_index])


func _set_ambience_profile(profile: String) -> void:
	if _ambience_player == null:
		return
	var options: Array = AMBIENCE_FILES.get(profile, [])
	var selected := ""
	for item in options:
		if _streams.has(str(item)):
			selected = str(item)
			break
	if not _enabled or selected.is_empty():
		_ambience_player.stop()
		_active_ambience_filename = ""
		return
	if _ambience_player.playing and _active_ambience_filename == selected:
		return
	var stream := _streams[selected] as AudioStream
	if stream is AudioStreamWAV:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = maxi(1, int(stream.get_length() * float(stream.mix_rate)))
	_ambience_player.stop()
	_ambience_player.stream = stream
	_ambience_player.volume_linear = clampf(_sfx_volume_linear * 0.09, 0.0, 1.0)
	_ambience_player.play()
	_active_ambience_filename = selected
	if profile.begins_with("city") and _streams.has(CITY_INTRO_WAV):
		_play_sfx(CITY_INTRO_WAV, 0.15)


func _play_music(filename: String, start_position: float = 0.0) -> void:
	if not _enabled or not _music_owned:
		return
	if not _streams.has(filename):
		return
	if _music_player.stream == _streams[filename] and _music_player.playing:
		return
	var stream := _streams[filename] as AudioStream
	if stream is AudioStreamWAV:
		stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		stream.loop_begin = 0
		stream.loop_end = maxi(1,int(stream.get_length()*float(stream.mix_rate)))
	elif stream is AudioStreamMP3:
		stream.loop = true
	_current_track = filename
	_music_player.stream = stream
	var length := stream.get_length()
	_music_player.play(fposmod(maxf(0,start_position),length) if length > 0 else 0.0)

func configure_soundtrack(settings: Dictionary, asset_root: String = "", music_owned: bool = true) -> void:
	_music_owned = music_owned
	_asset_root = asset_root
	_enabled = bool(settings.get("enabled", true))
	_music_player.volume_linear = clampf(float(settings.get("music_volume", 0.7)), 0.0, 1.0)
	_sfx_volume_linear = clampf(float(settings.get("sfx_volume", 0.8)), 0.0, 1.0)
	for player in _sfx_players:
		player.volume_linear = _sfx_volume_linear
	_set_ambience_profile(str(settings.get("ambience_profile", "")))
	if not _enabled:
		_music_player.stop()
		_set_ambience_profile("")
		return
	var path := str(settings.get("battle_music_path", ""))
	if not path.is_empty():
		_load_stream(path)
		if _streams.has(path):
			_battle_music = path
	if not _streams.has(_battle_music): _battle_music = "music_battle.wav"
	_play_music(_battle_music,float(settings.get("start_position",0.0)))

func _on_audio_event(event_name: String) -> void:
	match event_name:
		"move":                   _play_event_sfx("move", "sfx_move.wav")
		"fire":                   _play_event_sfx("fire", "sfx_fire.wav")
		"fire_pistol":            _play_event_sfx("fire_pistol", "sfx_fire.wav")
		"melee":                  _play_event_sfx("melee", "sfx_melee.wav")
		"psi":                    _play_sfx("sfx_psi.wav")
		"hit":                    _play_event_sfx("hit", "sfx_hit.wav")
		"miss":                   _play_sfx("sfx_miss.wav")
		"death":                  _play_sfx("sfx_death.wav")
		"overwatch":              _play_sfx("sfx_overwatch.wav")
		"ui_click":               _play_event_sfx("ui_click", "sfx_ui_click.wav")
		"ui_confirm":             _play_event_sfx("ui_confirm", "sfx_ui_click.wav")
		"ui_refuse":              _play_event_sfx("ui_refuse", "sfx_ui_click.wav")
		"fire_laser":             _play_event_sfx("fire_laser", "sfx_fire.wav")
		"hit_metal":              _play_event_sfx("hit_metal", "sfx_hit.wav")
		"hit_glass":              _play_event_sfx("hit_glass", "sfx_hit.wav")
		"hit_organic":            _play_event_sfx("hit_organic", "sfx_hit.wav")
		"move_concrete":          _play_event_sfx("move_concrete", "sfx_move.wav")
		"move_metal":             _play_event_sfx("move_metal", "sfx_move.wav")
		"move_robot":             _play_event_sfx("move_robot", "sfx_move.wav")
		"shield":                 _play_event_sfx("shield", "sfx_psi.wav")
		"terminal":               _play_event_sfx("terminal", "sfx_ui_click.wav")
		"door_open":              _play_event_sfx("door_open", "sfx_ui_click.wav")
		"explosion_small":        _play_event_sfx("explosion_small", "sfx_hit.wav")
		"turn_player":            _play_sfx("sfx_turn_player.wav"); _play_music(_battle_music)
		"turn_enemy":             _play_sfx("sfx_turn_enemy.wav")
		"victory":                _play_sfx("sfx_victory.wav");    _play_music("music_debrief.wav")
		"defeat":                 _play_sfx("sfx_defeat.wav");     _play_music("music_debrief.wav")
		"deploy":                 _play_sfx("sfx_deploy.wav")
		"stun":                   _play_sfx("sfx_stun.wav")
		"bleed":                  _play_sfx("sfx_bleed.wav")

func playback_bookmark() -> Dictionary:
	if _current_track.is_empty() or _music_player == null: return {}
	var path := _current_track if _current_track.is_absolute_path() else _asset_root.path_join("assets/audio/music").path_join(_current_track)
	return {"path":path,"position":_music_player.get_playback_position(),"captured_at":Time.get_unix_time_from_system()}
