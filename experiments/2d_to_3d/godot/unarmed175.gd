extends Node3D
## First visible deformation trial of the new neural mesh; no campaign logic.
const OUT := "E:/CyberCity2085-3d-lab/generated/phase2/rig175/"
var actor: Node3D
var player: AnimationPlayer
var frame := 0
var phase := -1
var camera: Camera3D
const CLIPS := ["Idle","Walk","Shoot","Melee","Death"]

func _ready() -> void:
	var doc:=GLTFDocument.new();var state:=GLTFState.new()
	assert(doc.append_from_file(OUT+"human.glb",state)==OK)
	actor=doc.generate_scene(state);add_child(actor)
	player=actor.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for clip in CLIPS:assert(player.has_animation(clip),clip)
	var world:=WorldEnvironment.new();world.environment=Environment.new()
	world.environment.background_mode=Environment.BG_COLOR
	world.environment.background_color=Color(.12,.13,.14)
	world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color=Color.WHITE;world.environment.ambient_light_energy=.6
	add_child(world)
	var lamp:=DirectionalLight3D.new();lamp.rotation_degrees=Vector3(-50,-30,0)
	lamp.light_energy=1.1;lamp.shadow_enabled=true;add_child(lamp)
	var ground:=MeshInstance3D.new();var plane:=PlaneMesh.new();plane.size=Vector2(8,8)
	ground.mesh=plane;var paint:=StandardMaterial3D.new();paint.albedo_color=Color(.22,.23,.24)
	ground.material_override=paint;ground.position.y=-.02;add_child(ground)
	camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=27.0 if "--game-scale" in OS.get_cmdline_user_args() else 3.0;add_child(camera)
	RenderingServer.frame_post_draw.connect(capture)
	print("UNARMED175_NATIVE_READY five clips")

func _process(_delta: float) -> void:
	if player==null:return
	var t:=float(frame)/30
	var index:=mini(4,int(t/2))
	if index!=phase:
		phase=index
		player.get_animation(CLIPS[index]).loop_mode=Animation.LOOP_NONE if index==4 else Animation.LOOP_LINEAR
		player.play(CLIPS[index],.1)
	player.advance(1.0/30)
	camera.position=Vector3(2.5*sin(.7+t*.08),2.1,3.5*cos(.7+t*.08))
	camera.look_at(Vector3(0,.85,0))
	frame+=1
	if frame>=330:get_tree().quit()

func capture() -> void:
	if frame in [15,75,135,195,285]:
		get_viewport().get_texture().get_image().save_png(OUT+("game_pose_%03d.png" if "--game-scale" in OS.get_cmdline_user_args() else "pose_%03d.png")%frame)
