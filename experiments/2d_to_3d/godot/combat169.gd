extends "res://demo167.gd"
## Continuous staged encounter. Independent of production rules and campaigns.
var refined := "--refined-stage" in OS.get_cmdline_user_args()
var medical_case: Node3D
var delivery_folder := ROOT+("combat171/" if "--refined-stage" in OS.get_cmdline_user_args() else "combat170/" if "--architecture170" in OS.get_cmdline_user_args() else "combat169/")
var rings: Array[MeshInstance3D] = []
var effects
var played: Array[String] = []
var health := [100,100,100,100,100]
var buildings: Array[Dictionary] = []
var event_index := 0
var steps := -1
var time_value := 0.0
var capturing := false
var recoil_until := 0.0
var bars: Array[MeshInstance3D] = []
var cover_cells := {}
var blocked_shots := 0
var occlusion_frames := 0
var crate_bounds := AABB()
const EVENTS := [[4.8,2,0],[7.2,1,0],[8.4,0,1],[9.6,1,0],[10.4,0,1],[11.3,0,1],[17.5,3,2],[18.5,3,2],[19.5,3,2]]

func load_glb(relative: String,place: Vector3) -> Node3D:
	if relative=="vtol_finish135/vtol_actions.glb" and "--vtol178" in OS.get_cmdline_user_args():relative="vtol178/vtol_actions.glb"
	var model := super.load_glb(relative,place)
	if model and relative.begins_with("vtol178/"):
		var motion=model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
		for clip in ["Rotor_Spin","Gear_Retract","Gear_Extend"]:assert(motion.has_animation(clip),clip)
		motion.get_animation("Rotor_Spin").loop_mode=Animation.LOOP_LINEAR
		print("VTOL178_NATIVE_CLIPS_READY ",motion.get_animation_list()," rotor_loop=",motion.get_animation("Rotor_Spin").loop_mode)
	if model and relative.contains("crate_procedural"):
		var first := true
		for mesh in model.find_children("*","MeshInstance3D",true,false):
			var box: AABB=mesh.global_transform*mesh.get_aabb()
			crate_bounds=box if first else crate_bounds.merge(box);first=false
	return model

func build_environment() -> void:
	var map_data=JSON.parse_string(FileAccess.get_file_as_string("E:/CyberCity2085-3d-lab/sources/tactical_map/city_exterior_neon_market_alley.walls.json"))
	for wall in map_data.walls:
		for cell in wall.cells:cover_cells[Vector2i(cell[0],cell[1])]=3.0 if "building" in wall.id else .7
	var floor := MeshInstance3D.new();var plane := PlaneMesh.new();plane.size=Vector2(40,28);floor.mesh=plane;floor.position.y=-.03
	var image := Image.load_from_file("E:/CyberCity2085-3d-lab/sources/tactical_map/city_exterior_neon_market_alley.png");image.generate_mipmaps()
	var mat := StandardMaterial3D.new();mat.albedo_texture=ImageTexture.create_from_image(image);mat.roughness=.9
	floor.material_override=mat;add_child(floor)
	var environment_path := "showcase174/environment.glb" if "--city-details" in OS.get_cmdline_user_args() else "showcase171/environment.glb" if refined else "showcase170/environment.glb" if "--architecture170" in OS.get_cmdline_user_args() else "showcase169/environment.glb"
	var environment := load_glb(environment_path,Vector3.ZERO)
	for group in environment.find_children("Occludable_*","Node3D",true,false):
		var bounds := AABB();var first := true;var materials: Array[StandardMaterial3D] = []
		for mesh in group.find_children("*","MeshInstance3D",true,false):
			var box: AABB = mesh.global_transform*mesh.get_aabb()
			bounds=box if first else bounds.merge(box);first=false
			for surface in mesh.mesh.get_surface_count():
				var original=mesh.get_active_material(surface)
				if original is StandardMaterial3D:
					var copy=original.duplicate() as StandardMaterial3D
					mesh.set_surface_override_material(surface,copy);materials.append(copy)
		if not first:buildings.append({"bounds":bounds,"materials":materials,"fade":1.0})

func make_hud() -> void:
	pass # Clean captures; selection rings and diegetic effects carry the action.

func _ready() -> void:
	super._ready()
	DirAccess.make_dir_recursive_absolute(delivery_folder+"frames")
	Engine.max_fps=30 if record else 60
	if OS.has_feature("movie"):Engine.max_fps=0
	for node in get_children():
		if node is MeshInstance3D and node.mesh is TorusMesh:node.visible=false
	psi.visible=false;medkit.visible=false
	var ally := actors[0].duplicate() as Node3D
	add_child(ally);actors.append(ally);origins.append(Vector3(-5,0,2))
	players.append(ally.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer)
	# Ally casts/medicates; hide the inherited pistol modules.
	for node in ally.find_children("*","MeshInstance3D",true,false):
		if str(node.name).begins_with("EquippedPistol_"):node.visible=false
	var enemy := actors[1].duplicate() as Node3D
	add_child(enemy);actors.append(enemy);origins.append(Vector3(6,0,3.5))
	players.append(enemy.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer)
	played.resize(actors.size());played.fill("")
	for index in actors.size():
		players[index].callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		var ring := MeshInstance3D.new();var shape := TorusMesh.new();shape.inner_radius=.36;shape.outer_radius=.39;ring.mesh=shape
		var paint := StandardMaterial3D.new();paint.albedo_color=Color(.06,.8,.9) if index in [0,3] else Color(.9,.13,.04)
		paint.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;ring.material_override=paint;add_child(ring);rings.append(ring)
		var bar := MeshInstance3D.new();var rectangle := QuadMesh.new();rectangle.size=Vector2(.6,.045);bar.mesh=rectangle
		var ink := paint.duplicate() as StandardMaterial3D;ink.billboard_mode=BaseMaterial3D.BILLBOARD_ENABLED
		bar.material_override=ink;add_child(bar);bars.append(bar)
	effects=preload("res://combat_effects169.gd").new();add_child(effects)
	var doc := GLTFDocument.new();var state := GLTFState.new()
	assert(doc.append_from_file("E:/CyberCity2085-3d-lab/sources/environment169/medical_box/medical_box_1k.gltf",state)==OK)
	var medical := doc.generate_scene(state) as Node3D;add_child(medical);medical.name="AuthoredMedicalCase"
	medical.position=Vector3(0,.02,1.7);medical.scale=Vector3.ONE*.7
	medical_case=medical
	if refined:
		medical_case.visible=false
		medical_case.position=Vector3(-.05,.02,1.95)
	for lamp_position in [Vector3(-3,3,1),Vector3(4,3,1)]:
		var lamp := OmniLight3D.new();lamp.position=lamp_position;lamp.omni_range=7;lamp.light_energy=.6;lamp.light_color=Color(.5,.15,.8);add_child(lamp)
	print("COMBAT169_READY five units / continuous timeline / authored PBR environment")

func clip(index: int,name_value: String,loop := true) -> void:
	if played[index]==name_value:return
	assert(players[index].has_animation(name_value),name_value)
	players[index].get_animation(name_value).loop_mode=Animation.LOOP_LINEAR if loop else Animation.LOOP_NONE
	players[index].play(name_value,.12);played[index]=name_value
	if index==0:equipment.refresh(name_value)

func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
	var fraction := clampf((t-start)/(end-start),0,1)
	actors[index].position=from.lerp(to,fraction)
	if fraction>0 and fraction<1:
		clip(index,walk);face(index,to)
		# Cycles stay proportional to distance/time, not a separate teleport track.
		players[index].speed_scale=from.distance_to(to)/(end-start)/.85
	else:players[index].speed_scale=1

func face(index: int,point: Vector3) -> void:
	point.y=actors[index].position.y
	if actors[index].position.distance_to(point)>.05:actors[index].look_at(point,Vector3.UP,true)

func muzzle_position(source: int) -> Vector3:
	if source==0 and equipment.attachment:
		equipment.attachment.on_skeleton_update()
		return equipment.attachment.global_position
	return actors[source].position+Vector3(0,1.3,0)

func fire(source: int,target_index: int) -> void:
	face(source,actors[target_index].position)
	clip(source,"ShootStudy" if source in [0,3] else ("Melee" if source==2 else "Pistol_Shoot"))
	players[source].seek(.16,true)
	var from := muzzle_position(source)
	var target_point := actors[target_index].position+Vector3(0,1.1,0)
	if target_index==0 and played[0]=="CoverStudy":target_point.y=.65
	from+=(target_point-from).normalized()*.22
	for sample in range(1,51):
		var point := from.lerp(target_point,float(sample)/50)
		var cell := Vector2i(floori(point.x+20),floori(point.z+14))
		if crate_bounds.has_point(point) or (cover_cells.has(cell) and point.y<float(cover_cells[cell])):
			effects.shot(from,point,true,source==2);blocked_shots+=1;return
	if source==3:
		clip(source,"PsiCast");effects.psychic(from,target_point)
		clip(target_index,"Hit",false)
	else:
		effects.shot(from,target_point,target_index==2,source==2)
		if target_index==0:clip(0,"HitStudy",false);players[0].seek(0,true)
		if target_index==1:
			clip(1,"Death01",false);players[1].seek(.05,true);recoil_until=effects.clock+.22
	health[target_index]=maxi(0,health[target_index]-12)

func _process(delta: float) -> void:
	if effects==null:return
	var dt := 1.0/30 if record else delta
	var t := time_value;effects.step(dt,t)
	# All positions are functions of continuous paths and remain at their endpoint.
	travel(0,Vector3(-5,0,1.5),Vector3(-2,0,1.2),0,4,"Walk (1_24)",t)
	if t<.05:clip(0,"Hard stand")
	if t>=4 and t<5.5:
		actors[0].position=Vector3(-2,0,1.2).lerp(Vector3(-2,0,.15),clampf((t-4)/.5,0,1))
		clip(0,"CoverStudy");face(0,Vector3(3,0,1.5))
	if t>=5.5 and t<6.2:
		actors[0].position=Vector3(-2,0,.15).lerp(Vector3(-2,0,1.2),(t-5.5)/.7)
		clip(0,"CoverExitStudy",false)
	if t>=6.2 and t<7.2:clip(0,"ShootStudy");face(0,Vector3(3,0,1.5))
	if t>=12:
		travel(0,Vector3(-2,0,1.2),Vector3(.5,0,1.5),12,14.5,"Walk (1_24)",t)
	if t>=14.5 and t<16.2:
		clip(0,"MeleeStudy");face(0,actors[1].position)
	if t>=16.2 and t<22:clip(0,"Hard stand")
	if t>=22:
		clip(0,"CoverStudy")
		if refined:face(0,Vector3(-.5,0,1.7))
	travel(1,Vector3(4,0,1.5),Vector3(1.5,0,1.5),3,6,"Walk",t)
	if t<3:clip(1,"Idle")
	if t>=6 and t<7.2:clip(1,"Pistol_Shoot");face(1,actors[0].position)
	travel(2,Vector3(-1,0,-3),Vector3(-1,0,-.2),8,13,"Walk",t)
	if t<8:clip(2,"Idle")
	if t>=13 and t<17.5:clip(2,"Melee");face(2,actors[0].position)
	if t>=20 and health[2]>0:
		health[2]=0;clip(2,"Death",false);effects.destroy_robot(actors[2])
	travel(3,Vector3(-5,0,2),Vector3(-3,0,2),0,3,"Walk (1_24)",t)
	if t>=3 and t<17.5:clip(3,"Hard stand")
	if t>=17.5 and t<20:face(3,actors[2].position)
	if t>=20:
		travel(3,Vector3(-3,0,2),Vector3(-.5,0,1.7),20,22,"Walk (1_24)",t)
	if t>=22:
		clip(3,"MedicalAidPrototype",false);face(3,actors[0].position)
		health[0]=mini(100,76+int((t-22)*5))
		if refined:medical_case.visible=true
	travel(4,Vector3(6,0,3.5),Vector3(6,0,1.5),6,9,"Walk",t)
	if t<6 or t>=9:clip(4,"Idle")
	while event_index<EVENTS.size():
		var shot_index := event_index
		if t<float(EVENTS[shot_index][0]):break
		fire(int(EVENTS[shot_index][1]),int(EVENTS[shot_index][2]));event_index+=1
	if health[1]>0 and played[1]=="Death01" and t>recoil_until:clip(1,"Pistol_Shoot")
	# Melee event has its own latch independent of later PSI event ordering.
	if t>=15.2 and health[1]>0:
		health[1]=0;clip(1,"Death01",false);effects.sound("melee",actors[1].position,-10);effects.spark(actors[1].position+Vector3(0,1,0))
	for index in actors.size():
		players[index].advance(dt);rings[index].position=actors[index].position+Vector3(0,.025,0)
		rings[index].visible=health[index]>0
		bars[index].position=actors[index].position+Vector3(0,2.05 if index!=2 else 2.5,0)
		bars[index].scale.x=float(health[index])/100;bars[index].visible=health[index]>0
	raider_pistol.visible=t>=6 and t<12
	var yaw := deg_to_rad(35+20*sin(t*.12))
	var target := Vector3(-.5,.3,1)
	var vertical := lerpf(23,5 if refined else 12,smoothstep(21,26,t))
	camera.position=target+Vector3(sin(yaw)*28,vertical,cos(yaw)*28);camera.look_at(target)
	camera.size=23-3*sin(t*.10)
	for building in buildings:
		var blocked := false
		for index in ([0,3,5] if actors.size()>5 else [0,3]):
			if building.bounds.intersects_segment(camera.position,actors[index].position+Vector3(0,1,0))!=null:blocked=true
		if blocked:occlusion_frames+=1
		building.fade=move_toward(float(building.fade),.2 if blocked else 1.0,dt*4)
		for material in building.materials:
			material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA if building.fade<.99 else BaseMaterial3D.TRANSPARENCY_DISABLED
			material.albedo_color.a=building.fade
	if int(t*2.5)!=steps and t<14:
		steps=int(t*2.5)
		if t<4 or (t>12 and t<14.5):effects.sound("step",actors[0].position,-24)
	time_value+=dt;frame+=1;capturing=true
	if record:RenderingServer.force_draw(false)
	if t>=30:
		FileAccess.open(delivery_folder+"audio.json",FileAccess.WRITE).store_string(JSON.stringify(effects.audio_events))
		FileAccess.open(delivery_folder+"encounter.json",FileAccess.WRITE).store_string(JSON.stringify({"blocked_shots":blocked_shots,"occlusion_frames":occlusion_frames,"health":health,"frames":frame,"scope":"Staged local encounter, not production tactical AI"}))
		print("COMBAT169_CAPTURE_FINISHED frames=",frame);get_tree().quit()

func capture() -> void:
	if not capturing:return
	capturing=false
	if record:get_viewport().get_texture().get_image().save_png(delivery_folder+"frames/%04d.png"%frame)
	elif frame==120:
		get_viewport().get_texture().get_image().save_png(delivery_folder+"preview.png")
		if "--quick" in OS.get_cmdline_user_args():get_tree().quit()
	if OS.has_feature("movie") and frame in [30,254,460,590,630,750]:
		get_viewport().get_texture().get_image().save_png(delivery_folder+"clean_%04d.png"%frame)
