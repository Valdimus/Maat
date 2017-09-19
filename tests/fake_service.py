#!/usr/bin/env python

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
# Date: 23/03/2017
# Description: This little script to rename the process to see that the PLSMonitoring can monitor user
#              process.
# I use the following python module:
# https://github.com/dvarrazzo/py-setproctitle

import time
import setproctitle

if __name__ == "__main__":
    setproctitle.setproctitle("FakeService")
    while True:
        time.sleep(1)