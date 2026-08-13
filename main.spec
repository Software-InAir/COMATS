# -*- mode: python ; coding: utf-8 -*-


from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).resolve()

print(f"BUILDING FROM SPEC: {PROJECT_ROOT}")
print(f"IMAGES EXISTS: {(PROJECT_ROOT / 'Images').exists()}")

PROJECT_ROOT = Path(SPECPATH).resolve()

data_folders = [
    "Automation",
    "COMATS-migration",
    "COMATSeasteregg",
    "Fonts",
    "Images",
    "Output",
    "Python",
    "Resources",
    "Themes",
    "Unity",
]

datas = [
    (str(PROJECT_ROOT / folder), folder)
    for folder in data_folders
]

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="main",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="main",
)