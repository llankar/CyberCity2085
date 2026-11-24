"""Review licensed Charge geometry in neutral light without embedded rig UI scripts."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector

source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
output=Path(sys.argv[sys.argv.index('--')+2]).resolve()
if source.drive.upper()!='E:' or output.drive.upper()!='E:':
    raise ValueError('Use external assets/output')
output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
# First geometry review excludes expensive film-only procedural displacement.
# Preserve the authoring file; do not mistake this for full material acceptance.
disabled=[]
for obj in bpy.data.objects:
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            if 'RIG-Displacement' in driver.data_path:
                driver.mute=True
    for modifier in obj.modifiers:
        if modifier.type=='NODES' and 'Displacement' in modifier.name:
            modifier.show_render=False; modifier.show_viewport=False
            disabled.append(obj.name+':'+modifier.name)
print('REVIEW_DISABLED_FILM_DISPLACEMENT',len(disabled),flush=True)
collections=[c for c in bpy.data.collections if c.name.startswith('CH-')]
print('CHARGE_COLLECTIONS',[c.name for c in collections],flush=True)
name='CH-einar' if 'einar' in source.name else 'CH-security_bot'
collection=bpy.data.collections.get(name)
if collection is None:
    raise ValueError('Expected author collection not found: '+name)
scene=bpy.data.scenes.new('NeutralAssetReview')
scene.collection.children.link(collection)
bpy.context.window.scene=scene
# Preserve subdivision topology: Surface Deform bindings depend on vertex counts.
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1000; scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('NeutralReview')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
for location,energy in [((3,-4,5),700),((-3,1,4),500)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    bpy.context.object.data.energy=energy; bpy.context.object.data.size=4
bpy.ops.object.camera_add()
camera=bpy.context.object; camera.data.type='ORTHO'; camera.data.ortho_scale=2.5
target_height=.95
if 'einar' not in source.name:
    camera.data.ortho_scale=3.6
    target_height=1.2
scene.camera=camera
for label,location in [('front',(0,-5,1)),('side',(5,0,1)),('back',(0,5,1))]:
    camera.location=location
    camera.rotation_euler=(Vector((0,0,target_height))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(output/f'{label}.png')
    bpy.ops.render.render(write_still=True)
print('CHARGE_NEUTRAL_VIEWS_RENDERED',name,flush=True)
