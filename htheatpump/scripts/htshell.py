#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2020  Daniel Strigl

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

""" Command line tool to send raw commands to the Heliotherm heat pump.

    Example:

    .. code-block:: shell

       $ python3 htshell.py --device /dev/ttyUSB1 --baudrate 9600 "AR,28,29,30" -r 3
       > 'AR,28,29,30'
       < 'AA,28,19,14.09.14-02:08:56,EQ_Spreizung'
       < 'AA,29,20,14.09.14-11:52:08,EQ_Spreizung'
       < 'AA,30,65534,15.09.14-09:17:12,Keine Stoerung'
"""

import argparse
import logging
import sys
import textwrap

from htheatpump import HtHeatpump
from htheatpump.utils import Timer

_LOGGER = logging.getLogger(__name__)


# Main program
def main():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
            Command shell tool to send raw commands to the Heliotherm heat pump.

            For commands which deliver more than one response from the heat pump
            the expected number of responses can be defined by the argument "-r"
            or "--responses".

            Example:

              $ python3 htshell.py --device /dev/ttyUSB1 "AR,28,29,30" -r 3
              > 'AR,28,29,30'
              < 'AA,28,19,14.09.14-02:08:56,EQ_Spreizung'
              < 'AA,29,20,14.09.14-11:52:08,EQ_Spreizung'
              < 'AA,30,65534,15.09.14-09:17:12,Keine Stoerung'
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            DISCLAIMER
            ----------

              Please note that any incorrect or careless usage of this program as well as
              errors in the implementation can damage your heat pump!

              Therefore, the author does not provide any guarantee or warranty concerning
              to correctness, functionality or performance and does not accept any liability
              for damage caused by this program or mentioned information.

              Thus, use it on your own risk!
            """
        )
        + "\r\n",
    )

    parser.add_argument(
        "-d",
        "--device",
        default="/dev/ttyUSB0",
        type=str,
        help="the serial device on which the heat pump is connected, default: %(default)s",
    )

    parser.add_argument(
        "-b",
        "--baudrate",
        default=115200,
        type=int,
        # the supported baudrates of the Heliotherm heat pump (HP08S10W-WEB):
        choices=[9600, 19200, 38400, 57600, 115200],
        help="baudrate of the serial connection (same as configured on the heat pump), default: %(default)s",
    )

    parser.add_argument(
        "-r",
        "--responses",
        default=1,
        type=int,
        help="number of expected responses for each given command, default: %(default)s",
    )

    parser.add_argument(
        "-t", "--time", action="store_true", help="measure the execution time"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity by activating logging",
    )

    parser.add_argument(
        "cmd",
        type=str,
        nargs="+",
        help="command(s) to send to the heat pump (without the preceding '~' and the trailing ';')",
    )

    args = parser.parse_args()

    # activate logging with level DEBUG in verbose mode
    log_format = "%(asctime)s %(levelname)s [%(name)s|%(funcName)s]: %(message)s"
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.WARNING, format=log_format)

    hp = HtHeatpump(args.device, baudrate=args.baudrate)
    try:
        hp.open_connection()
        hp.login()

        rid = hp.get_serial_number()
        if args.verbose:
            _LOGGER.info(
                "connected successfully to heat pump with serial number %d", rid
            )
        ver = hp.get_version()
        if args.verbose:
            _LOGGER.info("software version = %s (%d)", *ver)

        with Timer() as timer:
            for cmd in args.cmd:
                # write the given command to the heat pump
                print("> {!r}".format(cmd))
                hp.send_request(cmd)
                # and read all expected responses for this command
                for _ in range(args.responses):
                    resp = hp.read_response()
                    print("< {!r}".format(resp))
        exec_time = timer.elapsed

        # print execution time only if desired
        if args.time:
            print("execution time: {:.2f} sec".format(exec_time))

    except Exception as ex:
        _LOGGER.exception(ex)
        sys.exit(1)
    finally:
        hp.logout()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()

    sys.exit(0)


if __name__ == "__main__":
    main()
