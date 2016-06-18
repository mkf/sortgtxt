from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sortgtxt",
    version='0.0.1',
    description="Module for sorting Gettext files",
    url='https://github.com/ArchieT/sortgtxt',
    author="Michał Krzysztof Feiler",
    author_email="archiet@platinum.edu.pl",
    packages=find_packages(),
    install_requires=["babel", "re"],
)
