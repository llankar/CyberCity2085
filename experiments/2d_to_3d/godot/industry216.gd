extends "res://clinic214.gd"
var exhausts:Array[Vector3]=[]
var next_vapor:=0.0
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase216/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"industry216/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for mesh in find_children("Industry216_roof_exhaust*","MeshInstance3D",true,false):
  exhausts.append(mesh.global_transform*mesh.get_aabb().get_center()+Vector3(0,.25,0))
 # glTF may preserve spaces in node names.
 if exhausts.is_empty():
  for mesh in find_children("Industry216 roof exhaust*","MeshInstance3D",true,false):
   exhausts.append(mesh.global_transform*mesh.get_aabb().get_center()+Vector3(0,.25,0))
 assert(exhausts.size()==2)
 print("INDUSTRY216_READY authored repair/salvage stock, roof ducts and restrained vapor")
func _process(delta: float) -> void:
 super._process(delta)
 if effects==null or time_value<next_vapor:return
 next_vapor=time_value+.85
 for point in exhausts:
  effects.puff(point,.65,2.0,Vector3(.08,.32,-.035))
  var paint:=effects.clouds[-1].node.material_override as ShaderMaterial
  paint.set_shader_parameter("tint",Color(.42,.53,.58,.18))
