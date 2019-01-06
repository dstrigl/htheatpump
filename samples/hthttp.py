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
from daemon import Daemon
from datetime import datetime
import json
import sys
#import logging


class HttpGetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)

        hp.login()
        result = {}
        print("[{}]".format(datetime.now().isoformat()), parsed_path.path.lower())
        if parsed_path.path.lower() == "/datetime":
            dt, _ = hp.set_date_time(datetime.now())
            result.update({"datetime": dt.isoformat()})
            #print("[{}]".format(datetime.now().isoformat()), dt.isoformat())
        elif parsed_path.path.lower() == "/faultlist/last":
            # query for the last fault message of the heat pump
            idx, err, dt, msg = hp.get_last_fault()
            result.update({idx: {"error": err, "datetime": dt.isoformat(), "message": msg}})
            #print("[{}]".format(datetime.now().isoformat()),
            #      "#{:d} [{}]: {:d}, {}".format(idx, dt.isoformat(), err, msg))
        elif parsed_path.path.lower() == "/faultlist":
            # query for the whole fault list of the heat pump
            fault_lst = hp.get_fault_list()
            for idx, err in fault_lst.items():
                err.update({"datetime": err["datetime"].isoformat()})
                result.update({idx: err})
                #print("[{}]".format(datetime.now().isoformat()),
                #      "#{:03d} [{}]: {:05d}, {}".format(idx, err["datetime"], err["error"], err["message"]))
        elif parsed_path.path.lower() == "/":
            qsl = urlparse.parse_qsl(parsed_path.query, keep_blank_values=True)
            print("[{}]".format(datetime.now().isoformat()), qsl)
            if not qsl:
                for name in HtParams.keys():
                    value = hp.get_param(name)
                    result.update({name: value})
                    #print("[{}]".format(datetime.now().isoformat()), "{}: {}".format(name, value))
            else:
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
                    result.update({name: value})
                    #print("[{}]".format(datetime.now().isoformat()), "{}: {}".format(name, value))
        hp.logout()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        message = json.dumps(result, indent=2, sort_keys=True)
        print("[{}]".format(datetime.now().isoformat()), message)
        self.wfile.write(bytes(message, "utf8"))
        return


class HtHttpDaemon(Daemon):
    def run(self):
        #logging.basicConfig(level=logging.INFO)
        global hp
        hp = HtHeatpump("/dev/ttyUSB0", baudrate=115200)
        hp.open_connection()
        hp.login()
        rid = hp.get_serial_number()
        print("[{}]".format(datetime.now().isoformat()),
              "Connected successfully to heat pump with serial number: {:d}".format(rid))
        ver = hp.get_version()
        print("[{}]".format(datetime.now().isoformat()),
              "Software version: {} ({:d})".format(ver[0], ver[1]))
        hp.logout()
        server = HTTPServer(("192.168.11.90", 8080), HttpGetHandler)
        print("[{}]".format(datetime.now().isoformat()),
              "Starting server at: {}".format(server.server_address))
        server.serve_forever()
        hp.close_connection()


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

def main():
    daemon = HtHttpDaemon("/tmp/hthttp-daemon.pid",
                          stdout="/tmp/hthttp-daemon.log",
                          stderr="/tmp/hthttp-daemon.log")
    if len(sys.argv) == 2:
        cmd = sys.argv[1].lower()
        if cmd == "start":
            daemon.start()
        elif cmd == "stop":
            daemon.stop()
        elif cmd == "restart":
            daemon.restart()
        elif cmd == "status":
            daemon.status()
        else:
            sys.stderr.write("unknown command\n")
            sys.exit(2)
        sys.exit(0)
    else:
        sys.stderr.write("usage: {} start|stop|restart|status\n".format(sys.argv[0]))
        sys.exit(2)


if __name__ == "__main__":
    main()
