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

""" Tests for code in `htheatpump.htheatpump`. """

import pytest
import re
import datetime
import random
from htheatpump.htparams import HtParam, HtParams
from htheatpump.htheatpump import HtHeatpump
from htheatpump.httimeprog import TimeProgEntry, TimeProgram
from typing import List


@pytest.mark.parametrize("s, checksum", [(b"", 0x0)])  # TODO add some more samples
def test_calc_checksum(s: bytes, checksum: int):
    from htheatpump.htheatpump import calc_checksum
    assert calc_checksum(s) == checksum
    #assert 0


@pytest.mark.parametrize("s", [b"", b"\x01"])
def test_verify_checksum_raises_ValueError(s: bytes):
    from htheatpump.htheatpump import verify_checksum
    with pytest.raises(ValueError):
        verify_checksum(s)
    #assert 0


@pytest.mark.parametrize("s, result", [(b"\x00\x00", True)])  # TODO add some more samples
def test_verify_checksum(s: bytes, result: bool):
    from htheatpump.htheatpump import verify_checksum
    assert verify_checksum(s) == result
    #assert 0


@pytest.mark.parametrize("s", [b""])
def test_add_checksum_raises_ValueError(s: bytes):
    from htheatpump.htheatpump import add_checksum
    with pytest.raises(ValueError):
        add_checksum(s)
    #assert 0


@pytest.mark.parametrize("s, result", [(b"\x00", b"\x00\x00")])  # TODO add some more samples
def test_add_checksum(s: bytes, result: bytes):
    from htheatpump.htheatpump import add_checksum
    assert add_checksum(s) == result
    #assert 0


@pytest.mark.parametrize("cmd", ["?" * 254])
def test_create_request_raises_ValueError(cmd: str):
    from htheatpump.htheatpump import create_request
    with pytest.raises(ValueError):
        create_request(cmd)
    #assert 0


@pytest.mark.parametrize("cmd, result", [("", b"\x02\xfd\xd0\xe0\x00\x00\x02~;\x98")])  # TODO add some more samples
def test_create_request(cmd: str, result: bytes):
    from htheatpump.htheatpump import create_request
    assert create_request(cmd) == result
    #assert 0


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
    @pytest.mark.usefixtures("reconnect")
    def test_get_serial_number(self, hthp: HtHeatpump):
        rid = hthp.get_serial_number()
        assert isinstance(rid, int), "'rid' must be of type int"
        assert rid > 0
        #assert 0

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
        assert m is not None, "invalid response for query of the software version [{!r}]".format(resp)
        assert ver_str == m.group(1).strip()
        assert ver_num == int(m.group(2))
        #assert 0

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
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_date_time(self, hthp: HtHeatpump):
        pass  # TODO
        #assert 0

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
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_size(self, hthp: HtHeatpump):
        size = hthp.get_fault_list_size()
        assert isinstance(size, int), "'size' must be of type int"
        assert size >= 0
        #assert 0

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
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_with_index(self, hthp: HtHeatpump):
        size = hthp.get_fault_list_size()
        assert isinstance(size, int), "'size' must be of type int"
        assert size >= 0
        for i in range(size):
            entry = hthp.get_fault_list(i)
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
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_fault_list_with_index_raises_IOError(self, hthp: HtHeatpump):
        with pytest.raises(IOError):
            hthp.get_fault_list(-1)    # index=-1 is invalid
        with pytest.raises(IOError):
            hthp.get_fault_list(9999)  # index=9999 is invalid
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_get_param(self, hthp: HtHeatpump, name: str, param: HtParam):
        value = hthp.get_param(name)
        assert value is not None, "'value' must not be None"
        assert param.in_limits(value)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_set_param(self, hthp: HtHeatpump, name: str, param: HtParam):
        pass  # TODO
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_in_error(self, hthp: HtHeatpump):
        in_error = hthp.in_error
        assert isinstance(in_error, bool), "'in_error' must be of type bool"
        assert in_error == hthp.get_param("Stoerung")
        #assert 0

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
        for n, v in values.items():
            assert n in HtParams
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("names", [random.sample(HtParams.keys(), cnt)
                                       for cnt in range(len(HtParams) + 1)])
    def test_query_with_names(self, hthp: HtHeatpump, names: List[str]):
        values = hthp.query(*names)
        # { "HKR Soll_Raum": 21.0,
        #   "Stoerung": False,
        #   "Temp. Aussen": 8.8,
        #   # ...
        #   }
        assert isinstance(values, dict), "'values' must be of type dict"
        assert not names or len(values) == len(set(names))
        for n, v in values.items():
            assert n in HtParams
            assert not names or n in names
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_fast_query(self, hthp: HtHeatpump):
        values = hthp.fast_query()
        assert isinstance(values, dict), "'values' must be of type dict"
        assert len(values) == len(HtParams.of_type("MP"))
        for n, v in values.items():
            assert n in HtParams
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("names", [random.sample(HtParams.of_type("MP").keys(), cnt)
                                       for cnt in range(len(HtParams.of_type("MP")) + 1)])
    def test_fast_query_with_names(self, hthp: HtHeatpump, names: List[str]):
        values = hthp.fast_query(*names)
        assert isinstance(values, dict), "'values' must be of type dict"
        assert not names or len(values) == len(set(names))
        for n, v in values.items():
            assert n in HtParams
            assert not names or n in names
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_time_progs(self, hthp: HtHeatpump):
        time_progs = hthp.get_time_progs()
        assert isinstance(time_progs, List), "'time_progs' must be of type list"
        assert all([isinstance(time_prog, TimeProgram) for time_prog in time_progs])
        assert len(time_progs) > 0
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("index", range(5))  # TODO range(5) -> range(len(hthp.get_time_progs()))
    def test_get_time_prog(self, hthp: HtHeatpump, index: int):
        time_prog = hthp.get_time_prog(index, with_entries=False)
        assert isinstance(time_prog, TimeProgram), "'time_prog' must be of type TimeProgram"
        time_prog = hthp.get_time_prog(index, with_entries=True)
        assert isinstance(time_prog, TimeProgram), "'time_prog' must be of type TimeProgram"
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("index, day, num", [  # for ALL time program entries
        (index, day, num) for index in range(5) for day in range(7) for num in range(7)
    ])
    def test_get_time_prog_entry(self, hthp: HtHeatpump, index: int, day: int, num: int):
        entry = hthp.get_time_prog_entry(index, day, num)
        assert isinstance(entry, TimeProgEntry), "'entry' must be of type TimeProgEntry"
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_get_time_prog_entry_raises_IOError(self, hthp: HtHeatpump):
        with pytest.raises(IOError):
            hthp.get_time_prog_entry(5, 7, 0)  # index=5 is invalid
        with pytest.raises(IOError):
            hthp.get_time_prog_entry(0, 7, 0)  # day=7 is invalid
        with pytest.raises(IOError):
            hthp.get_time_prog_entry(0, 0, 7)  # num=7 is invalid
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_time_prog_entry(self, hthp: HtHeatpump):
        pass  # TODO
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    def test_set_time_prog(self, hthp: HtHeatpump):
        pass  # TODO
        #assert 0


# TODO: add some more tests here
