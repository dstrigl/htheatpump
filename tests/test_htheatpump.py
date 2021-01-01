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

""" Tests for code in `htheatpump.htheatpump`. """

import datetime
import random
import re
from typing import List

import pytest

from htheatpump import (
    HtDataTypes,
    HtHeatpump,
    HtParam,
    HtParams,
    TimeProgEntry,
    TimeProgram,
    VerifyAction,
)


@pytest.mark.parametrize(
    "s, checksum",
    [
        (b"", 0x0),
        (b"\x02\xfd\xd0\xe0\x00\x00\x05~LIN;", 0x4C),
        (b"\x02\xfd\xd0\xe0\x00\x00\x06~LOUT;", 0x92),
        (b"\x02\xfd\xe0\xd0\x00\x00\x06~OK;\r\n", 0x91),
        (b"\x02\xfd\xd0\xe0\x00\x00\t~SP,NR=9;", 0xDC),
    ],
)
def test_calc_checksum(s: bytes, checksum: int):
    from htheatpump.protocol import calc_checksum

    assert calc_checksum(s) == checksum
    # assert 0


@pytest.mark.parametrize("s", [b"", b"\x01"])
def test_verify_checksum_raises_ValueError(s: bytes):
    from htheatpump.protocol import verify_checksum

    with pytest.raises(ValueError):
        verify_checksum(s)
    # assert 0


@pytest.mark.parametrize(
    "s, result",
    [
        (b"\x00\x00", True),
        (b"\x02\xfd\xd0\xe0\x00\x00\x05~LIN;\x4c", True),
        (b"\x02\xfd\xd0\xe0\x00\x00\x06~LOUT;\x92", True),
        (b"\x02\xfd\xe0\xd0\x00\x00\x06~OK;\r\n\x91", True),
        (b"\x02\xfd\xd0\xe0\x00\x00\t~SP,NR=9;\xdc", True),
    ],
)
def test_verify_checksum(s: bytes, result: bool):
    from htheatpump.protocol import verify_checksum

    assert verify_checksum(s) == result
    # assert 0


@pytest.mark.parametrize("s", [b""])
def test_add_checksum_raises_ValueError(s: bytes):
    from htheatpump.protocol import add_checksum

    with pytest.raises(ValueError):
        add_checksum(s)
    # assert 0


@pytest.mark.parametrize(
    "s, result",
    [
        (b"\x00", b"\x00\x00"),
        (
            b"\x02\xfd\xd0\xe0\x00\x00\x05~LIN;",
            b"\x02\xfd\xd0\xe0\x00\x00\x05~LIN;\x4c",
        ),
        (
            b"\x02\xfd\xd0\xe0\x00\x00\x06~LOUT;",
            b"\x02\xfd\xd0\xe0\x00\x00\x06~LOUT;\x92",
        ),
        (
            b"\x02\xfd\xe0\xd0\x00\x00\x06~OK;\r\n",
            b"\x02\xfd\xe0\xd0\x00\x00\x06~OK;\r\n\x91",
        ),
        (
            b"\x02\xfd\xd0\xe0\x00\x00\t~SP,NR=9;",
            b"\x02\xfd\xd0\xe0\x00\x00\t~SP,NR=9;\xdc",
        ),
    ],
)
def test_add_checksum(s: bytes, result: bytes):
    from htheatpump.protocol import add_checksum

    assert add_checksum(s) == result
    # assert 0


@pytest.mark.parametrize("cmd", ["?" * 254])
def test_create_request_raises_ValueError(cmd: str):
    from htheatpump.protocol import create_request

    with pytest.raises(ValueError):
        create_request(cmd)
    # assert 0


@pytest.mark.parametrize(
    "cmd, result",
    [
        ("", b"\x02\xfd\xd0\xe0\x00\x00\x02~;\x98"),
        ("LIN", b"\x02\xfd\xd0\xe0\x00\x00\x05~LIN;\x4c"),
        ("LOUT", b"\x02\xfd\xd0\xe0\x00\x00\x06~LOUT;\x92"),
        ("SP,NR=9", b"\x02\xfd\xd0\xe0\x00\x00\t~SP,NR=9;\xdc"),
    ],
)
def test_create_request(cmd: str, result: bytes):
    from htheatpump.protocol import create_request

    assert create_request(cmd) == result
    # assert 0


@pytest.mark.run_if_connected
def test_HtHeatpump_init_del(cmdopt_device: str, cmdopt_baudrate: int):
    hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
    assert not hp.is_open
    hp.open_connection()
    assert hp.is_open
    del hp  # HtHeatpump.__del__ should be executed here!
    # assert 0


@pytest.mark.run_if_connected
def test_HtHeatpump_enter_exit(cmdopt_device: str, cmdopt_baudrate: int):
    with HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate) as hp:
        assert hp is not None
        assert hp.is_open
    assert hp is not None
    assert not hp.is_open
    # assert 0


@pytest.fixture(scope="class")
def hthp(cmdopt_device: str, cmdopt_baudrate: int):
    hthp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
    try:
        hthp.open_connection()
        yield hthp  # provide the heat pump instance
    finally:
        hthp.close_connection()


@pytest.fixture()
def reconnect(hthp: HtHeatpump):
    hthp.reconnect()
    hthp.login()
    yield
    hthp.logout()


class TestHtHeatpump:
    @pytest.mark.run_if_connected
    def test_open_connection(self, hthp: HtHeatpump):
        assert hthp.is_open
        with pytest.raises(IOError):
            hthp.open_connection()
        # assert 0

    @pytest.mark.parametrize(
        "action",
        [
            VerifyAction.NONE(),
            {VerifyAction.NAME},
            {VerifyAction.NAME, VerifyAction.MIN},
            {VerifyAction.NAME, VerifyAction.MIN, VerifyAction.MAX},
            {VerifyAction.NAME, VerifyAction.MIN, VerifyAction.MAX, VerifyAction.VALUE},
            {VerifyAction.MIN, VerifyAction.MAX, VerifyAction.VALUE},
            {VerifyAction.MAX, VerifyAction.VALUE},
            {VerifyAction.VALUE},
            VerifyAction.ALL(),
        ],
    )
    def test_verify_param_action(
        self, cmdopt_device: str, cmdopt_baudrate: int, action: set
    ):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        val = hp.verify_param_action
        assert isinstance(val, set)
        hp.verify_param_action = action
        assert hp.verify_param_action == action
        hp.verify_param_action = val
        # assert 0

    def test_verify_param_error(self, cmdopt_device: str, cmdopt_baudrate: int):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        val = hp.verify_param_error
        assert isinstance(val, bool)
        hp.verify_param_error = True
        assert hp.verify_param_error is True
        hp.verify_param_error = False
        assert hp.verify_param_error is False
        hp.verify_param_error = val
        # assert 0

    def test_send_request(self, cmdopt_device: str, cmdopt_baudrate: int):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(IOError):
            hp.send_request(r"LIN")
        # assert 0

    def test_read_response(self, cmdopt_device: str, cmdopt_baudrate: int):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(IOError):
            hp.read_response()
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_serial_number(self, hthp: HtHeatpump):
        rid = hthp.get_serial_number()
        assert isinstance(rid, int), "'rid' must be of type int"
        assert rid > 0
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_version(self, hthp: HtHeatpump):
        version = hthp.get_version()
        # ( "3.0.20", 2321 )
        assert isinstance(version, tuple), "'version' must be of type tuple"
        assert len(version) == 2
        ver_str, ver_num = version
        assert isinstance(ver_str, str), "'ver_str' must be of type str"
        m = re.match(r"^(\d+).(\d+).(\d+)$", ver_str)
        assert m is not None, "invalid version string [{!r}]".format(ver_str)
        assert isinstance(ver_num, int), "'ver_num' must be of type int"
        assert ver_num > 0
        hthp.send_request(r"SP,NR=9")
        resp = hthp.read_response()
        m = re.match(r"^SP,NR=9,.*NAME=([^,]+).*VAL=([^,]+).*$", resp)
        assert (
            m is not None
        ), "invalid response for query of the software version [{!r}]".format(resp)
        assert ver_str == m.group(1).strip()
        assert ver_num == int(m.group(2))
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_date_time(self, hthp: HtHeatpump):
        date_time = hthp.get_date_time()
        # (datetime.datetime(...), 2)  # 2 = Tuesday
        assert isinstance(date_time, tuple), "'date_time' must be of type tuple"
        assert len(date_time) == 2
        dt, weekday = date_time
        assert isinstance(dt, datetime.datetime), "'dt' must be of type datetime"
        assert isinstance(weekday, int), "'weekday' must be of type int"
        assert weekday in range(1, 8)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_date_time(self, hthp: HtHeatpump):
        pass  # TODO
        # assert 0

    def test_set_date_time_raises_TypeError(
        self, cmdopt_device: str, cmdopt_baudrate: int
    ):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(TypeError):
            hp.set_date_time(123)  # type: ignore
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_last_fault(self, hthp: HtHeatpump):
        fault = hthp.get_last_fault()
        # (29, 20, datetime.datetime(...), "EQ_Spreizung")
        assert isinstance(fault, tuple), "'fault' must be of type tuple"
        assert len(fault) == 4
        index, error, dt, msg = fault
        assert isinstance(index, int), "'index' must be of type int"
        assert 0 <= index < hthp.get_fault_list_size()
        assert isinstance(error, int), "'error' must be of type int"
        assert error >= 0
        assert isinstance(dt, datetime.datetime), "'dt' must be of type datetime"
        assert isinstance(msg, str), "'msg' must be of type str"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_size(self, hthp: HtHeatpump):
        size = hthp.get_fault_list_size()
        assert isinstance(size, int), "'size' must be of type int"
        assert size >= 0
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list(self, hthp: HtHeatpump):
        fault_list = hthp.get_fault_list()
        # [ { "index": 29,  # fault list index
        #     "error": 20,  # error code
        #     "datetime": datetime.datetime(...),  # date and time of the entry
        #     "message": "EQ_Spreizung",  # error message
        #     },
        #   # ...
        #   ]
        assert isinstance(fault_list, list), "'fault_list' must be of type list"
        assert len(fault_list) == hthp.get_fault_list_size()
        for entry in fault_list:
            assert isinstance(entry, dict), "'entry' must be of type dict"
            index = entry["index"]
            assert isinstance(index, int), "'index' must be of type int"
            assert 0 <= index < hthp.get_fault_list_size()
            error = entry["error"]
            assert isinstance(error, int), "'error' must be of type int"
            assert error >= 0
            dt = entry["datetime"]
            assert isinstance(dt, datetime.datetime), "'dt' must be of type datetime"
            msg = entry["message"]
            assert isinstance(msg, str), "'msg' must be of type str"
        # assert 0

    # @pytest.mark.skip(reason="test needs a rework")
    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_in_several_pieces(self, hthp: HtHeatpump):
        args = []
        cmd = ""
        fault_list_size = hthp.get_fault_list_size()
        while len(cmd) < 255 * 2:  # request has do be done in 3 parts
            item = random.randint(0, fault_list_size - 1)
            cmd += ",{}".format(item)
            args.append(item)
        fault_list = hthp.get_fault_list(*args)
        # [ { "index": 29,  # fault list index
        #     "error": 20,  # error code
        #     "datetime": datetime.datetime(...),  # date and time of the entry
        #     "message": "EQ_Spreizung",  # error message
        #     },
        #   # ...
        #   ]
        assert isinstance(fault_list, list), "'fault_list' must be of type list"
        assert len(fault_list) == len(args)
        for entry in fault_list:
            assert isinstance(entry, dict), "'entry' must be of type dict"
            index = entry["index"]
            assert isinstance(index, int), "'index' must be of type int"
            assert 0 <= index < fault_list_size
            error = entry["error"]
            assert isinstance(error, int), "'error' must be of type int"
            assert error >= 0
            dt = entry["datetime"]
            assert isinstance(dt, datetime.datetime), "'dt' must be of type datetime"
            msg = entry["message"]
            assert isinstance(msg, str), "'msg' must be of type str"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_with_index(self, hthp: HtHeatpump):
        size = hthp.get_fault_list_size()
        assert isinstance(size, int), "'size' must be of type int"
        assert size >= 0
        for i in range(size):
            fault_list = hthp.get_fault_list(i)
            assert isinstance(fault_list, list), "'fault_list' must be of type list"
            assert len(fault_list) == 1
            entry = fault_list[0]
            assert isinstance(entry, dict), "'entry' must be of type dict"
            index = entry["index"]
            assert isinstance(index, int), "'index' must be of type int"
            assert 0 <= index < hthp.get_fault_list_size()
            error = entry["error"]
            assert isinstance(error, int), "'error' must be of type int"
            assert error >= 0
            dt = entry["datetime"]
            assert isinstance(dt, datetime.datetime), "'dt' must be of type datetime"
            msg = entry["message"]
            assert isinstance(msg, str), "'msg' must be of type str"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_with_index_raises_IOError(self, hthp: HtHeatpump):
        with pytest.raises(IOError):
            hthp.get_fault_list(-1)
        with pytest.raises(IOError):
            hthp.get_fault_list(hthp.get_fault_list_size())
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_with_indices(self, hthp: HtHeatpump):
        size = hthp.get_fault_list_size()
        for cnt in range(size + 1):
            indices = random.sample(range(size), cnt)
            fault_list = hthp.get_fault_list(*indices)
            assert isinstance(fault_list, list), "'fault_list' must be of type list"
            assert len(fault_list) == (cnt if cnt > 0 else size)
            for entry in fault_list:
                assert isinstance(entry, dict), "'entry' must be of type dict"
                index = entry["index"]
                assert isinstance(index, int), "'index' must be of type int"
                assert 0 <= index < hthp.get_fault_list_size()
                error = entry["error"]
                assert isinstance(error, int), "'error' must be of type int"
                assert error >= 0
                dt = entry["datetime"]
                assert isinstance(
                    dt, datetime.datetime
                ), "'dt' must be of type datetime"
                msg = entry["message"]
                assert isinstance(msg, str), "'msg' must be of type str"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_get_param(self, hthp: HtHeatpump, name: str, param: HtParam):
        value = hthp.get_param(name)
        assert value is not None, "'value' must not be None"
        assert param.in_limits(value)
        # assert 0

    def test_get_param_raises_KeyError(self, cmdopt_device: str, cmdopt_baudrate: int):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(KeyError):
            hp.get_param("BlaBlaBla")
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_set_param(self, hthp: HtHeatpump, name: str, param: HtParam):
        pass  # TODO
        # assert 0

    def test_set_param_raises_KeyError(self, cmdopt_device: str, cmdopt_baudrate: int):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(KeyError):
            hp.set_param("BlaBlaBla", 123)
        # assert 0

    @pytest.mark.parametrize(
        "name, param",
        [
            (name, param)
            for name, param in HtParams.items()
            if param.data_type in (HtDataTypes.INT, HtDataTypes.FLOAT)
        ],
    )
    def test_set_param_raises_ValueError(
        self, cmdopt_device: str, cmdopt_baudrate: int, name: str, param: HtParam
    ):
        # hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        # with pytest.raises(ValueError):
        #    hp.set_param(name, param.min_val - 1, ignore_limits=False)  # type: ignore
        # with pytest.raises(ValueError):
        #    hp.set_param(name, param.max_val + 1, ignore_limits=False)  # type: ignore
        pass  # TODO
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_in_error(self, hthp: HtHeatpump):
        in_error = hthp.in_error
        assert isinstance(in_error, bool), "'in_error' must be of type bool"
        assert in_error == hthp.get_param("Stoerung")
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_query(self, hthp: HtHeatpump):
        values = hthp.query()
        # { "HKR Soll_Raum": 21.0,
        #   "Stoerung": False,
        #   "Temp. Aussen": 8.8,
        #   # ...
        #   }
        assert isinstance(values, dict), "'values' must be of type dict"
        assert len(values) == len(HtParams)
        for name, value in values.items():
            assert name in HtParams
            assert value is not None
            assert HtParams[name].in_limits(value)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize(
        "names",
        [
            random.sample(sorted(HtParams.keys()), cnt)
            for cnt in range(len(HtParams) + 1)
        ],
    )
    def test_query_with_names(self, hthp: HtHeatpump, names: List[str]):
        values = hthp.query(*names)
        # { "HKR Soll_Raum": 21.0,
        #   "Stoerung": False,
        #   "Temp. Aussen": 8.8,
        #   # ...
        #   }
        assert isinstance(values, dict), "'values' must be of type dict"
        assert not names or len(values) == len(set(names))
        for name, value in values.items():
            assert name in HtParams
            assert not names or name in names
            assert value is not None
            assert HtParams[name].in_limits(value)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_fast_query(self, hthp: HtHeatpump):
        values = hthp.fast_query()
        assert isinstance(values, dict), "'values' must be of type dict"
        assert len(values) == len(HtParams.of_type("MP"))
        for name, value in values.items():
            assert name in HtParams
            assert value is not None
            assert HtParams[name].in_limits(value)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize(
        "names",
        [
            random.sample(sorted(HtParams.of_type("MP").keys()), cnt)
            for cnt in range(len(HtParams.of_type("MP")) + 1)
        ],
    )
    def test_fast_query_with_names(self, hthp: HtHeatpump, names: List[str]):
        values = hthp.fast_query(*names)
        assert isinstance(values, dict), "'values' must be of type dict"
        assert not names or len(values) == len(set(names))
        for name, value in values.items():
            assert name in HtParams
            assert not names or name in names
            assert value is not None
            assert HtParams[name].in_limits(value)
        # assert 0

    def test_fast_query_with_names_raises_KeyError(
        self, cmdopt_device: str, cmdopt_baudrate: int
    ):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(KeyError):
            hp.fast_query("BlaBlaBla")
        # assert 0

    @pytest.mark.parametrize(
        "names",
        [
            random.sample(sorted(HtParams.of_type("SP").keys()), cnt)
            for cnt in range(1, len(HtParams.of_type("SP")) + 1)
        ],
    )
    def test_fast_query_with_names_raises_ValueError(
        self, cmdopt_device: str, cmdopt_baudrate: int, names: List[str]
    ):
        hp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
        with pytest.raises(ValueError):
            hp.fast_query(*names)
        # assert 0

    # @pytest.mark.skip(reason="test needs a rework")
    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_fast_query_in_several_pieces(self, hthp: HtHeatpump):
        args = []
        cmd = ""
        mp_data_points = [
            (name, param) for name, param in HtParams.items() if param.dp_type == "MP"
        ]
        while len(cmd) < 255 * 2:  # request has do be done in 3 parts
            name, param = random.choice(mp_data_points)
            cmd += ",{}".format(param.dp_number)
            args.append(name)
        values = hthp.fast_query(*args)
        assert isinstance(values, dict), "'values' must be of type dict"
        assert not args or len(values) == len(set(args))
        for name, value in values.items():
            assert name in HtParams
            assert not args or name in args
            assert value is not None
            assert HtParams[name].in_limits(value)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_time_progs(self, hthp: HtHeatpump):
        time_progs = hthp.get_time_progs()
        assert isinstance(time_progs, List), "'time_progs' must be of type list"
        assert len(time_progs) > 0
        assert all([isinstance(time_prog, TimeProgram) for time_prog in time_progs])
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize(
        "index", range(5)
    )  # TODO range(5) -> range(len(hthp.get_time_progs()))
    def test_get_time_prog(self, hthp: HtHeatpump, index: int):
        time_prog = hthp.get_time_prog(index, with_entries=False)
        assert isinstance(
            time_prog, TimeProgram
        ), "'time_prog' must be of type TimeProgram"
        time_prog = hthp.get_time_prog(index, with_entries=True)
        assert isinstance(
            time_prog, TimeProgram
        ), "'time_prog' must be of type TimeProgram"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("index", [-1, 5])
    def test_get_time_prog_raises_IOError(self, hthp: HtHeatpump, index: int):
        with pytest.raises(IOError):
            hthp.get_time_prog(index, with_entries=False)
        with pytest.raises(IOError):
            hthp.get_time_prog(index, with_entries=True)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize(
        "index, day, num",
        [  # for ALL time program entries
            (index, day, num)
            for index in range(5)
            for day in range(7)
            for num in range(7)
        ],
    )
    def test_get_time_prog_entry(
        self, hthp: HtHeatpump, index: int, day: int, num: int
    ):
        entry = hthp.get_time_prog_entry(index, day, num)
        assert isinstance(entry, TimeProgEntry), "'entry' must be of type TimeProgEntry"
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize(
        "index, day, num",
        [
            (5, 0, 0),  # index=5 is invalid
            (0, 7, 0),  # day=7 is invalid
            (0, 0, 7),  # num=7 is invalid
        ],
    )
    def test_get_time_prog_entry_raises_IOError(
        self, hthp: HtHeatpump, index: int, day: int, num: int
    ):
        with pytest.raises(IOError):
            hthp.get_time_prog_entry(index, day, num)
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_time_prog_entry(self, hthp: HtHeatpump):
        pass  # TODO
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_time_prog(self, hthp: HtHeatpump):
        pass  # TODO
        # assert 0


# TODO: add some more tests here
