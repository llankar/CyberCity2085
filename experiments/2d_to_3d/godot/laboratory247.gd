extends Node3D
## Art import review only. This scene does not implement tactical rules.
const ROOT := "E:/CyberCity2085-3d-lab/generated/phase2/lab247/"
func _ready() -> void:
 var document := GLTFDocument.new()
 var state := GLTFState.new()
 assert(document.append_from_file(ROOT+"environment.glb",state)==OK)
 var model := document.generate_scene(state)
 add_child(model)
 var world := WorldEnvironment.new()
 world.environment=Environment.new()
 world.environment.background_mode=Environment.BG_COLOR
 world.environment.background_color=Color(.07,.1,.13)
 world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
 world.environment.ambient_light_color=Color(.66,.78,.9)
 world.environment.ambient_light_energy=.65
 add_child(world)
 var light:=DirectionalLight3D.new()
 light.rotation_degrees=Vector3(-55,-30,0)
 light.light_energy=1.3
 light.shadow_enabled=true
 add_child(light)
 var camera:=Camera3D.new()
 add_child(camera)
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=34
 camera.position=Vector3(25,34,32)
 camera.look_at(Vector3.ZERO)
 camera.current=true
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(ROOT+"godot_overview.png")
 print("LAB247_NATIVE_IMPORTED meshes=",model.find_children("*","MeshInstance3D",true,false).size())
