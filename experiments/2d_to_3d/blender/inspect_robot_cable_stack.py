import sys,json
from pathlib import Path
import bpy
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_authored_scene
s=load_authored_scene(Path('E:/CyberCity2085-3d-lab/sources/charge_studio/security_bot_v1/security_bot_release_v1.blend'))
r=bpy.data.objects['RIG-security_bot'];root=r.pose.bones['Root'];rw=r.matrix_world@root.matrix.copy();feet=[r.pose.bones['IK-Foot.'+side] for side in ['L','R']];fw=[r.matrix_world@f.matrix.copy() for f in feet]
o=bpy.data.objects['GEO-cable_tube_leg_lower.L'];mods=list(o.modifiers);mods[0].fit_type='FIXED_COUNT';mods[0].count=28
report=[]
for lower in [0,.2]:
 root.matrix=r.matrix_world.inverted()@Matrix.Translation((0,0,-lower))@rw;r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
 for f,w in zip(feet,fw):f.matrix=r.matrix_world.inverted()@w
 r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
 for m in mods:m.show_viewport=False
 data={'lower':lower,'base_vertices':len(o.data.vertices),'prefix_counts':[]}
 for m in mods:
  if m.type=='NODES':continue
  m.show_viewport=True;o.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh();data['prefix_counts'].append([m.name,len(mesh.vertices)]);e.to_mesh_clear()
 report.append(data)
print('CABLE_PREFIX_TOPOLOGY',json.dumps(report),flush=True)
Path('E:/CyberCity2085-3d-lab/tmp/robot_cable_prefix.json').write_text(json.dumps(report,indent=2))
