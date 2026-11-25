"""Restore reviewed author game materials without changing mesh/animation payloads."""
import copy


def texture_infos(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key.endswith('Texture') and isinstance(child,dict) and 'index' in child:yield child
            else:yield from texture_infos(child)
    elif isinstance(value,list):
        for child in value:yield from texture_infos(child)


def restore(target,source):
    d,s=target.doc,source.doc
    supported=lambda ext:ext.startswith('KHR_materials_') or ext in ('EXT_texture_webp','KHR_texture_transform')
    if any(not supported(e) for e in set(d.get('extensionsUsed',[]))|set(s.get('extensionsUsed',[]))):
        raise ValueError('Binary extension needs explicit review')
    if any('sparse' in a for a in d.get('accessors',[])):raise ValueError('Expand sparse accessors first')
    original=[target.values(i) for i in range(len(d.get('accessors',[])))]
    materials={m['name']:m for m in s['materials']}
    if len(materials)!=len(s['materials']):raise ValueError('Source material names must be unique')
    image_offset=len(d.get('images',[]));texture_offset=len(d.get('textures',[]));sampler_offset=len(d.get('samplers',[]))
    d.setdefault('samplers',[]).extend(copy.deepcopy(s.get('samplers',[])))
    for image in s.get('images',[]):
        image=copy.deepcopy(image)
        if 'bufferView' not in image:raise ValueError('Embedded source images required')
        view=s['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
        payload=source.bin[start:start+view['byteLength']]
        target.bin.extend(b'\0'*(-len(target.bin)%4));image['bufferView']=len(d['bufferViews'])
        d['bufferViews'].append({'buffer':0,'byteOffset':len(target.bin),'byteLength':len(payload)})
        target.bin.extend(payload);d.setdefault('images',[]).append(image)
    for texture in s.get('textures',[]):
        texture=copy.deepcopy(texture)
        if 'source' in texture:texture['source']+=image_offset
        if 'sampler' in texture:texture['sampler']+=sampler_offset
        if 'EXT_texture_webp' in texture.get('extensions',{}):texture['extensions']['EXT_texture_webp']['source']+=image_offset
        d.setdefault('textures',[]).append(texture)
    matched=[]
    for index,material in enumerate(d['materials']):
        if material.get('name') not in materials:continue
        replacement=copy.deepcopy(materials[material['name']])
        for info in texture_infos(replacement):info['index']+=texture_offset
        d['materials'][index]=replacement;matched.append(material['name'])
    if not matched:raise ValueError('No matching reviewed materials')
    used_textures=sorted({info['index'] for info in texture_infos(d['materials'])})
    texture_map={old:new for new,old in enumerate(used_textures)}
    for info in texture_infos(d['materials']):info['index']=texture_map[info['index']]
    d['textures']=[d['textures'][i] for i in used_textures]
    used_images=set()
    for texture in d['textures']:
        if 'source' in texture:used_images.add(texture['source'])
        if 'EXT_texture_webp' in texture.get('extensions',{}):used_images.add(texture['extensions']['EXT_texture_webp']['source'])
    image_map={old:new for new,old in enumerate(sorted(used_images))}
    for texture in d['textures']:
        if 'source' in texture:texture['source']=image_map[texture['source']]
        if 'EXT_texture_webp' in texture.get('extensions',{}):
            texture['extensions']['EXT_texture_webp']['source']=image_map[texture['extensions']['EXT_texture_webp']['source']]
    d['images']=[d['images'][i] for i in sorted(used_images)]
    used_views={a['bufferView'] for a in d.get('accessors',[])}|{i['bufferView'] for i in d['images']}
    mapping={old:new for new,old in enumerate(sorted(used_views))};packed=bytearray();views=[]
    for old in sorted(used_views):
        view=copy.deepcopy(d['bufferViews'][old]);start=view.get('byteOffset',0)
        payload=target.bin[start:start+view['byteLength']];packed.extend(b'\0'*(-len(packed)%4))
        view['byteOffset']=len(packed);packed.extend(payload);views.append(view)
    for accessor in d.get('accessors',[]):accessor['bufferView']=mapping[accessor['bufferView']]
    for image in d['images']:image['bufferView']=mapping[image['bufferView']]
    d['bufferViews']=views;target.bin=packed
    for key in ('extensionsUsed','extensionsRequired'):d[key]=sorted(set(d.get(key,[]))|set(s.get(key,[])))
    assert all(target.values(i)==payload for i,payload in enumerate(original))
    return {'restored_materials':matched,'images':len(d['images']),'geometry_animation_accessors_exact':True}
