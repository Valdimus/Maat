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

import json
import time
from flask import Flask
import pytest
from maat import Backend
import multiprocessing as mp
from tests import get_open_port


@pytest.yield_fixture(autouse=True)
def fakebackend():
    """
    Directory fixture
    Will create directory and temp file for testing storage services
    :return:
    """

    app = Flask("FakeBackend")

    @app.route("/path")
    def path():
        return "OK"

    @app.route("/ping")
    def ping():
        return "PING"

    port = get_open_port()

    def run_this():
        app.run(host="127.0.0.1", port=port)

    process = mp.Process(target=run_this)

    yield (process, port)

    if process.is_alive():
        process.terminate()


def test_bacic():
    """Test property and default value"""
    back = Backend(
        hostname="127.0.0.1", port=None, protocol="http", path="", name=None, timeout=0.5, ping_path=None,
        ping_interval=1
    )

    assert(back.hostname == "127.0.0.1")
    assert(back.port is None)
    assert(back.protocol == "http")
    assert(back.path == "")
    assert(back.name == "127.0.0.1")
    assert(back.timeout == 0.5)
    assert(back.ping_path == back.path)
    assert(back.ping_interval == 1)
    assert(back.available is False)
    assert(back.url() == "http://127.0.0.1")
    assert(back.url("/") == "http://127.0.0.1/")
    assert(back.url("/toto") == "http://127.0.0.1/toto")
    assert(back.ping_url == "http://127.0.0.1")

    assert(back.to_dict() == {
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available
    })

    del back

    back = Backend(
        hostname="127.0.0.1", port=5000, protocol="http", path="/path", name="Test", timeout=0.5, ping_path="/ping",
        ping_interval=1
    )

    assert(back.hostname == "127.0.0.1")
    assert(back.port == 5000)
    assert(back.protocol == "http")
    assert (back.path == "/path")
    assert(back.name == "Test")
    assert(back.timeout == 0.5)
    assert(back.ping_path == "/ping")
    assert(back.ping_interval == 1)
    assert(back.available is False)
    assert(back.url() == "http://127.0.0.1:5000/path")
    assert(back.url("/") == "http://127.0.0.1:5000/")
    assert(back.url("/toto") == "http://127.0.0.1:5000/toto")
    assert(back.ping_url == "http://127.0.0.1:5000/ping")

    assert (back.to_dict() == {
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available
    })
    assert(str(back) == json.dumps({
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available
    }))
    assert (back.__repr__() == json.dumps({
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available
    }))


def test_ping(fakebackend):
    """Check if the ping method work as we except"""
    process, port = fakebackend

    back = Backend(
        hostname="127.0.0.1", port=port, protocol="http", path="/path", name="Test", timeout=0.1, ping_path="/ping",
        ping_interval=0.1
    )

    assert (back.hostname == "127.0.0.1")
    assert (back.port == port)
    assert (back.protocol == "http")
    assert (back.path == "/path")
    assert (back.name == "Test")
    assert (back.timeout == 0.1)
    assert (back.ping_path == "/ping")
    assert (back.ping_interval == 0.1)
    assert (back.url() == "http://127.0.0.1:%s/path" % port)
    assert (back.ping_url == "http://127.0.0.1:%s/ping" % port)

    # Backend must be unavailable
    assert (back.available is False)

    # Start the backend
    process.start()

    # Backend must pass available
    mtime = time.time()

    while not back.available:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Backend not seems to be started!!!")

    # Backend must be available now
    assert (back.available is True)

    # Now check that if we stop the fakebackend, the backend seems dead
    process.terminate()

    while back.available:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Backend not seems to be started!!!")

    assert(back.available is False)