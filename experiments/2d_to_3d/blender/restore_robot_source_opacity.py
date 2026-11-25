"""Write editable derivative and direct GLB material patch; retain binary geometry."""
import hashlib,json,struct,sys,shutil
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent.parent))
from compact_glb import unpack
from robot_opacity import restore

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
report_path=root/'security_alpha137/source_alpha.json'
report=json.loads(report_path.read_text())
for path,sha in report['sources'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha
source=root/'security_compact134/robot_actions.glb'
raw=source.read_bytes();doc,binary=unpack(raw)
assert hashlib.sha256(raw).hexdigest()=='75a895b65ba7cf4d8ab93253bfaecb61a2b22e4f0fefba5ef85ee6650da946f5'
patched,changed=restore(doc,report)
assert len(changed)==122
encoded=json.dumps(patched,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
glb=struct.pack('<4sII',b'glTF',2,28+len(encoded)+len(binary))
glb+=struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary
verified,retained=unpack(glb)
assert retained==binary
for a,b in zip(doc['materials'],verified['materials']):
    if b['name'] in changed:b['alphaMode']='BLEND'
assert verified==doc, 'Only alphaMode may differ'
out=root/'security_opaque137';out.mkdir(exist_ok=True)
(out/'robot_actions.glb').write_bytes(glb)
blend=root/'security_bundle01/robot_actions.blend'
blend_sha=hashlib.sha256(blend.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(blend),use_scripts=False)
for name in changed:
    material=bpy.data.materials[name]
    shader=material.node_tree.nodes.get('Principled BSDF');assert shader
    for link in list(shader.inputs['Alpha'].links):material.node_tree.links.remove(link)
    shader.inputs['Alpha'].default_value=1
bpy.ops.wm.save_as_mainfile(filepath=str(out/'robot_actions.blend'))
assert hashlib.sha256(blend.read_bytes()).hexdigest()==blend_sha
shutil.copyfile(root/'security_bundle01/CREDITS.txt',out/'CREDITS.txt')
with (out/'CREDITS.txt').open('a',encoding='utf-8') as f:f.write('\n137 derivative restores source-proven opaque alpha on122materials;2unresolved materials retained BLEND. Binary geometry/actions/textures unchanged.\n')
proof={'source_glb_sha256':hashlib.sha256(raw).hexdigest(),'output_glb_sha256':hashlib.sha256(glb).hexdigest(),
       'source_alpha_audit_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),
       'source_blend_sha256':blend_sha,'changed_materials':changed,
       'retained_blend_materials':[m['name'] for m in patched['materials'] if m.get('alphaMode')=='BLEND'],
       'binary_and_non_alpha_json_exact':True,
       'limitations':['Intended opacity shading change, not pixel-identical export','Native visual review required',
                      'Direct GLB patch avoids known Blender animation roundtrip resampling']}
(out/'opacity_report.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print('ROBOT_SOURCE_OPACITY_RESTORED',len(changed),'retained_blend',proof['retained_blend_materials'],flush=True)
