"""Explicit flat-joint pose rebasing for the authored experiment GLBs."""
from bisect import bisect_right
import numpy as np
from scipy.spatial.transform import Rotation


def matrix_trs(translation,quaternion,scale):
    result=np.eye(4)
    result[:3,:3]=Rotation.from_quat(quaternion).as_matrix() @ np.diag(scale)
    result[:3,3]=translation
    return result


def decompose(matrix):
    translation=matrix[:3,3]
    scale=np.linalg.norm(matrix[:3,:3],axis=0)
    if np.min(scale)<1e-10: raise ValueError('Singular joint scale')
    rotation=matrix[:3,:3]/scale
    if np.linalg.det(rotation)<0:
        scale[0]*=-1; rotation[:,0]*=-1
    quaternion=Rotation.from_matrix(rotation).as_quat()
    error=float(np.max(np.abs(matrix_trs(translation,quaternion,scale)-matrix)))
    if error>2e-5: raise ValueError(f'Joint rebase introduced shear: {error}')
    return translation.tolist(),quaternion.tolist(),scale.tolist(),error


def sample(times,values,time,quaternion=False):
    index=max(0,min(len(times)-1,bisect_right(times,time)-1))
    if index==len(times)-1: return values[index]
    fraction=(time-times[index])/(times[index+1]-times[index])
    first=np.asarray(values[index],dtype=float); second=np.asarray(values[index+1],dtype=float)
    if quaternion:
        dot=float(np.dot(first,second))
        if dot<0: second=-second; dot=-dot
        dot=np.clip(dot,-1,1)
        if dot<.9995:
            angle=np.arccos(dot)
            return (first*np.sin((1-fraction)*angle)+second*np.sin(fraction*angle))/np.sin(angle)
    value=first*(1-fraction)+second*fraction
    return value/np.linalg.norm(value) if quaternion else value


def rebase_flat_tracks(source,base,animation,float_values):
    """Return canonical TRS tracks satisfying newPose*baseBind=oldPose*oldBind."""
    joints=source.doc['skins'][0]['joints']; base_joints=base.doc['skins'][0]['joints']
    parents={child:index for index,node in enumerate(source.doc['nodes']) for child in node.get('children',[])}
    base_parents={child:index for index,node in enumerate(base.doc['nodes']) for child in node.get('children',[])}
    assert len({parents[joint] for joint in joints})==1,'Flat joint hierarchy required'
    assert len({base_parents[joint] for joint in base_joints})==1
    root=parents[joints[0]]
    assert source.doc['nodes'][root].get('matrix',np.eye(4).flatten().tolist())==np.eye(4).flatten().tolist()
    assert source.doc['nodes'][root].get('translation',[0,0,0])==[0,0,0]
    assert source.doc['nodes'][root].get('rotation',[0,0,0,1])==[0,0,0,1]
    assert source.doc['nodes'][root].get('scale',[1,1,1])==[1,1,1]
    assert all(channel['target']['node']!=root for channel in animation['channels'])
    source_binds=np.asarray(float_values(source,source.doc['skins'][0]['inverseBindMatrices'])).reshape(-1,4,4).transpose(0,2,1)
    base_binds=np.asarray(float_values(base,base.doc['skins'][0]['inverseBindMatrices'])).reshape(-1,4,4).transpose(0,2,1)
    tracks={}; all_times=set()
    for channel in animation['channels']:
        node=channel['target']['node']; path=channel['target']['path']
        if node not in joints: continue
        sampler=animation['samplers'][channel['sampler']]
        interpolation=sampler.get('interpolation','LINEAR')
        assert interpolation in {'LINEAR','STEP'},'Unsupported interpolation'
        times=float_values(source,sampler['input'])
        width=4 if path=='rotation' else 3
        values=np.asarray(float_values(source,sampler['output'])).reshape(-1,width)
        if interpolation=='STEP':
            assert np.array_equal(values,np.broadcast_to(values[0],values.shape)),'Varying STEP track requires discontinuity-preserving rebake'
        tracks[node,path]=(times,values); all_times.update(times)
    times=sorted(all_times); result=[]; max_error=0.0
    assert times
    for index,node in enumerate(joints):
        reference=source.doc['nodes'][node]
        correction=source_binds[index] @ np.linalg.inv(base_binds[index])
        output={'translation':[],'rotation':[],'scale':[]}; previous=None
        for time in times:
            values={}
            for path,default in [('translation',[0,0,0]),('rotation',[0,0,0,1]),('scale',[1,1,1])]:
                values[path]=sample(*tracks[node,path],time,path=='rotation') if (node,path) in tracks else reference.get(path,default)
            pose=matrix_trs(values['translation'],values['rotation'],values['scale']) @ correction
            translation,rotation,scale,error=decompose(pose)
            max_error=max(max_error,error)
            if previous is not None and np.dot(previous,rotation)<0: rotation=[-x for x in rotation]
            previous=rotation
            for path,value in [('translation',translation),('rotation',rotation),('scale',scale)]: output[path].extend(value)
        result.append((reference['name'],output))
    return times,result,max_error
