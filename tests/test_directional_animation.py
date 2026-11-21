"""Real posed walk frames, honest incomplete coverage and native playback."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
import pytest
from PIL import Image
from tools.audit_combat_visuals import validate_atlas
ROOT=Path(__file__).resolve().parents[1]
KEYS=['agent_psi','agent_diverse_01_neon_blade','agent_diverse_02_longcoat_gunner','agent_diverse_03_magenta_pistol','agent_diverse_04_trench_sniper','agent_diverse_05_psi_doctor','agent_diverse_06_street_medic','agent_diverse_07_hooded_infiltrator','agent_diverse_08_holo_hacker','agent_diverse_09_blue_mohawk_scout','agent_diverse_10_ronin_duelist','agent_diverse_11_rail_sniper','agent_diverse_12_violet_fixer','agent_diverse_13_silver_pistol','agent_diverse_14_armored_vanguard','agent_diverse_15_chrome_medic','agent_diverse_16_heavy_breacher','agent_diverse_17_yellow_strike','agent_diverse_18_red_enforcer','agent_diverse_19_drone_handler','agent_diverse_20_cyber_doc','agent_diverse_21_twin_blade_adept','agent_diverse_22_veteran_inquisitor','agent_diverse_23_dreadlock_rifle','agent_diverse_24_hooded_psion','agent_diverse_25_redline_runner','enemy_grunt','enemy_corp_37_power_armor_grunt','enemy_giant_robot_02_quadruped_siege','enemy_giant_robot_03_missile_artillery','enemy_giant_robot_04_riot_walker','enemy_giant_robot_05_railgun_sniper','enemy_giant_robot_06_flame_unit','enemy_giant_robot_07_drone_carrier','enemy_giant_robot_08_claw_demolisher','enemy_giant_robot_09_spider_tank','enemy_giant_robot_10_pacification_titan','robot_combat']
TARGET=os.environ.get('CYBERCITY_ANIMATION_ASSET')
KEYS.insert(-1,'enemy_giant_robot_11_samurai_warbot')
KEYS.insert(-1,'enemy_giant_robot_12_corp_security')
KEYS.insert(-1,'enemy_giant_robot_13_salvage_warbot')
KEYS.insert(-1,'enemy_giant_robot_14_killer_medic')
KEYS.insert(-1,'enemy_giant_robot_15_stealth_mech')
KEYS.insert(-1,'enemy_giant_robot_16_twin_cannon')
KEYS.insert(-1,'enemy_giant_robot_17_blade_hunter')
KEYS.insert(-1,'enemy_giant_robot_18_anti_air')
KEYS.insert(-1,'enemy_giant_robot_19_mining_combat')
KEYS.insert(-1,'enemy_giant_robot_20_command_titan')
KEYS.insert(-1,'enemy_mutant_01_hulk')
KEYS.insert(-1,'enemy_mutant_02_spine_stalker')
KEYS.insert(-1,'enemy_mutant_03_acid_psychic')
KEYS.insert(-1,'enemy_mutant_04_four_arm_brawler')
KEYS.insert(-1,'enemy_mutant_05_irradiated_medic')
KEYS.insert(-1,'enemy_mutant_06_pit_fighter')
KEYS.insert(-1,'enemy_mutant_07_sewer_veil')
KEYS.insert(-1,'enemy_mutant_08_crystal_growth')
KEYS.insert(-1,'enemy_mutant_09_toxin_carrier')
KEYS.insert(-1,'enemy_mutant_10_bone_blade')
KEYS.insert(-1,'enemy_mutant_11_cyber_graft')
KEYS.insert(-1,'enemy_mutant_12_plague_monk')
KEYS.insert(-1,'enemy_mutant_13_scrap_shield')
KEYS.insert(-1,'enemy_mutant_14_crawler')
KEYS.insert(-1,'enemy_mutant_15_horned_warlord')
KEYS.insert(-1,'enemy_mutant_16_gasmask_scavenger')
KEYS.insert(-1,'enemy_mutant_17_glowing_vein')
KEYS.insert(-1,'enemy_mutant_18_blind_sonar')
KEYS.insert(-1,'enemy_mutant_19_hive_scarred')
KEYS.insert(-1,'enemy_mutant_20_rust_mangler')
KEYS.insert(-1,'enemy_raider_01_sawblade_marauder')
KEYS.insert(-1,'enemy_raider_02_tire_armor_brute')
KEYS.insert(-1,'enemy_raider_03_flame_lancer')
KEYS.insert(-1,'enemy_raider_04_scrap_sniper')
KEYS.insert(-1,'enemy_raider_05_bike_scout')
KEYS.insert(-1,'enemy_raider_06_chain_hook')
KEYS.insert(-1,'enemy_raider_07_wasteland_medic')
KEYS.insert(-1,'enemy_raider_08_shield_brawler')
KEYS.insert(-1,'enemy_raider_09_mohawk_duelist')
KEYS.insert(-1,'enemy_raider_10_dust_preacher')
KEYS.insert(-1,'enemy_raider_11_drone_scavenger')
KEYS.insert(-1,'enemy_raider_12_explosive_thrower')
KEYS.insert(-1,'enemy_raider_13_nailgunner')
KEYS.insert(-1,'enemy_raider_14_armored_queen')
KEYS.insert(-1,'enemy_raider_15_skull_helm_heavy')
KEYS.insert(-1,'enemy_raider_16_harpoon_gunner')
KEYS.insert(-1,'enemy_raider_17_cyber_jaw')
KEYS.insert(-1,'enemy_raider_18_banner_carrier')
KEYS.insert(-1,'enemy_raider_19_oil_mechanic')
KEYS.insert(-1,'enemy_raider_grunt')
TEST_KEYS=[TARGET] if TARGET else KEYS
if TARGET and TARGET not in KEYS:raise ValueError(f'Unknown animation asset: {TARGET}')

def test_production_walk_and_idle_have_eight_distinct_views_and_real_frames():
    for key in TEST_KEYS:
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
            elif key=='agent_psi':
                expected_required.add('psi');expected_exempt={'fire','heal'}
            elif key=='agent_diverse_06_street_medic':
                expected_required.update({'fire','heal'});expected_exempt={'psi'}
            elif key=='agent_diverse_15_chrome_medic':
                expected_required.add('heal');expected_exempt={'fire','psi'}
            elif key=='agent_diverse_19_drone_handler':
                expected_required.add('psi');expected_exempt={'fire','heal'}
            elif key=='agent_diverse_20_cyber_doc':
                expected_required.add('heal');expected_exempt={'fire','psi'}
            elif key=='agent_diverse_24_hooded_psion':
                expected_required.update({'fire','psi'});expected_exempt={'heal'}
            elif key=='enemy_giant_robot_14_killer_medic':
                expected_required.update({'fire','heal'});expected_exempt={'psi'}
            elif key=='enemy_mutant_03_acid_psychic':
                expected_required.update({'fire','psi'});expected_exempt={'heal'}
            elif key=='enemy_mutant_05_irradiated_medic':
                expected_required.update({'fire','heal'});expected_exempt={'psi'}
            elif key=='enemy_mutant_19_hive_scarred':
                expected_required.add('psi');expected_exempt={'fire','heal'}
            elif key=='enemy_raider_07_wasteland_medic':
                expected_required.add('heal');expected_exempt={'fire','psi'}
            elif key=='enemy_raider_10_dust_preacher':
                expected_required.add('psi');expected_exempt={'fire','heal'}
            elif key in {'enemy_raider_14_armored_queen','enemy_raider_15_skull_helm_heavy','enemy_raider_17_cyber_jaw','enemy_raider_18_banner_carrier','enemy_raider_19_oil_mechanic'}:
                pass
            elif key not in {'agent_diverse_01_neon_blade','agent_diverse_07_hooded_infiltrator','agent_diverse_08_holo_hacker','agent_diverse_10_ronin_duelist','agent_diverse_21_twin_blade_adept','enemy_mutant_01_hulk','enemy_mutant_02_spine_stalker','enemy_mutant_04_four_arm_brawler','enemy_mutant_06_pit_fighter','enemy_mutant_07_sewer_veil','enemy_mutant_10_bone_blade','enemy_mutant_13_scrap_shield','enemy_mutant_14_crawler','enemy_mutant_15_horned_warlord','enemy_mutant_17_glowing_vein','enemy_mutant_19_hive_scarred','enemy_mutant_20_rust_mangler','enemy_raider_01_sawblade_marauder','enemy_raider_02_tire_armor_brute','enemy_raider_05_bike_scout','enemy_raider_06_chain_hook','enemy_raider_08_shield_brawler','enemy_raider_09_mohawk_duelist'}:
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


def test_raider_grunt_has_complete_native_verified_true_gait():
    path=ROOT/'assets/combat_visual/animations/enemy_raider_grunt.json'
    data=json.loads(path.read_text())
    assert data['coverage']=='complete'
    assert data['missing_clips']==[]
    assert data['review_status']=='native_render_verified'
    assert set(data['animations'])=={'idle','move','fire','melee','cover','hit','death'}
    assert set(data['required_clips'])=={'idle','move','fire','melee','cover','hit','death'}
    assert all(len(row)==4 for row in data['animations']['move']['rows'])
    assert len({frame for row in data['animations']['move']['rows'] for frame in row})==32
    assert validate_atlas(path,ROOT,set(data['animations']))==[]

@pytest.mark.skipif(not os.environ.get('DISPLAY'),reason='Native animation rendering requires X11')
def test_native_playback_facings_and_continuous_gait():
    exe=shutil.which('godot') or shutil.which('godot4')
    if not exe:pytest.skip('Godot unavailable')
    command=[exe,'--audio-driver','Dummy','--path',str(ROOT/'godot/combat_missions_ui'),'--script','tests/directional_animation_regression.gd','--quit-after','1200']
    if TARGET:command.extend(['--','--asset',TARGET])
    result=subprocess.run(command,capture_output=True,text=True,timeout=90)
    output=result.stdout+result.stderr
    assert result.returncode==0 and 'SCRIPT ERROR' not in output and 'SHADER ERROR' not in output,output
    assert f'DIRECTIONAL_ANIMATION_CHECKS_PASSED {32*len(TEST_KEYS)} actual frame selections' in output,output
