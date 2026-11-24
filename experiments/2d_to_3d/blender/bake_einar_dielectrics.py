"""Convert explicit cloth/skin source surfaces; account for every remaining part."""
import json
import sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from charge_dielectric import bake_dielectric

folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/einar_dielectrics01')
folder.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/einar_geometry01/einar_evaluated.blend', use_scripts=False)
objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
scene = bpy.data.scenes.new('IsolatedHumanDielectrics')
bpy.context.window.scene = scene
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 1
scene.render.bake.use_pass_direct = False; scene.render.bake.use_pass_indirect = False
scene.render.bake.use_pass_color = True; scene.render.bake.margin = 8
approved = {'einar.skin', 'einar.skin.fingers', 'einar.hat', 'einar.jacket.collar',
            'einar.jacket.canvas', 'einar.jacket.rim', 'einar.pants_fabric',
            'einar.pants_tarp', 'einar.pants_leather', 'einar.glove', 'einar.sweater',
            'einar.boots', 'einar.boots_soles', 'satchel', 'einar.cover', 'einar.tongue',
            'eianar.gums', 'einar.teeth', 'eyes.pupil', 'eyes.iris', 'eyes.white'}
diagnostic = bpy.data.materials.new('UnconvertedSourceSurface_NotFinal')
diagnostic.use_nodes = True
diagnostic.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.2, .23, .26, 1)
report = {'baked': [], 'unresolved': [], 'total_meshes': len(objects),
          'credit': 'Einar Rig (CC-BY) Blender Foundation | studio.blender.org',
          'license': 'https://creativecommons.org/licenses/by/4.0/',
          'limitations': ['Dielectric diffuse pass only; subsurface/eyes fidelity unverified',
                         'Metal and corneal shaders intentionally unconverted',
                         'No hair curves or exported rig/actions; not artistic acceptance']}
for index, obj in enumerate(objects):
    scene.collection.objects.link(obj); obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    names = {s.material.name for s in obj.material_slots if s.material}
    reason = None
    if not names or not names <= approved:
        reason = 'Not approved dielectric: ' + ', '.join(sorted(names))
    else:
        try: bake_dielectric(obj, folder, f'human_{index:03d}')
        except ValueError as error: reason = str(error)
    if reason:
        report['unresolved'].append({'object': obj.name, 'reason': reason})
        for slot in obj.material_slots: slot.material = diagnostic
    else: report['baked'].append(obj.name)
    obj.select_set(False); scene.collection.objects.unlink(obj)
    (folder / 'coverage.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('HUMAN_DIELECTRIC_COVERAGE', index + 1, len(report['baked']), flush=True)
for obj in objects: scene.collection.objects.link(obj); obj.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'human_partial.blend'))
bpy.ops.export_scene.gltf(filepath=str(folder / 'human_partial.glb'), export_format='GLB',
                         use_selection=True, use_active_scene=True, export_animations=False)
print('HUMAN_DIELECTRICS_EXPORTED', flush=True)
