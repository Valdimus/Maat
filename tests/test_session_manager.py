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
# Description: Test SessionManager

import time
import pytest
from maat import PLSBackend
from maat import SessionManager
import multiprocessing as mp
from tests import get_open_port
from tests import create_fake_pls_backend


def add_user(backend, username):
    """
    Add user for a backend
    :param backend: Backend
    :param username: Username
    :return:
    """
    r = backend.make_request(backend.agent_url("/add_sessions/%s" % username))
    r.raise_for_status()


@pytest.yield_fixture(autouse=True)
def fakebackends():
    """
    Create 5 backends to play with
    """

    def createPLSBackend(name):
        """Create a PLSBackend"""
        port = get_open_port()

        def run_this():
            """Create the fake backend"""
            create_fake_pls_backend(host="127.0.0.1", port=port, interval=30)

        # Create the process
        process = mp.Process(target=run_this)

        # Start it
        process.start()

        # Create the backend
        pls = PLSBackend(
            name=name,
            agent_port=port, hostname="127.0.0.1", port=port, protocol="http",
            monitoring_interval=0, sessions_interval=0, ping_interval=0, timeout=0.1
        )

        return {
            "process": process,
            "backend": pls
        }

    backends = []
    ref = []
    for i in range(0, 5):
        name = "FakePLSBackend_%s" % i
        a = createPLSBackend(name)
        backends.append(a["backend"])
        ref.append(a)
    time.sleep(0.1)
    yield (backends, ref)

    for v in ref:
        if v["process"].is_alive():
            v["process"].terminate()


def test_basic():
    """Basic test"""
    sm = SessionManager([])

    assert(sm.backends == [])
    assert (sm.nb_available == 0)
    assert(sm.nb_users == 0)
    assert(sm.connected_users == [])
    assert(sm.get_user_sessions("toto") == [])


def test_bacic_2(fakebackends):
    """Check basic function with 5 backends"""
    backends, ref = fakebackends

    sm = SessionManager(backends)

    assert (sm.backends == backends)
    assert (sm.nb_available == 5)
    assert (sm.nb_users == 0)
    assert (sm.connected_users == [])
    assert (sm.get_user_sessions("toto") == [])

    # Add a user to first backend
    add_user(ref[0]["backend"], "christophe")

    assert (sm.nb_users == 1)
    assert (sm.connected_users == ["christophe"])
    assert (sm.get_user_sessions("toto") == [])
    sess = sm.get_user_sessions("christophe")
    assert(len(sess) == 1)
    assert(sess[0].backend == ref[0]["backend"])

    # Add no user to the second backend
    add_user(ref[1]["backend"], "toto")

    assert (sm.nb_users == 2)
    assert (set(sm.connected_users) == set(["christophe", "toto"]))
    assert (sm.get_user_sessions("titi") == [])
    sess = sm.get_user_sessions("christophe")
    assert (len(sess) == 1)
    assert (sess[0].backend == ref[0]["backend"])
    sess = sm.get_user_sessions("toto")
    assert (len(sess) == 1)
    assert (sess[0].backend == ref[1]["backend"])

    # We kill the first backend
    ref[0]["process"].terminate()

    assert (sm.nb_available == 4)
    assert (sm.nb_users == 1)
    assert (sm.connected_users == ["toto"])
    assert (sm.get_user_sessions("titi") == [])
    assert (sm.get_user_sessions("christophe") == [])
    sess = sm.get_user_sessions("toto")
    assert (len(sess) == 1)
    assert (sess[0].backend == ref[1]["backend"])


def test_choose_backend(fakebackends):
    """Test choose backend"""

    backends, ref = fakebackends

    # Stop backend 4
    ref[3]["process"].terminate()
    sm = SessionManager(backends)

    assert (sm.nb_available == 4)
    assert (sm.nb_users == 0)

    # Should return the first backend
    choose = sm.quick_choose("christophe")
    assert(choose == ref[0]["backend"])
    add_user(choose, "christophe")

    assert (sm.nb_users == 1)

    # Should return the same backend
    choose = sm.quick_choose("christophe")
    assert(choose == ref[0]["backend"])
    assert (sm.nb_users == 1)

    # New user ask a backend, should return backend 2
    choose = sm.quick_choose("toto")
    assert (choose == ref[1]["backend"])
    add_user(choose, "toto")

    assert (sm.nb_users == 2)


def test_session(fakebackends):
    backends, ref = fakebackends
    sm = SessionManager(backends)
    assert (sm.nb_available == 5)
    assert (sm.nb_users == 0)

    # Should return the first backend
    choosen = sm.quick_choose("christophe")
    assert (choosen == ref[0]["backend"])

    # Add a new user
    add_user(choosen, "christophe")

    # Get the session of this user
    sessions = sm.get_user_sessions("christophe")

    assert(len(sessions) == 1)

    session = sessions[0]
    # Som verification on session
    assert(session.backend == ref[0]["backend"])
    assert(session.exist is True)
    assert(session.username == "christophe")
    # The fakeplsbackend launch first session with pid 42
    assert(session.pid == 42)
    assert(isinstance(session.session, dict) is True)


def test_add_session(fakebackends):
    backends, ref = fakebackends

    # Stop backend 3, 4, 5
    for i in [2, 3, 4]:
        ref[i]["process"].terminate()

    sm = SessionManager(backends)

    assert (sm.nb_available == 2)
    assert (sm.nb_users == 0)

    # Add a new session
    choosen = sm.add_session("christophe")

    # Should be the first backend
    assert (choosen == ref[0]["backend"])

    # Add a new user to this backend
    add_user(choosen, "christophe")
    assert("christophe" in sm.connected_users)

    # Should raise an exception, user 'christophe' have reach the maximum session (1 by default)
    with pytest.raises(Exception):
        sm.add_session("christophe")

    # Add a second client
    choosen = sm.add_session("toto")

    # Should be the second backend
    assert (choosen == ref[1]["backend"])

    # Add a new user to this backend
    add_user(choosen, "toto")
    assert ("toto" in sm.connected_users)

    # Should raise an exception, user 'christophe' have reach the maximum session (1 by default)
    with pytest.raises(Exception):
        sm.add_session("toto")

    # Verify that we alternate the backend to use
    for i in range(2, 6):
        username = "Test_%s" % i

        # Add client
        choosen = sm.add_session(username)

        # Should be the second backend
        assert (choosen == ref[i % 2]["backend"])

        # Add a new user to this backend
        add_user(choosen, username)

        assert (username in sm.connected_users)

        # Should raise an exception, user 'christophe' have reach the maximum session (1 by default)
        with pytest.raises(Exception):
            sm.add_session(username)

    # Kill all backends
    for i in [0, 1]:
        ref[i]["process"].terminate()

    # No backend available must raise an exception
    with pytest.raises(Exception):
        sm.add_session("toto")

    with pytest.raises(Exception):
        sm.add_session("Christophe")


def test_add_session_max_session_by_user(fakebackends):
    """Create a session manager with max_session_per_user set to 2"""
    backends, ref = fakebackends

    # Stop backend 3, 4, 5
    for i in [2, 3, 4]:
        ref[i]["process"].terminate()

    sm = SessionManager(backends, max_session_per_user=2)

    # Add a new session
    choosen = sm.add_session("christophe")

    # Should be the first backend
    assert (choosen == ref[0]["backend"])

    # Add a new user to this backend
    add_user(choosen, "christophe")
    assert ("christophe" in sm.connected_users)
    assert (len(sm.get_user_sessions("christophe")) == 1)

    choosen = sm.add_session("christophe")

    # Should be the second backend
    assert (choosen == ref[1]["backend"])

    # Add a new user to this backend
    add_user(choosen, "christophe")
    assert ("christophe" in sm.connected_users)
    assert (len(sm.get_user_sessions("christophe")) == 2)

    # max_session_per_user reach, must raise an exception
    with pytest.raises(Exception):
        sm.add_session("christophe")

    # Check each sessions have different backends
    sessions = sm.get_user_sessions("christophe")

    assert(sessions[0].backend != sessions[1].backend)
    assert(sessions[0].username == sessions[1].username)
