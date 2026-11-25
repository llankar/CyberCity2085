"""Inspect a genuinely licensed scan before any head replacement."""
import hashlib
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent.parent))
from head_normalization import normalization

root=Path('E:/CyberCity2085-3d-lab')
source=root/'sources/infinite_scan_head'
out=root/'generated/phase2/lee_perry_head01';out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source/'Head.fbx'),use_anim=False)
meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
assert meshes
points=[obj.matrix_world@v.co for obj in meshes for v in obj.data.vertices]
low=Vector([min(p[i] for p in points) for i in range(3)])
high=Vector([max(p[i] for p in points) for i in range(3)])
transform=Matrix(normalization(low,high).tolist())
scale=transform[0][0]
for obj in meshes:
    obj.data.transform(obj.matrix_world)
    obj.matrix_world.identity()
    obj.data.transform(transform)
    for face in obj.data.polygons:face.use_smooth=True
    material=bpy.data.materials.new('PhotographedSkin_SourceUV');material.use_nodes=True
    shader=material.node_tree.nodes['Principled BSDF']
    shader.inputs['Metallic'].default_value=0
    shader.inputs['Roughness'].default_value=.6
    texture=material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image=bpy.data.images.load(str(source/'Textures/lambertian.jpg'),check_existing=True)
    material.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    obj.data.materials.clear();obj.data.materials.append(material)
    assert obj.data.uv_layers.active
    obj.data.calc_loop_triangles()
notice=(source/'License.txt').read_text()+'\nNeutral isolated scan review, uniform45cm bust normalization and dielectric skin material. Original photo UVs retained; no facial retarget or Rook hair adaptation yet. Bump map acquired but not applied in this baseline.\n'
bpy.data.texts.new('SCAN_CREDITS').write(notice)
bpy.ops.file.pack_all()
for obj in bpy.context.scene.objects:obj.select_set(obj in meshes)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(out/'head.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'head.glb'),export_format='GLB',use_selection=True,export_animations=False,export_copyright=notice)
(out/'CREDITS.txt').write_text(notice,encoding='utf8')
(out/'import_report.json').write_text(json.dumps({'meshes':len(meshes),'vertices':sum(len(obj.data.vertices) for obj in meshes),'triangles':sum(len(obj.data.loop_triangles) for obj in meshes),'raw_bounds':[list(low),list(high)],'uniform_scale':scale,'texture_dimensions':list(texture.image.size),'glb_sha256':hashlib.sha256((out/'head.glb').read_bytes()).hexdigest(),'limitations':['No skeleton yet','No Rook likeness or outfit fit acceptance','Baseline albedo only; acquired bump not wired into GLB']},indent=2),encoding='utf8')
print('INFINITE_SCAN_EDITABLE_READY',flush=True)
