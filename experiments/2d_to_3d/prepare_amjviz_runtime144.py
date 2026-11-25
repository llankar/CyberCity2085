"""Retain the author's compressed Godot materials and normalize source clip clocks."""
import copy,hashlib,json,sys
from pathlib import Path
from glb_document import Glb
from animation_time_origin import normalize_origins

root=Path('E:/CyberCity2085-3d-lab');out=root/'generated/phase2/amjviz_runtime144'
if '--all-bones-diagnostic' in sys.argv:out=root/'generated/phase2/amjviz_full144'
raw=out/'unshifted_export.glb'
if not raw.exists():
    (out/'human.glb').rename(raw)
    if (out/'native_bounds.json').exists():(out/'native_bounds.json').rename(out/'failed_unshifted_bounds.json')
target=Glb(raw);source=Glb(root/'sources/blenderkit_cyberpunk143/source_godot.glb')
before=[target.expanded_values(i) for i in range(len(target.doc['accessors']))]
origins=normalize_origins(target)
by_name={m['name']:m for m in source.doc['materials']}
assert set(by_name)=={m['name'] for m in target.doc['materials']}
target.doc['materials']=[copy.deepcopy(by_name[m['name']]) for m in target.doc['materials']]
for key in ('samplers','textures'):target.doc[key]=copy.deepcopy(source.doc[key])
images=[]
for image in source.doc['images']:
    image=copy.deepcopy(image);view=source.doc['bufferViews'][image['bufferView']]
    payload=source.bin[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
    target.bin.extend(b'\0'*(-len(target.bin)%4));new={'buffer':0,'byteOffset':len(target.bin),'byteLength':len(payload)}
    target.bin.extend(payload);image['bufferView']=len(target.doc['bufferViews'])
    target.doc['bufferViews'].append(new);images.append(image)
target.doc['images']=images
for key in ('extensionsUsed','extensionsRequired'):
    target.doc[key]=sorted(set(target.doc.get(key,[]))|set(source.doc.get(key,[])))
assert not set(target.doc.get('extensionsUsed',[]))-{'EXT_texture_webp','KHR_materials_clearcoat','KHR_materials_emissive_strength','KHR_materials_ior','KHR_materials_specular','KHR_materials_transmission'}
# Prune orphan image views while retaining every accessor, including geometry,
# skin binds, pose outputs and old shared clock accessors byte-for-byte.
assert all('sparse' not in a for a in target.doc['accessors'])
used={a['bufferView'] for a in target.doc['accessors']}|{i['bufferView'] for i in images}
mapping={old:new for new,old in enumerate(sorted(used))};packed=bytearray();views=[]
for old in sorted(used):
    view=copy.deepcopy(target.doc['bufferViews'][old]);start=view.get('byteOffset',0)
    payload=target.bin[start:start+view['byteLength']];packed.extend(b'\0'*(-len(packed)%4))
    view['byteOffset']=len(packed);packed.extend(payload);views.append(view)
for a in target.doc['accessors']:a['bufferView']=mapping[a['bufferView']]
for i in images:i['bufferView']=mapping[i['bufferView']]
target.doc['bufferViews']=views;target.bin=packed
assert all(target.expanded_values(i)==payload for i,payload in enumerate(before))
target.save(out/'human.glb')
for actual,original in zip(images,source.doc['images']):
    a=target.doc['bufferViews'][actual['bufferView']];b=source.doc['bufferViews'][original['bufferView']]
    assert target.bin[a['byteOffset']:a['byteOffset']+a['byteLength']]==source.bin[b.get('byteOffset',0):b.get('byteOffset',0)+b['byteLength']]
report={'raw_export_bytes':raw.stat().st_size,'output_bytes':(out/'human.glb').stat().st_size,
        'clip_origins':origins,'original_geometry_skin_pose_accessor_payloads_exact':True,
        'author_godot_compressed_image_payloads_exact':True,
        'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),
        'scope':'Relative clip-time normalization and reuse of authored Godot materials, not lossless PNG recompression'}
(out/'runtime_preparation.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_RUNTIME_PREPARED',report['output_bytes'],flush=True)
