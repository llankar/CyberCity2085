extends SceneTree
func _initialize() -> void:
	var profile=load("res://scripts/unit_presentation.gd")
	var fixtures: Array[Dictionary]=[
		{"role":"samurai","size_scale":1.0},
		{"role":"psi","size_scale":1.1},
		{"role":"power_armor","size_scale":3.5},
		{"role":"robot","asset_type":"combat_robot","size_scale":3.5},
		{"enemy_theme":"corp_37_robot","size_scale":1.0},
		{"role":"robot","size_scale":3.5,"is_giant":true},
		{"vehicle_key":"vehicle_agent_vtol","size_scale":3.5},
		{"vehicle_key":"vehicle_enemy_corp_samurai","size_scale":5.0,"is_giant":true},
	]
	var expected: Array[float]=[1.0,1.1,1.15,1.65,1.0,3.5,3.5,3.5]
	var state:=JSON.stringify(fixtures)
	for i in range(fixtures.size()):
		assert(is_equal_approx(profile.body_scale(fixtures[i],""),expected[i]))
		var projection: Vector2=profile.shadow_projection(fixtures[i],"")
		assert(projection.y<0 and profile.shadow_opacity(fixtures[i],"")>0)
	assert(profile.is_aircraft(fixtures[6],"vehicle_aerial_military_01_vtol_gunship"))
	assert(not profile.is_aircraft(fixtures[7],"vehicle_terrestrial_military_01_battle_tank"))
	assert(profile.shadow_projection(fixtures[6],"")!=profile.shadow_projection(fixtures[0],""))
	assert(profile.shadow_opacity(fixtures[6],"")<profile.shadow_opacity(fixtures[7],""))
	assert(is_equal_approx(profile.body_scale({"size_scale":3.5},"enemy_corp_37_robot_grunt"),1.65))
	assert(profile.contact_half_width(fixtures[7],"",200.0,10.0)>60.0,"ground vehicle shadow spans its chassis")
	assert(profile.contact_half_width(fixtures[6],"",200.0,10.0)==10.0,"aircraft cannot acquire a chassis contact disc")
	assert(JSON.stringify(fixtures)==state,"presentation cannot mutate combat data")
	print("UNIT_PRESENTATION_CHECKS_PASSED")
	quit()
