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

""" Tests for code in `htheatpump.httimeprog`. """

import pytest
from htheatpump.httimeprog import TimeProgPeriod  # , TimeProgEntry, TimeProgram


class TestTimeProgPeriod:
    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        # -- should raise a 'ValueError':
        (25,  0,  0,  0),
        (99, 99, 99, 99),
        (12, 45, 23, 88),
        (22, 45, 19, 15),
        (24,  1,  0,  0),
        ( 0,  0, 24,  1),
        # ...
    ])
    def test_init_raises_ValueError(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        with pytest.raises(ValueError):
            TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        #assert 0

    @pytest.mark.parametrize("start_str, end_str", [
        # -- should raise a 'ValueError':
        ("25:00", "00:00"),
        ("99:99", "99:99"),
        ("12:45", "23:88"),
        ("22:45", "19:15"),
        ("24:01", "00:00"),
        ("00:00", "24:01"),
        ("ab:cd", "uv:wx"),
        ("12345", "67890"),
        # ...
    ])
    def test_from_str_raises_ValueError(self, start_str: str, end_str: str):
        with pytest.raises(ValueError):
            TimeProgPeriod.from_str(start_str, end_str)
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        # -- should raise a 'ValueError':
        (25,  0,  0,  0),
        (99, 99, 99, 99),
        (12, 45, 23, 88),
        (22, 45, 19, 15),
        (24,  1,  0,  0),
        ( 0,  0, 24,  1),
        # ...
    ])
    def test_set_raises_ValueError(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        period = TimeProgPeriod(0, 0, 0, 0)
        with pytest.raises(ValueError):
            period.set(start_hour, start_minute, end_hour, end_minute)
        #assert 0


# TODO: add some more tests here
