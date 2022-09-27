from setuptools import setup, find_packages
from cbviewer import __version__

setup(
    name = 'cbviewer',
    description = 'library for 3D volumetric data visualization',
    version = __version__,
    packages = find_packages(),
)
