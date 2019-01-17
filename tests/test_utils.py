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

""" Tests for code in htheatpump.utils. """

from htheatpump.utils import Singleton


# A simple Singleton class with one `int` member
class MySingleton(Singleton):
    val = -1

    def __init__(self, v):
        self.val = v


def test_SingletonClass():
    s1 = MySingleton(1)
    assert s1.val == 1
    s2 = MySingleton(2)
    assert s2.val == 2
    assert s1.val == 2  # now, 's1' should also be 2
