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


class PLSMonitoring(CachedData):
    """Monitor Process Launcher Service"""

    def __init__(self, *args, process_name="FakeService", **kwargs):
        # Default data
        kwargs["data"] = []
        CachedData.__init__(self, *args, **kwargs)
        self.__process_name = process_name

    @property
    def process_name(self):
        return self.__process_name

    def comparator(self, process_info):
        """
        Comprate the process name
        :param process_info:
        :return: boolean
        """
        return self.process_name == process_info["name"]

    def update(self, previous_data):
        """List all process that user"""
        data = []

        for process in psutil.process_iter():
            try:
                process_info = process.as_dict()
                if self.comparator(process_info):
                    obj = dict()
                    obj["username"] = process_info["username"]
                    obj["cpu_percent"] = process_info["cpu_percent"]
                    obj["memory_percent"] = process_info["memory_percent"]
                    obj["memory_info"] = dict((process_info["memory_info"]._asdict()))
                    obj["pid"] = process_info["pid"]
                    obj["ppid"] = process_info["ppid"]
                    obj["create_time"] = process_info["create_time"]

                    # More information but not all will be usefull
                    # obj["threads"] = element_to_dict(process_info["threads"])
                    # obj["name"] = process_info["name"]
                    # obj["exe"] = process_info["exe"]
                    # obj["cpu_times"] = element_to_dict(process_info["cpu_times"])
                    # obj["num_threads"] = process_info["num_threads"]
                    # obj["cwd"] = process_info["cwd"]
                    # obj["cmdline"] = process_info["cmdline"]
                    # obj["status"] = process_info["create_time"]
                    # obj["cpu_affinity"] = process_info["cpu_affinity"]
                    # obj["cpu_num"] = process_info["cpu_num"]
                    # obj["memory"] = element_to_dict(process_info["memory_full_info"])
                    data.append(obj)
            except Exception as e:
                print(str(e))
        return data

    def list_username(self):
        """List user that run process on host"""
        user_list = []
        for p in self.data:
            user_list.append(p["username"])
        return user_list

    def user_exist(self, user):
        """Check if a user have a process session running in host"""
        for p in self.data:
            if user == p["username"]:
                return p
        return None

    def number(self):
        """Get the number of user using process on host"""
        return len(self.data)
