extends SceneTree
const KEYS=["agent_psi","agent_diverse_01_neon_blade","agent_diverse_02_longcoat_gunner","agent_diverse_03_magenta_pistol","agent_diverse_04_trench_sniper","agent_diverse_05_psi_doctor","agent_diverse_06_street_medic","agent_diverse_07_hooded_infiltrator","agent_diverse_08_holo_hacker","agent_diverse_09_blue_mohawk_scout","agent_diverse_10_ronin_duelist","agent_diverse_11_rail_sniper","agent_diverse_12_violet_fixer","agent_diverse_13_silver_pistol","agent_diverse_14_armored_vanguard","agent_diverse_15_chrome_medic","agent_diverse_16_heavy_breacher","agent_diverse_17_yellow_strike","agent_diverse_18_red_enforcer","agent_diverse_19_drone_handler","agent_diverse_20_cyber_doc","agent_diverse_21_twin_blade_adept","agent_diverse_22_veteran_inquisitor","agent_diverse_23_dreadlock_rifle","agent_diverse_24_hooded_psion","agent_diverse_25_redline_runner","enemy_grunt","enemy_corp_37_power_armor_grunt","robot_combat"]
func _initialize() -> void:call_deferred("run")
func run() -> void:
	root.size=Vector2i(640,480)
	var base:=ProjectSettings.globalize_path("res://../..")
	var keys: Array=KEYS + ["agent_samurai", "enemy_commander", "enemy_sniper", "enemy_heavy", "enemy_elite", "enemy_psi", "enemy_corp_37_grunt", "enemy_corp_37_robot_grunt", "enemy_corp_37_robot_heavy", "enemy_corp_37_robot_elite", "enemy_corp_37_robot_commander", "enemy_corp_37_power_armor_heavy", "enemy_corp_37_power_armor_elite", "enemy_corp_37_power_armor_commander", "enemy_corp_37_heavy", "enemy_corp_37_elite", "enemy_corp_37_commander", "enemy_corp_samurai_grunt", "enemy_corp_samurai_heavy", "enemy_corp_samurai_elite", "enemy_corp_samurai_commander"]
	var args:=OS.get_cmdline_user_args()
	for i in range(args.size()-1):
		if args[i]=="--asset":
			assert(args[i+1] in keys,"unknown animation asset")
			keys=[args[i+1]]
	var unit=load("res://scripts/unit_visual.gd").new();root.add_child(unit)
	unit.position=Vector2(320,350);unit.facing_y_scale=1.0;unit.set_process(false)
	var observed:=0
	for key: String in keys:
		var image:=Image.load_from_file(base.path_join("assets/units/"+key+"_512.png"))
		var role: String="robot" if key=="robot_combat" else ("power_armor" if "power_armor" in key else ("psi" if "psi_doctor" in key else "samurai"))
		unit.setup({"hp":24,"max_hp":24,"role":role,"position":Vector2i(4,4)},0,false,ImageTexture.create_from_image(image),Vector2(150,150))
		unit.configure_animation(key,base)
		assert(unit.atlas!=null and unit.manifest.animations.has("move"),key+" real atlas loaded")
		var before:=JSON.stringify(unit.unit_data)
		var source_height: float=unit._body_height()
		for direction in range(8):
			unit.play_action("idle")
			var angle: float=direction*TAU/8
			assert(unit.play_action("move",unit.position+Vector2(cos(angle),sin(angle))*100))
			assert(unit.facing==direction,"top-down facings must match the requested heading")
			unit.frame_time=.27
			assert(unit.play_action("move",unit.position+Vector2(cos(angle),sin(angle))*200))
			assert(is_equal_approx(unit.frame_time,.27),"a new route cell must not restart the gait")
			for frame in range(4):
				unit.frame_time=(frame+.1)/8.0;unit._process(0)
				await process_frame;await RenderingServer.frame_post_draw
				assert(unit.frame_index==frame)
				assert(unit._art_sprite.texture==unit.atlas)
				assert(unit._cast_shadow.region_rect==unit._art_sprite.region_rect)
				assert(is_equal_approx(unit._art_sprite.scale.x,unit._art_sprite.scale.y),"no stretching")
				assert(is_equal_approx(unit._body_height(),source_height))
				assert(is_equal_approx(unit._art_rect.position.x,-unit._art_rect.size.x*.5),"authored foot anchor remains registered")
				observed+=1
		unit.play_action("idle")
		if unit.manifest.animations.has("fire"):
			for direction in range(8):
				unit.facing=direction;assert(unit.play_action("fire"));unit.frame_time=0.2;unit._process(0.0)
				assert(unit.frame_index==1,"pistol recoil frame must be selected")
		else:
			assert(not unit.play_action("fire"))
			assert(unit.clip=="idle","missing fire is not disguised as an animated shot")
		assert(JSON.stringify(unit.unit_data)==before,"animation cannot spend AP or move logical cells")
		for action in ["melee","cover","hit","death","psi","heal"]:
			if unit.manifest.animations.has(action):
				for direction in range(8):
					unit.facing=direction;assert(unit.play_action(action));unit.frame_time=0.2;unit._process(0.0)
					assert(unit.frame_index==1,action+" follow-through frame must be selected")
	# A missing asset must restore source art, not leave the previous atlas attached.
	unit.configure_animation("missing_animation_fixture",base)
	assert(unit.atlas==null and unit.manifest.is_empty())
	# Reject malformed frame indices before the draw loop can access them.
	var contract=load("res://scripts/unit_animation_contract.gd")
	assert(not contract.valid({"frame_size":[0,256]},Image.create(256,256,false,Image.FORMAT_RGBA8),base))
	print("DIRECTIONAL_ANIMATION_CHECKS_PASSED ",observed," actual frame selections")
	quit()
