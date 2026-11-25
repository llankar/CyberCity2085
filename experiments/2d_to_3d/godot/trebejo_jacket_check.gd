extends Node3D
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/generated/phase2/trebejo_jacket/"
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file(root+"jacket.glb",state)==OK)
	var model := doc.generate_scene(state)
	add_child(model)
	var meshes := model.find_children("*", "MeshInstance3D", true, false)
	assert(meshes.size()==1)
	var mesh := meshes[0] as MeshInstance3D
	assert(mesh.skin==null and mesh.mesh.get_surface_count()==1)
	var arrays := mesh.mesh.surface_get_arrays(0)
	assert(arrays[Mesh.ARRAY_INDEX].size()/3==18400)
	assert(arrays[Mesh.ARRAY_VERTEX].size()==55200 and arrays[Mesh.ARRAY_TEX_UV].size()==55200)
	var material := mesh.get_active_material(0) as StandardMaterial3D
	var textures := {}
	for slot in [BaseMaterial3D.TEXTURE_ALBEDO,BaseMaterial3D.TEXTURE_NORMAL,BaseMaterial3D.TEXTURE_METALLIC,BaseMaterial3D.TEXTURE_ROUGHNESS]:
		var texture := material.get_texture(slot)
		assert(texture!=null and texture.get_width()==1024 and texture.get_height()==1024)
		textures[texture.get_instance_id()]=true
	assert(textures.size()==3)
	var bounds: AABB = mesh.global_transform * mesh.get_aabb()
	assert(absf(bounds.size.y-.7)<.001)
	var output := FileAccess.open(root+"native_check.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"triangles":18400,"vertices":55200,"pbr_images":3,"height_m":bounds.size.y,"artistic_acceptance":false,"fit_or_rigged":false},"  "))
	print("TREBEJO_NATIVE_GARMENT_OK")
	get_tree().quit(0)
