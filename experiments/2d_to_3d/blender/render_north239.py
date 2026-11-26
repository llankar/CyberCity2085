"""Unobstructed neutral art view of the selected northern building, no master edits."""
from pathlib import Path
import bpy,argparse,sys
from mathutils import Vector
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant',choices=['showcase239','showcase243','showcase245'],default='showcase239')
parser.add_argument('--object',choices=['north_building','nw_building','sw_building'],default='north_building')
parser.add_argument('--size',type=float,default=9.5)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2'/args.variant
bpy.ops.wm.open_mainfile(filepath=str(OUT/'environment.blend'))
root=bpy.data.objects['Occludable_'+args.object];kept=set(root.children_recursive)|{root}
for obj in bpy.context.scene.objects:obj.hide_render=obj not in kept
body=next(o for o in kept if o.name.startswith('PBR_Facade_'))
points=[body.matrix_world@Vector(p) for p in body.bound_box];center=sum(points,Vector())/8
world=bpy.data.worlds.new('Neutral roof preview');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.08,.10,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;bpy.context.scene.world=world
for offset,power in [((3,-5,8),1100),((-4,3,5),650)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset));obj=bpy.context.object;obj.data.energy=power;obj.data.size=5;obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=center+Vector((6,-7,8)));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=args.size;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.filepath=str(OUT/'north_neutral.png')
bpy.ops.render.render(write_still=True)
print('NORTHERN239_NEUTRAL_RENDERED')
