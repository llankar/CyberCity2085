"""Generate the task-wide progress file from actual art and validation records.

Native load checks and artistic completion are deliberately separate measures.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
ART_REL = Path('godot/combat_missions_ui/art/environment')


def render_signature(root):
    project = root / 'godot/combat_missions_ui'
    paths = sorted((project / 'scripts').glob('*.gd')) + sorted((project / 'shaders').glob('*.gdshader'))
    paths += [root / ART_REL / 'environment_art.json', root / ART_REL / 'props25/library.json']
    paths += sorted((root / ART_REL / 'props25').glob('*-*.png'))
    scale_data=project/'art/environment/map_presentation.json'
    if scale_data.exists():paths.append(scale_data)
    animation_dir=root/'assets/combat_visual/animations'
    paths += sorted(animation_dir.glob('*.json')) + sorted(animation_dir.glob('*.png'))
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def metrics(root):
    art = root / ART_REL
    maps = json.loads((art / 'environment_art.json').read_text())['maps']
    library = json.loads((art / 'props25/library.json').read_text())
    active = [p for m in maps.values() for p in m['props'] if p['enabled']]
    animation_data=[json.loads(p.read_text()) for p in (root/'assets/combat_visual/animations').glob('*.json')]
    eligible=[p for p in (root/'assets/units').glob('*.png') if not p.stem.endswith('_512') and not p.stem.startswith('mission_objective_')]
    walk_verified=sum(a.get('review_status') in {'native_render_verified_partial','native_render_verified_complete'} and {'idle','move'}<=a.get('animations',{}).keys() for a in animation_data)
    complete_animations=sum(a.get('review_status')=='native_render_verified_complete' and a.get('coverage')=='complete' and set(a.get('required_clips',[]))<=a.get('animations',{}).keys() for a in animation_data)
    return dict(animation_eligible=len(eligible), animation_atlases=len(animation_data), directional_walk_verified=walk_verified, full_animation_sets=complete_animations, maps=len(maps), source_images=len({m['image_sha256'] for m in maps.values()}),
                families=len(library['assets']), frames=sum(len(a['yaw']) for a in library['assets'].values()),
                active=len(active), improved_maps=sum(any(p['enabled'] for p in m['props']) for m in maps.values()),
                used_families=len({p['asset'] for p in active}),
                partial=sum(bool(p.get('partial_source_object',False)) for p in active),
                retained=sum(len(m['remaining_2d']) for m in maps.values()),
                artistically_complete=sum(bool(m['validation']['artistically_complete']) for m in maps.values()))


def write_progress(root=ROOT):
    state = json.loads((root / 'docs/combat_visual_25_status.json').read_text())
    counts = metrics(root)
    current_validation = state['validation']['signature'] == render_signature(root)
    target=state.get('target_maps',122)
    complete=counts['maps']==target and counts['artistically_complete']==target and current_validation and bool(state['tasks']) and all(t['status']=='Terminé' for t in state['tasks'])
    lines = ['# Combat Visual 2.5 — avancement de la tâche complète', '',
             'Mis à jour : ' + datetime.now(ZoneInfo('Europe/Paris')).strftime('%d/%m/%Y') + '.', '',
             '**Tâche globale : '+('TERMINÉE' if complete else 'EN COURS')+'.** Le chargement réussi d’une carte ne signifie pas que sa refonte artistique est terminée.', '',
             '## État mesuré dans le projet', '',
             '| Indicateur | État |', '|---|---|',
             f'| Catalogue | {counts["maps"]} cartes / {counts["source_images"]} illustrations distinctes |',
             f'| Bibliothèque | {counts["families"]} familles / {counts["frames"]} vues |',
             f'| Familles réellement placées | {counts["used_families"]} / {counts["families"]} |',
             f'| Placements actifs | {counts["active"]} sur {counts["improved_maps"]} cartes |',
             f'| Dont groupes partiellement remplacés | {counts["partial"]} |',
             f'| Entrées de relevé conservées en 2D | {counts["retained"]} |',
             f'| Cartes déclarées artistiquement terminées | {counts["artistically_complete"]} / {counts["maps"]} |', '',
             'Les entrées de relevé peuvent regrouper plusieurs objets ou des structures. Leur nombre ne permet pas de calculer honnêtement un pourcentage de finition artistique.', '',
             '## Ce qui est livré', '']
    if counts['animation_eligible']:
        position=lines.index('## Ce qui est livré')
        lines[position:position]=['## Animations des unités','',
            '| Indicateur | État |','|---|---|',
            f'| Références d’entités à couvrir (hors objets de mission) | {counts["animation_eligible"]} |',
            f'| Atlas produits | {counts["animation_atlases"]} |',
            f'| Marche et attente à huit directions vérifiées dans Godot | {counts["directional_walk_verified"]} |',
            f'| Unités avec toutes les actions applicables animées et validées | {counts["full_animation_sets"]} |','',
            'Un cycle de marche ne termine pas les animations de combat. Les autres personnages gardent leurs ressources d’origine ; aucune famille n’est remplacée par un clone générique.','']
    lines += ['- ' + item for item in state['delivered']]
    lines += ['', '## Passe en cours', '', '| Travail | État | Résultat / reste à faire |', '|---|---|---|']
    lines += [f'| {t["name"]} | {t["status"]} | {t["detail"]} |' for t in state['tasks']]
    lines += ['', '## Validation', '',
              '- Dernière livraison de référence : `' + state['validation']['reference'] + '`.',
              '- Preuves : [captures et inventaire](' + state['validation']['evidence'] + ').',
              '- Concordance du code, des annotations et des sprites de décor : **' + ('oui' if current_validation else 'non — nouvelle validation requise pour les modifications en cours') + '**.',
              '- ' + state['validation']['summary'], '', '## Reste sur l’objectif complet', '']
    position=lines.index('## Ce qui est livré')
    lines[position:position]=['[Inventaire détaillé par carte](combat_visual_25_inventory.md).','']
    lines += ['- ' + item for item in state['remaining']]
    lines += ['', '## Historique des livraisons', '', '| Référence | Avancée |', '|---|---|']
    lines += [f'| `{h["reference"]}` | {h["summary"]} |' for h in state['history']]
    lines += ['', 'Ce fichier est régénéré par `python tools/art/update_environment_progress.py` à partir des catalogues, de la signature de validation et de `combat_visual_25_status.json`. Aucun indicateur de rendu ne coche automatiquement la finition artistique.', '']
    output = root / 'docs/combat_visual_25_progress.md'
    output.write_text('\n'.join(lines))
    return counts, current_validation


if __name__ == '__main__':
    print(write_progress())
