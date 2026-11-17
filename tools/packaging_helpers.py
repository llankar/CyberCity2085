"""Build-time data selection; exclude editor caches and live combat handoffs."""


def godot_runtime_data(directory):
    return [
        (str(path), str(path.parent.relative_to(directory.parent)))
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and not {"runtime", ".godot", "__pycache__"}.intersection(
            path.relative_to(directory).parts
        )
        and path.suffix not in {".pyc", ".tmp", ".log"}
    ]


def build_identity_data(project_root, label=None):
    """Stamp the actual build identity into frozen distributions without Git."""
    import json
    from game.version import build_label

    path = project_root / "build" / "metadata" / "build_info.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"label": label or build_label()}), encoding="utf-8")
    return [(str(path), ".")]
