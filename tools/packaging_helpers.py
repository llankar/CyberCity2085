"""Build-time data selection; exclude editor caches and live combat handoffs."""


def godot_runtime_data(directory):
    return [(str(path), str(path.parent.relative_to(directory.parent)))
            for path in sorted(directory.rglob("*")) if path.is_file()
            and not {"runtime", ".godot", "__pycache__"}.intersection(path.relative_to(directory).parts)
            and path.suffix not in {".pyc", ".tmp", ".log"}]
