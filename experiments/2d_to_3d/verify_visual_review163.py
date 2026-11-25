"""Verify genuine native review captures without claiming artistic acceptance."""
import hashlib,json,math
from pathlib import Path
from PIL import Image

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_capture(path,model_paths,dimensions):
    metadata=json.loads(Path(str(path)+'.json').read_text())
    assert metadata['capture_sha256']==sha(path),'Capture changed'
    with Image.open(path) as image:
        image.load();assert image.size==tuple(dimensions),'Unexpected PNG dimensions'
    assert metadata['render_texture_size']==list(dimensions)
    assert metadata['diagnostics_visible'] is False
    assert set(metadata['models'])==set(model_paths)
    for key,source in model_paths.items():
        assert metadata['models'][key]['path']==str(source).replace('\\','/')
        assert metadata['models'][key]['sha256']==sha(source),'Model changed'
    return metadata

def main():
    root=Path('E:/CyberCity2085-3d-lab/generated/phase2');folder=root/'review163'
    paths={'human':root/'sole_skin162/human.glb','robot':root/'security_opaque137/robot_actions.glb'}
    calibration_path=Path('E:/CyberCity2085-3d-lab/sources/sprite_review/calibration.json')
    calibration=json.loads(calibration_path.read_text())
    sprite_sources={}
    for item in calibration['atlases']:
        path=calibration_path.parent/(item['key']+'.png')
        assert sha(path)==item['sha256'],'Reference atlas changed'
        sprite_sources[item['key']]={'png_sha256':sha(path),'manifest_sha256':sha(path.with_suffix('.json'))}
    report={}
    for name in ('human','robot','pair','calibrated_close','calibrated_overview'):
        calibrated=name.startswith('calibrated_')
        metadata=verify_capture(folder/(name+'.png'),paths,(1920,1080) if calibrated else (1280,720))
        if calibrated:
            key='overview_human_px' if name.endswith('overview') else 'close_human_px'
            assert metadata['sprite_review'] and abs(metadata['projected_human_reference_height_px']-calibration[key])<.1
        else:assert math.isclose(metadata['camera_size'],6.2 if name=='pair' else 4.2,rel_tol=0,abs_tol=1e-5)
        report[name]=metadata
    (folder/'CREDITS.txt').write_text((root/'sole_skin162/CREDITS.txt').read_text()+'\nRobot attribution:\n'+(root/'security_opaque137/CREDITS.txt').read_text())
    (folder/'verified_review.json').write_text(json.dumps({'captures':report,'calibration_sha256':sha(calibration_path),'reference_atlases':sprite_sources,
        'scope':'Five actual Godot captures, source/model hashes and projected pixel scales only; no final artistic acceptance or performance claim'},indent=2))
    print('VISUAL_REVIEW163_VERIFIED captures=5 calibrated_close_and_overview')

if __name__=='__main__':main()
