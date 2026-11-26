extends "res://combat_effects179.gd"
## Preserve actual robot materials on fragments; keep a visible smoking wreck.
func destroy_robot(model: Node3D) -> void:
	var before:=motes.size()
	super.destroy_robot(model)
	var sources:=model.find_children("*","MeshInstance3D",true,false)
	var fragment_index:=0
	for index in range(before,motes.size()):
		var item: Dictionary=motes[index]
		if item.node is MeshInstance3D and item.velocity.length_squared()>0 and fragment_index<mini(6,sources.size()):
			var source:=sources[fragment_index] as MeshInstance3D
			var fragment:=item.node as MeshInstance3D
			fragment.material_override=source.material_override
			for surface in source.mesh.get_surface_count():
				fragment.set_surface_override_material(surface,source.get_active_material(surface))
			item.life=8.0
			fragment_index+=1
	# Taller clustered plume rises above the cover instead of disappearing behind it.
	for index in 5:
		puff(model.global_position+Vector3(.08*index,1.55+index*.14,0),
			1.1,3.2+index*.15,Vector3(.1,.6,.02))
		var paint:=clouds[-1].node.material_override as ShaderMaterial
		paint.set_shader_parameter("tint",Color(.16,.18,.20,.92))
	print("WRECK180 fragments retaining source materials: ",fragment_index)
