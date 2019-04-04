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

""" Definition of the Heliotherm heat pump parameters together with their

      - data point type ("MP", "SP"),
      - data point number,
      - access rights,
      - data type,
      - minimal value and
      - maximal value.
"""

import enum
import csv
from os import path
from typing import Union, Dict, Optional, Any

from htheatpump.utils import Singleton


# ------------------------------------------------------------------------------------------------------------------- #
# Constants and type aliases
# ------------------------------------------------------------------------------------------------------------------- #

CSV_FILE = "htparams.csv"                                    # CSV file with the parameter definitions of the heat pump

HtParamValueType = Union[bool, int, float]        # a heat pump parameter value can be of type 'bool', 'int' or 'float'


# ------------------------------------------------------------------------------------------------------------------- #
# Helper classes
# ------------------------------------------------------------------------------------------------------------------- #

@enum.unique
class HtDataTypes(enum.Enum):
    """ Supported data types of the Heliotherm heat pump:

    * ``BOOL``   The value of the parameter is given as **boolean** (e.g. on/off, yes/no, enabled/disabled).
    * ``INT``    The value of the parameter is given as **integer**.
    * ``FLOAT``  The value of the parameter is given as **floating point number**.
    """
    BOOL = 1
    INT = 2
    FLOAT = 3

    @staticmethod
    def from_str(s: str) -> "HtDataTypes":
        """ Create a corresponding enum representation for the passed string.

        :param s: The passed string.
        :type s: str
        :returns: The corresponding enum representation of the passed string.
        :rtype: ``HtDataTypes``
        :raises ValueError:
            Will be raised if the passed string does not have a corresponding enum representation.
        """
        if s == "BOOL":
            return HtDataTypes.BOOL
        elif s == "INT":
            return HtDataTypes.INT
        elif s == "FLOAT":
            return HtDataTypes.FLOAT
        else:
            raise ValueError("no corresponding enum representation ({!r})".format(s))


class HtParam:
    """ Representation of a specific heat pump parameter.

    :param dp_type: The data point type (:data:`"MP"`, :data:`"SP"`).
    :type dp_type: str
    :param dp_number: The data point number.
    :type dp_number: int
    :param acl: The access rights (:data:`'r'` = read, :data:`'w'` = write).
    :type acl: str
    :param data_type: The data type, see :class:`HtDataTypes`.
    :type data_type: HtDataTypes
    :param min_val: The minimal value (default :const:`None`, which means "doesn't matter").
    :type min_val: bool, int, float or None
    :param max_val: The maximal value (default :const:`None`, which means "doesn't matter").
    :type max_val: bool, int, float or None
    """

    def __init__(self, dp_type: str, dp_number: int, acl: str, data_type: HtDataTypes,
                 min_val: Optional[HtParamValueType] = None, max_val: Optional[HtParamValueType] = None) -> None:
        self.dp_type = dp_type
        self.dp_number = dp_number
        self.acl = acl
        self.data_type = data_type
        self.min_val = min_val
        self.max_val = max_val

    def __repr__(self) -> str:
        return "HtParam({},{:d},{!r},{}[{},{}])".format(self.dp_type, self.dp_number, self.acl,
                                                        self.data_type, self.min_val, self.max_val)

    def cmd(self) -> str:
        """ Return the command string, based on the data point type and number of the parameter.

        :returns: The command string.
        :rtype: ``str``
        """
        return "{},NR={:d}".format(self.dp_type, self.dp_number)

    def set_limits(self, min_val: Optional[HtParamValueType] = None,
                   max_val: Optional[HtParamValueType] = None) -> bool:
        """ Set the limits of the parameter and return whether the passed limit values differed
        from the old one.

        :param min_val: The minimal value (default :const:`None`, which means "doesn't matter").
        :type min_val: bool, int, float or None
        :param max_val: The maximal value (default :const:`None`, which means "doesn't matter").
        :type max_val: bool, int, float or None
        :returns: :const:`True` if the passed min- and/or max-value differed from the old one,
                    :const:`False` otherwise.
        :rtype: ``bool``
        """
        ret = (self.min_val != min_val) or (self.max_val != max_val)
        self.min_val = min_val
        self.max_val = max_val
        return ret

    def in_limits(self, val: HtParamValueType) -> bool:
        """ Determine whether the passed value is in between the parameter limits or not.

        :param val: The value to check against the parameter limits.
        :type val: bool, int or float
        :returns: :const:`True` if the passed value is in between the limits, :const:`False` otherwise.
        :rtype: ``bool``
        """
        assert val is not None, "'val' must not be None"
        # check the passed value against the defined limits (if given; 'None' means "doesn't matter")
        return (self.min_val is None or self.min_val <= val) and (self.max_val is None or val <= self.max_val)

    @staticmethod
    def _from_str(value: str, data_type: HtDataTypes) -> HtParamValueType:
        """ Convert the passed value (in form of a string) to the expected data type.

        :param value: The passed value (in form of a string).
        :type value: str
        :param data_type: The expected data type, see :class:`HtDataTypes`.
        :type data_type: HtDataTypes
        :returns: The passed value which data type matches the expected one.
        :rtype: ``bool``, ``int`` or ``float``
        :raises ValueError:
            Will be raised if the passed value could not be converted to the expected data type.
        """
        assert isinstance(value, str)
        assert isinstance(data_type, HtDataTypes)
        if data_type == HtDataTypes.BOOL:
            value = value.strip()
            # convert to bool ('0' = False, '1' = True)
            if value == "0":
                return False
            elif value == "1":
                return True
            else:
                raise ValueError("invalid representation for data type BOOL ({!r})".format(value))
        elif data_type == HtDataTypes.INT:
            return int(value.strip())  # convert to integer
        elif data_type == HtDataTypes.FLOAT:
            value = value.strip()
            ret = float(value)  # convert to floating point number
            try:  # to be more strict, the passed string shouldn't look like an integer!
                int(value)  # try to convert to integer -> should fail!
            except Exception:
                return ret
            else:
                raise ValueError("invalid representation for data type FLOAT ({!r})".format(value))
        else:
            assert 0, "unsupported data type ({!r})".format(data_type)

    def from_str(self: Union["HtParam", str], arg: Union[str, HtDataTypes]) -> HtParamValueType:
        """ Convert the passed value (in form of a string) to the expected data type.

        This method can be called as a *static method*, e.g.::

            val = HtParam.from_str("123", HtDataTypes.INT)

        or as a *member method* of :class:`HtParam`, e.g.::

            param = HtParams["Temp. Aussen"]
            val = param.from_str(s)

        If the method is called as a member method of :class:`HtParam`, the expected data
        type don't have to be specified. It will be automatically determined from the
        :class:`HtParam` instance.

        :returns: The passed value which data type matches the expected one.
        :rtype: ``bool``, ``int`` or ``float``
        :raises ValueError:
            Will be raised if the passed value could not be converted to the expected data type.
        """
        if isinstance(self, HtParam):  # called as a member method of HtParam
            assert isinstance(arg, str)
            return HtParam._from_str(arg, self.data_type)
        else:  # called as a static method of HtParam
            assert isinstance(self, str)
            assert isinstance(arg, HtDataTypes)
            return HtParam._from_str(self, arg)

    @staticmethod
    def _to_str(value: HtParamValueType, data_type: HtDataTypes) -> str:
        """ Convert the passed value to a string.

        :param value: The passed value.
        :type value: bool, int or float
        :param data_type: The data type of the passed value, see :class:`HtDataTypes`.
        :type data_type: HtDataTypes
        :returns: The string representation of the passed value.
        :rtype: ``str``
        """
        assert isinstance(value, (bool, int, float))
        assert isinstance(data_type, HtDataTypes)
        if data_type == HtDataTypes.BOOL:
            assert isinstance(value, bool)
            # convert to "0" for False and "1" for True
            return "1" if value is True else "0"
        elif data_type == HtDataTypes.INT:
            assert isinstance(value, int)
            return str(value)
        elif data_type == HtDataTypes.FLOAT:
            assert isinstance(value, (int, float))
            return str(float(value))
        else:
            assert 0, "unsupported data type ({!r})".format(data_type)

    def to_str(self: Union["HtParam", HtParamValueType], arg: Union[HtParamValueType, HtDataTypes]) -> str:
        """ Convert the passed value to a string.

        This method can be called as a *static method*, e.g.::

            s = HtParam.to_str(123, HtDataTypes.FLOAT)

        or as a *member method* of :class:`HtParam`, e.g.::

            param = HtParams["Temp. Aussen"]
            s = param.to_str(3.2)

        If the method is called as a member method of :class:`HtParam`, the data type of the
        passed value don't have to be specified. It will be automatically determined from the
        :class:`HtParam` instance.

        :returns: The string representation of the passed value.
        :rtype: ``str``
        """
        if isinstance(self, HtParam):  # called as a member method of HtParam
            assert isinstance(arg, (bool, int, float))
            return HtParam._to_str(arg, self.data_type)
        else:  # called as a static method of HtParam
            assert isinstance(self, (bool, int, float))
            assert isinstance(arg, HtDataTypes)
            return HtParam._to_str(self, arg)


class HtParamsMeta(type):  # pragma: no cover

    def __contains__(cls, item):
        return item in cls._params

    def __getitem__(cls, key):
        return cls._params[key]

    def __len__(cls):
        return len(cls._params)


# ------------------------------------------------------------------------------------------------------------------- #
# Parameter dictionary class
# ------------------------------------------------------------------------------------------------------------------- #

def _load_params_from_csv() -> Dict[str, HtParam]:
    """ Helper function to load all supported heat pump parameter definitions from the CSV file.

    :returns: Dictionary of the supported heat pump parameters:
        ::

            { "Parameter name": HtParam(dp_type=..., dp_number=...,
                                        acl=..., data_type=...,
                                        min_val=..., max_val=...),
              # ...
              }

    :rtype: ``dict``
    """
    # search for a user defined parameter CSV file in "~/.htheatpump"
    filename = path.expanduser(path.join("~/.htheatpump", CSV_FILE))
    if not path.exists(filename):
        # ... and switch back to the default one if no one was found
        filename = path.join(path.dirname(path.abspath(__file__)), CSV_FILE)
    print("HTHEATPUMP: load parameter definitions from: {}".format(filename))
    params = {}
    with open(filename) as f:
        reader = csv.reader(f, delimiter=',', skipinitialspace=True)
        for row in reader:
            # continue for empty rows or comments (starts with character '#')
            if not row or row[0].startswith('#'):
                continue
            name, dp_type, dp_number, acl, data_type, min_val, max_val = row  # type: Any, Any, Any, Any, Any, Any, Any
            # convert the data point number into an int
            dp_number = int(dp_number)
            # convert the given data type into the corresponding enum value
            data_type = HtDataTypes.from_str(data_type)
            # convert the minimal value to the expected data type
            min_val = None if min_val == "None" else HtParam.from_str(min_val, data_type)
            # convert the maximal value to the expected data type
            max_val = None if max_val == "None" else HtParam.from_str(max_val, data_type)
            # add the parameter definition to the dictionary
            params.update({name: HtParam(dp_type=dp_type, dp_number=dp_number,
                                         acl=acl, data_type=data_type,
                                         min_val=min_val, max_val=max_val)})
    return params


class HtParams(Singleton, metaclass=HtParamsMeta):
    """ Dictionary of the supported Heliotherm heat pump parameters. [*]_

    .. note::

        The supported parameters and their definitions are loaded from the CSV file
        :file:`htparams.csv` in this package, but the user can create his own user specific
        CSV file under :file:`~/.htheatpump/htparams.csv`.

    .. [*] Most of the supported heat pump parameters were found by "sniffing" the
           serial communication of the Heliotherm home control Windows application
           (http://homecontrol.heliotherm.com) during a refresh! ;-)
    """

    @classmethod
    def keys(cls):  # TODO -> type
        return cls._params.keys()

    @classmethod
    def items(cls):  # TODO -> type
        return cls._params.items()

    @classmethod
    def get(cls, key: str, default: Optional[HtParam] = None) -> Optional[HtParam]:
        assert isinstance(key, str), "'key' must be of type str"
        assert isinstance(default, str), "'default' must be of type HtParam or None"
        return cls._params.get(key, default)

    @classmethod
    def of_type(cls, dp_type: str) -> Dict[str, HtParam]:
        assert isinstance(dp_type, str), "'dp_type' must be of type str"
        return {n: p for n, p in cls._params.items() if cls._params[n].dp_type == dp_type}

    @classmethod
    def dump(cls) -> None:
        for name, param in HtParams.items():
            print("{!r}: dp_type = {!r}, dp_number = {:d}, acl = {!r}, data_type = {!s}, min = {!s}, max = {!s}"
                  .format(name, param.dp_type, param.dp_number, param.acl,
                          param.data_type if param.data_type else "<unknown>",
                          param.min_val, param.max_val))

    # Dictionary of the supported Heliotherm heat pump parameters
    _params = _load_params_from_csv()  # type: Dict[str, HtParam]


# ------------------------------------------------------------------------------------------------------------------- #
# Main program
# ------------------------------------------------------------------------------------------------------------------- #

# Only for testing: print all supported heat pump parameters
#def main():
#    HtParams.dump()
#
#
#if __name__ == "__main__":
#    main()


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["HtDataTypes", "HtParamValueType", "HtParam", "HtParams"]
