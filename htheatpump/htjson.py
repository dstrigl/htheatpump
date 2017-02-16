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

""" This module is responsible for writing the actual heat pump parameter values to a JSON file.
"""

import json
import io


# --------------------------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------------------------- #

import logging
_logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------------- #
# HtJson class
# --------------------------------------------------------------------------------------------- #

class HtJson:
    """ Helper class to store the current heat pump parameter values to a JSON file.

    :param filename: The filename to save to.
    :type filename: str
    """

    # name of the JSON file
    _filename = None

    def __init__(self, filename="htvalues.json"):
        self._filename = filename

    def write(self, params):
        """ Writes the actual heat pump parameter values to the JSON file.

        :param params: The parameter values as dict, e.g.:
            ::

                { "Niederdruck (bar)": 13.2,
                  "HKR Soll_Raum": 21.0,
                  "Stoerung": False,
                  # ...
                }
        """
        _logger.debug("write parameter values to JSON file %s:\n%s", repr(self._filename),
                      json.dumps(params, indent=4, sort_keys=True))
        with io.open(self._filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(params, indent=4, sort_keys=True))


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

# Only for testing: write a JSON file with some sample values
def main():
    logging.basicConfig(level=logging.DEBUG)
    # sample values of the Heliotherm heat pump parameters
    values = {
        "Niederdruck (bar)": 13.2,               # [bar]
        "HKR Soll_Raum": 21.0,                   # [°C]
        "Stoerung": False,                       # yes/no
        "Betriebsart": 1,                        # number 0..7
        "Verdichter_Status": 0,                  # number 0..11
        "WW Normaltemp.": 49,                    # [°C]
        "Frischwasserpumpe": 0,                  # number 0..100
        "Verdichteranforderung": 0,              # number 0..5
        "MKR2 Aktiviert": 0,                     # number 0..2
        "HKR Absenktemp. (K)": -3,               # [K] (Kelvin)
        "HKR Heizgrenze": 17,                    # [°C]
        "Temp. Verdampfung": 19.1,               # [°C]
        "Temp. Aussen": 8.8,                     # [°C]
        "HKR RLT Soll_oHG (Heizkurve)": 23.0,    # [°C]
        "Temp. Kondensation": 20.8,              # [°C]
        "Temp. Sauggas": 20.5,                   # [°C]
        "Temp. EQ_Austritt": 15.8,               # [°C]
        "Verdichter laeuft seit": 0,             # [seconds (s)]
        "Temp. Ruecklauf": 21.7,                 # [°C]
        "BSZ Verdichter Betriebsst. HKR": 403,   # [hours (h)]
        "Temp. EQ_Eintritt": 18.7,               # [°C]
        "Temp. Frischwasser_Istwert": 44.1,      # [°C]
        "HKR_Sollwert": 21.9,                    # [°C]
        "Temp. Brauchwasser": 46.5,              # [°C]
        "Energiezaehler": 0,                     # number 0..2
        "HKR Aufheiztemp. (K)": 3,               # [K] (Kelvin)
        "HKR RLT Soll_uHG (Heizkurve)": 30.0,    # [°C]
        "Temp. Vorlauf": 22.0,                   # [°C]
        "Heizkreispumpe": False,                 # on/off
        "BSZ Verdichter Betriebsst. ges": 706,   # [hours (h)]
        "HKR RLT Soll_0 (Heizkurve)": 27.0,      # [°C]
        "WW Minimaltemp.": 10,                   # [°C]
        "BSZ Verdichter Betriebsst. WW": 303,    # [hours (h)]
        "Hochdruck (bar)": 13.9,                 # [bar]
    }
    j = HtJson()
    j.write(values)


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------- #
# Exported symbols
# --------------------------------------------------------------------------------------------- #

__all__ = ["HtJson"]
