# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all files (pure Python, binaries, data) for PyNaCl and its cffi backend
nacl_datas,     nacl_binaries,     nacl_hiddenimports     = collect_all('nacl')
cffi_datas,     cffi_binaries,     cffi_hiddenimports     = collect_all('cffi')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=nacl_binaries + cffi_binaries,
    datas=nacl_datas + cffi_datas + [
        ('assets/plink.exe', 'assets'),
        ('assets/vncviewer.exe', 'assets'),
        ('assets/LICENSE_TIGERVNC.txt', 'assets'),
        ('assets/machineportal.ico', 'assets'),
    ],
    hiddenimports=nacl_hiddenimports + cffi_hiddenimports,
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
