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


def runtime_asset_data(directory: Path):
    entries = []
    for path in sorted(directory.iterdir()):
        if path.is_dir() and path.name == "combat_visual":
            entries.extend(
                (str(child), f"assets/combat_visual/{child.name}" if child.is_dir() else "assets/combat_visual")
                for child in sorted(path.iterdir())
                if child.name != "source_sheets"
            )
        else:
            entries.append((str(path), f"assets/{path.name}" if path.is_dir() else "assets"))
    return entries


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


def normalize_arcade_data(toc):
    """Correct the Arcade hook's directory destination for its VERSION file."""
    return [
        ("arcade/VERSION" if Path(destination.replace("\\", "/")).parts == ("arcade", "VERSION", "VERSION")
         else destination, source, kind)
        for destination, source, kind in toc
    ]


def build_identity_data(project_root, label=None, *, metadata_directory=None):
    """Stamp the actual build identity into frozen distributions without Git."""
    import json
    from game.version import build_label

    directory = metadata_directory if metadata_directory is not None else project_root / "build" / "metadata"
    path = directory / "build_info.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"label": label or build_label()}), encoding="utf-8")
    return [(str(path), ".")]
