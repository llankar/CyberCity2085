import importlib.util,math
from pathlib import Path
import pytest
p=Path(__file__).parents[1]/'experiments/2d_to_3d/atlas_facing.py'
s=importlib.util.spec_from_file_location('atlas_facing',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def projections():
    return [(-math.cos(i*math.tau/8),-math.sin(i*math.tau/8)*math.sin(.6)) for i in range(8)]

def test_measured_source_forward_and_view_order_match_existing_sectors():
    assert m.facing_lookup(projections())==[4,5,6,7,0,1,2,3]
    assert m.facing_lookup(projections()[2:]+projections()[:2])==[2,3,4,5,6,7,0,1]

@pytest.mark.parametrize('bad',[[(1.,0.)]*8,[(0.,0.)]*8,[(float('nan'),1.)]*8,[(1.,0.)]*7])
def test_missing_duplicate_degenerate_projections_rejected(bad):
    with pytest.raises(ValueError):m.facing_lookup(bad)
