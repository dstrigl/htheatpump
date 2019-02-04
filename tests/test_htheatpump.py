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
from htheatpump.htparams import HtParams
from htheatpump.htheatpump import HtHeatpump


@pytest.fixture(scope="class")
def hthp(cmdopt_device, cmdopt_baudrate):
    #hthp = HtHeatpump(device="/dev/ttyUSB0", baudrate=115200)
    hthp = HtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
    try:
        hthp.open_connection()
        hthp.login()
        yield hthp  # provide the heat pump instance
    finally:
        hthp.logout()  # try to logout for an ordinary cancellation (if possible)
        hthp.close_connection()


@pytest.mark.run_if_connected
def test_hthp_is_not_None(hthp):
    assert hthp is not None
    assert hthp.is_open
    #assert 0


class TestHtHeatpump:
    @pytest.mark.run_if_connected
    def test_get_serial_number(self, hthp):
        rid = hthp.get_serial_number()
        assert isinstance(rid, int)
        assert rid > 0
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_version(self, hthp):
        ret = hthp.get_version()
        # ( "3.0.20", 2321 )
        assert isinstance(ret, tuple)
        assert len(ret) == 2
        ver_str, ver_num = ret
        assert isinstance(ver_str, str)
        m = re.match(r"^(\d+).(\d+).(\d+)$", ver_str)
        assert m is not None, "invalid version string [{!r}]".format(ver_str)
        assert isinstance(ver_num, int)
        assert ver_num > 0
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_date_time(self, hthp):
        ret = hthp.get_date_time()
        # (datetime.datetime(...), 2)  # 2 = Tuesday
        assert isinstance(ret, tuple)
        assert len(ret) == 2
        dt, weekday = ret
        assert isinstance(dt, datetime.datetime)
        assert isinstance(weekday, int)
        assert weekday in range(1, 8)
        #assert 0

    @pytest.mark.run_if_connected
    def test_set_date_time(self, hthp):
        pass  # TODO
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_last_fault(self, hthp):
        ret = hthp.get_last_fault()
        # (29, 20, datetime.datetime(...), "EQ_Spreizung")
        assert isinstance(ret, tuple)
        assert len(ret) == 4
        index, error, dt, msg = ret
        assert isinstance(index, int)
        assert 0 <= index < hthp.get_fault_list_size()
        assert isinstance(error, int)
        assert error >= 0
        assert isinstance(dt, datetime.datetime)
        assert isinstance(msg, str)
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_fault_list_size(self, hthp):
        ret = hthp.get_fault_list_size()
        assert isinstance(ret, int)
        assert ret >= 0
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_fault_list(self, hthp):
        ret = hthp.get_fault_list()
        # [ { "index": 29,  # fault list index
        #     "error": 20,  # error code
        #     "datetime": datetime.datetime(...),  # date and time of the entry
        #     "message": "EQ_Spreizung",  # error message
        #     },
        #   # ...
        #   ]
        assert isinstance(ret, list)
        for e in ret:
            assert isinstance(e, dict)
            index = e["index"]
            assert isinstance(index, int)
            assert 0 <= index < hthp.get_fault_list_size()
            error = e["error"]
            assert isinstance(error, int)
            assert error >= 0
            dt = e["datetime"]
            assert isinstance(dt, datetime.datetime)
            msg = e["message"]
            assert isinstance(msg, str)
        #assert 0

    @pytest.mark.run_if_connected
    def test_get_fault_list_with_indices(self, hthp):
        pass  # TODO
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.parametrize("name, param", [(name, param) for name, param in HtParams.items()])
    def test_get_param(self, hthp, name, param):
        ret = hthp.get_param(name)
        assert ret is not None
        assert param.in_limits(ret)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.parametrize("name, param", [(name, param) for name, param in HtParams.items()])
    def test_set_param(self, hthp, name, param):
        pass  # TODO
        #assert 0

    @pytest.mark.run_if_connected
    def test_in_error(self, hthp):
        ret = hthp.in_error
        assert isinstance(ret, bool)
        assert ret == hthp.get_param("Stoerung")
        #assert 0

    @pytest.mark.run_if_connected
    def test_query(self, hthp):
        ret = hthp.query()
        # { "HKR Soll_Raum": 21.0,
        #   "Stoerung": False,
        #   "Temp. Aussen": 8.8,
        #   # ...
        #   }
        assert isinstance(ret, dict)
        for n, v in ret.items():
            assert n in HtParams
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.parametrize("names", [random.sample(HtParams.keys(), cnt)
                                       for cnt in range(0, len(HtParams) + 1)])
    def test_query_with_names(self, hthp, names):
        ret = hthp.query(*names)
        # { "HKR Soll_Raum": 21.0,
        #   "Stoerung": False,
        #   "Temp. Aussen": 8.8,
        #   # ...
        #   }
        assert isinstance(ret, dict)
        for n, v in ret.items():
            assert n in HtParams
            assert n in names
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    def test_fast_query(self, hthp):
        ret = hthp.fast_query()
        assert isinstance(ret, dict)
        for n, v in ret.items():
            assert n in HtParams
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.parametrize("names", [random.sample(HtParams.of_type("MP").keys(), cnt)
                                       for cnt in range(0, len(HtParams.of_type("MP")) + 1)])
    def test_fast_query_with_names(self, hthp, names):
        ret = hthp.fast_query(*names)
        assert isinstance(ret, dict)
        for n, v in ret.items():
            assert n in HtParams
            assert n in names
            assert v is not None
            assert HtParams[n].in_limits(v)
        #assert 0


# TODO: add some tests here
