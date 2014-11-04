"""
Setup for STAC harness and tools.

Most of this currently lives in educe, but the STAC
harness seems fairly STAC-specific
"""

from setuptools import setup, find_packages

setup(
    name="stac",
    version="2014.08.11",
    author="Philippe Muller, Stergos Afantenos, Pascal Denis, Eric Kow",
    author_email="eric@erickow.com",
    packages=find_packages(exclude=['guapi', 'guapi.*']),
    scripts=["cleanup/sanity-check", "irit-stac"],
    install_requires=["educe", "attelo", "sh", "pyzmq"]
)
