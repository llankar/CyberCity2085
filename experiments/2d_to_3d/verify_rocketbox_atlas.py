"""Validate real PNG framing, frame layout and observed motion; not artistic QA."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image


def verify(root,robot=False,cyborg=False):
    assert not(robot and cyborg)
    evidence={}
    for clip in (['PistolFireStudy'] if cyborg else (['Idle','Walk','Melee','Hit','Death'] if robot else ['Idle','Walk','Pistol_Shoot','Punch_Cross','Death01'])):
        manifest=json.loads((root/(clip+'_atlas.json')).read_text())
        image=np.array(Image.open(root/manifest['texture']).convert('RGBA'))
        width,height=manifest['frame_size']
        assert (width,height)==(192,192)
        count=10 if cyborg else 4
        assert image.shape==(count*height,8*width,4)
        animation=next(iter(manifest['animations'].values()))
        assert len(animation['rows'])==8 and all(len(row)==count for row in animation['rows'])
        assert sorted(index for row in animation['rows'] for index in row)==list(range(8*count))
        expected=62.208*1.949875712/1.869130611 if robot else 62.208
        assert all(abs(value-expected)<.001 for value in manifest['reference_height_px'])
        if cyborg:
            assert manifest['sample_scene_frames']==list(range(0,19,2))
            assert np.max(np.abs(np.array(manifest['sample_times_s'])-np.arange(10)/12))<1e-8
            assert manifest['sample_scene_frames'][4]==8, 'Recoil peak omitted'
            assert not animation['loop'] and animation['fps']==12
            assert manifest['source_model_sha256']==hashlib.sha256((root.parent/'human.blend').read_bytes()).hexdigest()
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
            if cyborg:
                assert hashes[4]!=hashes[3] and hashes[4]!=hashes[5], 'Recoil peak not visually resolved in this orbit view'
            motion.append(len(set(hashes)))
        evidence[clip]={'frames':8*count,'distinct_frames_by_view':motion,'sha256':hashlib.sha256((root/manifest['texture']).read_bytes()).hexdigest()}
    total=sum(value['frames'] for value in evidence.values())
    (root/'verification.json').write_text(json.dumps({'clips':evidence,'frames':total,'artistic_acceptance':False},indent=2),encoding='utf-8')
    print('ROCKETBOX_ATLAS_PIXELS_OK',total)


if __name__=='__main__':
    robot='--robot-bundle' in sys.argv
    cyborg='--cyborg-fire-study' in sys.argv
    verify(Path('E:/CyberCity2085-3d-lab/generated/phase2')/('security_bundle01/atlas' if robot else ('cyborg_fire01/atlas' if cyborg else 'rocketbox_military03/motion01/atlas')),robot=robot,cyborg=cyborg)
