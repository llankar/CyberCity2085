"""One visual material comparison, same mesh/camera/lights as the neutral review."""
from pathlib import Path
import bpy,argparse,sys
parser=argparse.ArgumentParser();parser.add_argument('--folder',default='E:/CyberCity2085-3d-lab/generated/phase2/paint168/robot_official')
folder=Path(parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []).folder).resolve()
assert folder.drive.upper()=='E:'
bpy.ops.wm.open_mainfile(filepath=str(folder/'review/model.blend'),use_scripts=False)
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='BSDF_PRINCIPLED':
            node.inputs['Metallic'].default_value=.15
            node.inputs['Roughness'].default_value=.58
bpy.context.scene.render.filepath=str(folder/'painted_isometric.png')
bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/('painted_robot.blend' if folder.name=='robot_official' else 'painted_model.blend')))
print('PAINTED_ROBOT_VISUAL_RENDERED',flush=True)
