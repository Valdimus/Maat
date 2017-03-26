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
    def max_session_per_user(self):
        return self.__max_session_per_user

    @property
    def nb_users(self):
        """Get the number of connected client"""
        nb_users = 0
        for backend in self.backends:
            if not backend.available:
                continue
            nb_users += backend.nb_users
        return nb_users

    @property
    def connected_users(self):
        """List all connected client"""
        tmp = []
        for backend in self.backends:
            if not backend.available:
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
        """Get all session for an user"""
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



