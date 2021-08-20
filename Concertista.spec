# -*- mode: python ; coding: utf-8 -*-

import os
from os.path import join
import sys
from concertista import consts

block_cipher = None


a = Analysis(
    [join('concertista', '__main__.py')],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
      (join('concertista', 'assets', 'icons'), 'icons'),
      (join('concertista', 'assets', 'music'), 'music')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Concertista',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Concertista')

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name=f'{consts.APP_NAME}.app',
        icon=None,
        bundle_identifier='name.andrs.osx.concertista',
        version=f'{consts.VERSION}',
        info_plist={
            'CFBundleGetInfoString': f'{consts.DESCRIPTION}',
            'NSHumanReadableCopyright': f'{consts.COPYRIGHT}'
        }
    )
