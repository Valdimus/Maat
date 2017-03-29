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


class SessionManager:
    """
    Session Manager
    This class is responsible to handle all client sessions. It's an abstract class, you must implement "load_balance"
    methods to get the most appropriate backend for a specific client.
    This class definied the admin panel
    """

    def __init__(self, backends, max_session_per_user=1):
        """
        :param backends: Backends to use
        """
        self.__backends = backends
        self.__max_session_per_user = max_session_per_user

    @property
    def backends(self):
        """Get the backends"""
        return self.__backends

    @property
    def available_backends(self):
        """Return all available backend"""
        tmp = []
        for backend in self.backends:
            if not backend.available:
                continue
            tmp.append(backend)
        return tmp

    @property
    def max_session_per_user(self):
        return self.__max_session_per_user

    @property
    def nb_users(self, backend_to_search):
        """
        Get the number of connected client on all backend or a specific one
        :param backend_to_search:
        :return:
        """
        bd = self.found_backend(backend_to_search)
        nb_users = 0
        for backend in self.backends:
            if not backend.available:
                continue
            if bd is not None and bd != backend:
                continue
            nb_users += backend.nb_users
        return nb_users

    @property
    def connected_users(self, backend_to_search):
        """
        List all connected client for all backend or a specific one
        :param backend_to_search:
        :return: list of user
        """
        tmp = []
        bd = self.found_backend(backend_to_search)
        for backend in self.backends:
            if not backend.available:
                continue
            if bd is not None and bd != backend:
                continue
            for username in backend.user_list:
                if username not in tmp:
                    tmp.append(username)
        return tmp

    @property
    def nb_available(self):
        """Count available backend"""
        nb = 0
        for backend in self.backends:
            if backend.available:
                nb += 1
        return nb

    def get_user_sessions(self, username):
        """
        Get all session for an user on all backend or a specific one
        :param username:
        :return: list of session
        """
        sessions = []
        for backend in self.backends:
            if not backend.available:
                continue
            sessions += backend.user_sessions(username)
        return sessions

    def add_session(self, username):
        """Search an available backend to start a new session"""
        # We get the session of the user
        sessions = self.get_user_sessions(username)

        # Check if user not already have the max session
        if self.max_session_per_user != 0 and len(sessions) >= self.__max_session_per_user:
            raise Exception("User have reach the maximum session!")

        # Search the backend with the less connection
        choosen = None
        lowest = 99999999999
        for backend in self.backends:
            if not backend.available:
                continue
            if backend.user_reach_max_session(username):
                continue
            if backend.nb_users < lowest:
                lowest = backend.nb_users
                choosen = backend
        if choosen is None:
            raise Exception("Impossible to found a backend")
        return choosen

    def quick_choose(self, username):
        """Make a quick search for the user. If no session found, it will create it"""
        sessions = self.get_user_sessions(username)

        if len(sessions) > 0:
            return sessions[0].backend
        return self.add_session(username)

    def found_backend(self, backend):
        """
        Found a backend by his name or his hostname
        :param backend: Thr backend name or hostname
        :return: Backend, if not found will return None
        """
        if backend is None:
            return None

        for bd in self.backends:
            if bd.name == backend or bd.hostname == backend:
                return bd
        return None

    def monitoring(self, backend=None):
        """
        Get the monitoring object of all backend or a specific one
        :param backend: Backend to
        :return:
        """
        # Get the backend
        bd = self.found_backend(backend)

        if bd is not None:
            return bd.simple_monitoring()

        mon = {
            "cpu": {
                "used": 0,
                "percent": 0,
                "total": 0
            },
            "memory": {
                "used": 0,
                "percent": 0,
                "total": 0
            },
            "swap": {
                "used": 0,
                "percent": 0,
                "total": 0
            },
            "nb_users": 0,
            "nb_sessions": 0
        }

        backends = self.available_backends

        simple_backends = [x.simple_monitoring() for x in backends]

        # Cpu
        mon["cpu"]["used"] = sum([ float(x["cpu"]["used"]) for x in simple_backends])
        mon["cpu"]["total"] = sum([ float(x["cpu"]["total"]) for x in simple_backends] )
        mon["cpu"]["percent"] = mon["cpu"]["used"] / mon["cpu"]["total"] * 100.0

        mon["memory"]["used"] = sum([ float(x["memory"]["used"]) for x in simple_backends])
        mon["memory"]["total"] = sum([ float(x["memory"]["total"]) for x in simple_backends])
        mon["memory"]["percent"] = 1.0 * mon["memory"]["used"] / mon["memory"]["total"] * 100.0

        mon["swap"]["used"] = sum([ float(x["swap"]["used"]) for x in simple_backends])
        mon["swap"]["total"] = sum([ float(x["swap"]["total"]) for x in simple_backends])
        mon["swap"]["percent"] = 1.0 * mon["swap"]["used"] / mon["swap"]["total"] * 100.0

        mon["nb_users"] = sum([x["nb_users"] for x in simple_backends])
        mon["nb_sessions"] = sum([x["nb_sessions"] for x in simple_backends])

        return mon

    def backends_sum(self):

        liste = []
        for backend in self.backends:
            data = backend.simple_monitoring()

            tmp = {
                "name": backend.name,
                "hostname": backend.hostname,
                "cpu": "%s%%, %s cores" % (round(data["cpu"]["percent"], 2), data["cpu"]["total"]),
                "memory": "%s/%s Go" % (round(data["memory"]["used"] / 1000000000, 3), round(data["memory"]["total"] / 1000000000, 3)),
                "swap": "%s/%s Go" % (round(data["swap"]["used"] / 1000000000, 3), round(data["swap"]["total"] / 1000000000, 3)),
                "users": data["nb_users"],
                "sessions": data["nb_sessions"],
                "available": "True" if backend.available is True else "False"
            }

            liste.append(tmp)
        return liste