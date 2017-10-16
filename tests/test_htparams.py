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

# import json
import re
# from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParams
#, HtDataTypes
from random import shuffle


def test_HtParamsCmdFormat():
    params = list(HtParams.keys())
    shuffle(params)  # shuffle list (in-place) to get a lesser deterministic test case!
    for p in params:
        cmd = HtParams[p].cmd
        m = re.match("^[S|M]P,NR=(\d+)$", cmd)
        assert m is not None, "non valid command string ('%s') for parameter '%s'" % (cmd, p)

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
#             dtype = HtParams[p].dtype
#             self.assertIsNotNone(dtype, "data type of parameter '%s' must not be 'None'" % p)
#             if dtype == HtDataTypes.STRING:
#                 self.assertIsInstance(val, str, "value of parameter '%s' not of type 'str'" % p)
#             elif dtype == HtDataTypes.BOOL:
#                 self.assertIsInstance(val, bool, "value of parameter '%s' not of type 'bool'" % p)
#             elif dtype == HtDataTypes.INT:
#                 self.assertIsInstance(val, int, "value of parameter '%s' not of type 'int'" % p)
#             elif dtype == HtDataTypes.FLOAT:
#                 self.assertIsInstance(val, float, "value of parameter '%s' not of type 'float'" % p)
#             else:
#                 self.fail("unknown data type (%d) for parameter '%s'" % (dtype, p))  # should not happen!
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
