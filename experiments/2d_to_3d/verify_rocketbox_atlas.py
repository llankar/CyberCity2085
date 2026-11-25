"""Validate real PNG framing, frame layout and observed motion; not artistic QA."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image


def verify(root,robot=False,cyborg=False,rook=False,native=False):
    assert not native or rook,'Native proof suite currently scopes the first actor'
    cyborg=cyborg or rook
    assert not(robot and cyborg)
    evidence={}
    clips=['CombatReadyStudy','walk','PistolFireStudy','MeleeStudy','DeathStudy'] if rook else (['PistolFireStudy'] if cyborg else (['Idle','Walk','Melee','Hit','Death'] if robot else ['Idle','Walk','Pistol_Shoot','Punch_Cross','Death01']))
    for clip in clips:
        manifest=json.loads((root/(clip+'_atlas.json')).read_text())
        image=np.array(Image.open(root/manifest['texture']).convert('RGBA'))
        width,height=manifest['frame_size']
        assert (width,height)==(192,192)
        count=len(manifest['sample_scene_frames']) if rook else (10 if cyborg else 4)
        assert 2<=count<=64
        assert image.shape==(count*height,8*width,4)
        animation=next(iter(manifest['animations'].values()))
        assert len(animation['rows'])==8 and all(len(row)==count for row in animation['rows'])
        assert sorted(index for row in animation['rows'] for index in row)==list(range(8*count))
        expected=62.208*1.949875712/1.869130611 if robot else 62.208
        assert all(abs(value-expected)<.001 for value in manifest['reference_height_px'])
        if rook:
            first,last=manifest['source_strip_frames']
            loop=clip in ('CombatReadyStudy','walk')
            expected_frames=list(range(round(first),round(last)+(0 if loop else 1)))
            assert manifest['sample_scene_frames']==expected_frames,'Native scene keys omitted or duplicated'
            assert animation['loop']==loop and abs(animation['fps']-24)<1e-6
            assert np.max(np.abs(np.array(manifest['sample_times_s'])-(np.array(expected_frames)-first)/24))<1e-8
            assert sorted(manifest['facing_to_orbit_view'])==list(range(8))
            assert manifest['facing_y_scale']==2.
            assert np.max(np.abs(np.array(manifest['source_forward_world'])-np.array([0,-1,0])))<1e-4
            assert manifest['credits_file']=='CREDITS.txt'
            assert manifest['credits_sha256']==hashlib.sha256((root/'CREDITS.txt').read_bytes()).hexdigest()
        if cyborg and not rook:
            assert manifest['sample_scene_frames']==list(range(0,19,2))
            assert np.max(np.abs(np.array(manifest['sample_times_s'])-np.arange(10)/12))<1e-8
            assert manifest['sample_scene_frames'][4]==8, 'Recoil peak omitted'
            assert not animation['loop'] and animation['fps']==12
        if cyborg:
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
            if cyborg and clip=='PistolFireStudy':
                peak=8 if rook else 4
                assert manifest['sample_scene_frames'][peak]==8
                assert hashes[peak]!=hashes[peak-1] and hashes[peak]!=hashes[peak+1], 'Recoil peak not visually resolved in this orbit view'
            motion.append(len(set(hashes)))
        evidence[clip]={'frames':8*count,'distinct_frames_by_view':motion,'sha256':hashlib.sha256((root/manifest['texture']).read_bytes()).hexdigest()}
        if native:
            proof_path=root/('native_'+clip.lower()+'_validation.json')
            proof=json.loads(proof_path.read_text())
            assert proof['status']=='PASS' and proof['action']==clip.lower()
            assert proof['frame_index_tests']==8*count and proof['display_scale']==1.
            assert proof['fps']==24. and proof['loop']==animation['loop'] and proof['production_order']
            assert proof['manifest_sha256']==hashlib.sha256((root/(clip+'_atlas.json')).read_bytes()).hexdigest()
            assert proof['atlas_png_sha256']==evidence[clip]['sha256']
            assert proof['texture_size']==[8*width,count*height]
            evidence[clip]['native_proof_sha256']=hashlib.sha256(proof_path.read_bytes()).hexdigest()
    total=sum(value['frames'] for value in evidence.values())
    (root/'verification.json').write_text(json.dumps({'clips':evidence,'frames':total,'native_proof_verified':native,'artistic_acceptance':False},indent=2),encoding='utf-8')
    print('ROCKETBOX_ATLAS_PIXELS_OK',total)


if __name__=='__main__':
    robot='--robot-bundle' in sys.argv
    cyborg='--cyborg-fire-study' in sys.argv
    rook='--rook-run-study' in sys.argv
    verify(Path('E:/CyberCity2085-3d-lab/generated/phase2')/('rook_run129/atlas' if rook else ('security_bundle01/atlas' if robot else ('cyborg_fire01/atlas' if cyborg else 'rocketbox_military03/motion01/atlas'))),robot=robot,cyborg=cyborg,rook=rook,native='--native-proof' in sys.argv)
