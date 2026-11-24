"""Check evaluated mesh coordinates through authored robot clips (not art approval)."""
import json
import math
import sys
from pathlib import Path
import bpy

folder = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
if folder.drive.upper() != 'E:':
    raise ValueError('Experimental evidence belongs on E:')
bpy.ops.wm.open_mainfile(filepath=str(folder / 'george_tactical.blend'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
for track in rig.animation_data.nla_tracks:
    track.mute = True
report = {}
for name in ['Idle', 'Walk', 'Run', 'Shoot', 'Punch', 'HitRecieve_1', 'Death']:
    action = bpy.data.actions[name]
    rig.animation_data.action = action
    samples = 0
    envelope = [[float('inf')] * 3, [float('-inf')] * 3]
    for frame in range(math.floor(action.frame_range[0]), math.ceil(action.frame_range[1]) + 1):
        bpy.context.scene.frame_set(frame)
        graph = bpy.context.evaluated_depsgraph_get()
        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH':
                continue
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            for vertex in mesh.vertices:
                point = evaluated.matrix_world @ vertex.co
                assert all(math.isfinite(v) for v in point), (name, frame)
                for axis in range(3):
                    envelope[0][axis] = min(envelope[0][axis], point[axis])
                    envelope[1][axis] = max(envelope[1][axis], point[axis])
            evaluated.to_mesh_clear()
        samples += 1
    report[name] = {'frames_evaluated': samples, 'world_envelope': envelope,
                    'finite_coordinates': True}
(folder / 'clip_geometry_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('ROBOT_CLIP_GEOMETRY_CHECKS ' + json.dumps(report))
