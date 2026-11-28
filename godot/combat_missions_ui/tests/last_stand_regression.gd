extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var mission = load("res://scenes/combat_mission_ui.tscn").instantiate()
	root.add_child(mission)
	await create_timer(2.3).timeout
	assert(mission.battle_started and mission.enemy_units.size() > 1)
	var session: Dictionary = mission.handoff.get("session", {})
	var actor: Dictionary = mission.player_units[mission.active_player_index]
	actor["hp"] = 1
	actor["aim"] = 100
	if session.is_empty():
		actor["last_stand_dialogue"] = "I've still got something to finish."
	assert(not str(actor.last_stand_dialogue).is_empty())
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
	assert(count == 1 and actor.last_stand_spoken and actor.last_stand_hp == 1)
	assert(actor.kills == 2 and actor.damage_dealt == 2)
	# Exercise a new presentation state with two hostile casualties in one blast.
	actor.erase("last_stand_spoken")
	actor["kills"] = 0
	actor["damage_dealt"] = 0
	actor["actions_used"] = 0
	mission.combat_log.clear()
	mission.active_player_index = mission.player_units.find(actor)
	actor["ap"] = 8
	var center: Vector2i = actor.position + Vector2i.RIGHT
	for i in range(2):
		mission.enemy_units[i]["hp"] = 1
		mission.enemy_units[i]["position"] = center + Vector2i(0, i)
	mission.selected_action = "Missile Salvo"
	mission._update_player_visibility()
	mission._apply_missile_salvo(center)
	assert(mission.enemy_units[0].hp == 0 and mission.enemy_units[1].hp == 0)
	assert(actor.actions_used == 8 - actor.ap and actor.actions_used > 0)
	count = 0
	for entry: String in mission.combat_log:
		if actor.last_stand_dialogue in entry:
			count += 1
	assert(count == 1 and actor.last_stand_spoken)
	assert(actor.kills == 2 and actor.damage_dealt == 2)
	actor["hp"] = 4
	mission._apply_hp_damage(actor, 3)
	assert(actor.hp == 1 and actor.damage_taken == 3)
	if not session.is_empty():
		mission._end_combat("retreat")
		mission._results._extract_btn.pressed.emit()
		assert(FileAccess.file_exists(session.result_path))
	print("GODOT_LAST_STAND_CHECKS_PASSED")
	quit()
