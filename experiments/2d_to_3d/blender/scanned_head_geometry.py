"""Extract the complete licensed photographed head/neck from the original rig."""
import sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent.parent))
from anatomical_groups import descendants


def extract(rig,body):
    world=[body.matrix_world@v.co for v in body.data.vertices]
    groups={g.index:g.name for g in body.vertex_groups}
    anatomy=descendants({b.name:b.parent.name if b.parent else None for b in rig.data.bones},'rp_nathan_animated_003_walking_neck_06')
    allowed={i for i,name in groups.items() if name in anatomy}
    weights=[sum(g.weight for g in v.groups if g.group in allowed) for v in body.data.vertices]
    faces=[face for face in body.data.polygons if all(world[i].z>1.54 and weights[i]>.5 for i in face.vertices)]
    used=sorted({i for face in faces for i in face.vertices})
    mapping={old:new for new,old in enumerate(used)}
    normal_matrix=body.matrix_world.to_3x3().inverted().transposed()
    eyes=[rig.matrix_world@rig.data.bones[name].head_local for name in ('rp_nathan_animated_003_walking_eye_l_011','rp_nathan_animated_003_walking_eye_r_013')]
    assert len(faces)==6630 and len(used)==3765
    return {'positions':[world[i].copy() for i in used],
            'faces':[[mapping[i] for i in face.vertices] for face in faces],
            'uv':[tuple(body.data.uv_layers.active.data[i].uv) for face in faces for i in face.loop_indices],
            'normals':[(normal_matrix@body.data.corner_normals[i].vector).normalized() for face in faces for i in face.loop_indices],
            'eye_midpoint':sum(eyes,Vector())/2}
