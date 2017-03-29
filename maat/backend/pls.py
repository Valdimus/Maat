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

import requests
from maat import Session
from maat import logger, CachedData
from maat.backend import Backend


class PLSBackend(Backend):
    """
    The Process Launcher Service.
    The main purpose of this class is to handle the PLS service like Rstudio or Jupyter that launch a process for each
    user by a service but don't have a load balancer to dispatch users between multiple host.

    This backend must be use with the agent to monitoring the PLS. Therefor, we will be
    able to dispatch user by load_average of host or by number of client connected to the host.
    """

    def __init__(self, agent_port=5005, monitoring_interval=30, sessions_interval=0.5, max_session_per_user=1, **kwargs):
        """
        :param agent_port: Port of the agent
        :param agent_path: Path to the agent
        :param kwargs:
        """
        Backend.__init__(self, **kwargs)
        self.__agent_port = agent_port

        self.__monitoring = CachedData(
            data=self._default_value_monitoring(), interval=monitoring_interval, update_fct=self._update_monitoring
        )
        self.__sessions = CachedData(
            data=self._default_value_pls(), interval=sessions_interval, update_fct=self._update_pls
        )
        self.__max_session_per_user = max_session_per_user

    @property
    def agent_port(self):
        return self.__agent_port

    @property
    def monitoring(self):
        return self.__monitoring.data

    @property
    def sessions(self):
        return self.__sessions.data

    @property
    def nb_users(self):
        return len(self.user_list)

    @property
    def user_list(self):
        """List the user connected to the backend"""
        user_list = []
        for client in self.sessions:
            if client["username"] not in user_list:
                user_list.append(client["username"])

        return user_list

    @property
    def max_session_per_user(self):
        return self.__max_session_per_user

    def user_reach_max_session(self, username):
        """Check if the user don't reach the max session on this backend"""
        return self.max_session_per_user != 0 and len(self.user_sessions(username)) >= self.max_session_per_user

    def user_sessions(self, username):
        """
        Get all session of an user
        :param username:
        :return: Session
        """
        sessions = []
        for session in self.user_monitoring_sessions(username):
            sessions.append(Session(self, username, session["pid"]))
        return sessions

    def user_monitoring_sessions(self, username):
        """
        Return all monitoring sessions of a user
        :param username: The user name
        :return: All monitoring sessions of user
        """
        user_sessions = []
        for session in self.sessions:
            if username == session["username"]:
                user_sessions.append(session)
        return user_sessions

    def get_user_monitoring_session(self, username, pid):
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
        return len(self.user_monitoring_sessions(username))

    def agent_url(self, path=""):
        """
        Generate the url to the agent
        :param path:
        :return:
        """
        return "%s://%s%s%s" % (
            self.protocol,
            self.hostname,
            ":%s" % self.agent_port if self.agent_port is not None else "",
            path
        )

    def _update_monitoring(self, previous_data):
        temp = self.make_request(self.agent_url("/v1/monitoring"))

        if temp is None:
            raise Exception("Impossible to update monitoring")

        return temp.json()

    def _update_pls(self, previous_data):
        temp = self.make_request(self.agent_url("/v1/sessions"))

        if temp is None:
            raise Exception("Impossible to update sessions")

        return temp.json()

    def _default_value_monitoring(self):
        return {
            "cpu": None,
            "memory": None,
            "swap": None
        }

    def _default_value_pls(self):
        return []

    def simple_monitoring(self):
        """Return a simple version of the monitoring CachedData"""
        mon = {}

        data = self.monitoring

        # Compute CPU
        mon["cpu"] = {
            "percent": data["cpu"]["percent"] / 100.0,
            "used": (float(data["cpu"]["percent"]) / 100.0)*float(data["cpu"]["count"]),
            "total": data["cpu"]["count"]
        }

        mon["memory"] = {
            "percent": data["memory"]["percent"] / 100.0,
            "used": data["memory"]["used"],
            "cached": data["memory"]["cached"],
            "total": data["memory"]["total"],
        }

        mon["swap"] = {
            "percent": data["swap"]["percent"] / 100.0,
            "used": data["swap"]["used"],
            "total": data["swap"]["total"]
        }

        data = self.sessions

        mon["nb_users"] = self.nb_users
        mon["nb_sessions"] = len(data)

        return mon

    def to_dict(self):
        a = Backend.to_dict(self)
        a["nb_users"] = self.nb_users
        return a




