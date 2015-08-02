#!/usr/bin/env python

# from distutils.core import setup
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
	install_requires = ['python >= 2.6.0'],
    author="Steve S Gee Jr.",
    author_email="ioexcept@gmail.com",
    license = "Apache License, Version 2.0",
    url="http://gee-5/repo/silo/browse",
    description="Utility to fetch the latest builds from Artifactory and/or additional files that are not available on the build server before building a Docker container",
    keywords = "docker artifactory",
)

