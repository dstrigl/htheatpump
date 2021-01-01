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

""" Protocol constants and functions for the Heliotherm heat pump communication. """


# ------------------------------------------------------------------------------------------------------------------- #
# Protocol constants
# ------------------------------------------------------------------------------------------------------------------- #

MAX_CMD_LENGTH = 253  # 253 = 255 - 1 byte for header - 1 byte for trailer

REQUEST_HEADER = b"\x02\xfd\xd0\xe0\x00\x00"
RESPONSE_HEADER_LEN = 6  # response header length
RESPONSE_HEADER = {
    #
    # NOTE:
    # =====
    # It seems that there is some inconsistency in the way how the heat pump replies to requests.
    # Depending on the received header (the first 6 bytes) we have to correct the payload length for
    #   the checksum computation, so that the received checksum fits with the computed one.
    # Additionally, for some replies the checksum seems to be totally ignored, because the received
    #   checksum is always zero (0x0), regardless of the content.
    #
    # This behavior will be handled in the following lines. See also function HtHeatpump.read_response().
    # normal response header with answer
    b"\x02\xfd\xe0\xd0\x00\x00": {
        "payload_len": lambda payload_len: payload_len,  # no payload length correction necessary
        # method to calculate the checksum of the response:
        "checksum": lambda header, payload_len, payload: calc_checksum(
            header + bytes([payload_len]) + payload
        ),
    },
    # response header for some of the "MR" command (HtHeatpump.fast_query) answers
    #   for this kind of answers the payload length must be corrected (for the checksum computation)
    #     so that the received checksum fits with the computed one
    #   observed on: HP08S10W-WEB, SW 3.0.20
    b"\x02\xfd\xe0\xd0\x01\x00": {
        "payload_len": lambda payload_len: payload_len - 1,  # payload length correction
        # method to calculate the checksum of the response:
        "checksum": lambda header, payload_len, payload: calc_checksum(
            header + bytes([payload_len]) + payload
        ),
    },
    # response header with answer
    #   for error messages (e.g. "ERR,INVALID IDX") and some "MR" command (HtHeatpump.fast_query) answers
    #   for this kind of answers the payload length must be corrected (for the checksum computation)
    #     so that the received checksum fits with the computed one
    #   observed on: HP08S10W-WEB, SW 3.0.20
    b"\x02\xfd\xe0\xd0\x02\x00": {
        "payload_len": lambda payload_len: payload_len - 2,  # payload length correction
        # method to calculate the checksum of the response:
        "checksum": lambda header, payload_len, payload: calc_checksum(
            header + bytes([payload_len]) + payload
        ),
    },
    # response header with answer
    #   when receiving an answer from the heat pump with this header the checksum is always 0x0 (don't ask me why!)
    #   observed on: HP08S10W-WEB, SW 3.0.20 for parameter requests ("SP"/"MP" commands)
    b"\x02\xfd\xe0\xd0\x04\x00": {
        "payload_len": lambda payload_len: payload_len,  # no payload length correction necessary
        # we don't know why, but for this kind of responses the checksum is always 0x0:
        "checksum": lambda header, payload_len, payload: 0x00,
    },
    # response header with answer
    #   when receiving an answer from the heat pump with this header the checksum is always 0x0 (don't ask me why!)
    #   observed on: HP10S12W-WEB, SW 3.0.8 for parameter requests ("SP"/"MP" commands)
    b"\x02\xfd\xe0\xd0\x08\x00": {
        "payload_len": lambda payload_len: payload_len,  # no payload length correction necessary
        # we don't know why, but for this kind of responses the checksum is always 0x0:
        "checksum": lambda header, payload_len, payload: 0x00,
    },
}


# special commands of the heat pump:
# ----------------------------------
#
LOGIN_CMD = r"LIN"  # login command
LOGIN_RESP = r"^OK"
LOGOUT_CMD = r"LOUT"  # logout command
LOGOUT_RESP = r"^OK"
RID_CMD = r"RID"  # query for the manufacturer's serial number
RID_RESP = r"^RID,(\d+)$"  # e.g. '~RID,123456;\r\n'
VERSION_CMD = r"SP,NR=9"  # query for the software version of the heat pump
VERSION_RESP = r"^SP,NR=9,.*NAME=([^,]+).*VAL=([^,]+).*$"  # e.g. 'SP,NR=9,ID=9,NAME=3.0.20,...,VAL=2321,...'
CLK_CMD = (
    r"CLK",  # get/set the current date and time of the heat pump
    r"CLK,DA={:02d}.{:02d}.{:02d},TI={:02d}:{:02d}:{:02d},WD={:d}",
)
CLK_RESP = (
    r"^CLK"  # answer for the current date and time of the heat pump
    r",DA=(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d\d)"  # date, e.g. '26.11.15'
    r",TI=([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"  # time, e.g. '21:28:57'
    r",WD=([1-7])$"
)  # weekday 1-7 (Monday through Sunday)
ALC_CMD = r"ALC"  # query for the last fault message of the heat pump
ALC_RESP = (
    r"^AA,(\d+),(\d+)"  # fault list index and error code (?)
    r",(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d\d)"  # date, e.g. '14.09.14'
    r"-([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"  # time, e.g. '11:52:08'
    r",(.*)$"
)  # error message, e.g. 'EQ_Spreizung'
ALS_CMD = r"ALS"  # query for the fault list size of the heat pump
ALS_RESP = r"^SUM=(\d+)$"  # e.g. 'SUM=2757'
AR_CMD = r"AR"  # query for specific entries of the fault list
AR_RESP = (
    r"^AA,(\d+),(\d+)"  # fault list index and error code (?)
    r",(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d\d)"  # date, e.g. '14.09.14'
    r"-([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"  # time, e.g. '11:52:08'
    r",(.*)$"
)  # error message, e.g. 'EQ_Spreizung'
MR_CMD = r"MR"  # fast query for several MP data point values
MR_RESP = r"^MA,(\d+),([^,]+),(\d+)$"  # MP data point number, value and ?; e.g. 'MA,0,-3.4,17'
PRL_CMD = r"PRL"  # query for the time programs of the heat pump
PRL_RESP = (
    r"^SUM=(\d+)$",  # e.g. 'SUM=5'
    r"^PRI{:d},.*NAME=([^,]+).*EAD=([^,]+).*NOS=([^,]+).*STE=([^,]+).*NOD=([^,]+).*$",
)  # e.g. 'PRI0,...'
PRI_CMD = r"PRI{:d}"  # query for a specific time program of the heat pump
PRI_RESP = r"^PRI{:d},.*NAME=([^,]+).*EAD=([^,]+).*NOS=([^,]+).*STE=([^,]+).*NOD=([^,]+).*$"  # e.g. 'PRI2,NAME=..'
PRD_CMD = (
    r"PRD{:d}"  # query for the entries of a specific time program of the heat pump
)
PRD_RESP = (
    r"^PRI{:d},*NAME=([^,]+).*EAD=([^,]+).*NOS=([^,]+).*STE=([^,]+).*NOD=([^,]+).*$",  # e.g. 'PRI0,...'
    r"^PRE,.*PR={:d},.*DAY={:d},.*EV={:d},.*ST=(\d+),"  # e.g. 'PRE,PR=0,DAY=3,EV=1,ST=1,...'
    r".*BEG=(\d?\d:\d?\d),.*END=(\d?\d:\d?\d).*$",
)  # '...BEG=03:30,END=22:00'
PRE_CMD = (
    r"PRE,PR={:d},DAY={:d},EV={:d}",  # get/set a specific time program entry of the heat pump
    r"PRE,PR={:d},DAY={:d},EV={:d},ST={:d},BEG={},END={}",
)
PRE_RESP = (
    r"^PRE,.*PR={:d},.*DAY={:d},.*EV={:d},.*ST=(\d+),"  # e.g. 'PRE,PR=2,DAY=5,EV=4,ST=1,...'
    r".*BEG=(\d?\d:\d?\d),.*END=(\d?\d:\d?\d).*$"
)  # '...BEG=13:30,END=14:45'


# ------------------------------------------------------------------------------------------------------------------- #
# Protocol functions
# ------------------------------------------------------------------------------------------------------------------- #


def calc_checksum(s: bytes) -> int:
    """Function that calculates the checksum of a provided bytes array.

    :param s: Byte array from which the checksum should be computed.
    :type s: bytes
    :returns: The computed checksum as ``int``.
    :rtype: ``int``
    """
    assert isinstance(s, bytes)
    checksum = 0x0
    for i in range(len(s)):
        databyte = s[i]
        checksum ^= databyte
        databyte = (databyte << 1) & 0xFF
        checksum ^= databyte
    return checksum


def verify_checksum(s: bytes) -> bool:
    """Verify if the provided bytes array is terminated with a valid checksum.

    :param s: The byte array including the checksum.
    :type s: bytes
    :returns: :const:`True` if valid, :const:`False` otherwise.
    :rtype: ``bool``
    :raises ValueError:
        Will be raised for an invalid byte array with length less than 2 bytes.
    """
    assert isinstance(s, bytes)
    if len(s) < 2:
        raise ValueError(
            "the provided array of bytes needs to be at least 2 bytes long"
        )
    return (
        calc_checksum(s[:-1]) == s[-1]
    )  # is the last byte of the array the correct checksum?


def add_checksum(s: bytes) -> bytes:
    """Add a checksum at the end of the provided bytes array.

    :param s: The provided byte array.
    :type s: bytes
    :returns: Byte array with the added checksum.
    :rtype: ``bytes``
    :raises ValueError:
        Will be raised for an invalid byte array with length less than 1 byte.
    """
    assert isinstance(s, bytes)
    if len(s) < 1:
        raise ValueError("the provided array of bytes needs to be at least 1 byte long")
    return s + bytes(
        [calc_checksum(s)]
    )  # append the checksum at the end of the bytes array


def create_request(cmd: str) -> bytes:
    """Create a specified request command for the heat pump.

    :param cmd: The command string.
    :type cmd: str
    :returns: The request string for the specified command as byte array.
    :rtype: ``bytes``
    :raises ValueError:
        Will be raised for an invalid byte array with length greater than 253 byte.
    """
    assert isinstance(cmd, str)
    if len(cmd) > MAX_CMD_LENGTH:
        raise ValueError("command must be lesser than 254 characters")
    cmd = "~" + cmd + ";"  # add header '~' and trailer ';'
    return add_checksum(REQUEST_HEADER + bytes([len(cmd)]) + cmd.encode("ascii"))
