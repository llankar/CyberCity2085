extends Node3D
## Independent scale-review stage. External files remain outside the game runtime.

var camera: Camera3D
var hud: Label
var subjects: Array[Node3D] = []
var selected := 0
var yaw := 0.65
var elevation := 0.6
var target := Vector3(0, 1.0, 0)
var orbiting := false
var orbit_mode := false
var clip_status := "Human: static fitting model; action clips unavailable"
var human_height := 1.718
var robot_height := 2.4
var vehicle_actor: Node3D
var sidearm_modules
var human_weapon: Node3D
var human_embedded_weapon: Array[MeshInstance3D] = []
var first_process_usec := 0
var generated_overlay
var human_sprite_reference: TextureRect
var human_sprite_caption: Label

func subject_height(subject: Node3D) -> float:
	var bounds := AABB()
	var first := true
	var probe := preload("res://skin_motion_check.gd").new()
	for mesh in subject.find_children("*", "MeshInstance3D", true, false):
		if not mesh.is_visible_in_tree(): continue
		if mesh.skin != null and mesh.get_node_or_null(mesh.skeleton) is Skeleton3D:
			var skeleton := mesh.get_node(mesh.skeleton) as Skeleton3D
			skeleton.force_update_all_bone_transforms()
			# Skin bind matrices can cancel FBX node scale/rotation. Mesh global
			# transform alone is not the rendered position of a skinned vertex.
			for point in probe.skinned_points(mesh, skeleton, 1, true):
				bounds = AABB(point, Vector3.ZERO) if first else bounds.expand(point)
				first = false
			continue
		# Mesh AABBs include the union of possible morph displacements, which is
		# not the actor's reference height and changes when clips are bundled.
		for surface in range(mesh.mesh.get_surface_count()):
			var vertices: PackedVector3Array = mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
			for vertex in vertices:
				var point: Vector3 = mesh.global_transform * vertex
				bounds = AABB(point, Vector3.ZERO) if first else bounds.expand(point)
				first = false
	probe.free()
	assert(not first and bounds.size.y > 0.5)
	return bounds.size.y

func load_subject(path: String, position_value: Vector3) -> bool:
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	if document.append_from_file(path, state) != OK:
		push_error("Missing comparison subject: " + path)
		return false
	# Rest-valued tracks reset prior action poses and must survive import.
	var authored_human := path.ends_with("unvanquished_motion01/human_actions.glb") or path.ends_with("scanned_armor_head01/human_actions.glb") or path.ends_with("scanned_armor_hair01/human_actions.glb") or path.ends_with("scanned_armor_shoot01/human_actions.glb") or path.ends_with("scanned_armor_contact01/human_actions.glb")
	var import_fps := 24 if path.ends_with("rook_run129/human.glb") else (120 if authored_human or path.contains("/amjviz_actions146/") or path.contains("/amjviz_budget147_") or path.contains("/amjviz_hair148/") or path.contains("/amjviz_grip149/") or path.contains("/amjviz_wardrobe150/") else 30)
	var subject := document.generate_scene(state, import_fps, false, false)
	add_child(subject)
	if "--nathan-eyes-study" in OS.get_cmdline_user_args() and path.ends_with("nathan_eyes01/human.glb"):
		var coats := preload("res://uniform_clearcoat.gd").new().apply_uniform_coats(state,subject)
		assert(coats.size()==1)
		print("NATHAN_EYE_COAT_STAGE_APPLIED")
	subject.position = position_value
	subjects.append(subject)
	for mesh in subject.find_children("*", "MeshInstance3D", true, false):
		for index in range(mesh.mesh.get_surface_count()):
			var material = mesh.get_active_material(index)
			if material is StandardMaterial3D:
				var copy := material.duplicate() as StandardMaterial3D
				copy.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
				for slot in [BaseMaterial3D.TEXTURE_ALBEDO, BaseMaterial3D.TEXTURE_NORMAL]:
					var texture := copy.get_texture(slot)
					if texture:
						var pixels := texture.get_image()
						if pixels and not pixels.has_mipmaps():
							pixels.generate_mipmaps(slot == BaseMaterial3D.TEXTURE_NORMAL)
							copy.set_texture(slot, ImageTexture.create_from_image(pixels))
				mesh.set_surface_override_material(index, copy)
	return true

func _ready() -> void:
	var generated_review := "--generated-atlas-review" in OS.get_cmdline_user_args()
	var current_atlas_review := "--wardrobe-atlas-review" in OS.get_cmdline_user_args()
	assert(not(current_atlas_review and generated_review),"Choose the atlas for the actual source")
	if current_atlas_review:assert("--sprite-review" in OS.get_cmdline_user_args())
	var texture_budget := "--texture-budget-study" in OS.get_cmdline_user_args()
	var hair_study := "--hair-study" in OS.get_cmdline_user_args()
	var support_study := "--support-study" in OS.get_cmdline_user_args()
	var motion_study := "--motion-extension159" in OS.get_cmdline_user_args()
	assert(not motion_study or not (current_atlas_review or generated_review),"New motions have no matching atlas")
	var current_budget := "--wardrobe-budget154" in OS.get_cmdline_user_args()
	assert(not current_budget or not current_atlas_review,"Budget variant requires separate atlas review")
	var modular_study := "--modular-equipment-study" in OS.get_cmdline_user_args()
	assert(not modular_study or (not motion_study and not current_budget and not current_atlas_review and not generated_review), "Module study has no matching rendered atlas")
	var wardrobe150_study := motion_study or current_budget or modular_study or "--wardrobe150-study" in OS.get_cmdline_user_args() or current_atlas_review
	assert(int(texture_budget)+int(hair_study)+int(support_study)+int(wardrobe150_study)<=1,"Choose one private human variant")
	var amjviz_combat := "--amjviz-combat-study" in OS.get_cmdline_user_args() or texture_budget or hair_study or support_study or wardrobe150_study
	var amjviz_pruned := "--amjviz-pruned-study" in OS.get_cmdline_user_args() or amjviz_combat
	var amjviz_study := "--amjviz-study" in OS.get_cmdline_user_args() or amjviz_pruned
	assert(not(amjviz_study and generated_review), "Atlas129 is not the AmJViZ character")
	var jacket_study := "--authored-jacket-study" in OS.get_cmdline_user_args()
	var pouch_study := "--pouch-study" in OS.get_cmdline_user_args() or jacket_study
	var skin_normal_study := "--skin-normal-study" in OS.get_cmdline_user_args() or pouch_study
	var single_neck_study := "--single-neck-study" in OS.get_cmdline_user_args() or skin_normal_study
	var undercut_study := "--undercut-study" in OS.get_cmdline_user_args() or single_neck_study
	assert(not(generated_review and undercut_study),"Generated atlas129 does not represent candidate133/138/139/140/141; rerender before synchronized comparison")
	if generated_review:
		assert("--sprite-review" in OS.get_cmdline_user_args())
		yaw=PI/4
	if "--msaa4" in OS.get_cmdline_user_args(): get_viewport().msaa_3d = Viewport.MSAA_4X
	if "--sprite-review" in OS.get_cmdline_user_args():
		get_window().content_scale_size = Vector2i(1920, 1080)
		get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
		await get_tree().process_frame
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/"
	var run_study := "--run-clearance-study" in OS.get_cmdline_user_args() or generated_review or undercut_study
	var neck_study := "--neck-uv-study" in OS.get_cmdline_user_args() or run_study
	var quiff_study := "--quiff-study" in OS.get_cmdline_user_args() or neck_study
	var head_fit_study := "--head-fit-study" in OS.get_cmdline_user_args() or quiff_study
	var rook_study := "--rook-material-study" in OS.get_cmdline_user_args() or head_fit_study
	var cyborg_actions := "--cyborg-actions-study" in OS.get_cmdline_user_args() or rook_study
	var cyborg_fire := "--cyborg-fire-study" in OS.get_cmdline_user_args() or cyborg_actions
	var cyborg_pistol := "--cyborg-pistol-study" in OS.get_cmdline_user_args() or cyborg_fire
	var cyborg_lod := "--grab3d-cyborg-lod" in OS.get_cmdline_user_args() or cyborg_pistol
	var cyborg_study := "--grab3d-cyborg-study" in OS.get_cmdline_user_args() or cyborg_lod
	var nathan_study := "--nathan-study" in OS.get_cmdline_user_args() or "--nathan-eyes-study" in OS.get_cmdline_user_args()
	var contact := "--contact-study" in OS.get_cmdline_user_args()
	var scanned_shoot := "--scanned-shoot-study" in OS.get_cmdline_user_args() or contact
	var scanned_hair := "--scanned-hair-study" in OS.get_cmdline_user_args() or scanned_shoot
	var scanned_head := "--scanned-head-study" in OS.get_cmdline_user_args() or scanned_hair
	var unvanquished_motion := "--unvanquished-motion-study" in OS.get_cmdline_user_args() or scanned_head
	var unvanquished_study := "--unvanquished-study" in OS.get_cmdline_user_args() or unvanquished_motion
	var human_file := "authored_outfit_realtime.glb" if "--realtime" in OS.get_cmdline_user_args() else "authored_outfit.glb"
	var wardrobe_study := "--wardrobe-study" in OS.get_cmdline_user_args()
	var head_study := "--rocketbox-head-study" in OS.get_cmdline_user_args() or wardrobe_study
	var rocketbox_motion := "--rocketbox-motion-study" in OS.get_cmdline_user_args() or head_study
	var rocketbox := "--rocketbox-study" in OS.get_cmdline_user_args() or rocketbox_motion
	var charge := "--charge" in OS.get_cmdline_user_args() or rocketbox or nathan_study or unvanquished_study or cyborg_study or amjviz_study
	var human_path := root + "einar_pbr01/human_pbr.glb" if charge else root + "authored_tactical01/" + human_file
	var bundled_human := charge and "--human-bundle-study" in OS.get_cmdline_user_args()
	var rigged_human := charge and ("--rigged-human" in OS.get_cmdline_user_args() or bundled_human)
	if rigged_human: human_path = root + "einar_motion01/human_motion.glb"
	if bundled_human: human_path = root + "einar_bundle02/human_actions.glb"
	var action_human := charge and "--human-action-study" in OS.get_cmdline_user_args()
	assert(not (bundled_human and action_human), "Choose one human study")
	if action_human: human_path = root + "einar_pistol_fit01_surfaces/human_pistol.glb"
	if rocketbox:
		assert(not rigged_human and not action_human, "Choose one human source")
		human_path = root + "rocketbox_military03/character_dielectric.glb"
		if rocketbox_motion:
			human_path = root + "rocketbox_military03/motion01/human_motion.glb"
			rigged_human = true
	if head_study: human_path = root + "rocketbox_hair08/character01/human.glb"
	if wardrobe_study: human_path = root + "wardrobe_fit01/human.glb"
	if nathan_study:
		assert(not rocketbox and not rigged_human and not action_human, "Choose one human source")
		human_path = root + ("nathan_eyes01/human.glb" if "--nathan-eyes-study" in OS.get_cmdline_user_args() else "renderpeople_nathan01/human.glb")
		rigged_human = true
	if unvanquished_study:
		assert(not rocketbox and not rigged_human and not action_human and not nathan_study, "Choose one human source")
		human_path = root + "unvanquished_human01/human_armor.glb"
		if unvanquished_motion:
			human_path = root + "unvanquished_motion01/human_actions.glb"
			rigged_human = true
		if scanned_head:human_path=root+"scanned_armor_head01/human_actions.glb"
		if scanned_hair:human_path=root+"scanned_armor_hair01/human_actions.glb"
		if scanned_shoot:human_path=root+"scanned_armor_shoot01/human_actions.glb"
		if contact:human_path=root+"scanned_armor_contact01/human_actions.glb"
	if cyborg_study:
		assert(not rocketbox and not nathan_study and not unvanquished_study and not rigged_human and not action_human, "Choose one human source")
		human_path = root + "grab3d_cyborg01/human.glb"
		if cyborg_lod: human_path = root + "grab3d_cyborg_lod01/human.glb"
		if cyborg_pistol: human_path = root + "cyborg_pistol01/human.glb"
		if cyborg_fire: human_path = root + "cyborg_fire01/human.glb"
		if cyborg_actions: human_path = root + "cyborg_actions01/human.glb"
		if rook_study: human_path = root + "rook_material01/human.glb"
		if head_fit_study: human_path = root + "rook_head_fit126/human.glb"
		if quiff_study: human_path = root + "rook_hair127/human.glb"
		if neck_study: human_path = root + "rook_neck_uv128/human.glb"
		if run_study: human_path = root + "rook_run129/human.glb"
		if undercut_study: human_path = root + "rook_undercut133/human.glb"
		if single_neck_study: human_path = root + "rook_single_neck138/human.glb"
		if skin_normal_study: human_path = root + "rook_normal_strength139/human.glb"
		if pouch_study: human_path = root + "rook_pouches140/human.glb"
		if jacket_study: human_path = root + "rook_diesel_replacement141/human.glb"
	if amjviz_study:
		assert(not(rocketbox or nathan_study or unvanquished_study or cyborg_study or bundled_human or action_human), "Choose one human source")
		human_path = "E:/CyberCity2085-3d-lab/sources/blenderkit_cyberpunk143/source_godot.glb"
		if amjviz_pruned:human_path=root+"amjviz_pruned145/human.glb"
		if amjviz_combat:human_path=root+"amjviz_actions146/human_actions.glb"
		if texture_budget:human_path=root+"amjviz_budget147_1024/human_actions.glb"
		if hair_study:human_path=root+"amjviz_hair148/human.glb"
		if support_study:human_path=root+"amjviz_grip149/human_actions.glb"
		if wardrobe150_study:human_path=root+"amjviz_wardrobe150/human_actions.glb"
		if current_budget:human_path=root+"amjviz_budget154_1024/human_actions.glb"
		if motion_study:human_path=root+"motion_extension159/human.glb"
		rigged_human = true
	var robot_path := root + "security_pbr_robot01/robot_pbr.glb" if charge else root + "george_tactical/george_tactical.glb"
	var robot_idle := charge and "--robot-idle-study" in OS.get_cmdline_user_args()
	var robot_walk := charge and "--robot-walk-study" in OS.get_cmdline_user_args()
	var robot_melee := charge and "--robot-melee-study" in OS.get_cmdline_user_args()
	var robot_hit := charge and "--robot-hit-study" in OS.get_cmdline_user_args()
	var robot_shutdown := charge and "--robot-shutdown-study" in OS.get_cmdline_user_args()
	var robot_bundle := charge and "--robot-action-bundle" in OS.get_cmdline_user_args()
	assert(int(robot_idle)+int(robot_walk)+int(robot_melee)+int(robot_hit)+int(robot_shutdown)+int(robot_bundle) <= 1, "Choose one mechanical action study")
	if robot_idle: robot_path = root + "security_idle01/robot_idle.glb"
	if robot_walk: robot_path = root + "security_walk01/robot_walk.glb"
	if robot_melee: robot_path = root + "security_melee01/robot_melee.glb"
	if robot_hit: robot_path = root + "security_hit01/robot_hit.glb"
	if robot_shutdown: robot_path = root + "security_death01/robot_death.glb"
	if robot_bundle: robot_path = root + "security_bundle01/robot_actions.glb"
	if robot_bundle and "--compact-robot-study" in OS.get_cmdline_user_args():
		robot_path = root + "security_compact134/robot_actions.glb"
	if robot_bundle and "--source-opacity-study" in OS.get_cmdline_user_args():
		robot_path = root + "security_opaque137/robot_actions.glb"
	if not load_subject(human_path, Vector3(-1.6, 0, 0)):
		get_tree().quit(2)
		return
	if not load_subject(robot_path, Vector3(1.6, 0, 0)):
		get_tree().quit(2)
		return
	if skin_normal_study:
		var skin_surfaces := 0
		for mesh in subjects[0].find_children("*", "MeshInstance3D", true, false):
			for surface in range(mesh.mesh.get_surface_count()):
				var mat := mesh.get_active_material(surface) as StandardMaterial3D
				if mat and mat.resource_name == "sm004_head":
					assert(mat.normal_enabled and mat.normal_texture != null)
					assert(absf(mat.normal_scale - .35) < .000001)
					assert(mat.normal_texture.get_size() == Vector2(2048, 2048))
					skin_surfaces += 1
		assert(skin_surfaces == 1)
		var skin_proof := FileAccess.open(human_path.get_base_dir() + "/native_skin_material.json", FileAccess.WRITE)
		skin_proof.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(human_path),"normal_scale":.35,"original_normal_texture_dimensions":[2048,2048],"matched_surfaces":skin_surfaces,"scope":"Actual imported skin material; not final artistic approval"},"  "))
		print("ORIGINAL_SKIN_NORMAL_NATIVE_SCALE_OK scale=0.35 surfaces=1")
	if cyborg_study: subjects[0].set_meta("action_aliases", {"Walk":"walk", "Run":"run"})
	if cyborg_pistol: subjects[0].set_meta("action_aliases", {"Walk":"walk", "Run":"run", "Idle":"CombatReadyStudy"})
	if cyborg_fire: subjects[0].set_meta("action_aliases", {"Walk":"walk", "Run":"run", "Idle":"CombatReadyStudy", "Shoot":"PistolFireStudy"})
	if cyborg_actions: subjects[0].set_meta("action_aliases", {"Walk":"walk", "Run":"run", "Idle":"CombatReadyStudy", "Shoot":"PistolFireStudy", "Melee":"MeleeStudy", "Death":"DeathStudy"})
	if amjviz_study: subjects[0].set_meta("action_aliases", {"Walk":"Walk (1_24)", "Run":"Run (1_18)", "Idle":"Hard stand"})
	if amjviz_combat:
		subjects[0].set_meta("action_aliases", {"Walk":"Walk (1_24)","Run":"Run (1_18)","Idle":"Hard stand","Shoot":"ShootStudy","Melee":"MeleeStudy","Death":"DeathStudy"})
		for mesh in subjects[0].find_children("*","MeshInstance3D",true,false):
			if str(mesh.name).begins_with("EquippedPistol_"):
				human_embedded_weapon.append(mesh)
				mesh.visible=false
		assert(human_embedded_weapon.size()==9)
	if motion_study:
		var extended_aliases:Dictionary=subjects[0].get_meta("action_aliases")
		extended_aliases.merge({"Hit":"HitStudy","Cover":"CoverStudy"})
		subjects[0].set_meta("action_aliases",extended_aliases)
	if modular_study:
		sidearm_modules = preload("res://equipment_modules153.gd").new()
		sidearm_modules.configure(subjects[0], root+"amjviz_wardrobe150/human_actions.glb")
	if robot_walk or robot_bundle: subjects[1].set_meta("forward_motion_study", true)
	if nathan_study: subjects[0].set_meta("forward_motion_study", true)
	if bundled_human:
		human_weapon = preload("res://pistol_attachment.gd").attach(subjects[0])
		human_weapon.visible = false
	if rocketbox_motion:
		human_weapon = preload("res://rocketbox_pistol_attachment.gd").attach(subjects[0])
		human_weapon.visible = false
	if scanned_shoot:
		human_weapon = preload("res://rocketbox_pistol_attachment.gd").attach(subjects[0],true,contact)
		human_weapon.visible = false
	if "--authored-groom" in OS.get_cmdline_user_args():
		assert(bundled_human, "Authored groom study requires the shared character rig")
		preload("res://groom_attachment.gd").attach(subjects[0], "einar_groom02_layered_lod")
	if charge:
		human_height = subject_height(subjects[0])
		robot_height = subject_height(subjects[1])
		print("CHARGE_STATIC_SUBJECTS_LOADED human_height=", human_height, " robot_height=", robot_height)
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(0.18, 0.18, 0.18)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color.WHITE
	world.environment.ambient_light_energy = 0.4
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 1.0
	sun.shadow_enabled = true
	add_child(sun)
	for x in range(-4, 5):
		for z in range(-3, 4):
			if "--tactical" in OS.get_cmdline_user_args():
				continue
			var tile := MeshInstance3D.new()
			var box := BoxMesh.new()
			box.size = Vector3(0.98, 0.04, 0.98)
			tile.mesh = box
			tile.position = Vector3(x, -0.035, z)
			var material := StandardMaterial3D.new()
			material.albedo_color = Color(0.23, 0.23, 0.23) if (x + z) % 2 == 0 else Color(0.28, 0.28, 0.28)
			material.roughness = 0.9
			tile.material_override = material
			add_child(tile)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 7.8
	add_child(camera)
	if "--tactical" in OS.get_cmdline_user_args():
		load_tactical_map()
		camera.size = 22
		target = Vector3(0, 1, 2)
	update_camera()
	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(20, 16)
	hud.add_theme_font_size_override("font_size", 19)
	layer.add_child(hud)
	if "--sprite-review" in OS.get_cmdline_user_args():
		setup_sprite_review(layer)
	if generated_review or current_atlas_review:
		generated_overlay=preload("res://generated_atlas_comparison.gd").new()
		layer.add_child(generated_overlay)
		generated_overlay.configure(camera,subjects[0],human_sprite_reference,human_sprite_caption,1.8 if current_atlas_review else human_height,current_atlas_review)
	selected = 1
	play_clip("Idle")
	if robot_idle:
		var idle_player := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		assert(idle_player.current_animation == "Idle")
		print("CHARGE_ROBOT_IDLE_DISPATCH_OK")
	selected = 0
	clip_status = "Human: static fitting model; action clips unavailable"
	if rigged_human: play_clip("Walk" if nathan_study else "Idle")
	if action_human: play_clip("Shoot")
	if cyborg_study: clip_status = "Human: source walk/run available; other actions unavailable"
	print("COMPARISON_STAGE_LOADED subjects=", subjects.size(), " tile_width_m=1")
	if modular_study:
		selected=0
		play_clip("Shoot")
		var swap_key:=InputEventKey.new()
		swap_key.pressed=true
		swap_key.keycode=KEY_E
		_unhandled_input(swap_key)
		assert(sidearm_modules.selected=="p320")
		selected=1
		_unhandled_input(swap_key)
		assert(sidearm_modules.selected=="p320")
		selected=0
		_unhandled_input(swap_key)
		assert(sidearm_modules.selected=="firewarden")
		print("MODULE_STAGE_INPUT153_PASS human_swap,robot_guard,restore")
	if motion_study:
		selected=0
		var extension_key:=InputEventKey.new();extension_key.pressed=true
		for entry in [[KEY_6,"HitStudy"],[KEY_K,"CoverStudy"]]:
			extension_key.keycode=entry[0];_unhandled_input(extension_key)
			assert(subjects[0].find_children("*","AnimationPlayer",true,false)[0].current_animation==entry[1])
		play_clip("Idle")
		print("MOTION159_STAGE_KEYS_PASS hit,cover,idle")
	if "--self-test" in OS.get_cmdline_user_args():
		if vehicle_actor != null:
			for entry in [[KEY_8,"Gear_Retract"],[KEY_9,"Gear_Extend"],[KEY_7,"Rotor_Spin"]]:
				var vehicle_key := InputEventKey.new()
				vehicle_key.pressed = true
				vehicle_key.keycode = entry[0]
				_unhandled_input(vehicle_key)
				assert(vehicle_actor.find_children("*","AnimationPlayer",true,false)[0].current_animation == entry[1])
			print("VTOL_STAGE_ACTION_KEYS_OK rotor,retract,extend")
		var key := InputEventKey.new()
		key.pressed = true
		key.keycode = KEY_TAB
		_unhandled_input(key)
		assert(selected == 1)
		key.keycode = KEY_2
		_unhandled_input(key)
		if robot_bundle:
			verify_robot_forward_walk()
			var mechanics := preload("res://mechanical_action_check.gd").new()
			mechanics.verify_strike(subjects[1])
			assert(mechanics.verify_hit(subjects[1]).size() == 5)
			assert(mechanics.verify_shutdown(subjects[1]).has("height_initial_m"))
			play_clip("Shoot")
			assert("unavailable" in clip_status)
		elif robot_shutdown:
			assert("unavailable" in clip_status)
			var shutdown_check := preload("res://mechanical_action_check.gd").new().verify_shutdown(subjects[1])
			assert(shutdown_check.has("height_initial_m"))
		elif robot_hit:
			assert("unavailable" in clip_status)
			var hit_evidence := preload("res://mechanical_action_check.gd").new().verify_hit(subjects[1])
			assert(hit_evidence.size() == 5)
		elif robot_melee:
			assert("unavailable" in clip_status)
			preload("res://mechanical_action_check.gd").new().verify_strike(subjects[1])
		elif robot_walk:
			verify_robot_forward_walk()
		elif charge:
			assert("unavailable" in clip_status)
			var robot_players := subjects[1].find_children("*", "AnimationPlayer", true, false)
			if robot_idle:
				assert(robot_players.size() == 1 and robot_players[0].has_animation("Idle"))
			else: assert(robot_players.is_empty())
		else:
			var player := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(player.current_animation == "Walk")
		key.keycode = KEY_C
		_unhandled_input(key)
		assert(orbit_mode)
		_unhandled_input(key)
		assert(not orbit_mode)
		key.keycode = KEY_TAB
		_unhandled_input(key)
		assert(selected == 0)
		play_clip("Walk")
		if rigged_human:
			var walking_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(walking_player.current_animation == ("Walk (1_24)" if amjviz_study else "Walk"))
			print("CHARGE_HUMAN_WALK_DISPATCH_OK")
			play_clip("Shoot")
		if action_human or bundled_human or rocketbox_motion:
			play_clip("Shoot")
			var action_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(action_player.current_animation == "Pistol_Shoot")
			if human_weapon: assert(human_weapon.visible)
			print("CHARGE_HUMAN_PISTOL_DISPATCH_OK")
		elif scanned_shoot:
			var shooting_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			assert(shooting_player.current_animation=="Shoot" and human_weapon.visible)
			play_clip("Walk")
			assert(not human_weapon.visible)
			play_clip("Shoot")
			assert(human_weapon.visible)
			print("SCANNED_SHOOT_PROP_DISPATCH_OK real_prop_visibility")
		elif amjviz_study:
			var authored_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			assert(authored_player.current_animation == ("ShootStudy" if amjviz_combat else "Walk (1_24)"))
			play_clip("Run")
			assert(authored_player.current_animation == "Run (1_18)")
			for requested in ["Shoot","Melee","Death"]:
				play_clip(requested)
				if amjviz_combat:
					assert(authored_player.current_animation==requested+"Study")
					for part in human_embedded_weapon:assert(part.visible==((requested=="Shoot") and sidearm_modules==null))
				else:assert("unavailable" in clip_status)
			print("AMJVIZ_COMBAT_DISPATCH_OK ready,walk,run,shoot,melee,death;weapon_visibility" if amjviz_combat else "AMJVIZ_SOURCE_DISPATCH_OK idle,walk,run;combat_unavailable")
		elif cyborg_study:
			var cyborg_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			assert(cyborg_player.current_animation=="walk")
			play_clip("Run")
			assert(cyborg_player.current_animation=="run")
			play_clip("Shoot")
			if cyborg_fire:assert(cyborg_player.current_animation=="PistolFireStudy")
			else:assert("unavailable" in clip_status)
			if cyborg_actions:
				play_clip("Melee")
				assert(cyborg_player.current_animation=="MeleeStudy")
				play_clip("Death")
				assert(cyborg_player.current_animation=="DeathStudy")
			if cyborg_pistol:
				play_clip("Idle")
				assert(cyborg_player.current_animation=="CombatReadyStudy")
				assert(cyborg_player.get_animation("CombatReadyStudy").loop_mode==Animation.LOOP_LINEAR)
			cyborg_player.stop()
			var cyborg_skeleton := subjects[0].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
			cyborg_skeleton.reset_bone_poses()
			cyborg_skeleton.force_update_all_bone_transforms()
			print("CYBORG_FIRE_ACTION_DISPATCH_OK walk,run,ready,fire" if cyborg_fire else "CYBORG_SOURCE_ACTION_DISPATCH_OK walk,run;shoot_unavailable")
			if cyborg_actions:print("CYBORG_SIX_ACTION_DISPATCH_OK ready,walk,run,fire,melee,death")
		else: assert("unavailable" in clip_status)
		if unvanquished_motion:
			var authored_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			for authored_clip in ["Run","Attack","Crouch","Death"]:
				play_clip(authored_clip)
				assert(authored_player.current_animation==authored_clip)
			assert(authored_player.get_animation_list().size()==(7 if scanned_shoot else 6))
			print("SCANNED_SEVEN_BODY_CLIPS_OK" if scanned_shoot else "UNV_SIX_AUTHORED_BODY_CLIPS_DISPATCH_OK no_fictitious_shoot_or_melee")
		if bundled_human or rocketbox_motion:
			var bundle_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			play_clip("Melee")
			assert(bundle_player.current_animation == "Punch_Cross")
			if human_weapon: assert(not human_weapon.visible)
			play_clip("Death")
			assert(bundle_player.current_animation == "Death01")
			if human_weapon: assert(not human_weapon.visible)
			print("CHARGE_HUMAN_FIVE_ACTION_DISPATCH_OK")
		selected = 1
		play_clip("Idle")
		selected = 0
		clip_status = "Human: static fitting model; action clips unavailable"
		if rigged_human:
			play_clip("Walk" if nathan_study else "Idle")
			var human_player := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
			assert(human_player.current_animation == ("Hard stand" if amjviz_study else ("Walk" if nathan_study else "Idle")))
			if nathan_study:
				assert(human_player.get_animation_list().size() == 1)
				assert(human_player.get_animation("Walk").loop_mode == Animation.LOOP_NONE)
				print("NATHAN_AUTHORED_WALK_ONLY_OK no_fictitious_idle_or_combat_actions")
			else: print("CHARGE_HUMAN_IDLE_DISPATCH_OK")
		if action_human: play_clip("Shoot")
		print("COMPARISON_INPUT_TEST_OK selection,camera_mode,explicit_action_availability robot_clip=", "Idle/Walk/Melee/Hit/Death" if robot_bundle else ("Death" if robot_shutdown else ("Hit" if robot_hit else ("Melee" if robot_melee else ("Walk_nonloop" if robot_walk else ("unavailable" if charge else "Walk"))))))
	if rigged_human and "--walk-preview" in OS.get_cmdline_user_args(): play_clip("Walk")
	if amjviz_combat:
		var preview_actions:Array=["Shoot","Melee","Death"]
		if motion_study:preview_actions.append_array(["Cover","Hit"])
		for requested in preview_actions:
			var flag := {"Shoot":"--shoot-preview","Melee":"--melee-preview","Death":"--death-preview","Cover":"--cover-preview","Hit":"--hit-preview"}
			if flag[requested] in OS.get_cmdline_user_args():
				play_clip(requested)
				var preview := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
				preview.seek(preview.current_animation_length*(1.0 if requested=="Death" else .5),true);preview.pause()
	if cyborg_study:
		clip_status = "Human: reference pose; source walk/run available; no combat actions"
		if cyborg_pistol: play_clip("Idle")
		if "--walk-preview" in OS.get_cmdline_user_args(): play_clip("Walk")
		if cyborg_fire and "--shoot-preview" in OS.get_cmdline_user_args():
			play_clip("Shoot")
			var fire_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
			fire_player.seek(8.0/24,true)
			fire_player.pause()
		if cyborg_actions:
			for requested in ["Melee","Death"]:
				if ("--melee-preview" if requested=="Melee" else "--death-preview") in OS.get_cmdline_user_args():
					play_clip(requested)
					var preview_player := subjects[0].find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
					preview_player.seek(preview_player.current_animation_length*(.5 if requested=="Melee" else 1.),true)
					preview_player.pause()
	if rigged_human and "--shoot-preview" in OS.get_cmdline_user_args(): play_clip("Shoot")
	if robot_walk:
		selected = 1
		play_clip("Walk")
		var walker := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		# A reproducible pose for native sprite-scale review, not a seamless loop.
		walker.seek(0.96, true)
		walker.pause()
		selected = 0
		clip_status = "Human animation: Idle | Robot: paused forward Walk study"
	if robot_melee:
		selected = 1
		play_clip("Melee")
		var striker := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		striker.seek(0.5, true)
		striker.pause()
		selected = 0
		clip_status = "Human animation: Idle | Robot: paused open-hand strike study"
	if robot_hit:
		selected = 1
		play_clip("Hit")
		var struck := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		struck.seek(0.2, true)
		struck.pause()
		selected = 0
		clip_status = "Robot: paused planted Hit recoil study"
	if robot_shutdown:
		selected = 1
		play_clip("Death")
		var shutdown_player := subjects[1].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		shutdown_player.seek(2.0, true)
		shutdown_player.pause()
		selected = 0
		clip_status = "Robot: settled mechanical shutdown study"
	if nathan_study:
		selected = 0
		play_clip("Walk")
		var authored_walk := subjects[0].find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
		authored_walk.seek(authored_walk.get_animation("Walk").length * .5, true)
		authored_walk.pause()
		clip_status = "Human: source-authored Walk pose | no cyberpunk wardrobe or accepted Rook identity"
	if generated_review and "--self-test" in OS.get_cmdline_user_args():
		yaw=PI/4;elevation=.6;update_camera()
		preload("res://generated_atlas_sync_check.gd").new().run_checks(self,generated_overlay)
	if current_atlas_review and "--self-test" in OS.get_cmdline_user_args():
		yaw=PI/4;elevation=.6;update_camera()
		preload("res://wardrobe_atlas_sync_check.gd").new().run_checks(self,generated_overlay)
	if generated_review or current_atlas_review:
		var compare_action:=""
		var compare_time:=0.
		for argument in OS.get_cmdline_user_args():
			if argument.begins_with("--compare-action="):compare_action=argument.trim_prefix("--compare-action=")
			if argument.begins_with("--compare-time="):
				var value:=argument.trim_prefix("--compare-time=")
				assert(value.is_valid_float());compare_time=value.to_float()
		if not compare_action.is_empty():
			assert(generated_overlay.player.has_animation(compare_action))
			assert(is_finite(compare_time) and compare_time>=0 and compare_time<=generated_overlay.player.get_animation(compare_action).length)
			selected=0;play_clip(compare_action)
			generated_overlay.player.seek(compare_time,true);generated_overlay.player.pause();generated_overlay.refresh()
			print("GENERATED_ATLAS_FROZEN_COMPARISON ",JSON.stringify(generated_overlay.state))
			assert(compare_action.get_file()==compare_action)
			var snapshot: Dictionary=generated_overlay.state.duplicate()
			snapshot["model_glb_sha256"]=FileAccess.get_sha256(generated_overlay.model_path)
			snapshot["scope"]="Frozen animation/camera state; PNG capture result and artistic inspection are separate"
			var snapshot_file:=FileAccess.open(generated_overlay.folder+"frozen_"+compare_action.to_lower()+("_comparison152.json" if current_atlas_review else "_comparison131.json"),FileAccess.WRITE)
			assert(snapshot_file!=null);snapshot_file.store_string(JSON.stringify(snapshot,"  "));snapshot_file.close()
	# Let asset upload/shader setup settle before collecting timing evidence.
	for frame in range(30):
		await get_tree().process_frame
	var started := Time.get_ticks_usec()
	for frame in range(120):
		await get_tree().process_frame
	var elapsed := (Time.get_ticks_usec() - started) / 1000000.0
	print("COMPARISON_RENDER_TIMING frames=120 seconds=", elapsed, " average_fps=", 120.0 / elapsed)
	for argument in OS.get_cmdline_user_args():
		if not argument.begins_with("--benchmark-output="): continue
		var destination := argument.trim_prefix("--benchmark-output=")
		assert(destination.begins_with(root) and destination.ends_with(".json"))
		await get_tree().create_timer(1.0).timeout
		var begin := Time.get_ticks_usec()
		var begin_utc := Time.get_unix_time_from_system()
		print("COMPARISON_BENCHMARK_BEGIN unix_s=",begin_utc)
		var begin_drawn := Engine.get_frames_drawn()
		var samples: Array[float] = []
		var max_draw_calls := 0.0
		var max_video_bytes := 0.0
		var previous := begin
		while Time.get_ticks_usec() - begin < 5000000:
			await RenderingServer.frame_post_draw
			var now := Time.get_ticks_usec()
			samples.append((now - previous) / 1000.0)
			previous = now
			max_draw_calls = maxf(max_draw_calls, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
			max_video_bytes = maxf(max_video_bytes, Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED))
		var seconds := (Time.get_ticks_usec() - begin) / 1000000.0
		var drawn := Engine.get_frames_drawn() - begin_drawn
		assert(drawn > 0 and not samples.is_empty())
		samples.sort()
		var texture_size := get_viewport().get_texture().get_size()
		var evidence := {"window_size": [get_window().size.x, get_window().size.y], "render_texture_size": [texture_size.x, texture_size.y], "logical_viewport_size": [get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y], "seconds": seconds, "rendered_frames": drawn, "rendered_frames_per_s": drawn / seconds, "frame_post_draw_interval_p95_ms": samples[int((samples.size() - 1) * 0.95)], "max_draw_calls": max_draw_calls, "engine_reported_video_bytes": max_video_bytes, "scope": "Five-second native rendered-frame interval; no GPU execution timing, no full VRAM peak or production benchmark", "human": human_path, "robot": robot_path}
		evidence["begin_utc_unix_s"]=begin_utc
		evidence["end_utc_unix_s"]=Time.get_unix_time_from_system()
		evidence["human_glb_sha256"]=FileAccess.get_sha256(human_path)
		evidence["robot_glb_sha256"]=FileAccess.get_sha256(robot_path)
		if is_instance_valid(vehicle_actor) and vehicle_actor.has_meta("source_glb"):
			evidence["vehicle"]=vehicle_actor.get_meta("source_glb")
			evidence["vehicle_glb_sha256"]=FileAccess.get_sha256(evidence["vehicle"])
		evidence["arguments"]=Array(OS.get_cmdline_user_args())
		evidence["godot_version"]=Engine.get_version_info().string
		if "--facades-study" in OS.get_cmdline_user_args():evidence["facade_glb_sha256"]=FileAccess.get_sha256(root+"tactical_facades01/facades.glb")
		var output := FileAccess.open(destination, FileAccess.WRITE)
		assert(output != null)
		output.store_string(JSON.stringify(evidence, "  "))
		output.close()
		print("COMPARISON_NATIVE_BENCHMARK_OK ", JSON.stringify(evidence))
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--capture="):
			var path := argument.trim_prefix("--capture=")
			if not path.begins_with(root):
				get_tree().quit(3)
				return
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var result := get_viewport().get_texture().get_image().save_png(path)
			print("COMPARISON_CAPTURE ", result)
			get_tree().quit(0 if result == OK else 4)

func update_camera() -> void:
	camera.position = target + Vector3(sin(yaw) * cos(elevation), sin(elevation), cos(yaw) * cos(elevation)) * 50
	camera.look_at(target)

func setup_sprite_review(layer: CanvasLayer) -> void:
	var folder := "E:/CyberCity2085-3d-lab/sources/sprite_review/"
	var calibration = JSON.parse_string(FileAccess.get_file_as_string(folder + "calibration.json"))
	if not calibration is Dictionary or get_viewport().get_visible_rect().size != Vector2(1920, 1080):
		push_error("Sprite review requires prepared inputs and 1920x1080 viewport")
		get_tree().quit(6)
		return
	var body_px: float = calibration.close_human_px
	if "--overview" in OS.get_cmdline_user_args():
		body_px = calibration.overview_human_px
	var calibration_height:=1.8 if "--wardrobe-atlas-review" in OS.get_cmdline_user_args() else human_height
	var measured := absf(camera.unproject_position(Vector3(0, calibration_height, 0)).y - camera.unproject_position(Vector3.ZERO).y)
	camera.size *= measured / body_px
	var verified := absf(camera.unproject_position(Vector3(0, calibration_height, 0)).y - camera.unproject_position(Vector3.ZERO).y)
	assert(absf(verified - body_px) < 0.1)
	for index in range(2):
		var key: String = calibration.atlases[index].key
		var manifest = JSON.parse_string(FileAccess.get_file_as_string(folder + key + ".json"))
		var atlas := Image.load_from_file(folder + key + ".png")
		var frame_size := Vector2i(manifest.frame_size[0], manifest.frame_size[1])
		var frame_index_value: int = manifest.animations.idle.rows[1][0]
		var columns := atlas.get_width() / frame_size.x
		var frame := atlas.get_region(Rect2i(Vector2i(frame_index_value % columns, frame_index_value / columns) * frame_size, frame_size))
		var display_body := body_px * (1.0 if index == 0 else float(calibration.robot_sprite_multiplier))
		var display_size := Vector2(frame_size) * display_body / (frame_size.y * float(manifest.reference_height_uv))
		var foot := camera.unproject_position(subjects[index].position)
		var reference_foot := foot + Vector2(-95 if index == 0 else 95, 0)
		var picture := TextureRect.new()
		picture.texture = ImageTexture.create_from_image(frame)
		picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		picture.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		picture.size = display_size
		picture.position = reference_foot - Vector2(manifest.anchor_uv[0], manifest.anchor_uv[1]) * display_size
		layer.add_child(picture)
		if index==0 and ("--generated-atlas-review" in OS.get_cmdline_user_args() or "--wardrobe-atlas-review" in OS.get_cmdline_user_args()):
			human_sprite_reference=picture
			picture.set_meta("reference_manifest",manifest)
			picture.set_meta("reference_full_texture",ImageTexture.create_from_image(atlas))
		for entry in [[reference_foot, "Sprite 2D"], [foot, "Mesh 3D"]]:
			var caption := Label.new()
			caption.text = entry[1]
			caption.position = entry[0] + Vector2(-35, 12)
			caption.add_theme_font_size_override("font_size", 14)
			layer.add_child(caption)
			if index==0 and entry[1]=="Sprite 2D":human_sprite_caption=caption
	var note := Label.new()
	note.position = Vector2(20, 310 if "--vtol-motion-study" in OS.get_cmdline_user_args() else 270)
	note.text = "SPRITE REVIEW: default alley calibration | human reference %.3f px | robot sprite x1.65\n3D human projected height verified; robot actual height %.3f m\nSprite shader/rim/ground shadows are not reproduced in this review." % [body_px, robot_height]
	if "--wardrobe-atlas-review" in OS.get_cmdline_user_args():
		note.text="SPRITE REVIEW: physical1.8m reference %.3fpx | current hair height %.3fm retained\nOriginal sprite/3D/Blender atlas lighting differs; not pixel-identical art."%[body_px,human_height]
	layer.add_child(note)
	print("SPRITE_PIXEL_HEIGHT_VERIFIED expected=", body_px, " projected=", verified)

func load_tactical_map() -> void:
	subjects[0].position = Vector3(-1.5, 0, 1.5)
	subjects[1].position = Vector3(1.5, 0, 1.5)
	var folder := "E:/CyberCity2085-3d-lab/sources/tactical_map/"
	var name_value := "city_exterior_neon_market_alley"
	var data = JSON.parse_string(FileAccess.get_file_as_string(folder + name_value + ".walls.json"))
	if not data is Dictionary:
		push_error("Run prepare_tactical_inputs.py first")
		get_tree().quit(5)
		return
	var image := Image.load_from_file(folder + name_value + ".png")
	if image == null:
		get_tree().quit(5)
		return
	image.generate_mipmaps()
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(data.grid[0], data.grid[1])
	floor_mesh.mesh = plane
	floor_mesh.position.y = -0.03
	var asphalt := StandardMaterial3D.new()
	asphalt.albedo_texture = ImageTexture.create_from_image(image)
	asphalt.roughness = 0.95
	asphalt.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	floor_mesh.material_override = asphalt
	add_child(floor_mesh)
	var occupied: Dictionary = {}
	var batches: Dictionary = {true: [], false: []}
	for obstacle in data.walls:
		var tall: bool = "building" in obstacle.id
		for cell in obstacle.cells:
			var key := Vector2i(cell[0], cell[1])
			if occupied.has(key):
				continue
			occupied[key] = true
			var height := 3.0 if tall else 0.7
			batches[tall].append(Transform3D(Basis.IDENTITY, Vector3(cell[0] - data.grid[0] / 2.0 + 0.5, height / 2, cell[1] - data.grid[1] / 2.0 + 0.5)))
	var batch_instances := 0
	var facades := "--facades-study" in OS.get_cmdline_user_args()
	if facades:
		preload("res://tactical_facade_loader.gd").load_model(self,folder+name_value+".walls.json",occupied.size())
		batch_instances=occupied.size()
	for tall in ([] if facades else batches.keys()):
		var geometry := MultiMeshInstance3D.new()
		var block := BoxMesh.new()
		block.size = Vector3(1, 3.0 if tall else 0.7, 1)
		var instances := MultiMesh.new()
		instances.transform_format = MultiMesh.TRANSFORM_3D
		instances.mesh = block
		instances.instance_count = batches[tall].size()
		for index in range(instances.instance_count): instances.set_instance_transform(index, batches[tall][index])
		geometry.multimesh = instances
		var surface := StandardMaterial3D.new()
		surface.albedo_color = Color(0.12, 0.15, 0.17) if tall else Color(0.28, 0.29, 0.27)
		surface.roughness = 0.8
		geometry.material_override = surface
		add_child(geometry)
		batch_instances += instances.instance_count
	assert(batch_instances == occupied.size())
	if facades:print("TACTICAL_FACADE_STAGE_OK cells=",batch_instances)
	else:print("TACTICAL_OBSTACLE_BATCHES_OK instances=",batch_instances," batches=2")
	# No clear landing footprint exists on this alley: show the aircraft hovering.
	var animated_vehicle := "--vtol-motion-study" in OS.get_cmdline_user_args()
	var vehicle_path := "vtol_motion01/vtol_actions.glb" if animated_vehicle else "vtol01/vtol.glb"
	if animated_vehicle and "--vtol-finish-study" in OS.get_cmdline_user_args():
		vehicle_path = "vtol_finish135/vtol_actions.glb"
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/" + vehicle_path, Vector3(-6, 4, -4))
	if animated_vehicle:
		vehicle_actor = subjects[-1]
		vehicle_actor.set_meta("source_glb", "E:/CyberCity2085-3d-lab/generated/phase2/" + vehicle_path)
		play_vehicle_clip("Rotor_Spin")
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/crate_procedural/crate_procedural.glb", Vector3(-3, 0, 2))
	load_subject("E:/CyberCity2085-3d-lab/generated/phase2/generator01/generator.glb", Vector3(4.5, 0, 1.5))
	assert(subjects.size() == 5)
	for subject in subjects.slice(0, 2):
		var cell := Vector2i(floori(subject.position.x + data.grid[0] / 2.0), floori(subject.position.z + data.grid[1] / 2.0))
		assert(not occupied.has(cell), "Actor spawned in blocked cell")
	print("TACTICAL_MAP_LAYOUT_LOADED cells=", occupied.size(), " subjects=", subjects.size(), " visual=2.5D_floor_plus_blocked_cells")

func verify_robot_forward_walk() -> void:
	var actor := subjects[1]
	var player := actor.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	assert(player.current_animation == "Walk")
	var animation := player.get_animation("Walk")
	assert(animation.loop_mode == Animation.LOOP_NONE)
	var skeleton := actor.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var foot: MeshInstance3D
	for candidate in actor.find_children("*", "MeshInstance3D", true, false):
		if str(candidate.name).replace(".", "_") == "GEO_toes_L_Evaluated" or str(candidate.name).replace(".", "_") == "GEO-toes_L_Evaluated": foot = candidate
	assert(foot != null, "Actual articulated foot mesh required")
	var probe := preload("res://skin_motion_check.gd").new()
	player.seek(0, true)
	skeleton.force_update_all_bone_transforms()
	var first: Vector3 = probe.skinned_points(foot, skeleton, 1)[0]
	player.seek(animation.length, true)
	skeleton.force_update_all_bone_transforms()
	var last: Vector3 = probe.skinned_points(foot, skeleton, 1)[0]
	var displacement := last - first
	assert(displacement.distance_to(Vector3(0, 0, 0.6)) < 0.0001)
	player.advance(0.2)
	skeleton.force_update_all_bone_transforms()
	var held: Vector3 = probe.skinned_points(foot, skeleton, 1)[0]
	assert(last.distance_to(held) < 0.0001, "Forward pass must not teleport to its first pose")
	probe.free()
	print("MECHANICAL_FORWARD_STAGE_OK displacement=", displacement, " loop=none")

func play_clip(name_value: String) -> void:
	var players := subjects[selected].find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		clip_status = "Requested action unavailable (not simulated)"
		return
	var player := players[0] as AnimationPlayer
	var source_aliases: Dictionary = subjects[selected].get_meta("action_aliases", {})
	if source_aliases.has(name_value): name_value = source_aliases[name_value]
	var aliases := {"Shoot": "Pistol_Shoot", "Melee": "Punch_Cross", "Death": "Death01"}
	if aliases.has(name_value) and player.has_animation(aliases[name_value]): name_value = aliases[name_value]
	if not player.has_animation(name_value):
		clip_status = "Requested action unavailable: " + name_value
		return
	player.play(name_value)
	if selected==0:
		for part in human_embedded_weapon:part.visible=name_value=="ShootStudy"
	if selected==0 and sidearm_modules!=null:sidearm_modules.refresh(name_value)
	if selected == 0 and human_weapon: human_weapon.visible = name_value in ["Pistol_Shoot","Shoot"]
	if name_value == "Idle" or name_value == "Walk":
		player.get_animation(name_value).loop_mode = Animation.LOOP_NONE if name_value == "Walk" and subjects[selected].get_meta("forward_motion_study", false) else Animation.LOOP_LINEAR
	if not source_aliases.is_empty() and name_value in ["walk","run"]:
		player.get_animation(name_value).loop_mode = Animation.LOOP_LINEAR
	if name_value in [source_aliases.get("Walk",""),source_aliases.get("Run","")]:
		player.get_animation(name_value).loop_mode = Animation.LOOP_LINEAR
	if source_aliases.has("Idle") and name_value==source_aliases["Idle"]:
		player.get_animation(name_value).loop_mode = Animation.LOOP_LINEAR
	clip_status = ("Human animation: " if selected == 0 else "Robot animation: ") + name_value

func _process(_delta: float) -> void:
	if first_process_usec==0:first_process_usec=Time.get_ticks_usec()
	if hud:
		var fps_value := str(Engine.get_frames_per_second()) if Time.get_ticks_usec()-first_process_usec > 2000000 else "warming up"
		hud.text = "EXPERIMENTAL SCALE REVIEW | 1 m tiles | NOT FINAL ART\nLeft: human %.3f m | Right: robot %.3f m (measured mesh heights)\nSelected: %s | %s\nTAB / click: select | 1 Idle  2 Walk  3 Shoot  4 Death  5 Melee  6 Hit\nC: isometric / orbit | RMB drag: orbit | Wheel: zoom\nFPS %s | draw calls %d | rendered primitives %d" % [human_height, robot_height, "Human" if selected == 0 else "Robot", clip_status, fps_value, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)]
		if "--motion-extension159" in OS.get_cmdline_user_args():hud.text += "\n6: authored hit | K: crouched cover study (no tactical rule change)"
		if sidearm_modules!=null:hud.text += "\nE: swap actual sidearm | 3: draw | module: "+sidearm_modules.selected
		if vehicle_actor != null:hud.text += "\nVTOL inspection: 7 rotors | 8 retract gear | 9 extend gear (no flight physics)"
		if "--unvanquished-motion-study" in OS.get_cmdline_user_args():hud.text += "\nAuthored human study: U Run | A Attack | K Crouch | weapon grip NOT accepted"
		if "--scanned-head-study" in OS.get_cmdline_user_args():hud.text += "\nScanned head assembly: U Run | A Attack | K Crouch | identity and face rig NOT accepted"
		if "--scanned-hair-study" in OS.get_cmdline_user_args():hud.text += "\nAuthored Maxwell hair: U Run | A Attack | K Crouch | fit and identity NOT accepted"
		if "--scanned-shoot-study" in OS.get_cmdline_user_args():hud.text += "\nFiring fit study: 3 real pistol | U Run | A Attack | K Crouch | contact NOT final"
		if "--tactical" in OS.get_cmdline_user_args():
			hud.text += "\nExisting alley layout + 2D floor / prototype obstacle volumes\nVTOL hovering: no clear landing footprint | art NOT accepted"
			if "--facades-study" in OS.get_cmdline_user_args():hud.text=hud.text.replace("prototype obstacle volumes","3D industrial facade study")

func play_vehicle_clip(clip: String) -> void:
	assert(vehicle_actor != null)
	var player := vehicle_actor.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	assert(player.has_animation(clip))
	player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR if clip == "Rotor_Spin" else Animation.LOOP_NONE
	player.play(clip)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_E and selected==0 and sidearm_modules!=null:
			sidearm_modules.next(sidearm_modules.animation_player.assigned_animation)
		if event.keycode == KEY_TAB:
			selected = 1 - selected
		if event.keycode == KEY_C:
			orbit_mode = not orbit_mode
			if not orbit_mode:
				yaw = 0.65
				elevation = 0.6
				update_camera()
		var vehicle_actions := {KEY_7:"Rotor_Spin",KEY_8:"Gear_Retract",KEY_9:"Gear_Extend"}
		if vehicle_actor != null and vehicle_actions.has(event.keycode):play_vehicle_clip(vehicle_actions[event.keycode])
		var actions := {KEY_1: "Idle", KEY_2: "Walk", KEY_3: "Shoot", KEY_4: "Death", KEY_5: "Melee", KEY_6: "Hit"}
		if "--unvanquished-motion-study" in OS.get_cmdline_user_args() or "--scanned-head-study" in OS.get_cmdline_user_args() or "--scanned-hair-study" in OS.get_cmdline_user_args() or "--scanned-shoot-study" in OS.get_cmdline_user_args():
			actions.merge({KEY_U:"Run",KEY_A:"Attack",KEY_K:"Crouch"})
		if "--motion-extension159" in OS.get_cmdline_user_args():actions[KEY_K]="Cover"
		if actions.has(event.keycode):
			play_clip(actions[event.keycode])
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_RIGHT:
			orbiting = event.pressed
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			var point: Vector2 = event.position
			var left := camera.unproject_position(subjects[0].position + Vector3.UP)
			var right := camera.unproject_position(subjects[1].position + Vector3.UP)
			selected = 0 if point.distance_to(left) < point.distance_to(right) else 1
		if event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			camera.size = clampf(camera.size + (-0.5 if event.button_index == MOUSE_BUTTON_WHEEL_UP else 0.5), 3, 16)
	if event is InputEventMouseMotion and orbiting and orbit_mode:
		yaw -= event.relative.x * 0.008
		elevation = clampf(elevation + event.relative.y * 0.008, 0.15, 1.35)
		update_camera()
