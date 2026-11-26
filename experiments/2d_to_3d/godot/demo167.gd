extends Node3D
## Private visual demonstrator. No campaign rules or production resources changed.
const ROOT := "E:/CyberCity2085-3d-lab/generated/phase2/"
const OUT := ROOT + "demo167_final/"
const CLIPS := [["Hard stand", "Idle", "Idle"], ["Walk (1_24)", "Walk", "Walk"],
	["ShootStudy", "Pistol_Shoot", "Idle"], ["MeleeStudy", "Punch_Cross", "Melee"],
	["CoverStudy", "Idle", "Hit"], ["PsiCast","Idle","Idle"],
	["MedicalAidPrototype","Idle","Idle"], ["DeathStudy", "Death01", "Death"]]
const PHASES := ["READY", "MOVE", "FIRE / INTERCHANGEABLE SIDEARM", "MELEE", "COVER / REACTION", "PSI CAST", "MEDICAL AID — ADAPTED KNEELING PROTOTYPE", "DOWN"]
var actors: Array[Node3D] = []
var players: Array[AnimationPlayer] = []
var origins: Array[Vector3] = []
var camera: Camera3D
var caption: Label
var equipment
var raider_pistol: Node3D
var frame := 0
var current_phase := -1
var record := false
var capture_frame := false
var showcase := false
var failures: Array[String] = []
var psi: MeshInstance3D
var medkit: MeshInstance3D
var performance_mode := false
var elapsed := 0.0
var frame_times: Array[float] = []
var overview := false

func load_glb(relative: String, place: Vector3) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file(ROOT + relative, state) != OK:
		failures.append(relative); return null
	# Keep rest-valued tracks for the new robot: every action must reset prior poses.
	var model := (doc.generate_scene(state,30,false,false) if (relative.begins_with("robot191/") or relative.begins_with("robot193/") or relative.begins_with("robot210/")) else doc.generate_scene(state)) as Node3D
	add_child(model); model.position = place
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		for index in mesh.mesh.get_surface_count():
			var material = mesh.get_active_material(index)
			if material is StandardMaterial3D:
				var copy := material.duplicate() as StandardMaterial3D
				copy.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
				for slot in [BaseMaterial3D.TEXTURE_ALBEDO,BaseMaterial3D.TEXTURE_NORMAL]:
					var texture := copy.get_texture(slot)
					if texture:
						var pixels := texture.get_image()
						if pixels and not pixels.has_mipmaps():
							pixels.generate_mipmaps(slot == BaseMaterial3D.TEXTURE_NORMAL)
							copy.set_texture(slot,ImageTexture.create_from_image(pixels))
				mesh.set_surface_override_material(index,copy)
	return model

func actor(relative: String, place: Vector3) -> Node3D:
	var model := load_glb(relative, place)
	assert(model != null)
	actors.append(model); origins.append(place)
	var player := model.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	players.append(player)
	return model

func _ready() -> void:
	record = "--record" in OS.get_cmdline_user_args()
	showcase = "--showcase" in OS.get_cmdline_user_args()
	performance_mode = "--performance" in OS.get_cmdline_user_args()
	overview = "--overview" in OS.get_cmdline_user_args()
	DirAccess.make_dir_recursive_absolute(OUT + ("showcase_frames" if showcase else "frames"))
	get_window().size = Vector2i(1920, 1080)
	Engine.max_fps = 15 if record else 60
	var world := WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color(.035,.05,.065)
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color(.72,.83,1)
	world.environment.ambient_light_energy = .65
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55,-35,0)
	sun.light_energy = 1.4; sun.shadow_enabled = true
	add_child(sun)
	build_environment()
	actor("sole_skin162/human.glb", Vector3(-2,0,1))
	# Import only the two new motions: retain the validated body and old clips.
	var support := load_glb("support167/human.glb",Vector3.ZERO)
	support.visible = false
	var extra := support.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	for clip in ["PsiCast","MedicalAidPrototype"]:
		players[0].get_animation_library("").add_animation(clip,extra.get_animation(clip).duplicate())
	support.queue_free()
	actor("modularity166/body_1.glb", Vector3(3,0,1.5))
	for clip in ["Idle","Walk","Pistol_Shoot","Punch_Cross","Death01"]:
		players[1].get_animation_library("").add_animation(clip,players[1].get_animation("Rocketbox_"+clip))
	actor("security_opaque137/robot_actions.glb", Vector3(-1,0,-3))
	equipment = preload("res://equipment_modules153.gd").new()
	equipment.configure(actors[0], ROOT + "amjviz_wardrobe150/human_actions.glb")
	raider_pistol = preload("res://rocketbox_pistol_attachment.gd").attach(actors[1])
	for index in actors.size():
		var marker := MeshInstance3D.new()
		var ring := TorusMesh.new(); ring.inner_radius = .37; ring.outer_radius = .41
		marker.mesh = ring; marker.position = origins[index] + Vector3(0,.025,0)
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(.1,.9,1) if index != 1 else Color(1,.25,.12)
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		marker.material_override = mat; add_child(marker)
	var vehicle := load_glb("vtol_finish135/vtol_actions.glb", Vector3(-6,3,-5))
	if vehicle:
		var rotor := vehicle.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
		rotor.play("Rotor_Spin")
	load_glb("crate_procedural/crate_procedural.glb", Vector3(-2,0,-.9))
	load_glb("generator01/generator.glb", Vector3(-6,0,1))
	psi = MeshInstance3D.new(); var orb := SphereMesh.new()
	orb.radius = .16; orb.height = .32; psi.mesh = orb
	var glow := StandardMaterial3D.new(); glow.albedo_color = Color(.7,.15,1)
	glow.emission_enabled = true; glow.emission = Color(.7,.1,1); glow.emission_energy_multiplier = 2
	psi.material_override = glow; add_child(psi)
	medkit = MeshInstance3D.new(); var case_mesh := BoxMesh.new()
	case_mesh.size = Vector3(.35,.18,.26); medkit.mesh = case_mesh
	var green := StandardMaterial3D.new(); green.albedo_color = Color(.03,.65,.4)
	medkit.material_override = green; medkit.position = Vector3(-2,.1,1.5); add_child(medkit)
	camera = Camera3D.new(); camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	add_child(camera)
	camera.position = Vector3(14,19,24); camera.look_at(Vector3.ZERO)
	camera.size = 24
	var height := absf(camera.unproject_position(Vector3(0,1.8,0)).y-camera.unproject_position(Vector3.ZERO).y)
	camera.size *= height / (180.0 if showcase else (21.0 if overview else 62.2))
	make_hud()
	RenderingServer.frame_post_draw.connect(capture)
	print("VISUAL_DEMO167_READY private scene / 3 animated actors / 6 asset roles")

func build_environment() -> void:
	var folder := "E:/CyberCity2085-3d-lab/sources/tactical_map/"
	var name_value := "city_exterior_neon_market_alley"
	var data = JSON.parse_string(FileAccess.get_file_as_string(folder+name_value+".walls.json"))
	var plane := MeshInstance3D.new(); var mesh := PlaneMesh.new()
	mesh.size = Vector2(data.grid[0],data.grid[1]); plane.mesh = mesh; plane.position.y = -.03
	var mat := StandardMaterial3D.new()
	var image := Image.load_from_file(folder+name_value+".png"); image.generate_mipmaps()
	mat.albedo_texture = ImageTexture.create_from_image(image); mat.roughness = .85
	plane.material_override = mat; add_child(plane)
	preload("res://tactical_facade_loader.gd").load_model(self,folder+name_value+".walls.json",627)
	# Restrained local cyan light complements neutral key light; geometry stays readable.
	var lamp := OmniLight3D.new(); lamp.position = Vector3(0,4,-2)
	lamp.light_color = Color(.15,.65,1); lamp.light_energy = 2; lamp.omni_range = 10
	add_child(lamp)

func make_hud() -> void:
	var hud := CanvasLayer.new(); add_child(hud)
	var panel := ColorRect.new(); panel.color = Color(.01,.025,.04,.88)
	panel.position = Vector2(20,18); panel.size = Vector2(880,105); hud.add_child(panel)
	caption = Label.new(); caption.position = Vector2(36,28)
	caption.add_theme_font_size_override("font_size",24); hud.add_child(caption)
	var footer := Label.new(); footer.position = Vector2(25,1000)
	footer.text = "PRIVATE 3D PROTOTYPE  |  Rook: AmJViZ  /  Raider: Rocketbox  /  Robot: Blender Studio\nPresentation only. PSI: authored spell motion. Medical: adapted kneeling interaction; final medical contact pending."
	footer.add_theme_font_size_override("font_size",18); hud.add_child(footer)
	if not showcase:
		var reference := TextureRect.new()
		var sprite := Image.load_from_file("E:/CyberCity2085-3d-lab/sources/rook_combat/00_E.png")
		sprite = sprite.get_region(sprite.get_used_rect())
		var pixels := 21 if overview else 62
		var width := maxi(1,roundi(float(sprite.get_width())/sprite.get_height()*pixels))
		sprite.resize(width,pixels,Image.INTERPOLATE_LANCZOS)
		reference.texture = ImageTexture.create_from_image(sprite)
		reference.position = Vector2(1770,990-pixels); reference.size = Vector2(width,pixels)
		reference.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		reference.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED; hud.add_child(reference)
		var label := Label.new(); label.text = "ROOK 2D SOURCE"; label.position = Vector2(1730,1020); hud.add_child(label)

func _process(delta: float) -> void:
	elapsed += delta
	if performance_mode:
		if elapsed > 1: frame_times.append(delta*1000)
		if elapsed > 6:
			frame_times.sort()
			var report := {"samples":frame_times.size(),"p95_frame_interval_ms":frame_times[int(frame_times.size()*.95)],"fps_cap":60,"renderer":"gl_compatibility","scope":"Integrated presentation scene frame intervals, not GPU execution or campaign performance"}
			FileAccess.open(OUT+"performance.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
			print("DEMO167_FRAME_TIMING ",JSON.stringify(report)); get_tree().quit(); return
	var t := float(frame)/15.0 if record else float(frame)/60.0
	var phase := 7 if t >= 24 else mini(int(t/3.0),6)
	if phase != current_phase:
		current_phase = phase
		for index in players.size():
			var clip: String = CLIPS[phase][index]
			assert(players[index].has_animation(clip),clip)
			players[index].get_animation(clip).loop_mode = Animation.LOOP_NONE if phase == 7 else Animation.LOOP_LINEAR
			players[index].play(clip); players[index].seek(0,true)
		equipment.choose("p320" if phase == 2 else "firewarden",CLIPS[phase][0])
		caption.text = "CYBERCITY 2085  //  TACTICAL 3D DEMO\n"+PHASES[phase]+("  |  DETAIL VIEW" if showcase else ("  |  OVERVIEW ~21 px / human" if overview else "  |  COMBAT ZOOM ~62 px / human"))
	for index in players.size():
		players[index].advance(1.0/15.0 if record else delta)
		actors[index].position = origins[index]
		actors[index].rotation.y = -PI/2 if phase == 1 and index == 1 else 0.0
		if phase == 1:
			if index == 1: actors[index].position.x -= fmod(t,3.0)*.8
			else: actors[index].position.z += fmod(t,3.0)*.8
		if phase == 4 and index == 0: actors[index].position.z = .15
	raider_pistol.visible = phase == 2
	psi.visible = phase == 5
	psi.position = actors[0].position + Vector3(0,1.25,.55)
	psi.scale = Vector3.ONE * (1+.15*sin(t*9))
	medkit.visible = phase == 6
	capture_frame = true
	frame += 1
	if record: RenderingServer.force_draw(false)
	if t >= 27:
		var report := {"status":"PASS" if failures.is_empty() else "FAIL", "actors":3,"resolution":[1920,1080],"phases":PHASES,"frames":frame,"showcase":showcase,"scope":"Presentation with existing animations, not tactical gameplay or final art acceptance","missing":["Final medical contacts","Hunyuan colour-textured rigged A-pose"]}
		FileAccess.open(OUT+("showcase.json" if showcase else "demo.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
		print("VISUAL_DEMO167_FINISHED ",JSON.stringify(report)); get_tree().quit()

func capture() -> void:
	if not capture_frame: return
	capture_frame = false
	if record:
		var path := OUT+("showcase_frames/" if showcase else "frames/")+"%04d.png"%frame
		get_viewport().get_texture().get_image().save_png(path)
	elif frame == 30:
		get_viewport().get_texture().get_image().save_png(OUT+"preview.png")
		if overview:
			get_viewport().get_texture().get_image().save_png(OUT+"overview_21px.png")
			print("OVERVIEW21_CAPTURED"); get_tree().quit()
