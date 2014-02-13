from setuptools import setup, find_packages
setup(
      name     = "stac",
      version  = "2014.02.06",
      author   = "Philippe Muller, Stergos Afantenos, Pascal Denis",
      author_email = "Philippe.Muller@irit.fr",
      packages = [ "stac", "stac.lexicon" ],
      scripts  = [ "cleanup/sanity-check", "stac-util" ]
);
