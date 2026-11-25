extends Node3D
## Actual GLB ray coverage, independent of producer's reported occupancy.
func _ready() -> void:
	var root := "E:/CyberCity2085-3d-lab/"
	var source := root+"sources/tactical_map/city_exterior_neon_market_alley.walls.json"
	var data = JSON.parse_string(FileAccess.get_file_as_string(source))
	var expected := {}
	for obstacle in data.walls:
		for cell in obstacle.cells:
			var key := Vector2i(cell[0],cell[1])
			if not expected.has(key):expected[key]=3.0 if "building" in str(obstacle.id) else .7
	assert(expected.size()==627)
	var model := preload("res://tactical_facade_loader.gd").load_model(self,source,expected.size())
	var body_mesh := model.find_child("ExactMapObstacleBody",true,false) as MeshInstance3D
	assert(body_mesh!=null and body_mesh.mesh.get_surface_count()>0)
	var collider := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	shape.shape=body_mesh.mesh.create_trimesh_shape()
	add_child(collider)
	collider.global_transform=body_mesh.global_transform
	collider.add_child(shape)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var space := get_world_3d().direct_space_state
	var hits := 0
	var misses := 0
	var max_height_error := 0.0
	for x in range(int(data.grid[0])):
		for y in range(int(data.grid[1])):
			var point := Vector3(x-data.grid[0]/2.0+.5,0,y-data.grid[1]/2.0+.5)
			var ray := PhysicsRayQueryParameters3D.create(point+Vector3.UP*5,point+Vector3.DOWN)
			var result := space.intersect_ray(ray)
			var key := Vector2i(x,y)
			if expected.has(key):
				assert(not result.is_empty(),str(key)+" missing solid cell")
				max_height_error=maxf(max_height_error,absf(result.position.y-float(expected[key])))
				hits+=1
			else:
				assert(result.is_empty(),str(key)+" blocked previously free cell")
				misses+=1
	assert(max_height_error<.0001)
	var report := {"glb_sha256":FileAccess.get_sha256(root+"generated/phase2/tactical_facades01/facades.glb"),"source_sha256":FileAccess.get_sha256(source),"occupied_cell_hits":hits,"free_cell_misses":misses,"max_roof_height_error_m":max_height_error,"scope":"Native actual body GLB ray coverage at all source grid cell centres; excludes decorative frame clearance, navigation and artistic acceptance"}
	var file := FileAccess.open(root+"generated/phase2/tactical_facades01/native_coverage_check.json",FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print("TACTICAL_FACADE_NATIVE_COVERAGE_OK occupied=",hits," free=",misses," height_error=",max_height_error)
	get_tree().quit()
