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


class HostMonitoring(CachedData):

    def __init__(self, *args, **kwargs):
        """
        :param process_name: The name of the process to watch
        """
        # Default data
        kwargs["default_data"] = {
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
        # We want to set the default value on error
        kwargs["default_on_failure"] = True

        # Disable the previous data deepcopy
        kwargs["no_previous_data"] = True

        CachedData.__init__(self, *args, **kwargs)

    def update_data(self, previous_data):
        """
        The udpate function to use
        :param previous_data: The previous data, will be None for us
        :return: the new data
        """

        return self.get_info()

    def get_info(self):
        """
        This function is use to get all the process that match the comparator function.
        :return: list
        """
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "cpu_percent": psutil.cpu_percent(),
            "cpu_nb": psutil.cpu_count(),
            "memory_used": mem.used,
            "memory_total": mem.total,
            "memory_free": mem.free,
            "memory_available": mem.available,
            "memory_percent": mem.percent,
            "swap_total": swap.total,
            "swap_free": swap.free,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        }
