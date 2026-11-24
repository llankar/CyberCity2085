"""Fit licensed authored MHCLO assets to the preserved MPFB prototype."""
import argparse
import sys
from pathlib import Path
import bpy
from bl_ext.blender_org.mpfb.services.humanservice import HumanService

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', required=True)
parser.add_argument('--clothes', action='append', default=[])
parser.add_argument('--hair')
parser.add_argument('--skin')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
output = Path(args.output_dir).resolve()
if output.drive.upper() != 'E:':
    raise ValueError('Generated assets must remain on E:')
for asset in args.clothes + [p for p in [args.hair, args.skin] if p]:
    if not Path(asset).is_file():
        raise FileNotFoundError(asset)
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/CyberCity2085-3d-lab/generated/phase2/rook_mpfb/rook_mpfb.blend')
body = bpy.data.objects['rook_mpfb']
for asset in args.clothes:
    HumanService.add_mhclo_asset(asset, body, asset_type='Clothes', subdiv_levels=1, material_type='MAKESKIN')
if args.hair:
    HumanService.add_mhclo_asset(args.hair, body, asset_type='Hair', subdiv_levels=1, material_type='MAKESKIN')
if args.skin:
    HumanService.set_character_skin(args.skin, body, skin_type='MAKESKIN')
for lamp in [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']:
    lamp.data.color = (1, 1, 1)
    lamp.data.energy = 450
bpy.context.scene.world.color = (0.18, 0.18, 0.18)
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'authored_outfit.blend'))
bpy.context.scene.render.filepath = str(output / 'authored_outfit_preview.png')
bpy.ops.render.render(write_still=True)
print('MPFB_AUTHORED_OUTFIT_SAVED')
