"""Actual embedded Blender cache check; environment variables alone are ignored."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent))
import anatomical_groups
expected=Path('E:/CyberCity2085-3d-lab/cache/python').resolve()
actual=Path(anatomical_groups.__cached__).resolve()
assert Path(sys.pycache_prefix).resolve()==expected and actual.is_relative_to(expected)
assert actual.is_file(),'Expected compiled module under the E: cache'
Path('E:/CyberCity2085-3d-lab/tmp/python_cache_check.json').write_text(json.dumps({'prefix':str(expected),'actual_import_cache':str(actual),'exists':True},indent=2))
print('EXPERIMENT_PYTHON_CACHE_ON_E',actual,flush=True)
