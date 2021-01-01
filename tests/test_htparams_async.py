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

""" Async tests for code in `htheatpump.htparams`. """

import re
from typing import Optional

import pytest

from htheatpump import AioHtHeatpump, HtDataTypes, HtParam, HtParams, HtParamValueType


class TestHtDataTypes:
    @pytest.mark.parametrize(
        "s",
        [
            # -- should raise a 'ValueError':
            "none",
            "NONE",
            "None",
            "string",
            "String",
            "bool",
            "Bool",
            "boolean",
            "Boolean",
            "BOOLEAN",
            "int",
            "Int",
            "integer",
            "Integer",
            "INTEGER",
            "float",
            "Float",
            "123456",
            "ÄbcDef",
            "äbcdef",
            "ab&def",
            "@bcdef",
            "aBcde$",
            "WzßrÖt",
            # ...
        ],
    )
    def test_from_str_raises_ValueError(self, s: str):
        with pytest.raises(ValueError):
            HtDataTypes.from_str(s)
        # assert 0

    def test_from_str(self):
        assert HtDataTypes.from_str("BOOL") == HtDataTypes.BOOL
        assert HtDataTypes.from_str("INT") == HtDataTypes.INT
        assert HtDataTypes.from_str("FLOAT") == HtDataTypes.FLOAT
        # assert 0


class TestHtParam:
    @pytest.mark.parametrize(
        "s, data_type, exp_value, strict",
        [
            ("0", HtDataTypes.BOOL, False, False),
            ("1", HtDataTypes.BOOL, True, False),
            ("123", HtDataTypes.INT, 123, False),
            ("-321", HtDataTypes.INT, -321, False),
            ("123.456", HtDataTypes.FLOAT, 123.456, False),
            ("-321.456", HtDataTypes.FLOAT, -321.456, False),
            ("789", HtDataTypes.FLOAT, 789.0, False),
            # -- should raise a 'ValueError':
            ("True", HtDataTypes.BOOL, None, False),
            ("False", HtDataTypes.BOOL, None, False),
            ("true", HtDataTypes.BOOL, None, False),
            ("false", HtDataTypes.BOOL, None, False),
            ("yes", HtDataTypes.BOOL, None, False),
            ("no", HtDataTypes.BOOL, None, False),
            ("y", HtDataTypes.BOOL, None, False),
            ("n", HtDataTypes.BOOL, None, False),
            ("TRUE", HtDataTypes.BOOL, None, False),
            ("FALSE", HtDataTypes.BOOL, None, False),
            ("YES", HtDataTypes.BOOL, None, False),
            ("NO", HtDataTypes.BOOL, None, False),
            ("Y", HtDataTypes.BOOL, None, False),
            ("N", HtDataTypes.BOOL, None, False),
            ("abc", HtDataTypes.BOOL, None, False),
            ("def", HtDataTypes.INT, None, False),
            ("--99", HtDataTypes.INT, None, False),
            ("12+55", HtDataTypes.INT, None, False),
            ("ghi", HtDataTypes.FLOAT, None, False),
            ("--99.0", HtDataTypes.FLOAT, None, False),
            ("12.3+55.9", HtDataTypes.FLOAT, None, False),
            ("789", HtDataTypes.FLOAT, None, True),
            # -- should raise a 'TypeError':
            (123, HtDataTypes.BOOL, None, False),
            (123, HtDataTypes.INT, None, False),
            (123, HtDataTypes.FLOAT, None, False),
            (123.123, HtDataTypes.BOOL, None, False),
            (123.123, HtDataTypes.INT, None, False),
            (123.123, HtDataTypes.FLOAT, None, False),
            (True, HtDataTypes.BOOL, None, False),
            (True, HtDataTypes.INT, None, False),
            (True, HtDataTypes.FLOAT, None, False),
            (False, HtDataTypes.BOOL, None, False),
            (False, HtDataTypes.INT, None, False),
            (False, HtDataTypes.FLOAT, None, False),
            (None, HtDataTypes.BOOL, None, False),
            (None, HtDataTypes.INT, None, False),
            (None, HtDataTypes.FLOAT, None, False),
            # ...
        ],
    )
    def test_from_str_static(
        self,
        s: str,
        data_type: HtDataTypes,
        exp_value: Optional[HtParamValueType],
        strict: bool,
    ):
        if exp_value is None:
            with pytest.raises((TypeError, ValueError)):
                HtParam.from_str(s, data_type, strict)
        else:
            assert HtParam.from_str(s, data_type, strict) == exp_value
        # assert 0

    @pytest.mark.parametrize("data_type", [None, "", 123, 123.123, True, False])
    def test_from_str_static_assert(self, data_type):
        with pytest.raises(AssertionError):
            HtParam.from_str("", data_type)
        # assert 0

    @pytest.mark.parametrize("param", HtParams.values())
    def test_from_str_member(self, param: HtParam):
        assert param.from_str(param.to_str(param.min_val)) == param.min_val  # type: ignore
        assert param.from_str(param.to_str(param.max_val)) == param.max_val  # type: ignore
        # assert 0

    @pytest.mark.parametrize(
        "val, data_type, exp_str",
        [
            (False, HtDataTypes.BOOL, "0"),
            (True, HtDataTypes.BOOL, "1"),
            (123, HtDataTypes.INT, "123"),
            (-321, HtDataTypes.INT, "-321"),
            (123.456, HtDataTypes.FLOAT, "123.456"),
            (-321.456, HtDataTypes.FLOAT, "-321.456"),
            (789, HtDataTypes.FLOAT, "789.0"),
            (-789, HtDataTypes.FLOAT, "-789.0"),
            (789.0, HtDataTypes.FLOAT, "789.0"),
            (-789.0, HtDataTypes.FLOAT, "-789.0"),
            # -- should raise a 'TypeError':
            (None, HtDataTypes.BOOL, None),
            ("abc", HtDataTypes.BOOL, None),
            (123, HtDataTypes.BOOL, None),
            (123.123, HtDataTypes.BOOL, None),
            (None, HtDataTypes.INT, None),
            ("abc", HtDataTypes.INT, None),
            (123.123, HtDataTypes.INT, None),
            (None, HtDataTypes.FLOAT, None),
            ("abc", HtDataTypes.FLOAT, None),
            # ...
        ],
    )
    def test_to_str_static(
        self, val: HtParamValueType, data_type: HtDataTypes, exp_str: str
    ):
        if exp_str is None:
            with pytest.raises(TypeError):
                HtParam.to_str(val, data_type)
        else:
            assert HtParam.to_str(val, data_type) == exp_str
        # assert 0

    @pytest.mark.parametrize("param", HtParams.values())
    def test_to_str_member(self, param: HtParam):
        assert param.to_str(param.min_val) == HtParam.to_str(param.min_val, param.data_type)  # type: ignore
        assert param.to_str(param.max_val) == HtParam.to_str(param.max_val, param.data_type)  # type: ignore
        # assert 0

    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_repr(self, name: str, param: HtParam):
        assert repr(param) == "HtParam({},{:d},{!r},{}[{},{}])".format(
            param.dp_type,
            param.dp_number,
            param.acl,
            param.data_type,
            param.min_val,
            param.max_val,
        )
        # assert 0

    @pytest.mark.parametrize(
        "name, cmd", [(name, param.cmd()) for name, param in HtParams.items()]
    )
    def test_cmd(self, name: str, cmd: str):
        m = re.match(r"^[S|M]P,NR=(\d+)$", cmd)
        assert (
            m is not None
        ), "non valid command string for parameter {!r} [{!r}]".format(name, cmd)
        # assert 0

    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_set_limits(self, name: str, param: HtParam):
        assert not param.set_limits(param.min_val, param.max_val)
        # assert 0

    @pytest.mark.parametrize(
        "data_type, min_val, max_val",
        [
            # -- should raise a 'TypeError':
            (HtDataTypes.BOOL, False, 123),
            (HtDataTypes.BOOL, False, 123.123),
            (HtDataTypes.BOOL, 123, True),
            (HtDataTypes.BOOL, 123.123, True),
            (HtDataTypes.BOOL, False, ""),
            (HtDataTypes.BOOL, "", True),
            (HtDataTypes.BOOL, "", ""),
            (HtDataTypes.BOOL, None, 123),
            (HtDataTypes.BOOL, 123, None),
            (HtDataTypes.INT, 123, 123.123),
            (HtDataTypes.INT, 122.123, 123),
            (HtDataTypes.INT, 122.123, 123.123),
            (HtDataTypes.INT, 123, ""),
            (HtDataTypes.INT, "", 123),
            (HtDataTypes.INT, "", ""),
            (HtDataTypes.INT, 123, True),
            (HtDataTypes.INT, False, 123),
            (HtDataTypes.INT, True, False),
            (HtDataTypes.INT, False, True),
            (HtDataTypes.INT, None, 123.123),
            (HtDataTypes.INT, 123.123, None),
            (HtDataTypes.FLOAT, 123, ""),
            (HtDataTypes.FLOAT, "", 123),
            (HtDataTypes.FLOAT, 123.123, ""),
            (HtDataTypes.FLOAT, "", 123.123),
            (HtDataTypes.FLOAT, "", ""),
            (HtDataTypes.FLOAT, 123, True),
            (HtDataTypes.FLOAT, False, 123),
            (HtDataTypes.FLOAT, 123.123, True),
            (HtDataTypes.FLOAT, False, 123.123),
            (HtDataTypes.FLOAT, True, False),
            (HtDataTypes.FLOAT, False, True),
            (HtDataTypes.FLOAT, None, True),
            (HtDataTypes.FLOAT, True, None),
            # ...
        ],
    )
    def test_set_limits_raises_TypeError(self, data_type, min_val, max_val):
        param = HtParam("MP", 123, "r-", data_type)
        with pytest.raises(TypeError):
            param.set_limits(min_val, max_val)
        # assert 0

    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_in_limits(self, name: str, param: HtParam):
        assert param.in_limits(param.min_val)
        assert param.in_limits(param.max_val)
        # assert 0

    @pytest.mark.parametrize("param", HtParams.values())
    def test_in_limits_None(self, param: HtParam):
        assert param.in_limits(None)
        # assert 0

    @pytest.mark.parametrize(
        "val, data_type",
        [
            (False, HtDataTypes.BOOL),
            (True, HtDataTypes.BOOL),
            (123, HtDataTypes.INT),
            (-321, HtDataTypes.INT),
            (123.456, HtDataTypes.FLOAT),
            (-321.456, HtDataTypes.FLOAT),
            (789, HtDataTypes.FLOAT),
            (-789, HtDataTypes.FLOAT),
            (789.0, HtDataTypes.FLOAT),
            (-789.0, HtDataTypes.FLOAT),
            # ...
        ],
    )
    def test_check_value_type(self, val, data_type):
        HtParam.check_value_type(val, data_type)
        # assert 0

    @pytest.mark.parametrize(
        "val, data_type",
        [
            # -- should raise a 'TypeError':
            (None, HtDataTypes.BOOL),
            ("abc", HtDataTypes.BOOL),
            (123, HtDataTypes.BOOL),
            (123.123, HtDataTypes.BOOL),
            (None, HtDataTypes.INT),
            ("abc", HtDataTypes.INT),
            (123.123, HtDataTypes.INT),
            (None, HtDataTypes.FLOAT),
            ("abc", HtDataTypes.FLOAT),
            # ...
        ],
    )
    def test_check_value_type_raises_TypeError(self, val, data_type):
        with pytest.raises(TypeError):
            HtParam.check_value_type(val, data_type)
        # assert 0


@pytest.fixture(scope="class")
def hthp(cmdopt_device: str, cmdopt_baudrate: int):
    hthp = AioHtHeatpump(device=cmdopt_device, baudrate=cmdopt_baudrate)
    try:
        hthp.open_connection()
        yield hthp  # provide the heat pump instance
    finally:
        hthp.close_connection()


@pytest.fixture()
async def reconnect(hthp: AioHtHeatpump):
    hthp.reconnect()
    await hthp.login_async()
    yield
    await hthp.logout_async()


class TestHtParams:
    @pytest.mark.parametrize(
        "name, acl", [(name, param.acl) for name, param in HtParams.items()]
    )
    def test_acl(self, name: str, acl: str):
        assert acl is not None, "'acl' must not be None"
        m = re.match(r"^(r-|-w|rw)$", acl)
        assert m is not None, "invalid acl definition for parameter {!r} [{!r}]".format(
            name, acl
        )
        # assert 0

    @pytest.mark.parametrize(
        "name, min_val, max_val",
        [(name, param.min_val, param.max_val) for name, param in HtParams.items()],
    )
    def test_limits(
        self, name: str, min_val: HtParamValueType, max_val: HtParamValueType
    ):
        assert (
            min_val is not None
        ), "minimal value for parameter {!r} must not be None".format(name)
        assert (
            max_val is not None
        ), "maximal value for parameter {!r} must not be None".format(name)
        assert min_val <= max_val
        assert max_val >= min_val
        # assert 0

    @pytest.mark.parametrize("name, param", HtParams.items())
    def test_get(self, name: str, param: HtParam):
        assert HtParams.get(name) == param
        # assert 0

    def test_dump(self):
        assert HtParams.dump() is None
        # assert 0

    @pytest.mark.run_if_connected
    @pytest.mark.usefixtures("reconnect")
    @pytest.mark.parametrize("name, param", HtParams.items())
    @pytest.mark.asyncio
    async def test_validate_param(self, hthp: AioHtHeatpump, name: str, param: HtParam):
        await hthp.send_request_async(param.cmd())
        resp = await hthp.read_response_async()
        m = re.match(
            r"^{},.*NAME=([^,]+).*VAL=([^,]+).*MAX=([^,]+).*MIN=([^,]+).*$".format(
                param.cmd()
            ),
            resp,
        )
        assert (
            m is not None
        ), "invalid response for query of parameter {!r} [{!r}]".format(name, resp)
        dp_name = m.group(1).strip()
        assert (
            dp_name == name
        ), "data point name doesn't match with the parameter name {!r} [{!r}]".format(
            name, dp_name
        )
        dp_value = param.from_str(m.group(2))
        assert dp_value is not None, "data point value must not be None [{}]".format(
            dp_value
        )
        dp_max = param.from_str(m.group(3))
        assert (
            dp_max == param.max_val
        ), "data point max value doesn't match with the parameter's one {!s} [{!s}]".format(
            param.max_val, dp_max
        )
        dp_min = param.from_str(m.group(4))
        if name == "Verdichter laeuft seit" and dp_min == 10:
            dp_min = 0  # seems to be incorrect for the data point "Verdichter laeuft seit" [10 == 0]
        assert (
            dp_min == param.min_val
        ), "data point min value doesn't match with the parameter's one {!s} [{!s}]".format(
            param.min_val, dp_min
        )
        # assert 0


# TODO: add some more tests here
