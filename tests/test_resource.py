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

import time
import pytest
from maat import Resource, DummyResource
import requests
import multiprocessing as mp
from maat import MaatAgent, create_agent_api
from tests import get_open_port


def test_assignement():
    toto = {
        "/ping": 42,
        "/test": "ok"
    }
    dr = DummyResource(
        toto, "DummyHost", 123456, protocol="ftp", timeout=1.0, ping_cmd="/ping",
        ping_interval=2.0, default_url="/default", name="Toto"
    )

    ## Basic test
    assert(dr.name == "Toto")
    assert(dr.host == "DummyHost")
    assert(dr.port == 123456)
    assert(dr.protocol == "ftp")
    assert(dr.timeout == 1.0)
    assert(dr.ping_cmd == "/ping")
    assert(dr.available is True)
    assert(dr.ping_interval == 2.0)
    assert(dr.url() == "%s://%s:%s/default" % (
        dr.protocol, dr.host, dr.port
    ))
    assert(dr.ping_url == "%s://%s:%s%s" % (
        dr.protocol, dr.host, dr.port, dr.ping_cmd
    ))
    assert(dr.cmd() is None)
    assert(dr.cmd("/ping") == 42)
    assert(dr.cmd("/test") == "ok")
    assert(dr.cmd("This do not exist") is None)
    assert(dr.ping(None) is True)

    titi = dr.to_dict()

    assert(titi["name"] == dr.name)
    assert(titi["hostname"] == dr.host)
    assert(titi["url"] == dr.url())
    assert(titi["ping_url"] == dr.ping_url)
    assert(titi["available"] == dr.available)

    ## Assignement test
    dr.name = "Titi"
    dr.host = "Tata"
    dr.port = 654321
    dr.protocol = "http"
    dr.timeout = 3.0
    dr.ping_cmd = "/azertyuiop"

    assert (dr.name == "Titi")
    assert (dr.host == "Tata")
    assert (dr.port == 654321)
    assert (dr.protocol == "http")
    assert (dr.timeout == 3.0)
    assert (dr.ping_cmd == "/azertyuiop")
    assert(dr.cmd("/azertyuiop") is None)
    assert (dr.url() == "%s://%s:%s/default" % (
        dr.protocol, dr.host, dr.port
    ))
    assert (dr.ping_url == "%s://%s:%s%s" % (
        dr.protocol, dr.host, dr.port, dr.ping_cmd
    ))
    assert (dr.ping_interval == 2.0)

    # Ping should failed
    assert(dr.ping(True) is False)

    print(dr)
    print(dr.__repr__())

    print(dr.make_request(None) is None)


def test_exception():

    with pytest.raises(Exception):
        DummyResource(
            None, "DummyHost", 123456, protocol="ftp", timeout=1.0, ping_cmd="/ping",
            ping_interval=2.0, default_url="/default", name="Toto"
        )


@pytest.yield_fixture(autouse=True)
def fake_agent():

    # Get a free port
    port = get_open_port()

    agent = MaatAgent("FakeService")

    # Create the fake backend
    def run_this():
        create_agent_api("127.0.0.1", port, agent)

    process = mp.Process(target=run_this, daemon=True)

    yield (process, port)

    if process.is_alive():
        process.terminate()

    agent.stop()
    del agent


def test_make_request(fake_agent):
    process, port = fake_agent

    process.start()

    agent = Resource("127.0.0.1", port, ping_cmd="/v1/ping", default_url="/v1/processes", name="FakeAgent")

    time.sleep(2)

    assert(agent.cmd("/v1/ping") == "OK")
    assert(agent.cmd("NotADefiniedOne") is None)

    process.terminate()