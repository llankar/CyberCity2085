extends RefCounted
## Independent authored cover-sequence preview; no tactical rules or production state.
var player:AnimationPlayer
var model:Node3D
var status_changed:Callable
var history:Array[String]=[]

func configure(actor:Node3D,status:Callable) -> void:
	model=actor;status_changed=status
	player=model.find_children("*","AnimationPlayer",true,false)[0]
	for clip in ["Hard stand","CoverEnterStudy","CoverStudy","CoverExitStudy"]:assert(player.has_animation(clip))
	player.animation_finished.connect(_finished)

func _play(clip:String) -> void:
	player.get_animation(clip).loop_mode=Animation.LOOP_LINEAR if clip in ["Hard stand","CoverStudy"] else Animation.LOOP_NONE
	player.play(clip)
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		if str(mesh.name).begins_with("EquippedPistol_"):mesh.visible=false
	history.append(clip)
	if status_changed.is_valid():status_changed.call(clip)

func toggle() -> bool:
	# Ignore repeat presses during transitions, avoiding mid-pose jumps.
	if player.assigned_animation in ["CoverEnterStudy","CoverExitStudy"] and player.is_playing():return false
	if player.assigned_animation=="Hard stand":_play("CoverEnterStudy");return true
	if player.assigned_animation=="CoverStudy":_play("CoverExitStudy");return true
	return false

func _finished(clip:StringName) -> void:
	if clip=="CoverEnterStudy":_play("CoverStudy")
	elif clip=="CoverExitStudy":_play("Hard stand")
