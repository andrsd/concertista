from setuptools import setup
from concertista import consts
from glob import glob
import os
import platform

PLIST_INFO = {
    'CFBundleName': consts.APP_NAME,
    'CFBundleDisplayName': consts.APP_NAME,
    'CFBundleGetInfoString': consts.DESCRIPTION,
    'CFBundleIdentifier': "name.andrs.osx.concertista",
    'CFBundleVersion': str(consts.VERSION),
    'CFBundleShortVersionString': str(consts.VERSION),
    'NSHumanReadableCopyright': consts.COPYRIGHT
}

main_script = 'concertista/__main__.py'
assets_dir = 'concertista/assets'

if platform.system() == 'Darwin':
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
            ('icons', glob(assets_dir + '/icons/*.svg'))
        ] + generate_music_files(assets_dir),
        options={
            'py2app': {
                'argv_emulation': True,
                'plist': PLIST_INFO
            }
        }
    )
elif platform.system() == 'win32':
    # TOOD
    pass
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install" and install
        # the main script as such
        scripts=[main_script]
    )

setup(
    name='Concertista',
    version='1.0',
    author='David Andrš',
    author_email='andrsd@gmail.com',
    url='https://github.com/andrsd/concertista',
    license='LICENSE',
    description=consts.DESCRIPTION,
    install_requires=[
        'PyQt5==5.15.2',
        'pyaml==20.4.0',
        'spotipy==2.16.1',
        'Flask==2.0.1',
        'waitress==1.4.4',
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
