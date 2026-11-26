extends "res://aircraft222.gd"
const ROOF_ASSET="E:/CyberCity2085-3d-lab/environment-library/assets/roof_twin_fan/source.json"
var reconstructed_roof:Node3D
func load_glb(relative: String,place: Vector3) -> Node3D:
 var model:=super.load_glb(relative,place)
 if relative!="showcase174/environment.glb":return model
 var record=JSON.parse_string(FileAccess.get_file_as_string(ROOF_ASSET))
 var association=record.map_associations[0]
 var groups=model.find_children("Occludable_"+association.occlusion_parent,"Node3D",true,false)
 assert(groups.size()==1)
 var group=groups[0] as Node3D
 # Replace the previous generic roof duct without touching tactical cells.
 for old in group.find_children("Industry216*","MeshInstance3D",true,false):old.visible=false
 var document:=GLTFDocument.new();var state:=GLTFState.new()
 assert(document.append_from_file(record.models.glb,state)==OK)
 reconstructed_roof=document.generate_scene(state) as Node3D
 group.add_child(reconstructed_roof)
 var p=association.position
 reconstructed_roof.global_position=Vector3(p[0],p[1]+.02,p[2])
 reconstructed_roof.rotation.y=float(association.rotation)
 print("ROOF226_ORIGINAL_DERIVED_PLACEMENT ",reconstructed_roof.global_position)
 # combat169 registers this group's materials after this method returns.
 return model
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"roof226/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 # Move the existing vapor source from the hidden generic duct to the new unit.
 for i in exhausts.size():
  if exhausts[i].x<0:exhausts[i]=reconstructed_roof.global_position+Vector3(0,.38,0)
