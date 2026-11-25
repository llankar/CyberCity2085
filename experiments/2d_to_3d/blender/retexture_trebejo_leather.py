"""Rework a genuinely authored garment using licensed photometric PBR maps."""
import hashlib
import json
import sys
from pathlib import Path
import bmesh
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import bake_object

root=Path('E:/CyberCity2085-3d-lab')
source=root/'generated/phase2/trebejo_jacket'
maps=root/'sources/ambientcg_Leather037'
fresh='--fresh-normal' in sys.argv
folder=root/('generated/phase2/trebejo_leather02' if fresh else 'generated/phase2/trebejo_leather01');folder.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'jacket.blend'),use_scripts=False)
obj=next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
original=obj.data.copy();obj.data.calc_loop_triangles()
assert len(obj.data.loop_triangles)==18400
corner_positions=[obj.data.vertices[loop.vertex_index].co.copy() for loop in obj.data.loops]
corner_normals=[tuple(normal.vector) for normal in obj.data.corner_normals]
source_shader=next(n for n in obj.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
source_normal=source_shader.inputs['Normal'].links[0].from_node
assert source_normal.type=='NORMAL_MAP'
normal_image=source_normal.inputs['Color'].links[0].from_node.image
assert tuple(normal_image.size)==(1024,1024)
# The GLB codec derivative stores independent corners; weld identical positions
# only in this derivative, retaining per-loop authored UVs for source seams.
bm=bmesh.new();bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bm.to_mesh(obj.data);bm.free()
assert len(obj.data.vertices)==9375 and len(obj.data.polygons)==18400
for face in obj.data.polygons:face.use_smooth=True
assert len(obj.data.loops)==len(corner_positions)
corner_error=max((obj.data.vertices[loop.vertex_index].co-position).length for loop,position in zip(obj.data.loops,corner_positions))
assert corner_error<1e-6,('Weld reordered authored corners',corner_error)
if fresh:obj.data.normals_split_custom_set([(0,0,0)]*len(obj.data.loops))
else:obj.data.normals_split_custom_set(corner_normals)
tree_material=bpy.data.materials.new('PhotometricLeather_SourceSeams');tree_material.use_nodes=True
tree=tree_material.node_tree;shader=tree.nodes['Principled BSDF']
uv=tree.nodes.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=8
tree.links.new(uv.outputs[0],scale.inputs[0])
images={}
for suffix,channel in [('Color','Base Color'),('Roughness','Roughness'),('NormalGL',None)]:
    image=bpy.data.images.load(str(maps/f'Leather037_2K-PNG_{suffix}.png'),check_existing=True)
    assert tuple(image.size)==(2048,2048)
    image.colorspace_settings.name='sRGB' if suffix=='Color' else 'Non-Color'
    texture=tree.nodes.new('ShaderNodeTexImage');texture.image=image
    tree.links.new(scale.outputs[0],texture.inputs['Vector'])
    if channel:tree.links.new(texture.outputs['Color'],shader.inputs[channel])
    images[suffix]=texture
old=tree.nodes.new('ShaderNodeTexImage');old.image=normal_image
tree.links.new(uv.outputs[0],old.inputs['Vector'])
seams=tree.nodes.new('ShaderNodeNormalMap');seams.uv_map='SourceUV'
tree.links.new(old.outputs['Color'],seams.inputs['Color'])
detail=tree.nodes.new('ShaderNodeNormalMap');detail.uv_map='SourceUV'
tree.links.new(images['NormalGL'].outputs['Color'],detail.inputs['Color'])
geometry=tree.nodes.new('ShaderNodeNewGeometry')
subtract=tree.nodes.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT'
tree.links.new(detail.outputs[0],subtract.inputs[0]);tree.links.new(geometry.outputs['Normal'],subtract.inputs[1])
strength=tree.nodes.new('ShaderNodeVectorMath');strength.operation='SCALE';strength.inputs['Scale'].default_value=.25
tree.links.new(subtract.outputs[0],strength.inputs[0])
add=tree.nodes.new('ShaderNodeVectorMath');add.operation='ADD'
tree.links.new(seams.outputs[0],add.inputs[0]);tree.links.new(strength.outputs[0],add.inputs[1])
normalize=tree.nodes.new('ShaderNodeVectorMath');normalize.operation='NORMALIZE'
tree.links.new(add.outputs[0],normalize.inputs[0]);tree.links.new(normalize.outputs[0],shader.inputs['Normal'])
if fresh:tree.links.new(detail.outputs[0],shader.inputs['Normal'])
shader.inputs['Metallic'].default_value=0
obj.data.materials.clear();obj.data.materials.append(tree_material)
for face in obj.data.polygons:face.material_index=0
bpy.context.view_layer.objects.active=obj;obj.select_set(True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
scene.render.bake.margin=8
scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False
bake_object(obj,folder,'jacket',size=2048,preserve_source_uv=True)
obj.name='AuthoredLeatherJacket_PBRStudy'
obj['modifications']='Authored topology and corner normals retained; identical-corner weld; CC0 photometric leather retexture; source seam normal plus weak detail-normal perturbation approximation; new offline UV bake'
if fresh:obj['modifications']='Authored topology retained; identical-corner weld; recalculated smooth normals; original painted albedo/normal replaced with CC0 photometric leather PBR; new offline UV bake'
credits=(source/'CREDITS.txt').read_text()+'\n'+(maps/'CREDITS.txt').read_text()
bpy.data.texts.new('PBR_REWORK_CREDITS').write(credits)
(folder/'CREDITS.txt').write_text(credits,encoding='utf8')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'jacket.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'jacket.glb'),export_format='GLB',use_selection=True,
    export_extras=True,export_animations=False,export_copyright='Trebejo_Nixon_Jacket / Nixontrebejo CC BY4; Leather037 / ambientCG CC0')
report={'triangles':18400,'vertices_after_identical_corner_weld':len(obj.data.vertices),
        'authored_corner_position_max_error_m':corner_error,'authored_corner_normals_preserved':not fresh,
        'bake_uv_layout':'Copy of authored UVs; no smart projection',
        'source_glb_sha256':hashlib.sha256((source/'jacket.glb').read_bytes()).hexdigest(),
        'surface_provenance':json.loads((maps/'provenance.json').read_text()),
        'normal_detail':'New leather normal on smooth garment geometry; original seam/facet normal removed' if fresh else 'Normalize(source seam normal + .25*(leather normal - geometric normal)); approximation, not RNM',
        'maps_baked':[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in folder.glob('jacket_*.png')],
        'limitations':['Standalone authored garment; no character fitting, skinning or artistic acceptance',
                       'Painted source albedo is replaced, including its painted decorative details',
                       'Original seam normal removed; no new geometric buttons claimed' if fresh else 'Source seam normal retained; no new geometric buttons claimed',
                       'Eight UV repeats are a material study, not verified calibrated grain size']}
(folder/'retexture_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('AUTHORED_JACKET_PBR_REWORK_EXPORTED',flush=True)
