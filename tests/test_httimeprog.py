#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2021  Daniel Strigl

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

from typing import Dict

import pytest

from htheatpump import TimeProgEntry, TimeProgPeriod, TimeProgram


class TestTimeProgPeriod:
    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            # -- should raise a 'ValueError':
            (25, 0, 0, 0),
            (99, 99, 99, 99),
            (12, 45, 23, 88),
            (22, 45, 19, 15),
            (24, 1, 0, 0),
            (0, 0, 24, 1),
            (23, 45, 0, 15),
            # ...
        ],
    )
    def test_init_raises_ValueError(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        with pytest.raises(ValueError):
            TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_init(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        # assert 0

    @pytest.mark.parametrize(
        "start_str, end_str",
        [
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
        ],
    )
    def test_from_str_raises_ValueError(self, start_str: str, end_str: str):
        with pytest.raises(ValueError):
            TimeProgPeriod.from_str(start_str, end_str)
        # assert 0

    @pytest.mark.parametrize(
        "start_str, end_str",
        [
            ("00:00", "00:00"),
            ("24:00", "24:00"),
            ("3:45", "4:00"),
            ("12:45", "23:15"),
            ("02:10", "03:35"),
            ("23:45", "24:00"),
            # ...
        ],
    )
    def test_from_str(self, start_str: str, end_str: str):
        TimeProgPeriod.from_str(start_str, end_str)
        # assert 0

    @pytest.mark.parametrize(
        "json_dict",
        [
            {"start": "00:00", "end": "00:00"},
            {"start": "24:00", "end": "24:00"},
            {"start": "3:45", "end": "4:00"},
            {"start": "12:45", "end": "23:15"},
            {"start": "02:10", "end": "03:35"},
            {"start": "23:45", "end": "24:00"},
            # ...
        ],
    )
    def test_from_json(self, json_dict: Dict[str, str]):
        TimeProgPeriod.from_json(json_dict)
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            # -- should raise a 'ValueError':
            (25, 0, 0, 0),
            (99, 99, 99, 99),
            (12, 45, 23, 88),
            (22, 45, 19, 15),
            (24, 1, 0, 0),
            (0, 0, 24, 1),
            # ...
        ],
    )
    def test_set_raises_ValueError(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        period = TimeProgPeriod(0, 0, 0, 0)
        with pytest.raises(ValueError):
            period.set(start_hour, start_minute, end_hour, end_minute)
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (3, 45, 4, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_set(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        TimeProgPeriod(0, 0, 0, 0).set(start_hour, start_minute, end_hour, end_minute)
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (3, 45, 4, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_str(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        assert str(
            TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        ) == "{:02d}:{:02d}-{:02d}:{:02d}".format(
            start_hour, start_minute, end_hour, end_minute
        )
        # assert 0

    def test_eq(self):
        assert TimeProgPeriod(0, 0, 0, 0) != None  # noqa: E711
        with pytest.raises(TypeError):
            TimeProgPeriod(0, 0, 0, 0) != 123
        assert TimeProgPeriod(0, 0, 0, 0) == TimeProgPeriod(0, 0, 0, 0)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 0, 0, 1)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 0, 1, 0)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(0, 1, 0, 1)
        assert TimeProgPeriod(0, 0, 0, 0) != TimeProgPeriod(1, 0, 1, 0)
        # ...
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (3, 45, 4, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_as_dict(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        assert TimeProgPeriod(
            start_hour, start_minute, end_hour, end_minute
        ).as_dict() == {
            "start": (start_hour, start_minute),
            "end": (end_hour, end_minute),
        }
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (3, 45, 4, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_as_json(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        assert TimeProgPeriod(
            start_hour, start_minute, end_hour, end_minute
        ).as_json() == {
            "start": "{:02d}:{:02d}".format(start_hour, start_minute),
            "end": "{:02d}:{:02d}".format(end_hour, end_minute),
        }
        # assert 0

    @pytest.mark.parametrize(
        "start_hour, start_minute, end_hour, end_minute",
        [
            (0, 0, 0, 0),
            (24, 0, 24, 0),
            (3, 45, 4, 0),
            (12, 45, 23, 15),
            (2, 10, 3, 35),
            (23, 45, 24, 0),
            # ...
        ],
    )
    def test_properties(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ):
        period = TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        assert period.start_str == "{:02d}:{:02d}".format(start_hour, start_minute)
        assert period.end_str == "{:02d}:{:02d}".format(end_hour, end_minute)
        assert period.start_hour == start_hour
        assert period.start_minute == start_minute
        assert period.end_hour == end_hour
        assert period.end_minute == end_minute
        assert period.start == (start_hour, start_minute)
        assert period.end == (end_hour, end_minute)
        # assert 0


class TestTimeProgEntry:
    def test_init(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry = TimeProgEntry(state, period)
        assert entry.state == state
        assert entry.period == period
        assert (
            entry.period is not period
        )  # entry.period should be a "deepcopy" of period
        # assert 0

    @pytest.mark.parametrize(
        "state",
        [
            # -- should raise a 'ValueError':
            "abc",
            "--1",
            "-1+",
            "0x8",
            "1,2",
            # ...
        ],
    )
    def test_from_str_raises_ValueError(self, state: str):
        with pytest.raises(ValueError):
            TimeProgEntry.from_str(state, "00:00", "00:00")
        # assert 0

    @pytest.mark.parametrize("state", range(-10, 10))
    def test_from_str(self, state: int):
        entry = TimeProgEntry.from_str(str(state), "00:00", "00:00")
        assert entry.state == state
        # assert 0

    @pytest.mark.parametrize("state", range(-10, 10))
    def test_from_json(self, state: int):
        entry = TimeProgEntry.from_json(
            {"state": state, "start": "00:00", "end": "00:00"}
        )
        assert entry.state == state
        # assert 0

    def test_set(self):
        entry = TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0))
        assert entry.state == 0
        assert entry.period == TimeProgPeriod(0, 0, 0, 0)
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry.set(state, period)
        assert entry.state == state
        assert entry.period == period
        assert (
            entry.period is not period
        )  # entry.period should be a "deepcopy" of period
        # assert 0

    @pytest.mark.parametrize("state", range(-10, 10))
    def test_str(self, state: int):
        assert str(
            TimeProgEntry.from_str(str(state), "00:00", "00:00")
        ) == "state={:d}, time={!s}".format(
            state, TimeProgPeriod.from_str("00:00", "00:00")
        )
        # assert 0

    def test_eq(self):
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != None  # noqa: E711
        with pytest.raises(TypeError):
            TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != 123
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) == TimeProgEntry(
            0, TimeProgPeriod(0, 0, 0, 0)
        )
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(
            1, TimeProgPeriod(0, 0, 0, 0)
        )
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(
            0, TimeProgPeriod(0, 0, 0, 1)
        )
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(
            0, TimeProgPeriod(0, 0, 1, 0)
        )
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(
            0, TimeProgPeriod(0, 1, 0, 1)
        )
        assert TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)) != TimeProgEntry(
            0, TimeProgPeriod(1, 0, 1, 0)
        )
        # ...
        # assert 0

    def test_as_dict(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        assert TimeProgEntry(state, period).as_dict() == {
            "state": state,
            "start": period.start,
            "end": period.end,
        }
        # assert 0

    def test_as_json(self):
        state = 123
        period = TimeProgPeriod(21, 22, 23, 24)
        assert TimeProgEntry(state, period).as_json() == {
            "state": state,
            "start": period.start_str,
            "end": period.end_str,
        }
        # assert 0

    def test_properties(self):
        state = 0
        period = TimeProgPeriod(0, 0, 0, 0)
        entry = TimeProgEntry(state, period)
        assert entry.state == state
        assert entry.period == period
        assert (
            entry.period is not period
        )  # entry.period should be a "deepcopy" of period
        entry.state = 123
        assert entry.state == 123
        period = TimeProgPeriod(21, 22, 23, 24)
        entry.period = period
        assert entry.period == period
        assert (
            entry.period is not period
        )  # entry.period should be a "deepcopy" of period
        # assert 0


class TestTimeProgram:
    def test_init(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert time_prog.index == 0
        assert time_prog.name == "Name"
        assert time_prog.entries_a_day == 10
        assert time_prog.number_of_states == 3
        assert time_prog.step_size == 10
        assert time_prog.number_of_days == 7
        assert len(time_prog._entries) == time_prog.number_of_days
        assert all(
            [
                len(entries_of_day) == time_prog.entries_a_day
                for entries_of_day in time_prog._entries
            ]
        )
        # assert 0

    def test_from_json(self):
        time_prog = TimeProgram.from_json(
            {"index": 0, "name": "Name", "ead": 10, "nos": 3, "ste": 10, "nod": 7}
        )
        assert time_prog.index == 0
        assert time_prog.name == "Name"
        assert time_prog.entries_a_day == 10
        assert time_prog.number_of_states == 3
        assert time_prog.step_size == 10
        assert time_prog.number_of_days == 7
        assert len(time_prog._entries) == time_prog.number_of_days
        assert all(
            [
                len(entries_of_day) == time_prog.entries_a_day
                for entries_of_day in time_prog._entries
            ]
        )
        time_prog = TimeProgram.from_json(
            {
                "index": 0,
                "name": "Name",
                "ead": 10,
                "nos": 3,
                "ste": 10,
                "nod": 7,
                "entries": [
                    [None for _ in range(time_prog.entries_a_day)]
                    for _ in range(time_prog.number_of_days)
                ],
            }
        )
        assert len(time_prog._entries) == time_prog.number_of_days
        assert all(
            [
                len(entries_of_day) == time_prog.entries_a_day
                for entries_of_day in time_prog._entries
            ]
        )
        assert all(
            time_prog.entry(day, num) is None
            for num in range(time_prog.entries_a_day)
            for day in range(time_prog.number_of_days)
        )
        time_prog = TimeProgram.from_json(
            {
                "index": 0,
                "name": "Name",
                "ead": 10,
                "nos": 3,
                "ste": 10,
                "nod": 7,
                "entries": [
                    [
                        {"state": 1, "start": "00:00", "end": "23:50"}
                        for _ in range(time_prog.entries_a_day)
                    ]
                    for _ in range(time_prog.number_of_days)
                ],
            }
        )
        assert len(time_prog._entries) == time_prog.number_of_days
        assert all(
            [
                len(entries_of_day) == time_prog.entries_a_day
                for entries_of_day in time_prog._entries
            ]
        )
        assert all(
            time_prog.entry(day, num) == TimeProgEntry(1, TimeProgPeriod(0, 0, 23, 50))
            for num in range(time_prog.entries_a_day)
            for day in range(time_prog.number_of_days)
        )
        # assert 0

    def test_str(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert str(
            time_prog
        ) == "idx={:d}, name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}, entries=[{}]".format(
            0, "Name", 10, 3, 10, 7, ""
        )
        time_prog.set_entry(0, 0, TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0)))
        assert str(
            time_prog
        ) == "idx={:d}, name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}, entries=[{}]".format(
            0, "Name", 10, 3, 10, 7, "..."
        )
        # assert 0

    def test_as_dict(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert time_prog.as_dict(False) == {
            "index": 0,
            "name": "Name",
            "ead": 10,
            "nos": 3,
            "ste": 10,
            "nod": 7,
        }
        assert time_prog.as_dict(True) == {
            "index": 0,
            "name": "Name",
            "ead": 10,
            "nos": 3,
            "ste": 10,
            "nod": 7,
            "entries": [
                [None for _ in range(time_prog.entries_a_day)]
                for _ in range(time_prog.number_of_days)
            ],
        }
        # assert 0

    def test_as_json(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert time_prog.as_json(False) == {
            "index": 0,
            "name": "Name",
            "ead": 10,
            "nos": 3,
            "ste": 10,
            "nod": 7,
        }
        assert time_prog.as_json(True) == {
            "index": 0,
            "name": "Name",
            "ead": 10,
            "nos": 3,
            "ste": 10,
            "nod": 7,
            "entries": [
                [None for _ in range(time_prog.entries_a_day)]
                for _ in range(time_prog.number_of_days)
            ],
        }
        # assert 0

    def test_properties(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert time_prog.index == 0
        assert time_prog.name == "Name"
        assert time_prog.entries_a_day == 10
        assert time_prog.number_of_states == 3
        assert time_prog.step_size == 10
        assert time_prog.number_of_days == 7
        # assert 0

    @pytest.mark.parametrize(
        "day, num", [(day, num) for day in range(7) for num in range(7)]
    )
    def test_entry(self, day: int, num: int):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        assert time_prog.entry(day, num) is None
        entry = TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0))
        time_prog.set_entry(day, num, entry)
        assert time_prog.entry(day, num) == entry
        assert (
            time_prog.entry(day, num) is not entry
        )  # time_prog.entry() should be a "deepcopy" of entry
        # assert 0

    def test_entry_raises_IndexError(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        with pytest.raises(IndexError):
            time_prog.entry(time_prog.number_of_days, 0)
        with pytest.raises(IndexError):
            time_prog.entry(0, time_prog.entries_a_day)
        with pytest.raises(IndexError):
            time_prog.entry(time_prog.number_of_days, time_prog.entries_a_day)
        # assert 0

    @pytest.mark.parametrize("day", range(7))
    def test_entries_of_day(self, day: int):
        time_prog = TimeProgram(0, "Name", 10, 3, 10, 7)
        entries_of_day = time_prog.entries_of_day(day)
        assert len(entries_of_day) == time_prog.entries_a_day
        assert entries_of_day == [None for _ in range(time_prog.entries_a_day)]
        # assert 0

    @pytest.mark.parametrize(
        "state, start_hour, start_minute, end_hour, end_minute",
        [
            # -- should raise a 'ValueError':
            (-1, 0, 0, 24, 0),
            (3, 0, 0, 24, 0),
            (0, 0, 1, 24, 0),
            (0, 0, 0, 0, 59),
            # ...
        ],
    )
    def test_set_entry_raises_ValueError(
        self,
        state: int,
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
    ):
        time_prog = TimeProgram(0, "Name", 10, 3, 15, 7)
        period = TimeProgPeriod(start_hour, start_minute, end_hour, end_minute)
        with pytest.raises(ValueError):
            time_prog.set_entry(0, 0, TimeProgEntry(state, period))
        # assert 0

    def test_set_entry_raises_IndexError(self):
        time_prog = TimeProgram(0, "Name", 10, 3, 15, 7)
        entry = TimeProgEntry(0, TimeProgPeriod(0, 0, 0, 0))
        with pytest.raises(IndexError):
            time_prog.set_entry(time_prog.number_of_days, 0, entry)
        with pytest.raises(IndexError):
            time_prog.set_entry(0, time_prog.entries_a_day, entry)
        # assert 0


# TODO: add some more tests here
