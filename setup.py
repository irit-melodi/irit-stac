"""
Setup for STAC harness and tools.

Most of this currently lives in educe, but the STAC
harness seems fairly STAC-specific
"""

from setuptools import setup, find_packages

setup(
    name="irit-stac",
    version="2015.3.24",
    author="IRIT Melodi team",
    author_email="eric@erickow.com",
    packages=find_packages(exclude=['guapi', 'guapi.*']),
    scripts=["irit-stac"],
    install_requires=["educe",
                      "attelo",
                      "enum34",
                      "pyzmq",
                      "six"]
)
