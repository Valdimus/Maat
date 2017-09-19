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
import json
import pytest
import psutil
import requests
import multiprocessing as mp
from maat import MaatAgent, create_agent_api
from tests import FakeStudio, get_open_port


import signal
import pytest_cov.embed


def cleanup(*_):
    pytest_cov.embed.cleanup()
    sys.exit(1)

signal.signal(signal.SIGTERM, cleanup)


@pytest.yield_fixture(autouse=True)
def fake_studio():

    fake_service = FakeStudio(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fake_service.py"))

    yield fake_service

    del fake_service
    gc.collect()


@pytest.yield_fixture(autouse=True)
def fake_agent():

    # Get a free port
    port = get_open_port()

    agent = MaatAgent("FakeService")

    # Create the fake backend
    def run_this():
        create_agent_api("127.0.0.1", port, agent)

    process = mp.Process(target=run_this, daemon=True)

    yield (process, port, agent)

    if process.is_alive():
        process.terminate()

    agent.stop()
    del agent


def test_assignment():
    """Test value assignement"""

    ma = MaatAgent("FakeService")

    assert(ma.sleep_time == 5)
    assert(ma.max_process_by_user == 1)
    assert(ma.request_time == 30)

    ma.stop()

    ma = MaatAgent("FakeService", sleep_time=1, max_process_by_user=2, request_time=1)

    assert(ma.sleep_time == 1)
    assert(ma.max_process_by_user == 2)
    assert(ma.request_time == 1)

    ma.stop()


def test_agent():
    """Test that the agent don't detect some fake thing"""
    ma = MaatAgent("FakeService", sleep_time=0.2, max_process_by_user=2, request_time=0.5)

    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    assert(len(data["requests"]) == 0)
    assert (data["nb_requests"] == 0)
    assert(data["nb"] == 0)

    time.sleep(1)

    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    assert(len(data["requests"]) == 0)
    assert (data["nb_requests"] == 0)
    assert(data["nb"] == 0)

    ma.stop()


def test_add_process_request():
    """
    Test the add_process_request:
        - add a request
        - don't add a request if the user have reach the maximum of sessions
        - Check that we can force the add of a request
        - Check that if the client give wrong know_value, we reject is request
    """
    username = pwd.getpwuid(os.getuid()).pw_name
    ma = MaatAgent("FakeService", sleep_time=0.2, max_process_by_user=2, request_time=0.5)

    time.sleep(1)

    assert(ma.add_process_request(username, 0) is True)
    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    assert(len(data["requests"]) == 1)
    assert(data["nb_requests"] == 1)
    assert(data["nb"] == 1)

    time.sleep(1)

    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    assert(len(data["requests"]) == 0)
    assert (data["nb_requests"] == 0)
    assert(data["nb"] == 0)

    time.sleep(1)

    assert(ma.add_process_request(username, 0) is True)
    assert(ma.add_process_request(username, 1) is True)
    assert(ma.add_process_request(username, 2) is False)
    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    # Only one user
    assert(len(data["requests"]) == 1)
    assert (data["nb_requests"] == 2)
    assert(data["nb"] == 2)

    time.sleep(1)

    assert(ma.add_process_request(username, 0) is True)
    assert(ma.add_process_request(username, 100) is False)
    assert(ma.add_process_request(username, 1) is True)
    assert(ma.add_process_request(username, 2, force=True) is True)
    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    # Only one user
    assert(len(data["requests"]) == 1)
    assert (data["nb_requests"] == 3)
    assert(data["nb"] == 3)

    ma.stop()


def test_update_request(fake_studio):
    """
    Check that the agent detect a new session and remove a request if the user have ask one
    :param fake_studio: The Fake Studio
    :return:
    """
    username = pwd.getpwuid(os.getuid()).pw_name
    ma = MaatAgent("FakeService", sleep_time=0.2, max_process_by_user=3, request_time=2, process_interval=0.2)

    time.sleep(1)

    # Request0
    assert(ma.add_process_request(username, 0) is True)
    data = json.loads(ma.data)
    assert(data["nb_process"] == 0)
    assert(len(data["requests"]) == 1)
    assert (data["nb_requests"] == 1)
    assert(data["nb"] == 1)

    print(data["requests"])

    time.sleep(1)
    assert (len(data["requests"]) == 1)
    assert (data["nb"] == 1)
    # Simulate the connection of an user on the service
    fake_studio.spawn_client(username)

    # Request1
    assert(ma.add_process_request(username, 0) is True)

    # Sleep, to let the agent detecting the changement
    time.sleep(2)

    # So now a request must be deleted and the user must have a session
    data = json.loads(ma.data)
    assert(data["nb_process"] == 1)
    assert(len(data["processes"][username]) == 1)
    assert(len(data["requests"]) == 1)
    assert (data["nb_requests"] == 1)
    assert(username in data["requests"])
    assert(data["nb"] == 2)

    time.sleep(2)

    # The Request1 must have expire
    data = json.loads(ma.data)
    assert(data["nb_process"] == 1)
    assert(len(data["processes"][username]) == 1)
    assert(len(data["requests"]) == 0)
    assert (data["nb_requests"] == 0)
    assert(data["nb"] == 1)

    fake_studio.stop_all()

    ma.stop()


def test_webservice(fake_agent):
    process, port, agent = fake_agent

    username = pwd.getpwuid(os.getuid()).pw_name
    process.start()

    time.sleep(0.5)

    def api(url, use_version=True):
        return "http://127.0.0.1:%s%s" % (port, url if not use_version else "/%s%s" % (agent.version, url))

    r = requests.get(api("/ping"))
    assert(r.status_code == 200)

    r = requests.get(api("/ping", use_version=False))
    assert (r.status_code == 200)

    print(api("/new_requests/%s/0" % username))
    r = requests.get(api("/new_requests/%s/0" % username))
    assert(r.status_code == 200)
    assert(r.json() is True)

    r = requests.get(api("/data"))
    assert(r.status_code == 200)
    data = r.json()
    assert(data["nb_process"] == 0)
    assert(data["nb_requests"] == 1)
    assert(data["nb"] == 1)
    assert(len(data["requests"]) == 1)

    r = requests.get(api("/info", use_version=False))

    assert(r.json() == {
        "process_name": "FakeService",
        "version": "v1"
    })
