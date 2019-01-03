#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse as urlparse
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParams


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
            'CLIENT VALUES:',
            'client_address=%s (%s)' % (self.client_address, self.address_string()),
            'command=%s' % self.command,
            'path=%s' % self.path,
            'real path=%s' % parsed_path.path,
            'query=%s' % parsed_path.query,
            'request_version=%s' % self.request_version,
            '',
            'SERVER VALUES:',
            'server_version=%s' % self.server_version,
            'sys_version=%s' % self.sys_version,
            'protocol_version=%s' % self.protocol_version,
            '',
            'HEADERS RECEIVED:',
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')

        qsl = urlparse.parse_qsl(parsed_path.query)
        param_parts = []
        for query in qsl:
            name, value = query
            # convert the passed value (as string) to the specific data type
            value = HtParams[name].from_str(value)
            # set the parameter of the heat pump to the passed value
            value = hp.set_param(name, value)
            param_parts.append('{} = {}'.format(name, value))
            print('{} = {}'.format(name, value))

        self.send_response(200)
        self.end_headers()
        message = '\r\n'.join(message_parts) + '\r\n' + '\r\n'.join(param_parts)
        self.wfile.write(bytes(message, 'utf8'))
        return


# Main program
def main():
    global hp
    hp = HtHeatpump('/dev/ttyUSB0', baudrate=115200)
    hp.open_connection()
    hp.login()
    rid = hp.get_serial_number()
    print("connected successfully to heat pump with serial number {:d}".format(rid))
    ver = hp.get_version()
    print("software version = {} ({:d})".format(ver[0], ver[1]))
    server = HTTPServer(('192.168.11.90', 8080), GetHandler)
    print('Starting server at http://localhost:8080, use <Ctrl-C> to stop.')
    server.serve_forever()
    #hp.logout()  # try to logout for an ordinary cancellation (if possible)
    #hp.close_connection()


if __name__ == "__main__":
    main()
