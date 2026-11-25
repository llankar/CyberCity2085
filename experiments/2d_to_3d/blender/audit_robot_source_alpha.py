"""Trace original robot adapter alpha without mutating any saved source."""
import hashlib
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import channels

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'security_alpha137';folder.mkdir(exist_ok=True)
geometry=root/'security_geometry01/security_geometry.blend'
baked=root/'security_pbr_robot02/robot_pbr.blend'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (geometry,baked)}
bpy.ops.wm.open_mainfile(filepath=str(baked),use_scripts=False)
mapping={o.name:[s.material.name for s in o.material_slots] for o in bpy.context.scene.objects if o.type=='MESH'}
coverage=json.loads((baked.parent/'coverage.json').read_text())
adapted=set(coverage['adapted_visor'])
bpy.ops.wm.open_mainfile(filepath=str(geometry),use_scripts=False)

def constant(value,depth=0):
    if isinstance(value,(int,float)):return float(value)
    if depth>12:return None
    node=value.node
    if node.type=='GROUP':
        output=next(n for n in node.node_tree.nodes if n.type=='GROUP_OUTPUT' and n.is_active_output)
        socket=output.inputs.get(value.name)
        if socket is None:return None
        return constant(socket.links[0].from_socket,depth+1) if socket.links else constant(socket.default_value,depth+1)
    if node.type=='VALUE':return float(value.default_value)
    return None

rows=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    original=[]
    for slot in obj.material_slots:
        try:
            alpha=channels(slot.material)['Alpha']
            original.append({'name':slot.material.name,'constant_alpha':constant(alpha),
                             'route':alpha.node.type+':'+alpha.name if hasattr(alpha,'node') else 'adapter_literal'})
        except ValueError as error:
            assert obj.name in adapted, str(error)
            original.append({'name':slot.material.name,'constant_alpha':None,'route':'documented_opaque_visor_approximation'})
    rows.append({'object':obj.name,'baked_materials':mapping[obj.name],'source_materials':original,
                 'documented_opaque_visor_approximation':obj.name in adapted,
                 'all_adapter_alpha_constant_one':all(r['constant_alpha']==1 for r in original)})
assert len(rows)==124
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
report={'sources':hashes,'objects':rows,
        'counts':{'total':len(rows),'constant_opaque_adapter':sum(r['all_adapter_alpha_constant_one'] for r in rows),
                  'documented_opaque_visor_approximation':len(adapted)},
        'scope':'Source adapter opacity, not a GPU equivalence proof; unknown alpha preserved'}
(folder/'source_alpha.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROBOT_SOURCE_ALPHA_TRACED',json.dumps(report['counts']),flush=True)
