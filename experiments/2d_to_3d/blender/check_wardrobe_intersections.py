"""Diagnostic visible-surface overlap audit; never an artistic acceptance gate."""
import json
import hashlib
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree

root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
folder=root/'wardrobe_fit01'
bpy.ops.wm.open_mainfile(filepath=str(folder/'human.blend'),use_scripts=False)
rig=bpy.data.objects['Bip01'];garment=bpy.data.objects['AuthoredLeatherJacket_PBRStudy']
others=[obj for obj in bpy.context.scene.objects if obj.type=='MESH' and obj!=garment]
details=json.loads((root/'rocketbox_military03/motion01/retarget_report.json').read_text())['clips']

def surface(obj,graph):
    evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
    mesh.calc_loop_triangles();points=[evaluated.matrix_world @ v.co for v in mesh.vertices]
    triangles=[];materials=[]
    for triangle in mesh.loop_triangles:
        material=mesh.materials[mesh.polygons[triangle.polygon_index].material_index]
        if material.name=='m014_opacity':continue # partial alpha cards need pixel-aware tests
        shader=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if shader and not shader.inputs['Alpha'].links and shader.inputs['Alpha'].default_value<.0001:continue
        triangles.append(tuple(triangle.vertices));materials.append(material.name)
    evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(points,triangles,all_triangles=True),points,triangles,materials

report={'blend_sha256':hashlib.sha256((folder/'human.blend').read_bytes()).hexdigest(),
        'clips':{},'scope':'45 sampled Blender poses, garment vs opaque visible body/head triangles; alpha-hidden original clothing and partial-alpha hair excluded. BVH overlap pairs require visible review; no continuous or cloth-self collision acceptance.'}
for clip,info in details.items():
    for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
    samples=[]
    for step in range(9):
        frame=(info['frames']-1)*step/8
        bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        graph=bpy.context.evaluated_depsgraph_get();tree,_,_,_=surface(garment,graph)
        found={}
        for obj in others:
            target,points,triangles,materials=surface(obj,graph)
            pairs=tree.overlap(target);locations=[]
            for _,index in pairs[:12]:
                center=sum((points[i] for i in triangles[index]),points[0]*0)/3
                locations.append({'target_material':materials[index],'target_triangle_center_m':list(center)})
            found[obj.name]={'overlap_pairs':len(pairs),'examples':locations}
        samples.append({'time_s':frame/30,'targets':found})
    report['clips'][clip]=samples
report['sampled_overlap_pairs']=sum(value['overlap_pairs'] for samples in report['clips'].values() for sample in samples for value in sample['targets'].values())
report['status']='REQUIRES_REVIEW' if report['sampled_overlap_pairs'] else 'NO_SAMPLED_OPAQUE_OVERLAPS'
(folder/'intersection_audit.json').write_text(json.dumps(report,indent=2))
print('WARDROBE_INTERSECTION_AUDIT',report['status'],report['sampled_overlap_pairs'],flush=True)
