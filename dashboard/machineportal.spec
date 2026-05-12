# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/plink.exe', 'assets'),
        ('assets/vncviewer.exe', 'assets'),
        ('assets/LICENSE_TIGERVNC.txt', 'assets'),
        ('assets/machineportal.ico', 'assets'),
    ],
    hiddenimports=["nacl", "nacl.signing", "nacl.exceptions", "nacl.bindings"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pygame'],
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
    name='MachinePortal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,   # UPX rewrites PE sections after icon embedding and drops the icon
    upx_exclude=[],
    runtime_tmpdir=None,
    icon='assets/machineportal.ico',
    console=False,   # windowless — no command prompt
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
