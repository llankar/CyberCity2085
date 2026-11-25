"""Add real rotor/gear pivots to existing procedural mechanical source."""
import json,sys,hashlib
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from vehicle_motion import vehicle_motion
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')
source=root/'vtol01/vtol.blend';out=root/'vtol_motion01';out.mkdir(exist_ok=True)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
scene=bpy.context.scene;scene.render.fps=30
parts=[o for o in scene.objects if o.type=='MESH'];controllers=[];assignments={}
def pivot(name,center,members,side,kind):
    control=bpy.data.objects.new(name,None);scene.collection.objects.link(control);control.location=center
    bpy.context.view_layer.update()
    for obj in members:
        matrix=obj.matrix_world.copy();obj.parent=control;obj.matrix_parent_inverse=control.matrix_world.inverted();obj.matrix_basis=matrix
        bpy.context.view_layer.update()
        assert max(abs(a-b) for ra,rb in zip(obj.matrix_world,matrix) for a,b in zip(ra,rb))<.000001,('Pivot changed neutral placement',obj.name)
    controllers.append((control,side,kind));assignments[name]=[o.name for o in members]
for side,label in [(-1,'L'),(1,'R')]:
    rotors=[o for o in parts if o.name.startswith(('RotorHub','RotorBlade')) and o.location.x*side>0]
    assert len(rotors)==11,(side,len(rotors))
    pivot('RotorPivot_'+label,(side*2.75,.5,.95),rotors,side,'rotor')
    for y,position in [(-1.5,'Front'),(2.,'Rear')]:
        gear=[o for o in parts if o.name.startswith(('LandingStrut','LandingShoe')) and o.location.x*side>0 and abs(o.location.y-y)<.01]
        assert len(gear)==2
        pivot('GearPivot_'+label+'_'+position,(side*.85,y,.6),gear,side,'gear')
assert sum(map(len,assignments.values()))==30
clips={'Rotor_Spin':2.,'Gear_Retract':1.,'Gear_Extend':1.}
references={}
for clip,duration in clips.items():
    frames=round(duration*30)
    for control,side,kind in controllers:
        control.animation_data_create();control.animation_data.action=bpy.data.actions.new(clip+'_'+control.name)
        for frame in range(frames+1):
            spin,gear=vehicle_motion(clip,frame/30,side)
            control.rotation_euler=(0,gear,0) if kind=='gear' else (0,0,spin)
            for path in ['location','rotation_euler','scale']:control.keyframe_insert(path,frame=frame)
        action=control.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
        track=control.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,0,action)
        control.animation_data.action=None
    for control,side,kind in controllers:
        for track in control.animation_data.nla_tracks:track.mute=track.name!=clip
    samples=[]
    for frame in sorted({round(frames*i/8) for i in range(9)}):
        scene.frame_set(frame);bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();geometry={}
        for name in [n for names in assignments.values() for n in names if n.startswith(('RotorBlade','LandingShoe'))]:
            obj=bpy.data.objects[name];evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
            geometry[name]=[list(evaluated.matrix_world @ mesh.vertices[i].co) for i in range(0,len(mesh.vertices),max(1,len(mesh.vertices)//5))];evaluated.to_mesh_clear()
        samples.append({'time_s':frame/30,'meshes':geometry})
    references[clip]=samples
for control,side,kind in controllers:
    for track in control.animation_data.nla_tracks:track.mute=False
scene.frame_start=0;scene.frame_end=60
for obj in scene.objects:obj.select_set(obj in parts or obj in [c for c,_,_ in controllers])
bpy.context.view_layer.objects.active=controllers[0][0]
notice='CyberCity2085 experimental procedural VTOL, derived from existing local project source; rotor and landing-gear articulation added. No production asset replacement.'
bpy.data.texts.new('EXPERIMENT_CREDITS').write(notice)
bpy.ops.export_scene.gltf(filepath=str(out/'vtol_actions.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_optimize_animation_size=False,export_optimize_animation_keep_anim_object=True,export_copyright=notice)
for control,side,kind in controllers:
    for track in control.animation_data.nla_tracks:track.mute=track.name!='Rotor_Spin'
scene.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/'vtol_actions.blend'))
(out/'source_surface_reference.json').write_text(json.dumps(references))
(out/'motion_report.json').write_text(json.dumps({'source_sha256':source_hash,'clips':clips,'mesh_count':len(parts),'pivots':assignments,'reference_samples_per_clip':9,'limitations':['Slowed120RPM rotor inspection, not flight physics','No landing bay cutouts; stowed gear/hull collision not accepted','Materials/hull art inherited experimental source, not final Nighthawk','Static hovering scene has no accepted landing footprint']},indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('VTOL_MECHANICAL_ACTIONS_EXPORTED',len(parts),len(controllers),list(clips),flush=True)
