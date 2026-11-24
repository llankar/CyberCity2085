"""Import an AI mesh, normalize it, optimize it and export Blender/GLB assets."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--target-faces", type=int, default=20_000)
    parser.add_argument("--size-m", type=float, default=1.0)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def mesh_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return Vector(map(min, zip(*points))), Vector(map(max, zip(*points)))


def add_stage(size: float) -> None:
    bpy.ops.mesh.primitive_plane_add(size=max(4.0, size * 4.0), location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "PreviewFloor"
    material = bpy.data.materials.new("PreviewFloorMaterial")
    material.diffuse_color = (0.015, 0.025, 0.04, 1.0)
    floor.data.materials.append(material)

    world = bpy.context.scene.world or bpy.data.worlds.new("PreviewWorld")
    bpy.context.scene.world = world
    world.color = (0.008, 0.012, 0.02)
    for location, energy, color, size_lamp in (
        ((3, -4, 5), 900, (0.1, 0.8, 1.0), 4.0),
        ((-3, -1, 3), 700, (1.0, 0.25, 0.08), 3.0),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.color = color
        light.data.shape = "DISK"
        light.data.size = size_lamp


def add_camera(size: float) -> None:
    bpy.ops.object.camera_add(location=(2.4 * size, -3.0 * size, 2.1 * size))
    camera = bpy.context.object
    direction = Vector((0, 0, size * 0.45)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 58
    bpy.context.scene.camera = camera


def main() -> None:
    args = arguments()
    source = Path(args.input).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    if source.suffix.lower() != ".obj":
        raise ValueError(f"Unsupported source format: {source.suffix}")
    bpy.ops.wm.obj_import(filepath=str(source), forward_axis="NEGATIVE_Z", up_axis="Y")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("The import produced no mesh")

    texture_path = source.with_name("texture.png")
    if texture_path.is_file():
        material = bpy.data.materials.new(f"{args.name}_material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        shader = nodes.get("Principled BSDF")
        image = nodes.new("ShaderNodeTexImage")
        image.image = bpy.data.images.load(str(texture_path), check_existing=True)
        material.node_tree.links.new(image.outputs["Color"], shader.inputs["Base Color"])
        material.node_tree.links.new(image.outputs["Alpha"], shader.inputs["Alpha"])
        material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
        for obj in meshes:
            obj.data.materials.clear()
            obj.data.materials.append(material)

    low, high = mesh_bounds(meshes)
    extent = max(high[i] - low[i] for i in range(3))
    scale = args.size_m / extent if extent else 1.0
    center = (low + high) * 0.5
    for obj in meshes:
        obj.location -= center
        obj.scale *= scale
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)

    low, _ = mesh_bounds(meshes)
    for obj in meshes:
        obj.location.z -= low.z

    original_faces = sum(len(obj.data.polygons) for obj in meshes)
    ratio = min(1.0, args.target_faces / max(1, original_faces))
    if ratio < 0.999:
        for obj in meshes:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            modifier = obj.modifiers.new("RealtimeDecimate", "DECIMATE")
            modifier.ratio = ratio
            modifier.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            obj.select_set(False)

    for obj in meshes:
        obj.name = args.name
        for polygon in obj.data.polygons:
            polygon.use_smooth = True

    add_stage(args.size_m)
    add_camera(args.size_m)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(output / f"{args.name}_preview.png")
    scene.render.image_settings.color_mode = "RGBA"

    bpy.ops.wm.save_as_mainfile(filepath=str(output / f"{args.name}.blend"))
    bpy.ops.render.render(write_still=True)

    for obj in bpy.context.scene.objects:
        obj.select_set(obj in meshes)
    bpy.ops.export_scene.gltf(
        filepath=str(output / f"{args.name}.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    final_faces = sum(len(obj.data.polygons) for obj in meshes)
    print(f"CYBERCITY_MESH_OK name={args.name} original_faces={original_faces} final_faces={final_faces}")


if __name__ == "__main__":
    main()

