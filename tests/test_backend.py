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
# Description: Test backend class

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
    Create a fakebackend to test the Backend class
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

    # Test that default value are correctly set
    # port = None => No ':' should be seen in url() and ping_url
    # name = None => Must use the hostname as name
    # ping_path = None => Must use the path as ping path
    back = Backend(
        hostname="127.0.0.1", port=None, protocol="http", path="", name=None, timeout=0.5, ping_path=None,
        ping_interval=1
    )

    assert(back.hostname == "127.0.0.1")

    # When name is None, it use the hostname as name
    assert(back.name == back.hostname)
    assert(back.port is None)
    assert(back.protocol == "http")
    assert(back.path == "")
    assert(back.timeout == 0.5)

    # When ping path is None, it will use path instead
    assert(back.ping_path == back.path)
    assert(back.ping_interval == 1)

    # Backend must be unavailable
    assert(back.available is False)

    # If port is None, url don't content any ':'
    assert(back.url() == "http://127.0.0.1")
    assert(back.url("/") == "http://127.0.0.1/")
    assert(back.url("/toto") == "http://127.0.0.1/toto")

    # As ping_path is None ping_url must be the same as url()
    assert(back.url() == back.ping_url)

    # Check that the to_dict method return what we are expected
    assert(back.to_dict() == {
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available,
        "ping_last_update": back.get_ping().last_update
    })

    del back

    # Check each value are correctly set
    back = Backend(
        hostname="127.0.0.1", port=5000, protocol="http", path="/path", name="Test", timeout=0.5, ping_path="/ping",
        ping_interval=1
    )

    assert(back.hostname == "127.0.0.1")
    assert(back.port == 5000)
    assert(back.protocol == "http")
    assert(back.path == "/path")
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
        "available": back.available,
        "ping_last_update": back.get_ping().last_update
    })
    assert(str(back) == json.dumps({
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available,
        "ping_last_update": back.get_ping().last_update
    }))
    assert(back.__repr__() == json.dumps({
        "name": back.name,
        "hostname": back.hostname,
        "url": back.url(),
        "ping_url": back.ping_url,
        "available": back.available,
        "ping_last_update": back.get_ping().last_update
    }))


def test_ping(fakebackend):
    """Check if the ping method work as we excepted"""
    process, port = fakebackend

    back = Backend(
        hostname="127.0.0.1", port=port, protocol="http", path="/path", name="Test", timeout=0.1, ping_path="/ping",
        ping_interval=0.1
    )

    # Recheck that all are correctly set
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

    # Start the backend
    process.start()

    # Backend must pass available
    mtime = time.time()

    # Wait until the backend appears available
    while not back.available:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Backend not seems to be started!!!")

    # Backend must be available now
    assert (back.available is True)

    # Now check that if we stop the fakebackend, the backend seems dead
    process.terminate()

    # Wait until backend is unavailable
    while back.available:
        time.sleep(0.1)
        if time.time() - mtime >= 60:
            raise Exception("Backend not seems to be started!!!")

    # Backend must be down
    assert(back.available is False)
