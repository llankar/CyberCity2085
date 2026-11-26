"""Adapt the existing PBR medical hard case into a spine-mounted equipment module."""
from pathlib import Path
import bpy,math,json
from mathutils import Matrix,Vector
LAB=Path('E:/CyberCity2085-3d-lab');OUT=LAB/'generated/phase2/medic201';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(LAB/'sources/environment169/medical_box/medical_box_1k.gltf'))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);center=(lo+hi)/2;scale=.42/max(hi-lo)
transform=Matrix.Rotation(-math.pi/2,4,'X')@Matrix.Scale(scale,4)@Matrix.Translation(-center)
for obj in meshes:
 obj.data=obj.data.copy();obj.data.transform(transform@obj.matrix_world);obj.parent=None;obj.matrix_world=Matrix.Identity(4);obj.name='MedicalPack201_'+obj.name
for obj in list(bpy.data.objects):
 if obj.type!='MESH':bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'medical_pack.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'medical_pack.glb'),export_format='GLB',use_selection=True)
(OUT/'equipment.json').write_text(json.dumps({'source':'local medical_box_1k.gltf','longest_original_axis_m':.42,'pose':'upright, lid facing character rear','scope':'genuine existing hard case adapted as detachable medical equipment, no body or garment edits'},indent=2));print('MEDICAL_PACK201_READY',len(meshes),flush=True)
