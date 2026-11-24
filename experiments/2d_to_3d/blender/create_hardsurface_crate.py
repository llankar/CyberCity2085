"""Build a clean, game-ready cyberpunk cargo crate from Blender primitives."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def make_material(name: str, color: tuple[float, float, float, float], metallic: float, roughness: float, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        shader.inputs["Emission Color"].default_value = color
        shader.inputs["Emission Strength"].default_value = emission
    return mat


def box(name: str, location, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("EdgeBevel", "BEVEL")
    modifier.width = bevel
    modifier.segments = 2
    obj.data.materials.append(mat)
    return obj


def main() -> None:
    args = arguments()
    output = Path(args.output_dir).resolve()
    if output.drive.upper() != "E:":
        raise ValueError("Experimental generated assets must be written to E:")
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    dark = make_material("Gunmetal", (0.025, 0.045, 0.06, 1), 0.85, 0.28)
    panel = make_material("ArmoredPanel", (0.08, 0.15, 0.17, 1), 0.65, 0.34)
    trim = make_material("SafetyTrim", (0.85, 0.32, 0.025, 1), 0.55, 0.3)
    glow = make_material("AccessGlow", (0.0, 0.75, 1.0, 1), 0.2, 0.22, 5.0)

    parts = [box("CargoCore", (0, 0, 0.62), (0.76, 0.54, 0.56), dark, 0.055)]
    for y in (-0.555, 0.555):
        parts.append(box("FrontPanel", (0, y, 0.64), (0.61, 0.035, 0.40), panel, 0.018))
        for x in (-0.68, 0.68):
            parts.append(box("CornerRail", (x, y * 0.96, 0.62), (0.055, 0.06, 0.51), trim, 0.012))
        parts.append(box("AccessStrip", (0, y * 1.025, 0.66), (0.28, 0.018, 0.035), glow, 0.008))
    for x in (-0.72, 0.72):
        for z in (0.16, 1.08):
            parts.append(box("FrameBrace", (x, 0, z), (0.055, 0.50, 0.055), trim, 0.012))
    for x in (-0.60, 0.60):
        for y in (-0.40, 0.40):
            parts.append(box("Foot", (x, y, 0.055), (0.12, 0.12, 0.055), dark, 0.018))
    parts.append(box("TopPlate", (0, 0, 1.19), (0.62, 0.43, 0.045), panel, 0.025))
    parts.append(box("Lock", (0, -0.595, 0.66), (0.12, 0.035, 0.13), dark, 0.018))
    parts.append(box("LockLight", (0, -0.635, 0.70), (0.055, 0.012, 0.025), glow, 0.006))

    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "PreviewFloor"
    floor.data.materials.append(make_material("PreviewFloorMaterial", (0.005, 0.012, 0.02, 1), 0.2, 0.5))
    for location, energy, color in (((2.5, -3, 3.5), 850, (0.1, 0.8, 1)), ((-2, -1, 2), 650, (1, 0.18, 0.04))):
        bpy.ops.object.light_add(type="AREA", location=location)
        bpy.context.object.data.energy = energy
        bpy.context.object.data.color = color
        bpy.context.object.data.size = 3
    bpy.ops.object.camera_add(location=(2.4, -3.2, 2.1))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, 0.6)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 58
    bpy.context.scene.camera = camera
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output / "crate_procedural_preview.png")
    scene.world = bpy.data.worlds.new("PreviewWorld")
    scene.world.color = (0.003, 0.006, 0.012)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "crate_procedural.blend"))
    bpy.ops.render.render(write_still=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=str(output / "crate_procedural.glb"), export_format="GLB", use_selection=True, export_apply=True)
    faces = sum(len(obj.data.polygons) for obj in parts)
    print(f"CYBERCITY_HARDSURFACE_OK name=crate parts={len(parts)} faces={faces}")


if __name__ == "__main__":
    main()
