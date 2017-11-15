#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2017  Daniel Strigl

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

""" This module is responsible for the communication with the Heliotherm heat pump.
"""

from htheatpump.htparams import HtParam, HtParams
#from timeit import default_timer as timer

#import sys
import serial
import time
import re
import datetime
# import pprint


# --------------------------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------------------------- #

import logging
_logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------------------------- #

_serial_timeout = 5
""" Serial timeout value in seconds; normally no need to change it. """
_login_retries = 2
""" Maximum number of retries for a login attempt; 1 regular try + :const:`_login_retries` retries.
"""


# --------------------------------------------------------------------------------------------- #
# Protocol constants
# --------------------------------------------------------------------------------------------- #

REQUEST_HEADER = b"\x02\xfd\xd0\xe0\x00\x00"
RESPONSE_HEADER_LEN = 6
RESPONSE_HEADER = {
    b"\x02\xfd\xe0\xd0\x00\x00" : None,  # checksum has to be computed!
    # on HP08S10W-WEB, SW 3.0.20
    b"\x02\xfd\xe0\xd0\x04\x00" : 0x00,  # checksum seems to be fixed 0x0, but why?
    # on HP10S12W-WEB, SW 3.0.8
    b"\x02\xfd\xe0\xd0\x08\x00" : 0x00,  # @Kilian; another response header with fixed checksum?!
}

# special commands of the heat pump; the request and response of this commands differ from the
#   normal parameter requests defined in htparams.py
LOGIN_CMD    = "LIN"                                                              # login command
LOGIN_RESP   = "OK"
LOGOUT_CMD   = "LOUT"                                                            # logout command
LOGOUT_RESP  = "OK"
RID_CMD      = "RID"          # returns the manufacturer's serial number, e.g. "~RID,123456;\r\n"
RID_RESP     = "^RID,(\d+)$"
VERSION_CMD  = "SP,NR=9"                          # returns the software version of the heat pump
VERSION_RESP = "^SP,NR=9,.*NAME=([^,]+).*VAL=([^,]+).*$"
CLK_CMD      = ("CLK",                       # get/set the current date and time of the heat pump
                "CLK,DA={:02d}.{:02d}.{:02d},TI={:02d}:{:02d}:{:02d},WD={:d}")
CLK_RESP     = ("^CLK"
                ",DA=(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d{2})"   # date, e.g. '26.11.15'
                ",TI=([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"                # time, e.g. '21:28:57'
                ",WD=([1-7])$")                             # weekday 1-7 (Monday through Sunday)
ALC_CMD      = "ALC"                            # returns the last fault message of the heat pump
ALC_RESP     = ("^AA,(\d+),(\d+)"                           # fault list index and error code (?)
                ",(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d{2})"      # date, e.g. '14.09.14'
                "-([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"                   # time, e.g. '11:52:08'
                ",(.*)$")                                    # error message, e.g. 'EQ_Spreizung'
ALS_CMD      = "ALS"                               # returns the fault list size of the heat pump
ALS_RESP     = "^SUM=(\d+)$"
AR_CMD       = "AR,{}"                               # returns a specific entry of the fault list
AR_RESP      = ("^AA,(\d+),(\d+)"                           # fault list index and error code (?)
                ",(3[0-1]|[1-2]\d|0[1-9])\.(1[0-2]|0[1-9])\.(\d{2})"      # date, e.g. '14.09.14'
                "-([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)"                   # time, e.g. '11:52:08'
                ",(.*)$")                                    # error message, e.g. 'EQ_Spreizung'


# --------------------------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------------------------- #

def calc_checksum(s):
    """ Function that calculates the checksum of a provided bytes array.

    :param s: Byte array from which the checksum should be computed.
    :type s: bytes
    :returns: The computed checksum as ``int``.
    :rtype: ``int``
    """
    checksum = 0x0
    for i in range(0, len(s)):
        databyte = s[i]
        checksum ^= databyte
        databyte = (databyte << 1) & 0xff
        checksum ^= databyte
    return checksum


def verify_checksum(s):
    """ Verify if the provided bytes array is terminated with a valid checksum.

    :param s: The byte array including the checksum.
    :type s: bytes
    :returns: :const:`True` if valid, :const:`False` otherwise.
    :rtype: ``bool``
    """
    if len(s) < 2:
        raise ValueError("the provided array of bytes needs to be at least 2 bytes long")
    return calc_checksum(s[:-1]) == s[-1]  # is the last byte of the array the correct checksum?


def add_checksum(s):
    """ Adds a checksum at the end of the provided bytes array.

    :param s: The provided byte array.
    :type s: bytes
    :returns: Byte array with the added checksum.
    :rtype: ``bytes``
    """
    if len(s) < 1:
        raise ValueError("the provided array of bytes needs to be at least 1 byte long")
    return s + bytes([calc_checksum(s)])  # append the checksum at the end of the bytes array


def create_request(cmd):
    """ Create a specified request command for the heat pump.

    :param cmd: The command string.
    :type cmd: str
    :returns: The request string for the specified command as byte array.
    :rtype: ``bytes``
    """
    if len(cmd) > 253:  # = 255 - 1 byte for header - 1 byte for trailer
        raise ValueError("command must be lesser than 254 characters")
    cmd = "~" + cmd + ";"  # add header '~' and trailer ';'
    return add_checksum(REQUEST_HEADER + bytes([len(cmd)]) + cmd.encode("ascii"))


# --------------------------------------------------------------------------------------------- #
# HtHeatpump class
# --------------------------------------------------------------------------------------------- #

class HtHeatpump:
    """ Object which encapsulates the communication with the Heliotherm heat pump.

    :param device: The serial device to attach to (e.g. :data:`/dev/ttyUSB0`).
    :type device: str
    :param baudrate: The baud rate to use for the serial device (optional).
    :type baudrate: int
    :param bytesize: The bytesize of the serial messages (optional).
    :type bytesize: int
    :param parity: Which kind of parity to use (optional).
    :type parity: str
    :param stopbits: The number of stop bits to use (optional).
    :type stopbits: float
    :param xonxoff: Software flow control enabled (optional).
    :type xonxoff: bool
    :param rtscts: Hardware flow control (RTS/CTS) enabled (optional).
    :type rtscts: bool
    :param dsrdtr: Hardware flow control (DSR/DTR) enabled (optional).
    :type dsrdtr: bool

    Example::

        hp = HtHeatpump("/dev/ttyUSB0", baudrate=9600)
        try:
            hp.open_connection()
            hp.login()
            # query for the outdoor temperature
            temp = hp.get_param("Temp. Aussen")
            print(temp)
            # ...
        finally:
            hp.logout()  # try to logout for an ordinary cancellation (if possible)
            hp.close_connection()
    """

    _ser_settings = None
    """ The serial device settings (device, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr)
        as ``dict``.
    """

    _ser = None
    """ The object which does the serial talking.
    """

    def __init__(self, device, **kwargs):
        # store the serial settings for later connection establishment
        self._ser_settings = { 'device': device }
        self._ser_settings.update(kwargs)

    def __del__(self):
        # close the connection if still established
        if self._ser and self._ser.is_open:
            self._ser.close()

    def open_connection(self):
        """ Opens the serial connection with the defined settings.

        :raises IOError:
            When the serial connection is already open.
        :raises ValueError:
            Will be raised when parameter are out of range, e.g. baudrate, bytesize.
        :raises SerialException:
            In case the device can not be found or can not be configured.
        """
        if self._ser:
            raise IOError("serial connection already open")
        device = self._ser_settings.get('device', '/dev/ttyUSB0')
        baudrate = self._ser_settings.get('baudrate', 115200)
        bytesize = self._ser_settings.get('bytesize', serial.EIGHTBITS)
        parity = self._ser_settings.get('parity', serial.PARITY_NONE)
        stopbits = self._ser_settings.get('stopbits', serial.STOPBITS_ONE)
        xonxoff = self._ser_settings.get('xonxoff', True)
        rtscts = self._ser_settings.get('rtscts', False)
        dsrdtr = self._ser_settings.get('dsrdtr', False)
        # open the serial connection (must fit with the settings on the heat pump!)
        self._ser = serial.Serial(device,
                                  baudrate=baudrate,
                                  bytesize=bytesize,
                                  parity=parity,
                                  stopbits=stopbits,
                                  xonxoff=xonxoff,
                                  rtscts=rtscts,
                                  dsrdtr=dsrdtr,
                                  timeout=_serial_timeout)
        _logger.info(self._ser)  # log serial connection properties

    def close_connection(self):
        """ Closes the serial connection.
        """
        if self._ser and self._ser.is_open:
            self._ser.close()
            self._ser = None
            # we wait for 1 sec, as it should be avoided to reopen the connection to fast
            time.sleep(1)

    @property
    def is_open(self):
        """  Returns the state of the serial port, whether it’s open or not.

        :returns: The state of the serial port as ``bool``.
        :rtype: ``bool``
        """
        return self._ser and self._ser.is_open

    def send_request(self, cmd):
        """ Sends a request to the heat pump.

        :param cmd: Command to send to the heat pump.
        :type cmd: str
        :raises IOError:
            Will be raised when the serial connection is not open.
        """
        if not self._ser:
            raise IOError("serial connection not open")
        req = create_request(cmd)
        _logger.debug("send request: [{}]".format(req))
        self._ser.write(req)

    def read_response(self):
        """ Reads a response from the heat pump.

        :returns: The returned response of the heat pump as ``str``.
        :rtype: ``str``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            (or unknown) response (e.g. broken data stream, invalid checksum).

        .. note::

            **There is a little bit strange behavior how the heat pump sometimes replies on some
            requests:**

            A response from the heat pump normally consists of the following header
            :data:`b"\\x02\\xfd\\xe0\\xd0\\x00\\x00"` together with the payload and a
            computed checksum. But sometimes the heat pump replies with a different header
            (:data:`b"\\x02\\xfd\\xe0\\xd0\\x04\\x00"` or :data:`b"\\x02\\xfd\\xe0\\xd0\\x08\\x00"`)
            together with the payload and a *fixed* value of :data:`0x0` for the checksum.

            We have no idea about the reason for this behavior. But after analysing the
            communication between the `Heliotherm home control <http://homecontrol.heliotherm.com/>`_
            Windows application and the heat pump, which simply accepts this kind of responses,
            we also decided to handle it as a valid response.
        """
        if not self._ser:
            raise IOError("serial connection not open")
        # read the header of the response message
        header = self._ser.read(RESPONSE_HEADER_LEN)
        if not header:
            raise IOError("data stream broken during reading response header")
        elif header not in RESPONSE_HEADER:
            raise IOError("wrong response header for a request [{}]".format(header))
        # read the length of the following payload
        payload_len = self._ser.read(1)
        if not payload_len:
            raise IOError("data stream broken during reading payload length")
        # read the payload itself
        payload = self._ser.read(payload_len[0])
        if not payload or len(payload) < payload_len[0]:
            raise IOError("data stream broken during reading payload")
        # read the checksum and verify the validity of the response
        checksum = self._ser.read(1)
        if not checksum:
            raise IOError("data stream broken during reading checksum")
        comp_checksum = RESPONSE_HEADER[header]
        if comp_checksum is None:
            # compute the checksum over header and payload
            comp_checksum = calc_checksum(header + payload_len + payload)
        else:  # log about response with unlikely (but handled) header!
            _logger.info("FYI: received response with \"unlikely\" header, but handled normally (checksum={})"
                         .format(hex(checksum[0])))
        if checksum[0] != comp_checksum:
            raise IOError("received response has an invalid checksum [{}]".format(hex(checksum[0])))
        # debug log of the received response
        _logger.debug("received response: [{}]".format(header + payload_len + payload + checksum))
        _logger.debug("  header = {}".format(header))
        _logger.debug("  payload = {}".format(payload))
        _logger.debug("  checksum = {}".format(hex(checksum[0])))
        # extract the relevant data from the payload (without header '~' and trailer ';\r\n')
        m = re.match("^~([^;]*);\r\n$", payload.decode("ascii"))
        if not m:
            raise IOError("failed to extract response data from payload [{}]".format(payload))
        return m.group(1)

    def login(self, max_retries=_login_retries):
        """ Log in the heat pump.

        :param max_retries: Maximal number of retries for a successful login. One regular try
            plus :const:`max_retries` retries.
        :type max_retries: int
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # we try to login the heat pump for several times
        success = False
        retry = 0
        while not success and retry <= max_retries:
            # send LOGIN request to the heat pump
            self.send_request(LOGIN_CMD)
            # ... and wait for the response
            try:
                resp = self.read_response()
                if resp == LOGIN_RESP:
                    success = True
                else:
                    raise IOError("invalid response for LOGIN command [{}]".format(resp))
            except Exception as e:
                _logger.warning("login try {:d} failed: {!s}".format(retry, e))
                retry += 1
                # try a reconnect, maybe this will help ;-)
                self.close_connection()
                self.open_connection()
        if not success:
            _logger.error("login failed after {:d} retries".format(retry))
            raise IOError("login failed after {:d} retries".format(retry))
        _logger.info("login successfully")

    def logout(self):
        """ Log out from the heat pump session.
        """
        try:
            # send LOGOUT request to the heat pump
            self.send_request(LOGOUT_CMD)
            # ... and wait for the response
            resp = self.read_response()
            if resp != LOGOUT_RESP:
                raise IOError("invalid response for LOGOUT command [{}]".format(resp))
            _logger.info("logout successfully")
        except Exception as e:
            # just a warning, because it's possible that we can continue without any further problems
            _logger.warning("logout failed: {!s}".format(e))
            # raise  # logout() should not fail!

    def get_serial_number(self):
        """ Query for the manufacturer's serial number of the heat pump.

        :returns: The manufacturer's serial number of the heat pump as ``int`` (e.g. :data:`123456`).
        :rtype: ``int``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # send RID request to the heat pump
        self.send_request(RID_CMD)
        # ... and wait for the response
        try:
            resp = self.read_response()  # e.g. "RID,123456"
            m = re.match(RID_RESP, resp)
            if not m:
                raise IOError("invalid response for RID command [{}]".format(resp))
            rid = int(m.group(1))
            _logger.debug("manufacturer's serial number = {:d}".format(rid))
            return rid  # return the received manufacturer's serial number as an int
        except Exception as e:
            _logger.error("query for manufacturer's serial number failed: {!s}".format(e))
            raise

    def get_version(self):
        """ Query for the software version of the heat pump.

        :returns: The software version of the heat pump as a tuple with 2 elements.
            The first element inside the returned tuple represents the software
            version as a readable string in a common version number format
            (e.g. :data:`"3.0.20"`). The second element (probably) contains a numerical
            representation as ``int`` of the software version returned by the heat pump.
            For example:
            ::

                ( "3.0.20", 2321 )

        :rtype: ``tuple`` ( str, int )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # send request command to the heat pump
        self.send_request(VERSION_CMD)
        # ... and wait for the response
        try:
            resp = self.read_response()
            # search for pattern "NAME=..." and "VAL=..." inside the response string;
            #   the textual representation of the version is encoded in the 'NAME',
            #   e.g. "SP,NR=9,ID=9,NAME=3.0.20,LEN=4,TP=0,BIT=0,VAL=2321,MAX=0,MIN=0,WR=0,US=1"
            #   => software version = 3.0.20
            m = re.match(VERSION_RESP, resp)
            if not m:
                raise IOError("invalid response for query of the software version [{}]".format(resp))
            ver = ( m.group(1).strip(), int(m.group(2)) )
            _logger.debug("software version = {} ({:d})".format(ver[0], ver[1]))
            return ver
        except Exception as e:
            _logger.error("query for software version failed: {!s}".format(e))
            raise

    def get_date_time(self):
        """ Read the current date and time of the heat pump.

        :returns: The current date and time of the heat pump as a tuple with 2 elements, where
            the first element is of type :class:`datetime.datetime` which represents the current
            date and time while the second element is the corresponding weekday in form of an
            ``int`` between 1 and 7, inclusive (Monday through Sunday). For example:
            ::

                ( datetime.datetime(...), 2 )  # 2 = Tuesday

        :rtype: ``tuple`` ( datetime.datetime, int )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # send CLK request to the heat pump
        self.send_request(CLK_CMD[0])
        # ... and wait for the response
        try:
            resp = self.read_response()  # e.g. "CLK,DA=26.11.15,TI=21:28:57,WD=4"
            m = re.match(CLK_RESP, resp)
            if not m:
                raise IOError("invalid response for CLK command [{}]".format(resp))
            year = 2000 + int(m.group(3))
            tmp = [ int(g) for g in m.group(2, 1, 4, 5, 6) ]  # month, day, hour, min, sec
            weekday = int(m.group(7))  # weekday 1-7 (Monday through Sunday)
            # create datetime object
            dt = datetime.datetime(year, *tmp)
            _logger.debug("datetime = {}, weekday = {:d}".format(dt.isoformat(), weekday))
            return (dt, weekday)  # return the heat pump's date and time as a datetime object
        except Exception as e:
            _logger.error("query for date and time failed: {!s}".format(e))
            raise

    def set_date_time(self, dt=None):
        """ Set the current date and time of the heat pump.

        :param dt: The date and time to set. If :const:`None` current date and time
            of the host will be used.
        :type dt: datetime.datetime
        :returns: A 2-elements tuple composed of a :class:`datetime.datetime` which represents
            the sent date and time and an ``int`` between 1 and 7, inclusive, for the corresponding
            weekday (Monday through Sunday).
        :rtype: ``tuple`` ( datetime.datetime, int )
        :raises TypeError:
            Raised for an invalid type of argument ``dt``. Must be :const:`None` or
            of type :class:`datetime.datetime`.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        if dt is None:
            dt = datetime.datetime.now()
        elif not isinstance(dt, datetime.datetime):
            raise TypeError("argument 'dt' must be None or of type datetime.datetime")
        # create CLK set command
        cmd = CLK_CMD[1].format(dt.day, dt.month, dt.year - 2000, dt.hour, dt.minute, dt.second, dt.isoweekday())
        # send command to the heat pump
        self.send_request(cmd)
        # ... and wait for the response
        try:
            resp = self.read_response()  # e.g. "CLK,DA=26.11.15,TI=21:28:57,WD=4"
            m = re.match(CLK_RESP, resp)
            if not m:
                raise IOError("invalid response for CLK command [{}]".format(resp))
            year = 2000 + int(m.group(3))
            tmp = [ int(g) for g in m.group(2, 1, 4, 5, 6) ]  # month, day, hour, min, sec
            weekday = int(m.group(7))  # weekday 1-7 (Monday through Sunday)
            # create datetime object
            dt = datetime.datetime(year, *tmp)
            _logger.debug("datetime = {}, weekday = {:d}".format(dt.isoformat(), weekday))
            return (dt, weekday)  # return the heat pump's date and time as a datetime object
        except Exception as e:
            _logger.error("set of date and time failed: {!s}".format(e))
            raise

    def get_last_fault(self):
        """ Query for the last fault message of the heat pump.

        :returns:
            The last fault message of the heat pump as a tuple with 4 elements.
            The first element of the returned tuple represents the index as ``int`` of
            the message inside the fault list. The second element is (probably) the
            the error code as ``int`` defined by Heliotherm. The last two elements of the
            tuple are the date and time when the error occurred (as :class:`datetime.datetime`)
            and the error message string itself. For example:
            ::

                ( 29, 20, datetime.datetime(...), "EQ_Spreizung" )

        :rtype: ``tuple`` ( int, int, datetime.datetime, str )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # send ALC request to the heat pump
        self.send_request(ALC_CMD)
        # ... and wait for the response
        try:
            resp = self.read_response()  # e.g. "AA,29,20,14.09.14-11:52:08,EQ_Spreizung"
            m = re.match(ALC_RESP, resp)
            if not m:
                raise IOError("invalid response for ALC command [{}]".format(resp))
            (idx, err) = [ int(g) for g in m.group(1, 2) ]  # fault list index, error code (?)
            year = 2000 + int(m.group(5))
            tmp = [ int(g) for g in m.group(4, 3, 6, 7, 8) ]  # month, day, hour, min, sec
            dt = datetime.datetime(year, *tmp)  # create datetime object
            msg = m.group(9).strip()
            _logger.debug("(idx: {:d}, err: {:d})[{}]: {}".format(idx, err, dt.isoformat(), msg))
            return ( idx, err, dt, msg )
        except Exception as e:
            _logger.error("query for last fault message failed: {!s}".format(e))
            raise

    def get_fault_list_size(self):
        """ Query for the fault list size of the heat pump.

        :returns: The size of the fault list as ``int``.
        :rtype: ``int``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        # send ALS request to the heat pump
        self.send_request(ALS_CMD)
        # ... and wait for the response
        try:
            resp = self.read_response()  # e.g. "SUM=2757"
            m = re.match(ALS_RESP, resp)
            if not m:
                raise IOError("invalid response for ALS command [{}]".format(resp))
            size = int(m.group(1))
            _logger.debug("fault list size = {:d}".format(size))
            return size
        except Exception as e:
            _logger.error("query for fault list size failed: {!s}".format(e))
            raise

    def get_fault_list(self, *args):
        """ Query for the fault list of the heat pump.

        :param args: The list of entry numbers requested from the fault list;
            if :const:`None` all entries are returned.
        :returns: The requested entries of the fault list as ``dict``, e.g.:
            ::

                { 29: { "error"   : 20,                     # error code
                        "datetime": datetime.datetime(...), # date and time of the entry
                        "message" : "EQ_Spreizung",         # error message
                      },
                  # ...
                }

        :rtype: ``dict``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        if not args:
            args = range(0, self.get_fault_list_size())
        # send AR request to the heat pump
        cmd = AR_CMD.format(','.join(map(lambda i: str(i), args)))
        self.send_request(cmd)
        # ... and wait for the response
        try:
            resp = []
            # read all all requested fault list entries
            for _ in args:
                resp.append(self.read_response())  # e.g. "AA,29,20,14.09.14-11:52:08,EQ_Spreizung"
            # extract data (fault list index, error code, date, time and message)
            faults = {}
            for i, r in enumerate(resp):
                m = re.match(AR_RESP, r)
                if not m:
                    raise IOError("invalid response for AR command [{}]".format(resp))
                (idx, err) = [ int(g) for g in m.group(1, 2) ]  # fault list index, error code
                year = 2000 + int(m.group(5))
                tmp = [ int(g) for g in m.group(4, 3, 6, 7, 8) ]  # month, day, hour, min, sec
                dt = datetime.datetime(year, *tmp)  # create datetime object from extracted data
                msg = m.group(9).strip()
                _logger.debug("(idx: {:03d}, err: {:05d})[{}]: {}".format(idx, err, dt.isoformat(), msg))
                if idx != args[i]:
                    raise IOError("fault list index doesn't match [{:d}, but should be {:d}]".format(idx, args[i]))
                # add the received fault list entry to the result dict
                faults.update({ idx: { "error"   : err,  # error code
                                       "datetime": dt,   # date and time of the entry
                                       "message" : msg,  # error message
                                       }
                                })
            return faults
        except Exception as e:
            _logger.error("query for fault list failed: {!s}".format(e))
            raise

    def get_param(self, name):
        """ Query for a specific parameter of the heat pump.

        :param name: The parameter name, e.g. :data:`"Betriebsart"`.
        :type name: str
        :returns: Returned value of the requested parameter.
            The type of the returned value is defined by the dictionary
            of supported heat pump parameters in :class:`htparams.HtParams`.
        :rtype: ``str``, ``bool``, ``int`` or ``float``
        :raises: KeyError:
            Will be raised when the parameter definition for the passed parameter is not found.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).

        For example, the following call
        ::

            temp = hp.get_param("Temp. Aussen")

        will return the current measured outdoor temperature in °C.
        """
        #
        # TODO: check received value against limits (min, max) in 'htparams.csv'
        #          and write a warning to the log if it doesn't match
        #
        # find the corresponding definition for the requested parameter
        if name not in HtParams:
            raise KeyError("parameter definition for parameter {!r} not found".format(name))
        param = HtParams[name]
        # send command to the heat pump
        self.send_request(param.cmd())
        # ... and wait for the response
        try:
            resp = self.read_response()
            # search for pattern "VAL=..." inside the response string
            m = re.match("^{},.*VAL=([^,]+).*$".format(param.cmd()), resp)
            if not m:
                raise IOError("invalid response for query of parameter {!r} [{}]".format(name, resp))
            val = m.group(1).strip()
            # convert the returned value (string) to the expected data type
            val = HtParam.from_str(val, param.data_type)
            _logger.debug("{!r} = {!s}".format(name, val))
            return val
        except Exception as e:
            _logger.error("query of parameter {!r} failed: {!s}".format(name, e))
            raise

    def set_param(self, name, val):
        """ Set the value of a specific parameter of the heat pump.

        :param name: The parameter name, e.g. :data:`"Betriebsart"`.
        :type name: str
        :param val: The value to set.
        :type val: ``str``, ``bool``, ``int`` or ``float``
        :returns: Returned value of the parameter set request.
            In case of success this value should be the same as the one
            passed to the function.
            The type of the returned value is defined by the dictionary
            of supported heat pump parameters in :class:`htparams.HtParams`.
        :rtype: ``str``, ``bool``, ``int`` or ``float``
        :raises: KeyError:
            Will be raised when the parameter definition for the passed parameter is not found.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).

        For example, the following call
        ::

            hp.set_param("HKR Soll_Raum", 21.5)

        will set the desired room temperature of the heating circuit to 21.5 °C.
        """
        #
        # TODO: check write access right of the parameter; see 'HtParam.acl'
        # TODO: check passed value against defined limits (min, max) in 'htparams.csv'
        #
        # find the corresponding definition for the requested parameter
        if name not in HtParams:
            raise KeyError("parameter definition for parameter {!r} not found".format(name))
        param = HtParams[name]
        # send command to the heat pump
        val = HtParam.to_str(val, param.data_type)
        self.send_request("{},VAL={}".format(param.cmd(), val))
        # ... and wait for the response
        try:
            resp = self.read_response()
            # search for pattern "VAL=..." inside the response string
            m = re.match("^{},.*VAL=([^,]+).*$".format(param.cmd()), resp)
            if not m:
                raise IOError("invalid response for set parameter {!r} to {!r} [{}]".format(name, val, resp))
            val = m.group(1).strip()
            # convert the returned value (string) to the expected data type
            val = HtParam.from_str(val, param.data_type)
            _logger.debug("{!r} = {!s}".format(name, val))
            return val
        except Exception as e:
            _logger.error("set parameter {!r} failed: {!s}".format(name, e))
            raise

    @property
    def in_error(self):
        """ Query whether the heat pump is malfunctioning.

        :returns: :const:`True` if the heat pump is malfunctioning, :const:`False` otherwise.
        :rtype: ``bool``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        return self.get_param("Stoerung")

    def query(self, params):
        """ Returns a dict of the requested parameters with their retrieved values from the heat pump.

        :param params: List of parameter names to request from the heat pump.
        :type params: list
        :returns: A dict of the requested parameters with their values, e.g.:
            ::

                { "HKR Soll_Raum": 21.0,
                  "Stoerung": False,
                  "Temp. Aussen": 8.8,
                  # ...
                }

        :rtype: ``dict``
        :raises ValueError:
            Will be raised when parameter are out of range, e.g. baudrate, bytesize.
        :raises SerialException:
            In case the device can not be found or can not be configured.
        :raises IOError:
            Will be raised when the login failed or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum) for the requests.
        """
        result = {}
        try:
            self.open_connection()
            self.login()
            rid = self.get_serial_number()
            _logger.info("connected successfully to heat pump with serial number {:d}".format(rid))
            # query for each parameter in the given list
            for p in params:
                result.update({p: self.get_param(p)})
        finally:
            self.logout()  # try to logout for an ordinary cancellation (if possible)
            self.close_connection()
        return result


# --------------------------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------------------------- #

# Only for testing: request for parameter values and print it
#def main():
#    if len(sys.argv) == 2:
#        logging.basicConfig(level=logging.DEBUG)
#    params = sys.argv[1:] if len(sys.argv) > 1 else HtParams.keys()
#    hp = HtHeatpump("/dev/ttyUSB0")
#    start = timer()
#    val = hp.query(params)
#    end = timer()
#    if len(params) > 1:
#        for p in sorted(params):
#            print("{:{width}}: {}".format(p, val[p], width=len(max(params, key=len))))
#    elif len(params) == 1:
#        print(val[params[0]])
#        # pprint.pprint(params)
#    print("query took {:.2f} sec".format(end - start))


#if __name__ == "__main__":
#    main()


# --------------------------------------------------------------------------------------------- #
# Exported symbols
# --------------------------------------------------------------------------------------------- #

__all__ = ["HtHeatpump"]
