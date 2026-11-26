extends Node3D

const Cutaway = preload("res://source_cutaway271.gd")


func obstruction(label: String, at: Vector3) -> MeshInstance3D:
 var group := Node3D.new()
 group.name = "Occludable_" + label
 add_child(group)
 var obstacle := MeshInstance3D.new()
 obstacle.mesh = BoxMesh.new()
 group.add_child(obstacle)
 obstacle.position = at
 return obstacle


func _ready() -> void:
 var camera := Camera3D.new()
 add_child(camera)
 camera.projection = Camera3D.PROJECTION_ORTHOGONAL
 camera.size = 12
 camera.position = Vector3(0, 1, 8)
 camera.look_at(Vector3(0, 1, 0))
 camera.make_current()
 var unit := Node3D.new()
 add_child(unit)
 unit.position.x = 3
 var in_front := obstruction("front", Vector3(3, 1, 4))
 var off_ray := obstruction("off_ray", Vector3(1.5, 1, 4))
 var behind := obstruction("behind", Vector3(3, 1, -2))
 await get_tree().process_frame
 var cutaway := Cutaway.new()
 cutaway.configure(self, [unit], camera, true)
 if cutaway.update(0) != 1 or in_front.visible or not off_ray.visible or not behind.visible:
  push_error("Orthographic cutaway failed to isolate the obstruction")
  get_tree().quit(1)
  return
 cutaway.actors = []
 cutaway.update(.06)
 if in_front.visible or cutaway.update(.07) != 0 or not in_front.visible:
  push_error("Cutaway did not restore the obstruction after the delay")
  get_tree().quit(2)
  return
 print("TACTICAL_CUTAWAY_OK")
 get_tree().quit()
