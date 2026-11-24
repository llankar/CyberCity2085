"""Render eight isometric directions from an experimental Blender source."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--size", type=int, default=256)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def main() -> None:
    args = arguments()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(Path(args.blend).resolve()))

    subject = bpy.data.objects.get(args.name)
    if subject is None or subject.type != "MESH":
        raise RuntimeError(f"Mesh object not found: {args.name}")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj != subject:
            obj.hide_render = True

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = args.size
    scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True

    camera = scene.camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.45 * max(subject.dimensions)
    distance = 3.0 * max(subject.dimensions)
    target = Vector((0.0, 0.0, subject.dimensions.z * 0.45))
    original_rotation = subject.rotation_euler.copy()
    frames: list[Path] = []
    for index in range(8):
        angle = math.tau * index / 8.0
        subject.rotation_euler = original_rotation
        subject.rotation_euler.z += angle
        camera.location = Vector((distance, -distance, distance * 0.8))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        frame = output / f"{args.name}_{index:02d}.png"
        scene.render.filepath = str(frame)
        bpy.ops.render.render(write_still=True)
        frames.append(frame)

    atlas = bpy.data.images.new(
        f"{args.name}_atlas", width=args.size * 8, height=args.size, alpha=True
    )
    pixels = [0.0] * (args.size * 8 * args.size * 4)
    for index, frame in enumerate(frames):
        image = bpy.data.images.load(str(frame), check_existing=False)
        source = list(image.pixels)
        for y in range(args.size):
            src = y * args.size * 4
            dst = (y * args.size * 8 + index * args.size) * 4
            pixels[dst : dst + args.size * 4] = source[src : src + args.size * 4]
        bpy.data.images.remove(image)
    atlas.pixels = pixels
    atlas.filepath_raw = str(output / f"{args.name}_atlas.png")
    atlas.file_format = "PNG"
    atlas.save()
    print(f"CYBERCITY_ATLAS_OK name={args.name} directions=8 size={args.size}")


if __name__ == "__main__":
    main()

