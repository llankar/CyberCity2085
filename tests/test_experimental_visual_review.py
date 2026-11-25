import importlib.util,json
from pathlib import Path
from PIL import Image
import pytest
spec=importlib.util.spec_from_file_location('review163',Path(__file__).parents[1]/'experiments/2d_to_3d/verify_visual_review163.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.fixture
def capture(tmp_path):
    path=tmp_path/'capture.png';Image.new('RGB',(32,18)).save(path)
    model=tmp_path/'fixture.glb';model.write_bytes(b'unit-test-hash-fixture')
    meta={'capture_sha256':module.sha(path),'render_texture_size':[32,18],'diagnostics_visible':False,
          'models':{'human':{'path':str(model).replace('\\','/'),'sha256':module.sha(model)}}}
    Path(str(path)+'.json').write_text(json.dumps(meta))
    return path,{'human':model}

def test_original_capture_verified(capture):
    path,models=capture
    assert module.verify_capture(path,models,(32,18))['diagnostics_visible'] is False

def test_changed_pixels_rejected(capture):
    path,models=capture;Image.new('RGB',(32,18),'white').save(path)
    with pytest.raises(AssertionError,match='Capture changed'):module.verify_capture(path,models,(32,18))

def test_changed_model_rejected(capture):
    path,models=capture;models['human'].write_bytes(b'changed')
    with pytest.raises(AssertionError,match='Model changed'):module.verify_capture(path,models,(32,18))
