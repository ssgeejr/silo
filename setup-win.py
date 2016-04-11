#!/usr/bin/env python

# from distutils.core import setup
# removed for installation purposes
# install_requires = ['python>=2.6.0','MySQL-python'],

from setuptools import setup

version_file = open('src/silo/__version__.py', 'r')
tmp_version = version_file.read()
version_file.close()
values = tmp_version.split("\"")
build_version =  values[1]

setup(
    name="silo",
    entry_points={
        'console_scripts': [
        'silo = silo:main',
        ],
    },
    version=build_version,
    packages=['silo'],
    package_dir={'silo': 'src/silo'},
    url="https://github.com/ssgeejr/silo",
    description="Utility to fetch the latest builds from Artifactory before building a Docker container",
    author="Steve S Gee Jr",
    author_email="ioexcept@gmail.com",
    license = "Apache License, Version 2.0",
    keywords = "docker artifactory silo",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    install_requires = [],

)
