#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2017  Daniel Strigl

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

""" Unit tests for code in htheatpump.utils. """

import unittest
from htheatpump.utils import Singleton


# A simple Singleton class with one `int` member
class MySingleton(Singleton):

    val = -1

    def __init__(self, v):
        self.val = v


class HtSingletonTest(unittest.TestCase):
    """ This is the unittest for the ``htheatpump.utils`` code.
    """

    def setUp(self):
        """ Initializes the test environment. """
        pass

    def tearDown(self):
        """ Cleans up the test environment. """
        pass

    def test_SingletonClass(self):
        s1 = MySingleton(1)
        self.assertEqual(s1.val, 1)
        s2 = MySingleton(2)
        self.assertEqual(s2.val, 2)
        self.assertEqual(s1.val, 2)


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    unittest.main()
