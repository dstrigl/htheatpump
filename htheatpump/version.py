#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2019  Daniel Strigl

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Version information handling of the :mod:`htheatpump` module.

    You should only have to change the version tuple :const:`version` at the end of this file,
    e.g.::

        version = Version("htheatpump", 1, 2, 3)  # version format <major>.<minor>.<patch>

    Given a version number ``MAJOR.MINOR.PATCH``, increment the:

        * ``MAJOR`` version when making incompatible API changes,
        * ``MINOR`` version when adding functionality in a backwards-compatible manner, and
        * ``PATCH`` version when making backwards-compatible bug fixes.
"""


class Version:
    """ Object which encapsulates the version information.

    :param package: Name of the package.
    :type package: str
    :param major: The major version number.
    :type major: int
    :param minor: The minor version number.
    :type minor: int
    :param patch: The patch version number.
    :type patch: int
    """

    def __init__(self, package: str, major: int, minor: int, patch: int) -> None:
        self.package = package
        self.major = major
        self.minor = minor
        self.patch = patch

    def short(self) -> str:
        """" Return a string in canonical short version format ``<major>.<minor>.<patch>``.

        :returns: A string in canonical short version format.
        :rtype: ``str``
        """
        return "{:d}.{:d}.{:d}".format(self.major, self.minor, self.patch)

    def __str__(self) -> str:
        """ Returns a string representation of the object.

        :returns: A string representation of this object.
        :rtype: ``str``
        """
        return "[{}, version {}]".format(self.package, self.short())


version = Version("htheatpump", 1, 2, 0)
""" Version definition of the :mod:`htheatpump` module. """
# version.__name__ = "htheatpump"


# ------------------------------------------------------------------------------------------------------------------- #
# Main program
# ------------------------------------------------------------------------------------------------------------------- #

# Only for testing: print the version
#def main():
#    print(version)
#
#
#if __name__ == "__main__":
#    main()


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["version"]
