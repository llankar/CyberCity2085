extends RefCounted
## Lab-only bridge for uniform KHR clearcoat factors omitted by native import.
## Texture-based coats intentionally unsupported rather than silently approximated.
func apply_uniform_coats(state: GLTFState, model: Node3D) -> Dictionary:
	var expected := {}
	for material in state.json.get("materials",[]):
		var extension: Dictionary = material.get("extensions",{}).get("KHR_materials_clearcoat",{})
		if extension.is_empty(): continue
		assert(not extension.has("clearcoatTexture") and not extension.has("clearcoatRoughnessTexture") and not extension.has("clearcoatNormalTexture"),"Textured clearcoat bridge unsupported")
		var factor := float(extension.get("clearcoatFactor",0.0))
		var roughness := float(extension.get("clearcoatRoughnessFactor",0.0))
		assert(is_finite(factor) and factor>=0 and factor<=1 and is_finite(roughness) and roughness>=0 and roughness<=1)
		assert(material.has("name") and not expected.has(material.name))
		expected[material.name]={"factor":factor,"roughness":roughness}
	var applied := {}
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		for surface in range(mesh.mesh.get_surface_count()):
			var material := mesh.get_active_material(surface) as StandardMaterial3D
			if material==null or not expected.has(material.resource_name):continue
			var config: Dictionary = expected[material.resource_name]
			var revised := material.duplicate() as StandardMaterial3D
			revised.clearcoat_enabled=config.factor>0
			revised.clearcoat=config.factor
			revised.clearcoat_roughness=config.roughness
			mesh.set_surface_override_material(surface,revised)
			applied[material.resource_name]=config
	assert(applied.size()==expected.size(),"Clearcoat material not found uniquely")
	return applied
