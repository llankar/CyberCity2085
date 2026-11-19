"""Real posed walk frames, honest incomplete coverage and native playback."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
import pytest
from PIL import Image
from tools.audit_combat_visuals import validate_atlas
ROOT=Path(__file__).resolve().parents[1]
KEYS=['agent_diverse_01_neon_blade','agent_diverse_02_longcoat_gunner','agent_diverse_03_magenta_pistol','agent_diverse_04_trench_sniper','agent_diverse_05_psi_doctor','agent_diverse_06_street_medic','agent_diverse_07_hooded_infiltrator','agent_diverse_08_holo_hacker','agent_diverse_09_blue_mohawk_scout','agent_diverse_10_ronin_duelist','agent_diverse_11_rail_sniper','agent_diverse_12_violet_fixer','agent_diverse_13_silver_pistol','agent_diverse_14_armored_vanguard','agent_diverse_15_chrome_medic','agent_diverse_16_heavy_breacher','agent_diverse_17_yellow_strike','agent_diverse_18_red_enforcer','agent_diverse_19_drone_handler','agent_diverse_20_cyber_doc','agent_diverse_21_twin_blade_adept','enemy_grunt','enemy_corp_37_power_armor_grunt','robot_combat']

def test_production_walk_and_idle_have_eight_distinct_views_and_real_frames():
    for key in KEYS:
        path=ROOT/'assets/combat_visual/animations'/f'{key}.json'
        assert validate_atlas(path,ROOT,{'idle','move'})==[]
        data=json.loads(path.read_text())
        expected_missing={'fire','melee','cover','hit','death','psi','heal'}
        if key in KEYS:
            expected_missing=set()
            assert data['coverage']=='complete'
            expected_required={'idle','move','melee','cover','hit','death'}
            expected_exempt={'fire','psi','heal'}
            if key=='agent_diverse_05_psi_doctor':
                expected_required.update({'psi','heal'});expected_exempt={'fire'}
            elif key=='agent_diverse_06_street_medic':
                expected_required.update({'fire','heal'});expected_exempt={'psi'}
            elif key=='agent_diverse_15_chrome_medic':
                expected_required.add('heal');expected_exempt={'fire','psi'}
            elif key=='agent_diverse_19_drone_handler':
                expected_required.add('psi');expected_exempt={'fire','heal'}
            elif key=='agent_diverse_20_cyber_doc':
                expected_required.add('heal');expected_exempt={'fire','psi'}
            elif key not in {'agent_diverse_01_neon_blade','agent_diverse_07_hooded_infiltrator','agent_diverse_08_holo_hacker','agent_diverse_10_ronin_duelist','agent_diverse_21_twin_blade_adept'}:
                expected_required.add('fire');expected_exempt={'psi','heal'}
            assert set(data['required_clips'])==expected_required
            assert set(data['non_applicable_clips'])==expected_exempt
        assert set(data['missing_clips'])==expected_missing
        assert validate_atlas(path,ROOT,set(data['required_clips']))==[]
        for action in set(data['required_clips'])-{'idle','move'}:
            assert len(data['animations'][action]['rows'])==8
            assert all(len(row)==2 for row in data['animations'][action]['rows'])
        assert data['anchor_uv']==[.5,244/256]
        assert hashlib.sha256((ROOT/data['texture']).read_bytes()).hexdigest()==data['texture_sha256']
        with Image.open(ROOT/data['texture']) as image:
            columns=image.width//256
            for clip,count in [('move',4),('idle',2)]:
                assert len(data['animations'][clip]['rows'])==8
                for row in data['animations'][clip]['rows']:
                    assert len(row)==count
                    for index in row:
                        x=index%columns*256;y=index//columns*256
                        bounds=image.crop((x,y,x+256,y+256)).getchannel('A').getbbox()
                        assert bounds and min(bounds[:2])>0 and bounds[2]<256 and bounds[3]<256


def test_shifted_copies_are_not_counted_as_real_animation(tmp_path):
    image=Image.new('RGBA',(128,16))
    for direction in range(8):
        for pose in range(2):
            # Different canvas positions; exactly the same visible body pose.
            image.paste((10+direction*20,180,90,255),(direction*16+pose*8+pose,2,direction*16+pose*8+pose+3,7))
    image.save(tmp_path/'atlas.png')
    data=dict(texture='atlas.png',frame_size=[8,8],animations={'move':dict(fps=8,rows=[[d*2,d*2+1] for d in range(8)])})
    (tmp_path/'a.json').write_text(json.dumps(data))
    assert any('same pose after translation/scale' in e for e in validate_atlas(tmp_path/'a.json',tmp_path,{'move'}))

@pytest.mark.skipif(not os.environ.get('DISPLAY'),reason='Native animation rendering requires X11')
def test_native_playback_facings_and_continuous_gait():
    exe=shutil.which('godot') or shutil.which('godot4')
    if not exe:pytest.skip('Godot unavailable')
    result=subprocess.run([exe,'--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/directional_animation_regression.gd','--quit-after','1200'],capture_output=True,text=True,timeout=90)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output and 'SHADER ERROR' not in output,output
    assert f'DIRECTIONAL_ANIMATION_CHECKS_PASSED {32*len(KEYS)} actual frame selections' in output,output
