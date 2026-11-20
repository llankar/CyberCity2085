from pathlib import Path
import os
from tools.packaging_helpers import (
    build_identity_data,
    godot_executable_data,
    godot_runtime_data,
    normalize_arcade_data,
)

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
    hiddenimports=["tools.check_unified_return", "tools.check_campaign_return"] if include_qa else [],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tests"],
    noarchive=False,
)
a.datas = normalize_arcade_data(a.datas)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CyberCity2085",
    console=include_qa,
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
