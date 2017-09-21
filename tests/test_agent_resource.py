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

from gevent import monkey
monkey.patch_all(thread=False)

import os
import gc
import pwd
import time
import json
import pytest
import psutil
import requests
import multiprocessing as mp
from tests import check_consistency
from maat import MaatAgent, create_agent_api
from maat import AgentResource, HTTPAgentResource, DirectAgentResource
from maat.agent import DEFAULT
from tests import FakeStudio, get_open_port


import signal
import pytest_cov.embed


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


def test_agent_resouce():

    agent_resource = AgentResource()

    assert(agent_resource.get() == DEFAULT)
    check_consistency(agent_resource.get(), DEFAULT)

    with pytest.raises(Exception):
        agent_resource.add_request("Toto", 254, False)

    assert(agent_resource.available() is True)


def test_HTTPAgentResource(fake_agent):
    process, port, agent = fake_agent

    username = pwd.getpwuid(os.getuid()).pw_name
    process.start()

    time.sleep(2)

    agent_resource = HTTPAgentResource("127.0.0.1", port)

    agent_resource.add_request(username, 0, 1)

    time.sleep(5)

    print("Agent data: %s" % agent_resource.get())
    assert (agent_resource.get()["nb_process"] == 0)
    assert (agent_resource.get()["nb_requests"] == 1)
    assert (agent_resource.get()["nb"] == 1)
    assert (len(agent_resource.get()["requests"]) == 1)
    check_consistency(agent_resource.get(), DEFAULT)

    assert(agent_resource.available() is True)


def test_direct_agent_resource():
    username = pwd.getpwuid(os.getuid()).pw_name
    agent = MaatAgent("FakeService")

    agent_resource = DirectAgentResource(agent)

    agent_resource.add_request(username, 0, 1)

    time.sleep(2)

    print("Agent data: %s" % agent_resource.get())
    assert (agent_resource.get()["nb_process"] == 0)
    assert (agent_resource.get()["nb_requests"] == 1)
    assert (agent_resource.get()["nb"] == 1)
    assert (len(agent_resource.get()["requests"]) == 1)
    check_consistency(agent_resource.get(), DEFAULT)

    assert (agent_resource.available() is True)

    agent_resource.set_available(False)
    assert (agent_resource.available() is False)

    agent_resource.set_available(True)
    assert (agent_resource.available() is True)

    agent.stop()
    del agent