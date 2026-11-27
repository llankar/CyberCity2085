extends SceneTree

const Cutaway = preload("res://source_cutaway271.gd")


func _initialize() -> void:
 call_deferred("check_cutaway")


func check_cutaway() -> void:
 var environment := Node3D.new()
 root.add_child(environment)
 var camera := Camera3D.new()
 environment.add_child(camera)
 camera.position = Vector3(0, 1, 5)
 var actor := Node3D.new()
 environment.add_child(actor)
 var group := Node3D.new()
 group.name = "Occludable_Test"
 environment.add_child(group)
 group.position = Vector3(0, 1, 2)
 var mesh := MeshInstance3D.new()
 mesh.mesh = BoxMesh.new()
 group.add_child(mesh)
 var cutaway := Cutaway.new()
 cutaway.configure(environment, [actor], camera)
 if cutaway.update(.016) != 1 or mesh.visible or cutaway.update(.016) != 1:
  push_error("Stationary blocked view did not retain its cutaway")
  quit(1)
  return
 actor.position.x = 3
 if cutaway.update(.04) != 1 or cutaway.update(.04) != 1 or mesh.visible:
  push_error("Stationary clear view did not retain the reveal delay")
  quit(1)
  return
 if cutaway.update(.06) != 0 or not mesh.visible:
  push_error("Stationary clear view did not finish its pending reveal")
  quit(1)
  return
 camera.position.x = -2
 if cutaway.update(.016) != 1 or mesh.visible:
  push_error("Camera movement did not invalidate the cached ray")
  quit(1)
  return
 print("CUTAWAY_CACHE_OK")
 quit()
