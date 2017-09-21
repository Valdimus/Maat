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


def test_assignment():
    """Test value assignement"""

    # Just check defaut value
    cd = CachedData()

    assert(cd.update_fct == cd.update_data)
    assert(cd.failed is False)
    assert(cd.last_update == 0)
    assert(cd.default_data is None)
    assert(cd.default_on_failure is False)
    assert(cd.interval == 1.0)
    assert(cd.no_previous_data is False)
    assert(cd.auto_update is True)
    assert(cd.name == "CachedData")

    assert(cd.data == cd.default_data)
    assert(cd.last_update == 0)
    assert(cd.failed is True)

    # Check Assignement
    cd = CachedData(
        default_data=False, default_on_failure=True, interval=2.0, no_previous_data=True, auto_update=False, name="Toto"
    )

    assert (cd.update_fct == cd.update_data)
    assert (cd.failed is False)
    assert (cd.last_update == 0)
    assert (cd.default_data is False)
    assert (cd.default_on_failure is True)
    assert (cd.interval == 2.0)
    assert (cd.no_previous_data is True)
    assert (cd.auto_update is False)
    assert (cd.name == "Toto")

    assert(cd.data == cd.default_data)
    assert(cd.last_update == 0)
    assert(cd.failed is False)

    # Do the update
    cd.do_update()

    assert(cd.data == cd.default_data)
    assert(cd.last_update == 0)
    assert (cd.failed is True)

    def update_fct(previous_data):
        update_fct.limit +=1
        if previous_data is None:
            raise Exception("Error0")
        rt = not previous_data
        if update_fct.limit > 1:
            raise Exception("Error1")
        return rt

    update_fct.limit = 0

    # Check the default_on_failure
    cd = CachedData(
        update_fct=update_fct, default_data=False, default_on_failure=True, no_previous_data=False
    )

    assert (cd.update_fct == update_fct)
    assert (cd.no_previous_data is False)

    assert (cd.data is True)
    lu = cd.last_update
    assert (cd.last_update > 0)
    assert (cd.failed is False)

    # This update must failed
    cd.do_update()

    assert (cd.data is False)
    assert (cd.last_update == lu)
    assert (cd.failed is True)

    # Check the no default_on_failure
    update_fct.limit = 0
    cd = CachedData(
        update_fct=update_fct, default_data=False, default_on_failure=False, no_previous_data=False
    )

    assert (cd.data is True)
    assert (cd.failed is False)

    # This update must failed
    cd.do_update()

    assert (cd.data is True)
    assert (cd.failed is True)

    # Check the previous_data
    update_fct.limit = 0
    cd = CachedData(
        update_fct=update_fct, default_data=False, default_on_failure=False, no_previous_data=True
    )

    assert (cd.data is False)
    assert (cd.failed is True)


def test_update():
    """Test that the data is update after the interval"""
    def update(previous_data):
        return previous_data + 1

    # When we create a cached data,
    cd = CachedData(default_data=-1, interval=0.1, update_fct=update)

    # First call to cd.data must call the udpate function
    assert(cd.data == 0)
    assert(cd.interval == 0.1)
    time.sleep(0.15)
    assert(cd.data == 1)


def test_interval():
    """Test that when interval is 0 update as each data call"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0.1, update_fct=update)

    for i in range(0, 9):
        assert(cd.data == i)
        time.sleep(0.15)


def test_no_interval():
    """Test that when interval is 0 update as each data call"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, interval=0, update_fct=update)

    for i in range(0, 9):
        assert(cd.data == i)


def test_force_data():
    """Test that when we use the force_data, data is update immediately"""
    def update(previous_data):
        return previous_data + 1

    cd = CachedData(default_data=-1, update_fct=update)

    for i in range(0, 10):
        cd.do_update()
        assert(cd.data == i)


def test_error_on_update_fct():
    """Test that we have the default value on error"""
    error = True

    def update(previous_data):
        if error:
            raise Exception("Toto")
        return "OK"

    cd = CachedData(default_data="FAILED", default_on_failure=True, interval=0, update_fct=update)

    for i in range(0, 9):
        assert(cd.data == "FAILED")

    error = False

    for i in range(0, 9):
        assert(cd.data == "OK")

    error = True
    assert(cd.data == "FAILED")

