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
# Date: 30/03/2017


class PLSHandler:

    def get_property(self, name):
        raise NotImplementedError

    @property
    def name(self):
        return self.get_property("name")

    @property
    def hostname(self):
        return self.get_property("hostname")

    @property
    def available(self):
        return self.get_property("available")

    @property
    def ping_last_update(self):
        return self.get_property("ping_last_update")

    @property
    def sessions(self):
        return self.get_property("sessions")

    @property
    def sessions_failed(self):
        return self.get_property("sessions_failed")

    @property
    def sessions_last_update(self):
        return self.get_property("sessions_last_update")

    @property
    def monitoring(self):
        return self.get_property("monitoring")

    @property
    def monitoring_failed(self):
        return self.get_property("monitoring_failed")

    @property
    def monitoring_last_update(self):
        return self.get_property("monitoring_last_update")

    @property
    def max_session_per_user(self):
        return self.get_property("max_session_per_user")

    def nb_sessions(self):
        return len(self.sessions)

    def user_list(self):
        """List the user connected to the backend"""
        user_list = []
        for session in self.sessions:
            if session["username"] not in user_list:
                user_list.append(session["username"])
        return user_list

    def nb_users(self):
        return len(self.user_list())

    def user_sessions(self, username):
        """
        Get all session of an user
        :param username:
        :return: Session
        """
        user_sessions = []
        for session in self.sessions:
            if username == session["username"]:
                user_sessions.append(session)
        return user_sessions

    def user_session(self, username, pid):
        """
        Return the monitoring session of username with pid
        :param username:
        :param pid:
        :return: None if no session found, else the session
        """
        for session in self.user_monitoring_sessions(username):
            if session["pid"] == pid:
                return session
        return None


    def nb_user_sessions(self, username):
        """
        Get the number of session for an user
        :param username: The user name
        :return: number
        """
        return len(self.user_sessions(username))

    def user_reach_max_session(self, username):
        """Check if the user don't reach the max session on this backend"""
        return self.max_session_per_user != 0 and len(self.user_sessions(username)) >= self.max_session_per_user


class PLSBackendHandler(PLSHandler):

    def __init__(self, backend):
        self.__backend = backend

    def get_property(self, name):
        if name == "name":
            return self.__backend.name
        if name == "hostname":
            return self.__backend.hostname
        if name == "available":
            return self.__backend.available
        if name == "ping_last_update":
            return self.__backend.name
        if name == "sessions":
            return self.__backend.sessions
        if name == "sessions_failed":
            return self.__backend.get_sessions().failed()
        if name == "sessions_last_update":
            return self.__backend.get_sessions().last_update
        if name == "monitoring":
            return self.__backend.monitoring
        if name == "monitoring_failed":
            return self.__backend.get_monitoring().failed()
        if name == "monitoring_last_update":
            return self.__backend.get_monitoring().last_update
        if name == "max_session_per_user":
            return self.__backend.max_session_per_user
        raise NotImplementedError

    def to_dict(self):
        return self.__backend.to_dict()

class PLSFrontendHandler(PLSHandler):

    def __init__(self, data):
        self.__data = data

    def get_property(self, name):
        return self.__data[name]

    def to_dict(self):
        return self.__data

