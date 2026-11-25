"""Validate real PNG framing, frame layout and observed motion; not artistic QA."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def verify(root):
    evidence={}
    for clip in ['Idle','Walk','Pistol_Shoot','Punch_Cross','Death01']:
        manifest=json.loads((root/(clip+'_atlas.json')).read_text())
        image=np.array(Image.open(root/manifest['texture']).convert('RGBA'))
        width,height=manifest['frame_size']
        assert (width,height)==(192,192)
        assert image.shape==(4*height,8*width,4)
        animation=next(iter(manifest['animations'].values()))
        assert sorted(index for row in animation['rows'] for index in row)==list(range(32))
        assert all(abs(value-62.208)<.001 for value in manifest['reference_height_px'])
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
    verify(Path('E:/CyberCity2085-3d-lab/generated/phase2/rocketbox_military03/motion01/atlas'))
