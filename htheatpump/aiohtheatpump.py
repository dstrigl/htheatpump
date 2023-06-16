#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  htheatpump - Serial communication module for Heliotherm heat pumps
#  Copyright (C) 2022  Daniel Strigl

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

""" This module provides an asynchronous communication with the Heliotherm heat pump. """

import asyncio
import copy
import datetime
import logging
import re
from typing import Dict, List, Optional, Set, Tuple, Union

import aioserial
import serial

from .htheatpump import HtHeatpump, VerifyAction
from .htparams import HtParams, HtParamValueType
from .httimeprog import TimeProgEntry, TimeProgram
from .protocol import (
    ALC_CMD,
    ALC_RESP,
    ALS_CMD,
    ALS_RESP,
    AR_CMD,
    AR_RESP,
    CLK_CMD,
    CLK_RESP,
    LOGIN_CMD,
    LOGIN_RESP,
    LOGOUT_CMD,
    LOGOUT_RESP,
    MAX_CMD_LENGTH,
    MR_CMD,
    MR_RESP,
    PRD_CMD,
    PRD_RESP,
    PRE_CMD,
    PRE_RESP,
    PRI_CMD,
    PRI_RESP,
    PRL_CMD,
    PRL_RESP,
    RESPONSE_HEADER,
    RESPONSE_HEADER_LEN,
    RID_CMD,
    RID_RESP,
    VERSION_CMD,
    VERSION_RESP,
    create_request,
)

# ------------------------------------------------------------------------------------------------------------------- #
# Logging
# ------------------------------------------------------------------------------------------------------------------- #


_LOGGER = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------- #
# AioHtHeatpump class
# ------------------------------------------------------------------------------------------------------------------- #


class AioHtHeatpump(HtHeatpump):
    """Object which encapsulates the asynchronous communication with the Heliotherm heat pump.

    :param device: The serial device to attach to (e.g. :data:`/dev/ttyUSB0`).
    :type device: str
    :param baudrate: The baud rate to use for the serial device.
    :type baudrate: int
    :param bytesize: The bytesize of the serial messages.
    :type bytesize: int
    :param parity: Which kind of parity to use.
    :type parity: str
    :param stopbits: The number of stop bits to use.
    :type stopbits: float or int
    :param timeout: The read timeout value.
        Default is :attr:`~htheatpump.htheatpump.HtHeatpump.DEFAULT_SERIAL_TIMEOUT`.
    :type timeout: None, float or int
    :param xonxoff: Software flow control enabled.
    :type xonxoff: bool
    :param rtscts: Hardware flow control (RTS/CTS) enabled.
    :type rtscts: bool
    :param write_timeout: The write timeout value.
    :type write_timeout: None, float or int
    :param dsrdtr: Hardware flow control (DSR/DTR) enabled.
    :type dsrdtr: bool
    :param inter_byte_timeout: Inter-character timeout, ``None`` to disable (default).
    :type inter_byte_timeout: None, float or int
    :param exclusive: Exclusive access mode enabled (POSIX only).
    :type exclusive: bool
    :param verify_param_action: Parameter verification actions.
    :type verify_param_action: None or set
    :param verify_param_error: Interpretation of parameter verification failure as error enabled.
    :type verify_param_error: bool
    :param loop: The event loop, ``None`` for the currently running event loop (default).
    :type loop: None or asyncio.AbstractEventLoop
    :param cancel_read_timeout: TODO
    :type cancel_read_timeout: int
    :param cancel_write_timeout: TODO
    :type cancel_write_timeout: int

    Example::

        hp = AioHtHeatpump("/dev/ttyUSB0", baudrate=9600)
        try:
            hp.open_connection()
            await hp.login_async()
            # query for the outdoor temperature
            temp = await hp.get_param_async("Temp. Aussen")
            print(temp)
            # ...
        finally:
            await hp.logout_async()  # try to logout for an ordinary cancellation (if possible)
            hp.close_connection()
    """

    def __init__(
        self,
        device: str,
        baudrate: int = 115200,
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: Union[float, int] = serial.STOPBITS_ONE,
        timeout: Optional[Union[float, int]] = HtHeatpump.DEFAULT_SERIAL_TIMEOUT,
        xonxoff: bool = True,
        rtscts: bool = False,
        write_timeout: Optional[Union[float, int]] = None,
        dsrdtr: bool = False,
        inter_byte_timeout: Optional[Union[float, int]] = None,
        exclusive: Optional[bool] = None,
        verify_param_action: Optional[Set["VerifyAction"]] = None,
        verify_param_error: bool = False,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cancel_read_timeout: int = 1,
        cancel_write_timeout: int = 1,
    ) -> None:
        """Initialize the AioHtHeatpump class."""
        # store the serial settings for later connection establishment
        self._ser_settings = {
            "port": device,
            "baudrate": baudrate,
            "bytesize": bytesize,
            "parity": parity,
            "stopbits": stopbits,
            "timeout": timeout,
            "xonxoff": xonxoff,
            "rtscts": rtscts,
            "write_timeout": write_timeout,
            "dsrdtr": dsrdtr,
            "inter_byte_timeout": inter_byte_timeout,
            "exclusive": exclusive,
            "loop": loop,
            "cancel_read_timeout": cancel_read_timeout,
            "cancel_write_timeout": cancel_write_timeout,
        }
        self._ser = None
        self._lock = asyncio.Lock()
        # store settings for parameter verification
        self._verify_param_action = (
            {VerifyAction.NAME} if verify_param_action is None else verify_param_action
        )
        assert isinstance(self._verify_param_action, set)
        self._verify_param_error = verify_param_error
        assert isinstance(self._verify_param_error, bool)

    def open_connection(self) -> None:
        """Open the serial connection with the defined settings.

        :raises IOError:
            When the serial connection is already open.
        :raises ValueError:
            Will be raised when parameter are out of range, e.g. baudrate, bytesize.
        :raises SerialException:
            In case the device can not be found or can not be configured.
        """
        if self._ser:
            raise IOError("serial connection already open")
        # open the serial connection (must fit with the settings on the heat pump!)
        self._ser = aioserial.AioSerial(**self._ser_settings)
        _LOGGER.info(self._ser)  # log serial connection properties

    async def send_request_async(self, cmd: str) -> None:
        """Send a request to the heat pump.

        :param cmd: Command to send to the heat pump.
        :type cmd: str
        :raises IOError:
            Will be raised when the serial connection is not open.
        """
        if not self._ser:
            raise IOError("serial connection not open")
        req = create_request(cmd)
        _LOGGER.debug("send request: [%s]", req)
        await self._ser.write_async(req)

    async def read_response_async(self) -> str:
        """Read the response message from the heat pump.

        :returns: The returned response message of the heat pump as :obj:`str`.
        :rtype: ``str``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            (or unknown) response (e.g. broken data stream, unknown header, invalid checksum, ...).

        .. note::

            **There is a little bit strange behavior how the heat pump sometimes replies on some requests:**

            A response from the heat pump normally consists of the following header (the first 6 bytes)
            ``b"\\x02\\xfd\\xe0\\xd0\\x00\\x00"`` together with the payload and a computed checksum.
            But sometimes the heat pump replies with a different header (``b"\\x02\\xfd\\xe0\\xd0\\x04\\x00"``
            or ``b"\\x02\\xfd\\xe0\\xd0\\x08\\x00"``) together with the payload and a *fixed* value of
            ``0x0`` for the checksum (regardless of the content).

            We have no idea about the reason for this behavior. But after analysing the communication between
            the `Heliotherm home control <http://homecontrol.heliotherm.com/>`_ Windows application and the
            heat pump, which simply accepts this kind of responses, we also decided to handle it as a valid
            answer to a request.

            Furthermore, we have noticed another behavior, which is not fully explainable:
            For some response messages from the heat pump (e.g. for the error message ``"ERR,INVALID IDX"``)
            the transmitted payload length in the protocol is zero (0 bytes), although some payload follows.
            In this case we read until we will found the trailing ``b"\\r\\n"`` at the end of the payload
            to determine the payload of the message.

            Additionally to the upper described facts, for some of the answers of the heat pump the payload length
            must be corrected (for the checksum computation) so that the received checksum fits with the computed
            one (e.g. for ``b"\\x02\\xfd\\xe0\\xd0\\x01\\x00"`` and ``b"\\x02\\xfd\\xe0\\xd0\\x02\\x00"``).
        """
        if not self._ser:
            raise IOError("serial connection not open")
        # read the header of the response message
        header = await self._ser.read_async(RESPONSE_HEADER_LEN)
        if not header:
            raise IOError("data stream broken during reading response header")
        elif header not in RESPONSE_HEADER:
            raise IOError("invalid or unknown response header [{}]".format(header))
        # read the length of the following payload
        payload_len_r = await self._ser.read_async(1)
        if not payload_len_r:
            raise IOError("data stream broken during reading payload length")
        payload_len = payload_len_r = payload_len_r[0]
        # We don't know why, but for some messages (e.g. for the error message "ERR,INVALID IDX") the
        # heat pump answers with a payload length of zero bytes. In order to also accept such responses
        # we read until we will found the trailing "\r\n" at the end of the payload. The payload length
        # itself will then be computed afterwards by counting the number of bytes of the payload.
        if payload_len == 0:
            _LOGGER.info(
                "received response with a payload length of zero;"
                " try to read until the occurrence of '\\r\\n' [header=%s]",
                header,
            )
            payload = b""
            while payload[-2:] != b"\r\n":
                tmp = await self._ser.read_async(1)
                if not tmp:
                    raise IOError(
                        "data stream broken during reading payload ending with '\\r\\n'"
                    )
                payload += tmp
            # compute the payload length by counting the number of read bytes
            payload_len = len(payload)
        else:
            # read the payload itself
            payload = await self._ser.read_async(payload_len)
            if not payload or len(payload) < payload_len:
                raise IOError("data stream broken during reading payload")
        # depending on the received header correct the payload length for the checksum computation,
        #   so that the received checksum fits with the computed one
        payload_len = RESPONSE_HEADER[header]["payload_len"](payload_len)
        # read the checksum and verify the validity of the response
        checksum = await self._ser.read_async(1)
        if not checksum:
            raise IOError("data stream broken during reading checksum")
        checksum = checksum[0]
        # compute the checksum over header, payload length and the payload itself (depending on the header)
        comp_checksum = RESPONSE_HEADER[header]["checksum"](
            header, payload_len, payload
        )
        if checksum != comp_checksum:
            raise IOError(
                "invalid checksum [{}] of response "
                "[header={}, payload_len={:d}({:d}), payload={}, checksum={}]".format(
                    hex(checksum),
                    header,
                    payload_len,
                    payload_len_r,
                    payload,
                    hex(comp_checksum),
                )
            )
        # debug log of the received response
        _LOGGER.debug(
            "received response: %s",
            header + bytes([payload_len]) + payload + bytes([checksum]),
        )
        _LOGGER.debug("  header = %s", header)
        _LOGGER.debug("  payload length = %d(%d)", payload_len, payload_len_r)
        _LOGGER.debug("  payload = %s", payload)
        _LOGGER.debug("  checksum = %s", hex(checksum))
        # extract the relevant data from the payload (without header '~' and trailer ';\r\n')
        m = re.match(r"^~([^;]*);\r\n$", payload.decode("ascii"))
        if not m:
            raise IOError(
                "failed to extract response data from payload [{}]".format(payload)
            )
        return m.group(1)

    async def login_async(
        self,
        update_param_limits: bool = False,
        max_retries: int = HtHeatpump.DEFAULT_LOGIN_RETRIES,
    ) -> None:
        """Log in the heat pump. If :attr:`update_param_limits` is :const:`True` an update of the
        parameter limits in :class:`~htheatpump.htparams.HtParams` will be performed. This will
        be done by requesting the current value together with their limits (MIN and MAX) for all
        “known” parameters directly after a successful login.

        :param update_param_limits: Determines whether an update of the parameter limits in
            :class:`~htheatpump.htparams.HtParams` should be done or not. Default is :const:`False`.
        :type update_param_limits: bool
        :param max_retries: Maximal number of retries for a successful login. One regular try
            plus :const:`max_retries` retries.
            Default is :attr:`~htheatpump.htheatpump.HtHeatpump.DEFAULT_LOGIN_RETRIES`.
        :type max_retries: int
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # we try to login the heat pump for several times
            success = False
            retry = 0
            while not success and retry <= max_retries:
                # send LOGIN request to the heat pump
                await self.send_request_async(LOGIN_CMD)
                # ... and wait for the response
                try:
                    resp = await self.read_response_async()
                    m = re.match(LOGIN_RESP, resp)
                    if not m:
                        raise IOError(
                            "invalid response for LOGIN command [{!r}]".format(resp)
                        )
                    else:
                        success = True
                except Exception as e:
                    retry += 1
                    _LOGGER.warning("login try #%d failed: %s", retry, e)
                    # try a reconnect, maybe this will help ;-)
                    self.reconnect()
            if not success:
                _LOGGER.error("login failed after %d try/tries", retry)
                raise IOError("login failed after {:d} try/tries".format(retry))
            _LOGGER.info("login successfully")
            # perform a limits update of all parameters (if desired)
            if update_param_limits:
                await self.update_param_limits_async()

    async def logout_async(self) -> None:
        """Log out from the heat pump session."""
        async with self._lock:
            try:
                # send LOGOUT request to the heat pump
                await self.send_request_async(LOGOUT_CMD)
                # ... and wait for the response
                resp = await self.read_response_async()
                m = re.match(LOGOUT_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for LOGOUT command [{!r}]".format(resp)
                    )
                _LOGGER.info("logout successfully")
            except Exception as e:
                # just a warning, because it's possible that we can continue without any further problems
                _LOGGER.warning("logout failed: %s", e)
                # raise  # logout_async() should not fail!

    async def get_serial_number_async(self) -> int:
        """Query for the manufacturer's serial number of the heat pump.

        :returns: The manufacturer's serial number of the heat pump as :obj:`int` (e.g. :data:`123456`).
        :rtype: ``int``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # send RID request to the heat pump
            await self.send_request_async(RID_CMD)
            # ... and wait for the response
            try:
                resp = await self.read_response_async()  # e.g. "RID,123456"
                m = re.match(RID_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for RID command [{!r}]".format(resp)
                    )
                rid = int(m.group(1))
                _LOGGER.debug("manufacturer's serial number = %d", rid)
                return rid  # return the received manufacturer's serial number as an int
            except Exception as e:
                _LOGGER.error("query for manufacturer's serial number failed: %s", e)
                raise

    async def get_version_async(self) -> Tuple[str, int]:
        """Query for the software version of the heat pump.

        :returns: The software version of the heat pump as a tuple with 2 elements.
            The first element inside the returned tuple represents the software
            version as a readable string in a common version number format
            (e.g. :data:`"3.0.20"`). The second element (probably) contains a numerical
            representation as :obj:`int` of the software version returned by the heat pump.
            For example:
            ::

                ( "3.0.20", 2321 )

        :rtype: ``tuple`` ( str, int )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # send request command to the heat pump
            await self.send_request_async(VERSION_CMD)
            # ... and wait for the response
            try:
                resp = await self.read_response_async()
                # search for pattern "NAME=..." and "VAL=..." inside the response string;
                #   the textual representation of the version is encoded in the 'NAME',
                #   e.g. "SP,NR=9,ID=9,NAME=3.0.20,LEN=4,TP=0,BIT=0,VAL=2321,MAX=0,MIN=0,WR=0,US=1"
                #   => software version = 3.0.20
                m = re.match(VERSION_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for query of the software version [{!r}]".format(
                            resp
                        )
                    )
                ver = (m.group(1).strip(), int(m.group(2)))
                _LOGGER.debug("software version = %s (%d)", *ver)
                return ver
            except Exception as e:
                _LOGGER.error("query for software version failed: %s", e)
                raise

    async def get_date_time_async(self) -> Tuple[datetime.datetime, int]:
        """Read the current date and time of the heat pump.

        :returns: The current date and time of the heat pump as a tuple with 2 elements, where
            the first element is of type :class:`datetime.datetime` which represents the current
            date and time while the second element is the corresponding weekday in form of an
            :obj:`int` between 1 and 7, inclusive (Monday through Sunday). For example:
            ::

                ( datetime.datetime(...), 2 )  # 2 = Tuesday

        :rtype: ``tuple`` ( datetime.datetime, int )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # send CLK request to the heat pump
            await self.send_request_async(CLK_CMD[0])
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "CLK,DA=26.11.15,TI=21:28:57,WD=4"
                m = re.match(CLK_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for CLK command [{!r}]".format(resp)
                    )
                year = 2000 + int(m.group(3))
                month, day, hour, minute, second = [
                    int(g) for g in m.group(2, 1, 4, 5, 6)
                ]
                weekday = int(m.group(7))  # weekday 1-7 (Monday through Sunday)
                # create datetime object from extracted data
                dt = datetime.datetime(year, month, day, hour, minute, second)
                _LOGGER.debug("datetime = %s, weekday = %d", dt.isoformat(), weekday)
                return (
                    dt,
                    weekday,
                )  # return the heat pump's date and time as a datetime object
            except Exception as e:
                _LOGGER.error("query for date and time failed: %s", e)
                raise

    async def set_date_time_async(
        self, dt: Optional[datetime.datetime] = None
    ) -> Tuple[datetime.datetime, int]:
        """Set the current date and time of the heat pump.

        :param dt: The date and time to set. If :const:`None` current date and time
            of the host will be used.
        :type dt: datetime.datetime
        :returns: A 2-elements tuple composed of a :class:`datetime.datetime` which represents
            the sent date and time and an :obj:`int` between 1 and 7, inclusive, for the corresponding
            weekday (Monday through Sunday).
        :rtype: ``tuple`` ( datetime.datetime, int )
        :raises TypeError:
            Raised for an invalid type of argument :attr:`dt`. Must be :const:`None` or
            of type :class:`datetime.datetime`.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            if dt is None:
                dt = datetime.datetime.now()
            elif not isinstance(dt, datetime.datetime):
                raise TypeError(
                    "argument 'dt' must be None or of type datetime.datetime"
                )
            # create CLK set command
            cmd = CLK_CMD[1].format(
                dt.day,
                dt.month,
                dt.year - 2000,
                dt.hour,
                dt.minute,
                dt.second,
                dt.isoweekday(),
            )
            # send command to the heat pump
            await self.send_request_async(cmd)
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "CLK,DA=26.11.15,TI=21:28:57,WD=4"
                m = re.match(CLK_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for CLK command [{!r}]".format(resp)
                    )
                year = 2000 + int(m.group(3))
                month, day, hour, minute, second = [
                    int(g) for g in m.group(2, 1, 4, 5, 6)
                ]
                weekday = int(m.group(7))  # weekday 1-7 (Monday through Sunday)
                # create datetime object from extracted data
                dt = datetime.datetime(year, month, day, hour, minute, second)
                _LOGGER.debug("datetime = %s, weekday = %d", dt.isoformat(), weekday)
                return (
                    dt,
                    weekday,
                )  # return the heat pump's date and time as a datetime object
            except Exception as e:
                _LOGGER.error("set of date and time failed: %s", e)
                raise

    async def get_last_fault_async(self) -> Tuple[int, int, datetime.datetime, str]:
        """Query for the last fault message of the heat pump.

        :returns:
            The last fault message of the heat pump as a tuple with 4 elements.
            The first element of the returned tuple represents the index as :obj:`int` of
            the message inside the fault list. The second element is (probably) the
            the error code as :obj:`int` defined by Heliotherm. The last two elements of the
            tuple are the date and time when the error occurred (as :class:`datetime.datetime`)
            and the error message string itself. For example:
            ::

                ( 29, 20, datetime.datetime(...), "EQ_Spreizung" )

        :rtype: ``tuple`` ( int, int, datetime.datetime, str )
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # send ALC request to the heat pump
            await self.send_request_async(ALC_CMD)
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "AA,29,20,14.09.14-11:52:08,EQ_Spreizung"
                m = re.match(ALC_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for ALC command [{!r}]".format(resp)
                    )
                idx, err = [
                    int(g) for g in m.group(1, 2)
                ]  # fault list index, error code (?)
                year = 2000 + int(m.group(5))
                month, day, hour, minute, second = [
                    int(g) for g in m.group(4, 3, 6, 7, 8)
                ]
                # create datetime object from extracted data
                dt = datetime.datetime(year, month, day, hour, minute, second)
                msg = m.group(9).strip()
                _LOGGER.debug(
                    "(idx: %d, err: %d)[%s]: %s", idx, err, dt.isoformat(), msg
                )
                return idx, err, dt, msg
            except Exception as e:
                _LOGGER.error("query for last fault message failed: %s", e)
                raise

    async def get_fault_list_size_async(self) -> int:
        """Query for the fault list size of the heat pump.

        :returns: The size of the fault list as :obj:`int`.
        :rtype: ``int``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            # send ALS request to the heat pump
            await self.send_request_async(ALS_CMD)
            # ... and wait for the response
            try:
                resp = await self.read_response_async()  # e.g. "SUM=2757"
                m = re.match(ALS_RESP, resp)
                if not m:
                    raise IOError(
                        "invalid response for ALS command [{!r}]".format(resp)
                    )
                size = int(m.group(1))
                _LOGGER.debug("fault list size = %d", size)
                return size
            except Exception as e:
                _LOGGER.error("query for fault list size failed: %s", e)
                raise

    async def get_fault_list_async(self, *args: int) -> List[Dict[str, object]]:
        """Query for the fault list of the heat pump.

        :param args: The index number(s) to request from the fault list (optional).
            If not specified all fault list entries are requested.
        :type args: int
        :returns: The requested entries of the fault list as :obj:`list`, e.g.:
            ::

                [ { "index"   : 29,                     # fault list index
                    "error"   : 20,                     # error code
                    "datetime": datetime.datetime(...), # date and time of the entry
                    "message" : "EQ_Spreizung",         # error message
                    },
                  # ...
                  ]

        :rtype: ``list``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        if not args:
            args = range(await self.get_fault_list_size_async())  # type: ignore
        # TODO args = set(args) ???
        async with self._lock:
            fault_list = []
            # request fault list entries in several pieces (if required)
            n = 0
            while n < len(args):
                cnt = 0
                cmd = AR_CMD
                while n < len(args):
                    item = ",{}".format(args[n])
                    if len(cmd + item) <= MAX_CMD_LENGTH:
                        cmd += item
                        cnt += 1
                        n += 1
                    else:
                        break
                assert cnt > 0
                # send AR request to the heat pump
                await self.send_request_async(cmd)
                # ... and wait for the response
                try:
                    resp = []
                    # read all requested fault list entries
                    for _ in range(cnt):
                        resp.append(
                            await self.read_response_async()
                        )  # e.g. "AA,29,20,14.09.14-11:52:08,EQ_Spreizung"
                    # extract data (fault list index, error code, date, time and message)
                    for i, r in enumerate(resp):
                        m = re.match(AR_RESP, r)
                        if not m:
                            raise IOError(
                                "invalid response for AR command [{!r}]".format(r)
                            )
                        idx, err = [
                            int(g) for g in m.group(1, 2)
                        ]  # fault list index, error code
                        year = 2000 + int(m.group(5))
                        month, day, hour, minute, second = [
                            int(g) for g in m.group(4, 3, 6, 7, 8)
                        ]
                        # create datetime object from extracted data
                        dt = datetime.datetime(year, month, day, hour, minute, second)
                        msg = m.group(9).strip()
                        _LOGGER.debug(
                            "(idx: %03d, err: %05d)[%s]: %s",
                            idx,
                            err,
                            dt.isoformat(),
                            msg,
                        )
                        if idx != args[n - cnt + i]:
                            raise IOError(
                                "fault list index doesn't match [{:d}, should be {:d}]".format(
                                    idx, args[n - cnt + i]
                                )
                            )
                        # add the received fault list entry to the result list
                        fault_list.append(
                            {
                                "index": idx,  # fault list index
                                "error": err,  # error code
                                "datetime": dt,  # date and time of the entry
                                "message": msg,  # error message
                            }
                        )
                except Exception as e:
                    _LOGGER.error("query for fault list failed: %s", e)
                    raise
            return fault_list

    async def _get_param_async(
        self, name: str
    ) -> Tuple[str, HtParamValueType, HtParamValueType, HtParamValueType]:
        """Read the data (NAME, MIN, MAX, VAL) of a specific parameter of the heat pump.

        :param name: The parameter name, e.g. :data:`"Betriebsart"`.
        :type name: str
        :returns: The extracted parameter data as a tuple with 4 elements. The first element inside
            the returned tuple represents the parameter name as :obj:`str`, the second and third element
            the minimal and maximal value (as :obj:`bool`, :obj:`int` or :obj:`float`) and the last element
            the current value (as :obj:`bool`, :obj:`int` or :obj:`float`) of the parameter. For example:
            ::

                ( "Temp. EQ_Austritt", -20.0, 30.0, 15.1 )  # name, min, max, val

        :rtype: ``tuple`` ( str, bool/int/float, bool/int/float, bool/int/float )
        :raises IOError:
            Will be raised for an incomplete/invalid response from the heat pump.
        """
        async with self._lock:
            # get the corresponding definition for the requested parameter
            assert (
                name in HtParams
            ), "parameter definition for parameter {!r} not found".format(name)
            param = HtParams[name]  # type: ignore
            # send command to the heat pump
            await self.send_request_async(param.cmd())
            # ... and wait for the response
            try:
                resp = await self.read_response_async()
                return self._extract_param_data(name, resp)
            except Exception as e:
                _LOGGER.error("query of parameter '%s' failed: %s", name, e)
                raise

    async def update_param_limits_async(self) -> List[str]:
        """Perform an update of the parameter limits in :class:`~htheatpump.htparams.HtParams` by requesting
        the limit values of all "known" parameters directly from the heat pump.

        :returns: The list of updated (changed) parameters.
        :rtype: ``list``
        :raises VerificationException:
            Will be raised if the parameter verification fails and the property :attr:`~HtHeatpump.verify_param_error`
            is set to :const:`True`. If property :attr:`~HtHeatpump.verify_param_error` is set to :const:`False` only
            a warning message will be emitted. The performed verification steps are defined by the property
            :attr:`~HtHeatpump.verify_param_action`.
        """
        updated_params = []  # stores the name of updated parameters
        for name in HtParams.keys():
            resp_name, resp_min, resp_max, _ = await self._get_param_async(name)
            # only verify the returned NAME here, ignore MIN and MAX (and also the returned VAL)
            self._verify_param_resp(name, resp_name)
            # update the limit values in the HtParams database and count the number of updated entries
            if HtParams[name].set_limits(resp_min, resp_max):
                updated_params.append(name)
                _LOGGER.debug(
                    "updated param '%s': MIN=%s, MAX=%s", name, resp_min, resp_max
                )
        _LOGGER.info(
            "updated %d (of %d) parameter limits", len(updated_params), len(HtParams)
        )
        return updated_params

    async def get_param_async(self, name: str) -> HtParamValueType:
        """Query for a specific parameter of the heat pump.

        :param name: The parameter name, e.g. :data:`"Betriebsart"`.
        :type name: str
        :returns: Returned value of the requested parameter.
            The type of the returned value is defined by the csv-table
            of supported heat pump parameters in :file:`htparams.csv`.
        :rtype: ``bool``, ``int`` or ``float``
        :raises KeyError:
            Will be raised when the parameter definition for the passed parameter is not found.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        :raises VerificationException:
            Will be raised if the parameter verification fails and the property :attr:`~HtHeatpump.verify_param_error`
            is set to :const:`True`. If property :attr:`~HtHeatpump.verify_param_error` is set to :const:`False` only
            a warning message will be emitted. The performed verification steps are defined by the property
            :attr:`~HtHeatpump.verify_param_action`.

        For example, the following call
        ::

            temp = await hp.get_param_async("Temp. Aussen")

        will return the current measured outdoor temperature in °C.
        """
        # find the corresponding definition for the parameter
        if name not in HtParams:
            raise KeyError(
                "parameter definition for parameter {!r} not found".format(name)
            )
        try:
            resp = await self._get_param_async(name)
            val = self._verify_param_resp(name, *resp)
            _LOGGER.debug("'%s' = %s", name, val)
            return val  # type: ignore
        except Exception as e:
            _LOGGER.error("get parameter '%s' failed: %s", name, e)
            raise

    async def set_param_async(
        self, name: str, val: HtParamValueType, ignore_limits: bool = False
    ) -> HtParamValueType:
        """Set the value of a specific parameter of the heat pump. If :attr:`ignore_limits` is :const:`False`
        and the passed value is beyond the parameter limits a :exc:`ValueError` will be raised.

        :param name: The parameter name, e.g. :data:`"Betriebsart"`.
        :type name: str
        :param val: The value to set.
        :type val: bool, int or float
        :param ignore_limits: Indicates if the parameter limits should be ignored or not.
        :type ignore_limits: bool
        :returns: Returned value of the parameter set request.
            In case of success this value should be the same as the one
            passed to the function.
            The type of the returned value is defined by the csv-table
            of supported heat pump parameters in :file:`htparams.csv`.
        :rtype: ``bool``, ``int`` or ``float``
        :raises KeyError:
            Will be raised when the parameter definition for the passed parameter is not found.
        :raises ValueError:
            Will be raised if the passed value is beyond the parameter limits and argument :attr:`ignore_limits`
            is set to :const:`False`.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        :raises VerificationException:
            Will be raised if the parameter verification fails and the property :attr:`~HtHeatpump.verify_param_error`
            is set to :const:`True`. If property :attr:`~HtHeatpump.verify_param_error` is set to :const:`False` only
            a warning message will be emitted. The performed verification steps are defined by the property
            :attr:`~HtHeatpump.verify_param_action`.

        For example, the following call
        ::

            await hp.set_param_async("HKR Soll_Raum", 21.5)

        will set the desired room temperature of the heating circuit to 21.5 °C.
        """
        async with self._lock:
            assert val is not None, "'val' must not be None"
            # find the corresponding definition for the parameter
            if name not in HtParams:
                raise KeyError(
                    "parameter definition for parameter {!r} not found".format(name)
                )
            param = HtParams[name]  # type: ignore
            # check the passed value against the defined limits (if desired)
            if not ignore_limits and not param.in_limits(val):
                raise ValueError(
                    "value {!r} is beyond the limits [{}, {}]".format(
                        val, param.min_val, param.max_val
                    )
                )
            # send command to the heat pump
            val = param.to_str(val)
            await self.send_request_async("{},VAL={}".format(param.cmd(), val))
            # ... and wait for the response
            try:
                resp = await self.read_response_async()
                data = self._extract_param_data(name, resp)
                ret = self._verify_param_resp(name, *data)
                _LOGGER.debug("'%s' = %s", name, ret)
                return ret  # type: ignore
            except Exception as e:
                _LOGGER.error("set parameter '%s' failed: %s", name, e)
                raise

    @property
    async def in_error_async(self) -> bool:
        """Query whether the heat pump is malfunctioning.

        :returns: :const:`True` if the heat pump is malfunctioning, :const:`False` otherwise.
        :rtype: ``bool``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        return await self.get_param_async("Stoerung")  # type: ignore

    async def query_async(self, *args: str) -> Dict[str, HtParamValueType]:
        """Query for the current values of parameters from the heat pump.

        :param args: The parameter name(s) to request from the heat pump.
            If not specified all "known" parameters are requested.
        :type args: str
        :returns: A dict of the requested parameters with their values, e.g.:
            ::

                { "HKR Soll_Raum": 21.0,
                  "Stoerung": False,
                  "Temp. Aussen": 8.8,
                  # ...
                  }

        :rtype: ``dict``
        :raises KeyError:
            Will be raised when the parameter definition for a passed parameter is not found.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        :raises VerificationException:
            Will be raised if the parameter verification fails and the property :attr:`~HtHeatpump.verify_param_error`
            is set to :const:`True`. If property :attr:`~HtHeatpump.verify_param_error` is set to :const:`False` only
            a warning message will be emitted. The performed verification steps are defined by the property
            :attr:`~HtHeatpump.verify_param_action`.
        """
        if not args:
            args = HtParams.keys()  # type: ignore
        values = {}
        try:
            # query for each parameter in the given list
            for name in args:
                values.update({name: await self.get_param_async(name)})
        except Exception as e:
            _LOGGER.error("query of parameter(s) failed: %s", e)
            raise
        return values

    async def fast_query_async(self, *args: str) -> Dict[str, HtParamValueType]:
        """Query for the current values of parameters from the heat pump the fast way.

        .. note::

            Only available for parameters representing a "MP" data point and no parameter verification possible!

        :param args: The parameter name(s) to request from the heat pump.
            If not specified all "known" parameters representing a "MP" data point are requested.
        :type args: str
        :returns: A dict of the requested parameters with their values, e.g.:
            ::

                { "EQ Pumpe (Ventilator)": False,
                  "FWS Stroemungsschalter": False,
                  "Frischwasserpumpe": 0,
                  "HKR_Sollwert": 26.8,
                  # ...
                  }

        :rtype: ``dict``
        :raises KeyError:
            Will be raised when the parameter definition for a passed parameter is not found.
        :raises ValueError:
            Will be raised when a passed parameter doesn't represent a "MP" data point.
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            if not args:
                args = (name for name, param in HtParams.items() if param.dp_type == "MP")  # type: ignore
            # TODO args = set(args) ???
            dp_list = []
            dp_dict = {}
            for name in args:
                if name not in HtParams:
                    raise KeyError(
                        "parameter definition for parameter {!r} not found".format(name)
                    )
                param = HtParams[name]  # type: ignore
                if param.dp_type != "MP":
                    raise ValueError(
                        "invalid parameter {!r}; only parameters representing a 'MP' data point are allowed".format(
                            name
                        )
                    )
                dp_list.append(param.dp_number)
                dp_dict.update({param.dp_number: (name, param)})
            values = {}
            # query for the current values of parameters in several pieces (if required)
            n = 0
            while n < len(dp_list):
                cnt = 0
                cmd = MR_CMD
                while n < len(dp_list):
                    number = ",{}".format(dp_list[n])
                    if len(cmd + number) <= MAX_CMD_LENGTH:
                        cmd += number
                        cnt += 1
                        n += 1
                    else:
                        break
                assert cnt > 0
                # send MR request to the heat pump
                await self.send_request_async(cmd)
                # ... and wait for the response
                try:
                    resp = []
                    # read all requested data point (parameter) values
                    for _ in range(cnt):
                        resp.append(
                            await self.read_response_async()
                        )  # e.g. "MA,11,46.0,16"
                    # extract data (MP data point number, data point value and "unknown" value)
                    for r in resp:
                        m = re.match(MR_RESP, r)
                        if not m:
                            raise IOError(
                                "invalid response for MR command [{!r}]".format(r)
                            )
                        # MP data point number, value and ?
                        dp_number, dp_value, unknown_val = m.group(
                            1, 2, 3
                        )  # type: Any, str, str
                        dp_number = int(dp_number)
                        if dp_number not in dp_dict:
                            raise IOError(
                                "non requested data point value received [MP,{:d}]".format(
                                    dp_number
                                )
                            )
                        name, param = dp_dict[dp_number]
                        val = param.from_str(dp_value)
                        _LOGGER.debug("'%s' = %s (%s)", name, val, unknown_val)
                        # check the received value against the limits and write a WARNING if necessary
                        if not param.in_limits(val):
                            _LOGGER.warning(
                                "value '%s' of parameter '%s' is beyond the limits [%s, %s]",
                                val,
                                name,
                                param.min_val,
                                param.max_val,
                            )
                        values.update({name: val})
                except Exception as e:
                    _LOGGER.error("fast query of parameter(s) failed: %s", e)
                    raise
            return values

    async def get_time_progs_async(self) -> List[TimeProgram]:
        """Return a list of all available time programs of the heat pump.

        :returns: A list of :class:`~htheatpump.httimeprog.TimeProgram` instances.
        :rtype: ``list``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            time_progs = []
            # send PRL request to the heat pump
            await self.send_request_async(PRL_CMD)
            # ... and wait for the response
            try:
                resp = await self.read_response_async()  # e.g. "SUM=5"
                m = re.match(PRL_RESP[0], resp)
                if not m:
                    raise IOError(
                        "invalid response for PRL command [{!r}]".format(resp)
                    )
                sum = int(m.group(1))
                _LOGGER.debug("number of time programs = %d", sum)
                for idx in range(sum):
                    resp = (
                        await self.read_response_async()
                    )  # e.g. "PRI0,NAME=Warmwasser,EAD=7,NOS=2,STE=15,NOD=7,ACS=0,US=1"
                    m = re.match(PRL_RESP[1].format(idx), resp)
                    if not m:
                        raise IOError(
                            "invalid response for PRL command [{!r}]".format(resp)
                        )
                    # extract data (NAME, EAD, NOS, STE and NOD)
                    name = m.group(1)
                    ead, nos, ste, nod = [int(g) for g in m.group(2, 3, 4, 5)]
                    _LOGGER.debug(
                        "[idx=%d]: name='%s', ead=%d, nos=%d, ste=%d, nod=%d",
                        idx,
                        name,
                        ead,
                        nos,
                        ste,
                        nod,
                    )
                    time_progs.append(TimeProgram(idx, name, ead, nos, ste, nod))
            except Exception as e:
                _LOGGER.error("query for time programs failed: %s", e)
                raise
            return time_progs

    async def _get_time_prog_async(self, idx: int) -> TimeProgram:
        """Return a specific time program (specified by their index) without their time program entries
        from the heat pump.

        :param idx: The time program index.
        :type idx: int

        :returns: The requested time program as :class:`~htheatpump.httimeprog.TimeProgram` without
            their time program entries.
        :rtype: ``TimeProgram``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            assert isinstance(idx, int)
            # send PRI request to the heat pump
            await self.send_request_async(PRI_CMD.format(idx))
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "PRI0,NAME=Warmwasser,EAD=7,NOS=2,STE=15,NOD=7,ACS=0,US=1"
                m = re.match(PRI_RESP.format(idx), resp)
                if not m:
                    raise IOError(
                        "invalid response for PRI command [{!r}]".format(resp)
                    )
                # extract data (NAME, EAD, NOS, STE and NOD)
                name = m.group(1)
                ead, nos, ste, nod = [int(g) for g in m.group(2, 3, 4, 5)]
                _LOGGER.debug(
                    "[idx=%d]: name='%s', ead=%d, nos=%d, ste=%d, nod=%d",
                    idx,
                    name,
                    ead,
                    nos,
                    ste,
                    nod,
                )
                time_prog = TimeProgram(idx, name, ead, nos, ste, nod)
                return time_prog
            except Exception as e:
                _LOGGER.error("query for time program failed: %s", e)
                raise

    async def _get_time_prog_with_entries_async(self, idx: int) -> TimeProgram:
        """Return a specific time program (specified by their index) together with their time program entries
        from the heat pump.

        :param idx: The time program index.
        :type idx: int

        :returns: The requested time program as :class:`~htheatpump.httimeprog.TimeProgram` together
            with their time program entries.
        :rtype: ``TimeProgram``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            assert isinstance(idx, int)
            # send PRD request to the heat pump
            await self.send_request_async(PRD_CMD.format(idx))
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "PRI0,NAME=Warmwasser,EAD=7,NOS=2,STE=15,NOD=7,ACS=0,US=1"
                m = re.match(PRD_RESP[0].format(idx), resp)
                if not m:
                    raise IOError(
                        "invalid response for PRD command [{!r}]".format(resp)
                    )
                # extract data (NAME, EAD, NOS, STE and NOD)
                name = m.group(1)
                ead, nos, ste, nod = [int(g) for g in m.group(2, 3, 4, 5)]
                _LOGGER.debug(
                    "[idx=%d]: name='%s', ead=%d, nos=%d, ste=%d, nod=%d",
                    idx,
                    name,
                    ead,
                    nos,
                    ste,
                    nod,
                )
                time_prog = TimeProgram(idx, name, ead, nos, ste, nod)
                # read the single time program entries for each day
                for (day, num) in [
                    (day, num) for day in range(nod) for num in range(ead)
                ]:
                    resp = (
                        await self.read_response_async()
                    )  # e.g. "PRE,PR=0,DAY=2,EV=1,ST=1,BEG=03:30,END=22:00"
                    m = re.match(PRD_RESP[1].format(idx, day, num), resp)
                    if not m:
                        raise IOError(
                            "invalid response for PRD command [{!r}]".format(resp)
                        )
                    # extract data (ST, BEG, END)
                    st, beg, end = m.group(1, 2, 3)
                    _LOGGER.debug(
                        "[idx=%d, day=%d, entry=%d]: st=%s, beg=%s, end=%s",
                        idx,
                        day,
                        num,
                        st,
                        beg,
                        end,
                    )
                    time_prog.set_entry(day, num, TimeProgEntry.from_str(st, beg, end))
                return time_prog
            except Exception as e:
                _LOGGER.error("query for time program with entries failed: %s", e)
                raise

    async def get_time_prog_async(
        self, idx: int, with_entries: bool = True
    ) -> TimeProgram:
        """Return a specific time program (specified by their index) together with their time program entries
        (if desired) from the heat pump.

        :param idx: The time program index.
        :type idx: int
        :param with_entries: Determines whether also the single time program entries should be requested or not.
            Default is :const:`True`.
        :type with_entries: bool

        :returns: The requested time program as :class:`~htheatpump.httimeprog.TimeProgram`.
        :rtype: ``TimeProgram``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        assert isinstance(idx, int)
        assert isinstance(with_entries, bool)
        return (
            await self._get_time_prog_with_entries_async(idx)
            if with_entries
            else await self._get_time_prog_async(idx)
        )

    async def get_time_prog_entry_async(
        self, idx: int, day: int, num: int
    ) -> TimeProgEntry:
        """Return a specific time program entry (specified by time program index, day and entry-of-day)
        of the heat pump.

        :param idx: The time program index.
        :type idx: int
        :param day: The day of the time program entry (inside the specified time program).
        :type day: int
        :param num: The number of the time program entry (of the specified day).
        :type num: int

        :returns: The requested time program entry as :class:`~htheatpump.httimeprog.TimeProgEntry`.
        :rtype: ``TimeProgEntry``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            assert isinstance(idx, int)
            assert isinstance(day, int)
            assert isinstance(num, int)
            # send PRE request to the heat pump
            await self.send_request_async(PRE_CMD[0].format(idx, day, num))
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "PRE,PR=0,DAY=2,EV=1,ST=1,BEG=03:30,END=22:00"
                m = re.match(PRE_RESP.format(idx, day, num), resp)
                if not m:
                    raise IOError(
                        "invalid response for PRE command [{!r}]".format(resp)
                    )
                # extract data (ST, BEG, END)
                st, beg, end = m.group(1, 2, 3)
                _LOGGER.debug(
                    "[idx=%d, day=%d, entry=%d]: st=%s, beg=%s, end=%s",
                    idx,
                    day,
                    num,
                    st,
                    beg,
                    end,
                )
                return TimeProgEntry.from_str(st, beg, end)
            except Exception as e:
                _LOGGER.error("query for time program entry failed: %s", e)
                raise

    async def set_time_prog_entry_async(
        self, idx: int, day: int, num: int, entry: TimeProgEntry
    ) -> TimeProgEntry:
        """Set a specific time program entry (specified by time program index, day and entry-of-day)
        of the heat pump.

        :param idx: The time program index.
        :type idx: int
        :param day: The day of the time program entry (inside the specified time program).
        :type day: int
        :param num: The number of the time program entry (of the specified day).
        :type num: int
        :param entry: The new time program entry as :class:`~htheatpump.httimeprog.TimeProgEntry`.
        :type entry: TimeProgEntry

        :returns: The changed time program entry :class:`~htheatpump.httimeprog.TimeProgEntry`.
        :rtype: ``TimeProgEntry``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        async with self._lock:
            assert isinstance(idx, int)
            assert isinstance(day, int)
            assert isinstance(num, int)
            assert isinstance(entry, TimeProgEntry)
            # send PRE command to the heat pump
            await self.send_request_async(
                PRE_CMD[1].format(
                    idx,
                    day,
                    num,
                    entry.state,
                    entry.period.start_str,
                    entry.period.end_str,
                )
            )
            # ... and wait for the response
            try:
                resp = (
                    await self.read_response_async()
                )  # e.g. "PRE,PR=0,DAY=2,EV=1,ST=1,BEG=03:30,END=22:00"
                m = re.match(PRE_RESP.format(idx, day, num), resp)
                if not m:
                    raise IOError(
                        "invalid response for PRE command [{!r}]".format(resp)
                    )
                # extract data (ST, BEG, END)
                st, beg, end = m.group(1, 2, 3)
                _LOGGER.debug(
                    "[idx=%d, day=%d, entry=%d]: st=%s, beg=%s, end=%s",
                    idx,
                    day,
                    num,
                    st,
                    beg,
                    end,
                )
                return TimeProgEntry.from_str(st, beg, end)
            except Exception as e:
                _LOGGER.error("set time program entry failed: %s", e)
                raise

    async def set_time_prog_async(self, time_prog: TimeProgram) -> TimeProgram:
        """Set all time program entries of a specific time program. Any non-specified entry
        (which is :const:`None`) in the time program will be requested from the heat pump.
        The returned :class:`~htheatpump.httimeprog.TimeProgram` instance includes therefore
        all entries of this time program.

        :param time_prog: The given time program as :class:`~htheatpump.httimeprog.TimeProgram`.
        :type time_prog: TimeProgram

        :returns: The time program as :class:`~htheatpump.httimeprog.TimeProgram` including all time program entries.
        :rtype: ``TimeProgram``
        :raises IOError:
            Will be raised when the serial connection is not open or received an incomplete/invalid
            response (e.g. broken data stream, invalid checksum).
        """
        assert isinstance(time_prog, TimeProgram)
        ret = copy.deepcopy(time_prog)
        for (day, num) in [
            (day, num)
            for day in range(time_prog.number_of_days)
            for num in range(time_prog.entries_a_day)
        ]:
            entry = time_prog.entry(day, num)
            _LOGGER.debug(
                "[idx=%d, day=%d, entry=%d]: %s", time_prog.index, day, num, entry
            )
            if entry is not None:
                entry = await self.set_time_prog_entry_async(
                    time_prog.index, day, num, entry
                )
            else:
                entry = await self.get_time_prog_entry_async(time_prog.index, day, num)
            ret.set_entry(day, num, entry)
        return ret


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["AioHtHeatpump"]
