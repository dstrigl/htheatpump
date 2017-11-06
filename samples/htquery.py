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

""" Command line tool to query for parameters of the Heliotherm heat pump.

    Example:

    .. code-block:: console

       $ python3 htquery.py --device /dev/ttyUSB1 --baudrate 9600 "Temp. Aussen"
       ... TODO ...
"""

import sys
import argparse
import textwrap
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParams
from timeit import default_timer as timer
import logging
_logger = logging.getLogger(__name__)


# Main program
def main():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''\
            Command line tool to query for parameters of the Heliotherm heat pump.

            Example:

              $ python3 %(prog)s --device /dev/ttyUSB1 "Temp. Aussen"
              ... TODO ...
            '''),
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''\
            DISCLAIMER
            ----------

              Please note that any incorrect or careless usage of this program as well as
              errors in the implementation can damage your heat pump.

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
        "-t", "--time",
        action = "store_true",
        help = "measure the execution time")

    parser.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help = "increase output verbosity by activating debug-logging")

    parser.add_argument(
        "name",
        type = str,
        nargs = '*',
        help = "parameter name(s) to query for (defined in htparams.csv)")

    args = parser.parse_args()

    # activate debug-logging in verbose mode
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
    # if not given, query for all "known" parameters
    params = args.name if args.name else HtParams.keys()

    hp = HtHeatpump(args.device, baudrate=args.baudrate)
    start = timer()
    try:
        hp.open_connection()
        hp.login()

        rid = hp.get_serial_number()
        if args.verbose:
            print("connected successfully to heat pump with serial number {:d}".format(rid))
        ver = hp.get_version()
        if args.verbose:
            print("software version = {} ({:d})".format(ver[0], ver[1]))

        # query for the given parameter(s)
        val = {}
        for p in params:
            val.update({p: hp.get_param(p)})

        # print the current value(s) of determined parameter(s)
        if len(params) > 1:
            for p in sorted(params):
                print("{:{width}}: {}".format(p, val[p], width=len(max(params, key=len))))
        elif len(params) == 1:
            print(val[params[0]])

    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        hp.logout()  # try to logout for a ordinary cancellation (if possible)
        hp.close_connection()
    end = timer()

    # print execution time only if desired
    if args.time:
        print("execution time: {:.2f} sec".format(end - start))

    sys.exit(0)


if __name__ == "__main__":
    main()
