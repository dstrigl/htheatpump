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

from htheatpump.utils import Singleton


# --------------------------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------------------------- #

CSV_FILE = "htparams.csv"              # CSV file with the parameter definitions of the heat pump


# --------------------------------------------------------------------------------------------- #
# Helper classes
# --------------------------------------------------------------------------------------------- #

@enum.unique
class HtDataTypes(enum.Enum):
    """ Supported data types of the Heliotherm heat pump:

    * ``STRING`` The value of the parameter is given in **text form**.
    * ``BOOL``   The value of the parameter is given as **boolean** (e.g. on/off, yes/no).
    * ``INT``    The value of the parameter is given as **integer**.
    * ``FLOAT``  The value of the parameter is given as **floating point number**.
    """
    STRING = 1
    BOOL   = 2
    INT    = 3
    FLOAT  = 4

    @classmethod
    def from_str(cls, s):
        """ Creates a corresponding enum representation for the passed string.

        :param s: The passed string.
        :type s: str
        :returns: The corresponding enum representation of the passed string.
        :rtype: ``HtDataTypes``
        :raises ValueError:
            Will be raised if the passed string does not have a corresponding enum representation.
        """
        if s == "STRING":
            return HtDataTypes.STRING
        elif s == "BOOL":
            return HtDataTypes.BOOL
        elif s == "INT":
            return HtDataTypes.INT
        elif s == "FLOAT":
            return HtDataTypes.FLOAT
        elif s == "None":
            return None
        else:
            raise ValueError("no corresponding enum representation (%s)" % s)


class HtParam:
    """ Representation of a specific heat pump parameter.

    :param dp_type: The data point type (:const:`"MP"`, :const:`"SP"`).
    :type dp_type: str
    :param dp_number: The data point number.
    :type dp_number: int
    :param acl: The access rights (:const:`'r'` = read, :const:`'w'` = write).
    :type acl: str
    :param data_type: The data type, see :class:`htparams.HtDataTypes`.
    :type data_type: HtDataTypes
    :param min: The minimal value (default :const:`None`).
    :type min: int, float or None
    :param max: The maximal value (default :const:`None`).
    :type max: int, float or None
    """

    def __init__(self, dp_type, dp_number, acl, data_type, min=None, max=None):
        self.dp_type = dp_type
        self.dp_number = dp_number
        self.acl = acl
        self.data_type = data_type
        self.min = min
        self.max = max

    def cmd(self):
        """ Returns the command string, based on the data point type and number of the parameter.

        :returns: The command string.
        :rtype: ``str``
        """
        return "{},NR={}".format(self.dp_type, self.dp_number)

    @classmethod
    def conv_value(cls, val, data_type):
        """ Convert the passed value to the expected data type.

        :param val: The passed value.
        :type val: str
        :param data_type: The expected data type, see :class:`htparams.HtDataTypes`.
        :type data_type: HtDataTypes
        :returns: The passed value which data type matches the expected one.
        :rtype: ``str``, ``bool``, ``int`` or ``float``
        :raises ValueError:
            Will be raised if the passed value could not be converted to the expected data type.
        """
        if data_type is None:
            raise ValueError("data type must not be None")
        elif data_type == HtDataTypes.STRING:
            assert isinstance(val, str)
            pass  # passed value should be already a string ;-)
        elif data_type == HtDataTypes.BOOL:
            # convert to bool (0 = True, 1 = False)
            if val == '0':
                val = False
            elif val == '1':
                val = True
            else:
                raise ValueError("invalid value for data type BOOL (%s)" % repr(val))
        elif data_type == HtDataTypes.INT:
            val = int(val)  # convert to integer
        elif data_type == HtDataTypes.FLOAT:
            val = float(val)  # convert to floating point number
        else:
            raise ValueError("unsupported data type (%d)" % data_type)
        return val


class HtParamsMeta(type):

    def __contains__(cls, item):
        return item in cls._params

    def __getitem__(cls, key):
        return cls._params[key]

    def __len__(cls):
        return len(cls._params)


# --------------------------------------------------------------------------------------------- #
# Parameter dictionary class
# --------------------------------------------------------------------------------------------- #

class HtParams(Singleton, metaclass=HtParamsMeta):
    """ Dictionary of the supported Heliotherm heat pump parameters. [*]_

    .. [*] Most of the supported heat pump parameters were found by "sniffing" the
           serial communication of the Heliotherm home control Windows application
           (http://homecontrol.heliotherm.com) during a refresh! ;-)
    """

    @classmethod
    def keys(cls):
        return cls._params.keys()

    @classmethod
    def items(cls):
        return cls._params.items()

    @classmethod
    def get(cls, key, default=None):
        return cls._params.get(key, default)

    @classmethod
    def dump(cls):
        for name, param in HtParams.items():
            print("%s: dp_type = %s, dp_number = %d, acl = %s, data_type = %s, min = %s, max = %s" %
                  (name, repr(param.dp_type), param.dp_number, repr(param.acl),
                   str(param.data_type) if param.data_type else "unknown",
                   str(param.min), str(param.max)))

    def _load_from_csv(filename):
        """ Load all supported heat pump parameter definitions from the passed CSV file.

        :param filename: Name of the CSV file with the parameter definitions.
        :type filename: str
        :returns: Dictionary of the supported heat pump parameters:
            ::

                { "Parameter name": HtParam(dp_type=..., dp_number=...,
                                            acl=..., data_type=...,
                                            min=..., max=...),
                  # ...
                }

        :rtype: ``dict``
        """
        params = {}
        with open(filename) as f:
            reader = csv.reader(f, delimiter=',', skipinitialspace=True)
            for row in reader:
                # continue for empty rows or comments
                if not row or row[0].startswith('#'):
                    continue
                name, dp_type, dp_number, acl, data_type, min_val, max_val = row
                # convert the data point number into an int
                dp_number = int(dp_number)
                # convert the given data type into the corresponding enum value
                data_type = HtDataTypes.from_str(data_type)
                # convert the minimal value to the expected data type
                min_val = None if min_val == "None" else HtParam.conv_value(min_val, data_type)
                # convert the maximal value to the expected data type
                max_val = None if max_val == "None" else HtParam.conv_value(max_val, data_type)
                # add the parameter definition to the dictionary
                params.update({name: HtParam(dp_type=dp_type, dp_number=dp_number,
                                             acl=acl, data_type=data_type,
                                             min=min_val, max=max_val)})
        return params

    # Dictionary of the supported Heliotherm heat pump parameters
    _params = _load_from_csv(path.join(path.dirname(path.abspath(__file__)), CSV_FILE))


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

# Only for testing: print all supported heat pump parameters
def main():
    HtParams.dump()


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------- #
# Exported symbols
# --------------------------------------------------------------------------------------------- #

__all__ = ["HtDataTypes", "HtParam", "HtParams"]
