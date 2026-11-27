extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	assert(AudioServer.get_driver_name() == "WASAPI")
	var mission = load("res://scenes/combat_mission_ui.tscn").instantiate()
	mission.project_root = ProjectSettings.globalize_path("res://../..")
	var args := OS.get_cmdline_user_args()
	var handoff_index := args.find("--handoff")
	if handoff_index >= 0 and handoff_index + 1 < args.size():
		mission.handoff_path = args[handoff_index + 1]
	root.add_child(mission)
	await create_timer(2.5).timeout
	mission._audio.configure_soundtrack({"enabled":true, "music_volume":0.7}, mission.project_root, true)
	var bus := AudioServer.get_bus_index("Music")
	assert(bus > 0 and AudioServer.get_bus_index("SFX") > 0)
	var music := AudioEffectCapture.new()
	AudioServer.add_bus_effect(bus, music)
	var effects := AudioEffectCapture.new()
	AudioServer.add_bus_effect(AudioServer.get_bus_index("SFX"), effects)
	for event in ["move", "fire_sniper"]:
		effects.clear_buffer()
		mission._audio._on_audio_event(event)
		await create_timer(0.5).timeout
		var effects_peak := 0.0
		for sample: Vector2 in effects.get_buffer(effects.get_frames_available()):
			effects_peak = maxf(effects_peak, maxf(absf(sample.x), absf(sample.y)))
		assert(effects_peak > 0.001)
		print("WASAPI SFX bus peak ", event, ": ", effects_peak)
	var peak := 0.0
	for sample: Vector2 in music.get_buffer(music.get_frames_available()):
		peak = maxf(peak, maxf(absf(sample.x), absf(sample.y)))
	assert(peak > 0.001)
	print("WASAPI music bus peak: ", peak)
	quit()

