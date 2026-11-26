extends "res://district208.gd"
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"medic209/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 var rig:=actors[3].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
 var head:=bone(rig,"DEF-spine.006")
 players[3].play("Hard stand");players[3].seek(0,true);rig.force_update_all_bone_transforms()
 var socket:=BoneAttachment3D.new();socket.name="MedicHelmetSocket209";socket.bone_name=rig.get_bone_name(head);rig.add_child(socket);socket.on_skeleton_update()
 var helmet:=load_glb("medic209/helmet.glb",Vector3.ZERO)
 helmet.reparent(socket,false)
 var position:Vector3=(rig.global_transform*rig.get_bone_global_pose(head)).origin+Vector3(0,.12,0)
 helmet.transform=socket.global_transform.affine_inverse()*Transform3D(actors[3].global_basis,position)
 print("MEDIC209_READY authored helmet follows existing head bone")
