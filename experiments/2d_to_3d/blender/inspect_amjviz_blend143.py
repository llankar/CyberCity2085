"""Inspect acquired original Blender file without executing its embedded scripts."""
import hashlib,json
from pathlib import Path
import bpy

folder=Path('E:/CyberCity2085-3d-lab/sources/blenderkit_cyberpunk143')
path=folder/'source.blend';assert path.stat().st_size==493590799
bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
objects=[]
for obj in bpy.context.scene.objects:
    if obj.type not in ('MESH','ARMATURE'):continue
    row={'name':obj.name,'type':obj.type}
    if obj.type=='MESH':
        row.update(vertices=len(obj.data.vertices),faces=len(obj.data.polygons),
                   materials=[m.name if m else None for m in obj.data.materials],
                   modifiers=[m.type for m in obj.modifiers])
    else:
        row.update(bones=len(obj.data.bones),deform_bones=sum(b.use_deform for b in obj.data.bones),
                   clips=[t.name for t in obj.animation_data.nla_tracks] if obj.animation_data else [])
    objects.append(row)
images=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'path':i.filepath}
        for i in bpy.data.images if i.source=='FILE']
report={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_bytes':path.stat().st_size,
        'objects':objects,'images':images,'embedded_script_execution':False,
        'missing_unpacked_images':[i['name'] for i in images if not i['packed'] and not Path(bpy.path.abspath(i['path'])).is_file()]}
assert not report['missing_unpacked_images']
(folder/'blender_inventory.json').write_text(json.dumps(report,indent=2))
print('AMJVIZ_BLENDER_SOURCE_OPEN_OK',len(objects),'objects',len(images),'file images',flush=True)
