"""Read-only visual resource audit; rejects duplicate-frame pseudo animation.

Run: python tools/audit_combat_visuals.py --output work/visual-audit.json
Use --require-complete for the final art delivery gate (expected to fail until
all units have real animation atlases). Never changes maps or their surveys.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'idle', 'move', 'fire', 'melee', 'cover', 'hit', 'death', 'psi', 'heal'}


def validate_atlas(path: Path, root: Path = ROOT, required: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    required = REQUIRED if required is None else required
    try:
        data = json.loads(path.read_text())
        texture = (root / data['texture']).resolve()
        if not texture.is_relative_to(root.resolve()):
            return ['texture escapes asset root']
        image = Image.open(texture).convert('RGBA')
        width, height = data['frame_size']
        if width <= 0 or height <= 0 or image.width % width or image.height % height:
            return ['invalid atlas dimensions']
        columns = image.width // width
        total = columns * (image.height // height)
        animations = data['animations']
        for name in sorted(required - animations.keys()):
            errors.append(f'missing clip: {name}')
        if 'source_image' in data:
            source=(root/data['source_image']).resolve()
            if not source.is_relative_to(root.resolve()) or not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest()!=data.get('source_sha256'):
                errors.append('source identity/hash mismatch')
        for name, clip in animations.items():
            rows = clip['rows']
            if len(rows) != 8:
                errors.append(f'{name}: requires eight directions')
                continue
            if not 0 < clip['fps'] <= 60:
                errors.append(f'{name}: invalid fps')
            direction_hashes = []
            for direction, frames in enumerate(rows):
                if len(frames) < 2:
                    errors.append(f'{name}/{direction}: fewer than two real frames')
                hashes = []
                canonical = []
                for index in frames:
                    if not isinstance(index, int) or not 0 <= index < total:
                        errors.append(f'{name}/{direction}: out of bounds frame {index}')
                        continue
                    x, y = (index % columns) * width, (index // columns) * height
                    frame = image.crop((x, y, x+width, y+height))
                    if frame.getchannel('A').getbbox() is None:
                        errors.append(f'{name}/{direction}: empty frame {index}')
                    hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
                    box=frame.getchannel('A').getbbox()
                    if box:canonical.append(hashlib.sha256(frame.crop(box).resize((96,96),Image.Resampling.NEAREST).tobytes()).hexdigest())
                if len(set(hashes)) < 2:
                    errors.append(f'{name}/{direction}: static/duplicate frames')
                if canonical and len(set(canonical))<2:
                    errors.append(f"{name}/{direction}: same pose after translation/scale")
                direction_hashes.append(tuple(hashes))
            if len(set(direction_hashes)) < 8:
                errors.append(f'{name}: duplicated directions')
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        errors.append(str(exc))
    return errors


def audit(root: Path = ROOT) -> dict:
    maps = []
    for survey in sorted((root/'assets/maps').glob('*.walls.json')):
        data = json.loads(survey.read_text())
        image = survey.parent / data['image']
        digest = hashlib.sha256(image.read_bytes()).hexdigest() if image.exists() else None
        maps.append({'image': data['image'], 'sha256_valid': digest == data.get('image_sha256'),
                     'walls': len(data.get('walls', [])), 'survey_sha256': hashlib.sha256(survey.read_bytes()).hexdigest()})
    sprites = sorted(p for p in (root/'assets/units').glob('*.png') if not p.stem.endswith('_512'))
    units = []
    for sprite in sprites:
        manifest = root/'assets/combat_visual/animations'/f'{sprite.stem}.json'
        errors = validate_atlas(manifest, root) if manifest.exists() else ['missing genuine multidirectional animations']
        highres = sprite.with_name(sprite.stem+'_512.png')
        with Image.open(highres if highres.exists() else sprite) as image:
            transparent = image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] < 255
        partial=manifest.exists() and not validate_atlas(manifest,root,{'idle','move'})
        eligible=not sprite.stem.startswith('mission_objective_')
        units.append({'animation_eligible':eligible,'usable_directional_walk':partial,'key': sprite.stem, 'highres': highres.exists(), 'transparent': transparent, 'animation_errors': errors})
    return {'maps': maps, 'units': units,
            'summary': {'surveyed_maps': len(maps), 'invalid_map_hashes': sum(not m['sha256_valid'] for m in maps),
                        'unit_art': len(units), 'animation_eligible_units':sum(u['animation_eligible'] for u in units),
                        'animated_units_partial':sum(u['animation_eligible'] and u['usable_directional_walk'] and bool(u['animation_errors']) for u in units),
                        'animated_units_complete': sum(u['animation_eligible'] and not u['animation_errors'] for u in units)}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['summary'], indent=2))
    missing = result['summary']['animated_units_complete'] != result['summary']['animation_eligible_units']
    return int(bool(result['summary']['invalid_map_hashes']) or (args.require_complete and missing))

if __name__ == '__main__':
    raise SystemExit(main())
