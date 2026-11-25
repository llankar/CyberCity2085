import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('sole161',Path(__file__).parents[1]/'experiments/2d_to_3d/verify_sole_contact161.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def evidence(drift,support):
    return {'clips':{'pose':{'maximum_lowest_sole_height_m':support,'metrics':{'L':{'maximum_individual_contact_vertex_drift_m':drift}}}}}

def test_real_contact_limits_pass():
    result=module.assess(evidence(.001,.001))['pose']
    assert result['support']=='PASS' and result['individual_contact_drift']=='PASS'

def test_small_average_cannot_hide_slipping_points():
    assert module.assess(evidence(.0056,.001))['pose']['individual_contact_drift']=='FAIL'

def test_still_feet_cannot_hide_missing_support():
    assert module.assess(evidence(.001,.06))['pose']['support']=='FAIL'
