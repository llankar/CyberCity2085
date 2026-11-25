import importlib.util
from pathlib import Path
import numpy as np
import pytest
import sys

sys.path.insert(0,str(Path(__file__).parents[1]/'experiments/2d_to_3d'))
spec=importlib.util.spec_from_file_location('audit_robot_alpha',Path(__file__).parents[1]/'experiments/2d_to_3d/audit_robot_alpha.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def test_interleaved_uv_accessor_respects_both_offsets_and_stride():
    binary=b'xxxx'+np.array([[88,.1,.2,99],[77,.3,.4,66]],dtype='<f4').tobytes()
    doc={'accessors':[{'componentType':5126,'type':'VEC2','count':2,'bufferView':0,'byteOffset':4}],
         'bufferViews':[{'byteOffset':4,'byteStride':16}]}
    assert audit.accessor(doc,binary,0)==pytest.approx(np.array([[.1,.2],[.3,.4]]))


def test_triangle_footprint_does_not_invent_full_rectangular_coverage():
    mask=np.asarray(audit.footprint((32,32),[[.1,.1],[.8,.1],[.1,.8]],[[0,1,2]]))
    assert mask[5,5]==255
    assert mask[26,26]==0


def test_uv_wrap_is_rejected_instead_of_silently_clipped():
    with pytest.raises(ValueError,match='Wrapped'):
        audit.footprint((32,32),[[-.1,0],[1,0],[0,1]],[[0,1,2]])
