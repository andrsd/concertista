from setuptools import setup
from concertista import consts
from glob import glob
import platform
import os

main_script = 'concertista/__main__.py'
assets_dir = 'concertista/assets'

if platform.system() == 'Darwin':
    PLIST_INFO = {
        'CFBundleName': consts.APP_NAME,
        'CFBundleDisplayName': consts.APP_NAME,
        'CFBundleGetInfoString': consts.DESCRIPTION,
        'CFBundleIdentifier': "name.andrs.osx.concertista",
        'CFBundleVersion': str(consts.VERSION),
        'CFBundleShortVersionString': str(consts.VERSION),
        'NSHumanReadableCopyright': consts.COPYRIGHT
    }

    def generate_music_files(location):
        data_files = []
        for path, dirs, files in os.walk(os.path.join(location, 'music')):
            install_dir = os.path.relpath(path, location)
            ymls = [os.path.join(path, f) for f in files if f.endswith('.yml')]
            data_files.append((install_dir, ymls))

        return data_files

    extra_options = dict(
        setup_requires=['py2app'],
        app=[main_script],
        data_files=[
            ('icons', glob(assets_dir + '/icons/*.svg')),
            ('icons', glob(assets_dir + '/icons/*.png')),
            ('', ['concertista/.env'])
        ] + generate_music_files(assets_dir),
        options={
            'py2app': {
                'argv_emulation': False,
                'plist': PLIST_INFO,
            }
        }
    )
elif platform.system() == 'win32':
    extra_options = dict(
     setup_requires=['py2exe'],
     app=[main_script],
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install" and install
        # the main script as such
        scripts=[main_script]
    )

setup(
    name='Concertista',
    version=consts.VERSION,
    author='David Andrš',
    author_email='andrsd@gmail.com',
    url='https://github.com/andrsd/concertista',
    license='LICENSE',
    description=consts.DESCRIPTION,
    install_requires=[
        'PyQt5==5.13.1',
        'pyaml==20.4.0',
        'spotipy==2.22.1',
        'Flask==2.0.1',
        'waitress==2.1.2',
        'python-dotenv>=0.15.0'
    ],
    packages=[
        'concertista',
        'concertista.assets',
    ],
    entry_points={
        'gui_scripts': [
            'concertista = concertista.__main__:main'
        ]
    },
    include_package_data=True,
    package_data={
        'concertista.assets': ['*.yml', '*.svg']
    },
    **extra_options
)
