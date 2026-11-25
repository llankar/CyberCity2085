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

@pytest.fixture
def robot_atlas(atlas):
    mapping={'Idle':'Idle','Walk':'Walk','Pistol_Shoot':'Melee','Punch_Cross':'Hit','Death01':'Death'}
    for old,new in mapping.items():
        path=atlas/(old+'_atlas.json');data=json.loads(path.read_text())
        data['animations']={new.lower():{'rows':next(iter(data['animations'].values()))['rows'],'loop':new=='Idle'}}
        data['reference_height_px']=[62.208*1.949875712/1.869130611]*8
        data['walk_root_motion_removed_m']=.6 if new=='Walk' else 0.
        data['walk_root_motion_removed_vector_m']=[0.,-.6,0.] if new=='Walk' else [0.,0.,0.]
        duration={'Idle':2.,'Walk':1.2,'Melee':1.,'Hit':.8,'Death':2.}[new]
        data['sample_times_s']=[duration*i/(4 if new=='Idle' else 3) for i in range(4)]
        data['source_strip_frames']=[1.,1.+duration*30]
        data['sample_scene_frames']=[1.+t*30 for t in data['sample_times_s']]
        data['texture']=new+'_atlas.png'
        if old!=new:
            (atlas/(old+'_atlas.png')).rename(atlas/data['texture'])
            for direction in range(8):
                for sample in range(4):
                    (atlas/f'{old}_d{direction}_f{sample}.png').rename(atlas/f'{new}_d{direction}_f{sample}.png')
        (atlas/(new+'_atlas.json')).write_text(json.dumps(data))
    return atlas


def test_actual_scale_robot_manifest_and_nonloop_motion_contract(robot_atlas):
    module.verify(robot_atlas,robot=True)
    assert set(json.loads((robot_atlas/'verification.json').read_text())['clips'])=={'Idle','Walk','Melee','Hit','Death'}


def test_robot_walk_cannot_silently_loop_or_keep_translation(robot_atlas):
    path=robot_atlas/'Walk_atlas.json';data=json.loads(path.read_text())
    data['animations']['walk']['loop']=True;path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):module.verify(robot_atlas,robot=True)
    data['animations']['walk']['loop']=False;data['walk_root_motion_removed_m']=0
    path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):module.verify(robot_atlas,robot=True)


def test_wrong_robot_pixel_scale_rejected(robot_atlas):
    path=robot_atlas/'Idle_atlas.json';data=json.loads(path.read_text())
    data['reference_height_px']=[62.208]*8;path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):module.verify(robot_atlas,robot=True)


def test_wrong_forward_translation_direction_is_rejected(robot_atlas):
    path=robot_atlas/'Walk_atlas.json';data=json.loads(path.read_text())
    data['walk_root_motion_removed_vector_m']=[0.,.6,0.]
    path.write_text(json.dumps(data))
    with pytest.raises(AssertionError):module.verify(robot_atlas,robot=True)
