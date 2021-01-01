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

""" Command line tool to query for parameters of the Heliotherm heat pump the fast way.
    Note: Only parameters representing a "MP" data point are supported!

    Example:

    .. code-block:: shell

       $ python3 htfastquery_async.py --device /dev/ttyUSB1 "Temp. Vorlauf" "Temp. Ruecklauf"
       Temp. Ruecklauf [MP,04]: 25.2
       Temp. Vorlauf   [MP,03]: 25.3

       $ python3 htfastquery_async.py --json "Temp. Vorlauf" "Temp. Ruecklauf"
       {
           "Temp. Ruecklauf": 25.2,
           "Temp. Vorlauf": 25.3
       }
"""

import argparse
import asyncio
import json
import logging
import sys
import textwrap

from htheatpump import AioHtHeatpump, HtDataTypes, HtParams
from htheatpump.utils import Timer

_LOGGER = logging.getLogger(__name__)


# Main program
async def main_async():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
            Command line tool to query for parameters of the Heliotherm heat pump the fast way.
            Note: Only parameters representing a "MP" data point are supported!

            Example:

              $ python3 htfastquery_async.py --device /dev/ttyUSB1 "Temp. Vorlauf" "Temp. Ruecklauf"
              Temp. Ruecklauf [MP,04]: 25.2
              Temp. Vorlauf   [MP,03]: 25.3
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
        "-j", "--json", action="store_true", help="output will be in JSON format"
    )

    parser.add_argument(
        "--bool-as-int",
        action="store_true",
        help="boolean values will be stored as '0' and '1'",
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
        "name",
        type=str,
        nargs="*",
        help="parameter name(s) to query for (as defined in htparams.csv) or omit to query for "
        "all known parameters representing a MP data point",
    )

    args = parser.parse_args()

    # activate logging with level DEBUG in verbose mode
    log_format = "%(asctime)s %(levelname)s [%(name)s|%(funcName)s]: %(message)s"
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.WARNING, format=log_format)

    hp = AioHtHeatpump(args.device, baudrate=args.baudrate)
    try:
        hp.open_connection()
        await hp.login_async()

        rid = await hp.get_serial_number_async()
        if args.verbose:
            _LOGGER.info(
                "connected successfully to heat pump with serial number %d", rid
            )
        ver = await hp.get_version_async()
        if args.verbose:
            _LOGGER.info("software version = %s (%d)", *ver)

        # fast query for the given parameter(s)
        with Timer() as timer:
            values = await hp.fast_query_async(*args.name)
        exec_time = timer.elapsed
        for name, val in values.items():
            if args.bool_as_int and HtParams[name].data_type == HtDataTypes.BOOL:
                values[name] = 1 if val else 0

        # print the current value(s) of the retrieved parameter(s)
        if args.json:
            print(json.dumps(values, indent=4, sort_keys=True))
        else:
            if len(values) > 1:
                for name in sorted(values.keys()):
                    print(
                        "{:{width}} [{},{:02d}]: {}".format(
                            name,
                            HtParams[name].dp_type,
                            HtParams[name].dp_number,
                            values[name],
                            width=len(max(values.keys(), key=len)),
                        )
                    )
            elif len(values) == 1:
                print(next(iter(values.values())))

        # print execution time only if desired
        if args.time:
            print("execution time: {:.2f} sec".format(exec_time))

    except Exception as ex:
        _LOGGER.exception(ex)
        sys.exit(1)
    finally:
        await hp.logout_async()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()

    sys.exit(0)


def main():
    # run the async main application
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
