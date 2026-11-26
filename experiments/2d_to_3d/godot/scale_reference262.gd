extends "res://laboratory247.gd"
## Read-only visual scale reference using a retained actor and original free cell.
@export var reference_cell:=Vector2i(23,14)
@export var reference_map:="city_interior_research_lab"
func _ready() -> void:
 await super._ready()
 var walls=JSON.parse_string(FileAccess.get_file_as_string("res://../../../assets/maps/"+reference_map+".walls.json"))
 assert(walls is Dictionary)
 for wall in walls.walls:
  for cell in wall.cells:assert(Vector2i(int(cell[0]),int(cell[1]))!=reference_cell,"Scale actor cell must be free in the original map")
 var document:=GLTFDocument.new()
 var state:=GLTFState.new()
 assert(document.append_from_file("E:/CyberCity2085-3d-lab/generated/phase2/sole_skin162/human.glb",state)==OK)
 var actor:=document.generate_scene(state)
 add_child(actor)
 actor.position=Vector3(reference_cell.x+.5-20,0,reference_cell.y+.5-14)
 for motion in actor.find_children("*","AnimationPlayer",true,false):
  if motion.has_animation("Hard stand"):
   motion.get_animation("Hard stand").loop_mode=Animation.LOOP_LINEAR
   motion.play("Hard stand");motion.advance(.15)
 for child in get_children():
  if child is CanvasLayer:child.hide()
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"scale_agent.png")
 review_camera.size=12
 review_target=actor.position+Vector3(0,.8,0)
 review_distance=10
 review_elevation=9
 update_review_camera()
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"scale_close.png")
 print("RETAINED_SCALE_ACTOR_CAPTURED map=",reference_map," free_cell=",reference_cell)
