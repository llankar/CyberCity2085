"""Progress never equates native load coverage with artistic completion."""
import json
from pathlib import Path
from tools.art.update_environment_progress import metrics, render_signature, write_progress


def fixture(root):
    art=root/'godot/combat_missions_ui/art/environment'
    (art/'props25').mkdir(parents=True)
    (root/'docs').mkdir()
    (art/'environment_art.json').write_text(json.dumps({'maps':{
        'a.png':{'image_sha256':'same','props':[{'enabled':True,'asset':'sample'},{'enabled':True,'asset':'sample','partial_source_object':True}],
                 'remaining_2d':['walls'],'validation':{'native_render':'passed','artistically_complete':False}},
        'b.png':{'image_sha256':'same','props':[{'enabled':False}],
                 'remaining_2d':['walls','furniture'],'validation':{'native_render':'passed','artistically_complete':False}},
    }}))
    (art/'props25/library.json').write_text(json.dumps({'assets':{'sample':{'yaw':[0,90,180,270]}}}))
    state=dict(delivered=[],tasks=[],remaining=['Architecture à finir'],history=[],
               validation=dict(signature=render_signature(root),reference='fixture',evidence='evidence.md',summary='Deux rendus natifs vérifiés.'))
    (root/'docs/combat_visual_25_status.json').write_text(json.dumps(state))


def test_counts_distinguish_placements_maps_and_source_entries(tmp_path):
    fixture(tmp_path)
    counts=metrics(tmp_path)
    assert (counts['active'],counts['improved_maps'],counts['source_images'],counts['retained'])==(2,1,1,3)


def test_native_passes_do_not_complete_the_art_task(tmp_path):
    fixture(tmp_path)
    counts,current=write_progress(tmp_path)
    text=(tmp_path/'docs/combat_visual_25_progress.md').read_text()
    assert current and counts['artistically_complete']==0
    assert '**Tâche globale : EN COURS.**' in text and '| 0 / 2 |' in text
    assert 'pourcentage de finition artistique' in text and '100%' not in text


def test_changed_renderer_requires_a_new_validation(tmp_path):
    fixture(tmp_path)
    scripts=tmp_path/'godot/combat_missions_ui/scripts';scripts.mkdir()
    (scripts/'renderer.gd').write_text('extends Node2D\n')
    _,current=write_progress(tmp_path)
    assert not current
    assert 'nouvelle validation requise' in (tmp_path/'docs/combat_visual_25_progress.md').read_text()


def test_an_approved_subset_does_not_finish_the_122_map_goal(tmp_path):
    fixture(tmp_path)
    path=tmp_path/'godot/combat_missions_ui/art/environment/environment_art.json'
    data=json.loads(path.read_text())
    for record in data['maps'].values():record['validation']['artistically_complete']=True
    path.write_text(json.dumps(data))
    state_path=tmp_path/'docs/combat_visual_25_status.json';state=json.loads(state_path.read_text())
    state['tasks']=[dict(name='Passe',status='Terminé',detail='Fini')]
    state['validation']['signature']=render_signature(tmp_path);state_path.write_text(json.dumps(state))
    _,current=write_progress(tmp_path)
    assert current and '**Tâche globale : EN COURS.**' in (tmp_path/'docs/combat_visual_25_progress.md').read_text()


def test_changed_sprite_invalidates_validation_even_without_manifest_update(tmp_path):
    fixture(tmp_path)
    sprite=tmp_path/ 'godot/combat_missions_ui/art/environment/props25/sample-0.png'
    sprite.write_bytes(b'changed production texture')
    _,current=write_progress(tmp_path)
    assert not current


def test_animation_files_do_not_invalidate_map_art_validation(tmp_path):
    fixture(tmp_path)
    directory=tmp_path/'assets/combat_visual/animations';directory.mkdir(parents=True)
    (directory/'new_walk.png').write_bytes(b'changed animation frame data')
    _,current=write_progress(tmp_path)
    assert current


def test_map_scale_data_invalidates_previous_render_evidence(tmp_path):
    fixture(tmp_path)
    path=tmp_path/'godot/combat_missions_ui/art/environment/map_presentation.json'
    path.write_text('{"maps":{"a.png":{"human_height_ratio":0.03}}}')
    _,current=write_progress(tmp_path)
    assert not current
