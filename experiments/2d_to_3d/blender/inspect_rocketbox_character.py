"""Import and inventory one pinned MIT game asset, preserving source files."""
import json
from pathlib import Path
import bpy

source=Path('E:/CyberCity2085-3d-lab/sources/rocketbox/Military_Male_03')
folder=Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03')
folder.mkdir(exist_ok=True)
acquisition=json.loads((source/'acquisition.json').read_text())
assert acquisition['manifest']['license']=='MIT'
notice=(source/'LICENSE.md').read_text()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source/'Export/Military_Male_03_facial.fbx'),use_anim=False)
textures={path.name.lower():path for path in (source/'Textures').iterdir() if path.is_file()}
images=[]
for image in bpy.data.images:
    if image.source!='FILE': continue
    name=Path(image.filepath.replace('\\','/')).name.lower()
    target=textures.get(name)
    if target is None: raise ValueError('Unresolved original texture: '+image.filepath)
    image.filepath=str(target); image.reload()
    images.append({'name':image.name,'file':name,'size':list(image.size),'space':image.colorspace_settings.name})
meshes=[]; rigs=[]
for obj in bpy.context.scene.objects:
    if obj.type=='ARMATURE':
        rigs.append({'name':obj.name,'bones':[{'name':bone.name,'parent':bone.parent.name if bone.parent else None,'deform':bone.use_deform} for bone in obj.data.bones]})
    if obj.type=='MESH':
        obj.data.calc_loop_triangles()
        meshes.append({'name':obj.name,'vertices':len(obj.data.vertices),'triangles':len(obj.data.loop_triangles),
            'dimensions':list(obj.dimensions),'materials':[slot.material.name for slot in obj.material_slots],
            'groups':len(obj.vertex_groups),'shapes':len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
            'modifiers':[{'type':m.type,'target':m.object.name if m.type=='ARMATURE' and m.object else None} for m in obj.modifiers],
            'visible':obj.visible_get(),'hidden_render':obj.hide_render})
materials=[]
for material in bpy.data.materials:
    shaders=[node for node in material.node_tree.nodes if node.type=='BSDF_PRINCIPLED'] if material.use_nodes else []
    materials.append({'name':material.name,'principled':[{'inputs':{socket.name:{'value':list(socket.default_value) if socket.type in {'RGBA','VECTOR'} else getattr(socket,'default_value',None),
        'links':[{'node':link.from_node.type,'socket':link.from_socket.name} for link in socket.links]} for socket in shader.inputs if socket.name in {'Base Color','Metallic','Roughness','Normal','Alpha','Specular IOR Level','Specular Tint'}}} for shader in shaders]})
bpy.data.texts.new('SOURCE_LICENSE_MIT').write(notice)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'imported_source.blend'))
report={'source_commit':acquisition['manifest']['commit'],'license':'MIT','copyright':'Copyright (c) 2020 Microsoft',
    'meshes':meshes,'rigs':rigs,'images':images,'materials':materials,'limitations':['Candidate inventory only; LOD selection, native render and artistic fit not accepted']}
(folder/'import_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ROCKETBOX_CHARACTER_IMPORTED',[(item['name'],item['triangles'],item['shapes']) for item in meshes],[(item['name'],len(item['bones'])) for item in rigs],len(images),flush=True)
