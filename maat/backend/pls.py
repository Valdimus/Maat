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
            default_data=self._default_value_monitoring(), interval=monitoring_interval, update_fct=self._update_monitoring
        )
        self.__sessions = CachedData(
            default_data=self._default_value_pls(), interval=sessions_interval, update_fct=self._update_pls
        )
        self.__max_session_per_user = max_session_per_user
        self.__agent_available = False

    @property
    def agent_port(self):
        return self.__agent_port

    @property
    def agent_available(self):
        return self.__agent_available

    @property
    def monitoring(self):
        return self.__monitoring.data

    @property
    def sessions(self):
        return self.__sessions.data

    @property
    def nb_sessions(self):
        return len(self.__sessions.data)

    @property
    def max_session_per_user(self):
        """Get the max session per user"""
        return self.__max_session_per_user

    def get_monitoring(self):
        """
        :return: The cached data for the monitoring
        """
        return self.__monitoring

    def get_sessions(self):
        """
        :return: The cached data for the sessions
        """
        return self.__sessions

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

    def make_agent_request(self, url, *args, **kwargs):
        """Make a call to the agent api"""

        temp = self.make_request(self.agent_url(url), *args, **kwargs)

        if temp is None:
            self.__agent_available = False
        self.__agent_available = True

        return temp

    def _update_monitoring(self, previous_data):
        temp = self.make_agent_request("/v1/monitoring")

        if temp is None:
            raise Exception("Impossible to update monitoring")

        return temp.json()

    def _update_pls(self, previous_data):
        temp = self.make_agent_request("/v1/sessions")

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

    def to_dict(self):
        a = Backend.to_dict(self)
        a["agent_url"] = self.agent_url("")
        a["agent_available"] = self.agent_available
        a["sessions"] = self.sessions
        a["sessions_failed"] = self.get_sessions().failed()
        a["sessions_last_update"] = self.get_sessions().last_update
        a["nb_sessions"] = self.nb_sessions
        a["monitoring"] = self.monitoring
        a["monitoring_failed"] = self.get_monitoring().failed()
        a["monitoring_last_update"] = self.get_monitoring().last_update
        a["max_session_per_user"] = self.max_session_per_user
        return a





