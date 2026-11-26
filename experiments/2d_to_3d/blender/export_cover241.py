"""Export the blue covering as one reusable assembly from the saved scene master."""
from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'environment-library/assets/east_blue_cover'
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase241/environment.blend'))
root=bpy.data.objects['Occludable_east_building'];source=[o for o in root.children_recursive if o.type=='MESH' and o.name.startswith(('East241 blue covering','East241 cover tension post','East241 cover edge rail'))]
assert len(source)==7
points=[o.matrix_world@Vector(p) for o in source for p in o.bound_box];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);anchor=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
bpy.ops.object.select_all(action='DESELECT');copies=[]
for old in source:
 obj=old.copy();obj.parent=None;bpy.context.collection.objects.link(obj);obj.matrix_world=Matrix.Translation(-anchor)@old.matrix_world;obj.select_set(True);copies.append(obj)
bpy.ops.export_scene.gltf(filepath=str(OUT/'cover.glb'),export_format='GLB',use_selection=True)
source_meta=json.loads((OUT/'source.json').read_text());source_meta.update(id='east_blue_cover',family='Shelters',isolated_reference=str(OUT/'cloth.png'),source_object_id='east_building',anchor='bottom_center',models={'glb':str(OUT/'cover.glb'),'blender':str(LAB/'generated/phase2/showcase241/environment.blend')},blender_source_objects=[o.name for o in source],map_anchor=[anchor.x,anchor.z,-anchor.y],dimensions=list(hi-lo),map_associations=[],artistic_status='PARTIAL_SOURCE_DERIVED_NATIVE_IN_SCENE_STANDALONE_NOT_VERIFIED',remaining=['Baked source highlights remain','Standalone placement is not yet activated; current map uses the same mesh inside environment'])
(OUT/'source.json').write_text(json.dumps(source_meta,indent=2))
catalog=LAB/'environment-library/library.json';data=json.loads(catalog.read_text(encoding='utf8'));assets={a['id']:a for a in data['assets']};assets[source_meta['id']]=source_meta;data['assets']=list(assets.values());catalog.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
print('EAST241_COVER_ASSEMBLY_EXPORTED',len(source),list(hi-lo))
