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
      * http://ip:port/faultlist/last
          query for the last fault message of the heat pump
      * http://ip:port/faultlist
          query for the whole fault list of the heat pump
      * http://ip:port/?Param1&Param2&Param3=Value&Param4=Value ...
          query and/or set specific parameter values of the heat pump
      * http://ip:port/
          query for all "known" parameter values of the heat pump

      The result in the HTTP response is given in JSON format.

    Example:

    .. code-block:: shell

       $ python3 hthttp.py start --device /dev/ttyUSB1 --ip 192.168.11.91 --port 8081
       hthttp.py started with PID 2061

       $ python3 hthttp.py stop
"""

import argparse
import textwrap
import sys
import json
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
        self._response_code = response_code
        Exception.__init__(self, message)

    @property
    def response_code(self):
        return self._response_code


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        _logger.info(parsed_path.path.lower())

        result = {}
        try:
            hp.reconnect()
            hp.login()

            if parsed_path.path.lower() in ("/datetime/sync", "/datetime/sync/"):
                # synchronize the system time of the heat pump with the current time
                dt, _ = hp.set_date_time(datetime.now())
                result.update({"datetime": dt.isoformat()})
                _logger.debug(dt.isoformat())

            elif parsed_path.path.lower() in ("/faultlist/last", "/faultlist/last/"):
                # query for the last fault message of the heat pump
                idx, err, dt, msg = hp.get_last_fault()
                result.update({idx: {"error": err, "datetime": dt.isoformat(), "message": msg}})
                _logger.debug("#{:d} [{}]: {:d}, {}".format(idx, dt.isoformat(), err, msg))

            elif parsed_path.path.lower() in ("/faultlist", "/faultlist/"):
                # query for the whole fault list of the heat pump
                fault_lst = hp.get_fault_list()
                for idx, err in fault_lst.items():
                    err.update({"datetime": err["datetime"].isoformat()})
                    result.update({idx: err})
                    _logger.debug("#{:03d} [{}]: {:05d}, {}".format(idx, err["datetime"], err["error"], err["message"]))

            elif parsed_path.path.lower() == "/":
                qsl = urlparse.parse_qsl(parsed_path.query, keep_blank_values=True)
                _logger.info(qsl)
                if not qsl:
                    # query for all "known" parameters
                    for name in HtParams.keys():
                        value = hp.get_param(name)
                        # convert boolean values to 0/1 (if requested)
                        if args.boolasint and HtParams[name].data_type == HtDataTypes.BOOL:
                            value = 1 if value else 0
                        result.update({name: value})
                        _logger.debug("{}: {}".format(name, value))
                else:
                    params = {}
                    try:
                        # check if all requested/given parameter names are known and all passed values are valid
                        for query in qsl:
                            name, value = query  # value = None for parameter requests (non given value)
                            if value:  # for given values (value not None)
                                # try to convert the passed value (as string) to the specific data type
                                value = HtParams[name].from_str(value)
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
                            # query for the value of the given parameter
                            value = hp.get_param(name)
                        else:
                            # set the parameter of the heat pump to the passed value
                            value = hp.set_param(name, value)
                        # convert boolean values to 0/1 (if requested)
                        if args.boolasint and HtParams[name].data_type == HtDataTypes.BOOL:
                            value = 1 if value else 0
                        result.update({name: value})
                        _logger.debug("{}: {}".format(name, value))

            else:
                # for an invalid url request: HTTP response 400 = Bad Request
                raise HttpGetException(400, "invalid url request {!r}".format(parsed_path.path.lower()))

        except HttpGetException as ex:
            _logger.error(ex)
            self.send_response(ex.response_code, str(ex))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
        except Exception as ex:
            _logger.error(ex)
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
            hp.logout()  # should not fail!


class HtHttpDaemon(Daemon):
    def run(self):
        _logger.info("=" * 100)
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
            _logger.error(ex)
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
              * http://ip:port/faultlist/last
                  query for the last fault message of the heat pump
              * http://ip:port/faultlist
                  query for the whole fault list of the heat pump
              * http://ip:port/?Param1&Param2&Param3=Value&Param4=Value ...
                  query and/or set specific parameter values of the heat pump
              * http://ip:port/
                  query for all "known" parameter values of the heat pump

              The result in the HTTP response is given in JSON format.

            Example:

              $ python3 %(prog)s start --device /dev/ttyUSB1 --ip 192.168.11.91 --port 8081
              hthttp.py started with PID 2061

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
    logging.basicConfig(level=level, format="[%(asctime)s][%(levelname)-8s] %(message)s")

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
