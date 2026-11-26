"""Neutral four-angle inspection of a new GLB, retaining source materials."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target-triangles", type=int, default=20000)
    parser.add_argument("--source-z-up", action="store_true")
    parser.add_argument("--normal-ab", action="store_true")
    parser.add_argument("--no-renders", action="store_true", help="Production batch: optimize/export now, review assembled maps later")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    if source.drive.upper() != "E:" or output.drive.upper() != "E:":
        raise ValueError("Experimental assets must stay on E:")
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    if args.source_z_up:
        # Trimesh's unrotated TRELLIS export puts Z-up coordinates in a Y-up GLB.
        orientation = bpy.data.objects.new("SourceZUpCorrection", None)
        bpy.context.collection.objects.link(orientation)
        for obj in list(bpy.context.scene.objects):
            if obj != orientation and obj.parent is None:
                obj.parent = orientation
        orientation.rotation_euler.x = -math.pi / 2
        bpy.context.view_layer.update()
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("No mesh imported")
    points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center = (low + high) / 2
    extent = max(high - low)
    if extent <= 0:
        raise RuntimeError("Degenerate model bounds")
    # World-space parent transform preserves all existing mesh/material data.
    root = bpy.data.objects.new("ReviewNormalization", None)
    bpy.context.collection.objects.link(root)
    for obj in list(bpy.context.scene.objects):
        if obj != root and obj.parent is None:
            obj.parent = root
    root.scale = (1 / extent,) * 3
    root.location = -center / extent
    world = bpy.data.worlds.new("NeutralWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.15, .15, .15, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .5
    bpy.context.scene.world = world
    for position, power in (((-3, -4, 4), 350), ((3, 2, 3), 250)):
        bpy.ops.object.light_add(type="AREA", location=position)
        light = bpy.context.object
        light.data.energy = power
        light.data.shape = "DISK"
        light.data.size = 5
        light.rotation_euler = (-light.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.4
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    report = {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "source_z_up_correction": args.source_z_up,
              "mesh_objects": len(meshes), "triangles": sum(
                  sum(len(face.vertices) - 2 for face in obj.data.polygons) for obj in meshes),
              "original_extent": list(high - low), "renders": {}, "artistic_acceptance": "NOT VERIFIED"}
    views={} if args.no_renders else {"front": (0, -3, 0), "profile": (3, 0, 0),
                           "back": (0, 3, 0), "isometric": (2, -3, 2)}
    for name, position in views.items():
        camera.location = position
        camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
        path = output / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        report["renders"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if args.normal_ab and not args.no_renders:
        nodes = [node for mat in bpy.data.materials if mat.use_nodes
                 for node in mat.node_tree.nodes if node.type == "NORMAL_MAP"]
        if not nodes:
            raise RuntimeError("Normal-map A/B requires an imported normal map")
        strengths = [node.inputs["Strength"].default_value for node in nodes]
        for node in nodes:
            node.inputs["Strength"].default_value = 0
        path = output / "isometric_normal_disabled.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        report["renders"]["isometric_normal_disabled"] = hashlib.sha256(path.read_bytes()).hexdigest()
        for node, strength in zip(nodes, strengths):
            node.inputs["Strength"].default_value = strength
        report["normal_ab"] = "Identical geometry, material and lighting; only normal strength disabled"
    if not args.no_renders:bpy.ops.wm.save_as_mainfile(filepath=str(output / "model.blend"))
    ratio = min(1.0, args.target_triangles / report["triangles"])
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new("RealtimeReduction", "DECIMATE")
        modifier.ratio = ratio
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    for obj in scene.objects:
        obj.select_set(obj in meshes or obj == root)
    optimized = output / "optimized.glb"
    bpy.ops.export_scene.gltf(filepath=str(optimized), export_format="GLB", use_selection=True)
    report["optimized_triangles"] = sum(
        sum(len(face.vertices) - 2 for face in obj.data.polygons) for obj in meshes)
    report["optimized_glb_sha256"] = hashlib.sha256(optimized.read_bytes()).hexdigest()
    scene.render.filepath = str(output / "optimized_isometric.png")
    if not args.no_renders:bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "optimized.blend"))
    (output / "review.json").write_text(json.dumps(report, indent=2))
    print("AI_MESH_BATCH_EXPORTED" if args.no_renders else "AI_NEUTRAL_REVIEW_RENDERED", json.dumps(report))


if __name__ == "__main__":
    main()
