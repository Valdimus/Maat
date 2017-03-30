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
# Description: Test PLSBackend

import time
import pytest
from maat import PLSBackend, PLSBackendHandler
import multiprocessing as mp
from tests import get_open_port
from tests import create_fake_pls_backend


@pytest.yield_fixture(autouse=True)
def fakebackend():
    """
    Create a fake PLSBackend
    """

    # Get a free port
    port = get_open_port()

    # Create the fake backend
    def run_this():
        create_fake_pls_backend(host="127.0.0.1", port=port, interval=30)

    process = mp.Process(target=run_this)

    yield (process, port)

    if process.is_alive():
        process.terminate()


def test_basic():
    """Test that basic assignment is functionnal"""
    pls = PLSBackend(agent_port=5005, hostname="127.0.0.1", port=5000, protocol="http")

    assert(pls.agent_port == 5005)
    assert(pls.agent_url() == "http://127.0.0.1:5005")
    assert(pls.agent_url("/test") == "http://127.0.0.1:5005/test")
    assert(pls.monitoring == pls._default_value_monitoring())
    assert(pls.sessions == pls._default_value_pls())
    assert(pls.nb_sessions == 0)
    assert(pls.to_dict() == {
        "name": pls.name,
        "hostname": pls.hostname,
        "url": pls.url(),
        "ping_url": pls.ping_url,
        "available": pls.available,
        "ping_last_update": pls.get_ping().last_update,
        "agent_url": pls.agent_url(""),
        "agent_available": pls.agent_available,
        "sessions": pls.sessions,
        "sessions_failed": pls.get_sessions().failed(),
        "sessions_last_update": pls.get_sessions().last_update,
        "nb_sessions": pls.nb_sessions,
        "monitoring": pls.monitoring,
        "monitoring_failed": pls.get_monitoring().failed(),
        "monitoring_last_update": pls.get_monitoring().last_update,
        "max_session_per_user": pls.max_session_per_user
    })
    assert(pls.max_session_per_user == 1)


def test_user_session(fakebackend):
    """Test that the PLSBackend see the PLS creating and removing a session for an user"""
    fk, port = fakebackend
    pls = PLSBackend(
        agent_port=port, hostname="127.0.0.1", port=port, protocol="http",
        monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
    )
    plsh = PLSBackendHandler(pls)

    assert(pls.available is False)
    assert(pls.monitoring == pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)

    # Start the fake backend
    fk.start()
    time.sleep(0.1)

    assert (pls.available is True)
    assert (pls.monitoring != pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)

    # Add a user
    r = pls.make_request(pls.agent_url("/add_sessions/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["christophe"])
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.nb_user_sessions("christophe") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("christophe") is True)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    assert(plsh.user_session("TOTO", 12324567) is None)

    # Remove the user
    r = pls.make_request(pls.agent_url("/rm_session/christophe"))
    r.raise_for_status()

    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)


def test_user_sessions(fakebackend):
    """Test that the PLSBackend see the PLS creating and removing multiple session for an user"""
    fk, port = fakebackend
    pls = PLSBackend(
        agent_port=port, hostname="127.0.0.1", port=port, protocol="http",
        monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1, max_session_per_user=2
    )
    plsh = PLSBackendHandler(pls)
    assert(pls.available is False)
    assert(pls.monitoring == pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("toto") is False)

    # Start the fake backend
    fk.start()
    time.sleep(0.1)

    assert (pls.available is True)
    assert (pls.monitoring != pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("toto") is False)

    # Add a session
    r = pls.make_request(pls.agent_url("/add_sessions/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["christophe"])
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.nb_user_sessions("christophe") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("christophe") is False)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    assert(plsh.user_session("TOTO", 12324567) is None)

    # Add a session
    r = pls.make_request(pls.agent_url("/add_sessions/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["christophe"])
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.nb_user_sessions("christophe") == 2)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("christophe") is True)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 2)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    a = plsh.user_session("christophe", sessions[1].pid)
    assert (a == sessions[1].session)
    assert (plsh.user_session("TOTO", 12324567) is None)

    # Remove a session
    r = pls.make_request(pls.agent_url("/rm_session/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["christophe"])
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.nb_user_sessions("christophe") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("christophe") is False)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    assert (plsh.user_session("TOTO", 12324567) is None)

    # Remove a session
    r = pls.make_request(pls.agent_url("/rm_session/christophe"))
    r.raise_for_status()

    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (plsh.max_session_per_user == 2)
    assert (plsh.user_reach_max_session("toto") is False)


def test_multiple_users(fakebackend):
    """Test that the PLSBackend see the PLS creating and removing a session for multiple users"""
    fk, port = fakebackend
    pls = PLSBackend(
        agent_port=port, hostname="127.0.0.1", port=port, protocol="http",
        monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
    )
    plsh = PLSBackendHandler(pls)
    assert(pls.available is False)
    assert(pls.monitoring == pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)

    # Start the fake backend
    fk.start()
    time.sleep(0.1)

    assert (pls.available is True)
    assert (pls.monitoring != pls._default_value_monitoring())
    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)

    # Add a session
    r = pls.make_request(pls.agent_url("/add_sessions/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["christophe"])
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.nb_user_sessions("christophe") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("christophe") is True)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    assert(plsh.user_session("TOTO", 12324567) is None)

    # Add a session
    r = pls.make_request(pls.agent_url("/add_sessions/alexandre"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 2)
    assert (set(plsh.user_list()) == set(["christophe", "alexandre"]))
    assert (plsh.user_sessions("christophe") != [])
    assert (plsh.user_sessions("alexandre") != [])
    assert (plsh.nb_user_sessions("christophe") == 1)
    assert (plsh.nb_user_sessions("alexandre") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("christophe") is True)
    assert (plsh.user_reach_max_session("alexandre") is True)
    sessions = plsh.user_sessions("christophe")
    assert (len(sessions) == 1)
    a = plsh.user_session("christophe", sessions[0].pid)
    assert (a == sessions[0].session)
    sessions = plsh.user_sessions("alexandre")
    assert (len(sessions) == 1)
    a = plsh.user_session("alexandre", sessions[0].pid)
    assert (a == sessions[0].session)
    assert (plsh.user_session("TOTO", 12324567) is None)

    # Remove a session
    r = pls.make_request(pls.agent_url("/rm_session/christophe"))
    r.raise_for_status()

    assert (pls.sessions != pls._default_value_pls())
    assert (pls.nb_sessions == 1)
    assert (plsh.user_list() == ["alexandre"])
    assert (plsh.user_sessions("alexandre") != [])
    assert (plsh.nb_user_sessions("alexandre") == 1)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (plsh.user_sessions("christophe") == [])
    assert (plsh.nb_user_sessions("christophe") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("alexandre") is True)
    sessions = plsh.user_sessions("alexandre")
    assert (len(sessions) == 1)
    a = plsh.user_session("alexandre", sessions[0].pid)
    assert (a == sessions[0].session)
    assert (plsh.user_session("TOTO", 12324567) is None)

    # Remove a session
    r = pls.make_request(pls.agent_url("/rm_session/alexandre"))
    r.raise_for_status()

    assert (pls.sessions == pls._default_value_pls())
    assert (pls.nb_sessions == 0)
    assert (plsh.user_list() == [])
    assert (plsh.user_sessions("alexandre") == [])
    assert (plsh.nb_user_sessions("alexandre") == 0)
    assert (plsh.nb_user_sessions("toto") == 0)
    assert (pls.max_session_per_user == 1)
    assert (plsh.user_reach_max_session("toto") is False)
