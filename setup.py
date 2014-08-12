"""
Setup for STAC harness and tools.

Most of this currently lives in educe, but the STAC
harness seems fairly STAC-specific
"""

from setuptools import setup

setup(
    name="stac",
    version="2014.08.11",
    author="Philippe Muller, Stergos Afantenos, Pascal Denis, Eric Kow",
    author_email="eric@eric.kow.com",
    packages=["stac.harness"],
    scripts=["cleanup/sanity-check", "irit-stac"],
    requires=["educe", "attelo", "sh"]
)
