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

""" Command line tool to validate all supported parameters of a Heliotherm heat pump.

    Example:

    .. code-block:: shell

       $ python3 htvalidate.py --device /dev/ttyUSB1 --baudrate 9600
       ... TODO ...
"""

import sys
import argparse
import textwrap
import re
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParam, HtParams
from timeit import default_timer as timer
import logging
_logger = logging.getLogger(__name__)


# Main program
def main():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''\
            Command shell tool to validate all supported parameters of a Heliotherm heat pump.

            Example:

              $ python3 %(prog)s --device /dev/ttyUSB1 --baudrate 9600
              ... TODO ...
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
        "-t", "--time",
        action = "store_true",
        help = "measure the execution time")

    parser.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help = "increase output verbosity by activating debug-logging")

    args = parser.parse_args()

    # activate debug-logging in verbose mode
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

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

        print("============================= parameter validation starts ==============================")
        for name, param in HtParams.items():
            s = {}
            try:
                hp.send_request(param.cmd())
                resp = hp.read_response()

                # TODO: validate data point type (SP, MP) and number!

                m = re.match("^{},.*NAME=([^,]+).*VAL=([^,]+).*MAX=([^,]+).*MIN=([^,]+).*$".format(param.cmd()), resp)
                if not m:
                    print("{!r}: \u001b[31mInvalid response [{!r}]\u001b[0m".format(name, resp))
                    continue

                dp_name = m.group(1).strip()
                if dp_name != name:
                    s['name'] = "\u001b[31m{!r}\u001b[0m".format(dp_name)
                else:
                    s['name'] = "{!r}".format(dp_name)

                try:
                    dp_max = HtParam.from_str(m.group(3), param.data_type)
                    if dp_max != param.max:
                        s['max'] = "max=\u001b[31m{!s}\u001b[0m".format(dp_max)
                    else:
                        s['max'] = "max={!s}".format(dp_max)
                except ValueError:
                    s['max'] = "\u001b[31mmax={!s}\u001b[0m".format(dp_max)

                try:
                    dp_min = HtParam.from_str(m.group(4), param.data_type)
                    if dp_min != param.min:
                        s['min'] = "min=\u001b[31m{!s}\u001b[0m".format(dp_min)
                    else:
                        s['min'] = "min={!s}".format(dp_min)
                except ValueError:
                    s['min'] = "\u001b[31mmin={!s}\u001b[0m".format(dp_min)

                print("{}: dp_type={!r}, dp_number={!s}, data_type={!s}, {}, {}".format(s['name'],
                                                                                        param.dp_type,
                                                                                        param.dp_number,
                                                                                        param.data_type,
                                                                                        s['min'],
                                                                                        s['max']))
            except Exception as e:
                print("{!r}: \u001b[31mQuery failed: {!s}\u001b[0m".format(name, e))
                continue

    except Exception as e:
        print("\u001b[31m{!s}\u001b[0m".format(e))
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
