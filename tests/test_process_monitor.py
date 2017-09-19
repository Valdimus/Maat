# coding: utf-8

# Copyright (C) 2017 NOUCHET Christophe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

# Author: Christophe Nouchet
# Email: nouchet.christophe@gmail.com
# Date: 25/03/2017
# Description: Test CachedData class

import os
import gc
import pwd
import time
import pytest
from maat import ProcessMonitoring
from tests import FakeStudio


@pytest.yield_fixture(autouse=True)
def fake_studio():

    fake_service = FakeStudio(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fake_service.py"))

    yield fake_service

    del fake_service
    gc.collect()


def test_assignment():
    """Test value assignement"""

    pm = ProcessMonitoring()

    assert(pm.process_name == "FakeService")

    pm = ProcessMonitoring(process_name="Toto")

    assert(pm.process_name == "Toto")


def test_get_process(fake_studio):
    """Check if we saw an application spawning"""
    pm = ProcessMonitoring(process_name="FakeService", interval=0.1)
    username = pwd.getpwuid(os.getuid()).pw_name
    data = pm.data

    assert(len(data["processes"]) == 0)
    assert(len(data["users"]) == 0)
    assert(data["nb"] == 0)

    fake_studio.spawn_client(username)

    time.sleep(0.2)
    data = pm.data
    print(data)
    assert(len(data["processes"]) == 1)
    assert(len(data["users"]) == 1)
    assert(len(data["users"][username]) == 1)
    assert(data["nb"] == 1)

    fake_studio.spawn_client(username)

    time.sleep(0.2)
    data = pm.data

    assert(len(data["processes"]) == 2)
    assert(len(data["users"]) == 1)
    assert(len(data["users"][username]) == 2)
    assert(data["nb"] == 2)

    fake_studio.stop_all()


def test_exception_in_comparator():
    class ProcessMonitoringException(ProcessMonitoring):

        def comparator(self, process_info):
            raise Exception("Error")

    pr = ProcessMonitoringException()

    assert(pr.get_processes() == [])
