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
	var path := "res://audio/" + filename
	if not ResourceLoader.exists(path):
		return
	var s := load(path) as AudioStream
	if s != null:
		_streams[filename] = s

func _play_sfx(filename: String) -> void:
	if not _streams.has(filename):
		return
	var player := _sfx_players[_pool_idx % POOL_SIZE] as AudioStreamPlayer
	_pool_idx += 1
	player.stream = _streams[filename] as AudioStream
	player.play()

func _play_music(filename: String) -> void:
	if not _streams.has(filename):
		return
	if _music_player.stream == _streams[filename]:
		return
	_music_player.stream = _streams[filename] as AudioStream
	_music_player.play()

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
		"turn_player":            _play_sfx("sfx_turn_player.wav"); _play_music("music_battle.wav")
		"turn_enemy":             _play_sfx("sfx_turn_enemy.wav")
		"victory":                _play_sfx("sfx_victory.wav");    _play_music("music_debrief.wav")
		"defeat":                 _play_sfx("sfx_defeat.wav");     _play_music("music_debrief.wav")
		"deploy":                 _play_sfx("sfx_deploy.wav")
		"stun":                   _play_sfx("sfx_stun.wav")
		"bleed":                  _play_sfx("sfx_bleed.wav")
