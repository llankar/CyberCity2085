"""Inventory a downloaded candidate without executing embedded Blender scripts."""
import json
import sys
from pathlib import Path
import bpy

source = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
output = Path(sys.argv[sys.argv.index('--') + 2]).resolve()
if source.drive.upper() != 'E:' or output.drive.upper() != 'E:':
    raise ValueError('Keep candidate inspection on E:')
bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
report = {'source': str(source), 'objects': [], 'texts': {}, 'images': [],
          'distribution_rights': 'NOT VERIFIED; inspection only'}
for obj in bpy.data.objects:
    entry = {'name': obj.name, 'type': obj.type, 'dimensions': list(obj.dimensions),
             'hidden_render': obj.hide_render}
    if obj.type == 'MESH':
        entry.update(vertices=len(obj.data.vertices), faces=len(obj.data.polygons),
                     materials=[s.material.name if s.material else None for s in obj.material_slots],
                     modifiers=[m.type for m in obj.modifiers])
    if obj.type == 'ARMATURE':
        entry['bones'] = len(obj.data.bones)
    report['objects'].append(entry)
for text in bpy.data.texts:
    report['texts'][text.name] = text.as_string()[:12000]
for image in bpy.data.images:
    report['images'].append({'name':image.name,'path':image.filepath,'packed':bool(image.packed_file)})
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CANDIDATE_INVENTORY',len(report['objects']),'objects; texts:',list(report['texts']))
print('CANDIDATE_RIGHTS_NOT_VERIFIED')
