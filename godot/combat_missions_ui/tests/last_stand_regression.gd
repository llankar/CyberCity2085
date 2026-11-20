extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var mission = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(mission)
	await create_timer(2.3).timeout
	assert(mission.battle_started and mission.enemy_units.size() > 1)
	var actor: Dictionary = mission.player_units[mission.active_player_index]
	actor["hp"] = 1
	actor["aim"] = 100
	actor["last_stand_dialogue"] = "I've still got something to finish."
	for i in range(2):
		var enemy: Dictionary = mission.enemy_units[i]
		enemy["hp"] = 1
		enemy["position"] = actor.position + Vector2i.RIGHT
		actor["ap"] = 4
		for attempt in range(12):
			mission._attack_enemy(i, "Rifle Burst")
			if enemy.hp == 0:
				break
			actor["ap"] = 4
		assert(enemy.hp == 0)
	var count := 0
	for entry: String in mission.combat_log:
		if actor.last_stand_dialogue in entry:
			count += 1
	assert(count == 1 and actor.last_stand_spoken)
	print("GODOT_LAST_STAND_CHECKS_PASSED")
	quit()
