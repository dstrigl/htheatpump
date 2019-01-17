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

""" Some useful helper classes and methods. """


class Singleton:
    """ Singleton base class.

    Example:

    >>> class MySingleton(Singleton):
    ...     def __init__(self, v):
    ...         self._val = v
    ...     def __str__(self):
    ...         return str(self._val)

    >>> s1 = MySingleton(1)
    >>> print(str(s1))
    1
    >>> s2 = MySingleton(2)
    >>> print(str(s2))
    2
    >>> print(str(s1))
    2

    .. seealso::
        https://mail.python.org/pipermail/python-list/2007-July/431423.html
    """
    def __new__(cls, *args, **kwargs):
        """ Create a new instance.
        """
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst


#if __name__ == "__main__":
#    import doctest
#    doctest.testmod()


# --------------------------------------------------------------------------------------------- #
# Exported symbols
# --------------------------------------------------------------------------------------------- #

__all__ = ["Singleton"]
