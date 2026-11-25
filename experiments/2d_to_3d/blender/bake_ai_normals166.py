"""Bake actual high-poly geometry to a UV normal map; no invented albedo/PBR."""
import hashlib
import json
from pathlib import Path
import struct
import bpy


def geometry_hash(mesh):
    data = bytearray()
    for vertex in mesh.vertices:
        data.extend(struct.pack("<3f", *vertex.co))
    for face in mesh.polygons:
        data.extend(struct.pack("<I", len(face.vertices)))
        data.extend(struct.pack("<%dI" % len(face.vertices), *face.vertices))
    return hashlib.sha256(data).hexdigest()


def main():
    folder = Path("E:/CyberCity2085-3d-lab/generated/phase2/triposg166/rook_combat")
    source = folder / "review_upright/model.blend"
    output = folder / "normal_bake166"
    output.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert len(meshes) == 1
    high = meshes[0]
    high_signature = geometry_hash(high.data)
    low = high.copy()
    low.data = high.data.copy()
    bpy.context.collection.objects.link(low)
    low.name = "UV_Runtime_Mesh"
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        obj.select_set(obj == low)
    bpy.context.view_layer.objects.active = low
    modifier = low.modifiers.new("RealtimeReduction", "DECIMATE")
    modifier.ratio = min(1, 40000 / len(high.data.polygons))
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    before = geometry_hash(low.data)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.1519173, island_margin=.005)
    bpy.ops.object.mode_set(mode="OBJECT")
    image = bpy.data.images.new("GeometryNormal1024", width=1024, height=1024, alpha=False)
    image.colorspace_settings.name = "Non-Color"
    material = bpy.data.materials.new("GeometryNormalDiagnostic")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (.45, .45, .45, 1)
    shader.inputs["Roughness"].default_value = .8
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    material.node_tree.nodes.active = texture
    low.data.materials.clear()
    low.data.materials.append(material)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.bake.margin = 12
    high.hide_render = False
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    bpy.ops.object.bake(type="NORMAL", use_selected_to_active=True, cage_extrusion=.005, max_ray_distance=.03)
    image.filepath_raw = str(output / "normal.png")
    image.file_format = "PNG"
    image.save()
    normal = material.node_tree.nodes.new("ShaderNodeNormalMap")
    material.node_tree.links.new(texture.outputs["Color"], normal.inputs["Color"])
    material.node_tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    assert geometry_hash(low.data) == before and geometry_hash(high.data) == high_signature
    high.hide_render = True
    high.hide_viewport = True
    for obj in scene.objects:
        obj.select_set(obj == low)
    glb = output / "mesh.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), use_selection=True, export_format="GLB",
                              export_animations=False, export_tangents=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "model.blend"))
    report = {"status": "PASS", "source_blend_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "high_geometry_sha256": high_signature, "low_geometry_sha256": before,
              "low_triangles": sum(len(p.vertices)-2 for p in low.data.polygons),
              "normal_png_sha256": hashlib.sha256((output / "normal.png").read_bytes()).hexdigest(),
              "glb_sha256": hashlib.sha256(glb.read_bytes()).hexdigest(),
              "scope": "Real geometry-derived tangent normals, UV and unchanged mesh. Constant neutral base colour/roughness; not generated albedo or measured PBR"}
    (output / "bake.json").write_text(json.dumps(report, indent=2))
    print("AI_GEOMETRY_NORMAL_BAKE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
