"""Exercise genuine shared actions on two existing authored Rocketbox bodies."""
import hashlib
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector


def bounds(rig, meshes):
    graph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    assert all(math.isfinite(v) for p in points for v in p)
    extent = high - low
    assert .2 < extent.z < 3.0 and max(extent) < 4.0, list(extent)
    return {"extent": list(extent), "vertex_sha256": hashlib.sha256(
        repr([tuple(round(v, 6) for v in p) for p in points]).encode()).hexdigest()}


def main():
    lab = Path("E:/CyberCity2085-3d-lab")
    pair = json.loads((lab / "generated/phase2/modularity166/rig_pair.json").read_text())
    assert pair["common_bones"] == 80 and not pair["parent_mismatches"]
    assert pair["max_rest_matrix_delta"] < .001
    bpy.ops.wm.read_factory_settings(use_empty=True)
    actors = []
    for item in pair["sources"]:
        source = Path(item["source"])
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["source_sha256"]
        previous = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=str(source), use_anim=False)
        imported = set(bpy.context.scene.objects) - previous
        rig = next(obj for obj in imported if obj.type == "ARMATURE")
        meshes = [obj for obj in imported if obj.type == "MESH"]
        actors.append((rig, meshes))
    library = lab / "generated/phase2/rocketbox_military03/motion01/human_motion.blend"
    with bpy.data.libraries.load(str(library), link=False) as (source, target):
        target.actions = [name for name in source.actions if name.startswith("Rocketbox_")]
    actions = target.actions
    assert len(actions) == 5, [a.name for a in actions]
    for action in actions:
        action.use_fake_user = True
    report = {"action_library": str(library), "action_library_sha256": hashlib.sha256(library.read_bytes()).hexdigest(),
              "samples": {}, "scope": "Actual shared action datablocks and bounded deformed meshes; no wardrobe or artistic acceptance"}
    for action in actions:
        samples = []
        for rig, _ in actors:
            rig.animation_data_create()
            rig.animation_data.action = action
            if action.slots:
                rig.animation_data.action_slot = action.slots[0]
        first, last = action.frame_range
        for frame in (first, (first + last) / 2, last):
            bpy.context.scene.frame_set(int(frame), subframe=frame-int(frame))
            bpy.context.view_layer.update()
            samples.append([bounds(rig, meshes) for rig, meshes in actors])
        report["samples"][action.name] = samples
    for index in (0, 1):
        hashes = {sample[index]["vertex_sha256"] for samples in report["samples"].values() for sample in samples}
        assert len(hashes) > 5, "Actions did not deform this body"
    for index, (rig, _) in enumerate(actors):
        for obj in bpy.context.scene.objects:
            if obj.parent == rig or obj == rig:
                obj.select_set(True)
        rig.location.x += index * 2.0
    output = lab / "generated/phase2/modularity166"
    report["status"] = "PASS"
    (output / "shared_actions.json").write_text(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "shared_actions.blend"))
    print("TWO_BODY_SHARED_ACTIONS_PASS", len(actions), "clips x 3 samples x 2 bodies")


if __name__ == "__main__":
    main()
