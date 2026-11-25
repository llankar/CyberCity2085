import importlib.util
from pathlib import Path
import numpy as np
import pytest

path=Path(__file__).resolve().parents[1]/'experiments/2d_to_3d/wardrobe_skinning.py'
spec=importlib.util.spec_from_file_location('wardrobe_skinning',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
triangle=np.array([[0.,0,0],[1,0,0],[0,1,0]])
weights=[{'hip':1.},{'spine':1.},{'arm':1.}]


def test_face_center_blends_actual_source_bones_equally():
    result,retained=module.surface_weights([1/3,1/3,0],triangle,weights)
    assert result==pytest.approx({'hip':1/3,'spine':1/3,'arm':1/3})
    assert retained==1


def test_transfer_is_rigid_transform_and_unit_scale_invariant():
    point=np.array([.2,.3,0]);first,_=module.surface_weights(point,triangle,weights)
    rotation=np.array([[0,0,1],[1,0,0],[0,1,0]])
    for scale in [.0001,10]:
        transformed=triangle@rotation.T*scale+[3,-2,5]
        other,_=module.surface_weights(point@rotation.T*scale+[3,-2,5],transformed,weights)
        assert other==pytest.approx(first)


def test_trimming_reports_loss_instead_of_claiming_full_weight_preservation():
    maps=[{'a':.2,'b':.2,'c':.2,'d':.2,'e':.2}]*3
    result,retained=module.surface_weights([.2,.2,0],triangle,maps)
    assert len(result)==4 and sum(result.values())==pytest.approx(1)
    assert retained==pytest.approx(.8)


def test_degenerate_face_and_outside_projection_are_rejected():
    with pytest.raises(ValueError,match='Degenerate'):module.surface_weights([0,0,0],[[0,0,0],[1,0,0],[2,0,0]],weights)
    with pytest.raises(ValueError,match='outside'):module.surface_weights([2,2,0],triangle,weights)


def test_invalid_weight_cannot_silently_enter_export():
    with pytest.raises(ValueError,match='Invalid source'):module.surface_weights([0,0,0],triangle,[{'hip':float('nan')},{'hip':1},{'hip':1}])


def test_eight_slot_export_keeps_six_real_influences_instead_of_lowering_retention_gate():
    source=[{'a':.5,'b':.5},{'c':.5,'d':.5},{'e':.5,'f':.5}]
    trimmed,loss=module.surface_weights([1/3,1/3,0],triangle,source,limit=4)
    full,retained=module.surface_weights([1/3,1/3,0],triangle,source,limit=8)
    assert len(trimmed)==4 and loss==pytest.approx(2/3)
    assert len(full)==6 and retained==pytest.approx(1)
    assert sum(full.values())==pytest.approx(1)
