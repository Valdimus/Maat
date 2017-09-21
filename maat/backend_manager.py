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
# Date: 20/03/2017

import logging
import datetime

from maat.backend import Backend

def to_gb(nb):
    return round(nb / 1000000000, 3)


class BackendManager(object):

    """
    BackendManager is a class to manage the different backend. It will check whitch backend is available and witch are
    not.
    """
    def __init__(self, backends=None, logger=None):
        """
        :param backends: List of backend to use
        :param logger:
        """
        my_backends = [] if backends is None else backends
        self.__backends = {i.name: i for i in my_backends}
        self.__logger = logger if logger is not None else logging.getLogger("%s:%s" % (
            __name__, self.__class__.__name__
        ))

    @property
    def backends(self):
        """Get all backends as dict"""
        return self.__backends

    def add(self, backend):
        """
        Add a backend to the manager
        :param backend: The backend to add
        :raise: Exception is the backend is not an instance of Backend
        :return:
        """
        if not isinstance(backend, Backend):
            self.__logger.error("This is not a Backend!")
            raise Exception("This is not a Backend!")

        self.__backends[backend.name] = backend

    def rm(self, backend):
        """
        Remove a backend from the manager
        :param backend: The backend to remove. Can be a string or a backend instance
        :return: boolean
        """
        name = None
        if isinstance(backend, str):
            name = backend
        elif isinstance(backend, Backend):
            name = backend.name

        if name is not None:
            del self.__backends[name]
            return True
        return False

    def get(self, name):
        """
        Get a backend by his name
        :param name: The name of the backend to get
        :return:
        """
        if name in self.__backends.keys():
            return self.__backends[name]
        return None

    def to_list(self, all_backends=False):
        """
        List all backends available
        :param all_backends: If true, it will add non available backend
        :return: list of backend
        """
        backends = []

        for i, backend in self.backends.items():
            to_add = None
            if all_backends:
                to_add = backend
            elif backend.available():
                to_add = backend
            if to_add:
                backends.append(to_add)

        return backends

    def sessions_for_users(self, username):
        """
        Get all sessions for an user
        :param username: The user
        :return: list
        """
        sessions = []
        for session in self.to_list():
            sessions += session.processes(username)
        return sessions

    def user_sessions_by_backend(self, username):
        """
        Get all sessions for an user as dict with backend name as key
        :param username: The user
        :return: dict
        """
        return {
            backend.name: backend.processes(username) for backend in self.to_list()
        }

    def nb_user_sessions_by_backend(self, username):
        """
        Get the number of sessions for on user for each backend
        :param username: The user
        :return: dict, with backend name as key
        """
        return {
            name: len(sessions) for name, sessions in self.user_sessions_by_backend(username).items()
        }

    def nb_user_all_by_backend(self, username):
        """
        Get the number of processes and requests for an user on each backend
        :param username: The user
        :return: dict, with backend name as key
        """
        return {
            backend.name: backend.user_nb_all(username) for backend in self.to_list()
            }

    def all_nb_user_sessions(self, username):
        """
        Get the number of all sessions of an user for all backends
        :param username: The user
        :return: number
        """
        all_sessions_nb = 0
        for name, sessions_nb in self.nb_user_sessions_by_backend(username).items():
            all_sessions_nb += sessions_nb
        return all_sessions_nb

    def nb_process_by_backend(self):
        """
        Get the number of all processes for each backend
        :return: dict, with backend name as key and value as number
        """
        return {
            backend.name: backend.nb_process() for backend in self.to_list()
        }

    def nb_all_by_backend(self):
        """
        Get the number of all processes and all requests for each backend
        :return: dict, with backend name as key and value as number
        """
        return {
            backend.name: backend.nb() for backend in self.to_list()
            }

    def list_user(self):
        """List connected user and get the number of process for each backend"""
        tmp = {}
        for backend in self.to_list():
            for user in backend.data["processes"]:
                tmp[user][backend.name] = len(backend.data["processes"][user])
        return tmp

    def monitoring_users(self, username=None):
        """Monitor users processes"""

        processes = []
        for backend in self.to_list():
            processes += backend.get_process(username=username)

        def create_data():
            return {
                "user": "",
                "cpu": 0.0,
                "memory": 0.0,
                "processes": 0
            }

        def update_data(data, process):
            username = process["username"]

            if username not in data:
                data[username] = create_data()
            data[username]["user"] = username
            data[username]["cpu"] += process["cpu_percent"]
            data[username]["memory"] += to_gb(process["memory_info"]["rss"])
            data[username]["processes"] += 1

        data = {}
        for process in processes:
            update_data(data, process)

        return data

    def monitoring_host(self, backend):

        all_backend = True
        backends = self.to_list()
        backend_name = None

        if isinstance(backend, str):
            bk = self.get(backend)
            if bk is not None:
                backends = [bk]
                all_backend = False
                backend_name = backend

        elif isinstance(backend, list):
            temp = []
            for i in backend:
                bk = self.get(i)
                if bk is not None:
                    temp.append(bk)
            if len(temp) > 0:
                all_backend = False
                backends = temp
        data = {
            "all_backend": all_backend,
            "backend_name": backend_name,
            "cpu_percent": 0.0,
            "cpu_core": 0,
            "memory": 0,
            "memory_total": 0,
            "swap": 0,
            "swap_total": 0,
            "nb_users": 0,
            "nb_processes": 0,
            "nb_requests": 0,
            "backends": [],
            "processes": [],
            "backend_used": 0,
            "backend_total": len(self.to_list(all_backends=True)),
            "dead_backend": [],
            "requests": []
        }
        for backend in backends:
            data["cpu_percent"] += backend.host("cpu_percent") / len(backends)
            data["cpu_core"] += backend.host("cpu_nb")
            data["memory"] += to_gb(backend.host("memory_used"))
            data["memory_total"] += to_gb(backend.host("memory_total"))
            data["swap"] += to_gb(backend.host("swap_used"))
            data["swap_total"] += to_gb(backend.host("swap_total"))
            data["nb_users"] += backend.nb_user()
            data["nb_processes"] += backend.nb_process()
            data["nb_requests"] += backend.nb_requests()
            data["backends"].append({
                "name": backend.name,
                "cpu_percent":  backend.host("cpu_percent"),
                "memory": "%s/%s" % (to_gb(backend.host("memory_used")), to_gb(backend.host("memory_total"))),
                "swap": "%s/%s" % (to_gb(backend.host("swap_used")), to_gb(backend.host("swap_total"))),
                "users": backend.nb_user(),
                "processes": backend.nb_process(),
                "requests": backend.nb_requests()
            })

            data["backend_used"] += 1

            for process in backend.get_all_processes():
                data["processes"].append({
                    "backend": backend.name,
                    "user": process["username"],
                    "cpu": process["cpu_percent"],
                    "memory": to_gb(process["memory_info"]["rss"])
                })

            for username, requests in backend.requests().items():
                for request in requests:
                    data["requests"].append({
                        "backend": backend.name,
                        "username": username,
                        "timestamp": datetime.datetime.fromtimestamp(request).strftime('%d-%m-%Y %H:%M:%S')
                    })

        for backend in self.to_list(all_backends=True):
            if not backend.available():
                data["dead_backend"].append({
                    "name": backend.name,
                    "available": False
                })

        return data





