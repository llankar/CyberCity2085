"""Derive existing top-down combat zoom and copy reference atlases to E:."""
import hashlib
import json
import shutil
from pathlib import Path


def combat_heights(width, height, source_width, source_height, ratio):
    overview = max(.1, min(3.0, min(width*.94/source_width, height*.72/source_height)))
    close = min(3.0, overview*3.0)
    return {'overview_zoom': overview, 'close_zoom': close,
            'overview_human_px': source_width*ratio*overview,
            'close_human_px': source_width*ratio*close}


def main():
    root = Path(__file__).resolve().parents[2]
    output = Path('E:/CyberCity2085-3d-lab/sources/sprite_review')
    output.mkdir(parents=True, exist_ok=True)
    name = 'city_exterior_neon_market_alley.png'
    presentation = root/'godot/combat_missions_ui/art/environment/map_presentation.json'
    ratio = json.loads(presentation.read_text())['maps'][name]['human_height_ratio']
    dimensions = json.loads((root/'assets/maps'/name.replace('.png','.walls.json')).read_text())['image_size']
    report = {'viewport': [1920, 1080], 'map': name, 'human_height_ratio': ratio,
              'source_size': dimensions, 'scope': 'default top-down presentation, no handoff overrides',
              'robot_sprite_multiplier': 1.65,
              **combat_heights(1920,1080,*dimensions,ratio), 'atlases': []}
    for key in ['agent_samurai','enemy_corp_samurai_robot_heavy']:
        source = root/'assets/combat_visual/animations'/f'{key}.json'
        manifest = json.loads(source.read_text())
        texture = root/manifest['texture']
        for file in [source,texture]:
            shutil.copy2(file,output/file.name)
        digest = hashlib.sha256(texture.read_bytes()).hexdigest()
        assert digest == manifest['texture_sha256']
        report['atlases'].append({'key':key,'sha256':digest})
    (output/'calibration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('SPRITE_REVIEW_CALIBRATION',json.dumps(report))


if __name__ == '__main__':
    main()
