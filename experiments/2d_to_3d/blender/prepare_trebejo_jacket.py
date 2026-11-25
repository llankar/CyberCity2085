"""Import a real CC BY garment, normalize units and preserve its PBR surfaces."""
import json
import shutil
from pathlib import Path
import bpy
from mathutils import Matrix
root=Path('E:/CyberCity2085-3d-lab/generated/phase2/trebejo_jacket')
source=Path('E:/CyberCity2085-3d-lab/sources/trebejo_jacket')
metadata=json.loads((source/'provenance.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'decoded_source.glb'))
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']; assert len(meshes)==1
obj=meshes[0]; obj.data.calc_loop_triangles(); assert len(obj.data.loop_triangles)==18400
obj.data.transform(Matrix.Scale(float(metadata['scale_to_real']),4) @ obj.matrix_world)
obj.matrix_world=Matrix.Identity(4); obj.name='AuthoredTrebejoJacket'
points=[vertex.co for vertex in obj.data.vertices]
low=[min(point[axis] for point in points) for axis in range(3)]
high=[max(point[axis] for point in points) for axis in range(3)]
assert abs(high[2]-low[2]-.7)<.001
obj['source_license']='CC BY 4.0'; obj['source_author']=metadata['author']
obj['source_url']=metadata['source_url']; obj['modifications']='Codec conversion and catalog unit normalization only'
bpy.data.texts.new('SOURCE_CREDITS_CC_BY_4').write((source/'CREDITS.txt').read_text())
bpy.ops.file.pack_all()
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'jacket.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'jacket.glb'),export_format='GLB',use_selection=True,
    export_extras=True,export_animations=False,export_copyright=metadata['attribution'])
shutil.copyfile(source/'CREDITS.txt',root/'CREDITS.txt')
(root/'blender_import_report.json').write_text(json.dumps({'vertices':len(obj.data.vertices),'triangles':18400,
    'normalized_bounds_blender':[low,high],'materials':len(obj.data.materials),
    'images':[{'name':image.name,'dimensions':list(image.size),'packed':bool(image.packed_file)} for image in bpy.data.images],
    'source_author':metadata['author'],'source_license':'CC BY 4.0',
    'limitations':['Standalone authored garment, no fit or rigging claim yet']},indent=2),encoding='utf-8')
print('TREBEJO_BLENDER_GARMENT_READY',len(obj.data.vertices),len(obj.data.loop_triangles),low,high,flush=True)
