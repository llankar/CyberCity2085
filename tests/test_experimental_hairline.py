import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('hairline',Path(__file__).parents[1]/'experiments/2d_to_3d/hairline.py')
hair=importlib.util.module_from_spec(spec);spec.loader.exec_module(hair)


def test_undercut_keeps_lower_front_quiff_and_raises_nape_and_temples():
    assert hair.cutoff(0,-.06)<hair.cutoff(0,.12)
    assert hair.cutoff(.08,0)==hair.cutoff(-.08,0)>hair.cutoff(0,0)


def test_clipping_planes_match_continuous_hairline():
    for x in (-.1,-.04,0,.04,.1):
        for y in (-.08,0,.15):
            expected=max(p[2]-(n[0]*x+n[1]*y)/n[2] for p,n in hair.planes())
            assert expected==pytest.approx(hair.cutoff(x,y))


@pytest.mark.parametrize('x,y',[(float('nan'),0),(0,float('inf'))])
def test_invalid_landmarks_rejected(x,y):
    with pytest.raises(ValueError):hair.cutoff(x,y)
