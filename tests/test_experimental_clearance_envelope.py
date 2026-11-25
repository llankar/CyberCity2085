import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('clearance_envelope',Path(__file__).parents[1]/'experiments/2d_to_3d/clearance_envelope.py')
envelope=importlib.util.module_from_spec(spec)
spec.loader.exec_module(envelope)


def test_endpoint_lifts_cover_every_interpolated_interval_without_summing_neighbours():
    deficits=[.002,.008,0.]
    result=envelope.endpoint_lifts(deficits)
    assert result==[.002,.008,.008,0.]
    for interval,needed in enumerate(deficits):
        for i in range(101):
            alpha=i/100
            assert result[interval]*(1-alpha)+result[interval+1]*alpha>=needed-1e-15


@pytest.mark.parametrize('values',[[],[-.001],[float('nan')],[float('inf')],['.01']])
def test_invalid_deficits_rejected(values):
    with pytest.raises(ValueError):envelope.endpoint_lifts(values)


def test_periodic_clearance_adds_no_new_loop_height_jump_or_reduces_clearance():
    keys=[.001,0,.003];deficits=[.004,.002]
    result=envelope.periodic_endpoint_lifts(keys,deficits)
    assert keys[0]+result[0]==pytest.approx(keys[-1]+result[-1])
    base=envelope.endpoint_lifts(deficits)
    assert all(a>=b for a,b in zip(result,base))


@pytest.mark.parametrize('keys',[[0],[0,float('nan'),0]])
def test_periodic_invalid_keys_rejected(keys):
    with pytest.raises(ValueError):envelope.periodic_endpoint_lifts(keys,[0,0])
