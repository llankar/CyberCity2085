"""Measure actual sole trajectories/contact runs; distinguish grounding from foot locking."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Matrix
root=Path('E:/CyberCity2085-3d-lab/generated/phase2');skin='--sole-skin162' in sys.argv
candidate=skin or '--candidate' in sys.argv
source=root/('sole_skin162' if skin else ('foot_contact161' if candidate else 'cover_transitions160'));out=root/('sole_skin162' if skin else 'foot_contact161');out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source/'human.blend'),use_scripts=False)
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');body=max((o for o in scene.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
base=Matrix(json.loads((root/'amjviz_actions146/bake_report.json').read_text())['base_game_world'])
rig.data.pose_position='REST';bpy.context.view_layer.update()
indices={}
for side in ('L','R'):
 names={g.index for g in body.vertex_groups if g.name in ('DEF-foot.'+side,'DEF-toe.'+side)}
 assert names
 selected=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if g.group in names)>.5]
 assert selected
 floor=min((body.matrix_world@body.data.vertices[i].co).z for i in selected)
 indices[side]=[i for i in selected if (body.matrix_world@body.data.vertices[i].co).z<floor+.012]
 assert len(indices[side])>=3
rig.data.pose_position='POSE';report={'scope':'Actual fixed sole vertex trajectories at120Hz; 5mm contact classification, not artistic acceptance','blend_sha256':hashlib.sha256((source/'human.blend').read_bytes()).hexdigest(),'sole_vertices':{s:len(v) for s,v in indices.items()},'clips':{}}
for label in ('CoverEnterStudy','CoverExitStudy'):
 track=next(t for t in rig.animation_data.nla_tracks if t.name==label)
 for t in rig.animation_data.nla_tracks:t.mute=t!=track
 rig.animation_data.action=None;rig.matrix_world=base.copy()
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 anchors={side:None for side in indices};vertex_drift={side:0. for side in indices}
 individual_anchors={side:[None]*len(ids) for side,ids in indices.items()};individual_drift={side:0. for side in indices};witness={side:None for side in indices}
 samples=[];first,last=track.strips[0].frame_start,track.strips[0].frame_end
 for frame in range(round(first),round(last)+1):
  scene.frame_set(frame);bpy.context.view_layer.update();evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();feet={}
  for side,ids in indices.items():
   points=[evaluated.matrix_world@mesh.vertices[i].co for i in ids]
   for i,p in enumerate(points):
    if p.z<=.005:
     if individual_anchors[side][i] is None:individual_anchors[side][i]=p.copy()
     a=individual_anchors[side][i];drift=math.hypot(p.x-a.x,p.y-a.y)
     if drift>individual_drift[side]:
      individual_drift[side]=drift;vertex=body.data.vertices[ids[i]]
      witness[side]={'vertex':ids[i],'frame':frame,'anchor':list(a),'position':list(p),'weights':{body.vertex_groups[g.group].name:g.weight for g in vertex.groups if g.weight>.00001}}
    else:individual_anchors[side][i]=None
   if min(p.z for p in points)<=.005:
    if anchors[side] is None:anchors[side]=[p.copy() for p in points]
    vertex_drift[side]=max(vertex_drift[side],max(math.hypot(p.x-a.x,p.y-a.y) for p,a in zip(points,anchors[side])))
   else:anchors[side]=None
   feet[side]={'minimum_z_m':min(p.z for p in points),'centroid':[sum(p[k] for p in points)/len(points) for k in range(3)]}
  evaluated.to_mesh_clear();samples.append({'time_s':frame/scene.render.fps,'feet':feet})
 metrics={}
 maximum_unsupported_height=max(min(s['feet'][side]['minimum_z_m'] for side in indices) for s in samples)
 for side in indices:
  previous=None;anchor=None;maximum=0.;distance=0.;contact_frames=0
  for sample in samples:
   foot=sample['feet'][side];p=foot['centroid']
   if foot['minimum_z_m']<=.005:
    contact_frames+=1
    if anchor is None:anchor=p
    maximum=max(maximum,math.hypot(p[0]-anchor[0],p[1]-anchor[1]))
    if previous:distance+=math.hypot(p[0]-previous[0],p[1]-previous[1])
    previous=p
   else:anchor=None;previous=None
  metrics[side]={'worst_contact_witness':witness[side],'contact_frames':contact_frames,'maximum_continuous_contact_vertex_drift_m':vertex_drift[side],'maximum_individual_contact_vertex_drift_m':individual_drift[side],'maximum_continuous_contact_centroid_drift_m':maximum,'contact_centroid_path_length_m':distance}
 report['clips'][label]={'samples':samples,'metrics':metrics,'maximum_lowest_sole_height_m':maximum_unsupported_height}
 print('SOLE_CONTACT161',label,json.dumps(metrics),flush=True)
(out/('candidate_sole_contact.json' if candidate else 'source_sole_contact.json')).write_text(json.dumps(report,indent=2));print('SOLE_CONTACT161_AUDIT_READY')
