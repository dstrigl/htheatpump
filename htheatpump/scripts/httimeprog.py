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

""" Command line tool to query for the time programs of the heat pump.

    Example:

    .. code-block:: shell

       $ python3 httimeprog.py --device /dev/ttyUSB1 --baudrate 9600
       idx=0, name='Warmwasser', ead=7, nos=2, ste=15, nod=7, entries=[]
       idx=1, name='Zirkulationspumpe', ead=7, nos=2, ste=15, nod=7, entries=[]
       idx=2, name='Heizung', ead=7, nos=3, ste=15, nod=7, entries=[]
       idx=3, name='Mischer 1', ead=7, nos=3, ste=15, nod=7, entries=[]
       idx=4, name='Mischer 2', ead=7, nos=3, ste=15, nod=7, entries=[]
"""

import argparse
import csv
import json
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
            Command line tool to query for the time programs of the heat pump.

            Example:

              $ python3 httimeprog.py --device /dev/ttyUSB1 --baudrate 9600
              idx=0, name='Warmwasser', ead=7, nos=2, ste=15, nod=7, entries=[]
              idx=1, name='Zirkulationspumpe', ead=7, nos=2, ste=15, nod=7, entries=[]
              idx=2, name='Heizung', ead=7, nos=3, ste=15, nod=7, entries=[]
              idx=3, name='Mischer 1', ead=7, nos=3, ste=15, nod=7, entries=[]
              idx=4, name='Mischer 2', ead=7, nos=3, ste=15, nod=7, entries=[]
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
        "-t", "--time", action="store_true", help="measure the execution time"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase output verbosity by activating logging",
    )

    parser.add_argument(
        "-j",
        "--json",
        type=str,
        help="write the time program entries to the specified JSON file",
    )

    parser.add_argument(
        "-c",
        "--csv",
        type=str,
        help="write the time program entries to the specified CSV file",
    )

    parser.add_argument(
        "index",
        type=int,
        nargs="?",
        help="time program index to query for (omit to get the list of available time programs of the heat pump)",
    )

    parser.add_argument(
        "day",
        type=int,
        nargs="?",
        help="number of day of a specific time program to query for",
    )

    parser.add_argument(
        "entry",
        type=int,
        nargs="?",
        help="number of entry of a specific day of a time program to query for",
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

        if args.index is not None and args.day is not None and args.entry is not None:
            # query for a specific time program entry of the heat pump
            with Timer() as timer:
                time_prog_entry = hp.get_time_prog_entry(
                    args.index, args.day, args.entry
                )
            exec_time = timer.elapsed
            print(
                "[idx={:d}, day={:d}, entry={:d}]: {!s}".format(
                    args.index, args.day, args.entry, time_prog_entry
                )
            )

            # write time program entry to JSON file
            if args.json:
                with open(args.json, "w") as jsonfile:
                    json.dump(
                        time_prog_entry.as_json(), jsonfile, indent=4, sort_keys=True
                    )
            # write time program entry to CSV file
            if args.csv:
                with open(args.csv, "w") as csvfile:
                    csvfile.write(
                        "# idx={:d}, day={:d}, entry={:d}".format(
                            args.index, args.day, args.entry
                        )
                    )
                    fieldnames = ["state", "start", "end"]
                    writer = csv.DictWriter(
                        csvfile, delimiter=",", fieldnames=fieldnames
                    )
                    writer.writeheader()
                    writer.writerow(time_prog_entry.as_json())

        elif args.index is not None and args.day is not None:
            # query for the entries of a specific day of a time program of the heat pump
            with Timer() as timer:
                time_prog = hp.get_time_prog(args.index, with_entries=True)
            exec_time = timer.elapsed
            print("[idx={:d}]: {!s}".format(args.index, time_prog))
            day_entries = time_prog.entries_of_day(args.day)
            for num in range(len(day_entries)):
                print(
                    "[day={:d}, entry={:d}]: {!s}".format(
                        args.day, num, day_entries[num]
                    )
                )

            # write time program entries of the specified day to JSON file
            if args.json:
                with open(args.json, "w") as jsonfile:
                    json.dump(
                        [entry.as_json() for entry in day_entries],
                        jsonfile,
                        indent=4,
                        sort_keys=True,
                    )
            # write time program entries of the specified day to CSV file
            if args.csv:
                with open(args.csv, "w") as csvfile:
                    csvfile.write("# {!s}\n".format(time_prog))
                    fieldnames = ["day", "entry", "state", "start", "end"]
                    writer = csv.DictWriter(
                        csvfile, delimiter=",", fieldnames=fieldnames
                    )
                    writer.writeheader()
                    for num in range(len(day_entries)):
                        row = {"day": args.day, "entry": num}
                        row.update(day_entries[num].as_json())
                        writer.writerow(row)

        elif args.index is not None:
            # query for the entries of a specific time program of the heat pump
            with Timer() as timer:
                time_prog = hp.get_time_prog(args.index, with_entries=True)
            exec_time = timer.elapsed
            print("[idx={:d}]: {!s}".format(args.index, time_prog))
            for (day, num) in [
                (day, num)
                for day in range(time_prog.number_of_days)
                for num in range(time_prog.entries_a_day)
            ]:
                entry = time_prog.entry(day, num)
                print("[day={:d}, entry={:d}]: {!s}".format(day, num, entry))

            # write time program entries to JSON file
            if args.json:
                with open(args.json, "w") as jsonfile:
                    json.dump(time_prog.as_json(), jsonfile, indent=4, sort_keys=True)
            # write time program entries to CSV file
            if args.csv:
                with open(args.csv, "w") as csvfile:
                    csvfile.write("# {!s}\n".format(time_prog))
                    fieldnames = ["day", "entry", "state", "start", "end"]
                    writer = csv.DictWriter(
                        csvfile, delimiter=",", fieldnames=fieldnames
                    )
                    writer.writeheader()
                    for (day, num) in [
                        (day, num)
                        for day in range(time_prog.number_of_days)
                        for num in range(time_prog.entries_a_day)
                    ]:
                        row = {"day": day, "entry": num}
                        row.update(time_prog.entry(day, num).as_json())
                        writer.writerow(row)

        else:
            # query for all available time programs of the heat pump
            with Timer() as timer:
                time_progs = hp.get_time_progs()
            exec_time = timer.elapsed
            for time_prog in time_progs:
                print("{!s}".format(time_prog))

            keys = ["index", "name", "ead", "nos", "ste", "nod"]
            data = []
            for time_prog in time_progs:
                data.append(time_prog.as_json(with_entries=False))
            # write time programs to JSON file
            if args.json:
                with open(args.json, "w") as jsonfile:
                    json.dump(data, jsonfile, indent=4, sort_keys=True)
            # write time programs to CSV file
            if args.csv:
                with open(args.csv, "w") as csvfile:
                    writer = csv.DictWriter(csvfile, delimiter=",", fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)

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
