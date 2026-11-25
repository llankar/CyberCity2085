extends RefCounted
## Private interchangeable props on one measured socket; no body/animation rebuild.
var attachment: BoneAttachment3D
var variants := {}
var originals: Array[MeshInstance3D] = []
var selected := "firewarden"
var config: Dictionary
var animation_player: AnimationPlayer

func configure(model: Node3D,model_path: String) -> void:
	var folder:="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_modules153/"
	config=JSON.parse_string(FileAccess.get_file_as_string(folder+"modules.json"))
	assert(config.body_glb_sha256==FileAccess.get_sha256(model_path),"Socket metadata is for another body")
	var rig:=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	var bone:=rig.find_bone(config.bone)
	if bone<0:bone=rig.find_bone(str(config.bone).replace(".","_"))
	assert(bone>=0)
	var player:=model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	animation_player=player
	var previous:=player.assigned_animation
	var was_playing:=player.is_playing()
	var previous_time:=player.current_animation_position if not previous.is_empty() else 0.
	player.play(config.reference_clip);player.seek(config.reference_time_s,true)
	rig.force_update_all_bone_transforms()
	var rows: Array=config.world_placement_yup
	var basis:=Basis(Vector3(rows[0][0],rows[1][0],rows[2][0]),Vector3(rows[0][1],rows[1][1],rows[2][1]),Vector3(rows[0][2],rows[1][2],rows[2][2]))
	var placement:=Transform3D(basis,Vector3(rows[0][3],rows[1][3],rows[2][3]))
	var local_mount: Transform3D=(rig.global_transform*rig.get_bone_global_pose(bone)).affine_inverse()*model.global_transform*placement
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name).begins_with("EquippedPistol_"):originals.append(mesh)
	assert(originals.size()==9)
	attachment=BoneAttachment3D.new();attachment.name="InterchangeableSidearm153";attachment.bone_name=rig.get_bone_name(bone)
	rig.add_child(attachment)
	for key in config.variants:
		var asset: Dictionary=config.variants[key]
		assert(FileAccess.get_sha256(asset.file)==asset.sha256)
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		assert(document.append_from_file(asset.file,state)==OK)
		var prop:=document.generate_scene(state) as Node3D
		attachment.add_child(prop);prop.transform=local_mount
		variants[key]=prop
	if previous.is_empty():player.stop();rig.reset_bone_poses()
	else:
		player.play(previous);player.seek(previous_time,true)
		if not was_playing:player.pause()
	rig.force_update_all_bone_transforms();attachment.on_skeleton_update()
	refresh(previous)

func choose(key: String,clip: String) -> void:
	assert(variants.has(key),"Unknown prop variant")
	selected=key;refresh(clip)

func refresh(clip: String) -> void:
	for mesh in originals:mesh.visible=false
	for key in variants:variants[key].visible=key==selected and clip=="ShootStudy"

func next(clip: String) -> void:
	choose("p320" if selected=="firewarden" else "firewarden",clip)
