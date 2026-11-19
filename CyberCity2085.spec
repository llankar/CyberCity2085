from pathlib import Path
import os
from tools.packaging_helpers import godot_runtime_data, godot_executable_data, build_identity_data

root = Path(SPECPATH)
include_qa = os.environ.get("CYBERCITY_PACKAGE_QA") == "1"

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / "assets"), "assets"),
        (str(root / "scenes"), "scenes"),
        *godot_runtime_data(root / "godot", include_qa=include_qa),
        *godot_executable_data(),
        *build_identity_data(root),
    ],
    hiddenimports=["tools.check_unified_return"] if include_qa else [],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CyberCity2085",
    console=False,
    contents_directory=".",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="CyberCity2085",
)
