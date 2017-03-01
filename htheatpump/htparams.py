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

""" Parameter of the Heliotherm heat pump together with their access command, access rights
    and data type.
"""

#import enum  # only for Python >= 3.4
from utils import Singleton


# --------------------------------------------------------------------------------------------- #
# Helper classes
# --------------------------------------------------------------------------------------------- #

#@enum.unique  # only for Python >= 3.4
#class HtDataTypes(enum.Enum):
class HtDataTypes:
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


class HtParam:
    """ Representation of a specific heat pump parameter.

    :param cmd: The command string.
    :type cmd: str
    :param acl: The access rights (:const:`'r'` = read, :const:`'w'` = write).
    :type acl: str
    :param dtype: The data type, see :class:`htparams.HtDataTypes`.
    :type dtype: HtDataTypes
    :param min: The minimal value (default :const:`None`).
    :type min: int, float or None
    :param max: The maximal value (default :const:`None`).
    :type max: int, float or None
    """

    def __init__(self, cmd, acl, dtype, min=None, max=None):
        self.cmd = cmd
        self.acl = acl
        self.dtype = dtype
        self.min = min
        self.max = max


class HtParamsMeta(type):
    def __contains__(cls, item):
        return item in cls._params
    def __getitem__(cls, key):
        return cls._params[key]
    def __len__(cls):
        return len(cls._params)


# --------------------------------------------------------------------------------------------- #
# Dictionary of all known Heliotherm heat pump parameters
# --------------------------------------------------------------------------------------------- #


class HtParams(Singleton, metaclass=HtParamsMeta):
    """ Dictionary of all known Heliotherm heat pump parameters.
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

    #
    # All known Heliotherm heat pump parameters:
    #
    _params = {
        # ----------------------------------------------------------------------------------------------------------------------------------------
        #  SP-Numbers:
        #
        "Softwareversion"                 :  HtParam(  cmd = "SP,NR=9",    acl = "r-",  dtype = HtDataTypes.INT,    min = None,   max = None    ),
        "Verdichter_Status"               :  HtParam(  cmd = "SP,NR=10",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 11      ),
        "Verdichter laeuft seit"          :  HtParam(  cmd = "SP,NR=11",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 100000  ),
        "Betriebsart"                     :  HtParam(  cmd = "SP,NR=13",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 7       ),
        "HKR Soll_Raum"                   :  HtParam(  cmd = "SP,NR=69",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 10.0,   max = 25.0    ),
        "HKR Aufheiztemp. (K)"            :  HtParam(  cmd = "SP,NR=71",   acl = "r-",  dtype = HtDataTypes.INT,    min = 1,      max = 10      ),
        "HKR Absenktemp. (K)"             :  HtParam(  cmd = "SP,NR=72",   acl = "r-",  dtype = HtDataTypes.INT,    min = -10,    max = -1      ),
        "HKR Heizgrenze"                  :  HtParam(  cmd = "SP,NR=76",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 45      ),
        "HKR RLT Soll_oHG (Heizkurve)"    :  HtParam(  cmd = "SP,NR=80",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 15.0,   max = 40.0    ),
        "HKR RLT Soll_0 (Heizkurve)"      :  HtParam(  cmd = "SP,NR=81",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 20.0,   max = 50.0    ),
        "HKR RLT Soll_uHG (Heizkurve)"    :  HtParam(  cmd = "SP,NR=82",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 25.0,   max = 60.0    ),
        "WW Normaltemp."                  :  HtParam(  cmd = "SP,NR=83",   acl = "r-",  dtype = HtDataTypes.INT,    min = 10,     max = 75      ),
        "WW Minimaltemp."                 :  HtParam(  cmd = "SP,NR=85",   acl = "r-",  dtype = HtDataTypes.INT,    min = 5,      max = 45      ),
        "BSZ Verdichter Betriebsst. WW"   :  HtParam(  cmd = "SP,NR=171",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 100000  ),
        "BSZ Verdichter Betriebsst. HKR"  :  HtParam(  cmd = "SP,NR=172",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 100000  ),
        "BSZ Verdichter Betriebsst. ges"  :  HtParam(  cmd = "SP,NR=173",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 100000  ),
        "MKR2 Aktiviert"                  :  HtParam(  cmd = "SP,NR=222",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 2       ),  # how to interpret?
        "Energiezaehler"                  :  HtParam(  cmd = "SP,NR=263",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 2       ),  # how to interpret?

        #
        # TODO
        #
        # "MKR1 Soll_Raum"                  :  HtParam(  cmd = "SP,NR=200",  acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max
        # "MKR1 Heizgrenze"                 :  HtParam(  cmd = "SP,NR=205",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max
        # "MKR2 Soll_Raum"                  :  HtParam(  cmd = "SP,NR=223",  acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max
        # "MKR2 Heizgrenze"                 :  HtParam(  cmd = "SP,NR=228",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max
        # "Kuehlgrenze"                     :  HtParam(  cmd = "SP,NR=293",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max
        # "MKR1 Betriebsart"                :  HtParam(  cmd = "SP,NR=221",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max
        # "MKR2 Betriebsart"                :  HtParam(  cmd = "SP,NR=244",  acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max

        #
        # ----------------------------------------------------------------------------------------------------------------------------------------
        #  MP-Numbers:
        #
        "Temp. Aussen"                    :  HtParam(  cmd = "MP,NR=0",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -20.0,  max = 40.0    ),
        "Temp. Brauchwasser"              :  HtParam(  cmd = "MP,NR=2",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 70.0    ),
        "Temp. Vorlauf"                   :  HtParam(  cmd = "MP,NR=3",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 70.0    ),
        "Temp. Ruecklauf"                 :  HtParam(  cmd = "MP,NR=4",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 70.0    ),
        "Temp. EQ_Eintritt"               :  HtParam(  cmd = "MP,NR=6",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -20.0,  max = 30.0    ),
        "Temp. EQ_Austritt"               :  HtParam(  cmd = "MP,NR=7",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -20.0,  max = 30.0    ),
        "Temp. Sauggas"                   :  HtParam(  cmd = "MP,NR=9",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -20.0,  max = 30.0    ),
        "Temp. Frischwasser_Istwert"      :  HtParam(  cmd = "MP,NR=11",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 70.0    ),
        "Temp. Verdampfung"               :  HtParam(  cmd = "MP,NR=12",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -50.0,  max = 30.0    ),
        "Temp. Kondensation"              :  HtParam(  cmd = "MP,NR=13",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = -50.0,  max = 60.0    ),
        "Niederdruck (bar)"               :  HtParam(  cmd = "MP,NR=20",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 18.0    ),
        "Hochdruck (bar)"                 :  HtParam(  cmd = "MP,NR=21",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 40.0    ),
        "Heizkreispumpe"                  :  HtParam(  cmd = "MP,NR=22",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "Stoerung"                        :  HtParam(  cmd = "MP,NR=31",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "Frischwasserpumpe"               :  HtParam(  cmd = "MP,NR=50",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 100     ),  # probably 0 - 100%
        "Verdichteranforderung"           :  HtParam(  cmd = "MP,NR=56",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 5       ),
        "HKR_Sollwert"                    :  HtParam(  cmd = "MP,NR=57",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0.0,    max = 50.0    ),
        "EQ Pumpe (Ventilator)"           :  HtParam(  cmd = "MP,NR=24",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "Warmwasservorrang"               :  HtParam(  cmd = "MP,NR=25",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "Zirkulationspumpe WW"            :  HtParam(  cmd = "MP,NR=29",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "Verdichter"                      :  HtParam(  cmd = "MP,NR=30",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        "FWS Stroemungsschalter"          :  HtParam(  cmd = "MP,NR=38",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),

        #
        # TODO
        #
        # "Temp. Pufferspeicher"            :  HtParam(  cmd = "MP,NR=5",    acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max
        # "Temp. Heissgas"                  :  HtParam(  cmd = "MP,NR=15",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max
        # "Pufferladepumpe"                 :  HtParam(  cmd = "MP,NR=23",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        # "Vierwegeventil Luft"             :  HtParam(  cmd = "MP,NR=32",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
        # "WMZ_Heizung (kWh)"               :  HtParam(  cmd = "MP,NR=52",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "Stromz_Heizung (kWh)"            :  HtParam(  cmd = "MP,NR=53",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "WMZ_Brauchwasser (kWh)"          :  HtParam(  cmd = "MP,NR=54",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "Stromz_Brauchwasser (kWh)"       :  HtParam(  cmd = "MP,NR=55",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "Stromz_Gesamt (kWh)"             :  HtParam(  cmd = "MP,NR=75",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "Stromz_Leistung (W)"             :  HtParam(  cmd = "MP,NR=83",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "WMZ_Gesamt (kWh)"                :  HtParam(  cmd = "MP,NR=84",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "WMZ_Durchfluss"                  :  HtParam(  cmd = "MP,NR=85",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max (type?)
        # "WMZ_Leistung (kW)"               :  HtParam(  cmd = "MP,NR=89",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "Verdichter Soll-n(%)"            :  HtParam(  cmd = "MP,NR=47",   acl = "r-",  dtype = HtDataTypes.INT,    min = 0,      max = 0       ),  # TODO min, max
        # "COP"                             :  HtParam(  cmd = "MP,NR=98",   acl = "r-",  dtype = HtDataTypes.FLOAT,  min = 0,      max = 0       ),  # TODO min, max (type?)
        # "EVU_Sperre"                      :  HtParam(  cmd = "MP,NR=37",   acl = "r-",  dtype = HtDataTypes.BOOL,   min = 0,      max = 1       ),
    }
    #
    #  Most of the upper access commands of the Heliotherm heat pump parameters were sniffed from the Heliotherm home control Windows application
    #    (http://homecontrol.heliotherm.com) during a refresh!


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

# Only for testing: print all known parameters
def main():
    for paramName, param in HtParams.items():
        print("%s: cmd = %s, acl = %s, dtype = %s, min = %s, max = %s" %
              (repr(paramName), repr(param.cmd), repr(param.acl),
              str(param.dtype) if param.dtype else "unknown",
              str(param.min), str(param.max)))


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------------------------- #
# Exported symbols
# --------------------------------------------------------------------------------------------- #

__all__ = ["HtDataTypes", "HtParam", "HtParams"]
