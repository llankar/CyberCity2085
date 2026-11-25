"""Small explicit adapters for the inspected Charge robot material interfaces."""
import bpy


def scaled_emission(tree, shader):
    """Bake radiance color, including the authored emission strength."""
    node=tree.nodes.new('ShaderNodeVectorMath'); node.operation='SCALE'
    color=shader.inputs['Emission Color']; strength=shader.inputs['Emission Strength']
    if color.links: tree.links.new(color.links[0].from_socket,node.inputs[0])
    else: node.inputs[0].default_value=color.default_value[:3]
    if strength.links: tree.links.new(strength.links[0].from_socket,node.inputs['Scale'])
    else: node.inputs['Scale'].default_value=strength.default_value
    return node.outputs['Vector']


def channels(material):
    nodes=material.node_tree.nodes
    group=next((n for n in nodes if n.type=='GROUP' and n.node_tree.name.startswith(('SH-secbot.','SH-metal_base','SH-metal_road_sign'))),None)
    if group and all(name in group.outputs for name in ['Color','Roughness','Metallic']):
        return {key:group.outputs[name] for key,name in [('BaseColor','Color'),('Roughness','Roughness'),('Metallic','Metallic')]} | {'Alpha':1.0,'Emission':(0,0,0,1)}
    group=next((n for n in nodes if n.type=='GROUP' and n.node_tree.name.startswith(('SH-cable.','SH-rubber_pads.','SH-RubberHose.','SH-metal_road_sign.'))),None)
    if group:
        tree=group.node_tree
        output=next(n for n in tree.nodes if n.type=='GROUP_OUTPUT' and n.is_active_output)
        links=output.inputs['BSDF'].links
        if len(links)!=1 or links[0].from_node.type!='BSDF_PRINCIPLED':
            raise ValueError('Group no longer has inspected direct Principled route: '+tree.name)
        shader=links[0].from_node
        target='GameBake_Emission'
        if target not in group.outputs:
            tree.interface.new_socket(name=target,in_out='OUTPUT',socket_type='NodeSocketColor')
            tree.links.new(scaled_emission(tree,shader),output.inputs[target])
        result={'Emission':group.outputs[target]}
        for key,name in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic'),('Alpha','Alpha')]:
            target='GameBake_'+key
            if target not in group.outputs:
                socket=shader.inputs[name]
                tree.interface.new_socket(name=target,in_out='OUTPUT',socket_type='NodeSocketColor' if key=='BaseColor' else 'NodeSocketFloat')
                if socket.links:
                    tree.links.new(socket.links[0].from_socket,output.inputs[target])
                else:
                    output.inputs[target].default_value=socket.default_value
            result[key]=group.outputs[target]
        return result
    group=next((n for n in nodes if n.type=='GROUP' and n.node_tree.name.startswith('SH-decal')),None)
    if group:
        return {'BaseColor':group.outputs['Color'],'Roughness':group.outputs['Roughness'],
                'Metallic':0.0,'Alpha':group.outputs['Alpha'],'Emission':(0,0,0,1)}
    shaders=[n for n in nodes if n.type=='BSDF_PRINCIPLED']
    if len(shaders)!=1:
        raise ValueError('Unresolved layered/transmission shader: '+material.name)
    shader=shaders[0]
    result={'Emission':scaled_emission(material.node_tree,shader)}
    for key,name in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic'),('Alpha','Alpha')]:
        socket=shader.inputs[name]
        result[key]=socket.links[0].from_socket if socket.links else socket.default_value
    return result


def pin_source_uv(tree,seen):
    if tree.as_pointer() in seen: return
    seen.add(tree.as_pointer())
    uv=tree.nodes.new('ShaderNodeUVMap'); uv.uv_map='SourceUV'
    for node in list(tree.nodes):
        if node==uv: continue
        if node.type=='GROUP': pin_source_uv(node.node_tree,seen)
        if node.type=='UVMAP': node.uv_map='SourceUV'
        if node.type=='TEX_IMAGE' and not node.inputs['Vector'].links:
            tree.links.new(uv.outputs[0],node.inputs['Vector'])
        if node.type=='TEX_COORD':
            for link in list(node.outputs['UV'].links):
                tree.links.new(uv.outputs[0],link.to_socket)


def bake_object(obj,folder,prefix,size=256,preserve_source_uv=False):
    # Preflight every material before changing this object.
    for slot in obj.material_slots: channels(slot.material)
    if obj.data.uv_layers.active:
        obj.data.uv_layers.active.name='SourceUV'
    else:
        if preserve_source_uv: raise ValueError('Authored UVs required for UV-preserving bake')
        obj.data.uv_layers.new(name='SourceUV')
    source_uv=obj.data.uv_layers.active
    bake_uv=obj.data.uv_layers.new(name='BakeUV')
    obj.data.uv_layers.active=bake_uv; bake_uv.active_render=True
    if preserve_source_uv:
        for first,second in zip(source_uv.data,bake_uv.data): second.uv=first.uv
    else:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(island_margin=.025)
        bpy.ops.object.mode_set(mode='OBJECT')
    adapters=[]
    for slot in obj.material_slots:
        slot.material=slot.material.copy(); material=slot.material
        tree=material.node_tree
        pin_source_uv(tree,set())
        output=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        original=output.inputs['Surface'].links[0].from_socket
        emission=tree.nodes.new('ShaderNodeEmission'); target=tree.nodes.new('ShaderNodeTexImage')
        adapters.append((material,channels(material),output,original,emission,target))
    images={}
    for key in ['BaseColor','Roughness','Metallic','Alpha','Emission','Normal']:
        image=bpy.data.images.new(prefix+'_'+key,width=size,height=size,alpha=False)
        # Emission is a color channel too. Scalar maps and tangent normals are data.
        if key not in {'BaseColor','Emission'}: image.colorspace_settings.name='Non-Color'
        for material,values,output,original,emission,target in adapters:
            tree=material.node_tree; target.image=image; tree.nodes.active=target
            if key=='Normal':
                tree.links.new(original,output.inputs['Surface'])
            else:
                for link in list(emission.inputs['Color'].links): tree.links.remove(link)
                value=values[key]
                if hasattr(value,'node'):
                    tree.links.new(value,emission.inputs['Color'])
                else:
                    emission.inputs['Color'].default_value=(value,value,value,1) if isinstance(value,(int,float)) else value
                tree.links.new(emission.outputs[0],output.inputs['Surface'])
        bpy.ops.object.bake(type='NORMAL' if key=='Normal' else 'EMIT',uv_layer='BakeUV')
        image.filepath_raw=str(folder/f'{prefix}_{key}.png'); image.file_format='PNG'; image.save()
        images[key]=image
    material=bpy.data.materials.new(prefix+'_GamePBR'); material.use_nodes=True
    tree=material.node_tree; shader=tree.nodes['Principled BSDF']
    uv=tree.nodes.new('ShaderNodeUVMap'); uv.uv_map='BakeUV'
    for key,name in [('BaseColor','Base Color'),('Roughness','Roughness'),('Metallic','Metallic'),('Alpha','Alpha'),('Emission','Emission Color')]:
        texture=tree.nodes.new('ShaderNodeTexImage'); texture.image=images[key]
        tree.links.new(uv.outputs[0],texture.inputs['Vector'])
        tree.links.new(texture.outputs['Color'],shader.inputs[name])
    shader.inputs['Emission Strength'].default_value=1.0
    texture=tree.nodes.new('ShaderNodeTexImage'); texture.image=images['Normal']
    tree.links.new(uv.outputs[0],texture.inputs['Vector'])
    normal=tree.nodes.new('ShaderNodeNormalMap'); normal.uv_map='BakeUV'
    tree.links.new(texture.outputs['Color'],normal.inputs['Color'])
    tree.links.new(normal.outputs[0],shader.inputs['Normal'])
    for slot in obj.material_slots: slot.material=material
    return material
