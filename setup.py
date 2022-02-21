from setuptools import setup
from proteotools import __version__ as version

setup(
    name='proteotools',
    version=version,
    packages=['proteotools'],
    url='https://github.com/kevinkovalchik/proteotools',
    license='MIT',
    author='Kevin Kovalchik',
    author_email='kevin.kovalchik@gmail.com',
    description='A simple Python package which lets you programmatically convert Thermo raw files using '
                'ThermoRawFileParser, run a few proteomics search engines (Comet, X! Tandem, MS-GF+), and use '
                'compiled Trans-Proteomic Pipeline (TPP) binaries without needing to '
                'compile the entire pipeline.',
    install_requires=['pyteomics.pepxmltk']
)
