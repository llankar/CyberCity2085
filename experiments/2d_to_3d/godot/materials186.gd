extends "res://presentation182.gd"
## Scene material direction; all source textures and normal maps remain active.
var material_changes := 0

func load_glb(relative: String, place: Vector3) -> Node3D:
	if (relative.begins_with("showcase195/") or relative.begins_with("showcase197/") or relative.begins_with("showcase198/") or relative.begins_with("showcase199/") or relative.begins_with("showcase206/") or relative.begins_with("showcase207/") or relative.begins_with("showcase208/") or relative.begins_with("showcase211/") or relative.begins_with("showcase214/") or relative.begins_with("showcase216/") or relative.begins_with("showcase219/") or relative.begins_with("showcase223/") or relative.begins_with("showcase229/") or relative.begins_with("showcase230/")):return super.load_glb(relative,place)
	if relative=="showcase174/environment.glb" and "--baked186" in OS.get_cmdline_user_args():
		var baked:=super.load_glb("showcase186/environment.glb",place)
		assert(baked!=null)
		print("MATERIAL186_BAKED_READY same97 source material edits")
		return baked
	var model:=super.load_glb(relative,place)
	if model==null or not relative.contains("environment.glb"):return model
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		for surface in mesh.mesh.get_surface_count():
			var original=mesh.get_active_material(surface)
			if not original is StandardMaterial3D:continue
			if original.emission_enabled:continue
			var paint:=original.duplicate() as StandardMaterial3D
			var label:=str(mesh.name)
			if label.begins_with("AuthoredGarageShutter"):
				paint.albedo_color*=Color(.28,.34,.38)
				paint.metallic=.35;paint.roughness=.78
			elif label.begins_with("PBR_Facade") and surface==1:
				paint.albedo_color*=Color(.45,.50,.55)
				paint.metallic=.08;paint.roughness=.92
			elif label.begins_with("AuthoredFacade_wall") or label.begins_with("AuthoredGarageBay"):
				paint.albedo_color*=Color(.65,.72,.76)
				paint.roughness=maxf(.75,paint.roughness)
			else:continue
			mesh.set_surface_override_material(surface,paint);material_changes+=1
	print("MATERIAL186_READY surfaces=",material_changes)
	return model

func _ready() -> void:
	super._ready()
	delivery_folder=ROOT+"materials186/"
	DirAccess.make_dir_recursive_absolute(delivery_folder)
