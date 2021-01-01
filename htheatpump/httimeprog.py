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

""" Classes representing the time programs of the Heliotherm heat pump. """

import copy
import re
from itertools import chain
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgPeriod class
# ------------------------------------------------------------------------------------------------------------------- #

TimeProgPeriodT = TypeVar("TimeProgPeriodT", bound="TimeProgPeriod")


class TimeProgPeriod:
    """Representation of a time program period defined by start- and end-time (``HH:MM``).

    :param start_hour: The hour value of the start-time (``HH``).
    :type start_hour: int
    :param start_minute: The minute value of the start-time (``MM``).
    :type start_minute: int
    :param end_hour: The hour value of the end-time (``HH``).
    :type end_hour: int
    :param end_minute: The minute value of the end-time (``MM``).
    :type end_minute: int
    :raises ValueError:
        Will be raised for any invalid argument.
    """

    TIME_PATTERN = r"^(\d?\d):(\d?\d)$"  # e.g. '23:45' or '2:5'
    HOURS_RANGE = range(0, 25)  # 0..24
    MINUTES_RANGE = range(0, 60)  # 0..59

    def __init__(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ) -> None:
        # verify the passed time values
        self._verify(start_hour, start_minute, end_hour, end_minute)
        # ... and store it
        self._start_hour, self._start_minute = start_hour, start_minute
        self._end_hour, self._end_minute = end_hour, end_minute

    @classmethod
    def _is_time_valid(cls: Type[TimeProgPeriodT], hour: int, minute: int) -> bool:
        if (hour not in cls.HOURS_RANGE) or (minute not in cls.MINUTES_RANGE):
            return False
        if (hour * 60 + minute) > (24 * 60 + 0):  # e.g. '24:15' -> not valid!
            return False
        return True

    @classmethod
    def _verify(
        cls: Type[TimeProgPeriodT],
        start_hour: int,
        start_minute: int,
        end_hour: int,
        end_minute: int,
    ) -> None:
        if not cls._is_time_valid(start_hour, start_minute):
            raise ValueError(
                "the provided start time does not represent a valid time value [{:02d}:{:02d}]".format(
                    start_hour, start_minute
                )
            )
        if not cls._is_time_valid(end_hour, end_minute):
            raise ValueError(
                "the provided end time does not represent a valid time value [{:02d}:{:02d}]".format(
                    end_hour, end_minute
                )
            )
        if (start_hour * 60 + start_minute) > (end_hour * 60 + end_minute):
            raise ValueError(
                "the provided start time must be lesser or equal to the end time [{:02d}:{:02d}-{:02d}:{:02d}]".format(
                    start_hour, start_minute, end_hour, end_minute
                )
            )

    @classmethod
    def from_str(
        cls: Type[TimeProgPeriodT], start_str: str, end_str: str
    ) -> TimeProgPeriodT:
        """Create a :class:`~TimeProgPeriod` instance from string representations of the start- and end-time.

        :param start_str: The start-time of the time program entry as :obj:`str`.
        :type start_str: str
        :param end_str: The end-time of the time program entry as :obj:`str`.
        :type end_str: str
        :returns: A :class:`~TimeProgPeriod` instance with the given properties.
        :rtype: ``TimeProgPeriod``
        :raises ValueError:
            Will be raised for any invalid argument.
        """
        m_start = re.match(cls.TIME_PATTERN, start_str)
        if not m_start:
            raise ValueError(
                "the provided 'start_str' does not represent a valid time value [{!r}]".format(
                    start_str
                )
            )
        m_end = re.match(cls.TIME_PATTERN, end_str)
        if not m_end:
            raise ValueError(
                "the provided 'end_str' does not represent a valid time value [{!r}]".format(
                    end_str
                )
            )
        start_hour, start_minute = [int(v) for v in m_start.group(1, 2)]
        end_hour, end_minute = [int(v) for v in m_end.group(1, 2)]
        return cls(start_hour, start_minute, end_hour, end_minute)

    @classmethod
    def from_json(
        cls: Type[TimeProgPeriodT], json_dict: Dict[str, str]
    ) -> TimeProgPeriodT:
        """Create a :class:`~TimeProgPeriod` instance from a JSON representation.

        :param json_dict: The JSON representation of the time program period as :obj:`dict`.
        :type json_dict: dict
        :rtype: ``TimeProgPeriod``
        :raises ValueError:
            Will be raised for any invalid argument.
        """
        return cls.from_str(json_dict["start"], json_dict["end"])

    def set(
        self, start_hour: int, start_minute: int, end_hour: int, end_minute: int
    ) -> None:
        """Set the start- and end-time of this time program period.

        :param start_hour: The hour value of the start-time.
        :type start_hour: int
        :param start_minute: The minute value of the start-time.
        :type start_minute: int
        :param end_hour: The hour value of the end-time.
        :type end_hour: int
        :param end_minute: The minute value of the end-time.
        :type end_minute: int
        :raises ValueError:
            Will be raised for any invalid argument.
        """
        # verify the passed time values
        self._verify(start_hour, start_minute, end_hour, end_minute)
        # ... and store it
        self._start_hour, self._start_minute = start_hour, start_minute
        self._end_hour, self._end_minute = end_hour, end_minute

    def __str__(self) -> str:
        """Return a string representation of this time program period.

        :returns: A string representation of this time program period.
        :rtype: ``str``
        """
        return "{:02d}:{:02d}-{:02d}:{:02d}".format(
            self._start_hour, self.start_minute, self.end_hour, self._end_minute
        )

    def __eq__(self, other):
        """Implement the equal operator.

        :param other: Another instance of :class:`~TimeProgPeriod` to check against.
        :returns: :const:`True` if we check against the same subclass and the raw values matches,
            :const:`False` otherwise.
        :rtype: ``bool``
        """
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            raise TypeError()
        return (
            self._start_hour == other.start_hour
            and self._start_minute == other.start_minute
            and self._end_hour == other.end_hour
            and self._end_minute == other.end_minute
        )

    def as_dict(self) -> Dict[str, object]:
        """Create a dict representation of this time program period.

        :returns: A dict representing this time program period.
        :rtype: ``dict``
        """
        return {
            "start": (self._start_hour, self._start_minute),
            "end": (self._end_hour, self._end_minute),
        }

    def as_json(self) -> Dict[str, object]:
        """Create a json-readable dict representation of this time program period.

        :returns: A json-readable dict representing this time program period.
        :rtype: ``dict``
        """
        return {
            "start": self.start_str,
            "end": self.end_str,
        }

    @property
    def start_str(self) -> str:
        """Return the start-time of this time program period as :obj:`str`.

        :returns: The start-time of this time program period as :obj:`str`. For example:
            ::

                '11:00'

        :rtype: ``str``
        """
        return "{:02d}:{:02d}".format(self._start_hour, self.start_minute)

    @property
    def end_str(self) -> str:
        """Return the end-time of this time program period as :obj:`str`.

        :returns: The end-time of this time program period as :obj:`str`. For example:
            ::

                '16:45'

        :rtype: ``str``
        """
        return "{:02d}:{:02d}".format(self._end_hour, self.end_minute)

    @property
    def start_hour(self) -> int:
        """Return the hour value of the start-time of this time program period.

        :returns: The hour value of the start-time of this time program period.
        :rtype: ``int``
        """
        return self._start_hour

    @property
    def start_minute(self) -> int:
        """Return the minute value of the start-time of this time program period.

        :returns: The minute value of the start-time of this time program period.
        :rtype: ``int``
        """
        return self._start_minute

    @property
    def end_hour(self) -> int:
        """Return the hour value of the end-time of this time program period.

        :returns: The hour value of the end-time of this time program period.
        :rtype: ``int``
        """
        return self._end_hour

    @property
    def end_minute(self) -> int:
        """Return the minute value of the end-time of this time program period.

        :returns: The minute value of the end-time of this time program period.
        :rtype: ``int``
        """
        return self._end_minute

    @property
    def start(self) -> Tuple[int, int]:
        """Return the start-time of this time program period as a tuple with 2 elements,
        where the first element represents the hours and the second one the minutes.

        :returns: The start-time of this time program period as tuple. For example:
            ::

                ( 11, 0 )  # -> 11:00

        :rtype: ``tuple`` ( int, int )
        """
        return self._start_hour, self._start_minute

    @property
    def end(self) -> Tuple[int, int]:
        """Return the end-time of this time program period as a tuple with 2 elements,
        where the first element represents the hours and the second one the minutes.

        :returns: The end-time of this time program period as tuple. For example:
            ::

                ( 16, 45 )  # -> 16:45

        :rtype: ``tuple`` ( int, int )
        """
        return self._end_hour, self._end_minute


# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgEntry class
# ------------------------------------------------------------------------------------------------------------------- #

TimeProgEntryT = TypeVar("TimeProgEntryT", bound="TimeProgEntry")


class TimeProgEntry:
    """Representation of a single time program entry.

    :param state: The state of the time program entry.
    :type state: int
    :param period: The period of the time program entry.
    :type period: TimeProgPeriod
    """

    def __init__(self, state: int, period: TimeProgPeriod) -> None:
        self._state = state
        self._period = copy.deepcopy(period)

    @classmethod
    def from_str(
        cls: Type[TimeProgEntryT], state: str, start_str: str, end_str: str
    ) -> TimeProgEntryT:
        """Create a :class:`~TimeProgEntry` instance from string representations of the state, start- and end-time.

        :param state: The state of the time program entry as :obj:`str`.
        :type state: str
        :param start_str: The start-time of the time program entry as :obj:`str`.
        :type start_str: str
        :param end_str: The end-time of the time program entry as :obj:`str`.
        :type end_str: str
        :returns: A :class:`~TimeProgEntry` instance with the given properties.
        :rtype: ``TimeProgEntry``
        """
        return cls(int(state), TimeProgPeriod.from_str(start_str, end_str))

    @classmethod
    def from_json(
        cls: Type[TimeProgEntryT], json_dict: Dict[str, Any]
    ) -> TimeProgEntryT:
        """Create a :class:`~TimeProgEntry` instance from a JSON representation.

        :param json_dict: The JSON representation of the time program entry as :obj:`dict`.
        :type json_dict: dict
        :rtype: ``TimeProgEntry``
        :raises ValueError:
            Will be raised for any invalid argument.
        """
        return cls(
            int(json_dict["state"]),
            TimeProgPeriod.from_str(json_dict["start"], json_dict["end"]),
        )

    def set(self, state: int, period: TimeProgPeriod) -> None:
        """Set the state and period of this time program entry.

        :param state: The state of the time program entry.
        :type state: int
        :param period: The period of the time program entry.
        :type period: TimeProgPeriod
        """
        self._state = state
        self._period = copy.deepcopy(period)

    def __str__(self) -> str:
        """Return a string representation of this time program entry.

        :returns: A string representation of this time program entry.
        :rtype: ``str``
        """
        return "state={:d}, time={!s}".format(self._state, self._period)

    def __eq__(self, other):
        """Implement the equal operator.

        :param other: Another instance of :class:`~TimeProgEntry` to check against.
        :returns: :const:`True` if we check against the same subclass and the raw values matches,
            :const:`False` otherwise.
        :rtype: ``bool``
        """
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            raise TypeError()
        return self._state == other.state and self._period == other.period

    def as_dict(self) -> Dict[str, object]:
        """Create a dict representation of this time program entry.

        :returns: A dict representing this time program entry.
        :rtype: ``dict``
        """
        ret = {"state": self._state}  # type: Dict[str, object]
        ret.update(self._period.as_dict())
        return ret

    def as_json(self) -> Dict[str, object]:
        """Create a json-readable dict representation of this time program entry.

        :returns: A json-readable dict representing this time program entry.
        :rtype: ``dict``
        """
        ret = {"state": self._state}  # type: Dict[str, object]
        ret.update(self._period.as_json())
        return ret

    @property
    def state(self) -> int:
        """Property to get or set the state of this time program entry.

        :param: The new state of the time program entry.
        :returns: The current state of the time program entry.
        :rtype: ``int``
        """
        return self._state

    @state.setter
    def state(self, val: int) -> None:
        self._state = val

    @property
    def period(self) -> TimeProgPeriod:
        """Property to get or set the period of this time program entry.

        :param: The new period of the time program entry as :class:`~TimeProgPeriod`.
        :returns: A copy of the current period of the time program entry as :class:`~TimeProgPeriod`.
        :rtype: ``TimeProgPeriod``
        """
        return copy.deepcopy(self._period)

    @period.setter
    def period(self, val: TimeProgPeriod) -> None:
        self._period = copy.deepcopy(val)


# ------------------------------------------------------------------------------------------------------------------- #
# TimeProgram class
# ------------------------------------------------------------------------------------------------------------------- #

TimeProgramT = TypeVar("TimeProgramT", bound="TimeProgram")


class TimeProgram:
    """Representation of a time program of the Heliotherm heat pump.

    :param idx: The time program index.
    :type idx: int
    :param name: The name of the time program (e.g. "Warmwasser").
    :type name: str
    :param ead: The number of entries a day of the time program.
    :type ead: int
    :param nos: The number of states of the time program.
    :type nos: int
    :param ste: The step-size (in minutes) of the start- and end-times of the time program entries.
    :type ste: int
    :param nod: The number of days of the time program.
    :type nod: int
    """

    def __init__(
        self, idx: int, name: str, ead: int, nos: int, ste: int, nod: int
    ) -> None:
        self._index = idx
        self._name = name
        self._entries_a_day = ead
        self._number_of_states = nos
        self._step_size = ste
        self._number_of_days = nod
        self._entries = [
            [None for _ in range(self._entries_a_day)]
            for _ in range(self._number_of_days)
        ]  # type: List[List[Optional[TimeProgEntry]]]
        # TODO verify args?!

    def _verify_entry(self, entry: TimeProgEntry) -> None:
        if entry.state not in range(0, self._number_of_states):
            raise ValueError(
                "the state of the provided entry is outside the allowed range [{:d}, 0..{:d}]".format(
                    entry.state, self._number_of_states
                )
            )
        if entry.period.start_minute % self._step_size != 0:
            raise ValueError(
                "the provided start time must be a multiple of the given step size [{}, {:d}]".format(
                    entry.period.start_str, self._step_size
                )
            )
        if entry.period.end_minute % self._step_size != 0:
            raise ValueError(
                "the provided end time must be a multiple of the given step size [{}, {:d}]".format(
                    entry.period.end_str, self._step_size
                )
            )

    @classmethod
    def from_json(cls: Type[TimeProgramT], json_dict: Dict[str, Any]) -> TimeProgramT:
        """Create a :class:`~TimeProgram` instance from a JSON representation.

        :param json_dict: The JSON representation of the time program as :obj:`dict`.
        :type json_dict: dict
        :rtype: ``TimeProgram``
        :raises ValueError:
            Will be raised for any invalid argument.
        """
        idx = int(json_dict["index"])  # type: int
        name = json_dict["name"]  # type: str
        ead = int(json_dict["ead"])  # type: int
        nos = int(json_dict["nos"])  # type: int
        ste = int(json_dict["ste"])  # type: int
        nod = int(json_dict["nod"])  # type: int
        time_prog = cls(idx, name, ead, nos, ste, nod)
        entries = json_dict.get(
            "entries"
        )  # type: Optional[List[List[Optional[Dict[str, Any]]]]]
        if entries is not None:
            for day_num, day_entries in enumerate(entries):
                for entry_num, entry in enumerate(day_entries):
                    if entry is not None:
                        time_prog.set_entry(
                            day_num, entry_num, TimeProgEntry.from_json(entry)
                        )
        return time_prog

    def __str__(self) -> str:
        """Return a string representation of this time program.

        :returns: A string representation of this time program.
        :rtype: ``str``
        """
        any_entries = (
            sum(
                [1 for entry in chain.from_iterable(self._entries) if entry is not None]
            )
            > 0
        )
        return "idx={:d}, name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}, entries=[{}]".format(
            self._index,
            self._name,
            self._entries_a_day,
            self._number_of_states,
            self._step_size,
            self._number_of_days,
            "..." if any_entries else "",
        )

    def as_dict(self, with_entries: bool = True) -> Dict[str, object]:
        """Create a dict representation of this time program.

        :param with_entries: Determines whether the single time program entries should be included or not.
            Default is :const:`True`.
        :type with_entries: bool
        :returns: A dict representing this time program.
        :rtype: ``dict``
        """
        ret = {
            "index": self._index,  # index of the time program
            "name": self._name,  # name of the time program
            "ead": self._entries_a_day,  # entries-a-day (?)
            "nos": self._number_of_states,  # number-of-states (?)
            "ste": self._step_size,  # step-size [in minutes] (?)
            "nod": self._number_of_days,  # number-of-days (?)
        }
        if with_entries:  # the time program entries itself
            ret.update({"entries": self._entries})
        return ret

    def as_json(self, with_entries: bool = True) -> Dict[str, object]:
        """Create a json-readable dict representation of this time program.

        :param with_entries: Determines whether the single time program entries should be included or not.
            Default is :const:`True`.
        :type with_entries: bool
        :returns: A json-readable dict representing this time program.
        :rtype: ``dict``
        """
        ret = {
            "index": self._index,  # index of the time program
            "name": self._name,  # name of the time program
            "ead": self._entries_a_day,  # entries-a-day (?)
            "nos": self._number_of_states,  # number-of-states (?)
            "ste": self._step_size,  # step-size [in minutes] (?)
            "nod": self._number_of_days,  # number-of-days (?)
        }
        if with_entries:  # the time program entries itself
            ret.update(
                {
                    "entries": [
                        [
                            entry.as_json() if entry is not None else None
                            for entry in day_entries
                        ]
                        for day_entries in self._entries
                    ]
                }
            )
        return ret

    @property
    def index(self) -> int:
        """Return the index of this time program.

        :returns: The index of this time program.
        :rtype: ``int``
        """
        return self._index

    @property
    def name(self) -> str:
        """Return the name of this time program.

        :returns: The name of this time program.
        :rtype: ``int``
        """
        return self._name

    @property
    def entries_a_day(self) -> int:
        """Return the number of entries a day of this time program.

        :returns: The number of entries a day of this time program.
        :rtype: ``int``
        """
        return self._entries_a_day

    @property
    def number_of_states(self) -> int:
        """Return the number of states of this time program.

        :returns: The number of states of this time program.
        :rtype: ``int``
        """
        return self._number_of_states

    @property
    def step_size(self) -> int:
        """Return the step-size (in minutes) of the start- and end-times of this time program entries.

        :returns: The step-size (in minutes) of the start- and end-times of this time program entries.
        :rtype: ``int``
        """
        return self._step_size

    @property
    def number_of_days(self) -> int:
        """Return the number of days of this time program.

        :returns: The number of days of this time program.
        :rtype: ``int``
        """
        return self._number_of_days

    def entry(self, day: int, num: int) -> Optional[TimeProgEntry]:
        """Return a copy of a specific time program entry.

        :param day: The day of the time program entry.
        :type day: int
        :param num: The number of the time program entry.
        :type num: int
        :returns: The time program entry as instance of :class:`~TimeProgEntry` or :const:`None` if not set.
        :rtype: ``TimeProgEntry``
        """
        return copy.deepcopy(self._entries[day][num])

    def entries_of_day(self, day: int) -> List[Optional[TimeProgEntry]]:
        """Return a list of copies of time program entries of a specific day.

        :param day: The day of the time program entries.
        :type day: int
        :returns: A list of :class:`~TimeProgEntry` instances or :const:`None` if not set.
        :rtype: ``list`` (TimeProgEntry)
        """
        return copy.deepcopy(self._entries[day])

    def set_entry(self, day: int, num: int, entry: TimeProgEntry) -> None:
        """Set the properties of a given time program entry of the heat pump.

        :param day: The day of the time program entry.
        :type day: int
        :param num: The number of the time program entry.
        :type num: int
        :param entry: The time program entry itself.
        :type entry: TimeProgEntry
        :raises ValueError:
            Will be raised if any property of the given entry is out of the specification of this time program.
        """
        self._verify_entry(entry)
        self._entries[day][num] = copy.deepcopy(entry)


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["TimeProgPeriod", "TimeProgEntry", "TimeProgram"]
