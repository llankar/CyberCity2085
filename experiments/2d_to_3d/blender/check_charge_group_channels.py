"""Native regression checks for lifted group channels and emission strength."""
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import channels

material=bpy.data.materials.new('GroupAdapterRegression'); material.use_nodes=True
tree=bpy.data.node_groups.new('SH-cable.Regression','ShaderNodeTree')
tree.interface.new_socket(name='BSDF',in_out='OUTPUT',socket_type='NodeSocketShader')
output=tree.nodes.new('NodeGroupOutput')
shader=tree.nodes.new('ShaderNodeBsdfPrincipled')
shader.inputs['Base Color'].default_value=(.12,.25,.4,1)
shader.inputs['Emission Color'].default_value=(.1,.2,.3,1)
shader.inputs['Emission Strength'].default_value=3
tree.links.new(shader.outputs[0],output.inputs['BSDF'])
group=material.node_tree.nodes.new('ShaderNodeGroup'); group.node_tree=tree
result=channels(material)
assert set(result)=={'BaseColor','Roughness','Metallic','Alpha','Emission'}
assert abs(output.inputs['GameBake_BaseColor'].default_value[0]-.12)<1e-6
emission=output.inputs['GameBake_Emission'].links[0].from_node
assert emission.type=='VECT_MATH' and emission.operation=='SCALE'
assert emission.inputs['Scale'].default_value==3
assert tuple(emission.inputs[0].default_value)==tuple(shader.inputs['Emission Color'].default_value[:3])
assert channels(material)['Emission']==result['Emission']
# An altered source group must be refused rather than reading a dead shader.
mix=tree.nodes.new('ShaderNodeMixShader')
tree.links.new(mix.outputs[0],output.inputs['BSDF'])
try: channels(material)
except ValueError: pass
else: raise AssertionError('Ambiguous changed group was not refused')
print('CHARGE_GROUP_REGRESSION_OK color,strength,cached_outputs,changed_route_refusal',flush=True)
