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
# Date: 22/03/2017

import psutil
from maat import CachedData


class Monitoring(CachedData):
    """Get Cpu, Memory and Swap Usage"""

    def __init__(self, *args, **kwargs):
        # Default data
        kwargs["data"] = self.update(None)
        CachedData.__init__(self, *args, **kwargs)

    def update(self, previous_data):
        """Update"""
        return {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "times": dict(psutil.cpu_times()._asdict()),
                "count": psutil.cpu_count(),
                "freq": dict(psutil.cpu_freq()._asdict()),
                "stats": dict(psutil.cpu_stats()._asdict())
            },
            "memory": dict(psutil.virtual_memory()._asdict()),
            "swap": dict(psutil.swap_memory()._asdict())
        }

