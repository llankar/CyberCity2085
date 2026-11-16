"""Blender batch export from AUTHORED rigged .blend files, never from flat PNGs.

blender -b character.blend --python-exit-code 1 --python tools/render_combat_atlas.py -- \
  --key agent_samurai --root /path/to/CyberCity2085

The .blend must contain: a rig with active action slots; one camera; lighting;
and actions named idle, move, fire, melee, cover, hit, death, psi, heal.
All clips must animate at least two distinct poses. The exporter uses each
clip's authored frame range, renders eight camera views with a fixed foot
origin, and packs unique frames. It does not synthesize missing animations.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path


def main():
    import bpy
    from mathutils import Vector
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key', required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--size', type=int, default=256)
    parser.add_argument('--fps', type=int, default=12)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    required = ['idle','move','fire','melee','cover','hit','death','psi','heal']
    missing = [name for name in required if name not in bpy.data.actions]
    if missing:
        raise RuntimeError('Missing authored clips: '+', '.join(missing))
    scene = bpy.context.scene
    if scene.camera is None:
        raise RuntimeError('Authored camera and lighting required')
    rigs = [obj for obj in scene.objects if obj.type == 'ARMATURE']
    if len(rigs) != 1:
        raise RuntimeError('Exactly one authored rig required per asset')
    rig = rigs[0]
    rig.animation_data_create()
    out = args.root/'work/combat_renders'/args.key
    out.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.fps = args.fps
    camera = scene.camera
    # Preserve the authored framing and orthographic scale around foot origin.
    if camera.data.type != 'ORTHO':
        raise RuntimeError('Orthographic camera required for isometric sprites')
    radius = math.hypot(camera.location.x, camera.location.y)
    camera_z = camera.location.z
    focus_z = float(scene.get('combat_focus_z', 0.9))
    clips = {}
    files = []
    for name in required:
        action = bpy.data.actions[name]
        start, end = map(int, action.frame_range)
        if end <= start:
            raise RuntimeError(f'{name}: at least two authored frames required')
        rig.animation_data.action = action
        if hasattr(action, 'slots') and len(action.slots):
            rig.animation_data.action_slot = action.slots[0]
        rows = []
        for direction in range(8):
            angle = direction*math.tau/8
            camera.location = (radius*math.cos(angle), radius*math.sin(angle), camera_z)
            camera.rotation_euler = (Vector((0,0,focus_z))-camera.location).to_track_quat('-Z','Y').to_euler()
            frames = []
            for frame in range(start, end+1):
                scene.frame_set(frame)
                path = out/f'{name}_{direction}_{frame:04d}.png'
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
                frames.append(len(files))
                files.append(str(path))
            rows.append(frames)
        clips[name] = {'fps':args.fps,'loop':name in ['idle','move','cover'],'rows':rows}
    # Blender Python need not have Pillow: pack via Blender image pixels.
    columns = 2 ** math.ceil(math.log2(math.sqrt(len(files))))
    rows = math.ceil(len(files)/columns)
    if columns*args.size > 16384 or rows*args.size > 16384:
        raise RuntimeError("Atlas exceeds 16384px; shorten authored clips or reduce --size")
    import numpy as np
    pixels = np.zeros((rows*args.size,columns*args.size,4),dtype=np.float32)
    for index, filename in enumerate(files):
        image = bpy.data.images.load(filename, check_existing=False)
        raw = np.empty(args.size*args.size*4,dtype=np.float32)
        image.pixels.foreach_get(raw)
        x = index%columns*args.size
        y = (rows-1-index//columns)*args.size
        pixels[y:y+args.size,x:x+args.size] = raw.reshape(args.size,args.size,4)
        bpy.data.images.remove(image)
    dest = args.root/'assets/combat_visual/animations'
    dest.mkdir(parents=True,exist_ok=True)
    atlas = bpy.data.images.new(args.key,width=columns*args.size,height=rows*args.size,alpha=True)
    atlas.pixels.foreach_set(pixels.ravel())
    atlas.filepath_raw = str(dest/f'{args.key}.png')
    atlas.file_format = 'PNG'
    atlas.save()
    data = {'texture':f'assets/combat_visual/animations/{args.key}.png','frame_size':[args.size,args.size],
            'directions':'E,SE,S,SW,W,NW,N,NE in projected world space','animations':clips,
            'source':bpy.data.filepath,'generator':'tools/render_combat_atlas.py'}
    (dest/f'{args.key}.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Exported authored animation atlas. Run audit_combat_visuals.py before integration.')

if __name__ == '__main__':
    main()
