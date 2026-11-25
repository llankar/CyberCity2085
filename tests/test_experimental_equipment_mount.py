import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('equipment_mount',Path(__file__).parents[1]/'experiments/2d_to_3d/equipment_mount.py')
mount=importlib.util.module_from_spec(spec);spec.loader.exec_module(mount)


def test_mount_stays_in_front_of_every_sample_not_only_average_surface():
    support=(-.084,-.063,-.071);rear=-.134
    shift=mount.front_offset(support,rear)
    assert all(y-(rear+shift)>=.004-1e-9 for y in support)
    assert shift==pytest.approx(.046)


def test_centimeter_meter_mismatch_and_invalid_geometry_are_rejected():
    with pytest.raises(ValueError,match='units'):mount.front_offset([-.08],-13.4)
    with pytest.raises(ValueError):mount.front_offset([],0)
    with pytest.raises(ValueError):mount.front_offset([float('nan')],0)
    with pytest.raises(ValueError):mount.front_offset([-.08],-.1,clearance=-.001)
