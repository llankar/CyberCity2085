extends "res://laboratory247.gd"
## A real native orbit through six environments, without pretending to be combat.
const FOLDERS:=["showcase245","residential253","lab248","factory249","metro250","wasteland254"]
var tour_ready:=false
var tour_frames:=0
var tour_index:=0
var selected_folders:Array=[]
var single_map:=-1
func _ready() -> void:
 selected_folders=FOLDERS.duplicate()
 if "--detail-pass" in OS.get_cmdline_user_args():
  selected_folders[1]="residential284"
  selected_folders[2]="lab290"
  selected_folders[3]="factory278"
  selected_folders[4]="metro282"
  selected_folders[5]="wasteland280"
 tour_index=int(get_tree().get_meta("environment_tour_index",0))
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--tour-map="):
   var value=argument.trim_prefix("--tour-map=")
   assert(value.is_valid_int(),"Tour map must be an integer index")
   single_map=int(value)
   assert(single_map>=0 and single_map<selected_folders.size(),"Tour map index outside selected environments")
   tour_index=single_map
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
 if single_map>=0 or tour_index+1>=selected_folders.size():
  print("ENVIRONMENT_TOUR_COMPLETE maps=",1 if single_map>=0 else selected_folders.size(),"; art review only")
  get_tree().quit()
 else:
  get_tree().set_meta("environment_tour_index",tour_index+1)
  get_tree().call_deferred("change_scene_to_file","res://tour255.tscn")
