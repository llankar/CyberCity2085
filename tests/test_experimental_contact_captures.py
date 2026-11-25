import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('review_contact_captures',Path(__file__).parents[1]/'experiments/2d_to_3d/review_contact_captures.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def manifest():
    return {'clip':'Shoot','captures':[{'camera_axis':view,'fraction':i/16} for view in ('posX','negX','posZ','negZ') for i in range(17)]}


def test_full_coverage():
    assert len(module.validate_manifest(manifest())) == 68


def motion_manifest():
    return {'captures':[{'clip':clip,'view':view,'fraction':i/5,'time_s':i/5,
                         'file':f'{clip}/{view}/{i}.png'}
                        for clip in module.MOTIONS for view in module.VIEWS for i in range(6)]}


def test_motion_review_full_coverage():
    assert len(module.validate_motion_manifest(motion_manifest()))==120


@pytest.mark.parametrize('defect',['missing','duplicate','wrong_clip','wrong_view','file_reuse','clock','nan'])
def test_motion_review_rejects_false_coverage(defect):
    data=motion_manifest();entries=data['captures']
    if defect=='missing':entries.pop()
    if defect=='duplicate':entries[-1]=entries[0]
    if defect=='wrong_clip':entries[0]['clip']='Run'
    if defect=='wrong_view':entries[0]['view']='invented'
    if defect=='file_reuse':entries[-1]['file']=entries[0]['file']
    if defect=='clock':entries[6]['time_s']=.5
    if defect=='nan':entries[0]['time_s']=float('nan')
    with pytest.raises(ValueError):module.validate_motion_manifest(data)


@pytest.mark.parametrize('defect',['missing','duplicate','wrong_view','wrong_clip'])
def test_rejects_incomplete_or_false_coverage(defect):
    data = manifest()
    if defect == 'missing': data['captures'].pop()
    if defect == 'duplicate': data['captures'][-1]=data['captures'][0]
    if defect == 'wrong_view': data['captures'][0]['camera_axis']='invented'
    if defect == 'wrong_clip': data['clip']='Idle'
    with pytest.raises(ValueError): module.validate_manifest(data)
