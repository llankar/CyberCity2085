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


@pytest.mark.parametrize('defect',['missing','duplicate','wrong_view','wrong_clip'])
def test_rejects_incomplete_or_false_coverage(defect):
    data = manifest()
    if defect == 'missing': data['captures'].pop()
    if defect == 'duplicate': data['captures'][-1]=data['captures'][0]
    if defect == 'wrong_view': data['captures'][0]['camera_axis']='invented'
    if defect == 'wrong_clip': data['clip']='Idle'
    with pytest.raises(ValueError): module.validate_manifest(data)
