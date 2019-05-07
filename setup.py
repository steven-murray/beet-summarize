#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import re

from setuptools import setup, find_packages


def find_version():
    with open(os.path.join(os.path.dirname(__file__), "summarize", "__init__.py")) as fp:
        version_file = fp.read()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
]

setup_requirements = [
]

test_requirements = ['pytest', ]

setup(
    author="Steven Murray",
    author_email='steven.g.murray@asu.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Scientists',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Summarize your beets library",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    name='summarize',
    packages=find_packages(include=['summarize']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/steven-murray/beet-summarize',
    version=find_version(),
    zip_safe=False,
)
