# -*- mode: python ; coding: utf-8 -*-
# PyInstaller SPEC — Blox Fruits 2D v1.1.0
# 用法：pyinstaller release/bloxfruits.spec
# 輸出：release/dist/BloxFruits2D.exe（單一執行檔）

import os

ROOT        = os.path.abspath(os.path.join(os.path.dirname(SPEC), '..'))
RELEASE_DIR = os.path.abspath(os.path.dirname(SPEC))

a = Analysis(
    [os.path.join(ROOT, 'main.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # 包含所有 JSON 內容資料
        (os.path.join(ROOT, 'content'), 'content'),
    ],
    hiddenimports=[
        'numpy',
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.sndarray',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'scipy', 'PIL',
        'IPython', 'jupyter', 'notebook',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BloxFruits2D',
    # Output goes inside release/ so the project root stays clean
    distpath=os.path.join(RELEASE_DIR, 'dist'),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # 隱藏 cmd 視窗（GUI 模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'release', 'icon.ico'),   # 遊戲圖示
    version=os.path.join(ROOT, 'release', 'file_version_info.txt'),  # Windows 版本資訊
)
