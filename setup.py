from setuptools import setup

setup(
    name='Concertista',
    version='1.0',
    author='David Andrš',
    author_email='andrsd@gmail.com',
    url='https://github.com/andrsd/concertista',
    license='LICENSE',
    description='Little app to fill your spotify queue with concert music',
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
)
