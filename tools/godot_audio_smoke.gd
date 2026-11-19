extends SceneTree

# Headless regression: parse and instantiate the real audio_manager.gd, load
# actual generated PCM WAVs, trigger both a new effect and a legacy event.
# It never starts music or modifies source assets.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var audio_script = load("res://scripts/audio_manager.gd")
	if audio_script == null:
		push_error("Cannot load audio_manager.gd")
		quit(1)
		return
	var manager: Node = audio_script.new()
	root.add_child(manager)
	if not manager._streams.has("fire_laser_cc0_01.wav"):
		push_error("Godot could not load generated 48 kHz PCM laser WAV")
		quit(2)
		return
	if not manager._streams.has("ui_click_cc0_01.wav"):
		push_error("Godot could not load generated 48 kHz PCM UI WAV")
		quit(3)
		return
	manager._on_audio_event("fire_laser")
	manager._on_audio_event("ui_click")
	manager._on_audio_event("turn_player")
	manager.configure_soundtrack({
		"enabled": true,
		"music_volume": 0.2,
		"sfx_volume": 0.4,
		"ambience_profile": "",
	})
	print("GODOT_CC_AUDIO_SMOKE_OK")
	quit(0)
