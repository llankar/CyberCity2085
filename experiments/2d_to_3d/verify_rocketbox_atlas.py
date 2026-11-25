"""Validate real PNG framing, frame layout and observed motion; not artistic QA."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image


def verify(root,robot=False):
    evidence={}
    for clip in (['Idle','Walk','Melee','Hit','Death'] if robot else ['Idle','Walk','Pistol_Shoot','Punch_Cross','Death01']):
        manifest=json.loads((root/(clip+'_atlas.json')).read_text())
        image=np.array(Image.open(root/manifest['texture']).convert('RGBA'))
        width,height=manifest['frame_size']
        assert (width,height)==(192,192)
        assert image.shape==(4*height,8*width,4)
        animation=next(iter(manifest['animations'].values()))
        assert sorted(index for row in animation['rows'] for index in row)==list(range(32))
        expected=62.208*1.949875712/1.869130611 if robot else 62.208
        assert all(abs(value-expected)<.001 for value in manifest['reference_height_px'])
        if robot:
            expected_duration={'Idle':2.,'Walk':1.2,'Melee':1.,'Hit':.8,'Death':2.}[clip]
            expected_times=[expected_duration*i/(4 if clip=='Idle' else 3) for i in range(4)]
            assert np.max(np.abs(np.array(manifest['sample_times_s'])-np.array(expected_times)))<.00001
            assert manifest['source_strip_frames'][0]==1.
            assert np.max(np.abs(np.array(manifest['sample_scene_frames'])-(1.+np.array(expected_times)*30)))<.00001
            assert animation['loop']==(clip=='Idle')
            assert abs(manifest['walk_root_motion_removed_m']-(.6 if clip=='Walk' else 0.))<.00001
            assert np.max(np.abs(np.array(manifest['walk_root_motion_removed_vector_m'])-np.array([0.,-.6,0.] if clip=='Walk' else [0.,0.,0.])))<.00001
        motion=[]
        for direction,row in enumerate(animation['rows']):
            hashes=[]
            for sample,index in enumerate(row):
                x,y=index%8,index//8
                frame=image[y*height:(y+1)*height,x*width:(x+1)*width]
                source=np.array(Image.open(root/f'{clip}_d{direction}_f{sample}.png').convert('RGBA'))
                assert np.max(np.abs(frame.astype(int)-source.astype(int)))<=2, 'Sheet/source mismatch'
                alpha=frame[:,:,3]
                assert np.count_nonzero(alpha>16)>100,'Empty/nearly empty frame'
                border=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
                assert border.max()<8,'Actor clipped by frame border'
                hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
            assert len(set(hashes))>1,'No observed motion in this view'
            motion.append(len(set(hashes)))
        evidence[clip]={'frames':32,'distinct_frames_by_view':motion,'sha256':hashlib.sha256((root/manifest['texture']).read_bytes()).hexdigest()}
    (root/'verification.json').write_text(json.dumps({'clips':evidence,'frames':160,'artistic_acceptance':False},indent=2),encoding='utf-8')
    print('ROCKETBOX_ATLAS_PIXELS_OK',160)


if __name__=='__main__':
    robot='--robot-bundle' in sys.argv
    verify(Path('E:/CyberCity2085-3d-lab/generated/phase2')/('security_bundle01/atlas' if robot else 'rocketbox_military03/motion01/atlas'),robot=robot)
