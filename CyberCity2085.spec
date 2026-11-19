from pathlib import Path
from tools.packaging_helpers import godot_runtime_data, godot_executable_data, build_identity_data

root = Path(SPECPATH)

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / "assets"), "assets"),
        (str(root / "scenes"), "scenes"),
        *godot_runtime_data(root / "godot"),
        *godot_executable_data(),
        *build_identity_data(root),
    ],
    hiddenimports=[],
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
