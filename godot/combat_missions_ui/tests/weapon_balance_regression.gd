extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var scene=load("res://scripts/combat_mission_ui.gd").new()
	assert(scene._action_range("Pistol Shot")>=6)
	assert(scene._action_range("Rifle Burst")>=18)
	assert(scene._action_range("Plasma Burst")>=15)
	assert(scene._action_range("Precision Shot")>scene._action_range("Rifle Burst"))
	assert(scene._action_range("Rifle Burst")>scene._action_range("Plasma Shot"))
	assert(scene._action_damage("Precision Shot")>scene._action_damage("Rifle Burst"))
	assert(scene._action_damage("Rifle Burst")>scene._action_damage("Pistol Shot"))
	assert(scene._action_damage("Shotgun Blast")>scene._action_damage("Rifle Burst") and scene._action_range("Shotgun Blast")<scene._action_range("Rifle Burst"))
	assert(scene._subtype_attack_range("grunt")==scene._action_range("Pistol Shot"))
	assert(scene._subtype_attack_range("elite")==scene._action_range("Rifle Burst"))
	assert(scene._subtype_attack_range("sniper")==scene._action_range("Precision Shot"))
	for action in ["Katana Slash","Blade Strike","Servo Punch"]:assert(scene._action_range(action)==1 and scene._action_ap_cost(action)==1)
	assert(scene._action_range("PSI")==0 and scene._role_attack_range("psi","PSI")==5)
	assert(scene._action_ap_cost("Rifle Burst")==1 and scene._action_ap_cost("Plasma Burst")==2)
	scene.free()
	var live=load("res://scenes/combat_mission_ui.tscn").instantiate()
	live.handoff_path="user://weapon-balance-fixture.json"
	var file:=FileAccess.open(live.handoff_path,FileAccess.WRITE)
	file.store_string(JSON.stringify({"audio":{"enabled":false},"mission":{"objective_type":"hack","risk_level":1},"squad":[{"name":"QA","role":"samurai","hp":24,"max_hp":24,"aim":100}],"support_assets":[{"name":"QA Armor","asset_type":"power_armor","hp":40},{"name":"QA Robot","asset_type":"combat_robot","hp":36}]}));file.close()
	root.add_child(live);await process_frame;await process_frame
	assert(live.player_units.size()==3,"both support entity families retain default actions when a handoff omits them")
	assert(live.player_units[1].available_actions==["Move","Defend","Rifle Burst","Servo Punch"])
	assert(live.player_units[2].available_actions==["Move","Defend","Missile Salvo"])
	var selection_state:=JSON.stringify(live.player_units)
	live._on_unit_clicked(1,false);assert(live.active_player_index==1,"power armor selects through the combat controller")
	live._on_unit_clicked(2,false);assert(live.active_player_index==2,"robot selects through the combat controller")
	live._on_unit_clicked(1000,false);assert(live.active_player_index==2,"decorative vehicles never become combat selections")
	live._on_unit_clicked(0,false);assert(live.active_player_index==0)
	assert(JSON.stringify(live.player_units)==selection_state,"selection never spends AP or changes unit statistics")
	live.active_player_index=0;live.player_units[0].position=Vector2i(5,5);live.player_units[0].ap=4;live.player_units[0].aim=100
	live.enemy_units[0].position=Vector2i(23,5);live.enemy_units[0].hp=100;live.enemy_units[0].defense=0
	live._battlefield._opaque_cells.clear()
	live._attack_enemy(0,"Pistol Shot")
	assert(live.player_units[0].ap==4 and live.enemy_units[0].hp==100 and live.status_line.begins_with("Cible hors de portée"))
	var hit_seed:=0
	seed(hit_seed)
	while randf()>=.94:
		hit_seed+=1;seed(hit_seed)
	seed(hit_seed)
	live._attack_enemy(0,"Rifle Burst")
	assert(live.player_units[0].ap==3 and live.enemy_units[0].hp==93,"rifle genuinely hits at 18 cells for its new damage and unchanged AP")
	live.selected_action="Missile Salvo"
	live._apply_missile_salvo(Vector2i(39,27))
	assert(live.player_units[0].ap==3,"AOE cannot bypass its displayed range or spend AP on an invalid target")
	live.selected_action="Grenade";live.enemy_units[0].position=Vector2i(10,5);live.enemy_units[0].hp=100
	live._apply_missile_salvo(Vector2i(10,5))
	assert(live.player_units[0].ap==1 and live.enemy_units[0].hp==92,"AOE uses the selected weapon damage rather than hardcoded missile stats")
	DirAccess.remove_absolute(live.handoff_path)
	live.queue_free();await process_frame
	print("WEAPON_BALANCE_CHECKS_PASSED")
	quit()
