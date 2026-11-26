"""Derive one quieter, varied material pass from the actual showcase174 source."""
from pathlib import Path
import bpy,json,numpy as np
LAB=Path('E:/CyberCity2085-3d-lab'); OUT=LAB/'generated/phase2/showcase183';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(LAB/'generated/phase2/showcase174/environment.blend'))
roots=sorted([o for o in bpy.data.objects if o.name.startswith('Occludable_')],key=lambda o:o.name)
palettes=[(.56,.65,.70),(.66,.58,.53),(.48,.57,.61)]
cache={}; changed=0

def tinted(source,palette):
    key=(source.name,palette)
    if key in cache:return cache[key]
    mat=source.copy();mat.name=source.name+'_District183_'+str(palette)
    shader=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
    if shader:
        socket=shader.inputs['Base Color']
        if socket.is_linked:
            tex=socket.links[0].from_node
            if tex.type=='TEX_IMAGE' and tex.image:
                img=tex.image.copy();img.name=mat.name
                px=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(px)
                px.reshape(-1,4)[:,:3]*=palettes[palette]
                img.pixels.foreach_set(px);img.update()
                img.filepath_raw=str(OUT/(f'district_{len(cache):03d}.png'));img.file_format='PNG';img.save();img.pack()
                tex.image=img
        else:
            c=list(socket.default_value);socket.default_value=tuple(c[i]*palettes[palette][i] for i in range(3))+(c[3],)
    cache[key]=mat;return mat

for index,root in enumerate(roots):
    for obj in root.children_recursive:
        if obj.type!='MESH':continue
        # Change only solid facade/roof surfaces; preserve authored glass, signs and props.
        if not (obj.name.startswith('AuthoredFacade_wall_') or obj.name.startswith('PBR_Facade_')):continue
        obj.data=obj.data.copy()
        for slot in obj.material_slots:
            if not slot.material:continue
            name=slot.material.name.lower()
            if any(word in name for word in ['glass','emiss','window_glass']):continue
            slot.material=tinted(slot.material,index%3);changed+=1
# The same giant valve repeated at alley positions was dominating the humans.
valves=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('modular_industrial_pipes_01_pipe08')]
for obj in valves:
    obj.scale*=.65
bpy.ops.object.select_all(action='SELECT')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'environment.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'environment.glb'),export_format='GLB',use_selection=True)
(OUT/'materials.json').write_text(json.dumps({'changed_slots':changed,'derived_materials':len(cache),'scaled_valves':len(valves),'scope':'same geometry footprints; derived local textures, no new models'},indent=2))
print('DISTRICT183_READY',changed,len(cache),len(valves),flush=True)
