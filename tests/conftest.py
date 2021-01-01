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

import logging

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--connected", action="store_true", dest="run_if_connected", default=False
    )
    parser.addoption("--device", action="store", default="/dev/ttyUSB0")
    parser.addoption("--baudrate", action="store", default=115200)
    parser.addoption("--loglevel", action="store", default=logging.WARNING)


def pytest_configure(config):
    if not config.option.run_if_connected:
        setattr(config.option, "markexpr", "not run_if_connected")

    loglevel = int(config.getoption("--loglevel"))
    logging.basicConfig(level=loglevel)

    print("connected: {}".format("NO" if not config.option.run_if_connected else "YES"))
    print("device: {}".format(config.getoption("--device")))
    print("baudrate: {:d}".format(int(config.getoption("--baudrate"))))
    print("loglevel: {:d}".format(loglevel))


@pytest.fixture(scope="session")
def cmdopt_device(request):
    return request.config.getoption("--device")


@pytest.fixture(scope="session")
def cmdopt_baudrate(request):
    return request.config.getoption("--baudrate")
