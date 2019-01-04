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

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse as urlparse
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParams
import json
import logging


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        qsl = urlparse.parse_qsl(parsed_path.query, keep_blank_values=True)
        print(qsl)

        hp.login()
        params = {}
        for query in qsl:
            name, value = query
            if not value:
                # query for the given parameter
                value = hp.get_param(name)
            else:
                # convert the passed value (as string) to the specific data type
                value = HtParams[name].from_str(value)
                # set the parameter of the heat pump to the passed value
                value = hp.set_param(name, value)
            params.update({name: value})
            print("{}: {}".format(name, value))
        hp.logout()
 
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        message = json.dumps(params, indent=2, sort_keys=True)
        self.wfile.write(bytes(message, "utf8"))
        return


# Main program
def main():
    #logging.basicConfig(level=logging.INFO)
    global hp
    hp = HtHeatpump("/dev/ttyUSB0", baudrate=115200)
    hp.open_connection()
    hp.login()
    rid = hp.get_serial_number()
    print("Connected successfully to heat pump with serial number: {:d}".format(rid))
    ver = hp.get_version()
    print("Software version: {} ({:d})".format(ver[0], ver[1]))
    hp.logout()
    server = HTTPServer(("192.168.11.90", 8080), GetHandler)
    print('Starting server at http://localhost:8080, use <Ctrl-C> to stop.')
    server.serve_forever()
    hp.close_connection()


if __name__ == "__main__":
    main()
