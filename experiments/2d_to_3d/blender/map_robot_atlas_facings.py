"""Measure actual camera projections and enrich manifests without rerendering PNGs."""
import sys,json,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent.parent))
from atlas_facing import facing_lookup
rook='--rook-run-study' in sys.argv
root=Path('E:/CyberCity2085-3d-lab/generated/phase2')/('rook_run129' if rook else 'security_bundle01')
folder=root/'atlas'
hash_file=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pngs={p.name:hash_file(p) for p in folder.glob('*.png')}
source_hash=hash_file(root/('human.blend' if rook else 'robot_actions.blend'))
if rook:
 bpy.ops.wm.open_mainfile(filepath=str(root/'human.blend'),use_scripts=False)
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 forward=rig.matrix_world.to_3x3()@(rig.data.bones['headfront'].head_local-rig.data.bones['Head'].head_local)
 forward.z=0;forward.normalize()
 assert (forward-Vector((0,-1,0))).length<.0001
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=192
scene.render.resolution_percentage=100
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
reports={}
for clip in (['CombatReadyStudy','walk','PistolFireStudy','MeleeStudy','DeathStudy'] if rook else ['Idle','Walk','Melee','Hit','Death']):
 path=folder/(clip+'_atlas.json');manifest=json.loads(path.read_text())
 assert manifest['source_model_sha256']==source_hash
 elevation=manifest['elevation_radians'];target=Vector((0,0,.9))
 camera.data.ortho_scale=192*manifest['calibration_human_height_m']*math.cos(elevation)/62.208
 if not rook:
  walk=json.loads((folder/'Walk_atlas.json').read_text())
  forward=Vector(walk['walk_root_motion_removed_vector_m']).normalized()
 assert (forward-Vector((0,-1,0))).length<.00001
 vectors=[];projections=[]
 for view in range(8):
  angle=view*math.tau/8
  camera.location=target+Vector((8*math.cos(angle),8*math.sin(angle),8*math.tan(elevation)))
  camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
  origin=world_to_camera_view(scene,camera,Vector((0,0,0)))
  ahead=world_to_camera_view(scene,camera,forward)
  delta=[ahead.x-origin.x,-(ahead.y-origin.y)];vectors.append(delta)
  projections.append({'orbit_view':view,'screen_forward':delta,'camera_world':list(camera.location)})
 lookup=facing_lookup(vectors,y_scale=2.)
 manifest.update({'facing_to_orbit_view':lookup,'facing_y_scale':2.,'source_forward_world':list(forward),
                  'camera_views':'Measured camera projection mapped to existing screen sectors E,SE,S,SW,W,NW,N,NE; artistic orientation review separate'})
 if rook:
  manifest.update({'source':'Grab3D body/hair CC0; Microsoft Rocketbox head MIT; Unvanquished hand CC BY-SA3; FireWarden pistol CC0; Quaternius motions CC0; complete notices in CREDITS.txt',
                   'credits_file':'CREDITS.txt','credits_sha256':hash_file(folder/'CREDITS.txt')})
 path.write_text(json.dumps(manifest,indent=2),encoding='utf8')
 reports[clip]={'facing_to_orbit_view':lookup,'projections':projections}
assert all(hash_file(folder/name)==sha for name,sha in pngs.items())
(folder/'facing_projection_check.json').write_text(json.dumps({'source_blend_sha256':source_hash,'clips':reports,'png_sha256_unchanged':pngs,'scope':('Actual headfront/Head rest-bone forward' if rook else 'Measured walk forward')+' and actual Blender camera projections, existing unit_visual facing_y_scale2 convention; not final art'},indent=2))
print('HUMAN_ATLAS_FACING_PROJECTION_OK' if rook else 'ROBOT_ATLAS_FACING_PROJECTION_OK',lookup,'PNG files unchanged',len(pngs),flush=True)
