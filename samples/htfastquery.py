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

""" TODO doc
Command line tool to fast query for parameters of the Heliotherm heat pump.

    Example:

    .. code-block:: shell

       $ python3 htquery.py --device /dev/ttyUSB1 "Temp. Aussen" "Stoerung"
       Stoerung    : False
       Temp. Aussen: 5.0

       $ python3 htquery.py --json "Temp. Aussen" "Stoerung"
       {
           "Stoerung": false,
           "Temp. Aussen": 3.2
       }
"""

import sys
import argparse
import textwrap
import json
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtDataTypes, HtParams
from timeit import default_timer as timer
import logging
_logger = logging.getLogger(__name__)


# Main program
def main():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''TODO doc\
            Command line tool to fast query for parameters of the Heliotherm heat pump.

            Example:

              $ python3 %(prog)s --device /dev/ttyUSB1 "Temp. Aussen" "Stoerung"
              Stoerung    : False
              Temp. Aussen: 5.0
            '''),
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''\
            DISCLAIMER
            ----------

              Please note that any incorrect or careless usage of this program as well as
              errors in the implementation can damage your heat pump!

              Therefore, the author does not provide any guarantee or warranty concerning
              to correctness, functionality or performance and does not accept any liability
              for damage caused by this program or mentioned information.

              Thus, use it on your own risk!
            ''') + "\r\n")

    parser.add_argument(
        "-d", "--device",
        default = "/dev/ttyUSB0",
        type = str,
        help = "the serial device on which the heat pump is connected, default: %(default)s")

    parser.add_argument(
        "-b", "--baudrate",
        default = 115200,
        type = int,
        # the supported baudrates of the Heliotherm heat pump (HP08S10W-WEB):
        choices = [9600, 19200, 38400, 57600, 115200],
        help = "baudrate of the serial connection (same as configured on the heat pump), default: %(default)s")

    parser.add_argument(
        "-j", "--json",
        action = "store_true",
        help = "output will be in JSON format")

    parser.add_argument(
        "--boolasint",
        action = "store_true",
        help = "boolean values will be stored as '0' and '1'")

    parser.add_argument(
        "-t", "--time",
        action = "store_true",
        help = "measure the execution time")

    parser.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help = "increase output verbosity by activating logging")

    parser.add_argument(
        "name",
        type = str,
        nargs = '*',
        help = "parameter name(s) to query for (as defined in htparams.csv) or omit to query for "
               "all known parameters representing a MP data point")

    args = parser.parse_args()

    # activate logging with level DEBUG in verbose mode
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    hp = HtHeatpump(args.device, baudrate=args.baudrate)
    start = timer()
    try:
        hp.open_connection()
        hp.login()

        rid = hp.get_serial_number()
        if args.verbose:
            _logger.info("connected successfully to heat pump with serial number {:d}".format(rid))
        ver = hp.get_version()
        if args.verbose:
            _logger.info("software version = {} ({:d})".format(ver[0], ver[1]))

        # fast query for the given parameter(s)
        values = hp.fast_query(*args.name)
        for name, val in values.items():
            if args.boolasint and HtParams[name].data_type == HtDataTypes.BOOL:
                values[name] = 1 if val else 0

        # print the current value(s) of the retrieved parameter(s)
        if args.json:
            print(json.dumps(values, indent=4, sort_keys=True))
        else:
            if len(values) > 1:
                for name in sorted(values.keys()):
                    print("{:{width}} [{},{:02d}]: {}".format(name,
                                                              HtParams[name].dp_type,
                                                              HtParams[name].dp_number,
                                                              values[name],
                                                              width=len(max(values.keys(), key=len))))
            elif len(values) == 1:
                print(next(iter(values.values())))

    except Exception as ex:
        _logger.error(ex)
        sys.exit(1)
    finally:
        hp.logout()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()
    end = timer()

    # print execution time only if desired
    if args.time:
        print("execution time: {:.2f} sec".format(end - start))

    sys.exit(0)


if __name__ == "__main__":
    main()
