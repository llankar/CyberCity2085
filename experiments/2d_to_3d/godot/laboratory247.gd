extends Node3D
@export var review_ambient_color := Color(.66, .78, .9)
@export var review_ambient_energy := .65
@export var review_key_energy := 1.3
## Art import review only. This scene does not implement tactical rules.
@export var review_folder := "E:/CyberCity2085-3d-lab/generated/phase2/lab247/"
@export var review_model_name := "environment.glb"
@export var review_size := 34.0
@export var review_target := Vector3.ZERO
@export var review_distance := 40.0
@export var review_elevation := 34.0
@export var review_top_down := false
var review_camera:Camera3D
var review_yaw:=0.663
func update_review_camera() -> void:
 review_camera.position=review_target+Vector3(sin(review_yaw)*review_distance,review_elevation,cos(review_yaw)*review_distance)
 review_camera.look_at(review_target)
func _unhandled_input(event:InputEvent) -> void:
 if event is InputEventKey and event.pressed:
  if event.keycode==KEY_Q:review_yaw-=.25;update_review_camera()
  if event.keycode==KEY_E:review_yaw+=.25;update_review_camera()
 if event is InputEventMouseButton and event.pressed:
  if event.button_index==MOUSE_BUTTON_WHEEL_UP:review_camera.size=maxf(8,review_camera.size-2)
  if event.button_index==MOUSE_BUTTON_WHEEL_DOWN:review_camera.size=minf(60,review_camera.size+2)
func _ready() -> void:
 if "--topdown-review" in OS.get_cmdline_user_args():review_top_down=true
 var document := GLTFDocument.new()
 var state := GLTFState.new()
 assert(document.append_from_file(review_folder+review_model_name,state)==OK)
 var model := document.generate_scene(state)
 add_child(model)
 if review_folder.ends_with("/showcase245/"):
  # The retained encounter creates its original ground at runtime; its GLB is
  # architecture only. Recreate that visual floor in this independent review.
  var image:=Image.load_from_file("E:/CyberCity2085-3d-lab/sources/tactical_map/city_exterior_neon_market_alley.png")
  assert(image!=null)
  image.generate_mipmaps()
  var material:=StandardMaterial3D.new()
  material.albedo_texture=ImageTexture.create_from_image(image)
  material.roughness=.7
  var ground:=MeshInstance3D.new()
  var plane:=PlaneMesh.new()
  plane.size=Vector2(40,28)
  ground.mesh=plane
  ground.material_override=material
  ground.position.y=-.03
  add_child(ground)
 var world := WorldEnvironment.new()
 world.environment=Environment.new()
 world.environment.background_mode=Environment.BG_COLOR
 world.environment.background_color=Color(.07,.1,.13)
 world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
 world.environment.ambient_light_color=review_ambient_color
 world.environment.ambient_light_energy=review_ambient_energy
 add_child(world)
 var light:=DirectionalLight3D.new()
 light.rotation_degrees=Vector3(-55,-30,0)
 light.light_energy=review_key_energy
 light.shadow_enabled=true
 add_child(light)
 var camera:=Camera3D.new()
 add_child(camera)
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=review_size
 camera.current=true
 review_camera=camera
 update_review_camera()
 if review_top_down:
  camera.size=28
  camera.position=Vector3(0,40,0)
  camera.look_at(Vector3.ZERO,Vector3.FORWARD)
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+("top_down.png" if review_top_down else "godot_overview.png"))
 print("ENVIRONMENT_REVIEW_IMPORTED folder=",review_folder," meshes=",model.find_children("*","MeshInstance3D",true,false).size())
 var canvas:=CanvasLayer.new()
 add_child(canvas)
 var back:=Button.new()
 back.text="ENVIRONMENTS // Q/E ROTATE // WHEEL ZOOM"
 back.position=Vector2(20,20)
 back.custom_minimum_size=Vector2(530,48)
 back.pressed.connect(func():assert(get_tree().change_scene_to_file("res://multimap251.tscn")==OK))
 canvas.add_child(back)
 if get_tree().has_meta("environment_menu_test"):
  get_tree().set_meta("environment_menu_returned",true)
  await get_tree().process_frame
  back.pressed.emit()
