extends SceneTree
func _initialize() -> void:call_deferred("check")
func check() -> void:
 var environment:=Node3D.new();root.add_child(environment)
 var group:=Node3D.new();group.name="Occludable_test";environment.add_child(group)
 var mesh:=MeshInstance3D.new();mesh.mesh=BoxMesh.new();mesh.mesh.size=Vector3(3,3,1);mesh.position=Vector3(0,1,4);group.add_child(mesh)
 var material:=StandardMaterial3D.new();mesh.material_override=material
 var originally_hidden:=MeshInstance3D.new();originally_hidden.mesh=BoxMesh.new();originally_hidden.position=mesh.position;originally_hidden.visible=false;group.add_child(originally_hidden)
 var actor:=Node3D.new();environment.add_child(actor)
 var camera:=Camera3D.new();environment.add_child(camera);camera.position=Vector3(0,3,8)
 var cutaway=load("res://source_cutaway271.gd").new();cutaway.configure(environment,[actor],camera)
 assert(cutaway.update(.1)==1 and not mesh.visible)
 assert(material.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED and material.albedo_color.a==1)
 camera.position=Vector3(8,3,0)
 cutaway.update(.04);assert(not mesh.visible)
 cutaway.update(.1);assert(mesh.visible and not originally_hidden.visible)
 print("CRISP284_NATIVE_CHECK_PASS hidden/restored without alpha ghost or material mutation")
 quit()
