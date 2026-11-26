extends Node3D
## Reversible inferred interior floor. Source PNG and route surfaces remain untouched.
func texture(path:String) -> ImageTexture:
 var image:=Image.load_from_file(path);image.generate_mipmaps()
 return ImageTexture.create_from_image(image)
func build(plan:Dictionary) -> void:
 var grid=plan.grid
 var tile:=PlaneMesh.new();tile.size=Vector2.ONE
 var source:=tile.surface_get_arrays(0)
 var vertices:=PackedVector3Array();var normals:=PackedVector3Array();var tangents:=PackedFloat32Array();var uv:=PackedVector2Array();var indices:=PackedInt32Array()
 for cell in plan.cells:
  var center:=Vector3(float(cell[0])+.5-float(grid[0])*.5,-.02,float(cell[1])+.5-float(grid[1])*.5)
  var start:=vertices.size()
  for point in source[Mesh.ARRAY_VERTEX]:
   var p:Vector3=point+center;vertices.append(p);normals.append(Vector3.UP);tangents.append_array(PackedFloat32Array([1,0,0,-1]));uv.append(Vector2(p.x,p.z)/2.0)
  for index in source[Mesh.ARRAY_INDEX]:indices.append(start+index)
 var arrays:=[];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_TANGENT]=tangents;arrays[Mesh.ARRAY_TEX_UV]=uv;arrays[Mesh.ARRAY_INDEX]=indices
 var mesh:=ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
 var material:=StandardMaterial3D.new();var base:="E:/CyberCity2085-3d-lab/sources/environment169/blue_metal_plate/"
 material.albedo_texture=texture(base+"diff.jpg");material.albedo_color=Color(.72,.75,.8);material.roughness=.88;material.metallic=.15
 material.roughness_texture=texture(base+"rough.jpg");material.normal_enabled=true;material.normal_texture=texture(base+"nor_gl.jpg");material.normal_scale=.3
 var surface:=MeshInstance3D.new();surface.name="InferredVolumeFloors244";surface.mesh=mesh;surface.material_override=material;surface.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;add_child(surface)
 var evidence={"occupied_cells":plan.cells.size(),"vertices":vertices.size(),"triangles":indices.size()/3,"surfaces":mesh.get_surface_count(),"scope":plan.scope}
 var file:=FileAccess.open("E:/CyberCity2085-3d-lab/generated/phase2/floor244/native.json",FileAccess.WRITE);file.store_string(JSON.stringify(evidence,"  "));file.close()
 print("VOLUME_FLOOR244_READY cells=",plan.cells.size()," surfaces=1 source_png_unchanged")
