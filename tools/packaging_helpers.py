"""Build-time data selection; exclude editor caches and live combat handoffs."""
import os
from pathlib import Path


def godot_executable_data():
    configured = os.environ.get("CYBERCITY_PACKAGE_GODOT")
    if not configured:
        if os.name == "nt":
            raise ValueError("Set CYBERCITY_PACKAGE_GODOT to the Windows Godot executable.")
        return []
    executable = Path(configured).resolve()
    if not executable.is_file() or executable.suffix.lower() != ".exe" or executable.stem.lower().endswith("_console"):
        raise ValueError("CYBERCITY_PACKAGE_GODOT must point to the standalone Windows Godot executable.")
    return [(str(executable), "bin/godot")]


def godot_runtime_data(directory, *, include_qa=False):
    excluded = {"runtime", ".godot", "__pycache__", "work"}
    if not include_qa:
        excluded.add("tests")
    return [
        (str(path), str(path.parent.relative_to(directory.parent)))
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and not excluded.intersection(path.relative_to(directory).parts)
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
