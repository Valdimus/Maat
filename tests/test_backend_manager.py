import time
import json
import pytest
import logging
from maat import Backend, DummyResource, BackendManager, DirectAgentResource, MaatAgent, FakeProcessMonitoring

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

    backendmanager = BackendManager()

    print()
    assert(backendmanager.backends == {})

    assert(backendmanager.get("Toto") is None)

    with pytest.raises(Exception):
        backendmanager.add(None)

    service = DummyResource({
        "/ping": "ok",
        "/default": "ok"
    }, "host", 123456, ping_cmd="/ping", default_url="/default", name="FakeStudio")

    # data = {
    #     "processes": {
    #         "christophe": [{
    #         "username": "christophe",
    #         "cpu_percent": 10.0,
    #         "memory_percent": 50.0,
    #         "memory_info": {},
    #         "pid": 112,
    #         "ppid": 111,
    #         "create_time": 2313249687,
    #         "cwd": "/home/christophe",
    #         "num_threads": 2,
    #         "cmdline": [],
    #         "exe": "R",
    #         "name": "R"
    #     }]},
    #     "nb_process": 1,
    #     "nb_request": 1,
    #     "processes_timestamp": 100,
    #     "requests": {
    #         "christophe": [
    #             123456789
    #         ]
    #     },
    #     "requests_timestamp": 200,
    #     "nb": 2,
    #     "timestamp": 300
    # }

    agent = DirectAgentResource(
        MaatAgent("FakeProcess", sleep_time=0.5, process_interval=0.5, process_monitoring=FakeProcessMonitoring))

    agent.agent.process_monitoring.add_session("christophe")

    time.sleep(2)

    agent.agent.requests.add("christophe")

    # agent1 = DummyResource({
    #     "/v1/data123132": None,
    #     "/v1/ping1231321": "OK"
    # }, "agentHost", 123456, ping_cmd="/v1/ping", default_url="/v1/ping", name="FakeAgent")

    backend = Backend("Test", service, agent, version="v1", interval=2.0, max_session_by_user=2)

    agent1 = DirectAgentResource(MaatAgent("FakeProcess", sleep_time=0.5, process_interval=0.5))
    agent1.set_available(False)
    backend1 = Backend("Toto", service, agent1, version="v1", interval=2.0, max_session_by_user=2)

    # Add a backend
    backendmanager.add(backend)
    assert(backendmanager.backends == {
        "Test": backend
    })

    # Add a second one
    backendmanager.add(backend1)
    assert(backendmanager.backends == {
        "Test": backend,
        "Toto": backend1
    })

    # Try to get the backend
    assert (backendmanager.get("Toto") == backend1)
    with pytest.raises(Exception):
        backendmanager.add("None")

    # Get a list of all backends
    assert(len(backendmanager.to_list(all_backends=True)) == 2)

    # Get only available backends
    assert(backendmanager.to_list() == [backend])

    # Get a session for an user
    assert(backendmanager.sessions_for_users(None) == [])
    assert(len(backendmanager.sessions_for_users("christophe")) == 1)

    # Get The session for an user for all backends
    assert (backendmanager.user_sessions_by_backend("christophe") == {
        "Test": [{
            "username": "christophe",
            "cpu_percent": 10.0,
            "memory_percent": 50.0,
            "memory_info": {},
            "pid": 112,
            "ppid": 111,
            "create_time": 2313249687,
            "cwd": "/home/christophe",
            "num_threads": 2,
            "cmdline": [],
            "exe": "R",
            "name": "R"
        }]
    })
    assert(backendmanager.user_sessions_by_backend("Toto") == {
        "Test": []
    })

    # Get the number session for an user for all backends
    assert (backendmanager.nb_user_sessions_by_backend("christophe") == {
        "Test": 1
    })
    assert (backendmanager.nb_user_sessions_by_backend("Toto") == {
        "Test": 0
    })

    # Get all number
    assert(backendmanager.all_nb_user_sessions_by_backend("christophe") == 1)
    assert(backendmanager.all_nb_user_sessions_by_backend("Toto") == 0)

    assert(backendmanager.nb_process_by_backend() == {
        "Test": 1
    })

    # Remove it with the instance
    backendmanager.rm(backend)
    assert (backendmanager.backends == {
        "Toto": backend1
    })

    # Remove it with his name
    backendmanager.rm("Toto")

    assert (backendmanager.backends == {})
