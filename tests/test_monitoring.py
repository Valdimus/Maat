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
# Description: Test monitoring classes

import gc
import os
import pwd
import time
import pytest
from maat import Monitoring
from maat import PLSMonitoring
from tests import FakeStudio


@pytest.yield_fixture(autouse=True)
def fakeservice():
    """
    Create a fake service to check that we can monitor a Process Launcher service for users. (one or more process by
    user)
    """

    fake_service = FakeStudio(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fake_service.py"))

    yield fake_service

    del fake_service
    gc.collect()


def test_montoring():
    """Test that we can get some information about the host like CPU/Memory/Swap usage percent"""
    monitoring = Monitoring()

    temp = monitoring.data

    # Cpu check
    assert("cpu" in temp)
    assert("percent" in temp["cpu"])
    assert(type(temp["cpu"]["percent"]) == float)
    assert("times" in temp["cpu"])
    assert(type(temp["cpu"]["times"]) == dict)
    assert("count" in temp["cpu"])
    assert(type(temp["cpu"]["count"]) == int)
    assert("freq" in temp["cpu"])
    assert(type(temp["cpu"]["freq"]) == dict)
    assert("stats" in temp["cpu"])
    assert(type(temp["cpu"]["stats"]) == dict)

    # Memory check
    assert("memory" in temp)
    assert (type(temp["memory"]) == dict)

    # Swap check
    assert("swap" in temp)
    assert (type(temp["swap"]) == dict)

    # assert(monitoring.force_data != temp)


def test_pls_one_session(fakeservice):
    """
    Test that PLSMonitoring can see that the PLS launch a session for a user
    """

    pls = PLSMonitoring(process_name="FakeService", interval=0.1)

    # No client should be available
    assert(pls.data == [])
    assert(pls.list_username() == [])
    assert(pls.user_exist("Toto") is None)
    assert(pls.number() == 0)

    # Get the current username
    username = pwd.getpwuid(os.getuid()).pw_name

    # Create a session for this user
    assert(fakeservice.spawn_client(username) is True)

    # Check that this user have a session in the monitoring
    mtime = time.time()
    while pls.number() == 0:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Session seem to not start!")
    assert(len(pls.data) == 1)
    assert(pls.list_username() == [username])
    assert(pls.user_exist(username) is not None)
    assert(pls.user_exist("Toto123456789Toto") is None)
    assert(pls.number() == 1)

    # Erase the client session's
    fakeservice.stop_client(username)

    del fakeservice
    gc.collect()

    # Check that the client don't have any session
    mtime = time.time()
    while pls.number() > 0:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Session seem to be still available!")

    assert (len(pls.data) == 0)
    assert (pls.list_username() == [])
    assert (pls.user_exist(username) is None)
    assert (pls.user_exist("Toto123456789Toto") is None)
    assert (pls.number() == 0)


# Todo:
# Test that we can watch multiple session for an user
