extends "res://laboratory247.gd"
## Visual scale/cutaway reference only; no gameplay, targeting or path simulation.
@export var reference_map:="city_transit_subway_platform"
@export var reference_cells:Array[Vector2i]=[Vector2i(22,24),Vector2i(24,24),Vector2i(26,24)]
@export var close_elevation:=9.0
@export var close_yaw:=.663
@export var delivery_next_scene:=""
@export var reference_models:Array[String]=["sole_skin162/human.glb","modularity166/body_1.glb","robot210/robot_actions.glb"]
@export var reference_idles:Array[String]=["Hard stand","Rocketbox_Idle","Idle"]
var units:Array=[]
var cutaway=preload("res://source_cutaway271.gd").new()
var active:=false
func _process(delta:float) -> void:
 if active:cutaway.update(delta)
func _ready() -> void:
 await super._ready()
 var walls=JSON.parse_string(FileAccess.get_file_as_string("res://../../../assets/maps/"+reference_map+".walls.json"))
 var blocked={}
 for wall in walls.walls:
  for cell in wall.cells:blocked[Vector2i(int(cell[0]),int(cell[1]))]=true
 assert(reference_cells.size()==reference_models.size() and reference_idles.size()==reference_models.size())
 for index in reference_models.size():
  assert(not blocked.has(reference_cells[index]),"Cast cell must be free in original tactical map")
  var document:=GLTFDocument.new()
  var state:=GLTFState.new()
  assert(document.append_from_file("E:/CyberCity2085-3d-lab/generated/phase2/"+reference_models[index],state)==OK)
  var actor:=document.generate_scene(state)
  add_child(actor)
  actor.position=Vector3(reference_cells[index].x+.5-20,0,reference_cells[index].y+.5-14)
  units.append(actor)
  for motion in actor.find_children("*","AnimationPlayer",true,false):
   assert(motion.has_animation(reference_idles[index]),"Retained idle clip missing")
   motion.get_animation(reference_idles[index]).loop_mode=Animation.LOOP_LINEAR
   motion.play(reference_idles[index]);motion.advance(.15)
 cutaway.configure(self,units,review_camera)
 for child in get_children():
  if child is CanvasLayer:child.hide()
 active=true
 for frame in 12:await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"cast_wide.png")
 var center:=Vector3.ZERO
 for actor in units:center+=actor.position
 review_target=center/units.size()+Vector3(0,.8,0)
 review_camera.size=14;review_distance=11;review_elevation=close_elevation;review_yaw=close_yaw;update_review_camera()
 for frame in 12:await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"cast_close.png")
 print("MULTICAST271_CAPTURED actors=",units.size()," source_free_cells=",reference_cells," hidden_groups=",cutaway.update(.1))
 if not delivery_next_scene.is_empty() and "--production-lot278" in OS.get_cmdline_user_args():
  for frame in 90:
   review_yaw+=.004
   update_review_camera()
   await get_tree().process_frame
  if delivery_next_scene=="QUIT":
   print("PRODUCTION278_REVIEW_COMPLETE assembled map sequence")
   get_tree().quit()
  else:assert(get_tree().change_scene_to_file(delivery_next_scene)==OK)
