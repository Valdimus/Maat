import time
import json
import pytest
import logging
from maat import Resource, DummyResource, Backend, DirectAgentResource, MaatAgent, FakeProcessMonitoring

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
# Date: 23/03/2017


def test_assignement():
    service = DummyResource({
        "/ping": "ok",
        "/default": "ok"
    }, "host", 123456, ping_cmd="/ping", default_url="/default", name="FakeStudio")

    agent = DirectAgentResource(MaatAgent("FakeProcess", sleep_time=0.5, process_interval=0.5))

    backend = Backend("Test", service, agent, version="v1", interval=2.0, max_session_by_user=2)

    assert(backend.name == "Test")
    assert(backend.service == service)
    assert(backend.agent == agent)
    logging.debug("Data: %s" % backend.data)
    # assert(backend.data == data)
    assert(backend.version == "v1")
    assert(backend.max_session_by_user == 2)

    assert(backend.available() is True)
    assert (backend.nb_process() == 0)
    assert(backend.processes("Titi") == [])
    assert(len(backend.users()) == 0)

    assert(backend.nb_user() == 0)
    assert(backend.processes_timestamp() == 0)
    assert(backend.requests() == {})
    assert(backend.requests_timestamp() == 0)
    assert(backend.nb() == 0)
    assert(backend.timestamp() == 0)
    assert(backend.user_nb_processes("titi") == 0)



def test_value():
    service = DummyResource({
        "/ping": "ok",
        "/default": "ok"
    }, "host", 123456, ping_cmd="/ping", default_url="/default", name="FakeStudio")

    agent = DirectAgentResource(MaatAgent("FakeProcess", sleep_time=0.5, process_interval=0.5, process_monitoring=FakeProcessMonitoring))

    agent.agent.process_monitoring.add_session("christophe")

    time.sleep(2)

    agent.agent.requests.add("christophe")

    print("Processes %s" % agent.agent.data)
    backend = Backend("Test", service, agent, version="v1", interval=2.0, max_session_by_user=2)
    print("Backend %s" % backend.processes("christophe"))
    assert (backend.available() is True)
    assert (backend.processes("Titi") == [])
    print(backend.processes("christophe"))
    assert (len(backend.processes("christophe")) == 1)
    assert (len(backend.users()) == 1)
    assert (backend.nb_process() == 1)
    assert (backend.nb_user() == 1)
    assert (backend.processes_timestamp() > 0)
    assert (len(backend.requests()) == 1)
    assert(len(backend.requests()["christophe"]) == 1)
    assert (backend.requests_timestamp() > 0)
    assert (backend.nb() == 2)
    assert (backend.timestamp() > 0)
    assert (backend.user_nb_processes("titi") == 0)
    assert (backend.user_nb_processes("christophe") == 1)



