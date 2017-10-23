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

""" Tests for code in htheatpump.htparams. """

import pytest
# import json
import re
# from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtDataTypes, HtParam, HtParams


class TestHtDataTypes:
    @pytest.mark.parametrize("str", [
        # -- should raise a 'ValueError':
        "none", "NONE",
        "string", "String",
        "bool", "Bool", "boolean", "Boolean", "BOOLEAN",
        "int", "Int", "integer", "Integer", "INTEGER",
        "float", "Float",
        "123456", "ÄbcDef", "äbcdef", "ab&def", "@bcdef", "aBcde$", "WzßrÖt",
        # ...
        ])
    def test_from_str_raises_ValueError(self, str):
        with pytest.raises(ValueError):
            HtDataTypes.from_str(str)
        #assert 0

    def test_from_str(self):
        assert HtDataTypes.from_str("None") is None
        assert HtDataTypes.from_str("STRING") == HtDataTypes.STRING
        assert HtDataTypes.from_str("BOOL") == HtDataTypes.BOOL
        assert HtDataTypes.from_str("INT") == HtDataTypes.INT
        assert HtDataTypes.from_str("FLOAT") == HtDataTypes.FLOAT
        #assert 0


class TestHtHtParam:
    @pytest.mark.parametrize("str, data_type, exp_value", [
        ("TestString", HtDataTypes.STRING, "TestString"),
        ("0", HtDataTypes.BOOL, False),
        ("1", HtDataTypes.BOOL, True),
        ("123", HtDataTypes.INT, 123),
        ("-321", HtDataTypes.INT, -321),
        ("123.456", HtDataTypes.FLOAT, 123.456),
        ("-321.456", HtDataTypes.FLOAT, -321.456),
        ("789", HtDataTypes.FLOAT, 789),
        # -- should raise a 'ValueError':
        ("Test", None, None),
        ("True", HtDataTypes.BOOL, None),
        ("False", HtDataTypes.BOOL, None),
        ("true", HtDataTypes.BOOL, None),
        ("false", HtDataTypes.BOOL, None),
        ("abc", HtDataTypes.BOOL, None),
        ("def", HtDataTypes.INT, None),
        ("--99", HtDataTypes.INT, None),
        ("12+55", HtDataTypes.INT, None),
        ("ghi", HtDataTypes.FLOAT, None),
        ("--99.0", HtDataTypes.FLOAT, None),
        ("12.3+55.9", HtDataTypes.FLOAT, None),
        # ...
    ])
    def test_conv_value(self, str, data_type, exp_value):
        if exp_value is None:
            with pytest.raises(ValueError):
                HtParam.conv_value(str, data_type)
        else:
            assert HtParam.conv_value(str, data_type) == exp_value
        #assert 0

    @pytest.mark.parametrize("name, cmd", [(name, param.cmd()) for name, param in HtParams.items()])
    def test_cmd_format(self, name, cmd):
        m = re.match("^[S|M]P,NR=(\d+)$", cmd)
        assert m is not None, "non valid command string ('%s') for parameter '%s'" % (cmd, name)
        #assert 0


class TestHtHtParams:
    @pytest.mark.parametrize("name, param", [(name, param) for name, param in HtParams.items()])
    def test_validate_param(self, name, param):
        pass  # TODO
        #assert 0


# TODO
# class HtParamsTestWithConnection(unittest.TestCase):
#     """ This is the unittest for the ``htheatpump.htparams`` code which **requires**
#         connection to the heat pump.
#     """
#
#     def setUp(self):
#         """ Initializes the test environment. """
#         with open('test_config.json') as config_file:
#             conn_settings = json.load(config_file)["connection"]
#         self.hp = HtHeatpump(**conn_settings)
#         self.hp.open_connection()
#         self.hp.login()
#
#     def tearDown(self):
#         """ Cleans up the test environment. """
#         self.hp.logout()
#         self.hp.close_connection()
#
#     def test_HtParamsValue(self):
#         params = HtParams.keys()
#         for p in sorted(params):
#             val = self.hp.get_param(p)
#             self.assertIsNotNone(val, "value of parameter '%s' must not be 'None'" % p)
#
#     def test_HtParamsDType(self):
#         params = HtParams.keys()
#         for p in sorted(params):
#             val = self.hp.get_param(p)
#             data_type = HtParams[p].data_type
#             self.assertIsNotNone(data_type, "data type of parameter '%s' must not be 'None'" % p)
#             if data_type == HtDataTypes.STRING:
#                 self.assertIsInstance(val, str, "value of parameter '%s' not of type 'str'" % p)
#             elif data_type == HtDataTypes.BOOL:
#                 self.assertIsInstance(val, bool, "value of parameter '%s' not of type 'bool'" % p)
#             elif data_type == HtDataTypes.INT:
#                 self.assertIsInstance(val, int, "value of parameter '%s' not of type 'int'" % p)
#             elif data_type == HtDataTypes.FLOAT:
#                 self.assertIsInstance(val, float, "value of parameter '%s' not of type 'float'" % p)
#             else:
#                 self.fail("unknown data type (%d) for parameter '%s'" % (data_type, p))  # should not happen!
#
#     def test_HtParamsLimits(self):
#         params = HtParams.keys()
#         for p in sorted(params):
#             val = self.hp.get_param(p)
#             self.assertIsNotNone(val, "value of parameter '%s' must not be 'None'" % p)
#             min = HtParams[p].min
#             if min is not None:
#                 self.assertGreaterEqual(val, min, "value (%s) of parameter '%s' must >= %s" % (str(val), p, str(min)))
#             max = HtParams[p].max
#             if max is not None:
#                 self.assertLessEqual(val, max, "value (%s) of parameter '%s' must <= %s" % (str(val), p, str(max)))


# TODO: add some more tests here
