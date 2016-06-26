# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sortgtxt",
    version='0.0.6',
    description="Module for sorting Gettext files",
    url='https://github.com/ArchieT/sortgtxt',
    author="Michał Krzysztof Feiler",
    author_email="archiet@platinum.edu.pl",
    classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(),
    install_requires=["babel"],
)
