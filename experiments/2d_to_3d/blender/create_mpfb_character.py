"""Create a reproducible, rigged MPFB humanoid for the isolated 3D lab.

Run with Blender and MPFB enabled. Generated assets must target the external
experimental drive; this script deliberately refuses to write inside the repo.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", default="rook_mpfb")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def require_external_output(path: Path) -> None:
    if path.drive.upper() != "E:":
        raise ValueError("Experimental generated assets must be written to E:")


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.48
    shader.inputs["Metallic"].default_value = metallic
    result.diffuse_color = color
    return result


def add_preview_scene(height: float) -> None:
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "PreviewFloor"
    floor.data.materials.append(material("PreviewFloorMaterial", (0.008, 0.018, 0.03, 1.0), 0.15))
    for location, energy, color, size in (
        ((2.8, -3.5, height * 1.1), 950, (0.08, 0.75, 1.0), 3.0),
        ((-2.5, -0.5, height * 0.8), 800, (1.0, 0.2, 0.05), 2.5),
        ((0.0, 2.0, height * 1.2), 650, (0.35, 0.25, 1.0), 2.0),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.data.energy = energy
        lamp.data.color = color
        lamp.data.shape = "DISK"
        lamp.data.size = size
    bpy.ops.object.camera_add(location=(2.3, -4.4, height * 0.58))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0.0, 0.0, height * 0.52)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 62
    bpy.context.scene.camera = camera


def main() -> None:
    args = arguments()
    output = Path(args.output_dir).resolve()
    require_external_output(output)
    output.mkdir(parents=True, exist_ok=True)

    from bl_ext.blender_org.mpfb.services.humanservice import HumanService
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    phenotype = TargetService.get_default_macro_info_dict()
    phenotype.update({"gender": 0.82, "age": 0.43, "muscle": 0.72, "weight": 0.48, "height": 0.58})
    phenotype["race"] = {"asian": 0.08, "african": 0.08, "caucasian": 0.84}
    human = HumanService.create_human(
        mask_helpers=True,
        detailed_helpers=True,
        extra_vertex_groups=True,
        feet_on_ground=True,
        scale=0.1,
        macro_detail_dict=phenotype,
    )
    human.name = args.name
    human.data.name = f"{args.name}_mesh"
    human.data.materials.clear()
    human.data.materials.append(material("Rook_Skin_Prototype", (0.38, 0.16, 0.09, 1.0)))
    rig = HumanService.add_builtin_rig(human, "game_engine", import_weights=True)
    rig.name = f"{args.name}_rig"

    dimensions = human.dimensions
    height = max(1.0, dimensions.z)
    add_preview_scene(height)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output / f"{args.name}_preview.png")
    scene.world.color = (0.004, 0.008, 0.015)

    bpy.ops.wm.save_as_mainfile(filepath=str(output / f"{args.name}.blend"))
    bpy.ops.render.render(write_still=True)
    bpy.ops.object.select_all(action="DESELECT")
    human.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(
        filepath=str(output / f"{args.name}.glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_animations=True,
    )
    print(
        "CYBERCITY_MPFB_OK "
        f"name={args.name} vertices={len(human.data.vertices)} faces={len(human.data.polygons)} "
        f"bones={len(rig.data.bones)} height={height:.3f}"
    )


if __name__ == "__main__":
    main()
