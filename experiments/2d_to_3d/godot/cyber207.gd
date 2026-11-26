extends "res://facade206.gd"
var hologram_materials:Array[StandardMaterial3D]=[]
var scan_bars:Array[Dictionary]=[]
func load_glb(relative: String,place: Vector3) -> Node3D:
 if relative=="showcase174/environment.glb":relative="showcase207/environment.glb"
 return super.load_glb(relative,place)
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"cyber207/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for mesh in find_children("Holo207*","MeshInstance3D",true,false):
  for surface in mesh.mesh.get_surface_count():
   var mat:=mesh.get_active_material(surface) as StandardMaterial3D
   if mat and not hologram_materials.has(mat):hologram_materials.append(mat)
 for bar in find_children("Scan207*","MeshInstance3D",true,false):
  scan_bars.append({"node":bar,"origin":bar.global_position})
 print("CYBER207_READY seven technical kiosks, transparent holograms, existing encounter")
func _process(delta: float) -> void:
 super._process(delta)
 # The inherited occlusion pass resets alpha each frame; retain its fade.
 for mat in hologram_materials:
  mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
  mat.albedo_color.a*=.75
 for i in scan_bars.size():
  var entry:Dictionary=scan_bars[i]
  var position:Vector3=entry.origin
  position.y+=1.35*fposmod(time_value*.22+i*.23,1.0)
  entry.node.global_position=position
