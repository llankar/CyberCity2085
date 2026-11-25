"""Inventory real material components across UV splits before modular extraction."""
import hashlib,json,sys
from pathlib import Path
import bpy

root=Path('E:/CyberCity2085-3d-lab/generated/phase2');source=root/'amjviz_wardrobe150/human_actions.blend'
p320='--p320' in sys.argv
if p320:source=root.parent.parent/'sources/blenderkit_p320153/source.blend'
out=root/'amjviz_components153';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
rig=next((o for o in bpy.context.scene.objects if o.type=='ARMATURE'),None)
if rig:rig.data.pose_position='REST';bpy.context.view_layer.update()
body=max((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
mesh=body.data;report=[]
for material_index,material in enumerate(mesh.materials):
    faces=[f for f in mesh.polygons if f.material_index==material_index]
    if not faces:continue
    ids={i for f in faces for i in f.vertices};parents={i:i for i in ids}
    def find(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b:parents[b]=a
    positions={}
    for i in ids:
        key=tuple(round(float(v)*1e6) for v in mesh.vertices[i].co)
        if key in positions:join(i,positions[key])
        else:positions[key]=i
    for face in faces:
        for i in face.vertices[1:]:join(face.vertices[0],i)
    components={}
    for face in faces:components.setdefault(find(face.vertices[0]),[]).append(face)
    for group in components.values():
        indices={i for f in group for i in f.vertices};points=[body.matrix_world@mesh.vertices[i].co for i in indices]
        influences={}
        for i in indices:
            for weight in mesh.vertices[i].groups:
                name=body.vertex_groups[weight.group].name;influences[name]=influences.get(name,0.)+weight.weight
        report.append({'material':material.name,'first_face':min(f.index for f in group),
            'faces':[f.index for f in group],'face_count':len(group),'vertices':len(indices),
            'bounds':[[min(p[j] for p in points) for j in range(3)],[max(p[j] for p in points) for j in range(3)]],
            'dominant_bones':sorted(influences,key=influences.get,reverse=True)[:5]})
report.sort(key=lambda c:c['face_count'],reverse=True)
(out/('p320_component_audit.json' if p320 else 'component_audit.json')).write_text(json.dumps({'source_blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'body':body.name,'components':report,'analysis_only_weld_tolerance_m':1e-6,
    'scope':'Connectivity across duplicate seam positions, not anatomy/garment semantics. Source mesh is unchanged.'},indent=2))
for component in report[:25]:print({k:v for k,v in component.items() if k!='faces'},flush=True)
print('AUTHORED_COMPONENTS_INVENTORIED',len(report),flush=True)
