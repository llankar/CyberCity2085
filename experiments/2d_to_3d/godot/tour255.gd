extends "res://laboratory247.gd"
## A real native orbit through six environments, without pretending to be combat.
const FOLDERS:=["showcase245","residential253","lab248","factory249","metro250","wasteland254"]
var tour_ready:=false
var tour_frames:=0
var tour_index:=0
var selected_folders:Array=[]
func _ready() -> void:
 selected_folders=FOLDERS.duplicate()
 if "--detail-pass" in OS.get_cmdline_user_args():
  selected_folders[2]="lab261"
  selected_folders[3]="factory260"
 tour_index=int(get_tree().get_meta("environment_tour_index",0))
 review_folder="E:/CyberCity2085-3d-lab/generated/phase2/"+str(selected_folders[tour_index])+"/"
 await super._ready()
 for child in get_children():
  if child is CanvasLayer:child.hide()
 tour_ready=true
func _process(_delta:float) -> void:
 if not tour_ready:return
 tour_frames+=1
 review_yaw=.663+float(tour_frames)*.004
 update_review_camera()
 if tour_frames<90:return
 tour_ready=false
 print("ENVIRONMENT_TOUR_STAGE_DONE ",selected_folders[tour_index])
 if tour_index+1>=selected_folders.size():
  print("ENVIRONMENT_TOUR_COMPLETE six native environments; art review only")
  get_tree().quit()
 else:
  get_tree().set_meta("environment_tour_index",tour_index+1)
  get_tree().call_deferred("change_scene_to_file","res://tour255.tscn")
