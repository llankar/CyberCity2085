extends "res://laboratory247.gd"
## Existing animated Rook is a visual scale reference, not a new combat system.
func _ready() -> void:
 await super._ready()
 var doc:=GLTFDocument.new()
 var state:=GLTFState.new()
 assert(doc.append_from_file("E:/CyberCity2085-3d-lab/generated/phase2/sole_skin162/human.glb",state)==OK)
 var actor:=doc.generate_scene(state)
 add_child(actor)
 # Cell9,19 was checked against the original survey; placement changes no rules.
 actor.position=Vector3(-10.5,0,5.5)
 for motion in actor.find_children("*","AnimationPlayer",true,false):
  for clip in motion.get_animation_list():
   if str(clip)=="Hard stand" or "idle" in str(clip).to_lower():
    motion.get_animation(clip).loop_mode=Animation.LOOP_LINEAR
    motion.play(clip)
    motion.advance(.15)
    break
 for child in get_children():
  if child is CanvasLayer:child.hide()
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"combat_scale_agent.png")
 review_camera.size=11
 review_target=Vector3(-10.9,.8,3.2)
 review_distance=10
 review_elevation=9
 update_review_camera()
 await get_tree().process_frame
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(review_folder+"close_agent.png")
 print("FACTORY257_RETAINED_AGENT_SCALE_CAPTURED")
