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
  var replaced:Array[MeshInstance3D]=[]
  for pattern in entry.replaces:
   for old in group.find_children(pattern,"MeshInstance3D",true,false):
    if old not in replaced:replaced.append(old)
    old.visible=false
  var document:=GLTFDocument.new();var state:=GLTFState.new()
  assert(document.append_from_file(entry.glb,state)==OK)
  var instance:=document.generate_scene(state) as Node3D
  group.add_child(instance)
  var p=entry.position;var s=entry.scale
  instance.global_position=Vector3(p[0],p[1],p[2])
  instance.rotation.y=float(entry.rotation_y);instance.scale=Vector3(s[0],s[1],s[2])
  if entry.get("match_replaced_bounds",false):
   assert(not replaced.is_empty())
   var old_bounds:AABB=replaced[0].global_transform*replaced[0].get_aabb()
   for old in replaced:old_bounds=old_bounds.merge(old.global_transform*old.get_aabb())
   var new_bounds:=model_bounds(instance)
   var center_error:=old_bounds.get_center().distance_to(new_bounds.get_center())
   var size_error:=old_bounds.size.distance_to(new_bounds.size)
   var imported:=instance.find_children("*","MeshInstance3D",true,false).size()
   assert(center_error<.05 and size_error<.05 and imported==replaced.size(),"Replacement placement differs")
   var evidence={"asset":entry.asset_id,"hidden_meshes":replaced.size(),"imported_meshes":imported,"center_error_m":center_error,"size_error_m":size_error,"scope":"Placement bounds and replaced mesh count only"}
   var file:=FileAccess.open(ROOT+"library227/replacement_check.json",FileAccess.WRITE)
   file.store_string(JSON.stringify(evidence,"  "));file.close()
   print("LIBRARY_REPLACEMENT_MATCH ",evidence)
  if entry.vapor_offset!=null:
   var offset=entry.vapor_offset;library_vapor.append(instance.global_position+Vector3(offset[0],offset[1],offset[2]))
  print("LIBRARY227_PLACED ",entry.id," ",instance.global_position)
 # Parent combat169 gathers the complete group's bounds/materials on return.
 return model
func _ready() -> void:
 var boot_start:=Time.get_ticks_usec()
 super._ready()
 delivery_folder=ROOT+"library227/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 if not record and not OS.has_feature("movie") and not ("--skip-warmup" in OS.get_cmdline_user_args()):
  warm_live_materials()
 if "--measure-live" in OS.get_cmdline_user_args():
  var probe=preload("res://live_frame_probe.gd").new()
  probe.startup_ms=float(Time.get_ticks_usec()-boot_start)/1000.0
  probe.tag="baseline" if "--measure-baseline" in OS.get_cmdline_user_args() else "live"
  add_child(probe)
 for point in library_vapor:
  var nearest:=0
  for i in exhausts.size():
   if exhausts[i].distance_squared_to(point)<exhausts[nearest].distance_squared_to(point):nearest=i
  if not exhausts.is_empty():exhausts[nearest]=point
func warm_live_materials() -> void:
 # Compile both cutaway/opaque variants before the timed encounter begins.
 # The temporary cover prevents exposing bind poses during this loading work.
 var layer:=CanvasLayer.new();layer.layer=100;add_child(layer)
 var cover:=ColorRect.new();cover.color=Color(.02,.03,.04);cover.size=get_viewport().get_visible_rect().size;layer.add_child(cover)
 update_camera(0.0)
 var modes:Array[Dictionary]=[]
 for building in buildings:
  for material in building.materials:
   modes.append({"material":material,"mode":material.transparency})
   material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
 RenderingServer.force_draw(false)
 for saved in modes:saved.material.transparency=saved.mode
 RenderingServer.force_draw(false)
 layer.queue_free()
