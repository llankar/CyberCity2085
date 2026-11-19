"""A subset, stale evidence or missing test run can never finish the project."""
import hashlib
import json
from pathlib import Path
import pytest
from tools import check_combat_visual_acceptance as check


def test_done_requires_tests_existing_evidence_and_no_remaining_work(tmp_path):
    task=dict(id='x', status='DONE', files=['a'], tests=[], evidence=['missing'], remaining='still open')
    issues=check.registry_issues(tmp_path, {'tasks':[task]})
    assert len(issues)==3


def test_blocked_requires_explicit_reason(tmp_path):
    task=dict(id='x',status='BLOCKED',files=[],tests=[],evidence=[],remaining='waiting')
    assert any('raison' in item for item in check.registry_issues(tmp_path, {'tasks':[task]}))


def test_invalid_status_and_duplicate_ids_fail(tmp_path):
    task=dict(id='x',status='COMPLETE',files=[],tests=[],evidence=[],remaining='')
    issues=check.registry_issues(tmp_path, {'tasks':[task,task]})
    assert any('dupliqué' in issue for issue in issues)
    assert any('statut invalide' in issue for issue in issues)


def test_missing_review_is_not_verified(tmp_path):
    assert check.manual_review(tmp_path,None,'current')[0]=='NOT VERIFIED'


def review(tmp_path):
    proof=tmp_path/'proof.txt';proof.write_text('Actual review evidence')
    return dict(status='PASS',scope='Only the reviewed fixture',render_signature='current',evidence=[dict(path='proof.txt',sha256=hashlib.sha256(proof.read_bytes()).hexdigest())])


def test_review_is_bound_to_scope_evidence_and_current_render(tmp_path):
    record=review(tmp_path)
    assert check.manual_review(tmp_path,record,'current')[0]=='PASS'
    assert check.manual_review(tmp_path,record,'new-render')[0]=='NOT VERIFIED'
    record['scope']=''
    assert check.manual_review(tmp_path,record,'current')[0]=='NOT VERIFIED'


def test_changed_or_missing_proof_cannot_pass(tmp_path):
    record=review(tmp_path);(tmp_path/'proof.txt').write_text('changed')
    assert check.manual_review(tmp_path,record,'current')[0]=='NOT VERIFIED'
    (tmp_path/'proof.txt').unlink()
    assert check.manual_review(tmp_path,record,'current')[0]=='NOT VERIFIED'


def test_missing_test_run_is_unknown_not_zero_failures(tmp_path):
    result=check.test_counts(tmp_path,{})
    assert result['passed'] is None and result['failed'] is None
    assert result['not_executed']=='UNKNOWN'


def test_junit_counts_failures_errors_skips_and_limits_scope(tmp_path):
    path=tmp_path/'tests.xml';path.write_text('<testsuites><testsuite><testcase name="pass"/><testcase name="fail"><failure/></testcase><testcase name="error"><error/></testcase><testcase name="skip"><skipped/></testcase></testsuite></testsuites>')
    record=dict(path='tests.xml',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='checker only',not_executed=['gameplay'])
    result=check.test_counts(tmp_path,record)
    assert (result['passed'],result['failed'],result['skipped'])==(1,2,1)
    assert result['scope']=='checker only' and result['not_executed']==['gameplay']
    path.write_text('corrupt')
    assert check.test_counts(tmp_path,record)['passed'] is None


def test_evidence_cannot_escape_repository(tmp_path):
    assert check.evidence_file(tmp_path,'../outside.txt') is None


@pytest.fixture
def project(tmp_path,monkeypatch):
    monkeypatch.setattr(check,'EXPECTED_MAPS',2)
    docs=tmp_path/'docs';docs.mkdir()
    art=tmp_path/'godot/combat_missions_ui/art/environment';(art/'props25').mkdir(parents=True)
    (art/'props25/library.json').write_text(json.dumps({'assets':{'prop':{'yaw':[0]}}}))
    (art/'props25/prop-0.png').write_bytes(b'fixture')
    maps={'a.png':{'validation':{'artistically_complete':False}},'b.png':{'validation':{'artistically_complete':False}}}
    (art/'environment_art.json').write_text(json.dumps({'maps':maps}))
    (docs/'CODEX_PROGRESS.json').write_text(json.dumps(dict(expected_maps=2,tasks=[],next_action='Review a.png')))
    (docs/'combat_visual_25_status.json').write_text(json.dumps({'validation':{'signature':'current'}}))
    native=docs/'images/combat-directional-animation';native.mkdir(parents=True)
    (native/'catalogue-01.jpg').write_bytes(b'fixture proof')
    (native/'native-report.json').write_text(json.dumps([dict(map=m,native_render=True,projection_and_zoom_checked=True) for m in maps]))
    monkeypatch.setattr(check,'render_signature',lambda root:'current')
    monkeypatch.setattr(check,'metrics',lambda root:dict(frames=1,families=1,active=1,improved_maps=1,retained=5,animation_eligible=2))
    monkeypatch.setattr(check,'audit',lambda root:dict(maps=[dict(image=m) for m in maps],summary=dict(surveyed_maps=2,invalid_map_hashes=0,unit_art=2,animated_units_complete=0,animated_units_partial=1)))
    return tmp_path


def criterion(report,key):return next(row for row in report['criteria'] if row['id']==key)


def test_all_maps_loaded_still_leaves_global_incomplete(project):
    report=check.build_report(project)
    assert criterion(report,'MAP-LOAD')['status']=='PASS'
    assert criterion(report,'MAP-ART')['status']=='FAIL'
    assert report['global_status']=='CHANTIER GLOBAL INCOMPLET'
    assert report['maps']['native_verified']==2 and report['maps']['artistic_verified']==0


def test_declared_art_completion_without_review_never_passes(project):
    path=project/'godot/combat_missions_ui/art/environment/environment_art.json'
    data=json.loads(path.read_text())
    for row in data['maps'].values():row['validation']['artistically_complete']=True
    path.write_text(json.dumps(data))
    assert criterion(check.build_report(project),'MAP-ART')['status']=='NOT VERIFIED'


def test_stale_native_evidence_is_not_verified(project,monkeypatch):
    monkeypatch.setattr(check,'render_signature',lambda root:'changed')
    report=check.build_report(project)
    assert criterion(report,'MAP-LOAD')['status']=='NOT VERIFIED'
    assert report['maps']['native_verified']==0


def test_missing_art_file_fails_resource_coverage(project):
    (project/'godot/combat_missions_ui/art/environment/props25/prop-0.png').unlink()
    report=check.build_report(project)
    assert criterion(report,'ART-FILES')['status']=='FAIL'
    assert report['resources']['missing_views']==['prop-0.png']


def test_report_separates_tasks_tests_native_loading_and_art(project):
    report=check.build_report(project);text=check.render_report(report)
    assert 'CHANTIER GLOBAL INCOMPLET' in text
    assert '0 / 2' in text and 'artistiquement' in text
    assert report['tests']['passed'] is None
    assert report['resources']['artistic_expected_objects'] is None


def test_missing_native_capture_proof_is_not_verified(project):
    (project/'docs/images/combat-directional-animation/catalogue-01.jpg').unlink()
    assert criterion(check.build_report(project),'MAP-LOAD')['status']=='NOT VERIFIED'


def test_register_cannot_reduce_the_expected_catalogue(project):
    path=project/'docs/CODEX_PROGRESS.json';data=json.loads(path.read_text());data['expected_maps']=1;path.write_text(json.dumps(data))
    report=check.build_report(project)
    assert report['maps']['native_expected']==2
    assert criterion(report,'MAP-SOURCE')['status']=='FAIL'


def test_unfinished_tasks_remain_an_open_global_criterion(project):
    path=project/'docs/CODEX_PROGRESS.json';data=json.loads(path.read_text());data['tasks']=[dict(id='later',status='TODO',files=[],tests=[],evidence=[],remaining='next batch')];path.write_text(json.dumps(data))
    assert criterion(check.build_report(project),'TASK-COMPLETION')['status']=='FAIL'


def test_permanent_rules_preserve_quality_and_distinguish_batches():
    root=Path(__file__).resolve().parents[1];text=(root/'AGENTS.md').read_text(encoding='utf-8')
    assert 'tasks per batch' not in text and 'any number of successive batches' in text
    assert 'Modularity' in text and 'Scope control' in text
    assert 'CHANTIER GLOBAL INCOMPLET' in text
    assert 'ne pas publier sans mon accord' not in text.lower()


def test_changed_tested_sources_invalidate_recorded_results(tmp_path):
    xml=tmp_path/'tests.xml';xml.write_text('<testsuite><testcase name="pass"/></testsuite>')
    source=tmp_path/'tested.py';source.write_text('original')
    record=dict(path='tests.xml',sha256=hashlib.sha256(xml.read_bytes()).hexdigest(),sources=[dict(path='tested.py',sha256=hashlib.sha256(source.read_bytes()).hexdigest())])
    assert check.test_counts(tmp_path,record)['passed']==1
    source.write_text('changed implementation')
    assert check.test_counts(tmp_path,record)['passed'] is None


def test_failed_refresh_invalidates_an_older_positive_report(tmp_path):
    import subprocess,sys
    reports=tmp_path/'docs/reports';reports.mkdir(parents=True)
    path=reports/'combat_visual_acceptance.json';path.write_text('{"global_status":"PASS"}')
    result=subprocess.run([sys.executable,'-m','tools.check_combat_visual_acceptance','--root',str(tmp_path),'--write'],capture_output=True,text=True)
    assert result.returncode==2
    current=json.loads(path.read_text())
    assert current['global_status']=='CHANTIER GLOBAL INCOMPLET'
    assert current['criteria'][0]['status']=='NOT VERIFIED'


def test_scale_review_is_separate_from_successful_loading(project):
    report=check.build_report(project)
    assert criterion(report,'MAP-LOAD')['status']=='PASS'
    assert criterion(report,'UNIT-SCALE')['status']=='NOT VERIFIED'
    assert '0 / 2' in criterion(report,'UNIT-SCALE')['detail']


def test_native_checks_follow_the_current_validation_evidence(project):
    old=project/'docs/images/combat-directional-animation'
    new=project/'docs/images/current-batch';old.rename(new)
    state_path=project/'docs/combat_visual_25_status.json'
    state=json.loads(state_path.read_text());state['validation']['evidence']='images/current-batch/README.md';state_path.write_text(json.dumps(state))
    report=check.build_report(project)
    assert criterion(report,'MAP-LOAD')['status']=='PASS'
    assert criterion(report,'MAP-LOAD')['evidence'][0]=='docs/images/current-batch/native-report.json'
