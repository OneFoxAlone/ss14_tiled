# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for building SS14 Tiled as a standalone EXE."""

block_cipher = None

a = Analysis(
    [r'ss14_tiled\gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[('ss14_tiled', 'ss14_tiled'), ('requirements.txt', '.')],
    hiddenimports=['PyQt6', 'cv2', 'yaml', 'deepdiff'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['matplotlib', 'numpy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SS14Tiled',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='toolbox.ico',
)
