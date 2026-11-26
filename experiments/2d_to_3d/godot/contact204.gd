extends "res://armored203.gd"
## Short nonlethal torso recoil; actual moving fist gates the staged melee hit.
var recoil_started:={}
var recoil_axis:={}
var recoil_base:={}
var impact_rigs:={}
var impact_bones:={}
var hand_rig:Skeleton3D
var hands:Array[int]=[]
var previous_hands:={}
var melee_minimum:=100.0
var melee_hit:=false
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"contact204/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 for index in [1,4]:
  var rig:=actors[index].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
  impact_rigs[index]=rig;impact_bones[index]=bone(rig,"Bip01 Spine2" if index==1 else "spine")
 hand_rig=actors[0].find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
 hands=[bone(hand_rig,"DEF-hand.R"),bone(hand_rig,"DEF-hand.L")]
 print("CONTACT204_READY moving fist contact and nonlethal torso recoil")
func resolve_staged_melee(_t: float) -> void:
 pass # Resolve after animation advancement using current skeleton positions.
func clip(index: int,name_value: String,loop:=true) -> void:
 if index==1 and name_value=="Death01" and health[1]>12:return
 if index==0 and name_value=="MeleeStudy":loop=false
 if index==2 and name_value=="Melee" and time_value>=13 and time_value<17.5:name_value="Idle"
 super.clip(index,name_value,loop)
func travel(index: int,from: Vector3,to: Vector3,start: float,end: float,walk: String,t: float) -> void:
 if index==0 and start==12:to.x=.65
 super.travel(index,from,to,start,end,walk,t)
func fire(source: int,target_index: int) -> void:
 var before:int=health[target_index]
 super.fire(source,target_index)
 if target_index in [1,4] and health[target_index]>0 and health[target_index]<before:
  # Stop using the beginning of Death as the survivor's hit animation.
  if target_index==1:clip(1,"Pistol_Shoot");players[1].seek(.16,true)
  recoil_started[target_index]=time_value
  var away:=actors[target_index].position-actors[source].position;away.y=0
  recoil_axis[target_index]=Vector3.UP.cross(away.normalized()).normalized()
func after_unit_animations(t: float) -> void:
 super.after_unit_animations(t)
 for index in recoil_started:
  var age:float=t-float(recoil_started[index])
  if age<0 or age>.32 or health[index]<=0:continue
  var rig:Skeleton3D=impact_rigs[index];var joint:int=impact_bones[index]
  var world_basis:=rig.global_basis*rig.get_bone_global_pose(joint).basis
  var axis:Vector3=(world_basis.inverse()*Vector3(recoil_axis[index])).normalized()
  recoil_base[index]=rig.get_bone_pose_rotation(joint)
  rig.set_bone_pose_rotation(joint,Quaternion(recoil_base[index])*Quaternion(axis,.14*sin(PI*age/.32)))
 if hand_rig==null:return
 if t>=14.5 and t<16.2 and not melee_hit:
  hand_rig.force_update_all_bone_transforms()
  var target_rig:Skeleton3D=impact_rigs[1]
  var chest:Vector3=(target_rig.global_transform*target_rig.get_bone_global_pose(impact_bones[1])).origin
  for joint in hands:
   var point:Vector3=(hand_rig.global_transform*hand_rig.get_bone_global_pose(joint)).origin
   var distance:=point.distance_to(chest);melee_minimum=minf(melee_minimum,distance)
   var previous:Vector3=previous_hands.get(joint,point)
   var advance:float=((point-previous)/maxf(.0001,get_process_delta_time())).dot((chest-point).normalized())
   previous_hands[joint]=point
   if t>=14.65 and distance<=.35 and advance>.12:
    health[1]=0;melee_hit=true;clip(1,"Death01",false)
    rings[1].visible=false;bars[1].visible=false
    effects.sound("melee",point,-10);effects.spark(point)
    FileAccess.open(delivery_folder+"melee_contact.json",FileAccess.WRITE).store_string(JSON.stringify({"time":t,"wrist_to_chest_m":distance,"forward_hand_speed_m_s":advance,"hand":hand_rig.get_bone_name(joint),"scope":"one moving fist vs approximate torso contact volume; not triangle collision"}))
    break
 if t>=16.2 and not melee_hit:
  FileAccess.open(delivery_folder+"missed_melee.json",FileAccess.WRITE).store_string(JSON.stringify({"minimum_wrist_to_chest_m":melee_minimum}))
  assert(melee_hit,"Staged melee did not reach its target")

func _process(delta: float) -> void:
 # Remove last frame's additive offset even when a source clip has no key for
 # this bone. Otherwise a short flinch could accumulate into a persistent lean.
 for index in recoil_base:
  var rig:Skeleton3D=impact_rigs[index]
  rig.set_bone_pose_rotation(impact_bones[index],recoil_base[index])
 recoil_base.clear()
 super._process(delta)
