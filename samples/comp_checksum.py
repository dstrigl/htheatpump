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

import sys

from htheatpump.protocol import calc_checksum

# header = b"\x02\xfd\xe0\xd0\x00\x00"
header = b"\x02\xfd\xe0\xd0\x01\x00"
# header = b"\x02\xfd\xe0\xd0\x02\x00"
# header = b"\x02\xfd\xe0\xd0\x04\x00"
# header = b"\x02\xfd\xe0\xd0\x08\x00"


# Main program
def main():
    payload = "~" + sys.argv[1] + ";\r\n"
    payload = payload.encode("ascii")
    payload_len = len(payload) - 1
    print(header + bytes([payload_len]) + payload)
    checksum = calc_checksum(header + bytes([payload_len]) + payload)
    print(hex(checksum))


if __name__ == "__main__":
    main()
