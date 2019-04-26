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
from htheatpump.httimeprog import TimeProgPeriod, TimeProgEntry  # , TimeProgram


class TestTimeProgPeriod:
    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        # -- should raise a 'ValueError':
        (25,  0,  0,  0),
        (99, 99, 99, 99),
        (12, 45, 23, 88),
        (22, 45, 19, 15),
        (24,  1,  0,  0),
        ( 0,  0, 24,  1),
        (23, 45,  0, 15),
        # ...
    ])
    def test_init_raises_ValueError(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        with pytest.raises(ValueError):
            TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_init(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
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
        (" 3:45", " 4:00"),
        ("00:00", "qwerz"),
        # ...
    ])
    def test_from_str_raises_ValueError(self, start_str: str, end_str: str):
        with pytest.raises(ValueError):
            TimeProgPeriod.from_str(start_str, end_str)
        #assert 0

    @pytest.mark.parametrize("start_str, end_str", [
        ("00:00", "00:00"),
        ("24:00", "24:00"),
        ( "3:45",  "4:00"),
        ("12:45", "23:15"),
        ("02:10", "03:35"),
        ("23:45", "24:00"),
        # ...
    ])
    def test_from_str(self, start_str: str, end_str: str):
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

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        ( 3, 45,  4,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_set(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        TimeProgPeriod(0, 0, 0, 0).set(start_hour, start_minute, end_hour, end_minute)
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        ( 3, 45,  4,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_str(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        assert str(TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)) ==\
            "{:02d}:{:02d}-{:02d}:{:02d}".format(start_hour, start_minute, end_hour, end_minute)
        #assert 0

    def test_eq(self):
        assert TimeProgPeriod(0, 0, 0, 0) == TimeProgPeriod(0, 0, 0, 0)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 0, 0, 1)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 0, 1, 0)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 1, 0, 1)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(1, 0, 1, 0)
        # ...
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        ( 3, 45,  4,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_as_dict(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        assert TimeProgPeriod(start_hour, start_minute, end_hour, end_minute).as_dict() ==\
            {"start": (start_hour, start_minute), "end": (end_hour, end_minute)}
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        ( 3, 45,  4,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_as_json(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        assert TimeProgPeriod(start_hour, start_minute, end_hour, end_minute).as_json() ==\
            {"start": "{:02d}:{:02d}".format(start_hour, start_minute),
             "end": "{:02d}:{:02d}".format(end_hour, end_minute),
             }
        #assert 0

    @pytest.mark.parametrize("start_hour, start_minute, end_hour, end_minute", [
        ( 0,  0,  0,  0),
        (24,  0, 24,  0),
        ( 3, 45,  4,  0),
        (12, 45, 23, 15),
        ( 2, 10,  3, 35),
        (23, 45, 24,  0),
        # ...
    ])
    def test_properties(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int):
        period = TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        assert period.start_str == "{:02d}:{:02d}".format(start_hour, start_minute)
        assert period.end_str == "{:02d}:{:02d}".format(end_hour, end_minute)
        assert period.start_hour == start_hour
        assert period.start_minute == start_minute
        assert period.end_hour == end_hour
        assert period.end_minute == end_minute
        assert period.start == (start_hour, start_minute)
        assert period.end == (end_hour, end_minute)
        #assert 0


class TestTimeProgEntry:

    def test_init(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry = TimeProgEntry(state, period)
        assert entry.state == state
        assert entry.period == period
        assert entry.period is not period  # entry.period should be a "deepcopy" of period
        #assert 0

    @pytest.mark.parametrize("state", [
        # -- should raise a 'ValueError':
        "abc",
        "--1",
        "-1+",
        "0x8",
        "1,2",
        # ...
    ])
    def test_from_str_raises_ValueError(self, state: str):
        with pytest.raises(ValueError):
            TimeProgEntry.from_str(state, "00:00", "00:00")
        #assert 0

    @pytest.mark.parametrize("state", range(-10, 10))
    def test_from_str(self, state: str):
        entry = TimeProgEntry.from_str(str(state), "00:00", "00:00")
        assert entry.state == state
        #assert 0

    def test_set(self):
        entry = TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0))
        assert entry.state == 0
        assert entry.period == TimeProgPeriod(0, 0, 0, 0)
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry.set(state, period)
        assert entry.state == state
        assert entry.period == period
        assert entry.period is not period  # entry.period should be a "deepcopy" of period
        #assert 0

    @pytest.mark.parametrize("state", range(-10, 10))
    def test_str(self, state: str):
        assert str(TimeProgEntry.from_str(str(state), "00:00", "00:00")) ==\
            "state={:d}, time={!s}".format(state, TimeProgPeriod.from_str("00:00", "00:00"))
        #assert 0

    def test_eq(self):
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) == TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0))
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(1, TimeProgPeriod(0, 0, 0, 0))
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 1))
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(0, TimeProgPeriod(0, 0, 1, 0))
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(0, TimeProgPeriod(0, 1, 0, 1))
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(0, TimeProgPeriod(1, 0, 1, 0))
        # ...
        #assert 0

    def test_as_dict(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        assert TimeProgEntry(state, period).as_dict() == {"state": state, "start": period.start, "end": period.end}
        #assert 0

    def test_as_json(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        assert TimeProgEntry(state, period).as_json() ==\
            {"state": state, "start": period.start_str, "end": period.end_str}
        #assert 0

    def test_properties(self):
        state = 0
        period = TimeProgPeriod(0, 0, 0, 0)
        entry = TimeProgEntry(state, period)
        assert entry.state == state
        assert entry.period == period
        assert entry.period is not period  # entry.period should be a "deepcopy" of period
        entry.state = 123
        assert entry.state == 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry.period = period
        assert entry.period == period
        assert entry.period is not period  # entry.period should be a "deepcopy" of period
        #assert 0


# TODO: add some more tests here
