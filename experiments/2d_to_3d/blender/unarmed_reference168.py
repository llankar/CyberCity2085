"""Render an actual retained clothed character in unarmed rest pose for Hunyuan."""
from pathlib import Path
import bpy
from mathutils import Vector,Matrix

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
out=root/'reference168';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'sole_skin162/human.blend'),use_scripts=False)
scene=bpy.context.scene
for obj in list(scene.objects):
    if obj.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(obj,do_unlink=True)
    elif obj.type=='ARMATURE':
        obj.animation_data_clear()
        for bone in obj.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    elif obj.type=='MESH' and obj.name.startswith('EquippedPistol_'):
        obj.hide_render=True
bpy.context.view_layer.update()
points=[]
for obj in scene.objects:
    if obj.type=='MESH' and not obj.hide_render:
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh=evaluated.to_mesh()
        points.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
        evaluated.to_mesh_clear()
low=Vector([min(v[i] for v in points) for i in range(3)])
high=Vector([max(v[i] for v in points) for i in range(3)])
center=(low+high)/2
bpy.ops.object.camera_add()
camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=max(high-low)*1.15
scene.camera=camera
world=bpy.data.worlds.new('ReferenceNeutral');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;scene.world=world
for offset,energy in [((-3,-4,4),450),((3,2,3),300)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(offset))
    light=bpy.context.object;light.data.energy=energy;light.data.shape='DISK';light.data.size=4
    light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
for name,direction in [('front',(0,-4,0)),('side',(4,0,0)),('back',(0,4,0))]:
    camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'unarmed.blend'))
print('UNARMED_REFERENCE168_RENDERED',flush=True)
