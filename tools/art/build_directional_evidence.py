"""Export native captures and resource previews without inventing animation poses."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'work/directional-animation/native'
OUTPUT = ROOT / 'docs/images/combat-directional-animation'


def gif(images, target, durations):
    # One palette for the whole sequence avoids palette flicker between poses.
    strip = Image.new('RGB', (images[0].width, images[0].height * len(images)))
    for i, frame in enumerate(images):
        strip.paste(frame.convert('RGB'), (0, i * frame.height))
    palette = strip.quantize(colors=256)
    frames = [frame.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE) for frame in images]
    frames[0].save(target, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=1, optimize=True)


def movement_gif(report, filename):
    assert len(report["actual_movement"]) == 40
    assert report["ap_before"] - report["ap_after"] == report["route_cost"]
    # Keep every movement phase, then sample the longer idle tail. Durations
    # retain the real elapsed time between retained captures.
    movement = report['actual_movement']
    sampled = [movement[i] for i in sorted(set(list(range(6)) + list(range(6, 40, 4)) + [39]))]
    moves = [Image.open(SOURCE / item['file']).convert('RGB') for item in sampled]
    for frame in moves:
        frame.thumbnail((960, 540))
    times = [item['elapsed_ms'] for item in sampled]
    durations = [max(20, times[i+1]-times[i]) for i in range(len(times)-1)] + [1000]
    gif(moves, OUTPUT / filename, durations)
    return len(moves)


def catalogue_evidence(catalogue):
    native = json.loads((catalogue / 'native-report.json').read_text())
    assert len(native) == 122 and all(row['native_render'] and row['projection_and_zoom_checked'] for row in native)
    for page in range(11):
        sheet = Image.new('RGB', (960, 800), (12, 20, 28))
        draw = ImageDraw.Draw(sheet)
        for cell, row in enumerate(native[page*12:(page+1)*12]):
            name = Path(row['map']).stem
            image = Image.open(catalogue / (name + '-1280x720.png')).convert('RGB')
            image.thumbnail((320, 180))
            x, y = cell % 3 * 320, cell // 3 * 200
            sheet.paste(image, (x, y+20))
            draw.text((x+3, y+3), name, fill=(160, 232, 236))
        sheet.save(OUTPUT / ('catalogue-%02d.jpg' % (page+1)), quality=88)
    (OUTPUT / 'native-report.json').write_text(json.dumps(native, indent=2) + '\n')
    return native


def main():
    global SOURCE, OUTPUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    parser.add_argument('--catalogue',type=Path,default=None,help='Native 122-map capture directory; defaults to SOURCE.parent/catalogue')
    parser.add_argument('--catalogue-only',action='store_true',help='Build only the 122-map native evidence; no animation source is required')
    parser.add_argument('--skip-catalogue',action='store_true',help='Export only native unit sequence; no catalogue coverage is claimed')
    args=parser.parse_args()
    SOURCE=args.source;OUTPUT=args.output
    OUTPUT.mkdir(parents=True, exist_ok=True)
    catalogue = args.catalogue or SOURCE.parent / 'catalogue'
    if args.catalogue_only:
        native=catalogue_evidence(catalogue)
        print('DIRECTIONAL_CATALOGUE_EVIDENCE_BUILT',len(native),'native maps')
        return
    report = json.loads((SOURCE / 'animation-report.json').read_text())
    assert len(report['actual_movement']) == 40
    assert report['ap_before'] - report['ap_after'] == report['route_cost']
    poses = [Image.open(SOURCE / item['file']).convert('RGB').crop((550, 75, 1540, 550)) for item in report['directions']]
    for frame in poses:
        frame.thumbnail((792, 380))
    ordered = poses
    gif(ordered, OUTPUT / 'native-eight-directions.gif', [125] * len(ordered))
    movement_count=movement_gif(report, 'native-click-movement.gif')
    if 'secondary_movement' in report:
        movement_gif(report['secondary_movement'], 'native-secondary-movement.gif')
    hashes = {}
    for path in sorted(SOURCE.glob('scene-*.png')) + [SOURCE / 'before-static-1920x1080.png', SOURCE / 'directions-00-00.png']:
        image = Image.open(path).convert('RGB')
        image.save(OUTPUT / (path.stem + '.webp'), 'WEBP', lossless=True, method=0)
        hashes[path.name] = hashlib.sha256(image.tobytes()).hexdigest()
    for manifest in sorted((ROOT / 'assets/combat_visual/animations').glob('*.json')):
        data = json.loads(manifest.read_text())
        atlas = Image.open(ROOT / data['texture']).convert('RGBA')
        frames = []
        for direction, row in enumerate(data['animations']['move']['rows']):
            for _ in range(2):
                for index in row:
                    frame = Image.new('RGB', (256, 280), (14, 23, 31))
                    tile = atlas.crop((index % 8 * 256, index // 8 * 256, index % 8 * 256 + 256, index // 8 * 256 + 256))
                    frame.paste(tile, (0, 20), tile)
                    ImageDraw.Draw(frame).text((12, 7), ['E','SE','S','SW','W','NW','N','NE'][direction], fill=(74, 242, 244))
                    frames.append(frame)
        gif(frames, OUTPUT / (manifest.stem + '.gif'), [125] * len(frames))
    (OUTPUT / 'animation-report.json').write_text(json.dumps(report, indent=2) + '\n')
    (OUTPUT / 'capture-rgb-sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    if args.skip_catalogue:
        print('DIRECTIONAL_UNIT_EVIDENCE_BUILT',len(report['directions']),'native poses;',movement_count,'retained movement frames')
        return
    native=catalogue_evidence(catalogue)
    print('DIRECTIONAL_EVIDENCE_BUILT', len(report['directions']), 'native poses;', movement_count, 'retained movement frames')


if __name__ == '__main__':
    main()
