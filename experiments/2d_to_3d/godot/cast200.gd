extends "res://roof199.gd"
## Use the already-authored second body/helmet; retain the shared five motions.
var reinforcement_fired:=false
var treatment_start_health:=76
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"cast200/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 var old:=actors[4]
 var replacement:=load_glb("modularity166/body_0_helmet_restfixed.glb",old.position)
 actors[4]=replacement
 players[4]=replacement.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
 players[4].callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 for action in ["Idle","Walk","Pistol_Shoot","Punch_Cross","Death01"]:
  assert(players[4].has_animation("Rocketbox_"+action),action)
  players[4].get_animation_library("").add_animation(action,players[4].get_animation("Rocketbox_"+action))
 played[4]=""
 preload("res://rocketbox_pistol_attachment.gd").attach(replacement)
 old.visible=false;old.queue_free()
 print("CAST200_READY second authored body with real rigged helmet; shared clips retained")
func _process(delta: float) -> void:
 var t:=time_value
 super._process(delta)
 if actors.size()<6:return
 if t>=11.7 and not reinforcement_fired:
  var before:int=health[0]
  fire(4,0);reinforcement_fired=true
  var origin:=muzzle_position(4)
  var target:=actors[0].position+Vector3(0,1.1,0)
  var teammate:=actors[1].position+Vector3(0,1.1,0)
  var clearance:=teammate.distance_to(Geometry3D.get_closest_point_to_segment(teammate,origin,target))
  assert(clearance>.35,"Staged reinforcement shot crosses its teammate")
  FileAccess.open(delivery_folder+"retaliation.json",FileAccess.WRITE).store_string(JSON.stringify({"time":t,"health_before":before,"health_after":health[0],"teammate_clearance_m":clearance,"scope":"one staged shot; not general friendly-fire collision"}))
 if t>=11.7 and t<12.25:
  clip(4,"Pistol_Shoot",false);face(4,actors[0].position)
 # Start treatment at actual remaining HP, avoiding a jump to the old fixed76
 # after the added retaliation. Existing treatment rate/cap remain unchanged.
 if t<22:treatment_start_health=health[0]
 else:
  health[0]=mini(100,treatment_start_health+int((t-22)*5))
  bars[0].scale.x=float(health[0])/100

func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
 if index==4 and start==6:to=Vector3(6,0,.45)
 super.travel(index,from,to,start,end,walk,t)

func muzzle_position(source: int) -> Vector3:
 if source!=4:return super.muzzle_position(source)
 # Use the source motion's already-calibrated firing pose and actual wrist,
 # rather than emitting this new unit's shot from the generic chest marker.
 players[4].seek(.3,true)
 var rig:=actors[4].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
 rig.force_update_all_bone_transforms()
 var hand:=rig.find_bone("Bip01 R Hand")
 assert(hand>=0)
 return (rig.global_transform*rig.get_bone_global_pose(hand)).origin

func clip(index: int,name_value: String,loop:=true) -> void:
 # The inherited reinforcement idle must not restart its shoot clip on each
 # frame during this added burst; allow the existing animation to finish.
 if index==4 and name_value=="Idle" and time_value>=11.7 and time_value<12.25:return
 super.clip(index,name_value,loop)
