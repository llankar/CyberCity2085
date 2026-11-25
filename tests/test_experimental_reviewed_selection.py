import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('reviewed_selection',Path(__file__).parents[1]/'experiments/2d_to_3d/reviewed_selection.py')
selection=importlib.util.module_from_spec(spec);spec.loader.exec_module(selection)


def test_reviewed_selection_cannot_transfer_to_another_asset():
    document={'source_glb_sha256':'original','selected':[2,5]}
    assert selection.face_selection(document,'original',6)=={2,5}
    with pytest.raises(ValueError):selection.face_selection(document,'changed',6)


@pytest.mark.parametrize('faces',[[],[1,1],[-1],[6],[True],[1.0]])
def test_invalid_topology_selection_rejected(faces):
    with pytest.raises(ValueError):selection.face_selection({'source_glb_sha256':'original','selected':faces},'original',6)
