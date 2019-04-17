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

""" TODO """

from typing import Optional, List, Dict, Tuple, Any  # , Type, TypeVar
from itertools import chain

import re
import copy


# ------------------------------------------------------------------------------------------------------------------- #
# Logging
# ------------------------------------------------------------------------------------------------------------------- #

import logging
_logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgPeriod class
# ------------------------------------------------------------------------------------------------------------------- #

#T = TypeVar("T", bound="TimeProgPeriod")  # TODO


class TimeProgPeriod:
    """ TODO doc
    """
    TIME_PATTERN = r"^(\d{1,2}):(\d{1,2})$"  # e.g. '23:45'
    HOURS_RANGE = range(0, 25)               # 0..24
    MINUTES_RANGE = range(0, 60)             # 0..59

    def __init__(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> None:
        # verify the passed time values
        self._verify(start_hour, start_minute, end_hour, end_minute)
        # ... and store it
        self._start_hour, self._start_minute = start_hour, start_minute
        self._end_hour, self._end_minute = end_hour, end_minute

    @classmethod
    #def _is_time_valid(cls: Type[T], hour, minute) -> bool:
    def _is_time_valid(cls, hour, minute) -> bool:
        if (hour not in cls.HOURS_RANGE) or (minute not in cls.MINUTES_RANGE):
            return False
        if (hour * 60 + minute) > (24 * 60 + 0):  # e.g. '24:15' -> not valid!
            return False
        return True

    @classmethod
    #def _verify(cls: Type[T], start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> None:
    def _verify(cls, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> None:
        if not cls._is_time_valid(start_hour, start_minute):
            raise ValueError("the provided start time does not represent a valid time value [{:d}:{:d}]".format(
                start_hour, start_minute))
        if not cls._is_time_valid(end_hour, end_minute):
            raise ValueError("the provided end time does not represent a valid time value [{:d}:{:d}]".format(
                end_hour, end_minute))
        if (start_hour * 60 + start_minute) > (end_hour * 60 + end_minute):
            raise ValueError(
                "the provided start time must be lesser or equal to the end time [{:d}:{:d}-{:d}:{:d}]".format(
                    start_hour, start_minute, end_hour, end_minute))

    @classmethod
    #def from_str(cls: Type[T], start_str: str, end_str: str) -> T:
    def from_str(cls, start_str: str, end_str: str) -> Any:
        m_start = re.match(cls.TIME_PATTERN, start_str)
        if not m_start:
            raise ValueError("the provided 'start_str' does not represent a valid time value [{}]".format(start_str))
        m_end = re.match(cls.TIME_PATTERN, end_str)
        if not m_end:
            raise ValueError("the provided 'end_str' does not represent a valid time value [{}]".format(end_str))
        start_hour, start_minute = [int(v) for v in m_start.group(1, 2)]
        end_hour, end_minute = [int(v) for v in m_end.group(1, 2)]
        return cls(start_hour, start_minute, end_hour, end_minute)

    def set(self, start_hour: int, start_minute: int, end_hour: int, end_minute: int) -> None:
        # verify the passed time values
        self._verify(start_hour, start_minute, end_hour, end_minute)
        # ... and store it
        self._start_hour, self._start_minute = start_hour, start_minute
        self._end_hour, self._end_minute = end_hour, end_minute

    def __str__(self) -> str:
        return "{:02d}:{:02d}-{:02d}:{:02d}".format(self._start_hour, self.start_minute,
                                                    self.end_hour, self._end_minute)

    def as_dict(self) -> Dict:
        """ Create a dict representation of this time period.
        """
        return {
            "start": self.start_str,
            "end": self.end_str,
        }

    @property
    def start_str(self) -> str:
        return "{:02d}:{:02d}".format(self._start_hour, self.start_minute)

    @property
    def end_str(self) -> str:
        return "{:02d}:{:02d}".format(self._end_hour, self.end_minute)

    @property
    def start_hour(self) -> int:
        return self._start_hour

    @property
    def start_minute(self) -> int:
        return self._start_minute

    @property
    def end_hour(self) -> int:
        return self._end_hour

    @property
    def end_minute(self) -> int:
        return self._end_minute

    @property
    def start(self) -> Tuple[int, int]:
        return self._start_hour, self._start_minute

    @property
    def end(self) -> Tuple[int, int]:
        return self._end_hour, self._end_minute


# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgEntry class
# ------------------------------------------------------------------------------------------------------------------- #

class TimeProgEntry:
    """ TODO doc
    """
    def __init__(self, state: int, period: TimeProgPeriod) -> None:
        self._state = state
        self._period = copy.deepcopy(period)

    @classmethod
    #def from_str(cls: Type[T], state: str, start_str: str, end_str: str) -> T:
    def from_str(cls, state: str, start_str: str, end_str: str) -> Any:
        return cls(int(state), TimeProgPeriod.from_str(start_str, end_str))

    def set(self, state: int, period: TimeProgPeriod) -> None:
        self._state = state
        self._period = copy.deepcopy(period)

    def __str__(self) -> str:
        return "state={:d}, time={!s}".format(self._state, self._period)

    def as_dict(self) -> Dict:
        """ Create a dict representation of this time program entry.
        """
        ret = {"state": self._state}
        ret.update(self._period.as_dict())
        return ret

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, val: int) -> None:
        self._state = val

    @property
    def period(self) -> TimeProgPeriod:
        return copy.deepcopy(self._period)

    @period.setter
    def period(self, val: TimeProgPeriod) -> None:
        self._period = copy.deepcopy(val)


# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgram class
# ------------------------------------------------------------------------------------------------------------------- #

class TimeProgram:
    """ TODO doc
    """
    def __init__(self, idx: int, name: str, ead: int, nos: int, ste: int, nod: int) -> None:
        self._index = idx
        self._name = name
        self._entries_a_day = ead
        self._number_of_states = nos
        self._step_size = ste
        self._number_of_days = nod
        self._entries = [[None for _ in range(self._entries_a_day)] for _ in range(self._number_of_days)] \
            # type: List[List[Optional[TimeProgEntry]]]
        # TODO verify args!

    def _verify_entry(self, entry: TimeProgEntry) -> None:
        if entry.state not in range(0, self._number_of_states):
            raise ValueError("the state of the provided entry is outside the allowed range [{:d}, 0..{:d}]".format(
                entry.state, self._number_of_states))
        if entry.period.start_minute % self._step_size != 0:
            raise ValueError("the provided start time must be a multiple of the given step size [{}, {:d}]".format(
                entry.period.start_str, self._step_size))
        if entry.period.end_minute % self._step_size != 0:
            raise ValueError("the provided end time must be a multiple of the given step size [{}, {:d}]".format(
                entry.period.end_str, self._step_size))

    def __str__(self) -> str:
        any_entries = sum([1 for entry in chain.from_iterable(self._entries) if entry is not None]) > 0
        return "idx={:d}, name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}, entries=[{}]".format(
            self._index, self._name, self._entries_a_day, self._number_of_states, self._step_size,
            self._number_of_days, "..." if any_entries else "")

    def as_dict(self) -> Dict:
        """ Create a dict representation of this time program.
        """
        return {
            "index": self._index,           # index of the time program
            "name": self._name,             # name of the time program
            "ead": self._entries_a_day,     # entries-a-day (?)
            "nos": self._number_of_states,  # number-of-states (?)
            "ste": self._step_size,         # step-size [in minutes] (?)
            "nod": self._number_of_days,    # number-of-days (?)
            "entries": self._entries,       # the time program entries itself
        }

    @property
    def index(self) -> int:
        return self._index

    @property
    def name(self) -> str:
        return self._name

    @property
    def entries_a_day(self) -> int:
        return self._entries_a_day

    @property
    def number_of_states(self) -> int:
        return self._number_of_states

    @property
    def step_size(self) -> int:
        return self._step_size

    @property
    def number_of_days(self) -> int:
        return self._number_of_days

    def entry(self, day: int, num: int) -> Optional[TimeProgEntry]:
        return copy.deepcopy(self._entries[day][num])

    def entries_of_day(self, day: int) -> List[Optional[TimeProgEntry]]:
        return copy.deepcopy(self._entries[day])

    def set_entry(self, day: int, num: int, entry: TimeProgEntry) -> None:
        self._verify_entry(entry)
        self._entries[day][num] = copy.deepcopy(entry)


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["TimeProgPeriod", "TimeProgEntry", "TimeProgram"]
