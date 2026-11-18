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
    return dict(maps=len(maps), source_images=len({m['image_sha256'] for m in maps.values()}),
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
