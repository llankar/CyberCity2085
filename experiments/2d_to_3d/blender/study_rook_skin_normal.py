"""Controlled material-intensity candidate, not a normal convention bug fix."""
import hashlib,json,sys,shutil
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent.parent))
from glb_document import Glb
from skin_normal_strength import set_skin_strength

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'rook_single_neck138';out=root/'rook_normal_strength139';out.mkdir(exist_ok=True)
strength=.35
glb=Glb(source/'human.glb');original_doc=glb.doc;binary=bytes(glb.bin)
glb.doc=set_skin_strength(glb.doc,strength);glb.save(out/'human.glb')
check=Glb(out/'human.glb');assert bytes(check.bin)==binary
material=next(m for m in check.doc['materials'] if m.get('name')=='sm004_head')
material['normalTexture'].pop('scale');assert check.doc==original_doc
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
material=bpy.data.materials['sm004_head'];normal=next(n for n in material.node_tree.nodes if n.type=='NORMAL_MAP')
assert normal.inputs['Strength'].default_value==1
normal.inputs['Strength'].default_value=strength
bpy.ops.wm.save_as_mainfile(filepath=str(out/'human.blend'))
shutil.copyfile(source/'native_reference.json',out/'native_reference.json')
notice=(source/'CREDITS.txt').read_text()+'\n139skin normal intensity study35percent; actual normal/photo images and geometry unchanged. Artistic calibration, not established handedness/import correction.\n'
(out/'CREDITS.txt').write_text(notice,encoding='utf-8')
(out/'material_report.json').write_text(json.dumps({'source_glb_sha256':hashlib.sha256((source/'human.glb').read_bytes()).hexdigest(),
    'glb_sha256':hashlib.sha256((out/'human.glb').read_bytes()).hexdigest(),'normal_strength':strength,
    'binary_and_non_scale_json_exact':True,'scope':'Material calibration candidate; no normal convention bug fix or final character acceptance'},indent=2))
print('ORIGINAL_SKIN_NORMAL_INTENSITY_STUDY_EXPORTED',strength,flush=True)
