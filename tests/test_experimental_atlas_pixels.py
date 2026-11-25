"""Pixel contracts catch clipped poses and scrambled atlas construction."""
import importlib.util
import json
from pathlib import Path
import numpy as np
from PIL import Image
import pytest

SOURCE=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/verify_rocketbox_atlas.py'
spec=importlib.util.spec_from_file_location('rocket_atlas',SOURCE)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
CLIPS=['Idle','Walk','Pistol_Shoot','Punch_Cross','Death01']


@pytest.fixture
def atlas(tmp_path):
    for clip in CLIPS:
        sheet=np.zeros((768,1536,4),dtype=np.uint8)
        rows=[]
        for direction in range(8):
            row=[]
            for sample in range(4):
                index=direction*4+sample; x,y=index%8,index//8
                frame=np.zeros((192,192,4),dtype=np.uint8)
                frame[50:110,80:100]=[40+index*5,70,90,255]
                Image.fromarray(frame).save(tmp_path/f'{clip}_d{direction}_f{sample}.png')
                sheet[y*192:(y+1)*192,x*192:(x+1)*192]=frame
                row.append(index)
            rows.append(row)
        Image.fromarray(sheet).save(tmp_path/(clip+'_atlas.png'))
        (tmp_path/(clip+'_atlas.json')).write_text(json.dumps({'texture':clip+'_atlas.png',
            'frame_size':[192,192],'animations':{clip.lower():{'rows':rows}},'reference_height_px':[62.208]*8}))
    return tmp_path


def test_complete_real_png_layout_passes(atlas):
    module.verify(atlas)
    assert json.loads((atlas/'verification.json').read_text())['frames']==160


def test_clipped_pose_rejected_even_when_sheet_matches_source(atlas):
    source=atlas/'Idle_d0_f0.png'
    frame=np.array(Image.open(source)); frame[0,90]=[60,80,90,255]
    Image.fromarray(frame).save(source)
    path=atlas/'Idle_atlas.png'; sheet=np.array(Image.open(path)); sheet[:192,:192]=frame
    Image.fromarray(sheet).save(path)
    with pytest.raises(AssertionError,match='clipped'): module.verify(atlas)


def test_scrambled_sheet_rejected(atlas):
    path=atlas/'Idle_atlas.png'; sheet=np.array(Image.open(path))
    sheet[:192,:192]=sheet[:192,192:384].copy()
    Image.fromarray(sheet).save(path)
    with pytest.raises(AssertionError,match='Sheet/source mismatch'): module.verify(atlas)
