"""Read-only global acceptance audit. Only --write updates generated documentation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from tools.audit_combat_visuals import audit
from tools.art.update_environment_progress import metrics, render_signature

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {'TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED'}
EXPECTED_MAPS = 122


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def evidence_file(root, relative):
    path = (root / relative).resolve()
    return path if path.is_relative_to(root.resolve()) and path.is_file() else None


def manual_review(root, record, signature):
    if not record:
        return 'NOT VERIFIED', 'Revue explicite et preuves non enregistrées.'
    if record.get('status') not in {'PASS', 'FAIL'} or not record.get('scope'):
        return 'NOT VERIFIED', 'Portée ou résultat de revue absent.'
    if record.get('render_signature') != signature:
        return 'NOT VERIFIED', 'Revue périmée : le rendu ou les ressources ont changé.'
    evidence = record.get('evidence', [])
    if not evidence:
        return 'NOT VERIFIED', 'Aucune preuve de revue.'
    for item in evidence:
        path = evidence_file(root, item.get('path', ''))
        if not path:
            return 'NOT VERIFIED', 'Preuve de revue introuvable.'
        if hashlib.sha256(path.read_bytes()).hexdigest() != item.get('sha256'):
            return 'NOT VERIFIED', 'Empreinte de preuve différente de la revue.'
    return record['status'], record['scope']


def test_counts(root, record):
    """No XML means unknown, never zero failures interpreted as success."""
    empty = dict(passed=None, failed=None, skipped=None, not_executed='UNKNOWN', scope='Aucun résultat JUnit enregistré.')
    if not record:
        return empty
    path = evidence_file(root, record.get('path', ''))
    if not path or hashlib.sha256(path.read_bytes()).hexdigest() != record.get('sha256'):
        return empty
    for source in record.get('sources', []):
        tested = evidence_file(root, source.get('path', ''))
        if not tested or hashlib.sha256(tested.read_bytes()).hexdigest() != source.get('sha256'):
            return empty
    try:
        cases = list(ET.parse(path).getroot().iter('testcase'))
    except (ET.ParseError, OSError):
        return empty
    if not cases:
        return empty
    failed = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped = sum(c.find('skipped') is not None for c in cases)
    return dict(passed=len(cases)-failed-skipped, failed=failed, skipped=skipped,
                not_executed=record.get('not_executed', 'UNKNOWN'), scope=record.get('scope', 'Portée non décrite'))


def registry_issues(root, registry):
    issues = []
    ids = set()
    for task in registry.get('tasks', []):
        key = task.get('id', '?')
        if key in ids:
            issues.append(key + ': identifiant dupliqué')
        ids.add(key)
        if task.get('status') not in STATUSES:
            issues.append(key + ': statut invalide')
        if not all(field in task for field in ['files', 'tests', 'evidence', 'remaining']):
            issues.append(key + ': suivi incomplet')
        if task.get('status') == 'BLOCKED' and not task.get('reason'):
            issues.append(key + ': blocage sans raison')
        if task.get('status') == 'DONE':
            if not task.get('tests') or not task.get('evidence'):
                issues.append(key + ': DONE sans tests/contrôles et preuves')
            if task.get('remaining'):
                issues.append(key + ': DONE avec travail restant dans la portée déclarée')
            for relative in task.get('evidence', []):
                if not evidence_file(root, relative):
                    issues.append(key + ': preuve absente ' + relative)
    return issues


def build_report(root=ROOT):
    registry = read_json(root/'docs/CODEX_PROGRESS.json', {})
    resource_audit = audit(root)
    counts = metrics(root)
    signature = render_signature(root)
    state = read_json(root/'docs/combat_visual_25_status.json', {})
    current = state.get('validation', {}).get('signature') == signature
    art = read_json(root/'godot/combat_missions_ui/art/environment/environment_art.json', {'maps': {}})['maps']
    expected = EXPECTED_MAPS
    native = read_json(root/'docs/images/combat-directional-animation/native-report.json', [])
    native_names = {row.get('map') for row in native if row.get('native_render') and row.get('projection_and_zoom_checked')}
    expected_names = {row['image'] for row in resource_audit['maps']}
    capture_dir = root/'docs/images/combat-directional-animation'
    native_proofs = all((capture_dir/f'catalogue-{page:02d}.jpg').is_file() for page in range(1, (expected+11)//12+1))
    loaded = len(native_names & expected_names) if current and native_proofs else 0
    declared_art = sum(bool(m.get('validation', {}).get('artistically_complete')) for m in art.values())
    rows = []

    def add(key, title, status, detail, evidence):
        rows.append(dict(id=key, title=title, mandatory=True, status=status, detail=detail, evidence=evidence))

    summary = resource_audit['summary']
    add('MAP-SOURCE', 'Intégrité des cartes et relevés',
        'PASS' if summary['surveyed_maps'] == expected and summary['invalid_map_hashes'] == 0 and registry.get('expected_maps') == expected else 'FAIL',
        f"{summary['surveyed_maps']} / {expected} cartes relevées ; {summary['invalid_map_hashes']} empreintes invalides.", ['assets/maps/*.walls.json'])
    add('MAP-LOAD', 'Chargement natif et projection',
        'PASS' if loaded == expected and len(expected_names) == expected else ('NOT VERIFIED' if not current or not native or not native_proofs else 'FAIL'),
        f'{loaded} / {expected} cartes dans les preuves natives compatibles avec la signature actuelle. Ne valide pas leur finition.',
        ['docs/images/combat-directional-animation/native-report.json', 'docs/combat_visual_25_status.json'])
    reviewed = registry.get('reviews', {})
    status, detail = manual_review(root, reviewed.get('MAP-ART'), signature)
    if declared_art != expected:
        status, detail = 'FAIL', f'{declared_art} / {expected} cartes déclarées finalisées ; revue artistique complète absente.'
    add('MAP-ART', 'Finition artistique de chaque carte', status, detail, ['godot/combat_missions_ui/art/environment/environment_art.json'])
    library = read_json(root/'godot/combat_missions_ui/art/environment/props25/library.json', {'assets': {}})['assets']
    directory = root/'godot/combat_missions_ui/art/environment/props25'
    missing = [f'{name}-{yaw}.png' for name, asset in library.items() for yaw in asset['yaw'] if not (directory/f'{name}-{yaw}.png').is_file()]
    add('ART-FILES', 'Présence des ressources de décor déclarées', 'FAIL' if missing or not library else 'PASS',
        f"{counts['frames']-len(missing)} / {counts['frames']} vues déclarées présentes ; {counts['families']} familles. Présence ≠ qualité artistique.",
        ['godot/combat_missions_ui/art/environment/props25/library.json'])
    scale_verified = len(set(registry.get('scale_review', {}).get('verified_maps', [])) & expected_names)
    for key, title, note in [
        ('ART-OBJECTS', 'Silhouettes, matériaux et intégration des objets', f"{counts['active']} placements sur {counts['improved_maps']} cartes ; {counts['retained']} entrées source conservées. Nombre total d’objets artistiques attendus inconnu ; une entrée peut regrouper plusieurs objets."),
        ('UNIT-SCALE', 'Échelle PJ/PNJ/robots/armures/véhicules sur les 122 cartes', f'{scale_verified} / {expected} cartes documentées pour cette passe. Comparer aux portes, voitures du décor, mobilier et rues ; ne pas assimiler le profil visuel existant à une validation.'),
        ('UNIT-ART', 'Identité et qualité de toutes les unités', f"{summary['unit_art']} références source auditées, dont {counts['animation_eligible']} entités éligibles aux animations ; l’audit technique ne vaut pas revue individuelle."),
        ('FUNCTIONAL', 'Déplacement, ciblage, LOS, IA, PA, tours et fallback', 'Preuves historiques partielles disponibles ; aucune exécution exhaustive ni revue de toutes les interactions déduite des seuls tests de chargement.'),
        ('RESOLUTIONS', 'Lisibilité et interactions à 720p, 1080p et 1440p', 'Captures de cinq familles à trois résolutions disponibles ; revue exhaustive de contraste, occultation et ergonomie non enregistrée.'),
        ('PERFORMANCE', 'Performances et mémoire sur matériel joueur', 'Rendu logiciel llvmpipe disponible ; benchmark représentatif sur GPU joueur absent.')]:
        status, detail = manual_review(root, reviewed.get(key), signature)
        if key=='UNIT-SCALE' and status=='PASS' and scale_verified!=expected:
            status, detail='FAIL', 'La revue ne couvre pas les repères des 122 cartes attendues.'
        add(key, title, status, note+' '+detail, [item['path'] for item in reviewed.get(key, {}).get('evidence', [])])
    complete = summary['animated_units_complete']
    add('ANIMATIONS', 'Actions multidirectionnelles complètes', 'PASS' if complete == counts['animation_eligible'] and complete > 0 else 'FAIL',
        f"{complete} / {counts['animation_eligible']} ensembles complets selon le contrat actuel de neuf clips ; {summary['animated_units_partial']} partiels. Applicabilité par famille à documenter avant toute exemption.", ['assets/combat_visual/animations/*.json'])
    issues = registry_issues(root, registry)
    add('REGISTER', 'Registre complet et preuves des tâches DONE', 'FAIL' if issues or not registry.get('tasks') else 'PASS',
        '; '.join(issues) if issues else 'Statuts, portées, tests/contrôles, preuves et travail restant enregistrés.', ['docs/CODEX_PROGRESS.json'])
    tests = test_counts(root, registry.get('test_run'))
    add('TARGETED-TESTS', 'Tests exécutés dans la portée du lot',
        'NOT VERIFIED' if tests['passed'] is None else ('FAIL' if tests['failed'] else ('NOT VERIFIED' if tests['skipped'] else 'PASS')),
        str(tests), [registry.get('test_run', {}).get('path', '')])
    done = sum(t.get('status') == 'DONE' for t in registry.get('tasks', []))
    add('TASK-COMPLETION', 'Toutes les tâches obligatoires du registre réalisées',
        'PASS' if registry.get('tasks') and done == len(registry['tasks']) else 'FAIL',
        f"{done} / {len(registry.get('tasks', []))} tâches DONE ; les lots suivants ne disparaissent pas du bilan.", ['docs/CODEX_PROGRESS.json'])
    return dict(global_status='PASS' if all(r['status']=='PASS' for r in rows) else 'CHANTIER GLOBAL INCOMPLET',
                tasks=dict(done=done, total=len(registry.get('tasks', []))),
                maps=dict(native_verified=loaded, native_expected=expected, artistically_declared=declared_art, artistic_verified=expected if next(r for r in rows if r['id']=='MAP-ART')['status']=='PASS' else 0),
                resources=dict(declared_families=counts['families'], declared_views=counts['frames'], missing_views=missing, artistic_expected_objects=None, artistic_complete_objects=None),
                animations=dict(complete=complete, partial=summary['animated_units_partial'], expected=counts['animation_eligible']),
                tests=tests, render_signature=signature, criteria=rows,
                open_criteria=[r['id'] for r in rows if r['status']!='PASS'], next_action=registry.get('next_action', 'NON RENSEIGNÉE'))


def render_report(report):
    lines = ['# Combat Visual — bilan reproductible', '', '**'+report['global_status']+'**', '',
             f"Tâches DONE : {report['tasks']['done']} / {report['tasks']['total']}. Ce ratio porte sur le registre, pas sur la finition artistique.",
             f"Cartes : {report['maps']['native_verified']} / {report['maps']['native_expected']} chargées ; {report['maps']['artistic_verified']} artistiquement vérifiées.",
             f"Animations complètes : {report['animations']['complete']} / {report['animations']['expected']} ; {report['animations']['partial']} partielles.",
             'Objets artistiques complets / attendus : **inconnus**, ne pas calculer de pourcentage.', '',
             '| Critère obligatoire | Résultat | Preuve / limite |', '|---|---|---|']
    lines += [f"| {r['id']} — {r['title']} | {r['status']} | {r['detail']} |" for r in report['criteria']]
    lines += ['', '## Tests réellement enregistrés', '', json.dumps(report['tests'], ensure_ascii=False), '',
              '## Critères encore ouverts', '', ', '.join(report['open_criteria']) or 'Aucun', '',
              '## Prochaine action précise', '', report['next_action'], '']
    return '\n'.join(lines)


def render_register(registry):
    lines = ['# CODEX — registre persistant', '', '**CHANTIER GLOBAL INCOMPLET**', '',
             'Source structurée : `docs/CODEX_PROGRESS.json`. Générer ce document avec la commande de [vérification globale](COMBAT_VISUAL_ACCEPTANCE.md).', '',
             'Statuts : `TODO` non commencé ; `IN_PROGRESS` en cours ; `DONE` réalisé et vérifié dans la portée indiquée ; `BLOCKED` bloqué avec raison explicite.', '',
             '## Tâches et preuves', '']
    for task in registry['tasks']:
        lines += [f"### {task['id']} — {task['status']} — {task['title']}", '',
                  '- Fichiers : '+', '.join('`'+f+'`' for f in task['files'])+'.',
                  '- Tests / contrôles réellement exécutés : '+('; '.join(task['tests']) or 'Aucun — non exécutés')+'.',
                  '- Preuves : '+(', '.join('`'+f+'`' for f in task['evidence']) or 'Aucune')+'.',
                  '- Travail restant dans cette portée : '+(task['remaining'] or 'Aucun')+'.']
        if task.get('reason'):
            lines += ['- Problème / raison : '+task['reason']+'.']
        lines += ['']
    lines += ['## Problèmes et ressources en attente', '']+['- '+s for s in registry.get('problems', [])]
    lines += ['', '## Prochaine action précise', '', registry['next_action'], '',
              'Le nombre de tâches DONE et les critères ouverts sont calculés dans [le bilan global](reports/combat_visual_acceptance.md). Un lot validé ne termine pas le chantier.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='Update only generated docs; never game resources')
    args = parser.parse_args()
    try:
        report = build_report(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        message = 'CHANTIER GLOBAL INCOMPLET — NOT VERIFIED: '+str(exc)
        # Never leave an older positive report in place after a failed refresh.
        if args.write:
            directory = args.root/'docs/reports';directory.mkdir(parents=True, exist_ok=True)
            failure = dict(global_status='CHANTIER GLOBAL INCOMPLET', error=str(exc),
                           criteria=[dict(id='AUDIT-EXECUTION', mandatory=True, status='NOT VERIFIED', detail=str(exc))],
                           next_action='Réparer la donnée manquante ou corrompue puis relancer la vérification. Le registre existant est conservé.')
            (directory/'combat_visual_acceptance.json').write_text(json.dumps(failure, ensure_ascii=False, indent=2)+'\n')
            (directory/'combat_visual_acceptance.md').write_text('# Combat Visual — contrôle non exécuté\n\n'+message+'\n')
        print(message)
        return 2
    if args.write:
        directory = args.root/'docs/reports';directory.mkdir(parents=True, exist_ok=True)
        (directory/'combat_visual_acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        (directory/'combat_visual_acceptance.md').write_text(render_report(report))
        registry = read_json(args.root/'docs/CODEX_PROGRESS.json')
        (args.root/'docs/CODEX_PROGRESS.md').write_text(render_register(registry))
    print(render_report(report))
    return int(bool(report['open_criteria']))


if __name__ == '__main__':
    raise SystemExit(main())
