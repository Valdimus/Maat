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

import os
import time
from flask import Flask
import pytest
from maat import PLSBackend
import multiprocessing as mp
from tests import get_open_port
from tests import create_fake_pls_backend


@pytest.yield_fixture(autouse=True)
def fakebackend():
    """
    Directory fixture
    Will create directory and temp file for testing storage services
    :return:
    """

    port = get_open_port()

    # Create the fake backend
    def run_this():
        create_fake_pls_backend(host="127.0.0.1", port=port, interval=30)

    process = mp.Process(target=run_this)

    yield (process, port)

    if process.is_alive():
        process.terminate()


def test_basic():
    """Basic test"""
    pls = PLSBackend(agent_port=5005, hostname="127.0.0.1", port=5000, protocol="http")

    assert(pls.agent_port == 5005)
    assert(pls.agent_url() == "http://127.0.0.1:5005")
    assert(pls.agent_url("/test") == "http://127.0.0.1:5005/test")
    assert(pls.monitoring == pls._default_value_monitoring())
    assert(pls.sessions == pls._default_value_pls())
    assert(pls.nb_users == 0)
    assert(pls.user_list == [])
    assert (pls.user_monitoring_sessions("toto") == [])
    assert (pls.nb_user_sessions("toto") == 0)
    assert (pls.to_dict() == {
        "name": pls.name,
        "hostname": pls.hostname,
        "url": pls.url(),
        "ping_url": pls.ping_url,
        "available": pls.available,
        "nb_users": pls.nb_users
    })
    assert(pls.max_session_per_user == 1)
    assert(pls.user_reach_max_session("toto") is False)


def test_backend(fakebackend):
    """Test that the backend is correctly usable"""
    fk, port = fakebackend
    pls = PLSBackend(
        agent_port=port, hostname="127.0.0.1", port=port, protocol="http",
        monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
    )
    assert(pls.available is False)
    assert(pls.monitoring == pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_users == 0)
    assert (pls.user_list == [])
    assert (pls.user_monitoring_sessions("christophe") == [])
    assert (pls.nb_user_sessions("christophe") == 0)
    assert (pls.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (pls.user_reach_max_session("toto") is False)

    # Start the fake backend
    fk.start()
    time.sleep(0.1)

    assert (pls.available is True)
    assert (pls.monitoring != pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_users == 0)
    assert (pls.user_list == [])
    assert (pls.user_monitoring_sessions("christophe") == [])
    assert (pls.nb_user_sessions("christophe") == 0)
    assert (pls.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (pls.user_reach_max_session("toto") is False)

    # Add a user
    r = pls.make_request(pls.agent_url("/add_sessions/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_users == 1)
    assert (pls.user_list == ["christophe"])
    assert (pls.user_monitoring_sessions("christophe") != [])
    assert (pls.nb_user_sessions("christophe") == 1)
    assert (pls.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (pls.user_reach_max_session("christophe") is True)
    sessions = pls.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = pls.get_user_monitoring_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    assert(pls.get_user_monitoring_session("TOTO", 12324567) is None)