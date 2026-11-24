"""Add explicitly adapted authored metal/cable channels to the human study."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).parent))
from charge_pbr import channels, bake_object

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'einar_pbr01'; folder.mkdir(parents=True,exist_ok=True)
resume='--resume' in sys.argv
previous=json.loads((folder/'coverage.json' if resume else root/'einar_dielectrics01/coverage.json').read_text())
completed=previous.get('baked',previous.get('dielectric_baked',[]))+previous.get('mechanical_baked',[])
bpy.ops.wm.open_mainfile(filepath=str(folder/'human_pbr.blend' if resume else root/'einar_dielectrics01/human_partial.blend'),use_scripts=False)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
pending=[o for o in objects if o.name not in completed]
names=tuple(o.name for o in pending)
with bpy.data.libraries.load(str(root/'einar_geometry01/einar_evaluated.blend'),link=False) as (source,target):
    assert all(name in source.objects for name in names)
    target.objects=list(names)
originals=dict(zip(names,target.objects))
scene=bpy.data.scenes.new('HumanMechanicsBake'); bpy.context.window.scene=scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=1
scene.render.bake.margin=4
report={'dielectric_baked':previous.get('baked',previous.get('dielectric_baked',[])),
        'mechanical_baked':list(previous.get('mechanical_baked',[])),'unresolved':[],
        'total_meshes':len(objects),'credit':previous['credit'],'license':previous['license'],
        'limitations':['Static unoptimized derivative; no rig/actions or curve hair',
                       'Subsurface, glass, emission and full artistic fidelity not accepted']}
for index,obj in enumerate(pending):
    original=originals[obj.name]
    materials=[slot.material for slot in original.material_slots]
    try:
        for material in materials: channels(material)
    except ValueError as error:
        report['unresolved'].append({'object':obj.name,'reason':str(error)})
    else:
        obj.data.materials.clear()
        for material in materials: obj.data.materials.append(material)
        scene.collection.objects.link(obj); obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bake_object(obj,folder,f'mechanic_{"resume_" if resume else ""}{index:03d}',size=256)
        obj.select_set(False); scene.collection.objects.unlink(obj)
        report['mechanical_baked'].append(obj.name)
    (folder/'coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('HUMAN_MECHANICS_COVERAGE',index+1,len(pending),len(report['mechanical_baked']),flush=True)
for obj in objects: scene.collection.objects.link(obj); obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'human_pbr.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder/'human_pbr.glb'),export_format='GLB',
                        use_selection=True,use_active_scene=True,export_animations=False)
print('HUMAN_MECHANICS_EXPORTED',flush=True)
