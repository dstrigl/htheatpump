#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (c) 2017 Daniel Strigl. All Rights Reserved.

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

""" Unit tests for code in htheatpump.version. """

import os, sys
sys.path.insert(0, os.path.abspath('..'))

import unittest
from htheatpump.version import Version


class HtVersionTest(unittest.TestCase):
    """ This is the unittest for the ``htheatpump.version`` code.
    """

    def setUp(self):
        """ Initializes the test environment. """
        pass

    def tearDown(self):
        """ Cleans up the test environment. """
        pass

    def testVersionClass(self):
        version = Version('package-name', 1,2,3)
        self.assertEqual(version.short(), '1.2.3')
        self.assertEqual(str(version), '[package-name, version 1.2.3]')


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    unittest.main()
