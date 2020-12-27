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

import asyncio
import logging
import random
import sys
import time
from timeit import default_timer as timer

from htheatpump import AioHtHeatpump, HtParams

# _LOGGER = logging.getLogger(__name__)


# Main program
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s|%(funcName)s]: %(message)s",
    )

    hp = AioHtHeatpump("/dev/ttyUSB0", baudrate=115200)
    hp.open_connection()
    await hp.login_async()

    rid = await hp.get_serial_number_async()
    print("connected successfully to heat pump with serial number {:d}".format(rid))
    ver = await hp.get_version_async()
    print("software version = {} ({:d})".format(ver[0], ver[1]))

    names = HtParams.of_type("MP").keys()

    t_query = t_fast_query = 0.0
    for i in range(10):
        start = timer()
        values = await hp.query_async(*names)
        t_query += timer() - start
        start = timer()
        values = await hp.fast_query_async(*names)
        t_fast_query += timer() - start
    i += 1
    t_query = t_query / i
    t_fast_query = t_fast_query / i

    print("\n" + "-" * 100)
    print(
        "AioHtHeatpump.query({:d})      execution time: {:.3f} sec".format(
            len(names), t_query
        )
    )
    print(
        "AioHtHeatpump.fast_query({:d}) execution time: {:.3f} sec".format(
            len(names), t_fast_query
        )
    )
    print("-> {:.3f} x faster".format(t_query / t_fast_query))

    while True:
        print("\n" + "-" * 100)
        rand_names = random.sample(sorted(names), random.randint(0, len(names)))
        print("{!s}".format(rand_names))
        # fast query for the given parameter(s)
        values = await hp.fast_query_async(*rand_names)
        # print the current value(s) of the retrieved parameter(s)
        print(
            ", ".join(map(lambda name: "{!r} = {}".format(name, values[name]), values))
        )
        # for name in sorted(values.keys()):
        #    print("{:{width}} [{},{:02d}]: {}".format(name,
        #                                              HtParams[name].dp_type,
        #                                              HtParams[name].dp_number,
        #                                              values[name],
        #                                              width=len(max(values.keys(), key=len))))
        for i in range(5, 0, -1):
            # print(i)
            sys.stdout.write("\rContinue in {:d}s ...".format(i))
            sys.stdout.flush()
            time.sleep(1)
        print("\rContinue in 0s ...")

    await hp.logout_async()  # try to logout for an ordinary cancellation (if possible)
    hp.close_connection()

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
