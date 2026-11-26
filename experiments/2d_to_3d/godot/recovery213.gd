extends "res://tempo212.gd"
var medical_hold:=0.0
var medical_length:=0.0
var recovery_recorded:=false
func healing_end() -> float:
 return 22.0+float(100-treatment_start_health)/5.0
func encounter_duration() -> float:
 return 31.0
func medical_contact_active() -> bool:
 return time_value>=22 and time_value<healing_end()
func _ready() -> void:
 super._ready()
 delivery_folder=ROOT+"recovery213/";DirAccess.make_dir_recursive_absolute(delivery_folder)
 medical_length=players[3].get_animation("MedicalAidPrototype").length
 var head:=bone(medic_rig,"DEF-spine.006")
 var lowest:=INF
 players[3].play("MedicalAidPrototype")
 # Seven samples select an existing kneeling pose, without new retargeting/rig.
 for sample in range(2,9):
  var phase:=medical_length*float(sample)/10
  players[3].seek(phase,true);medic_rig.force_update_all_bone_transforms()
  var height:float=(medic_rig.global_transform*medic_rig.get_bone_global_pose(head)).origin.y
  if height<lowest:lowest=height;medical_hold=phase
 players[3].play("Hard stand");players[3].seek(0,true);played[3]=""
 print("RECOVERY213_READY hold=",medical_hold," clip=",medical_length," recover after actual healing")
func clip(index: int,name_value: String,loop:=true) -> void:
 if time_value>=healing_end():
  if index==0 and name_value=="CoverStudy":name_value="CoverExitStudy" if time_value<healing_end()+1 else "Hard stand";loop=false
  if index==3 and name_value=="MedicalAidPrototype" and time_value>=healing_end()+1:name_value="Hard stand";loop=true
 super.clip(index,name_value,loop)
func after_unit_animations(t: float) -> void:
 super.after_unit_animations(t)
 if t<22:return
 var end:=healing_end()
 if t<end:
  players[3].seek(minf(t-22,medical_hold),true)
 elif t<end+1:
  var fraction:=clampf(t-end,0,1)
  players[3].seek(lerpf(medical_hold,medical_length,fraction),true)
  players[0].seek(players[0].get_animation("CoverExitStudy").length*fraction,true)
 if t>=end+1.2 and not recovery_recorded:
  # The imported idle omits rest-valued tracks. Clear the preceding full-body
  # interaction's unkeyed channels after the short animation crossfade finishes.
  medic_rig.reset_bone_poses();players[3].advance(0)
  patient_rig.reset_bone_poses();players[0].advance(0)
  assert(health[0]==100)
  assert(not medical_contact_active())
  recovery_recorded=true
  FileAccess.open(delivery_folder+"recovery.json",FileAccess.WRITE).store_string(JSON.stringify({"healing_end":end,"recovered_at":t,"health":health[0],"medic_clip":played[3],"patient_clip":played[0],"contact_active":medical_contact_active(),"idle_rest_channels_reset":true,"held_source_phase":medical_hold,"source_clip_length":medical_length}))
