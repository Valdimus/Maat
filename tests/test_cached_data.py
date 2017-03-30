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

import time
import pytest
from maat import CachedData


def test_update():
    """Test that the data is update after the interval"""
    def update(previous_data):
        return previous_data + 1

    # When we create a cached data,
    cd = CachedData(default_data=-1, interval=0.2, update_fct=update)

    # First call to cd.data must call the udpate function
    assert(cd.data == 0)
    assert(cd.interval == 0.2)
    time.sleep(0.5)
    assert(cd.data == 1)


def test_setter():
    """Test if we can set a new interval"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0.1, update_fct=update)
    assert(cd.interval == 0.1)
    cd.interval = 0.2
    assert(cd.interval == 0.2)
    assert(cd.data == 0)
    time.sleep(0.05)
    # Data must not change
    assert(cd.data == 0)
    time.sleep(0.2)
    # Data must have change
    assert(cd.data == 1)


def test_last_update():
    """Test that the last_update is update each time the  data is update"""

    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0.5, update_fct=update)

    assert (cd.data == 0)
    lu = cd.last_update

    mtime = time.time()

    # Check that last_update is update
    while cd.last_update == lu:
        time.sleep(0.001)
        d = cd.data
        if cd.last_update == lu:
            assert (d == 0)
        else:
            break
        if time.time() - mtime >= 60:
            raise Exception("last_update was not update!")

    # Data must have change
    assert (cd.data == 1)


def test_interval():
    """Test tha we can't see wrong value as interval. Interval must be a number"""

    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0.5, update_fct=update)

    with pytest.raises(Exception):
        cd.interval = -1
    with pytest.raises(Exception):
        cd.interval = -1.0
    with pytest.raises(Exception):
        cd.interval = "Toto"
    with pytest.raises(Exception):
        cd.interval = None

    with pytest.raises(Exception):
        CachedData(default_data=-1, interval=-1, update_fct=update)
    with pytest.raises(Exception):
        CachedData(default_data=-1, interval=-1.0, update_fct=update)
    with pytest.raises(Exception):
        CachedData(default_data=-1, interval="Toto", update_fct=update)
    with pytest.raises(Exception):
        CachedData(default_data=-1, interval=None, update_fct=update)


def test_update_raise():
    """Test if the update function raise an exception, we will still return a data (the previous one)"""
    def update(previous_data):
        raise Exception("Just an example")

    cd = CachedData(update_fct=update)

    assert(cd.default_on_failure is True)
    assert(cd.default_data is None)
    assert(cd.data is None)
    assert(cd.data is None)

    cd = CachedData(default_data=0, update_fct=update, default_on_failure=False)

    assert (cd.default_on_failure is False)
    assert (cd.default_data == 0)
    assert (cd.data == 0)
    assert (cd.data == 0)

    def titi(pv):
        if pv == 1:
            return -1
        raise Exception("Toto")

    titi.toto = False

    cd = CachedData(default_data=1, update_fct=titi)

    assert (cd.default_on_failure is True)
    assert (cd.default_data == 1)
    assert (cd.data == -1)
    assert (cd.data == 1)


def test_no_update_fct():
    """Test that when no update function is set, it does nothing"""
    cd = CachedData(default_data=-1, interval=0)
    assert(cd.data == -1)
    assert(cd.data == -1)


def test_no_interval():
    """Test that when interval is 0 update as each data call"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0, update_fct=update)

    for i in range(0,9):
        assert(cd.data == i)


def test_force_data():
    """Test that when we use the force_data, data is update immediately"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0.2, update_fct=update)

    for i in range(0, 10):
        assert(cd.force_data == i)
