extends SceneTree
## Turn banners retain bounded, frame-step-independent pacing.

func _initialize() -> void:
	call_deferred("run")

func _banner(reduced: bool):
	var banner = preload("res://scripts/phase_banner.gd").new()
	banner.reduced_motion = reduced
	root.add_child(banner)
	return banner

func run() -> void:
	var normal = _banner(false)
	normal.show_banner("player", 3)
	assert(normal._active and normal.visible)
	assert(normal._label_text == "PLAYER TURN — 03")
	normal._transition.custom_step(1.85)
	assert(normal._active, "normal banner must remain until slide + hold + slide completes")
	normal._transition.custom_step(0.02)
	assert(not normal._active and not normal.visible)

	var reduced = _banner(true)
	reduced.show_banner("enemy", 4)
	assert(reduced._slide_progress == 1.0)
	reduced._transition.custom_step(1.29)
	assert(reduced._active, "reduced-motion banner keeps the readable hold interval")
	reduced._transition.custom_step(0.02)
	assert(not reduced._active and not reduced.visible)

	var replaced = _banner(false)
	replaced.show_banner("player", 5)
	replaced._transition.custom_step(0.5)
	replaced.show_banner("enemy", 5)
	assert(replaced._active and replaced._label_text == "ENEMY TURN — 05")
	replaced._transition.custom_step(1.87)
	assert(not replaced._active and not replaced.visible)
	print("PHASE_PACING_CHECKS_PASSED")
	quit()
