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


class ProcessMonitoring(CachedData):
    """
    This class is use to monitor some specific process, that can be determined by the comparator function for each user.
    By default, we do the filter by the process name.
    """

    def __init__(self, process_name="FakeService", comparator=None, *args, **kwargs):
        """
        :param process_name: The name of the process to watch
        """
        # Default data
        kwargs["default_data"] = {
            "processes": [],
            "users": {},
            "nb": 0
        }
        # We want to set the default value on error
        kwargs["default_on_failure"] = True

        # Disable the previous data deepcopy
        kwargs["no_previous_data"] = True

        CachedData.__init__(self, *args, **kwargs)

        # The Process Name
        self.__process_name = process_name

        # The comparator function to use
        self.__comparator = self.comparator if comparator is None else comparator

    @property
    def process_name(self):
        """
        Get the process name to monitor
        :return: string
        """
        return self.__process_name

    def comparator(self, process_info):
        """
        This function is use to obtain the
        :param process_info:
        :return: boolean
        """
        return self.process_name == process_info.name()

    def update_data(self, previous_data):
        """
        The udpate function to use
        :param previous_data: The previous data, will be None for us
        :return: the new data
        """

        sessions = self.get_processes()
        data = {
            "processes": sessions,
            "users": self.user_sessions(sessions),
            "nb": len(sessions)
        }

        return data

    def get_processes(self):
        """
        This function is use to get all the process that match the comparator function.
        :return: list
        """
        data = []

        # for process in process_iter_filter(self.comparator):
        for process in psutil.process_iter():
            try:
                if self.comparator(process):
                    process_info = process.as_dict()
                    obj = {
                        "username": process_info["username"],
                        "cpu_percent": process_info["cpu_percent"],
                        "memory_percent":  process_info["memory_percent"],
                        "memory_info": dict((process_info["memory_info"]._asdict())),
                        "pid": process_info["pid"],
                        "ppid": process_info["ppid"],
                        "create_time": process_info["create_time"],
                        "cwd": process_info["cwd"],
                        "num_threads": process_info["num_threads"],
                        "cmdline": [i for i in process_info["cmdline"] if i != ""],
                        "exe": process_info["exe"],
                        "name": process_info["name"]
                    }

                    # obj = dict()
                    # obj["username"] = process_info["username"]
                    # obj["cpu_percent"] = process_info["cpu_percent"]
                    # obj["memory_percent"] = process_info["memory_percent"]
                    # obj["memory_info"] = dict((process_info["memory_info"]._asdict()))
                    # obj["pid"] = process_info["pid"]
                    # obj["ppid"] = process_info["ppid"]
                    # obj["create_time"] = process_info["create_time"]
                    # obj["cwd"] = process_info["cwd"]
                    # obj["num_threads"] = process_info["num_threads"]

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

    @staticmethod
    def user_sessions(processes):
        """
        Will reduce all the process for each user
        :param processes: the list of process
        :return: dictionary:
        {
            "USERNAME_0": {
                "sessions": [ ... ],
                "nb": 1
            }
        }
        """
        user_list = {}
        for p in processes:
            if p["username"] not in user_list:
                user_list[p["username"]] = []
            user_list[p["username"]].append(p)
        return user_list


class FakeProcessMonitoring(ProcessMonitoring):

    def __init__(self, *args, **kwargs):
        ProcessMonitoring.__init__(self, *args, **kwargs)

        self.__fake_processes = {}

    @property
    def fake_process(self):
        """Get the fake processes"""
        return self.__fake_processes

    def add_session(self, username):
        """Add a session for an user"""
        if username not in self.fake_process:
            self.fake_process[username] = 0
        self.fake_process[username] += 1

    def rm_sessions(self, username):
        if username in self.fake_process:
            self.fake_process[username] -= 1
            if self.fake_process[username] <= 0:
                del self.fake_process[username]

    def get_processes(self):
        data = []

        for username, processes in self.fake_process.items():
            for i in range(0, processes):
                data.append({
                    "username": username,
                    "cpu_percent": 10.0,
                    "memory_percent": 50.0,
                    "memory_info": {},
                    "pid": 112,
                    "ppid": 111,
                    "create_time": 2313249687,
                    "cwd": "/home/christophe",
                    "num_threads": 2,
                    "cmdline": [],
                    "exe": "R",
                    "name": "R"
                })

        return data