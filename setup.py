#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" The setup script """

import io
import os
import re

from setuptools import find_packages, setup


def read(*parts):
    """ Read file. """
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()


def get_version():
    """ Get current version from code. """
    regex = r"__version__\s=\s\"(?P<version>[\d\.]+?)\""
    path = ("htheatpump", "__version__.py")
    return re.search(regex, read(*path)).group("version")


# Get the description from the README file
with open("README.rst") as readme_file:
    readme = readme_file.read()

# Get the history from the HISTORY file
with open("HISTORY.rst") as history_file:
    history = history_file.read()


def pip(filename):
    """ Parse pip reqs file and transform it to setuptools requirements. """
    requirements = []
    for line in io.open(os.path.join("requirements", "{0}.pip".format(filename))):
        line = line.strip()
        if not line or "://" in line or line.startswith("#"):
            continue
        requirements.append(line)
    return requirements


install_requires = pip("install")
doc_require = pip("doc")
tests_require = pip("test")
dev_require = tests_require + pip("develop")


setup(
    # Project name
    name="htheatpump",
    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_version(),
    # Project description
    description="Easy-to-use Python communication module for Heliotherm heat pumps",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    # Choosen license
    license="GNU General Public License v3",
    # The project's main homepage
    url="https://github.com/dstrigl/htheatpump",
    # Author details
    author="Daniel Strigl",
    # author_email="?",
    # Supported platforms
    platforms=["Linux"],
    # Project packages
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    # Project requirements (used by pip to install its dependencies)
    install_requires=install_requires,
    tests_require=tests_require,
    # dev_require=dev_require,  # UserWarning: Unknown distribution option: 'dev_require'
    extras_require={"test": tests_require, "doc": doc_require, "dev": dev_require},
    # Prevent zip archive creation
    zip_safe=False,
    # Keywords that describes the project
    keywords="python python3 heatpump serial protocol Heliotherm",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        # Language and Platform
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        # Additional topic classifier
        "Topic :: Communications",
        "Topic :: Home Automation",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Terminals :: Serial",
    ],
    # Entry points specification
    entry_points={
        "console_scripts": [
            #
            "htheatpump=htheatpump.__main__:main",
            #
            "htbackup=htheatpump.scripts.htbackup:main",
            "htbackup_async=htheatpump.scripts.htbackup_async:main",
            #
            "htcomplparams=htheatpump.scripts.htcomplparams:main",
            "htcomplparams_async=htheatpump.scripts.htcomplparams_async:main",
            #
            "htdatetime=htheatpump.scripts.htdatetime:main",
            "htdatetime_async=htheatpump.scripts.htdatetime_async:main",
            #
            "htfastquery=htheatpump.scripts.htfastquery:main",
            "htfastquery_async=htheatpump.scripts.htfastquery_async:main",
            #
            "htfaultlist=htheatpump.scripts.htfaultlist:main",
            "htfaultlist_async=htheatpump.scripts.htfaultlist_async:main",
            #
            "htquery=htheatpump.scripts.htquery:main",
            "htquery_async=htheatpump.scripts.htquery_async:main",
            #
            "htset=htheatpump.scripts.htset:main",
            "htset_async=htheatpump.scripts.htset_async:main",
            #
            "htshell=htheatpump.scripts.htshell:main",
            "htshell_async=htheatpump.scripts.htshell_async:main",
            #
            "httimeprog=htheatpump.scripts.httimeprog:main",
            "httimeprog_async=htheatpump.scripts.httimeprog_async:main",
            #
            "hthttp=htheatpump.scripts.hthttp:main",
        ],
    },
)
