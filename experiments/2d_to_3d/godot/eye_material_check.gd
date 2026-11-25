extends Node3D
func _ready() -> void:
	var folder := "E:/CyberCity2085-3d-lab/generated/phase2/nathan_eyes01/"
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	assert(document.append_from_file(folder+"human.glb",state)==OK)
	var model := document.generate_scene(state)
	add_child(model)
	var imported_coat := false
	for node in model.find_children("*","MeshInstance3D",true,false):
		for surface in range(node.mesh.get_surface_count()):
			var mat := node.get_active_material(surface) as StandardMaterial3D
			if mat.resource_name=="AuthoredEyePhototexture_CornealSurface":imported_coat=mat.clearcoat_enabled
	var applied := preload("res://uniform_clearcoat.gd").new().apply_uniform_coats(state,model)
	assert(applied.size()==1)
	var meshes := model.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==1)
	var mesh := meshes[0] as MeshInstance3D
	assert(mesh.mesh.get_surface_count()==2)
	var materials := {}
	for surface in range(2):
		var mat := mesh.get_active_material(surface) as StandardMaterial3D
		assert(mat != null and mat.albedo_texture != null)
		var values := {"roughness":mat.roughness,"texture_dimensions":str(mat.albedo_texture.get_size())}
		for property in mat.get_property_list():
			if str(property.name).begins_with("clearcoat"):values[property.name]=mat.get(property.name)
		materials[mat.resource_name]=values
		if mat.resource_name=="AuthoredEyePhototexture_CornealSurface":
			assert(absf(mat.roughness-.18)<.00001)
			assert(mat.clearcoat_enabled)
		else:assert(mat.roughness>.99)
	assert(materials.has("AuthoredEyePhototexture_CornealSurface"))
	var renderer := str(RenderingServer.get_current_rendering_method())
	var file := FileAccess.open(folder+"native_material_check_"+renderer+".json",FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify({"glb_sha256":FileAccess.get_sha256(folder+"human.glb"),"renderer":renderer,"materials":materials,"native_import_clearcoat_enabled":imported_coat,"uniform_extension_bridge":applied,"scope":"Native imported roughness/clearcoat/photographic textures; not full artistic acceptance"},"  "))
	print("NATHAN_EYE_NATIVE_MATERIAL_OK")
	get_tree().quit(0)
