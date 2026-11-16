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

var _sfx_players : Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer = null
var _streams     : Dictionary         = {}   # filename → AudioStream
var _pool_idx    : int                = 0
var _battle_music: String = "music_battle.wav"
var _enabled: bool = true
const POOL_SIZE  := 6

func _ready() -> void:
	# SFX pool — allows overlapping sounds
	for _i in range(POOL_SIZE):
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_sfx_players.append(p)

	# Music player
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music"
	_music_player.volume_db = -6.0
	add_child(_music_player)

	_preload_streams()
	_play_music("music_battle.wav")

	CombatSignals.audio_event.connect(_on_audio_event)

func _preload_streams() -> void:
	for _fname: String in SFX_MAP.values():
		_load_stream(_fname)
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

func _play_sfx(filename: String) -> void:
	if not _enabled:
		return
	if not _streams.has(filename):
		return
	var player := _sfx_players[_pool_idx % POOL_SIZE] as AudioStreamPlayer
	_pool_idx += 1
	player.stream = _streams[filename] as AudioStream
	player.play()

func _play_music(filename: String) -> void:
	if not _enabled:
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
	_music_player.stream = stream
	_music_player.play()

func configure_soundtrack(settings: Dictionary) -> void:
	_enabled = bool(settings.get("enabled", true))
	_music_player.volume_linear = clampf(float(settings.get("music_volume", 0.7)), 0.0, 1.0)
	for player in _sfx_players:
		player.volume_linear = clampf(float(settings.get("sfx_volume", 0.8)), 0.0, 1.0)
	if not _enabled:
		_music_player.stop()
		return
	var path := str(settings.get("battle_music_path", ""))
	if not path.is_empty():
		_load_stream(path)
		if _streams.has(path):
			_battle_music = path
	if not _streams.has(_battle_music): _battle_music = "music_battle.wav"
	_play_music(_battle_music)

func _on_audio_event(event_name: String) -> void:
	match event_name:
		"move":                   _play_sfx("sfx_move.wav")
		"fire":                   _play_sfx("sfx_fire.wav")
		"melee":                  _play_sfx("sfx_melee.wav")
		"psi":                    _play_sfx("sfx_psi.wav")
		"hit":                    _play_sfx("sfx_hit.wav")
		"miss":                   _play_sfx("sfx_miss.wav")
		"death":                  _play_sfx("sfx_death.wav")
		"overwatch":              _play_sfx("sfx_overwatch.wav")
		"ui_click":               _play_sfx("sfx_ui_click.wav")
		"turn_player":            _play_sfx("sfx_turn_player.wav"); _play_music(_battle_music)
		"turn_enemy":             _play_sfx("sfx_turn_enemy.wav")
		"victory":                _play_sfx("sfx_victory.wav");    _play_music("music_debrief.wav")
		"defeat":                 _play_sfx("sfx_defeat.wav");     _play_music("music_debrief.wav")
		"deploy":                 _play_sfx("sfx_deploy.wav")
		"stun":                   _play_sfx("sfx_stun.wav")
		"bleed":                  _play_sfx("sfx_bleed.wav")
