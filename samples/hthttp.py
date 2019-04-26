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

""" Simple HTTP server which provides the possibility to access the Heliotherm heat pump via URL requests.

    Supported URL requests:

      * http://ip:port/datetime/sync
          synchronize the system time of the heat pump with the current time
      * http://ip:port/datetime
          query for the current system time of the heat pump
      * http://ip:port/faultlist/last
          query for the last fault message of the heat pump
      * http://ip:port/faultlist
          query for the whole fault list of the heat pump
      * http://ip:port/timeprog
          query for the list of available time programs of the heat pump
      * http://ip:port/timeprog/<idx>
          query for a specific time program of the heat pump
      * http://ip:port/param/?Param1&Param2&Param3=Value&Param4=Value ...
          query and/or set specific parameter values of the heat pump
      * http://ip:port/param/
          query for all "known" parameter values of the heat pump
      * http://ip:port/
          query for some properties of the connected heat pump

      The result in the HTTP response is given in JSON format.

    Example:

    .. code-block:: shell

       $ python3 hthttp.py start --device /dev/ttyUSB1 --ip 192.168.11.91 --port 8081
       hthttp.py started with PID 1099

       $ tail /tmp/hthttp-daemon.log
       [2019-01-18 20:24:20,379][INFO    ] Serial<id=0x764857f0, open=True>(port='/dev/ttyUSB0', baudrate=115200, ...
       [2019-01-18 20:24:20,389][INFO    ] login successfully
       192.168.11.127 - - [18/Jan/2019 20:24:20] "GET /faultlist/last HTTP/1.1" 200 -
       [2019-01-18 20:24:20,414][INFO    ] {
         "datetime": "2018-09-07T09:14:02",
         "error": 65534,
         "index": 61,
         "message": "Keine Stoerung"
       }
       [2019-01-18 20:24:20,425][INFO    ] logout successfully

       $ python3 hthttp.py stop
"""

import argparse
import textwrap
import sys
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse as urlparse
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtDataTypes, HtParams
from daemon import Daemon
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class HttpGetException(Exception):
    def __init__(self, response_code, message):
        super().__init__(self, message)
        self._response_code = response_code

    @property
    def response_code(self):
        return self._response_code


class HttpGetHandler(BaseHTTPRequestHandler):

    DATETIME_SYNC_PATH  = r"^\/datetime\/sync\/?$"
    DATETIME_PATH       = r"^\/datetime\/?$"
    FAULTLIST_LAST_PATH = r"^\/faultlist\/last\/?$"
    FAULTLIST_PATH      = r"^\/faultlist\/?$"
    TIMEPROG_PATH       = r"^\/timeprog\/(\d+)\/?$"
    TIMEPROGS_PATH      = r"^\/timeprog\/?$"
    PARAM_PATH          = r"^\/param\/?$"

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        _logger.info(parsed_path.path.lower())

        result = None
        try:
            hp.reconnect()
            hp.login()

            if re.match(self.DATETIME_SYNC_PATH, parsed_path.path.lower()):
                # synchronize the system time of the heat pump with the current time
                dt, _ = hp.set_date_time(datetime.now())
                result = {"datetime": dt.isoformat()}
                _logger.debug(dt.isoformat())

            elif re.match(self.DATETIME_PATH, parsed_path.path.lower()):
                # return the current system time of the heat pump
                dt, _ = hp.get_date_time()
                result = {"datetime": dt.isoformat()}
                _logger.debug(dt.isoformat())

            elif re.match(self.FAULTLIST_LAST_PATH, parsed_path.path.lower()):
                # query for the last fault message of the heat pump
                idx, err, dt, msg = hp.get_last_fault()
                result = {"index": idx, "error": err, "datetime": dt.isoformat(), "message": msg}
                _logger.debug("#{:d} [{}]: {:d}, {}".format(idx, dt.isoformat(), err, msg))

            elif re.match(self.FAULTLIST_PATH, parsed_path.path.lower()):
                # query for the whole fault list of the heat pump
                result = []
                for entry in hp.get_fault_list():
                    entry.update({"datetime": entry["datetime"].isoformat()})  # convert datetime dict entry to string
                    result.append(entry)
                    _logger.debug("#{:03d} [{}]: {:05d}, {}".format(
                        entry["index"], entry["datetime"], entry["error"], entry["message"]))

            elif re.match(self.TIMEPROG_PATH, parsed_path.path.lower()):
                # query for a specific time program of the heat pump (including all time program entries)
                m = re.match(self.TIMEPROG_PATH, parsed_path.path.lower())
                try:
                    idx = int(m.group(1))
                except ValueError as ex:
                    # for an invalid time program index: HTTP response 400 = Bad Request
                    raise HttpGetException(400, str(ex))
                time_prog = hp.get_time_prog(idx, with_entries=True)
                result = time_prog.as_json()
                _logger.debug("{}".format(time_prog))

            elif re.match(self.TIMEPROGS_PATH, parsed_path.path.lower()):
                # query for the list of available time programs of the heat pump
                time_progs = hp.get_time_progs()
                result = []
                for time_prog in time_progs:
                    result.append(time_prog.as_json(with_entries=False))
                    _logger.debug("{}".format(time_prog))

            elif re.match(self.PARAM_PATH, parsed_path.path.lower()):
                # query and/or set parameter values of the heat pump
                qsl = urlparse.parse_qsl(parsed_path.query, keep_blank_values=True)
                _logger.info(qsl)
                result = {}
                if not qsl:
                    # query for all "known" parameters
                    for name in HtParams.keys():
                        value = hp.get_param(name)
                        # convert boolean values to 0/1 (if desired)
                        if args.boolasint and HtParams[name].data_type == HtDataTypes.BOOL:
                            value = 1 if value else 0
                        result.update({name: value})
                        _logger.debug("{}: {}".format(name, value))
                else:
                    # query and/or set specific parameter values of the heat pump
                    params = {}
                    try:
                        # check if all requested/given parameter names are known and all passed values are valid
                        for query in qsl:
                            name, value = query  # value is '' (blank string) for non given values
                            # try to convert the passed value (if given) to the specific data type
                            value = HtParams[name].from_str(value) if value else None
                            params.update({name: value})
                    except KeyError as ex:
                        # for unknown parameter name: HTTP response 404 = Not Found
                        raise HttpGetException(404, str(ex))
                    except ValueError as ex:
                        # for an invalid parameter value: HTTP response 400 = Bad Request
                        raise HttpGetException(400, str(ex))
                    # query/set all requested parameter values
                    for name, value in params.items():
                        if value is None:
                            # query for the value of the requested parameter
                            value = hp.get_param(name)
                        else:
                            # set the parameter of the heat pump to the passed value
                            value = hp.set_param(name, value)
                        # convert boolean values to 0/1 (if desired)
                        if args.boolasint and HtParams[name].data_type == HtDataTypes.BOOL:
                            value = 1 if value else 0
                        result.update({name: value})
                        _logger.debug("{}: {}".format(name, value))

            elif parsed_path.path.lower() == "/":
                # query for some properties of the connected heat pump
                property_id = hp.get_param("Liegenschaft") if "Liegenschaft" in HtParams else 0
                serial_number = hp.get_serial_number()
                software_version, _ = hp.get_version()
                dt, _ = hp.get_date_time()
                result = {"property_id": property_id,
                          "serial_number": serial_number,
                          "software_version": software_version,
                          "datetime": dt.isoformat(),
                          }
                _logger.debug("property_id: {}, serial_number: {}, software_version: {}, datetime: {}".format(
                    property_id, serial_number, software_version, dt.isoformat()))

            else:
                # for an invalid url request: HTTP response 400 = Bad Request
                raise HttpGetException(400, "invalid url request {!r}".format(parsed_path.path.lower()))

        except HttpGetException as ex:
            _logger.exception(ex)
            self.send_response(ex.response_code, str(ex))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        except Exception as ex:
            _logger.exception(ex)
            # HTTP response 500 = Internal Server Error
            self.send_response(500, str(ex))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        else:
            # HTTP response 200 = OK
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            message = json.dumps(result, indent=2, sort_keys=True)
            _logger.info(message)
            self.wfile.write(bytes(message, "utf8"))

        finally:
            hp.logout()  # logout() should not fail!


class HtHttpDaemon(Daemon):
    def run(self):
        _logger.info("=== HtHttpDaemon.run() {}".format("=" * 100))
        global hp
        try:
            hp = HtHeatpump(args.device, baudrate=args.baudrate)
            hp.open_connection()
            hp.login()
            rid = hp.get_serial_number()
            _logger.info("Connected successfully to heat pump with serial number: {:d}".format(rid))
            ver = hp.get_version()
            _logger.info("Software version: {} ({:d})".format(ver[0], ver[1]))
            hp.logout()
            server = HTTPServer((args.ip, args.port), HttpGetHandler)
            _logger.info("Starting server at: {}".format(server.server_address))
            server.serve_forever()  # start the server and wait for requests
        except Exception as ex:
            _logger.exception(ex)
            sys.exit(2)
        finally:
            hp.logout()  # try to logout for an ordinary cancellation (if possible)
            hp.close_connection()


# Main program
def main():
    parser = argparse.ArgumentParser(
        description = textwrap.dedent('''\
            Simple HTTP server which provides the possibility to access the Heliotherm heat pump via URL requests.

            Supported URL requests:

              * http://ip:port/datetime/sync
                  synchronize the system time of the heat pump with the current time
              * http://ip:port/datetime
                  query for the current system time of the heat pump
              * http://ip:port/faultlist/last
                  query for the last fault message of the heat pump
              * http://ip:port/faultlist
                  query for the whole fault list of the heat pump
              * http://ip:port/timeprog
                  query for the list of available time programs of the heat pump
              * http://ip:port/timeprog/<idx>
                  query for a specific time program of the heat pump
              * http://ip:port/param/?Param1&Param2&Param3=Value&Param4=Value ...
                  query and/or set specific parameter values of the heat pump
              * http://ip:port/param/
                  query for all "known" parameter values of the heat pump
              * http://ip:port/
                  query for some properties of the connected heat pump

              The result in the HTTP response is given in JSON format.

            Example:

              $ python3 %(prog)s start --device /dev/ttyUSB1 --ip 192.168.11.91 --port 8081
              hthttp.py started with PID 1099

              $ tail /tmp/hthttp-daemon.log
              ...

              $ python3 %(prog)s stop
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
        "cmd",
        type = str.lower,
        choices = ["start", "stop", "restart", "status"],
        help = "command to be executed for the HTTP server daemon")

    parser.add_argument(
        "-ip", "--ip",
        default = "192.168.11.90",
        type = str,
        help = "IP address of the HTTP server, default: %(default)s")

    parser.add_argument(
        "-p", "--port",
        default = 8080,
        type = int,
        help = "port number of the HTTP server, default: %(default)s")

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
        "--boolasint",
        action = "store_true",
        help = "boolean values will be returned as '0' and '1'")

    parser.add_argument(
        "-v", "--verbose",
        action = "store_true",
        help = "increase output verbosity by activating logging")

    global args
    args = parser.parse_args()

    # activate logging with level DEBUG in verbose mode
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(asctime)s][%(levelname)-8s][%(name)s|%(funcName)s]: %(message)s")

    daemon = HtHttpDaemon("/tmp/hthttp-daemon.pid", stdout="/tmp/hthttp-daemon.log", stderr="/tmp/hthttp-daemon.log")
    if args.cmd == "start":
        daemon.start()
    elif args.cmd == "stop":
        daemon.stop()
    elif args.cmd == "restart":
        daemon.restart()
    elif args.cmd == "status":
        daemon.status()
    else:
        sys.stderr.write("unknown command\n")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
