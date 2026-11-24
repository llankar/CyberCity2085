"""Mesh evaluated authored hair with lightweight triangular strand profiles."""
import json
import math
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'einar_hair01'; folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/sources/charge_studio/einar_release_v1.blend',use_scripts=False)
source_scene=bpy.context.scene
objects=[]
for obj in bpy.data.objects:
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            if 'depsgraph.scene.camera' in driver.driver.expression: driver.mute=True
graph=bpy.context.evaluated_depsgraph_get()
report={'parts':[],'credit':'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
        'license':'https://creativecommons.org/licenses/by/4.0/',
        'limitations':['Deterministic subset of authored strands; no film hair shader',
                       'Approximate gray/brown strand palette; not source-color fidelity',
                       'Static triangular strands; head attachment and deformation still pending',
                       'No alpha cards or final hair LOD/antialiasing acceptance'],
        'prior_failure':'Reading evaluated CURVES.data did not include final GN deformation; strands appeared at feet. Replaced with explicit GN mesh output.'}
for name,budget,gray in [('GEO-einar_beard',2200,True),('GEO-einar_mustache',800,True),
                         ('GEO-einar_eyebrows',400,True),('GEO-einar_hair',800,False)]:
    source=bpy.data.objects[name]
    count=len(source.data.curves)
    step=max(1,math.ceil(count/budget))
    tree=bpy.data.node_groups.new(name+'_GameStrandMeshing','GeometryNodeTree')
    tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    incoming=tree.nodes.new('NodeGroupInput'); output=tree.nodes.new('NodeGroupOutput')
    info=tree.nodes.new('GeometryNodeObjectInfo'); info.inputs['Object'].default_value=source
    info.transform_space='ORIGINAL'
    index=tree.nodes.new('GeometryNodeInputIndex')
    modulo=tree.nodes.new('ShaderNodeMath'); modulo.operation='MODULO'; modulo.inputs[1].default_value=step
    tree.links.new(index.outputs[0],modulo.inputs[0])
    comparison=tree.nodes.new('ShaderNodeMath'); comparison.operation='GREATER_THAN'; comparison.inputs[1].default_value=.5
    tree.links.new(modulo.outputs[0],comparison.inputs[0])
    delete=tree.nodes.new('GeometryNodeDeleteGeometry'); delete.domain='CURVE'
    tree.links.new(info.outputs['Geometry'],delete.inputs['Geometry'])
    tree.links.new(comparison.outputs[0],delete.inputs['Selection'])
    resample=tree.nodes.new('GeometryNodeResampleCurve'); resample.inputs['Count'].default_value=6
    tree.links.new(delete.outputs['Geometry'],resample.inputs['Curve'])
    profile=tree.nodes.new('GeometryNodeCurvePrimitiveCircle'); profile.inputs['Resolution'].default_value=3
    profile.inputs['Radius'].default_value=.0005
    meshing=tree.nodes.new('GeometryNodeCurveToMesh')
    radius=tree.nodes.new('GeometryNodeSetCurveRadius'); radius.inputs['Radius'].default_value=1.0
    tree.links.new(resample.outputs['Curve'],radius.inputs['Curve'])
    tree.links.new(radius.outputs['Curve'],meshing.inputs['Curve'])
    tree.links.new(profile.outputs['Curve'],meshing.inputs['Profile Curve'])
    tree.links.new(meshing.outputs['Mesh'],output.inputs['Geometry'])
    carrier=bpy.data.objects.new(name+'_MeshEvaluationCarrier',bpy.data.meshes.new(name+'_EmptyCarrier'))
    source_scene.collection.objects.link(carrier)
    carrier.matrix_world=source.matrix_world
    modifier=carrier.modifiers.new('ExperimentalGameStrands','NODES'); modifier.node_group=tree
    bpy.context.view_layer.update(); graph=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(carrier.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
    mesh.transform(carrier.matrix_world); mesh.calc_loop_triangles()
    assert mesh.vertices and mesh.polygons
    # Wrong-space raw curves previously put facial hair at the feet.
    low=min(v.co.z for v in mesh.vertices); high=max(v.co.z for v in mesh.vertices)
    assert 1.2<low<high<2.1,(name,low,high)
    obj=bpy.data.objects.new(name+'_GameHair',mesh)
    mesh.materials.clear()
    for level in range(3):
        material=bpy.data.materials.new(name+'_StrandPalette_'+str(level)); material.use_nodes=True
        shader=material.node_tree.nodes['Principled BSDF']
        value=(.22+level*.13) if gray else (.025+level*.018)
        shader.inputs['Base Color'].default_value=(value,value*.9,value*.78,1)
        shader.inputs['Roughness'].default_value=.72
        material.use_backface_culling=False
        mesh.materials.append(material)
    for polygon in mesh.polygons: polygon.material_index=(polygon.index//5)%3
    objects.append(obj)
    report['parts'].append({'source':name,'source_curves':count,'stride':step,
                            'triangles':len(mesh.loop_triangles),'vertices':len(mesh.vertices),
                            'z_bounds':[low,high]})
coverage=json.loads((root/'einar_pbr01/coverage.json').read_text())
names=tuple(coverage['dielectric_baked']+coverage['mechanical_baked'])
with bpy.data.libraries.load(str(root/'einar_pbr01/human_pbr.blend'),link=False) as (source,target):
    target.objects=list(names)
objects.extend(target.objects)
game_scene=bpy.data.scenes.new('HumanWithAuthoredHair')
bpy.context.window.scene=game_scene
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    if obj.name not in game_scene.objects: game_scene.collection.objects.link(obj)
    obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
report['hair_triangles']=sum(p['triangles'] for p in report['parts'])
assert 0<report['hair_triangles']<200000
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_hair.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_hair.glb'),export_format='GLB',
                        use_selection=True,use_active_scene=True,export_animations=False)
(folder/'hair_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EINAR_AUTHORED_HAIR_EXPORTED',report['hair_triangles'],flush=True)
