"""Inventory existing visual scale estimates. Never calibrate or change a map."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def build_inventory(root=ROOT, expected_maps=122):
    presentation = root/'godot/combat_missions_ui/art/environment/map_presentation.json'
    profiles = json.loads(presentation.read_text())['maps']
    rows = []
    shared = defaultdict(list)
    for survey in sorted((root/'assets/maps').glob('*.walls.json')):
        record = json.loads(survey.read_text())
        name = record['image']
        image = root/'assets/maps'/name
        row = dict(map=name, survey=survey.relative_to(root).as_posix(), calibration_status='NOT VERIFIED', anchors=[], issues=[])
        if not image.is_file():
            row['issues'].append('source image missing')
            rows.append(row)
            continue
        with Image.open(image) as opened:
            width, height = opened.size
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        if digest != record.get('image_sha256'):
            row['issues'].append('source SHA-256 differs from survey')
        if [width,height] != record.get('image_size'):
            row['issues'].append('source dimensions differ from survey')
        profile = profiles.get(name, {})
        configured = float(profile.get('human_height_ratio', .035))
        applied = min(.10, max(.015, configured))
        row.update(source_sha256=digest, source_size=[width,height], profile=profile.get('profile','fallback'),
                   configured_human_ratio=configured, current_human_ratio=applied,
                   standing_human_source_pixel_equivalent=round(width*applied,3),
                   explicit_profile=bool(profile), measurement_status='ESTIMATE_ONLY')
        if applied != configured:
            row['issues'].append('configured ratio is clamped by current runtime')
        rows.append(row)
        shared[digest].append(row)
    aliases=[]
    for digest, group in shared.items():
        if len(group)>1:
            aliases.append(dict(source_sha256=digest,maps=[r['map'] for r in group],
                                current_ratios=sorted({r['current_human_ratio'] for r in group}),
                                conflicting_estimates=len({r['current_human_ratio'] for r in group})>1))
    files=['godot/combat_missions_ui/art/environment/map_presentation.json',
           'godot/combat_missions_ui/scripts/map_presentation.gd',
           'godot/combat_missions_ui/scripts/unit_presentation.gd']
    return dict(scope='Baseline of current estimates, not validated calibration', expected_maps=expected_maps,
                surveyed_maps=len(rows), distinct_source_images=len(shared), verified_scale_maps=0,
                missing_explicit_profiles=sum(not r.get('explicit_profile',False) for r in rows),
                source_integrity_issues=sum(any('source' in issue for issue in r['issues']) for r in rows),
                shared_art=aliases, maps=rows,
                input_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},
                next_action='Measure visible reference objects per source image: doors, embedded cars, furniture and streets. Record measured pixel bounds and justified relative dimensions; review aliases separately. Do not derive object identity or physical size from collisions.')


def render_inventory(report):
    lines=['# Échelle des entités — inventaire des estimations actuelles','',
           '**NOT VERIFIED — aucune taille n’est calibrée par cet inventaire.**','',
           f"{report['surveyed_maps']} / {report['expected_maps']} cartes ; {report['distinct_source_images']} illustrations distinctes ; 0 carte vérifiée pour l’échelle.",
           'La hauteur équivalente en pixels source est le ratio configuré multiplié par la largeur du PNG. Ce nombre ne mesure pas un personnage ni une distance réelle.',
           'Les multiplicateurs de robots, armures, véhicules et géants restent ceux du runtime actuel. Aucune donnée tactique ou image n’est modifiée.','',
           '| Carte | Dimensions source | Profil estimé | Ratio appliqué | Hauteur humaine équivalente (px source) | Échelle validée |',
           '|---|---|---|---|---|---|']
    for row in report['maps']:
        lines.append(f"| {row['map']} | {row.get('source_size','INCONNU')} | {row.get('profile','INCONNU')} | {row.get('current_human_ratio','INCONNU')} | {row.get('standing_human_source_pixel_equivalent','INCONNU')} | NOT VERIFIED |")
    lines+=['','## Illustrations partagées','',
            'Un même PNG peut être utilisé par plusieurs missions. Les estimations contradictoires sont à examiner ; une correction ne se propage pas automatiquement à toutes les variantes tactiques.','']
    for group in report['shared_art']:
        lines.append('- '+', '.join(group['maps'])+' — ratios '+str(group['current_ratios'])+(' **contradictoires**' if group['conflicting_estimates'] else ' identiques mais non mesurés'))
    lines+=['','## Prochaine action','',report['next_action'],'']
    return '\n'.join(lines)


def main():
    report=build_inventory()
    out=ROOT/'docs/reports';out.mkdir(parents=True,exist_ok=True)
    (out/'entity_scale_baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (out/'entity_scale_baseline.md').write_text(render_inventory(report))
    print(json.dumps({k:report[k] for k in ['surveyed_maps','distinct_source_images','verified_scale_maps','source_integrity_issues']},indent=2))
    return int(report['surveyed_maps']!=report['expected_maps'] or report['source_integrity_issues']>0)


if __name__=='__main__':
    raise SystemExit(main())
