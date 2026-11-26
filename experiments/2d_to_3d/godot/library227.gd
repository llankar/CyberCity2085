extends "res://aircraft222.gd"
@export var bindings_path:String
var library_vapor:Array[Vector3]=[]
func load_glb(relative: String,place: Vector3) -> Node3D:
 var is_environment:=relative=="showcase174/environment.glb"
 var bindings:Dictionary={}
 if is_environment:
  bindings=JSON.parse_string(FileAccess.get_file_as_string(bindings_path))
  relative=bindings.get("environment_relative",relative)
 var model:=super.load_glb(relative,place)
 if not is_environment:return model
 assert(bindings.schema_version==1 and not bindings.tactical_mutation)
 for entry in bindings.instances:
  var groups=model.find_children("Occludable_"+entry.parent,"Node3D",true,false)
  assert(groups.size()==1)
  var group=groups[0] as Node3D
  for pattern in entry.replaces:
   for old in group.find_children(pattern,"MeshInstance3D",true,false):old.visible=false
  var document:=GLTFDocument.new();var state:=GLTFState.new()
  assert(document.append_from_file(entry.glb,state)==OK)
  var instance:=document.generate_scene(state) as Node3D
  group.add_child(instance)
  var p=entry.position;var s=entry.scale
  instance.global_position=Vector3(p[0],p[1],p[2])
  instance.rotation.y=float(entry.rotation_y);instance.scale=Vector3(s[0],s[1],s[2])
  if entry.vapor_offset!=null:
   var offset=entry.vapor_offset;library_vapor.append(instance.global_position+Vector3(offset[0],offset[1],offset[2]))
  print("LIBRARY227_PLACED ",entry.id," ",instance.global_position)
 # Parent combat169 gathers the complete group's bounds/materials on return.
 return model
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"library227/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for point in library_vapor:
  var nearest:=0
  for i in exhausts.size():
   if exhausts[i].distance_squared_to(point)<exhausts[nearest].distance_squared_to(point):nearest=i
  if not exhausts.is_empty():exhausts[nearest]=point
