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
from flask import Flask
import multiprocessing as mp
from maat import LoadBalancer, Backend, BackendManager, MaatAgent, SuperDummyResource
from maat import FakeProcessMonitoring, create_agent_api, Resource, DirectAgentResource, MaatAgent
from tests import get_open_port


def create_fake_agent(port, agent):
    """
    Create a fake agent
    A fake agent is just an agent with a FakeProcessMonitoring instead of a real ProcessMonitoring. Like so, we
    can easily test the agent.
    """
    app = Flask("Fake agent")

    @app.route("/fadd/<string:username>")
    def fake_add(username):
        """Add a fake session for an user"""
        agent.process_monitoring.add_session(username)
        return "OK"

    @app.route("/frm/<string:username>")
    def kafe_rm(username):
        """Rm a fake session for an user"""
        agent.process_monitoring.rm_sessions(username)
        return "OK"

        # Create the fake agent
    create_agent_api("127.0.0.1", port, agent, application=app)



@pytest.yield_fixture(autouse=True)
def test_bench():
    """
    A little test bench
    :return:
    """
    # Create the fake agent
    # agent0 = MaatAgent("agent0", sleep_time=1, process_interval=1, processMonitoring=FakeProcessMonitoring)
    # agent1 = MaatAgent("agent1", sleep_time=1, process_interval=1, processMonitoring=FakeProcessMonitoring)
    agent0 = DirectAgentResource(
        MaatAgent("Ressource-Agent0", sleep_time=0.5, process_interval=0.5, process_monitoring=FakeProcessMonitoring
    ))
    agent1 = DirectAgentResource(
        MaatAgent("Ressource-Agent1", sleep_time=0.5, process_interval=0.5, process_monitoring=FakeProcessMonitoring
    ))

    # Get an open port for the first agent

    # Create the corresponding backend
    backend0 = Backend(
        "Agent0", SuperDummyResource({
            "/ping": "ok",
            "/default": "ok"
        }, "host", 123456, ping_cmd="/ping", default_url="/default", name="FakeStudio"),
        agent0,
        interval=0.5
    )

    backend1 = Backend(
        "Agent1", SuperDummyResource({
            "/ping": "ok",
            "/default": "ok"
        }, "host", 123456, ping_cmd="/ping", default_url="/default", name="FakeStudio"),
        agent1,
        interval=0.5
    )

    time.sleep(2)

    backend0.service.ping(False)
    backend1.service.ping(False)

    time.sleep(1)
    # Create the backend manager
    backend_manager = BackendManager(backends=[backend0, backend1])


    yield (backend_manager, backend0, backend1)


def test_load_balancer(test_bench):
    """Test the load balancer"""
    backend_manager, backend0, backend1 = test_bench

    lb = LoadBalancer(backend_manager=backend_manager, max_sessions_by_user=1, max_attempt_nb=3)

    print(backend0.data)
    print(backend1.data)
    assert(lb.backend_manager == backend_manager)
    assert(lb.max_sessions_by_user == 1)
    assert(lb.max_attempt_nb == 3)

    # Check if it can choose a backend
    choosen = lb.balance("Christophe")

    time.sleep(1)
    liste = [backend0, backend1]
    print("CHOOSE %s" % choosen.name)
    assert(choosen in liste)

    choosen2 = lb.balance("Christophe")
    liste.remove(choosen)
    print("CHOOSEn2 %s" % choosen2.name)
    assert(choosen2 in liste)

    assert(lb.balance("Christophe"))