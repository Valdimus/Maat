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

from maat import ProcessMonitoring


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