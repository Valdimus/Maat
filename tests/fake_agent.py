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
# Date: 21/03/2017

import json


class FakeAgent:

    def __init__(self, process_name, backend_name):
        self.__processes = {
            "sessions": {
                "processes": [],
                "users": {
                    "christophe": {
                        "processes": [{
                            "backend": "Test",
                            "username": "christophe",
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
                        }],
                        "nb": 1
                    }
                },
                "nb_process": 1,
                "nb_user": 1
            },
            "sessions_timestamp": 100,
            "requests": {
            },
            "requests_timestamp": 200,
            "nb": 2,
            "timestamp": 300
        }

    @property
    def sessions(self):
        return self.__processes

    def __add_process(self, username):
        """Add a process to processes"""
        new_process = self.__generate_process(username)
        self.sessions["processes"].append(new_process)
        if username not in self.sessions["user"]:
            self.sessions["users"][username] = {
                "processes": [],
                "nb": 0
            }
        self.sessions["users"][username]["processes"].append(new_process)


    def __generate_process(self, username):
        """Create an fake process"""
        return {
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
            }

    def processes(self):
        return json.dumps(self.__processes, indent=4)

    def ping(self):
        return "OK"
