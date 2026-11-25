"""Export the newly checked pair with genuine shared clips and source textures."""
import hashlib
import json
from pathlib import Path
import bpy


def main():
    lab = Path("E:/CyberCity2085-3d-lab")
    output = lab / "generated/phase2/modularity166"
    bpy.ops.wm.open_mainfile(filepath=str(output / "shared_actions.blend"), use_scripts=False)
    texture_files = list((lab / "sources/rocketbox/Male_Adult_08/Textures").rglob("*"))
    texture_files += list((lab / "sources/rocketbox/Military_Male_03/Textures").rglob("*"))
    repaired, missing = [], []
    for image in bpy.data.images:
        if image.source != "FILE":
            continue
        if Path(bpy.path.abspath(image.filepath)).is_file():
            continue
        name = Path(image.filepath.replace('\\', '/')).name.lower()
        candidates = [p for p in texture_files if p.is_file() and p.name.lower() == name]
        if len(candidates) == 1:
            image.filepath = str(candidates[0])
            image.reload()
            repaired.append(str(candidates[0]))
        else:
            missing.append(image.filepath)
    if missing:
        raise RuntimeError(f"Missing real source textures: {missing}")
    library = lab / "generated/phase2/rocketbox_military03/motion01/human_motion.blend"
    with bpy.data.libraries.load(str(library), link=False) as (source, target):
        target.actions = [name for name in source.actions if name.startswith("Rocketbox_") and name not in bpy.data.actions]
    actions = [a for a in bpy.data.actions if a.name.startswith("Rocketbox_")]
    rigs = sorted([obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"], key=lambda o:o.name)
    assert len(rigs) == 2 and len(actions) == 5
    exports = []
    for index, rig in enumerate(rigs):
        rig.location.x = 0
        rig.animation_data.action = None
        for track in list(rig.animation_data.nla_tracks):
            rig.animation_data.nla_tracks.remove(track)
        for action in actions:
            track = rig.animation_data.nla_tracks.new()
            track.name = action.name
            strip = track.strips.new(action.name, 0, action)
            if action.slots:
                strip.action_slot = action.slots[0]
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and
                  any(m.type == "ARMATURE" and m.object == rig for m in obj.modifiers)]
        assert meshes
        for obj in bpy.context.scene.objects:
            obj.select_set(obj == rig or obj in meshes)
        path = output / f"body_{index}.glb"
        bpy.ops.export_scene.gltf(filepath=str(path), use_selection=True,
                                  export_format="GLB", export_animation_mode="NLA_TRACKS")
        exports.append({"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bones": len(rig.data.bones), "clips": [a.name for a in actions]})
    report = {"exports": exports, "repaired_real_textures": repaired,
              "missing_textures": missing, "scope": "Authored source textures and shared actions; native import pending"}
    (output / "exports.json").write_text(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "export_sources.blend"))
    print("TWO_BODY_GLBS_EXPORTED", json.dumps(report))


if __name__ == "__main__":
    main()
