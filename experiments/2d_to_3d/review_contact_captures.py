"""Assemble native pose captures for inspection; never declare art acceptance."""
import hashlib
import json
import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw


def validate_manifest(manifest):
    captures = manifest['captures']
    expected = {(view, index/16) for view in ('posX','negX','posZ','negZ') for index in range(17)}
    actual = [(entry['camera_axis'],entry['fraction']) for entry in captures]
    if len(captures) != 68 or set(actual) != expected or len(set(actual)) != 68:
        raise ValueError('Need exactly four views of all seventeen distinct times')
    if manifest['clip'] != 'Shoot':
        raise ValueError('Wrong animation')
    return captures


MOTIONS = ('Hard stand','Walk (1_24)','ShootStudy','MeleeStudy','DeathStudy')
VIEWS = ('front','right','back','left')


def validate_motion_manifest(manifest):
    captures=manifest['captures']
    expected={(clip,view,index/5) for clip in MOTIONS for view in VIEWS for index in range(6)}
    actual=[(entry['clip'],entry['view'],entry['fraction']) for entry in captures]
    if len(captures)!=120 or set(actual)!=expected or len(set(actual))!=120:
        raise ValueError('Need five motions, four views and six distinct native times')
    if len({entry['file'] for entry in captures})!=120:
        raise ValueError('Each captured view/time needs its own source file')
    clocks={}
    for entry in captures:
        if not math.isfinite(entry['time_s']) or entry['time_s']<0:
            raise ValueError('Invalid sample clock')
        key=(entry['clip'],entry['fraction'])
        if key in clocks and clocks[key]!=entry['time_s']:
            raise ValueError('View clocks disagree')
        clocks[key]=entry['time_s']
    return captures


def motion_sheets(folder):
    manifest=json.loads((folder/'captures.json').read_text())
    model=Path(manifest['model'])
    assert model.resolve().parent==folder.resolve().parent
    assert hashlib.sha256(model.read_bytes()).hexdigest()==manifest['model_sha256']
    captures=validate_motion_manifest(manifest)
    for clip in MOTIONS:
        sheet=Image.new('RGB',(1280,1224),(24,24,24));draw=ImageDraw.Draw(sheet)
        for entry in (e for e in captures if e['clip']==clip):
            path=Path(entry['file']);assert path.resolve().parent==folder.resolve()
            assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
            with Image.open(path) as native:
                assert native.size==(1280,720)
                tile=native.convert('RGB').resize((320,180),Image.Resampling.LANCZOS)
            x=VIEWS.index(entry['view'])*320;y=round(entry['fraction']*5)*204
            sheet.paste(tile,(x,y+24))
            draw.text((x+5,y+5),f"{clip} | {entry['view']} | {entry['fraction']:.1f}",fill='white')
        sheet.save(folder/(clip.replace(' ','_')+'_review.png'))
    print('NATIVE_MOTION_REVIEW_SHEETS_OK originals=120 sheets=5 no_art_acceptance')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--motion151',action='store_true');args=parser.parse_args()
    if args.motion151:
        motion_sheets(Path('E:/CyberCity2085-3d-lab/generated/phase2/amjviz_wardrobe150/motion_review151'))
        return
    folder = Path('E:/CyberCity2085-3d-lab/generated/phase2/scanned_armor_contact01/contact_review01')
    manifest = json.loads((folder/'captures.json').read_text())
    model = folder.parent/'pistol_fit01/human_pistol.glb'
    assert hashlib.sha256(model.read_bytes()).hexdigest() == manifest['model_sha256']
    captures = validate_manifest(manifest)
    for view in ('posX','negX','posZ','negZ'):
        sheet = Image.new('RGB',(1920,1500),(24,24,24))
        draw = ImageDraw.Draw(sheet)
        selected = sorted((entry for entry in captures if entry['camera_axis']==view),key=lambda entry:entry['fraction'])
        for index,entry in enumerate(selected):
            path = Path(entry['file'])
            assert path.resolve().parent == folder.resolve()
            image = Image.open(path).convert('RGB')
            assert image.size == (1280,720), image.size
            image = image.resize((480,270),Image.Resampling.LANCZOS)
            x,y = (index%4)*480,(index//4)*300
            sheet.paste(image,(x,y+25))
            draw.text((x+8,y+7),f"{view} | t={entry['time_s']:.5f}s | fraction={entry['fraction']:.4f}",fill='white')
        sheet.save(folder/(view+'_review.png'))
    print('CONTACT_CAPTURE_REVIEW_SHEETS_OK originals=68 sheets=4 no_art_acceptance')


if __name__ == '__main__':
    main()
