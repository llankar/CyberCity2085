import importlib.util
import json
from pathlib import Path
from PIL import Image
import pytest

spec = importlib.util.spec_from_file_location('texture_review155', Path(__file__).parents[1] / 'experiments/2d_to_3d/verify_current_textures155.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

@pytest.fixture
def evidence(tmp_path):
    folder = tmp_path / 'texture_review155'
    folder.mkdir()
    for index, variant in enumerate(('amjviz_wardrobe150','amjviz_budget154_1024')):
        asset = tmp_path / variant / 'human_actions.glb'
        asset.parent.mkdir()
        asset.write_bytes(f'test-fixture-{index}'.encode())
        for facing in ('front','side','back'):
            Image.new('RGB',(1280,720)).save(folder / f'{variant}_{facing}.png')
        data = dict(human_glb_sha256=review.digest(asset),render_texture_size=[1280,720],seconds=5,rendered_frames=100,
                    robot_glb_sha256='robot',facade_glb_sha256='facade',max_draw_calls=571,godot_version='test',
                    begin_utc_unix_s=index*10,end_utc_unix_s=index*10+5,engine_reported_video_bytes=100-index*50)
        (folder / f'{("source","budget")[index]}_benchmark.json').write_text(json.dumps(data))
    return tmp_path

def test_valid_pair(evidence):
    assert review.verify(evidence)['engine_video_memory_reduction_bytes']==50

def test_changed_source_rejected(evidence):
    (evidence / 'amjviz_wardrobe150/human_actions.glb').write_bytes(b'changed')
    with pytest.raises(AssertionError):review.verify(evidence)

def test_overlapping_intervals_rejected(evidence):
    path=evidence / 'texture_review155/budget_benchmark.json'
    data=json.loads(path.read_text());data['begin_utc_unix_s']=4;path.write_text(json.dumps(data))
    with pytest.raises(AssertionError,match='Overlapping'):review.verify(evidence)
