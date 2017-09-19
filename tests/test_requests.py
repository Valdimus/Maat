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
from maat import Requests



def test_requests():
    requests = Requests()

    assert(requests.requests == {})
    assert(requests.nb == 0)

    update_time = time.time()

    # Add a request
    requests.add("Titi")

    assert(requests.last_update > update_time)
    assert(requests.nb == 1)
    assert(len(requests.requests["Titi"]) == 1)
    assert(len(requests.requests) == 1)


    # Try to add new request for an existing user and for a new one
    previous_update = requests.last_update
    requests.add("Titi")
    requests.add("Toto")

    assert(requests.nb == 3)
    assert(len(requests.requests["Titi"]) == 2)
    assert(len(requests.requests["Toto"]) == 1)
    assert (len(requests.requests) == 2)
    assert(requests.last_update > previous_update)


    # Remove
    previous_update = requests.last_update
    requests.rm("Toto", requests.requests["Toto"][-1])

    assert (requests.nb == 2)
    assert (len(requests.requests["Titi"]) == 2)
    assert (len(requests.requests) == 1)
    assert (requests.last_update > previous_update)