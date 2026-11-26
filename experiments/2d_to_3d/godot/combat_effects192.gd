extends "res://combat_effects180.gd"
## A single-mesh AI robot must not spawn scaled copies of its whole body.
func destroy_robot(model: Node3D) -> void:
	var first:=motes.size()
	super.destroy_robot(model)
	var bodies:=model.find_children("*","MeshInstance3D",true,false)
	var removed:=0
	for index in range(motes.size()-1,first-1,-1):
		var node=motes[index].node
		if not node is MeshInstance3D:continue
		for body in bodies:
			if node.mesh==body.mesh:
				node.queue_free();motes.remove_at(index);removed+=1;break
	print("PAINTED192_WRECK_EFFECT whole-body fragment copies removed=",removed)
