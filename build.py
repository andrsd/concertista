"""
Build release files
"""

from distutils.sysconfig import get_python_lib
import os.path
import shutil
import sys

import PyInstaller.__main__

from concertista import consts


def datapath(src, dest):
    return os.path.join(*src) + os.pathsep + os.path.join(*dest)


appname = f'{consts.APP_NAME}'
pyqt_dir = os.path.join(get_python_lib(), 'PyQt5', 'Qt')

if sys.platform.startswith('win'):
    libdir = 'bin'
    # icon = 'logo.ico'
else:
    libdir = 'lib'
    # icon = 'logo.icns'  # For OSX; param gets ignored on Linux

PyInstaller.__main__.run([
    '--noconfirm',
    '--onedir',
    '--windowed',
    '--name', appname,
    # '--icon', os.path.join('concertista', 'assets', icon),
    '--add-data', datapath(
        [pyqt_dir, 'plugins', 'platforms'], ['platforms']),
    '--add-data', datapath(
        [pyqt_dir, 'plugins', 'imageformats'], ['imageformats']),
    '--add-data', datapath([pyqt_dir, libdir], ['.']),
    '--add-data', datapath(
        ['concertista', 'assets'], ['assets']),
    'concertista/__main__.py'
])

outfilename = os.path.join(
    'dist',
    f'{appname}-{consts.VERSION}-{sys.platform}')

if sys.platform.startswith('darwin'):
    print(f'Creating archive: {outfilename}.tar.gz')
    shutil.make_archive(
        outfilename,
        'gztar',
        root_dir='dist',
        base_dir=appname + '.app')
else:
    print(f'Creating archive: {outfilename}.zip')
    shutil.make_archive(
        outfilename,
        'zip',
        root_dir='dist',
        base_dir=appname)
print('Done')
