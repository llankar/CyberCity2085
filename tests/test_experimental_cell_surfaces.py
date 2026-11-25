import importlib.util
from pathlib import Path
from collections import Counter
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('cell_surfaces',Path(__file__).parents[1]/'experiments/2d_to_3d/cell_surfaces.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('cells',[{(0,0):3}, {(0,0):3,(1,0):3}, {(0,0):3,(1,0):.7}, {(x,y):3 for x in range(3) for y in range(3) if (x,y)!=(1,1)}])
def test_closed_volume_and_exact_roof_coverage(cells):
    faces=module.surfaces(cells)
    roofs=[cell for kind,cell,_ in faces if kind=='roof']
    assert set(roofs)==set(cells) and len(roofs)==len(cells)
    edges=Counter(tuple(sorted((points[i],points[(i+1)%4]))) for _,_,points in faces for i in range(4))
    assert set(edges.values())=={2}
    # Independent divergence-volume check also catches reversed wall winding.
    volume=0.
    for _,_,points in faces:
        a,b,c,d=map(np.asarray,points)
        volume+=float(a@np.cross(b,c)+a@np.cross(c,d))/6
    assert volume==pytest.approx(sum(cells.values()))


def test_adjacent_cells_have_no_internal_wall():
    faces=module.surfaces({(0,0):3,(1,0):3})
    assert not any(kind=='wall' and all(point[0]==1 for point in points) for kind,_,points in faces)


@pytest.mark.parametrize('cells',[{}, {(0,0):float('nan')},{(0,0):-1},{(.5,0):3}])
def test_rejects_invalid_cells(cells):
    with pytest.raises(ValueError):module.surfaces(cells)
