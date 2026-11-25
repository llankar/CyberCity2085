"""Preserve authored groom radii/taper and bake its real palette to vertex color.

This approximates the clean primary hair surface; layered film blood/diffuse FX
and exact per-fiber shader random numbers are not reproduced.
"""
import json
import math
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from authored_scene import load_einar_scene
source_scene=load_einar_scene()
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
full_density='--full-density' in sys.argv
layered='--layered-palette' in sys.argv
compensate='--width-compensation' in sys.argv
folder=root/(('einar_groom_full02' if full_density else 'einar_groom02')+('_layered' if layered else '')+('_lod' if compensate else '')); folder.mkdir(exist_ok=True)
scene=bpy.data.scenes.new('AuthoredGroomStudy'); scene.render.engine='CYCLES'
scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.target='VERTEX_COLORS'
parts=[]; objects=[]
for name,budget in [('GEO-einar_beard',2200),('GEO-einar_mustache',800),('GEO-einar_eyebrows',400),('GEO-einar_hair',800)]:
    bpy.context.window.scene=source_scene
    bpy.context.view_layer.update()
    source=bpy.data.objects[name]; count=len(source.data.curves)
    tree=bpy.data.node_groups.new(name+'_NaturalGroom','GeometryNodeTree')
    tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    output=tree.nodes.new('NodeGroupOutput')
    info=tree.nodes.new('GeometryNodeObjectInfo'); info.inputs['Object'].default_value=source
    info.transform_space='ORIGINAL'; geometry=info.outputs['Geometry']
    index=tree.nodes.new('GeometryNodeInputIndex')
    random=tree.nodes.new('FunctionNodeRandomValue'); random.data_type='FLOAT'
    random.inputs['Seed'].default_value=137; tree.links.new(index.outputs[0],random.inputs['ID'])
    parameter=tree.nodes.new('GeometryNodeSplineParameter')
    radius=tree.nodes.new('GeometryNodeInputRadius')
    diameter=tree.nodes.new('ShaderNodeMath'); diameter.operation='MULTIPLY'; diameter.inputs[1].default_value=2
    tree.links.new(radius.outputs[0],diameter.inputs[0])
    length=tree.nodes.new('GeometryNodeSplineLength')
    for attribute,domain,field in [('GameHairRandom','CURVE',random.outputs['Value']),
            ('GameHairIntercept','POINT',parameter.outputs['Factor']),
            ('GameHairThickness','POINT',diameter.outputs[0]),('GameHairLength','CURVE',length.outputs['Length'])]:
        store=tree.nodes.new('GeometryNodeStoreNamedAttribute'); store.data_type='FLOAT'; store.domain=domain
        store.inputs['Name'].default_value=attribute
        tree.links.new(geometry,store.inputs['Geometry']); tree.links.new(field,store.inputs['Value'])
        geometry=store.outputs['Geometry']
    stride=1 if full_density else max(1,math.ceil(count/budget))
    width_scale=math.sqrt(stride) if compensate else 1.0
    modulo=tree.nodes.new('ShaderNodeMath'); modulo.operation='MODULO'; modulo.inputs[1].default_value=stride
    tree.links.new(index.outputs[0],modulo.inputs[0])
    compare=tree.nodes.new('ShaderNodeMath'); compare.operation='GREATER_THAN'; compare.inputs[1].default_value=.5
    tree.links.new(modulo.outputs[0],compare.inputs[0])
    delete=tree.nodes.new('GeometryNodeDeleteGeometry'); delete.domain='CURVE'
    tree.links.new(geometry,delete.inputs['Geometry']); tree.links.new(compare.outputs[0],delete.inputs['Selection'])
    resample=tree.nodes.new('GeometryNodeResampleCurve'); resample.inputs['Count'].default_value=6
    tree.links.new(delete.outputs['Geometry'],resample.inputs['Curve'])
    profile=tree.nodes.new('GeometryNodeCurvePrimitiveCircle'); profile.inputs['Resolution'].default_value=3
    profile.inputs['Radius'].default_value=1
    meshing=tree.nodes.new('GeometryNodeCurveToMesh')
    tree.links.new(resample.outputs['Curve'],meshing.inputs['Curve']); tree.links.new(profile.outputs['Curve'],meshing.inputs['Profile Curve'])
    scaled_radius=tree.nodes.new('ShaderNodeMath'); scaled_radius.operation='MULTIPLY'; scaled_radius.inputs[1].default_value=width_scale
    tree.links.new(radius.outputs[0],scaled_radius.inputs[0])
    if 'Scale' in meshing.inputs: tree.links.new(scaled_radius.outputs[0],meshing.inputs['Scale'])
    elif compensate:
        adjusted=tree.nodes.new('GeometryNodeSetCurveRadius')
        tree.links.new(resample.outputs['Curve'],adjusted.inputs['Curve']); tree.links.new(scaled_radius.outputs[0],adjusted.inputs['Radius'])
        tree.links.new(adjusted.outputs['Curve'],meshing.inputs['Curve'])
    tree.links.new(meshing.outputs['Mesh'],output.inputs['Geometry'])
    carrier=bpy.data.objects.new(name+'_GroomCarrier',bpy.data.meshes.new(name+'_Carrier'))
    source_scene.collection.objects.link(carrier)
    modifier=carrier.modifiers.new('NaturalGroom','NODES'); modifier.node_group=tree
    bpy.context.view_layer.update(); graph=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(carrier.evaluated_get(graph),preserve_all_data_layers=True,depsgraph=graph)
    # Object Info ORIGINAL yields local groom geometry. Its constrained source
    # transform must be read after depsgraph evaluation, not from a stale carrier.
    mesh.transform(source.matrix_world.copy()); mesh.calc_loop_triangles()
    thickness=mesh.attributes.get('GameHairThickness'); assert thickness and thickness.data
    widths=[item.value for item in thickness.data]
    assert 0<max(widths)<.01,('Unexpected authored strand width',name,min(widths),max(widths))
    low=min(v.co.z for v in mesh.vertices); high=max(v.co.z for v in mesh.vertices)
    assert 1.2<low<high<2.1,(name,low,high)
    material=source.data.materials[0].copy(); nodes=material.node_tree.nodes; links=material.node_tree.links
    shader=nodes['Principled BSDF']; color=shader.inputs['Base Color']
    assert color.links,'Expected authored palette route'
    for node in list(nodes):
        if node.type!='HAIR_INFO': continue
        for socket in node.outputs:
            for link in list(socket.links):
                if socket.name in {'Random','Intercept','Thickness','Length'}:
                    attribute=nodes.new('ShaderNodeAttribute'); attribute.attribute_name='GameHair'+socket.name
                    links.new(attribute.outputs['Fac'],link.to_socket)
                elif socket.name=='Is Strand':
                    value=nodes.new('ShaderNodeValue'); value.outputs[0].default_value=1
                    links.new(value.outputs[0],link.to_socket)
                elif socket.name=='Tangent Normal':
                    geometry_node=nodes.new('ShaderNodeNewGeometry'); links.new(geometry_node.outputs['Normal'],link.to_socket)
                else: raise ValueError('Unsupported Hair Info output: '+socket.name)
    palette=color.links[0].from_socket
    factor=None
    if layered:
        diffuse=nodes['Diffuse BSDF.001']; mixture=nodes['Mix Shader.003']
        assert mixture.inputs[1].links[0].from_node==shader and mixture.inputs[2].links[0].from_node==diffuse
        factor=mixture.inputs[0]
        blend=nodes.new('ShaderNodeMixRGB'); blend.blend_type='MIX'
        links.new(palette,blend.inputs[1])
        if diffuse.inputs['Color'].links: links.new(diffuse.inputs['Color'].links[0].from_socket,blend.inputs[2])
        else: blend.inputs[2].default_value=diffuse.inputs['Color'].default_value
        if factor.links: links.new(factor.links[0].from_socket,blend.inputs[0])
        else: blend.inputs[0].default_value=factor.default_value
        palette=blend.outputs[0]
    emission=nodes.new('ShaderNodeEmission'); links.new(palette,emission.inputs['Color'])
    material_output=next(node for node in nodes if node.type=='OUTPUT_MATERIAL' and node.is_active_output)
    links.new(emission.outputs[0],material_output.inputs['Surface'])
    mesh.materials.clear(); mesh.materials.append(material)
    obj=bpy.data.objects.new(name+'_NaturalGroom',mesh); scene.collection.objects.link(obj)
    bpy.context.window.scene=scene
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    colors=mesh.color_attributes.new(name='GameHairColor',type='FLOAT_COLOR',domain='CORNER')
    color_index=len(mesh.color_attributes)-1
    mesh.color_attributes.active_color_index=len(mesh.color_attributes)-1
    mesh.color_attributes.render_color_index=len(mesh.color_attributes)-1
    bpy.ops.object.bake(type='EMIT')
    diffuse_fraction=0.0
    if layered:
        mix_colors=mesh.color_attributes.new(name='GameHairDiffuseFraction',type='FLOAT_COLOR',domain='CORNER')
        mesh.color_attributes.active_color_index=len(mesh.color_attributes)-1
        if factor.links: links.new(factor.links[0].from_socket,emission.inputs['Color'])
        else:
            for link in list(emission.inputs['Color'].links): links.remove(link)
            emission.inputs['Color'].default_value=(factor.default_value,)*3+(1,)
        bpy.ops.object.bake(type='EMIT')
        diffuse_fraction=sum(value.color[0] for value in mix_colors.data)/len(mix_colors.data)
        mesh.color_attributes.active_color_index=color_index; mesh.color_attributes.render_color_index=color_index
        assert 0<=diffuse_fraction<=1.00001
    game_material=bpy.data.materials.new(name+'_AuthoredPalette'); game_material.use_nodes=True
    game_shader=game_material.node_tree.nodes['Principled BSDF']
    game_shader.inputs['Roughness'].default_value=shader.inputs['Roughness'].default_value
    game_shader.inputs['Specular IOR Level'].default_value=shader.inputs['Specular IOR Level'].default_value*(1-diffuse_fraction)
    vertex=game_material.node_tree.nodes.new('ShaderNodeVertexColor'); vertex.layer_name='GameHairColor'
    game_material.node_tree.links.new(vertex.outputs['Color'],game_shader.inputs['Base Color'])
    mesh.materials[0]=game_material
    objects.append(obj)
    parts.append({'source':name,'source_curves':count,'stride':stride,'triangles':len(mesh.loop_triangles),
                  'mean_authored_diffuse_mix':diffuse_fraction,
                  'lod_width_scale':width_scale,'render_diameter_max_m':max(widths)*width_scale,
                  'authored_diameter_range_m':[min(widths),max(widths)],'z_bounds':[low,high]})
    print('AUTHORED_GROOM_PART_BAKED',name,parts[-1],flush=True)
for obj in objects: obj.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'authored_groom.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'authored_groom.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
reference=json.loads((root/'einar_ual_Pistol_Shoot01_surfaces/rig_report.json').read_text())
head=next(item['joint'] for item in reference['joints_map'] if item['source']==['RIG-einar','DEF-Head'])
(folder/'groom_report.json').write_text(json.dumps({'parts':parts,'full_density':full_density,'width_compensation':compensate,'layered_clean_palette':layered,'head_joint':head,'credit':reference['credit'],
    'license':reference['license'],'limitations':['Clean primary/diffuse color mixture with uniform specular attenuation; film blood FX omitted' if layered else 'Clean primary shader palette only; film shader layering omitted','Deterministic per-strand random seed137, not exact film random identity','Static groom follows head, not lip/jaw expressions','Artistic and LOD acceptance not verified']},indent=2),encoding='utf-8')
print('AUTHORED_GROOM_EXPORTED',sum(part['triangles'] for part in parts),flush=True)
