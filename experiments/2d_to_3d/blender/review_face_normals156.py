"""Isolate current face normal strength; preserve real authored geometry and PBR maps."""
import copy, hashlib, json, sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'amjviz_wardrobe150';out=root/'face_review156';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human_actions.blend'),use_scripts=False)
body=bpy.data.materials.get('Body');assert body and body.use_nodes
nodes=[n for n in body.node_tree.nodes if n.type=='NORMAL_MAP'];assert len(nodes)==1
before=float(nodes[0].inputs['Strength'].default_value)
nodes[0].inputs['Strength'].default_value=.35
notice=(source/'CREDITS.txt').read_text()+'\n156 face material study: Body normal map strength0.35; original geometry, UV, skin, other materials and PBR images preserved. Not final likeness/art.\n'
bpy.data.texts.new('FACE_NORMAL156').write(notice)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human_face035.blend'))
original=Glb(source/'human_actions.glb')
for diagnostic in ('normal_off','metal_off'):
    test=copy.deepcopy(original)
    mat=next(m for m in test.doc['materials'] if m.get('name')=='Body')
    if diagnostic=='normal_off':mat['normalTexture']['scale']=0
    else:mat['pbrMetallicRoughness']['metallicFactor']=0
    test.save(out/(diagnostic+'.glb'))
variant=copy.deepcopy(original)
material=next(m for m in variant.doc['materials'] if m.get('name')=='Body')
assert 'normalTexture' in material
material['normalTexture']['scale']=.35
assert bytes(original.bin)==bytes(variant.bin)
variant.save(out/'human_face035.glb')
(out/'CREDITS.txt').write_text(notice)
report={'source_sha256':hashlib.sha256((source/'human_actions.glb').read_bytes()).hexdigest(),
        'variant_sha256':hashlib.sha256((out/'human_face035.glb').read_bytes()).hexdigest(),
        'original_blender_normal_strength':before,'candidate_strength':.35,
        'binary_payload_exact':True,'scope':'Material diagnostic, not geometry/likeness improvement or final acceptance'}
(out/'face_material.json').write_text(json.dumps(report,indent=2))
print('FACE_NORMAL156_SOURCE_READY',json.dumps(report))
