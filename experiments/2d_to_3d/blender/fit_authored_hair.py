"""Fit a CC BY authored hair mesh onto one MPFB study, preserving both sources."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

output=Path(sys.argv[sys.argv.index('--')+1]).resolve()
if output.drive.upper()!='E:':
    raise ValueError('External output required')
output.mkdir(parents=True,exist_ok=True)
source='E:/CyberCity2085-3d-lab/sources/blender_studio_vincent/vincent_v1.blend'
bpy.ops.wm.open_mainfile(filepath=source,use_scripts=False)
for obj in bpy.data.objects:
    if obj.type=='ARMATURE': obj.data.pose_position='REST'
bpy.context.view_layer.update()
donor=bpy.data.objects['GEO-vincent_hair']
evaluated=donor.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh()
positions=[evaluated.matrix_world@v.co for v in mesh.vertices]
faces=[list(p.vertices) for p in mesh.polygons]
evaluated.to_mesh_clear()
low=Vector(tuple(min(v[i] for v in positions) for i in range(3)))
high=Vector(tuple(max(v[i] for v in positions) for i in range(3)))
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/authored_tactical01/authored_outfit.blend',use_scripts=False)
body=bpy.data.objects['rook_mpfb']
rig=body.parent
assert 'head' in rig.data.bones
evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh()
top=max((evaluated.matrix_world@v.co).z for v in mesh.vertices)
scalp=[evaluated.matrix_world@v.co for v in mesh.vertices if (evaluated.matrix_world@v.co).z>top-.08]
scalp_y=(min(v.y for v in scalp)+max(v.y for v in scalp))*.5
evaluated.to_mesh_clear()
for obj in list(bpy.context.scene.objects):
    if 'short02' in obj.name:
        bpy.data.objects.remove(obj,do_unlink=True)
data=bpy.data.meshes.new('VincentAuthoredHairFit')
# Fit bounding extents explicitly; no generated locks or primitive helmet.
center=(low+high)*.5
dimensions=high-low
target=Vector((0,scalp_y,top-.015))
scale=Vector((.205/dimensions.x,.205/dimensions.y,.16/dimensions.z))
fitted=[target+Vector(((v.x-center.x)*scale.x,(v.y-center.y)*scale.y,(v.z-center.z)*scale.z)) for v in positions]
data.from_pydata(fitted,[],faces)
data.update()
hair=bpy.data.objects.new('Authored_Vincent_Hair_CC_BY',data)
bpy.context.collection.objects.link(hair)
hair.parent=rig
hair.matrix_parent_inverse=rig.matrix_world.inverted()
group=hair.vertex_groups.new(name='head')
group.add(list(range(len(data.vertices))),1.0,'REPLACE')
modifier=hair.modifiers.new('HeadAttachment','ARMATURE')
modifier.object=rig
material=bpy.data.materials.new('AuthoredHairCopper')
material.use_nodes=True
shader=material.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.16,.045,.013,1)
shader.inputs['Roughness'].default_value=.65
hair.data.materials.append(material)
for polygon in data.polygons: polygon.use_smooth=True
attribution={'source':source,'license':'https://creativecommons.org/licenses/by/4.0/',
 'credit':'Vincent: design Matias Mendiola; modeling/texturing Andy Goralczyk; rig Juan Pablo Bouza; Blender Studio',
 'modifications':'Hair only: evaluated rest mesh, refitted proportions, material replacement, head-bone attachment',
 'vertices':len(positions),'head_top_m':top,'status':'single-character fitting study; artistic acceptance open'}
(output/'ATTRIBUTION.json').write_text(json.dumps(attribution,indent=2),encoding='utf-8')
(output/'material_factors.json').write_text(json.dumps({'armor_helios':[.075,.12,.115,1]}),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(output/'authored_outfit.blend'))
print('AUTHORED_HAIR_FITTED',json.dumps(attribution))
