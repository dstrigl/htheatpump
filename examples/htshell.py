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

""" Command line program to send commands/requests to the Heliotherm heat pump.

    Example:

    .. code-block:: console

        pi@raspberrypi:~/htheatpump $ python3 htshell.py "SP,NR=13"
        'SP,NR=13,ID=13,NAME=Betriebsart,LEN=1,TP=0,BIT=0,VAL=1,MAX=7,MIN=0,WR=1,US=1'
        query took 1.97 seconds

"""

import os, sys
sys.path.insert(0, os.path.abspath('../htheatpump'))

import sys
from htheatpump import HtHeatpump
from timeit import default_timer as timer


# Main program
def main():
    if len(sys.argv) != 2:
        print("usage: %s <cmd>" % sys.argv[0])
        sys.exit(1)

    hp = HtHeatpump("/dev/ttyUSB0")
    start = timer()
    try:
        hp.open_connection()
        hp.login()
        # print(repr(sys.argv[1]))
        hp.send_request(sys.argv[1])
        resp = hp.read_response()
        print(repr(resp))
    finally:
        hp.logout()  # try to logout for a ordinary cancellation (if possible)
        hp.close_connection()
    end = timer()
    print("query took %.2f seconds" % (end - start))

if __name__ == "__main__":
    main()
