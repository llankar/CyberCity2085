extends "res://cast200.gd"
## Real PBR hard case, rigidly following the existing medic's upper spine.
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"medic201/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 var rig:=actors[3].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
 var spine:=bone(rig,"DEF-spine.003")
 players[3].play("Hard stand");players[3].seek(0,true);rig.force_update_all_bone_transforms()
 var socket:=BoneAttachment3D.new();socket.name="MedicalEquipmentSocket201";socket.bone_name=rig.get_bone_name(spine);rig.add_child(socket);socket.on_skeleton_update()
 var pack:=load_glb("medic201/medical_pack.glb",Vector3.ZERO)
 pack.reparent(socket,false)
 var placement:=actors[3].global_transform*Transform3D(Basis.IDENTITY,Vector3(0,1.25,-.24))
 pack.transform=socket.global_transform.affine_inverse()*placement
 print("MEDIC201_READY actual medical case on upper spine; original human/clips retained")
