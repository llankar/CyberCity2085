"""Transfer one genuine authored helmet between the two compatible bodies."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Matrix


def main():
    lab = Path("E:/CyberCity2085-3d-lab")
    output = lab / "generated/phase2/modularity166"
    bpy.ops.wm.open_mainfile(filepath=str(output / "export_sources.blend"), use_scripts=False)
    rigs = sorted([o for o in bpy.context.scene.objects if o.type == "ARMATURE"], key=lambda o:o.name)
    target = rigs[0]
    original_meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and
                       any(m.type == "ARMATURE" and m.object == target for m in o.modifiers)]
    # Use the actual original donor rig already evaluated in this shared scene.
    # An unlinked imported armature had a stale world matrix and floated the prop.
    source_rig = rigs[1]
    bpy.context.view_layer.update()
    prop_file = lab / "generated/phase2/rocketbox_military03/accessories01/accessories.blend"
    with bpy.data.libraries.load(str(prop_file), link=False) as (available, loaded):
        loaded.objects = ["AuthoredProp_5028"]
    helmet = loaded.objects[0]
    if helmet is None:
        raise RuntimeError("Missing authored helmet component")
    bpy.context.collection.objects.link(helmet)
    bpy.context.view_layer.update()
    source_rest = source_rig.matrix_world @ source_rig.data.bones["Bip01 Head"].matrix_local
    target_rest = target.matrix_world @ target.data.bones["Bip01 Head"].matrix_local
    transform = target_rest @ source_rest.inverted() @ helmet.matrix_world
    for vertex in helmet.data.vertices:
        vertex.co = transform @ vertex.co
    helmet.matrix_world = Matrix.Identity(4)
    helmet.name = "HelmetModule166"
    for group in list(helmet.vertex_groups):
        helmet.vertex_groups.remove(group)
    group = helmet.vertex_groups.new(name="Bip01 Head")
    group.add(list(range(len(helmet.data.vertices))), 1.0, "REPLACE")
    modifier = helmet.modifiers.new("SharedSkeletonBinding", "ARMATURE")
    modifier.object = target
    rest = [v.co.copy() for v in helmet.data.vertices]
    from mathutils import Vector
    rest_center = sum(rest, Vector()) / len(rest)
    rest_anchor_distance = (rest_center - target_rest.translation).length
    assert rest_anchor_distance < .35, (rest_center[:], target_rest.translation[:])
    actions = [a for a in bpy.data.actions if a.name.startswith("Rocketbox_")]
    assert len(actions) == 5
    for track in target.animation_data.nla_tracks:
        track.mute = True
    errors = []
    for action in actions:
        target.animation_data.action = action
        if action.slots:
            target.animation_data.action_slot = action.slots[0]
        first, last = action.frame_range
        for frame in (first, (first+last)/2, last):
            bpy.context.scene.frame_set(int(frame), subframe=frame-int(frame))
            bpy.context.view_layer.update()
            expected = target.matrix_world @ target.pose.bones["Bip01 Head"].matrix @ target_rest.inverted()
            evaluated = helmet.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh = evaluated.to_mesh()
            error = max(((evaluated.matrix_world @ v.co) - expected @ p).length
                        for v, p in zip(mesh.vertices, rest))
            evaluated.to_mesh_clear()
            assert error < .00001, error
            errors.append(error)
    target.animation_data.action = None
    for track in target.animation_data.nla_tracks:
        track.mute = False
    for obj in bpy.context.scene.objects:
        obj.select_set(obj == target or obj == helmet or obj in original_meshes)
    path = output / "body_0_helmet_restfixed.glb"
    bpy.ops.export_scene.gltf(filepath=str(path), use_selection=True,
                              export_format="GLB", export_animation_mode="NLA_TRACKS")
    report = {"status": "PASS", "authored_component": "AuthoredProp_5028",
              "source": str(prop_file), "source_sha256": hashlib.sha256(prop_file.read_bytes()).hexdigest(),
              "vertices": len(rest), "sampled_poses": len(errors), "max_binding_error_m": max(errors),
              "rest_anchor_distance_m": rest_anchor_distance,
              "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "scope": "One real helmet transferred, bound and animated. Fit/intersections and interchangeable clothing unverified"}
    (output / "helmet_transfer_restfixed.json").write_text(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "helmet_transfer_restfixed.blend"))
    print("AUTHORED_HELMET_TRANSFER_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
