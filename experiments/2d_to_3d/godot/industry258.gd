extends "res://factory257_scale.gd"
## Short native environment detail orbit, with retained human for scale.
var recording_ready:=false
var recorded_frames:=0
func _ready() -> void:
 await super._ready()
 review_camera.size=12
 recording_ready=true
func _process(_delta:float) -> void:
 if not recording_ready:return
 recorded_frames+=1
 review_yaw=.40+float(recorded_frames)*.004
 update_review_camera()
 if recorded_frames>=180:
  print("INDUSTRIAL_DETAIL258_NATIVE_ORBIT_COMPLETE")
  get_tree().quit()
