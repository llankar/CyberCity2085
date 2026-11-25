import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('wrist_ownership',Path(__file__).parents[1]/'experiments/2d_to_3d/verify_wrist_ownership.py')
ownership=importlib.util.module_from_spec(spec);spec.loader.exec_module(ownership)


def test_bright_body_and_glove_pixels_are_surfaces_and_background_is_separate():
    original=np.array([[[240,220,180],[230,210,190],[200,180,160],[40,40,40]]],dtype=np.uint8)
    owner=np.array([[[255,0,255],[0,255,255],[40,40,40],[255,0,255]]],dtype=np.uint8)
    assert ownership.analyze(original,owner,(0,0,4,1))=={'bright_band_pixels':3,'bright_pixels_on_retained_body':1,'bright_pixels_on_authored_glove':1}


@pytest.mark.parametrize('roi',[(-1,0,1,1),(0,0,0,1),(0,0,3,1)])
def test_invalid_crop_is_rejected(roi):
    image=np.zeros((1,2,3),dtype=np.uint8)
    with pytest.raises(ValueError):ownership.analyze(image,image,roi)
