"""Assemble native pose captures for inspection; never declare art acceptance."""
import hashlib
import json
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


def main():
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
