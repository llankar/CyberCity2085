"""Validate an official MPFB asset pack and install in the external profile."""
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from bl_ext.blender_org.mpfb.services.assetservice import AssetService
from bl_ext.blender_org.mpfb.services.locationservice import LocationService

archive = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
target = Path(LocationService.get_user_data()).resolve()
if archive.drive.upper() != 'E:' or target.drive.upper() != 'E:':
    raise ValueError('Pack and MPFB data must reside on E:')
tempfile.tempdir = 'E:/CyberCity2085-3d-lab/tmp'
with zipfile.ZipFile(archive) as pack:
    for entry in pack.infolist():
        resolved = (target / entry.filename).resolve()
        if not resolved.is_relative_to(target):
            raise ValueError('Unsafe ZIP path: ' + entry.filename)
    failure = pack.testzip()
    if failure:
        raise ValueError('ZIP CRC failure: ' + failure)
error = AssetService.check_asset_pack_zip(str(archive))
if error:
    raise ValueError('Invalid pack structure: ' + error)
error = AssetService.fix_and_extract_asset_pack_zip(str(archive), str(target))
if error:
    raise RuntimeError(error)
AssetService.rescan_pack_metadata()
AssetService.update_all_asset_lists()
print('MPFB_PACK_INSTALLED', target)
print(json.dumps([str(path.relative_to(target)) for path in target.rglob('*.mhclo')], indent=2))
