"""Verify original-resolution source preservation, skin data and one render pair."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from glb_document import Glb

root=Path('E:/CyberCity2085-3d-lab')
folder=root/'generated/phase2/renderpeople_nathan01'
source=root/'sources/renderpeople_nathan'
glb=Glb(folder/'human.glb');doc=glb.doc
assert len(doc['meshes'])==len(doc['skins'])==len(doc['images'])==1
assert len(doc['skins'][0]['joints'])==89
primitive=doc['meshes'][0]['primitives'][0]
count=doc['accessors'][primitive['indices']]['count'];assert count==21506*3
weights=np.frombuffer(glb.values(primitive['attributes']['WEIGHTS_0']),dtype='<f4').reshape(-1,4)
assert np.isfinite(weights).all() and weights.min()>=0 and weights.max()<=1
assert np.abs(weights.sum(axis=1)-1).max()<1e-4
joint_id=primitive['attributes']['JOINTS_0']
kind=doc['accessors'][joint_id]['componentType']
joints=np.frombuffer(glb.values(joint_id),dtype={5121:'u1',5123:'<u2'}[kind]).reshape(-1,4)
assert joints[weights>1e-7].max()<89
normal=np.frombuffer(glb.values(primitive['attributes']['NORMAL']),dtype='<f4').reshape(-1,3)
assert np.isfinite(normal).all() and np.abs(np.linalg.norm(normal,axis=1)-1).max()<.001
image=doc['images'][0];assert image['mimeType']=='image/jpeg'
view=doc['bufferViews'][image['bufferView']]
embedded=bytes(glb.bin[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])
original=(source/'textures/rp_nathan_animated_003_mat_baseColor.jpeg').read_bytes()
assert original==embedded,'Source texture was recompressed or replaced'
assert Image.open(source/'textures/rp_nathan_animated_003_mat_baseColor.jpeg').size==(8192,8192)
assert len(doc['animations'])==1 and doc['animations'][0]['name']=='Walk'
duration=max(float(np.frombuffer(glb.values(sampler['input']),dtype='<f4').max()) for sampler in doc['animations'][0]['samplers'])
assert abs(duration-67/30)<1e-5
assert 'Renderpeople' in doc['asset']['copyright'] and 'CC-BY-4.0' in doc['asset']['copyright']
before=np.asarray(Image.open(folder/'source_walk_side.png')).astype('int16')
after=np.asarray(Image.open(folder/'walk_side.png')).astype('int16')
assert before.shape==after.shape
difference=np.abs(before-after);changed=int((difference[...,:3].max(axis=2)>0).sum())
report={'glb_sha256':hashlib.sha256((folder/'human.glb').read_bytes()).hexdigest(),
        'source_8k_jpeg_sha256':hashlib.sha256(original).hexdigest(),
        'original_jpeg_bytes_identical':True,'triangles':21506,'joints':89,
        'weight_sum_max_error':float(np.abs(weights.sum(axis=1)-1).max()),'clip_duration_s':duration,
        'one_native_equal_pose_view':{'source_clip':'Take 001','export_clip':'Walk','fraction':.5,
                                    'max_channel_difference':int(difference.max()),
                                    'mean_channel_difference':float(difference.mean()),
                                    'changed_pixels':changed,'total_pixels':int(before.shape[0]*before.shape[1]),
                                    'pixel_exact':changed==0},
        'scope':'Structural/source preservation PASS; pixel differences are observations, not an exact image PASS. No artist acceptance or complete PBR/action set.'}
(folder/'source_preservation_check.json').write_text(json.dumps(report,indent=2))
print('NATHAN_ORIGINAL_RESOLUTION_SKIN_OK',len(weights),duration,'changed source/export pixels',changed)
