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
from tests import check_consistency
from maat import HostMonitoring


def test_assignment():
    """Test value assignement"""

    hm = HostMonitoring(name="Test")
    assert(hm.name == "Test")


def test_get_info():
    """Check that we have consistent data on update"""
    hm = HostMonitoring(interval=0.1)

    data = hm.data

    default = {
        "cpu_percent": 0.0,
        "cpu_nb": 0,
        "memory_used": 0,
        "memory_total": 0,
        "memory_free": 0,
        "memory_available": 0,
        "memory_percent": 0.0,
        "swap_total": 0,
        "swap_free": 0,
        "swap_used": 0,
        "swap_percent": 0.0
    }

    check_consistency(data, default)

    time.sleep(0.2)

    for name, _ in default.items():
        assert(name in data)

