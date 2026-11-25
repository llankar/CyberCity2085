"""Read-only alpha footprint audit; raster evidence is not permission to discard alpha."""
import io
import json
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from compact_glb import unpack


def accessor(doc, binary, index):
    item=doc['accessors'][index]
    if 'sparse' in item or item.get('normalized'):
        raise ValueError('Unsupported accessor encoding')
    view=doc['bufferViews'][item['bufferView']]
    dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[item['componentType']]
    columns={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[item['type']]
    width=np.dtype(dtype).itemsize
    stride=view.get('byteStride',columns*width)
    offset=view.get('byteOffset',0)+item.get('byteOffset',0)
    return np.ndarray((item['count'],columns),dtype=dtype,buffer=binary,offset=offset,strides=(stride,width))


def footprint(size, coordinates, triangles):
    uv=np.asarray(coordinates)
    if not np.isfinite(uv).all() or uv.min()<0 or uv.max()>1:
        raise ValueError('Wrapped/out-of-range UVs need explicit repeat handling')
    mask=Image.new('L',size)
    draw=ImageDraw.Draw(mask)
    for tri in triangles:
        draw.polygon([(float(uv[i,0])*size[0],float(uv[i,1])*size[1]) for i in tri],fill=255)
    return mask


def audit(path,output):
    data=path.read_bytes();doc,binary=unpack(data)
    rows=[]
    for index,material in enumerate(doc['materials']):
        pbr=material.get('pbrMetallicRoughness',{})
        texture=pbr.get('baseColorTexture')
        if texture is None:raise ValueError('Expected textured source material')
        if texture.get('extensions'):raise ValueError('Texture transforms not audited')
        image_info=doc['images'][doc['textures'][texture['index']]['source']]
        view=doc['bufferViews'][image_info['bufferView']]
        start=view.get('byteOffset',0)
        rgba=Image.open(io.BytesIO(binary[start:start+view['byteLength']])).convert('RGBA')
        mask=Image.new('L',rgba.size);count=0
        for mesh in doc['meshes']:
            for primitive in mesh['primitives']:
                if primitive.get('material')!=index:continue
                if primitive.get('mode',4)!=4:raise ValueError('Expected triangles')
                uv=accessor(doc,binary,primitive['attributes']['TEXCOORD_'+str(texture.get('texCoord',0))])
                indices=accessor(doc,binary,primitive['indices']).reshape(-1,3)
                part=footprint(rgba.size,uv,indices)
                mask=Image.fromarray(np.maximum(np.asarray(mask),np.asarray(part)))
                count+=len(indices)
        alpha=np.asarray(rgba.getchannel('A'))
        selected=np.asarray(mask)>0
        margin=np.asarray(mask.filter(ImageFilter.MaxFilter(5)))>0
        if not selected.any():raise ValueError('Empty material footprint')
        row={'material':material['name'],'mode':material.get('alphaMode','OPAQUE'),
             'triangles':count,'texture_size':rgba.size,'texcoord':texture.get('texCoord',0),
             'alpha_factor':pbr.get('baseColorFactor',[1,1,1,1])[3],
             'whole_min_alpha':int(alpha.min()),'raster_footprint_min_alpha':int(alpha[selected].min()),
             'two_texel_margin_min_alpha':int(alpha[margin].min()),
             'raster_footprint_translucent_texels':int(np.count_nonzero(alpha[selected]<255)),
             'footprint_texels':int(selected.sum())}
        rows.append(row)
        if index==0:
            mask.save(output.parent/'first_material_footprint.png')
            rgba.save(output.parent/'first_material_rgba.png')
    assert path.read_bytes()==data, 'Read-only audit source changed during execution'
    result={'glb_sha256':hashlib.sha256(data).hexdigest(),'materials':rows,
            'counts':{'materials':len(rows),
                      'entire_basecolor_image_opaque':sum(r['whole_min_alpha']==255 for r in rows),
                      'footprint_contains_alpha_below_255':sum(r['raster_footprint_min_alpha']<255 for r in rows),
                      'two_texel_margin_opaque':sum(r['two_texel_margin_min_alpha']==255 for r in rows)},
            'limitations':['Conservative PIL triangle raster, not exact GPU coverage',
                          'Two texel margin does not cover every mip level',
                          'No alpha mutation or opaque acceptance inferred']}
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('ROBOT_ALPHA_AUDIT',len(rows),'footprints_with_nonopaque_texels',sum(r['raster_footprint_min_alpha']<255 for r in rows))


if __name__=='__main__':
    folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/security_alpha136')
    folder.mkdir(exist_ok=True)
    audit(folder.parent/'security_compact134/robot_actions.glb',folder/'alpha_audit.json')
