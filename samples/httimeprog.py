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

""" Command line tool to query for the time programs of the heat pump.

    Example:

    .. code-block:: shell

       $ python3 httimeprog.py --device /dev/ttyUSB1 --baudrate 9600
       TODO
"""

import sys
import argparse
import textwrap
import json
import csv
import timeit
from htheatpump.htheatpump import HtHeatpump
import logging
_logger = logging.getLogger(__name__)


class Timer:  # TODO move to utils.py?
    def __enter__(self):
        self._start = timeit.default_timer()
        return self

    def __exit__(self, *args):
        self._end = timeit.default_timer()
        self._duration = self._end - self._start

    @property
    def duration(self):
        return self._duration


# Main program
def main():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''\
            Command line tool to query for the time programs of the heat pump.

            Example:

              $ python3 %(prog)s --device /dev/ttyUSB1
              TODO
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
        help = "increase output verbosity by activating logging")

    parser.add_argument(
        "-j", "--json",
        type = str,
        help = "write the time program entries to the specified JSON file")

    parser.add_argument(
        "-c", "--csv",
        type = str,
        help = "write the time program entries to the specified CSV file")

    parser.add_argument(
        "index",
        type = int,
        nargs = '?',
        help = "time program index to query for (omit to get the list of available time programs of the heat pump)")

    args = parser.parse_args()

    # activate logging with level DEBUG in verbose mode
    if args.verbose:  # TODO format="%(asctime)s %(levelname)s [%(name)s] %(message)s" + %(funcName)s
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    hp = HtHeatpump(args.device, baudrate=args.baudrate)
    try:
        hp.open_connection()
        hp.login()

        rid = hp.get_serial_number()
        if args.verbose:
            _logger.info("connected successfully to heat pump with serial number {:d}".format(rid))
        ver = hp.get_version()
        if args.verbose:
            _logger.info("software version = {} ({:d})".format(ver[0], ver[1]))

        if args.index is None:
            # query for all available time programs of the heat pump
            with Timer() as timer:
                time_progs = hp.get_time_progs()
            exec_time = timer.duration
            for time_prog in time_progs:
                print("[idx={:d}]: name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}".format(
                    time_prog["index"], time_prog["name"], time_prog["ead"], time_prog["nos"],
                    time_prog["ste"], time_prog["nod"]))

            # write time programs to JSON file
            if args.json:
                with open(args.json, 'w') as jsonfile:
                    json.dump(time_progs, jsonfile, indent=4, sort_keys=True)
            # write time programs to CSV file
            if args.csv:
                with open(args.csv, 'w') as csvfile:
                    fieldnames = ["index", "name", "ead", "nos", "ste", "nod"]
                    writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldnames)
                    writer.writeheader()
                    for time_prog in time_progs:
                        writer.writerow({n: time_prog[n] for n in fieldnames})

        else:
            # query for the desired time program entries of the heat pump
            with Timer() as timer:
                time_prog = hp.get_time_prog(args.index)
                time_prog_entries = hp.get_time_prog_entries(args.index)
            exec_time = timer.duration
            print("[idx={:d}]: name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}".format(args.index, *time_prog))
            for day in range(len(time_prog_entries)):
                day_entries = time_prog_entries[day]
                for entry in range(len(day_entries)):
                    data = day_entries[entry]
                    print("day={:d}, entry={:d}, state={:d}, begin={:02d}:{:02d}, end={:02d}:{:02d}".format(
                        day, entry, data["state"], *data["begin"], *data["end"]))

            # write time program entries to JSON file
            if args.json:
                data = {n: time_prog[i] for i, n in enumerate(("index", "name", "ead", "nos", "ste", "nod"))}
                data.update({"entries": time_prog_entries})
                with open(args.json, 'w') as jsonfile:
                    json.dump(data, jsonfile, indent=4, sort_keys=True)
            # write time program entries to CSV file
            if args.csv:
                with open(args.csv, 'w') as csvfile:
                    csvfile.write("# idx={:d}, name={!r}, ead={:d}, nos={:d}, ste={:d}, nod={:d}".format(*time_prog))
                    fieldnames = ["index", "name", "ead", "nos", "ste", "nod"]
                    writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldnames)
                    writer.writeheader()
                    for day in range(len(time_prog_entries)):
                        for entry in time_prog_entries[day]:
                            writer.writerow({n: entry[n] for n in fieldnames})

        # print execution time only if desired
        if args.time:
            print("execution time: {:.2f} sec".format(exec_time))

    except Exception as ex:
        _logger.error(ex)
        sys.exit(1)
    finally:
        hp.logout()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()

    sys.exit(0)


if __name__ == "__main__":
    main()
