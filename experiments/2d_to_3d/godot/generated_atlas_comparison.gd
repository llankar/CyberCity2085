extends Node2D
## Independent comparison overlay; follows the real AnimationPlayer clock.
var camera: Camera3D
var actor: Node3D
var player: AnimationPlayer
var original: TextureRect
var original_caption: Label
var original_manifest: Dictionary
var original_texture: Texture2D
var original_region := AtlasTexture.new()
var picture := TextureRect.new()
var region := AtlasTexture.new()
var caption := Label.new()
var note := Label.new()
var folder := "E:/CyberCity2085-3d-lab/generated/phase2/rook_run129/atlas/"
var manifests := {}
var textures := {}
var reference_height := 1.8
var state := {}
var current_wardrobe := false
var original_actions := {}
var atlas_actions := {}
var model_path := ""
const ORIGINAL_ACTIONS = {"CombatReadyStudy":"idle","walk":"move","PistolFireStudy":"shoot","MeleeStudy":"melee","DeathStudy":"death"}

func configure(view: Camera3D,model: Node3D,old_picture: TextureRect,old_caption: Label,height: float,wardrobe152: bool=false) -> void:
	current_wardrobe=wardrobe152;original_actions=ORIGINAL_ACTIONS.duplicate()
	if current_wardrobe:
		folder="E:/CyberCity2085-3d-lab/generated/phase2/amjviz_wardrobe150/atlas_full152/"
		original_actions={"Hard stand":"idle","Walk (1_24)":"move","ShootStudy":"shoot","MeleeStudy":"melee","DeathStudy":"death"}
		atlas_actions={"Hard stand":"idle","Walk (1_24)":"walk","ShootStudy":"shoot","MeleeStudy":"melee","DeathStudy":"death"}
	model_path=folder+("../human_actions.glb" if current_wardrobe else "../human.glb")
	camera=view;actor=model;original=old_picture;original_caption=old_caption;reference_height=height
	player=actor.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	original_manifest=original.get_meta("reference_manifest")
	original_texture=original.get_meta("reference_full_texture")
	original_region.atlas=original_texture;original.texture=original_region
	picture.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	picture.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	picture.texture=region;add_child(picture);add_child(caption);add_child(note)
	caption.add_theme_font_size_override("font_size",14)
	note.position=Vector2(20,390);note.add_theme_font_size_override("font_size",16)
	process_priority=100
	var proof=JSON.parse_string(FileAccess.get_file_as_string(folder+("../native_actions.json" if current_wardrobe else "../native_actions_validation.json")))
	assert(proof.glb_sha256==FileAccess.get_sha256(model_path))
	if current_wardrobe:assert(proof.maximum_error_m<.0005 and proof.samples==288)
	else:assert(proof.status=="PASS")
	for clip in original_actions:
		var name_value: String=clip+"_atlas.json"
		var manifest=JSON.parse_string(FileAccess.get_file_as_string(folder+name_value))
		assert(manifest.source_model_sha256==FileAccess.get_sha256(folder+("../human_actions.blend" if current_wardrobe else "../human.blend")))
		assert(str(manifest.texture).get_file()==str(manifest.texture))
		manifests[clip]=manifest
		var image:=Image.load_from_file(folder+manifest.texture)
		assert(image!=null)
		textures[clip]=ImageTexture.create_from_image(image)
	refresh()

func frame_at_time(animation: Dictionary,seconds: float) -> int:
	var count: int=animation.rows[0].size()
	var index:=maxi(0,int(floor(seconds*float(animation.fps)+.00001)))
	return index%count if animation.loop else mini(count-1,index)

func refresh() -> void:
	if player==null:return
	var clip:=str(player.assigned_animation)
	var foot:=camera.unproject_position(actor.global_position)
	var projected:=absf(camera.unproject_position(actor.global_position+Vector3.UP*reference_height).y-foot.y)
	var ahead:=camera.unproject_position(actor.global_position+actor.global_basis*Vector3(0,0,1))-foot
	var facing:=posmod(int(floor(atan2(ahead.y*2,ahead.x)/(TAU/8)+.5)),8)
	var seconds:=player.current_animation_position if not clip.is_empty() else 0.
	var actual_elevation:=asin(clampf(camera.global_basis.z.y,-1,1))
	var view_supported:=camera.projection==Camera3D.PROJECTION_ORTHOGONAL and absf(actual_elevation-.6)<.01
	var available:=manifests.has(clip) and view_supported
	picture.visible=available;original.visible=false
	caption.position=foot+Vector2(-55,132)
	original_caption.position=foot+Vector2(-135,12)
	state={"clip":clip,"seconds":seconds,"facing":facing,"generated_available":available,"original_available":false,"view_supported":view_supported,"projected_reference_px":projected}
	if not available:
		caption.text="Atlas unavailable: "+clip if view_supported else "Atlas fixed elevation: 0.600"
		original_caption.text="Original: no comparison"
		note.text="Comparison unavailable for action "+clip if view_supported else "Comparison hidden: atlas elevation is fixed at0.600; live camera %.3f"%actual_elevation
		return
	var manifest: Dictionary=manifests[clip]
	var animation: Dictionary=manifest.animations[atlas_actions.get(clip,clip.to_lower())]
	var source_origin:=float(manifest.source_strip_frames[0])/120. if current_wardrobe else 0.
	var atlas_seconds:=maxf(0.,seconds-source_origin)
	var sample:=0 if manifest.get("static_pose",false) else frame_at_time(animation,atlas_seconds)
	var orbit: int=manifest.facing_to_orbit_view[facing]
	var index: int=animation.rows[orbit][sample]
	var frame_size:=Vector2(manifest.frame_size[0],manifest.frame_size[1])
	region.atlas=textures[clip]
	region.region=Rect2(Vector2(index%8,index/8)*frame_size,frame_size)
	picture.size=frame_size*projected/float(manifest.reference_height_px[orbit])
	var anchor: Array=manifest.anchors_by_orbit_view[orbit]
	picture.position=foot+Vector2(0,120)-Vector2(anchor[0],anchor[1])*picture.size
	caption.text="Generated 2D\n"+clip
	state.merge({"sample":sample,"orbit":orbit,"atlas_index":index,"atlas_seconds":atlas_seconds,"source_origin_s":source_origin},true)
	var old_clip: String=original_actions[clip]
	if original_manifest.animations.has(old_clip):
		var old_animation: Dictionary=original_manifest.animations[old_clip]
		var old_sample:=frame_at_time(old_animation,seconds)
		var old_index: int=old_animation.rows[facing][old_sample]
		var old_size:=Vector2(original_manifest.frame_size[0],original_manifest.frame_size[1])
		var columns:=int(original_texture.get_width()/old_size.x)
		original_region.region=Rect2(Vector2(old_index%columns,old_index/columns)*old_size,old_size)
		original.size=old_size*projected/(old_size.y*float(original_manifest.reference_height_uv))
		original.position=foot+Vector2(-95,0)-Vector2(original_manifest.anchor_uv[0],original_manifest.anchor_uv[1])*original.size
		original.visible=true;original_caption.text="Original 2D\n"+old_clip
		state.merge({"original_available":true,"original_sample":old_sample,"original_action":old_clip},true)
	else:original_caption.text="Original 2D\nno "+old_clip+" clip"
	note.text="SYNCHRONIZED REVIEW | same elapsed time, each source's own cadence\nGenerated atlas: %s frame %d | %.3f s | 8-view facing quantized; no original clip is invented"%[clip,sample,seconds]

func _process(_delta: float) -> void:
	refresh()
